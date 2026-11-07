#!/usr/bin/env python3
"""
maestro_mcp_server.py — MCP-Server für Maestro-Integration im echo-Framework.

Acht Tools (#082 — typisierte Kommandos, keine freien Pfade):
  maestro_list       — Liste der Records eines Archetypes (GET /{archetype}/agent)
  maestro_record     — Einzelsatz mit Details als Markdown (GET /{archetype}/{id}/agent)
  maestro_create     — Datensatz anlegen; Bestätigung = frisch abgerufener Datensatz
  maestro_update     — Datensatz ändern; Bestätigung = frisch abgerufener Datensatz
  maestro_attach     — many_to_many-Verknüpfung anlegen (record_relations)
  maestro_detac h     — many_to_many-Verknüpfung lösen
  maestro_report     — Chronicle-Tagesbericht als Markdown (mit Größenlimit)
  maestro_skill      — Skill-Definition für einen Archetype (Felder, Regeln, Werte)
  maestro_archetypes — Liste der Archetypes mit Skill-Definition
  maestro_refs       — gecachte Referenzdaten (time-accounts/-categories, activity-types, todo-types)
  maestro_create_for_agent — Task/Todo im Auftrag eines anderen Agenten anlegen (owner_uuid/person auf Ziel-Agent)

HTTP-Zugriff (GET/POST) ist interne Mechanik dieses Servers; Routen werden ausschließlich
hier gebildet.

Konfiguration: liest maestro.base_url aus .agent/config.json (Pfad relativ zum Skript).

MCP-Eintrag in settings.local.json:
  {
    "mcpServers": {
      "echo-maestro": {
        "command": "python3",
        "args": [".agent/skills/echo-maestro/tools/maestro_mcp_server.py"]
      }
    }
  }

Voraussetzungen:
  python3 -m pip install fastmcp
"""

import json
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    sys.exit(
        "Fehler: fastmcp nicht installiert.\n"
        "Bitte installieren: python3 -m pip install fastmcp"
    )

from maestro_client import (
    _AGENT_DIR,
    _CACHE_DIR,
    _cache_path,
    _load_agent_auth,
    _obtain_token,
    _bearer_token,
    _refresh_token,
    _auth_headers,
    _find_maestro_url,
    _http_get,
    _http_post_json,
    _post_raw,
    _coerce_form_value,
    _form_fields,
    _identifier_from_content,
    _segment,
    _record_markdown,
    _fetch_record_markdown,
)

mcp = FastMCP("echo-maestro")

# Referenz-Cache (#067): selten wechselnde Stammdaten, lokal zwischengespeichert.
_REFS_TTL = timedelta(days=7)
_CHORE_RUN_META_PREFIX = 'chore_run_meta='


# Pro Archetype nur die für die Relationsauflösung benötigten Felder cachen.
_TRIM_FIELDS = {
    'time-accounts':   ('name', 'uuid', 'time_category_uuid', 'description'),
    'time-categories': ('name', 'uuid', 'description'),
    'activity-types':  ('name', 'ucid', 'uuid'),
    'todo-types':      ('name', 'ucid', 'uuid'),
}


def _validate_activity_duration(fields: dict) -> None:
    """Lehnt duration-Werte für activities ab, die nicht durch 5 teilbar sind (#139)."""
    raw = fields.get('duration')
    if raw is None:
        return
    try:
        d = int(raw)
    except (ValueError, TypeError):
        return
    if d > 0 and d % 5 != 0:
        floor = (d // 5) * 5
        ceil = floor + 5
        raise RuntimeError(
            f'Duration {d} ist ungültig. Gültige Werte: {floor} oder {ceil}.'
        )


def _check_activity_overlap(base_url: str, fields: dict) -> None:
    """Prüft vor dem Anlegen einer Activity auf Zeitkonflikt mit bestehenden Einträgen (#139)."""
    start_raw = fields.get('start_time')
    if not start_raw:
        return
    try:
        start_new = datetime.fromisoformat(str(start_raw))
    except ValueError:
        return
    duration_new = int(fields.get('duration', 0))
    end_new = start_new + timedelta(minutes=duration_new) if duration_new > 0 else None

    date_str = start_new.date().isoformat()
    try:
        result = _http_get(base_url, f'activities/agent?activity_date={date_str}&per_page=200')
    except RuntimeError:
        return
    records = result if isinstance(result, list) else result.get('data', [])

    for rec in records:
        attrs = rec.get('attributes', rec) if isinstance(rec, dict) else {}
        try:
            start_ex = datetime.fromisoformat(str(attrs.get('start_time', '')))
            dur_ex = int(attrs.get('duration', 0))
        except (ValueError, TypeError):
            continue
        if dur_ex <= 0:
            continue
        end_ex = start_ex + timedelta(minutes=dur_ex)

        if end_new is not None:
            overlap = start_new < end_ex and end_new > start_ex
        else:
            overlap = start_ex <= start_new < end_ex

        if overlap:
            name = attrs.get('name', '?')
            uuid = attrs.get('uuid', '?')
            raise RuntimeError(
                f'Zeitkonflikt: "{name}" ({uuid}) läuft '
                f'{start_ex.strftime("%H:%M")}–{end_ex.strftime("%H:%M")}.\n'
                f'Optionen:\n'
                f'1. Startzeit der neuen Activity anpassen: frühestens {end_ex.strftime("%H:%M")}\n'
                f'2. Bestehende Activity umbenennen und duration erweitern statt neue anlegen\n'
                f'3. Bestehende Activity kürzen und neue Activity ab {end_ex.strftime("%H:%M")} starten'
            )


def _floor_5(dt: datetime) -> datetime:
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)


