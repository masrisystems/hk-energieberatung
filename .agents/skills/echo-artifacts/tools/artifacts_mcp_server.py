#!/usr/bin/env python3
"""
artifacts_mcp_server.py — MCP-Server für Artefakte im echo-Framework.

Vier Tools, je Artefaktart eines:
  create_ticket              — Ticket
  create_implementation_plan — Implementierungsplan
  create_walkthrough         — Walkthrough
  create_milestone           — Milestone

Jedes Tool nimmt `project` als Pflichtparameter. Aus dem Maestro-Projektrecord ergibt sich
`ticket_system`; danach richtet sich das Zielsystem:
  internal — Markdown-Datei im Projektverzeichnis
  maestro  — Record über die Maestro-API
  gitlab   — Issue, Kommentar am Issue oder Projekt-Milestone

Der Aufrufer übergibt ausschließlich Daten — keine Pfade, keine Vorlagen, keine
Fallunterscheidung nach Zielsystem.

MCP-Eintrag in .mcp.json:
  {
    "mcpServers": {
      "echo-artifacts": {
        "command": "python3",
        "args": [".agent/skills/echo-artifacts/tools/artifacts_mcp_server.py"]
      }
    }
  }

Voraussetzungen:
  python3 -m pip install fastmcp
"""

import hashlib
import importlib.util
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    sys.exit(
        "Fehler: fastmcp nicht installiert.\n"
        "Bitte installieren: python3 -m pip install fastmcp"
    )

# Agent-Verzeichnis: im Antigravity-Setup wird der Literal '.agent' vom Finalize-sed auf
# '.agents' umgeschrieben (#065) — derselbe Code funktioniert in beiden Layouts.
_AGENT_DIR = Path(__file__).parents[4] / '.agent'

sys.path.insert(0, str(_AGENT_DIR / 'skills' / 'echo-maestro' / 'tools'))

from maestro_client import (  # noqa: E402
    _find_maestro_url,
    _http_get,
    _post_raw,
    _form_fields,
    _identifier_from_content,
    _fetch_record_markdown,
    project_directory,
)

mcp = FastMCP("echo-artifacts")

_TEMPLATES = {
    'ticket': 'echo-artifacts/templates/ticket.md',
    'implementation-plan': 'echo-artifacts/templates/implementation-plan.md',
    'walkthrough': 'echo-artifacts/templates/walkthrough.md',
    'milestone': 'echo-artifacts/templates/milestone.md',
}

_TICKET_DIRS = ('open', 'backlog', 'completed', 'discarded')

_TICKET_SYSTEMS_DIR = _AGENT_DIR / 'skills' / 'echo-workroutine' / 'tools' / 'ticket_systems'
_STAGING_DIR = _AGENT_DIR / '.maestro' / 'artifact-staging'


