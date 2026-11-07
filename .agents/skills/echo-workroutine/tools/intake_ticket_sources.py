#!/usr/bin/env python3
"""intake_ticket_sources — mechanischer Ereignisabgleich für work-routine Schritt 1.

Läuft über alle für den Agenten sichtbaren Maestro-Projekte. Je Projekt bestimmt
`ticket_system`, welches `ticket_systems/<ticket_system>.py`-Modul verwendet wird.
`list_assigned(project)` liefert die dem Agenten aktuell zugewiesenen Tickets dieses
Projekts.

Ticketbezogene Todos tragen den Namen `<project_ucid>#<ticket_number>: <title>` und
liegen am tagesbezogenen Task "Ereignisabgleich <Datum>". Datengrundlage ist
ausschließlich der Tagesbericht (`chronicle-days/report/<Datum>`, Markdown). Der
Verarbeitungsstand wird über die Todo-Zeilen dieser einen, heutigen Aufgabe geführt:
Existiert dort bereits ein offenes Todo mit demselben Präfix, wird es weiterverwendet.
Andernfalls entsteht ein neues — unabhängig davon, ob unter einer Aufgabe eines anderen
Tages noch ein offenes Todo für dasselbe Ticket besteht.

Ausgabe (stdout): immer der Tagesbericht (`chronicle-days/report`) — unabhängig davon,
ob neue Todos entstanden sind.

Aufruf: python3 intake_ticket_sources.py
"""

import argparse
import importlib.util
import json
import re
import sys
import urllib.request
from datetime import datetime, date, timedelta
from pathlib import Path

# Agent-Verzeichnis: im Antigravity-Setup wird der Literal '.agent' vom Finalize-sed auf
# '.agents' umgeschrieben (#065) — derselbe Code funktioniert in beiden Layouts.
AGENT_DIR = Path(__file__).parents[4] / '.agent'
_TICKET_SYSTEMS_DIR = AGENT_DIR / 'skills' / 'echo-workroutine' / 'tools' / 'ticket_systems'
_MAESTRO_TOOLS_DIR = AGENT_DIR / 'skills' / 'echo-maestro' / 'tools'

if str(_MAESTRO_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_MAESTRO_TOOLS_DIR))

import maestro_client as mc  # noqa: E402


def _records(result) -> list:
    return result if isinstance(result, list) else result.get('data', [])


