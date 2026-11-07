#!/usr/bin/env python3
"""operations — ticketsystemspezifische Funktionen für die interne Quelle
(`ticket_system == internal`) der `work-routine`/Artefakt-Mechanik.

Stellt `list_assigned`, `read_ticket`, `write_status`, `write_assignee`,
`write_description`, `write_comment` und `person_external_id` bereit — dieselben
Funktionsnamen wie jedes andere Modul unter `ticket_systems/`. Tickets liegen als Datei
unter `docs/tickets/<folder>/`, das `Verantwortlich`-Meta-Feld ist zugleich Assignee und
`assigned_by`.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

_MAESTRO_TOOLS_DIR = Path(__file__).resolve().parents[3] / 'echo-maestro' / 'tools'

if str(_MAESTRO_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_MAESTRO_TOOLS_DIR))

import maestro_client as mc  # noqa: E402
from maestro_client import project_directory  # noqa: E402

_ARTIFACT_SUBDIR = {
    'implementation-plan': 'plans',
    'walkthrough': 'walkthroughs',
}


def _parse_comments(content: str) -> list[dict]:
    match = re.search(r'(?ms)^## Kommentare\s*\n(.*?)(?=\n## |\Z)', content)
    if not match:
        return []
    comments = []
    for block in re.split(r'(?m)^### ', match.group(1))[1:]:
        lines = block.splitlines()
        identifier = lines[0].strip()
        author = created_at = reply_to = None
        body_start = len(lines)
        for i, line in enumerate(lines[1:], start=1):
            field = re.match(r'^-\s*(Autor|Zeitpunkt|Antwort auf):\s*(.*)$', line)
            if not field:
                body_start = i
                break
            if field[1] == 'Autor':
                author = field[2].strip()
            elif field[1] == 'Zeitpunkt':
                created_at = field[2].strip()
            elif field[1] == 'Antwort auf':
                reply_to = field[2].strip() or None
        body = '\n'.join(lines[body_start:]).strip('\n')
        comments.append({
            'identifier': identifier,
            'author_name': author,
            'created_at': created_at,
            'reply_to': reply_to,
            'body': body,
        })
    return comments


def list_assigned(project: dict) -> list[dict]:
    base_url = mc._find_maestro_url()
    current_agent = person_external_id(project, mc.current_agent_person_uuid(base_url))
    root = project_directory(project)
    entries = []
    for path in sorted((root / 'docs' / 'tickets' / 'open').glob('*.md')):
        content = path.read_text(encoding='utf-8')
        match_id = re.search(r'^- ID:\s*(.+)$', content, re.MULTILINE)
        if not match_id:
            continue
        verantwortlich_match = re.search(r'^- Verantwortlich:\s*(.+)$', content, re.MULTILINE)
        if not verantwortlich_match or verantwortlich_match.group(1).strip() != current_agent:
            continue
        title = content.splitlines()[0][2:].strip()
        title = title.split(': ', 1)[1] if ': ' in title else title
        entries.append({'ticket_number': match_id.group(1).strip(), 'title': title, 'updated_at': None})
    return entries


def _ticket_path(project: dict, ticket_number) -> Path:
    root = project_directory(project)
    for folder in ('open', 'backlog', 'completed', 'discarded'):
        matches = list((root / 'docs' / 'tickets' / folder).glob(f'{ticket_number}[_-]*.md'))
        if matches:
            return matches[0]
    raise RuntimeError(f'Ticket {ticket_number} nicht gefunden.')


def read_ticket(project: dict, ticket_number) -> dict:
    path = _ticket_path(project, ticket_number)
    content = path.read_text(encoding='utf-8')

    def _meta(label):
        m = re.search(rf'^- {label}:\s*(.+)$', content, re.MULTILINE)
        return m.group(1).strip() if m else None

    title = content.splitlines()[0][2:].strip()
    title = title.split(': ', 1)[1] if ': ' in title else title
    verantwortlich = _meta('Verantwortlich')
    return {
        'ticket_number': ticket_number,
        'title': title,
        'description': content,
        'web_url': None,
        'assignees': [{'id': verantwortlich, 'name': verantwortlich}] if verantwortlich else [],
        'comments': _parse_comments(content),
        'assigned_by': verantwortlich,
        'assigned_at': None,
        'status': (_meta('Status') or '').lower(),
        'type': (_meta('Typ') or '').lower(),
    }


def write_status(project: dict, ticket_number, status: str) -> None:
    path = _ticket_path(project, ticket_number)
    content = path.read_text(encoding='utf-8')
    updated = re.sub(r'(?m)^(- Status:\s*).+$', lambda m: m.group(1) + status, content, count=1)
    path.write_text(updated, encoding='utf-8')


def write_assignee(project: dict, ticket_number, target, purpose: str | None = None) -> None:
    path = _ticket_path(project, ticket_number)
    content = path.read_text(encoding='utf-8')
    updated = re.sub(r'(?m)^(- Verantwortlich:\s*).+$', lambda m: m.group(1) + str(target), content, count=1)
    path.write_text(updated, encoding='utf-8')


def person_external_id(project: dict, person_uuid: str) -> str:
    base_url = mc._find_maestro_url()
    person = mc._http_get(base_url, f'persons/{person_uuid}/agent')
    name = ' '.join(part for part in (person.get('first_name'), person.get('last_name')) if part)
    return name or person.get('ucid') or person_uuid


def write_description(project: dict, ticket_number, file_path: str) -> None:
    path = _ticket_path(project, ticket_number)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    path.write_text(content, encoding='utf-8')


def write_comment(project: dict, ticket_number, text: str) -> None:
    path = _ticket_path(project, ticket_number)
    content = path.read_text(encoding='utf-8')
    base_url = mc._find_maestro_url()
    author = person_external_id(project, mc.current_agent_person_uuid(base_url))
    timestamp = datetime.now().isoformat()

    existing = [int(n) for n in re.findall(rf'^### {re.escape(str(ticket_number))}-(\d+)$', content, re.MULTILINE)]
    identifier = f'{ticket_number}-{max(existing, default=0) + 1}'
    block = (
        f'\n### {identifier}\n'
        f'- Autor: {author}\n'
        f'- Zeitpunkt: {timestamp}\n'
        f'- Antwort auf: \n\n'
        f'{text}\n'
    )

    if re.search(r'(?m)^## Kommentare\s*$', content):
        content = content.rstrip('\n') + '\n' + block
    else:
        content = content.rstrip('\n') + '\n\n## Kommentare\n' + block
    path.write_text(content, encoding='utf-8')


def deliver_artifact(project: dict, identifier: str, temp_file_path: str, artifact_type: str) -> str:
    root = project_directory(project)
    dest = root / 'docs' / _ARTIFACT_SUBDIR[artifact_type] / Path(temp_file_path).name
    Path(temp_file_path).rename(dest)
    return str(dest)
