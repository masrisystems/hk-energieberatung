#!/usr/bin/env python3
"""operations — ticketsystemspezifische Funktionen der GitLab-Quelle für `work-routine`.

Stellt `list_assigned`, `read_ticket`, `write_description`, `write_comment`,
`update_comment`, `write_status`, `write_assignee` und `person_external_id`
bereit — dieselben Funktionsnamen wie jedes andere Modul unter `ticket_systems/`.
Verwendet für jeden GitLab-Zugriff `query_gitlab.py` mit `project["gitlab_project_id"]`
als Ziel-Projekt-ID.
"""

import json
import re
import sys
from pathlib import Path

_GITLAB_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / 'gitlab-integration' / 'scripts'
_MAESTRO_TOOLS_DIR = Path(__file__).resolve().parents[3] / 'echo-maestro' / 'tools'

for _p in (_GITLAB_SCRIPTS_DIR, _MAESTRO_TOOLS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import query_gitlab as gl  # noqa: E402
import maestro_client as mc  # noqa: E402

_NO_STATUS_LABEL = 'kein Statuslabel'


def _project_config(project: dict) -> dict:
    cfg = gl.load_config()
    cfg['project_id'] = project['gitlab_project_id']
    cfg['repo'] = str(mc.project_directory(project))
    return cfg


def list_assigned(project: dict) -> list[dict]:
    cfg = _project_config(project)
    issues = gl.make_request_all_pages(cfg, f"projects/{cfg['project_id']}/issues", {
        'state': 'opened',
        'scope': 'assigned_to_me',
    })
    return [
        {'ticket_number': issue['iid'], 'title': issue['title'], 'updated_at': issue['updated_at']}
        for issue in issues
    ]


def _status_for_labels(project: dict, labels: list[str]) -> str:
    by_label = {row['label']: row['status'].lower() for row in project.get('status_labels', [])}
    for label in labels:
        if label in by_label:
            return by_label[label]
    return _NO_STATUS_LABEL


def _assigned_by(notes: list[dict], assignee_usernames: set[str]) -> tuple[int | None, str | None]:
    system_notes = [n for n in notes if n['system']]
    system_notes.sort(key=lambda n: n['created_at'])
    author_id, assigned_at = None, None
    for note in system_notes:
        body = note['body']
        if not body.lower().startswith('assigned to'):
            continue
        if any(f'@{username}' in body for username in assignee_usernames):
            author_id = note['author']['id']
            assigned_at = note['created_at']
    return author_id, assigned_at


def _meta_field(description: str, field: str) -> str | None:
    match = re.search(rf'^- {re.escape(field)}:\s*(.+)$', description or '', re.MULTILINE)
    return match.group(1).strip() if match else None


def read_ticket(project: dict, ticket_number) -> dict:
    cfg = _project_config(project)

    issue = gl.make_request(cfg, f"projects/{cfg['project_id']}/issues/{ticket_number}")
    all_notes = gl.make_request_all_pages(
        cfg, f"projects/{cfg['project_id']}/issues/{ticket_number}/notes", {'sort': 'asc'}
    )

    assignees = [{'id': a['id'], 'name': a['name'], 'username': a['username']} for a in issue['assignees']]
    assignee_usernames = {a['username'] for a in assignees}

    comments = [
        {
            'note_id': note['id'],
            'author_id': note['author']['id'],
            'author_name': note['author']['name'],
            'created_at': note['created_at'],
            'body': note['body'],
        }
        for note in all_notes if not note['system']
    ]

    status = _status_for_labels(project, issue['labels'])
    assigned_by, assigned_at = _assigned_by(all_notes, assignee_usernames)

    return {
        'ticket_number': issue['iid'],
        'title': issue['title'],
        'description': issue['description'],
        'web_url': issue['web_url'],
        'assignees': assignees,
        'comments': comments,
        'assigned_by': assigned_by,
        'assigned_at': assigned_at,
        'status': status,
        'type': _meta_field(issue['description'], 'Typ'),
    }


def list_tickets(project: dict, state: str | None = 'opened') -> list[dict]:
    cfg = _project_config(project)
    params = {'state': state} if state else {}
    issues = gl.make_request_all_pages(cfg, f"projects/{cfg['project_id']}/issues", params)
    return [{'iid': i['iid'], 'title': i['title'], 'labels': i['labels']} for i in issues]


def list_notes(project: dict, ticket_number) -> list[dict]:
    cfg = _project_config(project)
    notes = gl.make_request_all_pages(
        cfg, f"projects/{cfg['project_id']}/issues/{ticket_number}/notes", {'sort': 'asc'}
    )
    return [{'note_id': n['id'], 'body': n['body']} for n in notes if not n['system']]


def list_milestones(project: dict) -> list[dict]:
    cfg = _project_config(project)
    milestones = gl.make_request_all_pages(cfg, f"projects/{cfg['project_id']}/milestones", {})
    return [{'id': m['id'], 'title': m['title']} for m in milestones]


def write_description(project: dict, ticket_number, file_path: str) -> None:
    cfg = _project_config(project)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    gl._replace_description(cfg, ticket_number, content)


def write_comment(project: dict, ticket_number, text: str) -> dict:
    cfg = _project_config(project)
    endpoint = f"projects/{cfg['project_id']}/issues/{ticket_number}/notes"
    return gl.make_post_put_request(cfg, endpoint, method='POST', data={'body': text})


def deliver_artifact(project: dict, ticket_number, temp_file_path: str, artifact_type: str) -> str:
    content = Path(temp_file_path).read_text(encoding='utf-8')
    note = write_comment(project, ticket_number, content)
    return f"Kommentar {note['id']} an Issue #{ticket_number}"


def update_comment(project: dict, ticket_number, note_id, text: str) -> None:
    cfg = _project_config(project)
    endpoint = f"projects/{cfg['project_id']}/issues/{ticket_number}/notes/{note_id}"
    gl.make_post_put_request(cfg, endpoint, method='PUT', data={'body': text})


def write_status(project: dict, ticket_number, status: str) -> None:
    cfg = _project_config(project)
    by_status = {row['status'].lower(): row['label'] for row in project.get('status_labels', [])}
    target_label = by_status.get(status)
    if not target_label:
        raise RuntimeError(f'Kein Label für Status {status!r} in Projekt {project["uuid"]} hinterlegt.')

    status_label_values = set(by_status.values())
    endpoint = f"projects/{cfg['project_id']}/issues/{ticket_number}"
    current = gl.make_request(cfg, endpoint)
    labels = [l for l in current['labels'] if l not in status_label_values]
    labels.append(target_label)
    gl.make_post_put_request(cfg, endpoint, method='PUT', data={'labels': ','.join(labels)})


def write_assignee(project: dict, ticket_number, external_id) -> None:
    cfg = _project_config(project)
    endpoint = f"projects/{cfg['project_id']}/issues/{ticket_number}"
    gl.make_post_put_request(cfg, endpoint, method='PUT', data={'assignee_ids': [int(external_id)]})


def person_external_id(project: dict, person_uuid: str) -> str:
    base_url = mc._find_maestro_url()

    links = mc._http_get(
        base_url,
        f'source-links/agent?archetype=projects&record_uuid={project["uuid"]}&connector_id=gitlab&per_page=1',
    )
    link_records = links.get('data', []) if isinstance(links, dict) else links
    if not link_records:
        raise RuntimeError(f'Kein GitLab-Source-Link für Projekt {project["uuid"]} gefunden.')
    source_account_uuid = link_records[0]['source_account_uuid']

    account = mc._http_get(base_url, f'source-accounts/{source_account_uuid}/agent')
    config_json = account.get('config_json')
    config = json.loads(config_json) if isinstance(config_json, str) else (config_json or {})
    platform_ucid = config.get('platform_ucid')
    if not platform_ucid:
        raise RuntimeError(f'Source-Account {source_account_uuid} trägt kein platform_ucid.')

    platforms = mc._http_get(base_url, f'platforms/agent?ucid={platform_ucid}&per_page=1')
    platform_records = platforms.get('data', []) if isinstance(platforms, dict) else platforms
    if not platform_records:
        raise RuntimeError(f'Keine Platform mit ucid {platform_ucid!r} gefunden.')
    platform_uuid = platform_records[0]['uuid']

    identities = mc._http_get(
        base_url,
        f'identities/agent?person_uuid={person_uuid}&platform_uuid={platform_uuid}&per_page=1',
    )
    identity_records = identities.get('data', []) if isinstance(identities, dict) else identities
    if not identity_records:
        raise RuntimeError(f'Keine Identity für Person {person_uuid} auf Platform {platform_uuid} gefunden.')
    return identity_records[0]['external_id']


def verify_remote_branch(project: dict, branch: str) -> None:
    cfg = _project_config(project)
    gl.make_request(cfg, f"projects/{cfg['project_id']}/repository/branches/{branch}")


def find_open_merge_request(project: dict, source_branch: str, target_branch: str = 'develop') -> dict | None:
    cfg = _project_config(project)
    mrs = gl.make_request_all_pages(cfg, f"projects/{cfg['project_id']}/merge_requests", {
        'state': 'opened', 'source_branch': source_branch, 'target_branch': target_branch,
    })
    return mrs[0] if mrs else None


def ensure_merge_request(project: dict, source_branch: str, title: str, target_branch: str = 'develop') -> dict:
    existing = find_open_merge_request(project, source_branch, target_branch)
    if existing:
        return existing
    cfg = _project_config(project)
    endpoint = f"projects/{cfg['project_id']}/merge_requests"
    return gl.make_post_put_request(cfg, endpoint, method='POST', data={
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': title,
        'remove_source_branch': True,
    })