def _ceil_5(dt: datetime) -> datetime:
    floored = _floor_5(dt)
    if dt.second == 0 and dt.microsecond == 0 and dt.minute % 5 == 0:
        return floored
    return floored + timedelta(minutes=5)


def _find_open_activity(base_url: str, date_str: str) -> dict | None:
    """Offene Activity (duration <= 0) eines Agenten am angegebenen Tag, falls vorhanden."""
    result = _http_get(base_url, f'activities/agent?activity_date={date_str}&per_page=200')
    records = result if isinstance(result, list) else result.get('data', [])
    open_records = []
    for rec in records:
        attrs = rec.get('attributes', rec) if isinstance(rec, dict) else {}
        try:
            dur = int(attrs.get('duration', 0))
        except (ValueError, TypeError):
            continue
        if dur <= 0:
            open_records.append(attrs)
    if len(open_records) > 1:
        raise RuntimeError(
            f'Mehr als eine offene Activity am {date_str} gefunden — Datenfehler, keine automatische Auswahl.'
        )
    return open_records[0] if open_records else None


def _write_activity(base_url: str, fields: dict, identifier: str | None) -> str:
    """Reiht sich in denselben Validierungs- und Schreibpfad wie maestro_create/maestro_update
    ein — keine Parallel-Implementierung des HTTP-Schreibwegs."""
    creating = identifier is None
    _validate_fields('activities', fields, creating=creating)
    _validate_activity_duration(fields)
    str_fields = _form_fields(fields)
    if creating:
        content = _post_raw(base_url, 'activities', str_fields)
        identifier = _identifier_from_content(content, 'activities')
    else:
        _post_raw(base_url, f'activities/{identifier}', str_fields)
    result = _fetch_record_markdown(base_url, 'activities', identifier)
    _invalidate_refs_for('activities')
    return result


def _validate_fields(archetype: str, fields: dict, creating: bool) -> None:
    """Prüft Schreib-Felder gegen die Skill-Definition des Archetypes (#084).

    Unbekannte Felder, fehlende Pflichtfelder beim Anlegen und ungültige ENUM-Werte
    führen zu lauten Fehlern — kein Request verlässt den Server mit Feldern außerhalb
    der Definition (Maestro ignoriert unbekannte Form-Felder stillschweigend)."""
    skill = _fetch_skill_definition(archetype)
    required = list(skill.get('required') or [])
    update_only = set(skill.get('update_only') or [])
    allowed = set(required)
    allowed.update(skill.get('optional') or [])
    allowed.update((skill.get('conditional') or {}).keys())
    relations = skill.get('relations') or {}
    allowed.update(relations.keys())
    if not creating:
        allowed.update(update_only)

    enum_values = skill.get('values') or {}

    problems = []
    wrong_phase = [k for k in fields if creating and k in update_only]
    unknown = [k for k in fields if k not in allowed and k not in wrong_phase]
    missing = [f for f in required if creating and f not in fields]

    if wrong_phase:
        problems.append(f'nur bei Update erlaubt: {", ".join(wrong_phase)}')
    if unknown:
        problems.append(f'unbekannte Felder: {", ".join(unknown)}')

    for field in sorted(fields):
        if field in unknown or field in wrong_phase:
            continue
        allowed_vals = enum_values.get(field)
        if allowed_vals and str(fields[field]) not in allowed_vals:
            problems.append(
                f'Feld "{field}" hat ungültigen Wert "{fields[field]}"'
                f' — erlaubte Werte: {", ".join(allowed_vals)}'
            )

    if missing:
        missing_parts = []
        for f in missing:
            hint = relations.get(f)
            if hint:
                missing_parts.append(f'{f} (Lookup: {hint})')
            else:
                missing_parts.append(f)
        problems.append(f'Pflichtfelder fehlen: {", ".join(missing_parts)}')

    if problems:
        raise RuntimeError(
            f'Write auf "{archetype}" abgelehnt — {"; ".join(problems)}. '
            f'Gültige Felder: {", ".join(sorted(allowed))}.'
        )


def _record_attrs(rec: object) -> dict:
    if not isinstance(rec, dict):
        raise RuntimeError(f'Unerwartete Record-Antwort: {type(rec).__name__}')
    return rec.get('attributes', rec)


def _extract_chore_run_meta(description: str | None) -> dict | None:
    for line in str(description or '').splitlines():
        line = line.strip()
        if not line.startswith(_CHORE_RUN_META_PREFIX):
            continue
        try:
            meta = json.loads(line[len(_CHORE_RUN_META_PREFIX):])
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Ungültige chore_run_meta in Task-Beschreibung: {e}')
        if isinstance(meta, dict):
            return meta
    return None


def _list_records(base_url: str, archetype: str, filters: dict | None = None, per_page: int = 10, page: int = 1) -> dict:
    params = {k: str(v) for k, v in (filters or {}).items()}
    params['per_page'] = str(per_page)
    params['page'] = str(page)
    return _http_get(base_url, f'{archetype}/agent?{urllib.parse.urlencode(params)}')


def _ensure_single_record(base_url: str, archetype: str, filters: dict) -> dict | None:
    result = _list_records(base_url, archetype, filters=filters, per_page=10, page=1)
    records = result if isinstance(result, list) else result.get('data', [])
    if len(records) > 1:
        raise RuntimeError(
            f'Mehrere Datensätze für {archetype} mit {filters} gefunden — keine automatische Auswahl.'
        )
    return records[0] if records else None