def _load_operations_module(ticket_system: str):
    ops_file = _TICKET_SYSTEMS_DIR / f'{ticket_system}.py'
    spec = importlib.util.spec_from_file_location(f'artifact_source_operations_{ticket_system}', ops_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_todo_completion_module():
    todo_file = _TICKET_SYSTEMS_DIR.parent / 'todo_completion.py'
    spec = importlib.util.spec_from_file_location('todo_completion', todo_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _resolve_todo(system: str, record: dict, ticket: str, artifact_type: str, todo: str):
    """Lädt `ops` und `todo_completion`, prüft das übergebene Todo. Wirft `RuntimeError` bei
    jeder Abweichung — inklusive Ticketsystemen, die den Todo-Abschluss (noch) nicht
    unterstützen. Rückgabe: `(ops, todo_completion_module, base_url, ticket_obj, todo_record)`."""
    ops = _load_operations_module(system)
    if not hasattr(ops, 'read_ticket'):
        raise RuntimeError(f'Todo-gekoppelter Abschluss ist für Ticketsystem {system!r} nicht unterstützt.')
    todo_completion = _load_todo_completion_module()
    base_url = _find_maestro_url()
    todo_record = todo_completion.resolve_todo(base_url, todo)
    ticket_obj = ops.read_ticket(record, ticket)
    active_plan = todo_completion.find_active_plan(
        list_implementation_plans, view_implementation_plan, system, record['uuid'], ticket
    )
    todo_completion.validate_todo_for_artifact(todo_record, record['ucid'], ticket, artifact_type, ticket_obj, active_plan)
    return ops, todo_completion, base_url, ticket_obj, todo_record


def _deliver(system: str, project: dict, identifier: str, content: str, filename: str, artifact_type: str):
    _STAGING_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = _STAGING_DIR / filename
    temp_path.write_text(content, encoding='utf-8')
    ops = _load_operations_module(system)
    result = ops.deliver_artifact(project, identifier, str(temp_path), artifact_type)
    if temp_path.exists():
        temp_path.unlink()
    return result


def _config() -> dict:
    return json.loads((_AGENT_DIR / 'config.json').read_text(encoding='utf-8'))


def _project_record(project: str) -> dict:
    """Projektrecord über die Agent-Route. `project` ist die UUID des Projekts."""
    return _http_get(_find_maestro_url(), f'projects/{project}/agent')


def _target_system(record: dict) -> str:
    return record['ticket_system']


_UMLAUTE = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'})


def _kebab(value: str) -> str:
    """Dateinamensform: Kleinbuchstaben, Bindestriche, Umlaute in ASCII-Umschrift."""
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower().translate(_UMLAUTE).strip())
    return slug.strip('-')


def _require_short_title(title: str) -> None:
    if len(title.split()) > 5:
        raise RuntimeError(f'Titel zu lang (max. 5 Wörter): "{title}"')


def _template(name: str) -> str:
    return (_AGENT_DIR / 'skills' / _TEMPLATES[name]).read_text(encoding='utf-8')


def _render(template: str, title: str, meta: dict, sections: dict) -> str:
    """Vorlage befüllen: H1-Titel, Frontmatter-/Meta-Werte, Abschnittsinhalte.

    `meta` bildet Feldnamen auf Werte ab — sowohl Frontmatter (`key: wert`) als auch
    Meta-Listen (`- Key:            wert`). `sections` bildet Überschriften ohne `## `
    auf ihren Inhalt ab; Kommentarzeilen und Platzhalterzeilen der Vorlage entfallen.
    """
    out: list[str] = []
    replaced_section = False
    for line in template.splitlines():
        if line.startswith('# ') and not line.startswith('## '):
            prefix, _, _ = line[2:].partition(':')
            out.append(f'# {prefix}: {title}' if _ else f'# {title}')
            continue
        if line.startswith('## '):
            heading = line[3:].strip()
            out.append(line)
            if heading in sections:
                out.extend(['', str(sections[heading]).rstrip('\n'), ''])
                replaced_section = True
            else:
                replaced_section = False
            continue
        if replaced_section:
            continue
        meta_value = _meta_line(line, meta)
        out.append(meta_value if meta_value is not None else line)
    return '\n'.join(out).rstrip('\n') + '\n'


def _meta_line(line: str, meta: dict) -> str | None:
    frontmatter = re.match(r'^([a-z_]+):\s', line)
    if frontmatter and frontmatter.group(1) in meta:
        return f'{frontmatter.group(1)}: {meta[frontmatter.group(1)]}'
    listed = re.match(r'^- (\S[^:]*):(\s+)', line)
    if listed:
        key = listed.group(1).strip().lower()
        if key in meta:
            return f'- {listed.group(1)}:{listed.group(2)}{meta[key]}'
    return None


def _maestro_agent_list(base_url: str, archetype: str, **filters: str) -> list[dict]:
    query = '&'.join(f'{key}={urllib.parse.quote(str(value))}' for key, value in filters.items() if value)
    path = f'{archetype}/agent' + (f'?{query}' if query else '')
    result = _http_get(base_url, path)
    return result.get('data', []) if isinstance(result, dict) else result


_TICKET_META_LABELS = {'id': 'ID', 'typ': 'Typ', 'status': 'Status'}


def _ticket_meta(content: str) -> dict:
    """Liest `- ID:`, `- Typ:`, `- Status:` aus einer internen Ticket-Datei; Titel aus der H1-Zeile."""
    meta = {'title': _current_title(content, 'Ticket')}
    for key, label in _TICKET_META_LABELS.items():
        match = re.search(rf'^- {label}:\s*(.+)$', content, re.MULTILINE)
        if match:
            meta[key] = match.group(1).strip()
    return meta


def _write(path: Path, content: str) -> str:
    if path.exists():
        raise RuntimeError(f'{path} existiert bereits.')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return str(path)


def _next_ticket_id(root: Path) -> str:
    highest = 0
    for folder in _TICKET_DIRS:
        for entry in (root / 'docs' / 'tickets' / folder).glob('[0-9]*[_-]*.md'):
            number = re.match(r'^(\d+)', entry.name)
            if number:
                highest = max(highest, int(number.group(1)))
    return f'{highest + 1:03d}'


def _find_ticket_path(root: Path, ticket_id: str) -> Path:
    for folder in _TICKET_DIRS:
        matches = list((root / 'docs' / 'tickets' / folder).glob(f'{ticket_id}[_-]*.md'))
        if matches:
            return matches[0]
    raise RuntimeError(f'Ticket {ticket_id} nicht gefunden.')


def _current_title(content: str, heading_prefix: str) -> str:
    first_line = content.splitlines()[0]
    text = first_line[2:].strip()
    prefix = f'{heading_prefix}: '
    return text[len(prefix):] if text.startswith(prefix) else text


def _maestro_create(archetype: str, fields: dict) -> str:
    base_url = _find_maestro_url()
    content = _post_raw(base_url, archetype, _form_fields(fields))
    identifier = _identifier_from_content(content, archetype)
    return _fetch_record_markdown(base_url, archetype, identifier)


def _maestro_update(archetype: str, identifier: str, fields: dict) -> str:
    base_url = _find_maestro_url()
    _post_raw(base_url, f'{archetype}/{identifier}', _form_fields(fields))
    return _fetch_record_markdown(base_url, archetype, identifier)


def _gitlab_post(path: str, data: dict) -> dict:
    config = _config()
    url = f"{config['gitlab_url'].rstrip('/')}/api/v4/{path.lstrip('/')}"
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode('utf-8'),
        headers={'PRIVATE-TOKEN': config['private_token']},
        method='POST',
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode('utf-8'))


