#!/usr/bin/env python3
"""operations — ticketsystemspezifische Funktionen für die Maestro-Tickets-Quelle
(`ticket_system == maestro`) der `work-routine`/Artefakt-Mechanik.

Stellt `list_assigned`, `read_ticket`, `write_status`, `write_assignee`,
`write_description`, `write_comment` und `person_external_id` bereit — dieselben
Funktionsnamen wie jedes andere Modul unter `ticket_systems/`. Zuweisung läuft über die
Maestro-Archetypes `tickets` und `ticket-assignments` — je Ticket existiert dabei höchstens
ein `ticket-assignments`-Record.
"""

import re
import sys
from pathlib import Path

_MAESTRO_TOOLS_DIR = Path(__file__).resolve().parents[3] / 'echo-maestro' / 'tools'
if str(_MAESTRO_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_MAESTRO_TOOLS_DIR))

import maestro_client as mc  # noqa: E402


def list_assigned(project: dict) -> list[dict]:
    base_url = mc._find_maestro_url()
    result = mc._http_get(base_url, f'tickets/agent?project_uuid={project["uuid"]}&assignee=me')
    rows = _records(result)
    return [{'ticket_number': row['uuid'], 'title': row['title'], 'updated_at': None} for row in rows]


def read_ticket(project: dict, ticket_number) -> dict:
    base_url = mc._find_maestro_url()
    data = mc._http_get(base_url, f'tickets/{ticket_number}/agent')
    assignments = _records(mc._http_get(base_url, f'ticket-assignments/agent?ticket_uuid={ticket_number}'))
    assignment = assignments[0] if assignments else None
    return {
        'ticket_number': ticket_number,
        'title': data['title'],
        'description': data.get('context') or '',
        'web_url': None,
        'assignees': [{'id': assignment['identity_uuid']}] if assignment else [],
        'comments': [],
        'assigned_by': assignment['identity_uuid'] if assignment else None,
        'assigned_at': assignment['created_at'] if assignment else None,
        'status': data['status'].lower(),
        'type': (data.get('type') or '').lower(),
    }


def write_status(project: dict, ticket_number, status: str) -> None:
    base_url = mc._find_maestro_url()
    mc._post_raw(base_url, f'tickets/{ticket_number}', mc._form_fields({'status': status.upper()}))


def write_assignee(project: dict, ticket_number, target, purpose: str | None = None) -> None:
    base_url = mc._find_maestro_url()
    mc._post_raw(base_url, f'tickets/{ticket_number}/relations/assignees/attach', mc._form_fields({'target_uuid': target}))
    mc._post_raw(base_url, 'ticket-assignments', mc._form_fields({
        'ticket_uuid': ticket_number, 'identity_uuid': target, 'purpose': purpose or 'IMPLEMENT',
    }))


def person_external_id(project: dict, person_uuid: str) -> str:
    return assignee_identity_uuid(project, person_uuid)


_SECTION_FIELDS = {
    'Kontext': 'context',
    'Ziel': 'goal',
    'Anforderungen': 'requirements',
    'Akzeptanzkriterien': 'acceptance_criteria',
    'Risiken': 'risks',
    'Offene Fragen': 'open_questions',
}


def _parse_sections(content: str) -> dict[str, str]:
    fields = {}
    headings = list(re.finditer(r'(?m)^## (.+)$', content))
    for i, heading in enumerate(headings):
        field = _SECTION_FIELDS.get(heading.group(1).strip())
        if not field:
            continue
        start = heading.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
        fields[field] = content[start:end].strip()
    return fields


def write_description(project: dict, ticket_number, file_path: str) -> None:
    base_url = mc._find_maestro_url()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    mc._post_raw(base_url, f'tickets/{ticket_number}', mc._form_fields(_parse_sections(content)))


def write_comment(project: dict, ticket_number, text: str) -> None:
    base_url = mc._find_maestro_url()
    data = mc._http_get(base_url, f'tickets/{ticket_number}/agent')
    updated = f"{data.get('context') or ''}\n\n{text}".strip()
    mc._post_raw(base_url, f'tickets/{ticket_number}', mc._form_fields({'context': updated}))


def _records(result) -> list:
    return result.get('data', []) if isinstance(result, dict) else result


def assignee_identity_uuid(project: dict, person_uuid: str) -> str:
    base_url = mc._find_maestro_url()

    project_links = mc._http_get(
        base_url, f'source-links/agent?archetype=projects&record_uuid={project["uuid"]}&per_page=1'
    )
    project_link_records = _records(project_links)
    if not project_link_records:
        raise RuntimeError(f'Kein Source-Link für Projekt {project["uuid"]} gefunden.')
    source_account_uuid = project_link_records[0]['source_account_uuid']

    identities = mc._http_get(base_url, f'identities/agent?person_uuid={person_uuid}&per_page=50')
    for identity in _records(identities):
        identity_links = mc._http_get(
            base_url, f'source-links/agent?archetype=identities&record_uuid={identity["uuid"]}&per_page=1'
        )
        identity_link_records = _records(identity_links)
        if identity_link_records and identity_link_records[0]['source_account_uuid'] == source_account_uuid:
            return identity['uuid']
    raise RuntimeError(f'Keine Identity für Person {person_uuid} auf dem Source-Account {source_account_uuid} gefunden.')