@mcp.tool()
def maestro_chore_start(identifier: str = '') -> dict:
    """Semantischer Chore-Start über UUID, Datum oder now.

    identifier:
      - leer  -> `POST /chores/start`
      - Datum -> `POST /chores/start/<YYYY-MM-DD>`
      - UUID  -> `POST /chores/start/<uuid>`
    """
    base_url = _find_maestro_url()
    raw = str(identifier or '').strip()
    path = 'chores/start'
    if raw:
        path += f'/{urllib.parse.quote(_segment(raw, "Identifier"), safe="")}'
    result = _http_post_json(base_url, path)
    if not isinstance(result, dict):
        raise RuntimeError('Chore-Start hat kein JSON-Objekt geliefert.')
    return result


@mcp.tool()
def maestro_task_start(task_uuid: str) -> dict:
    """Semantischer Task-Start über Task-UUID."""
    base_url = _find_maestro_url()
    result = _http_post_json(base_url, f'tasks/{_segment(task_uuid, "Task-UUID")}/start')
    if not isinstance(result, dict):
        raise RuntimeError('Task-Start hat kein JSON-Objekt geliefert.')
    return result


@mcp.tool()
def maestro_todo_complete(todo_uuid: str) -> str:
    """Idempotenter Todo-Abschluss über UUID.

    Der Server setzt `finished_at` beim Statuswechsel selbst.
    """
    base_url = _find_maestro_url()
    todo_uuid = _segment(todo_uuid, 'Todo-UUID')
    record = _http_get(base_url, f'todos/{todo_uuid}/agent')
    attrs = _record_attrs(record)
    if attrs.get('finished_at') or attrs.get('status') == 'DONE':
        return _record_markdown(record)
    return maestro_update('todos', todo_uuid, {'status': 'DONE'})


@mcp.tool()
def maestro_task_complete(task_uuid: str) -> str:
    """Idempotenter Task-Abschluss über UUID.

    Der Server setzt den Zielzustand semantisch; `finished_at` entsteht Maestro-seitig.
    """
    base_url = _find_maestro_url()
    task_uuid = _segment(task_uuid, 'Task-UUID')
    record = _http_get(base_url, f'tasks/{task_uuid}/agent')
    attrs = _record_attrs(record)
    if attrs.get('outcome') == 'DONE' or attrs.get('finished_at'):
        return _record_markdown(record)
    return maestro_update('tasks', task_uuid, {'outcome': 'DONE'})


@mcp.tool()
def maestro_chore_run_complete(task_uuid: str) -> str:
    """Idempotenter Abschluss des Chore-Fulfillments über Task-UUID."""
    base_url = _find_maestro_url()
    task_uuid = _segment(task_uuid, 'Task-UUID')
    task_record = _http_get(base_url, f'tasks/{task_uuid}/agent')
    task_attrs = _record_attrs(task_record)
    meta = _extract_chore_run_meta(task_attrs.get('description'))
    if not meta:
        raise RuntimeError(
            f'Task {task_uuid} enthält keine chore_run_meta — Chore-Fulfillment kann nicht abgeleitet werden.'
        )

    chore_uuid = _segment(str(meta.get('chore_uuid') or ''), 'Chore-UUID')
    chore_date = str(meta.get('chore_date') or '').strip()
    person_uuid = str(task_attrs.get('person_uuid') or meta.get('person_uuid') or '').strip()

    if not chore_date:
        raise RuntimeError(f'Task {task_uuid} enthält keine chore_date in chore_run_meta.')
    if not person_uuid:
        raise RuntimeError(
            f'Task {task_uuid} liefert keinen Person-Kontext für das Chore-Fulfillment.'
        )

    existing = _ensure_single_record(
        base_url,
        'chore-fulfillments',
        {'chore_uuid': chore_uuid, 'chore_date': chore_date, 'person_uuid': person_uuid},
    )
    if existing is not None and _record_attrs(existing).get('status') == 'DONE':
        return (
            f'Chore-Fulfillment bereits DONE: chore={chore_uuid}, '
            f'date={chore_date}, person={person_uuid}, task={task_uuid}'
        )

    _post_raw(
        base_url,
        f'chores/{chore_uuid}/toggle',
        {'chore_date': chore_date, 'person_uuid': person_uuid},
    )
    return (
        f'Chore-Fulfillment auf DONE gesetzt: chore={chore_uuid}, '
        f'date={chore_date}, person={person_uuid}, task={task_uuid}'
    )


@mcp.tool()
def maestro_list(archetype: str, filters: dict | None = None, per_page: int = 10, page: int = 1) -> dict:
    """Liste der Records eines Archetypes — kompaktes flaches JSON mit Pagination.

    archetype: Name des Archetypes, z.B. "tasks", "todos", "activities"
    filters:   optionale Gleichheitsfilter auf Feldnamen des Archetypes,
               z.B. {"task_uuid": "..."} oder {"status": "DONE"}
    per_page:  maximale Anzahl gelieferter Records (Standard 10)
    page:      Seite (Standard 1)

    Hinweis: Records ohne gesetzten Status gelten als offen und tragen kein
    status-Feld — offene Einträge ohne status-Filter abrufen.
    """
    base_url = _find_maestro_url()
    archetype = _segment(archetype, 'Archetype')
    return _list_records(base_url, archetype, filters=filters, per_page=per_page, page=page)