def _gitlab_get(path: str) -> dict:
    config = _config()
    url = f"{config['gitlab_url'].rstrip('/')}/api/v4/{path.lstrip('/')}"
    request = urllib.request.Request(url, headers={'PRIVATE-TOKEN': config['private_token']})
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode('utf-8'))


def _gitlab_put(path: str, data: dict) -> dict:
    config = _config()
    url = f"{config['gitlab_url'].rstrip('/')}/api/v4/{path.lstrip('/')}"
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode('utf-8'),
        headers={'PRIVATE-TOKEN': config['private_token']},
        method='PUT',
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode('utf-8'))


def _gitlab_project_id(record: dict) -> str:
    """GitLab-Ziel aus dem für den Aufruf aufgelösten Projektdatensatz liefern."""
    project_id = record.get('gitlab_project_id')
    if project_id is None or not str(project_id).strip():
        raise RuntimeError('GitLab-Projekt-ID fehlt im Projektdatensatz.')
    return str(project_id)


def _issue_body(sections: dict, meta: dict | None = None) -> str:
    parts = []
    if meta:
        meta_lines = '\n'.join(f'- {key}: {value}' for key, value in meta.items())
        parts.append(f'## Meta\n\n{meta_lines}')
    parts.extend(f'## {heading}\n\n{value}' for heading, value in sections.items())
    return '\n\n'.join(parts)