def load_operations_module(ticket_system: str):
    ops_file = _TICKET_SYSTEMS_DIR / f'{ticket_system}.py'
    spec = importlib.util.spec_from_file_location(f'ticket_source_operations_{ticket_system}', ops_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _section(report: str, heading: str, next_headings: list[str]) -> str:
    start = report.find(heading)
    if start == -1:
        return ''
    end = len(report)
    for next_heading in next_headings:
        idx = report.find(next_heading, start + len(heading))
        if idx != -1:
            end = min(end, idx)
    return report[start:end]


def _task_uuid_by_title(report: str, title: str) -> str | None:
    aufgaben = _section(report, '## Aufgaben', ['## Abgeschlossen', '## Aktivitäten'])
    for match in re.finditer(r'^### \[([0-9a-f-]+)\] (.+?)\s*$', aufgaben, re.MULTILINE):
        if match.group(2) == title:
            return match.group(1)
    return None


def _open_todo_uuids(report: str, task_uuid: str) -> list[str]:
    section = _task_todos_section(report, task_uuid)
    return re.findall(r'^\s*- \[ \] \[([0-9a-f-]+)\]', section, re.MULTILINE)


def _reassign_todo(base_url: str, todo_uuid: str, new_task_uuid: str) -> None:
    content = mc._post_raw(base_url, f'todos/{todo_uuid}', mc._form_fields({'task': new_task_uuid}))
    mc._identifier_from_content(content, 'todos')


def find_or_create_task(report: str, base_url: str, time_account_uuid: str) -> str:
    title = f'Ereignisabgleich {datetime.now().date().isoformat()}'

    found = _task_uuid_by_title(report, title)
    if found:
        return found

    abgeschlossen = _section(report, '## Abgeschlossen', ['## Aktivitäten'])
    for match in re.finditer(r'^- \[([0-9a-f-]+)\] (.+?)\s*$', abgeschlossen, re.MULTILINE):
        if match.group(2) == title:
            return match.group(1)

    content = mc._post_raw(base_url, 'tasks', mc._form_fields({
        'title': title,
        'time_account': time_account_uuid,
        'description': 'Mechanisch angelegte Todos aus konfigurierten Ticketquellen.',
    }))
    new_task_uuid = mc._identifier_from_content(content, 'tasks')

    vortag = (date.today() - timedelta(days=1)).isoformat()
    vortag_task_uuid = _task_uuid_by_title(report, f'Ereignisabgleich {vortag}')
    if vortag_task_uuid:
        for todo_uuid in _open_todo_uuids(report, vortag_task_uuid):
            _reassign_todo(base_url, todo_uuid, new_task_uuid)

    return new_task_uuid


def _task_todos_section(report: str, task_uuid: str) -> str:
    match = re.search(rf'^### \[{re.escape(task_uuid)}\].*$', report, re.MULTILINE)
    if not match:
        return ''
    start = match.end()
    next_heading = re.search(r'^#{2,3} ', report[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(report)
    return report[start:end]


def has_open_todo_for_prefix(report: str, task_uuid: str, prefix: str) -> bool:
    section = _task_todos_section(report, task_uuid)
    pattern = re.compile(rf'^\s*- \[ \] \[[0-9a-f-]+\] {re.escape(prefix)}:', re.MULTILINE)
    return bool(pattern.search(section))


def create_todo(base_url: str, task_uuid: str, prefix: str, title: str) -> str:
    content = mc._post_raw(base_url, 'todos', mc._form_fields({
        'name': f'{prefix}: {title}',
        'task': task_uuid,
    }))
    return mc._identifier_from_content(content, 'todos')


def resolve_time_account(project_name: str) -> str:
    refs = json.loads((AGENT_DIR / '.maestro' / 'time-dimensions.json').read_text(encoding='utf-8'))
    for account in refs.get('time_accounts', []):
        if account.get('name') == project_name:
            return account['uuid']
    for account in refs.get('time_accounts', []):
        if account.get('name') == 'Projekte':
            return account['uuid']


def fetch_report_markdown(base_url: str, date: str = '') -> str:
    if not date:
        date = datetime.now().date().isoformat()
    req = urllib.request.Request(
        f'{base_url}/chronicle-days/report/{date}',
        headers=mc._auth_headers(base_url),
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()


def process_project(report: str, base_url: str, task_uuid: str, project: dict, ops) -> None:
    project_ucid = project['ucid']
    for issue in ops.list_assigned(project):
        prefix = f'{project_ucid}#{issue["ticket_number"]}'
        if has_open_todo_for_prefix(report, task_uuid, prefix):
            continue

        create_todo(base_url, task_uuid, prefix, issue['title'])


def run_intake(project_ucid: str | None = None) -> None:
    base_url = mc._find_maestro_url()
    date = datetime.now().date().isoformat()
    report = fetch_report_markdown(base_url, date)
    projects = _records(mc._http_get(base_url, 'projects/agent?per_page=200'))

    if project_ucid is not None:
        projects = [p for p in projects if p.get('ucid') == project_ucid]
        if not projects:
            raise ValueError(f'Unbekannter project_ucid: {project_ucid!r}')

    task_uuid = None

    for project in projects:
        ticket_system = project.get('ticket_system')
        if not ticket_system:
            continue

        ops = load_operations_module(ticket_system)

        if task_uuid is None:
            task_uuid = find_or_create_task(report, base_url, resolve_time_account(project['name']))

        process_project(report, base_url, task_uuid, project, ops)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', dest='project_ucid', default=None)
    args = parser.parse_args()
    run_intake(project_ucid=args.project_ucid)
    print(fetch_report_markdown(mc._find_maestro_url()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