@mcp.tool()
def maestro_record(archetype: str, identifier: str) -> str:
    """Einzelner Datensatz mit Details — Markdown, Relationen aufgelöst.

    archetype:  Name des Archetypes, z.B. "tasks", "activities"
    identifier: UUID des Datensatzes

    Felder und Regeln eines Archetypes liefert maestro_skill(archetype).
    """
    base_url = _find_maestro_url()
    return _fetch_record_markdown(base_url, _segment(archetype, 'Archetype'), _segment(identifier, 'Identifier'))


@mcp.tool()
def maestro_create(archetype: str, fields: dict) -> str:
    """Neuen Datensatz anlegen. Bestätigung ist der frisch abgerufene Datensatz (Markdown).

    archetype: Name des Archetypes, z.B. "activities", "tasks", "todos"
    fields:    Felder laut maestro_skill(archetype); Werte werden als Strings übertragen.
    """
    base_url = _find_maestro_url()
    archetype = _segment(archetype, 'Archetype')
    _validate_fields(archetype, fields, creating=True)
    if archetype == 'activities':
        _validate_activity_duration(fields)
        _check_activity_overlap(base_url, fields)
    content = _post_raw(base_url, archetype, _form_fields(fields))
    identifier = _identifier_from_content(content, archetype)
    result = _fetch_record_markdown(base_url, archetype, identifier)
    # Referenz-Cache nach Writes auf Stammdaten neu aufbauen, damit selbst angelegte
    # Datensätze sofort über maestro_refs sichtbar sind (#067).
    _invalidate_refs_for(archetype)
    return result


@mcp.tool()
def maestro_update(archetype: str, identifier: str, fields: dict) -> str:
    """Bestehenden Datensatz ändern. Bestätigung ist der frisch abgerufene Datensatz (Markdown).

    archetype:  Name des Archetypes
    identifier: UUID des Datensatzes
    fields:     zu ändernde Felder laut maestro_skill(archetype)
    """
    base_url = _find_maestro_url()
    archetype = _segment(archetype, 'Archetype')
    identifier = _segment(identifier, 'Identifier')
    _validate_fields(archetype, fields, creating=False)
    if archetype == 'activities':
        _validate_activity_duration(fields)
    _post_raw(base_url, f'{archetype}/{identifier}', _form_fields(fields))
    result = _fetch_record_markdown(base_url, archetype, identifier)
    _invalidate_refs_for(archetype)
    return result


@mcp.tool()
def maestro_assign_task_person(identifier: str, person_uuid: str) -> str:
    """Setzt `person` bei einem bestehenden Task auf eine andere Person — einziger Zweck
    dieses Tools, kein Ersatz für maestro_update. `person` ist absichtlich nicht Teil von
    dessen allgemeiner Feldliste für "tasks" (Standard: Task gehört dem Ersteller); dieses
    Tool ist der einzige Weg, das für eine andere Person zu ändern.

    identifier:  UUID des Tasks
    person_uuid: UUID der Person, der der Task künftig gehören soll
    """
    base_url = _find_maestro_url()
    identifier = _segment(identifier, 'Identifier')
    _post_raw(base_url, f'tasks/{identifier}', _form_fields({'person': person_uuid}))
    result = _fetch_record_markdown(base_url, 'tasks', identifier)
    _invalidate_refs_for('tasks')
    return result


def _resolve_agent(base_url: str, agent_name: str) -> dict:
    agent = _ensure_single_record(base_url, 'agents', {'display_name': agent_name})
    if agent is None:
        raise RuntimeError(f'Kein Agent mit display_name={agent_name!r} gefunden.')
    return agent


@mcp.tool()
def maestro_create_for_agent(archetype: str, fields: dict, agent_name: str) -> str:
    """Legt einen Task oder ein Todo im Auftrag eines anderen Agenten an — `owner_uuid` wird
    auf den Ziel-Agenten gesetzt (bei `tasks` zusätzlich `person`), statt auf den aufrufenden
    Agenten. `owner_uuid`/`person` sind absichtlich nicht Teil der allgemeinen Feldliste von
    `maestro_create` (siehe `maestro_assign_task_person`); dieses Tool ist der einzige Weg,
    einen neuen Datensatz direkt einem anderen Agenten zuzuordnen.

    archetype:  "tasks" oder "todos" — kein anderer Archetype unterstützt.
    fields:     Felder laut maestro_skill(archetype), ohne owner_uuid/person.
    agent_name: display_name des Ziel-Agenten (Archetype "agents").

    Rückgabe: der Datensatz-Stand direkt nach der Anlage (vor der Owner-/Person-Umstellung —
    danach ist er für den Aufrufer über die reguläre Route nicht mehr abrufbar, da
    owner-gescoped), ergänzt um eine Zeile mit der durchgeführten Umstellung.
    """
    if archetype not in ('tasks', 'todos'):
        raise RuntimeError(f'archetype muss "tasks" oder "todos" sein, nicht {archetype!r}.')
    base_url = _find_maestro_url()
    agent = _resolve_agent(base_url, agent_name)
    _validate_fields(archetype, fields, creating=True)
    content = _post_raw(base_url, archetype, _form_fields(fields))
    identifier = _identifier_from_content(content, archetype)
    result = _fetch_record_markdown(base_url, archetype, identifier)
    owner_fields = {'owner_uuid': agent['uuid']}
    reassignment = f"Owner auf {agent_name} ({agent['uuid']}) umgestellt"
    if archetype == 'tasks':
        owner_fields['person'] = agent['person_uuid']
        reassignment += f", Person auf {agent['person_uuid']}"
    _post_raw(base_url, f'{archetype}/{identifier}', _form_fields(owner_fields))
    _invalidate_refs_for(archetype)
    return f'{result}\n\n{reassignment}.'