@mcp.tool()
def create_ticket(project: str, title: str, folder: str, type: str, status: str, responsible: str,
                  context: str, goal: str, requirements: str, acceptance_criteria: str,
                  risks: str = '', open_questions: str = '', references: str = '',
                  first_approach: str = '', assignee: str = '') -> str:
    """Ticket im Ticketsystem des Projekts anlegen.

    project:             UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    title:               Titel des Tickets, max. 5 Wörter.
    folder:              Zielordner bei `ticket_system=internal` — `open` oder `backlog`,
                         nach der Kriterientabelle in `ticketing-config.md` bestimmt.
    type:                feature | bug | refactor | chore | epic
    status:              Zustand laut ticket-rules, z.B. draft, proposed, approved.
    responsible:         Verantwortliche Person.
    context bis first_approach: Inhalt der jeweiligen Abschnitte als Markdown.
    assignee:            Maestro-Personen-UUID für die Ticket-Zuweisung bei `gitlab`/`maestro`
                         (bei `internal` unbenutzt — dort deckt `responsible` die Zuweisung ab).
    """
    _require_short_title(title)
    record = _project_record(project)
    system = _target_system(record)
    sections = {
        'Kontext': context,
        'Ziel': goal,
        'Anforderungen': requirements,
        'Akzeptanzkriterien': acceptance_criteria,
        'Risiken': risks,
        'Offene Fragen': open_questions,
        'Erste Umsetzungsidee': first_approach,
    }

    if system == 'internal':
        if folder not in _TICKET_DIRS[:2]:
            raise RuntimeError(f'Unbekannter Zielordner: {folder}')
        root = project_directory(record)
        ticket_id = _next_ticket_id(root)
        meta = {
            'id': ticket_id,
            'typ': type,
            'status': status,
            'erstellt': date.today().isoformat(),
            'erstellt von': _config().get('agent', ''),
            'verantwortlich': responsible,
            'referenzen': references,
        }
        content = _render(_template('ticket'), title, meta, sections)
        return _write(root / 'docs' / 'tickets' / folder / f'{ticket_id}_{_kebab(title)}.md', content)

    if system == 'maestro':
        base_url = _find_maestro_url()
        content = _post_raw(base_url, 'tickets', _form_fields({
            'project': project,
            'title': title,
            'type': type,
            'status': status,
            'context': context,
            'goal': goal,
            'requirements': requirements,
            'acceptance_criteria': acceptance_criteria,
            'risks': risks,
            'open_questions': open_questions,
        }))
        ticket_uuid = _identifier_from_content(content, 'tickets')
        if assignee:
            ops = _load_operations_module('maestro')
            identity_uuid = ops.assignee_identity_uuid(record, assignee)
            _post_raw(base_url, f'tickets/{ticket_uuid}/relations/assignees/attach',
                      _form_fields({'target_uuid': identity_uuid}))
        return _fetch_record_markdown(base_url, 'tickets', ticket_uuid)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        meta = {
            'ID': 'siehe GitLab-Issue-Nummer',
            'Typ': type,
            'Status': status,
            'Erstellt': date.today().isoformat(),
            'Erstellt von': _config().get('agent', ''),
            'Verantwortlich': responsible,
            'Referenzen': references,
        }
        by_status = {row['status'].lower(): row['label'] for row in record.get('status_labels', [])}
        target_label = by_status.get(status)
        if not target_label:
            raise RuntimeError(f'Kein Label für Status {status!r} in Projekt {record["uuid"]} hinterlegt.')
        issue = _gitlab_post(f'projects/{gitlab_project_id}/issues', {
            'title': title,
            'description': _issue_body(sections, meta),
            'labels': target_label,
        })
        if assignee:
            ops = _load_operations_module('gitlab')
            external_id = ops.person_external_id(record, assignee)
            ops.write_assignee(record, issue['iid'], external_id)
        return f"Issue #{issue['iid']}: {issue['web_url']}"


@mcp.tool()
def update_ticket(project: str, ticket: str, title: str | None = None, type: str | None = None,
                  status: str | None = None, responsible: str | None = None,
                  context: str | None = None, goal: str | None = None,
                  requirements: str | None = None, acceptance_criteria: str | None = None,
                  risks: str | None = None, open_questions: str | None = None,
                  references: str | None = None, first_approach: str | None = None) -> str:
    """Bestehendes Ticket ändern — nur gesetzte Parameter überschreiben, der Rest bleibt erhalten.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Dateiname-ID (z.B. "042") bei internal, UUID bei maestro,
             Issue-IID bei gitlab.
    Alle übrigen Parameter: None bedeutet unverändert.
    """
    record = _project_record(project)
    system = _target_system(record)
    sections = {k: v for k, v in {
        'Kontext': context,
        'Ziel': goal,
        'Anforderungen': requirements,
        'Akzeptanzkriterien': acceptance_criteria,
        'Risiken': risks,
        'Offene Fragen': open_questions,
        'Erste Umsetzungsidee': first_approach,
    }.items() if v is not None}
    meta = {k: v for k, v in {
        'typ': type,
        'status': status,
        'verantwortlich': responsible,
        'referenzen': references,
    }.items() if v is not None}

    if system == 'internal':
        root = project_directory(record)
        path = _find_ticket_path(root, ticket)
        current = path.read_text(encoding='utf-8')
        baseline_hash = hashlib.sha256(current.encode('utf-8')).hexdigest()
        content = _render(current, title or _current_title(current, 'Ticket'), meta, sections)
        if hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest() != baseline_hash:
            raise RuntimeError(
                f'{path}: Datei wurde zwischen Lesen und Schreiben von update_ticket() geändert — '
                'Schreibvorgang abgebrochen.'
            )
        path.write_text(content, encoding='utf-8')
        return str(path)

    if system == 'maestro':
        fields = {k: v for k, v in {
            'title': title,
            'type': type,
            'status': status,
            'context': context,
            'goal': goal,
            'requirements': requirements,
            'acceptance_criteria': acceptance_criteria,
            'risks': risks,
            'open_questions': open_questions,
        }.items() if v is not None}
        return _maestro_update('tickets', ticket, fields)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        data = {}
        if title is not None:
            data['title'] = title
        if sections or meta:
            issue = _gitlab_get(f'projects/{gitlab_project_id}/issues/{ticket}')
            data['description'] = _render(issue.get('description') or '', '', meta, sections)
        if data:
            _gitlab_put(f'projects/{gitlab_project_id}/issues/{ticket}', data)
        return f'Issue #{ticket} aktualisiert'


@mcp.tool()
def list_tickets(project: str, folder: str | None = None) -> str:
    """Offene Tickets eines Projekts auflisten.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    folder:  bei `internal` optional `open`/`backlog`/`completed`/`discarded`;
             ohne Angabe `open`+`backlog` (offene Tickets).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        folders = (folder,) if folder else ('open', 'backlog')
        if folder and folder not in _TICKET_DIRS:
            raise RuntimeError(f'Unbekannter Ordner: {folder}')
        entries = []
        for f in folders:
            for path in sorted((root / 'docs' / 'tickets' / f).glob('*.md')):
                meta = _ticket_meta(path.read_text(encoding='utf-8'))
                entries.append({'folder': f, 'file': path.name, **meta})
        return json.dumps(entries, ensure_ascii=False)

    if system == 'maestro':
        return json.dumps(_maestro_agent_list(_find_maestro_url(), 'tickets', project=project), ensure_ascii=False)

    if system == 'gitlab':
        ops = _load_operations_module('gitlab')
        return json.dumps(ops.list_tickets(record), ensure_ascii=False)


@mcp.tool()
def view_ticket(project: str, ticket: str) -> str:
    """Vollständigen Inhalt eines Tickets liefern, unabhängig vom Lebenszyklusstand.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Dateiname-ID (`internal`), UUID (`maestro`) oder Issue-IID (`gitlab`).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        return _find_ticket_path(root, ticket).read_text(encoding='utf-8')

    if system == 'maestro':
        return _fetch_record_markdown(_find_maestro_url(), 'tickets', ticket)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        issue = _gitlab_get(f'projects/{gitlab_project_id}/issues/{ticket}')
        return f"# {issue['title']}\n\n{issue['description']}"