@mcp.tool()
def maestro_task_with_todos(todos: list, task_fields: dict = None, task_uuid: str = None) -> str:
    """Legt einen Task zusammen mit mehreren Todos in einem Tool-Call an, oder ergänzt
    Todos zu einem bereits bestehenden Task — sequenziell über die bestehenden
    Single-Archetype-Writes, keine Backend-Transaktion (#066).

    Genau eines von task_fields/task_uuid angeben:
    - task_fields: Felder laut maestro_skill("tasks") — legt einen neuen Task an.
    - task_uuid: UUID eines bestehenden Tasks — Todos werden diesem Task hinzugefügt.
    todos: Liste von Feld-Dicts laut maestro_skill("todos"), je ohne das Feld "task" —
           die Task-Relation wird automatisch gesetzt.

    Kein Rollback bei Teilfehlschlag: bereits angelegte Datensätze (Task, vorherige
    Todos) bleiben bestehen; ein Fehler bei einem Todo bricht die Ausführung ab und wird
    unverändert weitergereicht.
    """
    base_url = _find_maestro_url()
    if (task_fields is None) == (task_uuid is None):
        raise RuntimeError(
            'Genau eines von task_fields oder task_uuid angeben, nicht beides und nicht keins.'
        )

    if task_fields is not None:
        _validate_fields('tasks', task_fields, creating=True)
        content = _post_raw(base_url, 'tasks', _form_fields(task_fields))
        task_id = _identifier_from_content(content, 'tasks')
        _invalidate_refs_for('tasks')
    else:
        task_id = _segment(task_uuid, 'Task-UUID')

    todo_ids = []
    for todo_fields in todos:
        fields = dict(todo_fields)
        fields['task'] = task_id
        _validate_fields('todos', fields, creating=True)
        content = _post_raw(base_url, 'todos', _form_fields(fields))
        todo_ids.append(_identifier_from_content(content, 'todos'))

    parts = [_fetch_record_markdown(base_url, 'tasks', task_id)]
    for todo_id in todo_ids:
        parts.append(_fetch_record_markdown(base_url, 'todos', todo_id))
    return '\n\n'.join(parts)


@mcp.tool()
def maestro_attach(archetype: str, identifier: str, relation: str, target_uuid: str) -> str:
    """Verknüpft einen Ziel-Datensatz über eine im Archetype-Spec deklarierte
    many_to_many-Relation (Ablage in record_relations; Dublettenschutz übernimmt Maestro).

    archetype:   Parent-Archetype, z.B. "chronicle-days"
    identifier:  UUID des Parent-Datensatzes
    relation:    Relationsname aus dem Spec, z.B. "day_confirmed_assertions",
                 "day_worked_tickets" — gültige Namen nennt die Spec-Description
                 bzw. das Skill-YAML des Parent-Archetypes
    target_uuid: UUID des zu verknüpfenden Ziel-Datensatzes
    """
    base_url = _find_maestro_url()
    archetype = _segment(archetype, 'Archetype')
    identifier = _segment(identifier, 'Identifier')
    relation = _segment(relation, 'Relation')
    _post_raw(base_url, f'{archetype}/{identifier}/relations/{relation}/attach',
              {'target_uuid': str(target_uuid)})
    return f'Verknüpft: {archetype}/{identifier} —[{relation}]→ {target_uuid}'


@mcp.tool()
def maestro_detach(archetype: str, identifier: str, relation: str, target_uuid: str) -> str:
    """Löst eine bestehende many_to_many-Verknüpfung (record_relations) wieder.

    archetype:   Parent-Archetype, z.B. "chronicle-days"
    identifier:  UUID des Parent-Datensatzes
    relation:    Relationsname aus dem Spec
    target_uuid: UUID des bisher verknüpften Ziel-Datensatzes
    """
    base_url = _find_maestro_url()
    archetype = _segment(archetype, 'Archetype')
    identifier = _segment(identifier, 'Identifier')
    relation = _segment(relation, 'Relation')
    _post_raw(base_url, f'{archetype}/{identifier}/relations/{relation}/detach',
              {'target_uuid': str(target_uuid)})
    return f'Gelöst: {archetype}/{identifier} —[{relation}]→ {target_uuid}'