@mcp.tool()
def create_implementation_plan(project: str, ticket: str, title: str, initial_situation: str,
                               implementation_goal: str, affected_areas: str, approach: str,
                               verification_plan: str, todo: str | None = None) -> str:
    """Implementierungsplan zu einem Ticket anlegen.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    title:   Titel des Plans, max. 5 Wörter.
    todo:    optional, UUID eines Maestro-Ticket-Todos. Passt es zu Ticket und aktuellem
             Status (`approved` ohne aktiven Plan), werden nach der Ablieferung Zuweisung
             und Todo-Abschluss im selben Aufruf ausgeführt. Passt es nicht, bricht der
             Aufruf vor jeder Ablieferung mit der konkreten Abweichung ab.
    """
    _require_short_title(title)
    record = _project_record(project)
    system = _target_system(record)

    todo_ops = todo_completion = base_url = ticket_obj = todo_record = None
    if todo is not None:
        todo_ops, todo_completion, base_url, ticket_obj, todo_record = _resolve_todo(
            system, record, ticket, 'implementation-plan', todo
        )

    today = date.today().isoformat()
    now = datetime.now().strftime('%H:%M')
    sections = {
        'Ausgangslage': initial_situation,
        'Umsetzungsziel': implementation_goal,
        'Betroffene Bereiche': affected_areas,
        'Ansatz': approach,
        'Verifikationsplan': verification_plan,
    }
    logbuch = (f'| Datum | Uhrzeit | Status | Details |\n'
               f'|-------|---------|--------|---------|\n'
               f'| {today} | {now} | Erstellt | |')

    if system == 'maestro':
        return _maestro_create('implementation-plans', {
            'ticket': ticket,
            'title': title,
            'plan_date': today,
            'initial_situation': initial_situation,
            'implementation_goal': implementation_goal,
            'affected_areas': affected_areas,
            'approach': approach,
            'verification_plan': verification_plan,
        })

    meta = {'ticket': f'"#{ticket}"', 'plan_date': today, 'status': 'DRAFT'}
    plan_sections = {'Logbuch': logbuch, **sections}
    content = _render(_template('implementation-plan'), title, meta, plan_sections)
    filename = f'{today}_{ticket}_{_kebab(title)}.md'
    result = _deliver(system, record, ticket, content, filename, 'implementation-plan')
    if todo is not None:
        todo_completion.complete_ticket_todo(
            base_url, todo_ops, record, ticket, ticket_obj, todo_record, 'implementation-plan'
        )
    return result


@mcp.tool()
def list_implementation_plans(project: str, ticket: str) -> str:
    """Implementierungspläne eines Tickets auflisten.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        entries = [
            {'file': path.name}
            for path in sorted((root / 'docs' / 'plans').glob(f'*_{ticket}_*.md'))
        ]
        return json.dumps(entries, ensure_ascii=False)

    if system == 'maestro':
        return json.dumps(
            _maestro_agent_list(_find_maestro_url(), 'implementation-plans', ticket_uuid=ticket), ensure_ascii=False
        )

    if system == 'gitlab':
        ops = _load_operations_module('gitlab')
        notes = ops.list_notes(record, ticket)
        entries = [
            {'note_id': n['note_id'], 'title': _current_title(n['body'], 'Implementierungsplan')}
            for n in notes if n['body'].startswith('# Implementierungsplan:')
        ]
        return json.dumps(entries, ensure_ascii=False)


@mcp.tool()
def view_implementation_plan(project: str, ticket: str, plan: str) -> str:
    """Vollständigen Inhalt eines Implementierungsplans liefern.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    plan:    Dateiname (`internal`), UUID (`maestro`) oder `note_id` (`gitlab`).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        return (root / 'docs' / 'plans' / plan).read_text(encoding='utf-8')

    if system == 'maestro':
        return _fetch_record_markdown(_find_maestro_url(), 'implementation-plans', plan)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        return _gitlab_get(f'projects/{gitlab_project_id}/issues/{ticket}/notes/{plan}')['body']