@mcp.tool()
def maestro_tracking(name: str, time_account: str, activity_type: str | None = None,
                      task: str | None = None, description: str | None = None,
                      ticket_number: int | None = None, project: str | None = None) -> str:
    """Fortsetzen, aktualisieren oder abschließen+neu-anlegen der laufenden Activity —
    Zeitabruf, 5-Minuten-Rasterung und die kanonische Namensbildung übernimmt dieses Tool.
    Lücken und Sessionwechsel korrigiert der maestro-tracking-Hook der Plattform im
    Hintergrund; zum Aufrufzeitpunkt ist die offene Activity bereinigt.

    name:          rohe Bezeichnung der ausgeführten Tätigkeit — ohne Projekt- oder
                   Ticketpräfix; ein enthaltenes `#<Ziffern>` oder der aufgelöste
                   Projektname (falls `project` gesetzt) wird abgelehnt
    time_account:  Zeitkonto-UUID (maestro_refs())
    activity_type: optional, UCID des ActivityTypes
    task:          optional, Task-UUID
    description:   optional
    ticket_number: optional, erzeugt den Präfix `#<ticket_number>: `
    project:       optional, nur zusammen mit ticket_number — Projekt-UUID; bei vom
                   Zeitkonto abweichendem Projektnamen `<projekt-ucid>#<ticket_number>: `

    Fortsetzung setzt unverändertes `name` UND unverändertes `time_account` voraus; ein
    Zeitkontowechsel erzeugt immer eine neue Activity, auch bei unverändertem Namen.

    Rückgabe: erste Zeile benennt die ausgeführte Aktion (fortgesetzt / neu angelegt /
    geschlossen + neu angelegt (Themenwechsel) / erweitert (Themenwechsel innerhalb des
    5-Minuten-Rasters)), danach der Markdown-Datensatz.
    """
    base_url = _find_maestro_url()
    now = datetime.now()
    today = now.date().isoformat()

    if project and not ticket_number:
        raise RuntimeError('project ist nur zusammen mit ticket_number zulässig.')
    if ticket_number and re.search(r'#\d+', name):
        raise RuntimeError(
            'name enthält bereits eine Ticketnummer — ticket_number verwenden, der Präfix wird automatisch erzeugt.'
        )

    project_name = None
    project_ucid = None
    if project:
        project_record = _http_get(base_url, f'projects/{project}/agent')
        project_attrs = project_record.get('attributes', project_record) if isinstance(project_record, dict) else {}
        project_name = project_attrs.get('name')
        project_ucid = project_attrs.get('ucid')
        if project_name and project_name.lower() in name.lower():
            raise RuntimeError(
                'name enthält bereits den Projektnamen — project verwenden, der Präfix wird automatisch erzeugt.'
            )

    time_dims = _ensure_cache('time-dimensions', False, _rebuild_time_dimensions)
    time_accounts = time_dims.get('time_accounts', [])
    if not any(a['uuid'] == time_account for a in time_accounts):
        time_dims = _ensure_cache('time-dimensions', True, _rebuild_time_dimensions)
        time_accounts = time_dims.get('time_accounts', [])
    if not any(a['uuid'] == time_account for a in time_accounts):
        raise RuntimeError(
            f'time_account {time_account!r} entspricht keinem existierenden Zeitkonto — '
            f'maestro_refs() liefert die gültigen UUIDs.'
        )

    canonical_name = name
    if ticket_number:
        time_account_name = next(
            (a['name'] for a in time_accounts if a['uuid'] == time_account),
            None,
        )
        if project and project_name and time_account_name and project_name.lower() != time_account_name.lower():
            canonical_name = f'{project_ucid}#{ticket_number}: {name}'
        else:
            canonical_name = f'#{ticket_number}: {name}'

    open_rec = _find_open_activity(base_url, today)

    fields = {'name': canonical_name, 'time_account': time_account, 'duration': 0}
    if activity_type:
        fields['activity_type'] = activity_type
    if task:
        fields['task'] = task
    if description:
        fields['description'] = description

    if open_rec is None:
        fields['start_time'] = _floor_5(now).strftime('%Y-%m-%dT%H:%M')
        result = _write_activity(base_url, fields, None)
        action = 'neu angelegt'
    elif open_rec.get('name') == canonical_name and open_rec.get('time_account_uuid') == time_account:
        result = _fetch_record_markdown(base_url, 'activities', open_rec['uuid'])
        action = 'fortgesetzt'
    else:
        time_account_changed = open_rec.get('time_account_uuid') != time_account
        start_prev = datetime.fromisoformat(str(open_rec['start_time']))
        close_time = _ceil_5(now)
        duration = int((close_time - start_prev).total_seconds() // 60)
        if duration <= 0 and not time_account_changed:
            # Themenwechsel bei unverändertem Zeitkonto innerhalb des 5-Minuten-Rasters:
            # Schließen ergäbe duration 0, was per Konvention (duration <= 0) als offen gilt
            # und einen zweiten offenen Datensatz erzeugen würde (#184). Stattdessen die
            # offene Activity erweitern.
            prev_desc = str(open_rec.get('description') or '').strip()
            new_desc = fields.get('description', '')
            if prev_desc and new_desc:
                fields['description'] = f'{prev_desc} — danach: {new_desc}'
            elif prev_desc:
                fields['description'] = prev_desc
            result = _write_activity(base_url, fields, open_rec['uuid'])
            action = 'erweitert (Themenwechsel innerhalb des 5-Minuten-Rasters)'
        else:
            if duration <= 0:
                # Zeitkontowechsel erzeugt immer eine neue Activity, auch innerhalb des
                # 5-Minuten-Rasters: Mindestdauer statt duration <= 0, damit kein zweiter
                # gleichzeitig offener Datensatz entsteht (#184).
                duration = 5
            _write_activity(base_url, {'duration': duration}, open_rec['uuid'])
            fields['start_time'] = close_time.strftime('%Y-%m-%dT%H:%M')
            result = _write_activity(base_url, fields, None)
            action = 'geschlossen + neu angelegt (Themenwechsel)'

    return f'Aktion: {action}\n\n{result}'


@mcp.tool()
def maestro_tracking_close() -> str:
    """Schließt die laufende Activity — Zeitabruf und 5-Minuten-Rasterung übernimmt dieses
    Tool. Legt nie eine neue Activity an; kein Ersatz für `maestro_tracking`.
    """
    base_url = _find_maestro_url()
    now = datetime.now()
    today = now.date().isoformat()

    open_rec = _find_open_activity(base_url, today)
    if open_rec is None:
        return 'Keine laufende Activity.'

    start_prev = datetime.fromisoformat(str(open_rec['start_time']))
    close_time = _ceil_5(now)
    duration = int((close_time - start_prev).total_seconds() // 60)
    if duration <= 0:
        duration = 5

    _write_activity(base_url, {'duration': duration}, open_rec['uuid'])
    result = _fetch_record_markdown(base_url, 'activities', open_rec['uuid'])
    return f'Aktion: geschlossen\n\n{result}'


@mcp.tool()
def maestro_report(date: str = '', max_chars: int = 6000) -> str:
    """GET chronicle-days/report/{date} — Tagesbericht als Markdown.

    date: ISO-Datum, z.B. "2026-05-25"; ohne Angabe der heutige Tag.
    max_chars: maximale Zeichenanzahl der Ausgabe (Standard 6000).
               Volle Berichte können 30 000+ Zeichen haben. Die Trunkierung
               bewahrt den Anfang (neueste Aktivitäten stehen oben).

    Gibt Markdown zurück. Am Ende wird auf Trunkierung hingewiesen wenn aktiv.
    404 = kein Eintrag für dieses Datum.
    """
    try:
        if not date:
            date = datetime.now().date().isoformat()
        base_url = _find_maestro_url()
        url = f"{base_url}/chronicle-days/report/{date}"
        req = urllib.request.Request(url, headers=_auth_headers(base_url))
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return f'Kein Tagesbericht für {date} vorhanden.'
            return f'Fehler: GET {url} → {e.code} {e.reason}'
        except urllib.error.URLError as e:
            return f'Fehler: GET {url} → {e.reason}'

        if len(body) > max_chars:
            body = (
                body[:max_chars]
                + f'\n\n[Bericht gekürzt — {len(body):,} Zeichen gesamt,'
                f' {max_chars:,} zurückgegeben. Für mehr: max_chars erhöhen.]'
            )
        return body
    except RuntimeError as e:
        return f'Fehler: {e}'


def _fetch_archetype_list() -> list:
    base = _find_maestro_url()
    data = _http_get(base, 'agent-skills')
    return sorted((data or {}).get('archetypes') or [])


def _fetch_skill_definition(archetype: str) -> dict:
    """Skill-Definition eines Archetypes — Quelle ist ausschließlich
    `GET /{archetype}/skill/agent` der Maestro-Instanz (#168)."""
    base = _find_maestro_url()
    definition = _http_get(base, f'{archetype}/skill/agent')
    if not isinstance(definition, dict) or definition.get('error'):
        raise RuntimeError(f'Keine Skill-Definition für "{archetype}" — Instanz meldet: {definition}')
    return definition


def _format_skill(archetype: str, skill: dict) -> str:
    labels = skill.get('labels') or {}

    def lbl(f: str) -> str:
        return f' — {labels[f]}' if f in labels else ''

    def with_values(f: str) -> str:
        vals = skill.get('values', {}).get(f)
        return f' ({" / ".join(vals)})' if vals else ''

    lines = [f'## Skill: {archetype}', '']

    if skill.get('purpose'):
        lines += [skill['purpose'], '']

    lines += [
        f'**Anlegen:** `maestro_create(archetype="{archetype}", fields={{...}})`',
        f'**Ändern:** `maestro_update(archetype="{archetype}", identifier="<uuid>", fields={{...}})`',
        '',
    ]

    if skill.get('required'):
        lines.append('### Pflichtfelder')
        for f in skill['required']:
            lines.append(f'- `{f}`{lbl(f)}{with_values(f)}')
        lines.append('')

    if skill.get('optional'):
        lines.append('### Optionale Felder')
        for f in skill['optional']:
            lines.append(f'- `{f}`{lbl(f)}{with_values(f)}')
        lines.append('')

    if skill.get('conditional'):
        lines.append('### Bedingte Felder')
        for f, note in skill['conditional'].items():
            lines.append(f'- `{f}`{lbl(f)} — {note}')
        lines.append('')

    if skill.get('update_only'):
        lines.append('### Nur bei Update')
        for f in skill['update_only']:
            lines.append(f'- `{f}`{lbl(f)}{with_values(f)}')
        lines.append('')

    if skill.get('relations'):
        lines.append('### Relationsfelder (Abruf vor Write)')
        for f, fetch_note in skill['relations'].items():
            lines.append(f'- `{f}`{lbl(f)}: {fetch_note}')
        lines.append('')

    if skill.get('rules'):
        lines.append('### Verbindliche Regeln')
        for rule in skill['rules']:
            lines.append(f'- {rule}')
        lines.append('')

    if skill.get('notes'):
        lines.append('### Hinweise')
        for note in skill['notes']:
            lines.append(f'- {note}')
        lines.append('')

    return '\n'.join(lines).rstrip()


@mcp.tool()
def maestro_skill(archetype: str) -> str:
    """Skill-Definition für einen Maestro-Archetype — Felder, Regeln, erlaubte Werte.

    archetype: Name des Archetypes, z.B. "tasks", "todos", "activities", "time-units"

    Quelle ist ausschließlich die Maestro-Instanz (`GET /{archetype}/skill/agent`) —
    kein lokaler Zweitbestand in Echo (#168). Ist für den Archetype keine
    Skill-Definition hinterlegt, antwortet der Abruf mit einem Fehler.

    Gibt eine strukturierte Skill-Definition als Markdown zurück.
    Für die Liste verfügbarer Archetypes: maestro_archetypes()
    """
    try:
        skill = _fetch_skill_definition(archetype)
    except RuntimeError as e:
        return f'Fehler: {e}'
    return _format_skill(archetype, skill)


@mcp.tool()
def maestro_archetypes() -> str:
    """Liste der Maestro-Archetypes mit hinterlegter Skill-Definition.

    Quelle ist `GET /agent-skills` der Maestro-Instanz — kein lokaler Zweitbestand in
    Echo (#168).

    Für Details: maestro_skill(archetype="{name}")
    """
    archetypes = _fetch_archetype_list()
    lines = ['## Verfügbare Maestro-Archetypes (mit Skill-Definition)', '']
    for name in archetypes:
        lines.append(f'- `{name}` — `maestro_skill(archetype="{name}")`')
    return '\n'.join(lines)


# ── Referenz-Cache (#067) ────────────────────────────────────────────────────────

def _read_cache(name: str):
    """Gecachte Daten oder None, wenn die Datei fehlt, defekt oder älter als der TTL ist."""
    path = _cache_path(name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        fetched = datetime.fromisoformat(data['fetched_at'])
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return None
    if datetime.now() - fetched >= _REFS_TTL:
        return None
    return data


def _write_cache_atomic(name: str, data: dict) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(name)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def _trim(result: object, fields: tuple) -> list:
    """Reduziert eine JSON-Liste ({"data": [{"attributes": {...}}]}) auf die gewünschten Felder."""
    records = result.get('data', []) if isinstance(result, dict) else []
    out = []
    for rec in records:
        attrs = rec.get('attributes', rec)
        out.append({f: attrs.get(f) for f in fields})
    return out


def _rebuild_time_dimensions() -> dict:
    base = _find_maestro_url()
    data = {
        'fetched_at': datetime.now().isoformat(timespec='seconds'),
        'time_accounts': _trim(_http_get(base, 'time-accounts/json'), _TRIM_FIELDS['time-accounts']),
        'time_categories': _trim(_http_get(base, 'time-categories/json'), _TRIM_FIELDS['time-categories']),
    }
    _write_cache_atomic('time-dimensions', data)
    return data


def _rebuild_activity_types() -> dict:
    base = _find_maestro_url()
    data = {
        'fetched_at': datetime.now().isoformat(timespec='seconds'),
        'activity_types': _trim(_http_get(base, 'activity-types/json'), _TRIM_FIELDS['activity-types']),
    }
    _write_cache_atomic('activity-types', data)
    return data


def _rebuild_todo_types() -> dict:
    base = _find_maestro_url()
    data = {
        'fetched_at': datetime.now().isoformat(timespec='seconds'),
        'todo_types': _trim(_http_get(base, 'todo-types/json'), _TRIM_FIELDS['todo-types']),
    }
    _write_cache_atomic('todo-types', data)
    return data


def _ensure_cache(name: str, refresh: bool, rebuild_fn) -> dict:
    if not refresh:
        cached = _read_cache(name)
        if cached is not None:
            return cached
    return rebuild_fn()


def _invalidate_refs_for(archetype: str) -> None:
    """Nach Writes auf Referenz-Archetypes den passenden Cache neu aufbauen (best-effort)."""
    try:
        if archetype in ('time-accounts', 'time-categories'):
            _rebuild_time_dimensions()
        elif archetype == 'activity-types':
            _rebuild_activity_types()
        elif archetype == 'todo-types':
            _rebuild_todo_types()
    except Exception:
        pass


@mcp.tool()
def maestro_refs(refresh: bool = False) -> dict:
    """Gecachte Referenzdaten: time-accounts, time-categories und activity-types.

    Liefert die getrimmten Stammdaten aus dem lokalen Cache (.maestro/ im Agent-Verzeichnis) und hält
    ihn selbst aktuell: bei fehlendem/defektem/über 7 Tage altem Cache lädt es von der Maestro-API
    neu, und nach eigenen Writes auf diese Archetypes erneuert es den Cache automatisch.

    Kadenz: einmal je Session abrufen und die benötigte UUID/UCID im Sitzungskontext weiterverwenden.

    Felder: time-accounts → name, uuid, time_category_uuid, description;
            time-categories → name, uuid, description;
            activity-types → name, ucid, uuid (Activities referenzieren den Typ per ucid);
            todo-types → name, ucid, uuid (Todos referenzieren den Typ per ucid).
    """
    dims = _ensure_cache('time-dimensions', refresh, _rebuild_time_dimensions)
    types = _ensure_cache('activity-types', refresh, _rebuild_activity_types)
    todo_types = _ensure_cache('todo-types', refresh, _rebuild_todo_types)
    return {
        'time_accounts': dims.get('time_accounts', []),
        'time_categories': dims.get('time_categories', []),
        'activity_types': types.get('activity_types', []),
        'todo_types': todo_types.get('todo_types', []),
        'cache': {
            'time_dimensions_fetched_at': dims.get('fetched_at'),
            'activity_types_fetched_at': types.get('fetched_at'),
            'todo_types_fetched_at': todo_types.get('fetched_at'),
            'ttl_days': _REFS_TTL.days,
        },
    }


if __name__ == '__main__':
    mcp.run(transport='stdio')