@mcp.tool()
def update_implementation_plan(project: str, ticket: str, plan: str, status: str = 'DRAFT') -> str:
    """Bestehenden Implementierungsplan ändern — nur `status` wird geschrieben.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    plan:    Dateiname (`internal`), UUID (`maestro`) oder `note_id` (`gitlab`).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'maestro':
        return _maestro_update('implementation-plans', plan, {'status': status})

    if system == 'internal':
        root = project_directory(record)
        path = root / 'docs' / 'plans' / plan
        content = path.read_text(encoding='utf-8')
        updated = re.sub(r'(?m)^(status:\s*)\S+', rf'\g<1>{status}', content, count=1)
        path.write_text(updated, encoding='utf-8')
        return str(path)

    if system == 'gitlab':
        ops = _load_operations_module('gitlab')
        gitlab_project_id = _gitlab_project_id(record)
        current = _gitlab_get(f'projects/{gitlab_project_id}/issues/{ticket}/notes/{plan}')
        updated = re.sub(r'(?m)^(status:\s*)\S+', rf'\g<1>{status}', current['body'], count=1)
        ops.update_comment(record, ticket, plan, updated)
        return f'Kommentar {plan} aktualisiert'


@mcp.tool()
def create_walkthrough(project: str, ticket: str, title: str, summary: str,
                       implemented_changes: str, technical_details: str, deviations: str,
                       tests_review: str, open_points: str, learning_reflection: str,
                       implementation_plan: str = '', todo: str | None = None) -> str:
    """Walkthrough zu einer abgeschlossenen Umsetzung anlegen.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    todo:    optional, UUID eines Maestro-Ticket-Todos. Passt es zu Ticket und aktuellem
             Status (`doing`), werden nach der Ablieferung Zuweisung, Statusübergang auf
             `review` und Todo-Abschluss im selben Aufruf ausgeführt. Passt es nicht, bricht
             der Aufruf vor jeder Ablieferung mit der konkreten Abweichung ab.
    """
    record = _project_record(project)
    system = _target_system(record)

    todo_ops = todo_completion = base_url = ticket_obj = todo_record = None
    if todo is not None:
        todo_ops, todo_completion, base_url, ticket_obj, todo_record = _resolve_todo(
            system, record, ticket, 'walkthrough', todo
        )

    today = date.today().isoformat()
    sections = {
        'Zusammenfassung': summary,
        'Umgesetzte Änderungen': implemented_changes,
        'Technische Details': technical_details,
        'Abweichungen': deviations,
        'Tests & Review': tests_review,
        'Offene Punkte': open_points,
        'Erkenntnisse & Reflexion': learning_reflection,
    }

    if system == 'maestro':
        result = _maestro_create('walkthroughs', {
            'ticket': ticket,
            'title': title,
            'walkthrough_date': today,
            'implementation_plan': implementation_plan,
            'summary': summary,
            'implemented_changes': implemented_changes,
            'technical_details': technical_details,
            'deviations': deviations,
            'tests_review': tests_review,
            'open_points': open_points,
            'learning_reflection': learning_reflection,
        })
        if implementation_plan:
            update_implementation_plan(project, ticket, implementation_plan, status='COMPLETED')
        return result

    meta = {
        'ticket': f'"#{ticket}"',
        'walkthrough_date': today,
        'implementation_plan': f'"{implementation_plan}"',
    }
    content = _render(_template('walkthrough'), title, meta, sections)
    filename = f'{today}_{ticket}_{_kebab(title)}.md'
    result = _deliver(system, record, ticket, content, filename, 'walkthrough')
    if implementation_plan:
        update_implementation_plan(project, ticket, implementation_plan, status='COMPLETED')
    if todo is not None:
        todo_completion.complete_ticket_todo(
            base_url, todo_ops, record, ticket, ticket_obj, todo_record, 'walkthrough'
        )
    return result


@mcp.tool()
def list_walkthroughs(project: str, ticket: str) -> str:
    """Walkthroughs eines Tickets auflisten.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        entries = [
            {'file': path.name}
            for path in sorted((root / 'docs' / 'walkthroughs').glob(f'*_{ticket}_*.md'))
        ]
        return json.dumps(entries, ensure_ascii=False)

    if system == 'maestro':
        return json.dumps(
            _maestro_agent_list(_find_maestro_url(), 'walkthroughs', ticket_uuid=ticket), ensure_ascii=False
        )

    if system == 'gitlab':
        ops = _load_operations_module('gitlab')
        notes = ops.list_notes(record, ticket)
        entries = [
            {'note_id': n['note_id'], 'title': _current_title(n['body'], 'Walkthrough')}
            for n in notes if n['body'].startswith('# Walkthrough:')
        ]
        return json.dumps(entries, ensure_ascii=False)


@mcp.tool()
def view_walkthrough(project: str, ticket: str, walkthrough: str) -> str:
    """Vollständigen Inhalt eines Walkthroughs liefern.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    ticket:  Ticket-Bezug — Nummer bei internal, UUID bei maestro, Issue-IID bei gitlab.
    walkthrough: Dateiname (`internal`), UUID (`maestro`) oder `note_id` (`gitlab`).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        return (root / 'docs' / 'walkthroughs' / walkthrough).read_text(encoding='utf-8')

    if system == 'maestro':
        return _fetch_record_markdown(_find_maestro_url(), 'walkthroughs', walkthrough)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        return _gitlab_get(f'projects/{gitlab_project_id}/issues/{ticket}/notes/{walkthrough}')['body']


@mcp.tool()
def create_milestone(project: str, name: str, description: str, target_date: str,
                     version: str = '', tickets: str = '') -> str:
    """Milestone im Ticketsystem des Projekts anlegen.

    project:     UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    name:        Titel des Milestones, max. 5 Wörter.
    target_date: Zieldatum (YYYY-MM-DD).
    version:     Versionswert, falls der Milestone einer Version entspricht.
    tickets:     Ticket-Referenzen als Markdown-Liste (internal), sonst ungenutzt.
    """
    _require_short_title(name)
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        meta = {
            'milestone': f'"{name}"',
            'version': f'"{version}"',
            'target_date': target_date,
        }
        sections = {'Beschreibung': description, 'Tickets': tickets}
        content = _render(_template('milestone'), name, meta, sections)
        return _write(root / 'docs' / 'milestones' / f'{version or _kebab(name)}.md', content)

    if system == 'maestro':
        fields = {
            'project': project,
            'name': name,
            'description': description,
            'target_date': target_date,
        }
        if version:
            fields['version'] = version
        return _maestro_create('milestones', fields)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        milestone = _gitlab_post(f'projects/{gitlab_project_id}/milestones', {
            'title': name,
            'description': description,
            'due_date': target_date,
        })
        return f"Milestone {milestone['id']}: {milestone['web_url']}"


@mcp.tool()
def list_milestones(project: str) -> str:
    """Milestones eines Projekts auflisten.

    project: UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        entries = [
            {'file': path.name, 'title': _current_title(path.read_text(encoding='utf-8'), '')}
            for path in sorted((root / 'docs' / 'milestones').glob('*.md'))
        ]
        return json.dumps(entries, ensure_ascii=False)

    if system == 'maestro':
        return json.dumps(
            _maestro_agent_list(_find_maestro_url(), 'milestones', project=project), ensure_ascii=False
        )

    if system == 'gitlab':
        ops = _load_operations_module('gitlab')
        return json.dumps(ops.list_milestones(record), ensure_ascii=False)


@mcp.tool()
def view_milestone(project: str, milestone: str) -> str:
    """Vollständigen Inhalt eines Milestones liefern.

    project:   UUID des Maestro-Projektrecords — bestimmt das Zielsystem.
    milestone: Dateiname (`internal`), UUID (`maestro`) oder Milestone-ID (`gitlab`).
    """
    record = _project_record(project)
    system = _target_system(record)

    if system == 'internal':
        root = project_directory(record)
        return (root / 'docs' / 'milestones' / milestone).read_text(encoding='utf-8')

    if system == 'maestro':
        return _fetch_record_markdown(_find_maestro_url(), 'milestones', milestone)

    if system == 'gitlab':
        gitlab_project_id = _gitlab_project_id(record)
        result = _gitlab_get(f'projects/{gitlab_project_id}/milestones/{milestone}')
        return f"# {result['title']}\n\n{result['description'] or ''}"


if __name__ == '__main__':
    mcp.run(transport='stdio')
