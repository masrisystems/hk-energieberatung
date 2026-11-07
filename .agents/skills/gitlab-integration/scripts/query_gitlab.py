#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import sys
import os
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(__file__)
_AGENT_CONFIG_PATH = os.path.join(_SCRIPT_DIR, '../../../config.json')
_SKILL_CONFIG_PATH = os.path.join(_SCRIPT_DIR, '../config.json')

def load_config():
    # Primary: .agent/config.json
    agent_cfg_path = os.path.normpath(_AGENT_CONFIG_PATH)
    if os.path.exists(agent_cfg_path):
        with open(agent_cfg_path, 'r') as f:
            cfg = json.load(f)
        if cfg.get('gitlab_url') and cfg.get('private_token'):
            return {
                'gitlab_url': cfg['gitlab_url'].rstrip('/'),
                'project_id': int(cfg.get('gitlab_project_id') or 0),
                'private_token': cfg['private_token'],
            }

    # Fallback: skill-local config.json
    skill_cfg_path = os.path.normpath(_SKILL_CONFIG_PATH)
    if os.path.exists(skill_cfg_path):
        with open(skill_cfg_path, 'r') as f:
            cfg = json.load(f)
        if cfg.get('gitlab_url') and cfg.get('private_token'):
            print(
                "Warning: GitLab config loaded from skill-local config.json.\n"
                "Migrate credentials to .agent/config.json (gitlab_url, gitlab_project_id, private_token).",
                file=sys.stderr
            )
            return cfg

    print(
        "Error: No GitLab credentials found.\n"
        "Set gitlab_url, gitlab_project_id and private_token in .agent/config.json.",
        file=sys.stderr
    )
    sys.exit(1)

def make_request(config, endpoint, params=None):
    url = f"{config['gitlab_url']}/api/v4/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    req = urllib.request.Request(url)
    req.add_header('PRIVATE-TOKEN', config['private_token'])
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def _next_page_url(link_header):
    if not link_header:
        return None
    for part in link_header.split(','):
        section = part.split(';')
        if len(section) < 2:
            continue
        url_part = section[0].strip().strip('<>')
        rel_part = section[1].strip()
        if rel_part == 'rel="next"':
            return url_part
    return None

def make_request_all_pages(config, endpoint, params=None):
    params = dict(params or {})
    params.setdefault('per_page', 100)
    url = f"{config['gitlab_url']}/api/v4/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    results = []
    while url:
        req = urllib.request.Request(url)
        req.add_header('PRIVATE-TOKEN', config['private_token'])
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                results.extend(json.load(response))
                url = _next_page_url(response.getheader('Link'))
        except urllib.error.HTTPError as e:
            print(f"Error: {e.code} - {e.read().decode('utf-8')}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    return results

def make_post_put_request(config, endpoint, method='POST', data=None):
    url = f"{config['gitlab_url']}/api/v4/{endpoint}"
    
    body = None
    if data:
        body = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header('PRIVATE-TOKEN', config['private_token'])
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def list_issues(config, args):
    params = {
        'scope': 'all',
        'state': 'opened',
        'per_page': 50
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--label' and i + 1 < len(args):
            params['labels'] = args[i+1]
            i += 2
        elif arg == '--state' and i + 1 < len(args):
            params['state'] = args[i+1]
            i += 2
        else:
            params['search'] = arg
            i += 1
        
    endpoint = f"projects/{config['project_id']}/issues"
    data = make_request_all_pages(config, endpoint, params)

    print(f"Found {len(data)} issues:")
    for issue in data:
        print(f"#{issue['iid']} - {issue['title']} (Labels: {', '.join(issue['labels'])})")

def get_milestone_issues(config, args):
    if len(args) < 1:
        print("Usage: get_milestone_issues <milestone_title>")
        sys.exit(1)

    milestone_title = args[0]
    params = {'scope': 'all', 'state': 'all', 'milestone': milestone_title}
    endpoint = f"projects/{config['project_id']}/issues"
    data = make_request_all_pages(config, endpoint, params)

    print(f"Found {len(data)} issues in milestone '{milestone_title}':")
    for issue in data:
        print(f"#{issue['iid']} - {issue['title']} (Labels: {', '.join(issue['labels'])})")

def get_issue_full(config, args):
    if len(args) < 1:
        print("Usage: get_issue_full <iid>")
        sys.exit(1)

    iid = args[0]
    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    data = make_request(config, endpoint)

    print(f"Title: {data['title']}")
    print(f"Description:\n{data['description']}")
    print(f"State: {data['state']}")
    print(f"Labels: {', '.join(data['labels'])}")
    print(f"Assignees: {', '.join([a['name'] for a in data['assignees']])}")
    print(f"Milestone: {data['milestone']['title'] if data.get('milestone') else '-'}")
    print(f"Web URL: {data['web_url']}")

    notes_endpoint = f"projects/{config['project_id']}/issues/{iid}/notes"
    notes = make_request_all_pages(config, notes_endpoint, {'sort': 'desc'})
    non_system_notes = [n for n in notes if not n['system']]
    print(f"\n{len(non_system_notes)} Notes:")
    for note in non_system_notes:
        print(f"--- NOTE {note['id']} (Discussion: {note.get('discussion_id')}) by {note['author']['name']} ---")
        print(note['body'])

def get_issue(config, args):
    if len(args) < 1:
        print("Usage: get_issue <iid>")
        sys.exit(1)
        
    iid = args[0]
    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    data = make_request(config, endpoint)
    
    print(f"Title: {data['title']}")
    print(f"Description:\n{data['description']}")
    print(f"State: {data['state']}")
    print(f"Labels: {', '.join(data['labels'])}")
    print(f"Assignees: {', '.join([a['name'] for a in data['assignees']])}")
    print(f"Web URL: {data['web_url']}")

def list_assigned_issues(config, args):
    params = {
        'state': 'opened',
        'scope': 'assigned_to_me', # Uses the authenticated user context
    }

    data = make_request_all_pages(config, "issues", params)

    print(f"Found {len(data)} assigned issues:")
    for issue in data:
        print(f"Project: {issue['project_id']} - #{issue['iid']} - {issue['title']} "
              f"(Labels: {', '.join(issue['labels'])})")

def update_issue(config, args):
    if len(args) < 2:
        print("Usage: update_issue <iid> <action> [value]")
        print("Actions: add_label, remove_label, assign_user, set_assignee_id")
        sys.exit(1)
    
    iid = args[0]
    action = args[1]
    
    # Fetch current issue to get current labels/assignees
    endpoint_get = f"projects/{config['project_id']}/issues/{iid}"
    current_issue = make_request(config, endpoint_get)
    
    data = {}
    
    if action == 'add_label':
        if len(args) < 3: print("Missing label"); sys.exit(1)
        new_label = args[2]
        labels = current_issue['labels']
        if new_label not in labels:
            labels.append(new_label)
        data['labels'] = ','.join(labels)
        
    elif action == 'remove_label':
        if len(args) < 3: print("Missing label"); sys.exit(1)
        remove_label = args[2]
        labels = current_issue['labels']
        if remove_label in labels:
            labels.remove(remove_label)
        data['labels'] = ','.join(labels)
        
    elif action == 'set_assignee_id':
         if len(args) < 3: print("Missing user_id"); sys.exit(1)
         user_id = int(args[2])
         data['assignee_ids'] = [user_id]

    elif action == 'assign_user':
         # Resolves username to ID first
         if len(args) < 3: print("Missing username query"); sys.exit(1)
         username_query = args[2]
         users = make_request(config, 'users', {'search': username_query})
         if not users:
             print(f"User '{username_query}' not found.")
             sys.exit(1)
         user_id = users[0]['id']
         print(f"Resolved '{username_query}' to ID {user_id} ({users[0]['name']})")
         data['assignee_ids'] = [user_id]
    
    elif action == 'close':
        data['state_event'] = 'close'
        
    elif action == 'reopen':
        data['state_event'] = 'reopen'
         
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
        
    endpoint_put = f"projects/{config['project_id']}/issues/{iid}"
    result = make_post_put_request(config, endpoint_put, method='PUT', data=data)
    print(f"Updated Issue #{iid}. {action}: {data}")

def clear_assignees(config, args):
    if len(args) < 1:
        print("Usage: clear_assignees <iid>")
        sys.exit(1)

    iid = args[0]
    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    make_post_put_request(config, endpoint, method='PUT', data={'assignee_ids': []})
    print(f"Cleared assignees for Issue #{iid}")

def update_issue_content_in_project(config, args):
    if len(args) < 3:
        print("Usage: update_issue_content_in_project <project_id> <iid> <title> [description]")
        sys.exit(1)
        
    project_id = args[0]
    iid = args[1]
    data = {'title': args[2]}
    
    if len(args) > 3:
        data['description'] = args[3]
        
    endpoint = f"projects/{project_id}/issues/{iid}"
    result = make_post_put_request(config, endpoint, method='PUT', data=data)
    print(f"Updated Issue #{iid} in Project {project_id}: {result['web_url']}")

def create_issue_link(config, args):
    if len(args) < 4:
        print("Usage: create_issue_link <source_project_id> <source_issue_iid> <target_project_id> <target_issue_iid>")
        sys.exit(1)
        
    source_project_id = args[0]
    source_issue_iid = args[1]
    target_project_id = args[2]
    target_issue_iid = args[3]
    
    endpoint = f"projects/{source_project_id}/issues/{source_issue_iid}/links"
    data = {
        'target_project_id': target_project_id,
        'target_issue_iid': target_issue_iid
    }
    
    result = make_post_put_request(config, endpoint, method='POST', data=data)
    print(f"Linked Issue #{source_issue_iid} (Project {source_project_id}) to Issue #{target_issue_iid} (Project {target_project_id})")

def comment_issue(config, args):
    if len(args) < 2:
        print("Usage: comment_issue <iid> <comment_text>")
        sys.exit(1)
        
    iid = args[0]
    body = args[1]
    
    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes"
    result = make_post_put_request(config, endpoint, method='POST', data={'body': body})
    print(f"Comment added to #{iid} (Note ID: {result['id']})")

def comment_issue_from_file(config, args):
    if len(args) < 2:
        print("Usage: comment_issue_from_file <iid> <filepath>")
        sys.exit(1)
    
    iid = args[0]
    filepath = args[1]
    
    try:
        with open(filepath, 'r') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes"
    result = make_post_put_request(config, endpoint, method='POST', data={'body': text})
    print(f"Added comment from file to Issue #{iid}")

_UMLAUT_MAP = {
    'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
    'à': 'a', 'á': 'a', 'â': 'a', 'è': 'e', 'é': 'e', 'ê': 'e',
    'ì': 'i', 'í': 'i', 'ò': 'o', 'ó': 'o', 'ô': 'o', 'ù': 'u', 'ú': 'u',
}

def _slugify(title):
    text = title.lower()
    for src, dst in _UMLAUT_MAP.items():
        text = text.replace(src, dst)
    slug = ''.join(c if c.isalnum() else '-' for c in text)
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')

def _store_original(config, kind, iid, title, content):
    """Legt die bisherige Fassung als Markdown-Datei im Projekt-Repository ab."""
    if not config.get('repo'):
        print(
            "Error: Repository-Pfad fehlt.\n"
            "Aufruf mit --repo <pfad-zum-projekt-repo> wiederholen.",
            file=sys.stderr
        )
        sys.exit(1)

    target_dir = os.path.join(config['repo'], 'docs', 'original', kind)
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}_{iid}_{_slugify(title)}.md"
    target = os.path.join(target_dir, filename)

    with open(target, 'w') as f:
        f.write(content)

    print(f"Stored original in {target}")

def _store_original_note(config, iid, note_id):
    issue = make_request(config, f"projects/{config['project_id']}/issues/{iid}")
    note = make_request(config, f"projects/{config['project_id']}/issues/{iid}/notes/{note_id}")
    _store_original(config, 'plans', iid, issue['title'], note['body'])

def edit_comment(config, args):
    if len(args) < 3:
        print("Usage: edit_comment <iid> <note_id> <new_text> --repo <pfad>")
        sys.exit(1)

    iid = args[0]
    note_id = args[1]
    body = args[2]

    _store_original_note(config, iid, note_id)

    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes/{note_id}"
    result = make_post_put_request(config, endpoint, method='PUT', data={'body': body})
    print(f"Comment {note_id} on #{iid} updated.")

def edit_comment_from_file(config, args):
    if len(args) < 3:
        print("Usage: edit_comment_from_file <iid> <note_id> <filepath> --repo <pfad>")
        sys.exit(1)

    iid = args[0]
    note_id = args[1]
    filepath = args[2]

    try:
        with open(filepath, 'r') as f:
            body = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    _store_original_note(config, iid, note_id)

    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes/{note_id}"
    result = make_post_put_request(config, endpoint, method='PUT', data={'body': body})
    print(f"Comment {note_id} on #{iid} updated from file.")

def reply_discussion(config, args):
    if len(args) < 3:
        print("Usage: reply_discussion <iid> <discussion_id> <text>")
        sys.exit(1)
        
    iid = args[0]
    discussion_id = args[1]
    body = args[2]
    
    endpoint = f"projects/{config['project_id']}/issues/{iid}/discussions/{discussion_id}/notes"
    result = make_post_put_request(config, endpoint, method='POST', data={'body': body})
    print(f"Reply added to discussion {discussion_id} (Note ID: {result['id']})")

def create_issue(config, args):
    if len(args) < 1:
        print("Usage: create_issue <title> [description] [milestone_id] [assignee_id] [labels]")
        sys.exit(1)
        
    data = {
        'title': args[0]
    }
    if len(args) > 1: data['description'] = args[1]
    if len(args) > 2 and args[2]: data['milestone_id'] = int(args[2])
    if len(args) > 3 and args[3]: data['assignee_ids'] = [int(args[3])]
    if len(args) > 4: data['labels'] = args[4]
    
    endpoint = f"projects/{config['project_id']}/issues"
    result = make_post_put_request(config, endpoint, method='POST', data=data)
    print(f"Created Issue #{result['iid']}: {result['web_url']}")

def create_issue_in_project(config, args):
    if len(args) < 2:
        print("Usage: create_issue_in_project <project_id> <title> [description] [milestone_id] [assignee_id] [labels]")
        sys.exit(1)
        
    project_id = args[0]
    data = {
        'title': args[1]
    }
    if len(args) > 2: data['description'] = args[2]
    if len(args) > 3 and args[3]: data['milestone_id'] = int(args[3])
    if len(args) > 4 and args[4]: data['assignee_ids'] = [int(args[4])]
    if len(args) > 5: data['labels'] = args[5]
    
    endpoint = f"projects/{project_id}/issues"
    result = make_post_put_request(config, endpoint, method='POST', data=data)
    print(f"Created Issue #{result['iid']}: {result['web_url']}")

def list_milestones(config, args):
    endpoint = f"projects/{config['project_id']}/milestones"
    data = make_request_all_pages(config, endpoint)
    for ms in data:
        print(f"ID: {ms['id']} - Title: {ms['title']} (State: {ms['state']})")

def get_milestone(config, args):
    if len(args) < 1:
        print("Usage: get_milestone <milestone_id>")
        sys.exit(1)

    milestone_id = args[0]
    endpoint = f"projects/{config['project_id']}/milestones/{milestone_id}"
    data = make_request(config, endpoint)

    print(f"Title: {data['title']}")
    print(f"State: {data['state']}")
    print(f"Due Date: {data.get('due_date') or '-'}")
    print(f"Description:\n{data['description']}")

def update_milestone_description_from_file(config, args):
    if len(args) < 2:
        print("Usage: update_milestone_description_from_file <milestone_id> <filepath>")
        sys.exit(1)

    milestone_id = args[0]
    filepath = args[1]

    try:
        with open(filepath, 'r') as f:
            description = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    endpoint = f"projects/{config['project_id']}/milestones/{milestone_id}"
    make_post_put_request(config, endpoint, method='PUT', data={'description': description})
    print(f"Updated description for Milestone {milestone_id} from file")

def set_issue_milestone(config, args):
    if len(args) < 2:
        print("Usage: set_issue_milestone <iid> <milestone_id>")
        sys.exit(1)

    iid = args[0]
    milestone_id = int(args[1])

    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    result = make_post_put_request(config, endpoint, method='PUT', data={'milestone_id': milestone_id})
    milestone = result.get('milestone')
    print(f"Issue #{iid} assigned to milestone: {milestone['title'] if milestone else '-'}")

def list_group_milestones(config, args):
    if len(args) < 1:
        print("Usage: list_group_milestones <group_id>")
        sys.exit(1)

    group_id = args[0]
    endpoint = f"groups/{group_id}/milestones"
    data = make_request_all_pages(config, endpoint, {'state': 'active'})
    for ms in data:
        print(f"ID: {ms['id']} - IID: {ms['iid']} - Title: {ms['title']} (State: {ms['state']})")

def list_group_milestone_issues(config, args):
    if len(args) < 2:
        print("Usage: list_group_milestone_issues <group_id> <milestone_id>")
        sys.exit(1)

    group_id, milestone_id = args[0], args[1]
    endpoint = f"groups/{group_id}/milestones/{milestone_id}/issues"
    data = make_request_all_pages(config, endpoint)
    for issue in data:
        labels = ', '.join(issue['labels'])
        assignees = ', '.join(a['name'] for a in issue['assignees'])
        print(f"Project: {issue['project_id']} - #{issue['iid']} - {issue['title']} "
              f"(State: {issue['state']}) (Labels: {labels}) (Assignees: {assignees})")

def set_group_milestone_description(config, args):
    if len(args) < 3:
        print("Usage: set_group_milestone_description <group_id> <milestone_id> <filepath>")
        sys.exit(1)

    group_id, milestone_id, filepath = args[0], args[1], args[2]

    try:
        with open(filepath, 'r') as f:
            description = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    endpoint = f"groups/{group_id}/milestones/{milestone_id}"
    make_post_put_request(config, endpoint, method='PUT', data={'description': description})
    print(f"Updated description for Group Milestone {milestone_id} from file")

def list_labels(config, args):
    endpoint = f"projects/{config['project_id']}/labels"
    data = make_request_all_pages(config, endpoint)
    for label in data:
        description = label.get('description') or '-'
        print(f"{label['name']} (Color: {label['color']}) - {description}")

def create_merge_request(config, args):
    if len(args) < 3:
        print("Usage: create_merge_request <source_branch> <target_branch> <title> [description]")
        sys.exit(1)
        
    data = {
        'source_branch': args[0],
        'target_branch': args[1],
        'title': args[2],
        'remove_source_branch': True
    }
    if len(args) > 3: data['description'] = args[3]
    
    endpoint = f"projects/{config['project_id']}/merge_requests"
    result = make_post_put_request(config, endpoint, method='POST', data=data)
    print(f"Created MR !{result['iid']}: {result['web_url']}")

def list_users(config, args):
    if len(args) < 1:
        print("Usage: list_users <search_term>")
        sys.exit(1)
    
    search = args[0]
    data = make_request(config, 'users', {'search': search})
    
    print(f"Found {len(data)} users:")
    for user in data:
        print(f"ID: {user['id']} - Username: {user['username']} - Name: {user['name']} (State: {user['state']})")

def get_user_details(config, args):
    if len(args) < 1:
        print("Usage: get_user <user_id>")
        sys.exit(1)
        
    user_id = args[0]
    data = make_request(config, f"users/{user_id}")
    
    print(json.dumps(data, indent=2))

def list_user_issues(config, args):
    if len(args) < 1:
        print("Usage: list_user_issues <user_id>")
        sys.exit(1)
    user_id = args[0]
    params = {'author_id': user_id, 'per_page': 50, 'state': 'all'}
    endpoint = f"projects/{config['project_id']}/issues"
    data = make_request(config, endpoint, params)
    print(f"Issues created by user {user_id}:")
    for issue in data:
        print(f"#{issue['iid']} - {issue['title']}")

def list_issue_notes(config, args):
    if len(args) < 1:
        print("Usage: list_issue_notes <iid>")
        sys.exit(1)
    iid = args[0]
    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes"
    data = make_request_all_pages(config, endpoint, {'sort': 'desc'})
    for note in data:
        if not note['system']:
            print(f"--- NOTE {note['id']} (Discussion: {note.get('discussion_id')}) by {note['author']['name']} ---")
            print(note['body'])

def list_issues_updated_since(config, args):
    if len(args) < 1:
        print("Usage: list_issues_updated_since <iso_timestamp>")
        sys.exit(1)

    since = args[0]
    params = {'scope': 'all', 'state': 'opened', 'updated_after': since}
    endpoint = f"projects/{config['project_id']}/issues"
    data = make_request_all_pages(config, endpoint, params)

    print(f"Found {len(data)} issues updated after {since}:")
    for issue in data:
        assignees = ', '.join([a['name'] for a in issue['assignees']]) or '-'
        print(
            f"#{issue['iid']} - {issue['title']} "
            f"(Updated: {issue['updated_at']} | Assignees: {assignees} | "
            f"Labels: {', '.join(issue['labels'])})"
        )

def _parse_timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def list_issue_notes_since(config, args):
    if len(args) < 2:
        print("Usage: list_issue_notes_since <iid> <iso_timestamp>")
        sys.exit(1)

    iid = args[0]
    since = args[1]
    since_ts = _parse_timestamp(since)
    endpoint = f"projects/{config['project_id']}/issues/{iid}/notes"
    data = make_request_all_pages(config, endpoint, {'sort': 'asc'})

    notes = [
        n for n in data
        if not n['system'] and _parse_timestamp(n['created_at']) > since_ts
    ]
    print(f"{len(notes)} Notes on #{iid} after {since}:")
    for note in notes:
        print(
            f"--- NOTE {note['id']} (Created: {note['created_at']} | "
            f"Discussion: {note.get('discussion_id')}) by {note['author']['name']} ---"
        )
        print(note['body'])

def link_issues(config, args):
    """Link two issues together as related items"""
    if len(args) < 2:
        print("Usage: link_issues <source_iid> <target_iid>")
        sys.exit(1)
    
    source_iid = args[0]
    target_iid = args[1]
    
    # Create link using issue links API
    endpoint = f"projects/{config['project_id']}/issues/{source_iid}/links"
    data = {
        'target_project_id': config['project_id'],
        'target_issue_iid': int(target_iid)
    }
    
    try:
        result = make_post_put_request(config, endpoint, method='POST', data=data)
        print(f"Successfully linked #{source_iid} with #{target_iid}")
    except Exception as e:
        print(f"Failed to link issues: {e}")
        sys.exit(1)

def get_issue_links(config, args):
    if len(args) < 1:
        print("Usage: get_issue_links <iid>")
        sys.exit(1)
        
    iid = args[0]
    endpoint = f"projects/{config['project_id']}/issues/{iid}/links"
    data = make_request(config, endpoint)
    
    print(f"Found {len(data)} linked issues:")
    for link in data:
        print(f"IID: {link['iid']} - Title: {link['title']} - State: {link['state']} - Type: {link.get('link_type', 'related')}")

def list_projects(config, args):
    search = args[0] if len(args) > 0 else ""
    data = make_request(config, 'projects', {'search': search, 'simple': True})
    
    print(f"Found {len(data)} projects:")
    for project in data:
        print(f"ID: {project['id']} - Name: {project['name']} - Path: {project['path_with_namespace']}")

def update_merge_request(config, args):
    if len(args) < 2:
        print("Usage: update_merge_request <iid> <state_event> [target_project_id]")
        print("Events: close, reopen")
        sys.exit(1)
        
    iid = args[0]
    state_event = args[1] # close, reopen
    
    # Optional: override project_id for this call if provided
    # (Checking if args[2] looks like a project ID, otherwise assume it's part of standard config)
    # Actually, let's keep it simple and use the config's project_id or the --project_id flag
    
    endpoint = f"projects/{config['project_id']}/merge_requests/{iid}"
    result = make_post_put_request(config, endpoint, method='PUT', data={'state_event': state_event})
    print(f"Updated MR !{iid} status to: {result['state']}")

def _replace_description(config, iid, new_description):
    current = make_request(config, f"projects/{config['project_id']}/issues/{iid}")
    _store_original(config, 'tickets', iid, current['title'], current['description'])
    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    return make_post_put_request(config, endpoint, method='PUT', data={'description': new_description})

def update_issue_description(config, args):
    if len(args) < 2:
        print("Usage: update_issue_description <iid> <description> --repo <pfad>")
        sys.exit(1)

    iid = args[0]
    description = args[1]

    result = _replace_description(config, iid, description)
    print(f"Updated description for Issue #{iid}")

def update_issue_description_from_file(config, args):
    if len(args) < 2:
        print("Usage: update_issue_description_from_file <iid> <filepath> --repo <pfad>")
        sys.exit(1)

    iid = args[0]
    filepath = args[1]

    try:
        with open(filepath, 'r') as f:
            description = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    result = _replace_description(config, iid, description)
    print(f"Updated description for Issue #{iid} from file")

def update_issue_title(config, args):
    if len(args) < 2:
        print("Usage: update_issue_title <iid> <title>")
        sys.exit(1)
    
    iid = args[0]
    title = args[1]
    
    endpoint = f"projects/{config['project_id']}/issues/{iid}"
    result = make_post_put_request(config, endpoint, method='PUT', data={'title': title})
    print(f"Updated title for Issue #{iid}")


def list_wiki(config, args):
    endpoint = f"projects/{config['project_id']}/wikis"
    params = {'with_content': False}
    data = make_request(config, endpoint, params)
    
    print(f"Found {len(data)} wiki pages:")
    for page in data:
        print(f"- {page['slug']} ({page['title']})")

def list_wiki_full(config, args):
    endpoint = f"projects/{config['project_id']}/wikis"
    params = {'with_content': True}
    data = make_request(config, endpoint, params)
    
    for page in data:
        print(f"--- WIKI PAGE: {page['slug']} ---")
        print(f"Title: {page['title']}")
        print(f"Content:\n{page['content']}\n")

    print(f"Title: {data['title']}")
def get_wiki(config, args):
    if len(args) < 1:
        print("Usage: get_wiki <slug>")
        sys.exit(1)
        
    slug = urllib.parse.quote(args[0], safe='/')
    endpoint = f"projects/{config['project_id']}/wikis/{slug}"
    data = make_request(config, endpoint)
    
    print(f"Title: {data['title']}")
    print(f"Slug: {data['slug']}")
    print(f"Content:\n{data['content']}")

def delete_wiki(config, args):
    if len(args) < 1:
        print("Usage: delete_wiki <slug>")
        sys.exit(1)
        
    slug = urllib.parse.quote(args[0], safe='/')
    endpoint = f"projects/{config['project_id']}/wikis/{slug}"
    
    url = f"{config['gitlab_url']}/api/v4/{endpoint}"
    req = urllib.request.Request(url, method='DELETE')
    req.add_header('PRIVATE-TOKEN', config['private_token'])
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                print(f"Deleted wiki page: {args[0]}")
            else:
                print(f"Status: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: query_gitlab.py <command> [args...]")
        print("Commands: list_issues, get_issue, list_assigned_issues")
        print("          update_issue <iid> <add_label|remove_label|assign_user> <value>")
        print("          comment_issue <iid> <text>")
        print("          edit_comment <iid> <note_id> <text> --repo <pfad>")
        print("          edit_comment_from_file <iid> <note_id> <filepath> --repo <pfad>")
        print("          update_issue_description <iid> <description> --repo <pfad>")
        print("          update_issue_description_from_file <iid> <filepath> --repo <pfad>")
        print("          reply_discussion <iid> <discussion_id> <text>")
        print("          create_issue <title> [description] [milestone_id] [assignee_id] [labels]")
        print("          list_milestones")
        print("          get_milestone <milestone_id>")
        print("          update_milestone_description_from_file <milestone_id> <filepath>")
        print("          set_issue_milestone <iid> <milestone_id>")
        print("          list_group_milestones <group_id>")
        print("          list_group_milestone_issues <group_id> <milestone_id>")
        print("          set_group_milestone_description <group_id> <milestone_id> <filepath>")
        print("          list_labels")
        print("          create_merge_request <source_branch> <target_branch> <title> [description]")
        print("          list_wiki")
        print("          delete_wiki <slug>")
        print("          get_wiki <slug>")
        print("          list_users <search_term>")
        print("          get_user <user_id>")
        print("          list_user_issues <user_id>")
        print("          list_issue_notes <iid>")
        print("          list_issues_updated_since <iso_timestamp>")
        print("          list_issue_notes_since <iid> <iso_timestamp>")
        print("          link_issues <source_iid> <target_iid>")
        print("          get_milestone_issues <milestone_title>")
        print("          get_issue_full <iid>")
        print("          clear_assignees <iid>")
        sys.exit(1)
        
    config = load_config()
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if '--project_id' in args:
        idx = args.index('--project_id')
        config['project_id'] = args[idx+1]
        args.pop(idx+1)
        args.pop(idx)

    if '--repo' in args:
        idx = args.index('--repo')
        config['repo'] = args[idx+1]
        args.pop(idx+1)
        args.pop(idx)
        
    if command == 'list_issues':
        list_issues(config, args)
    elif command == 'get_issue':
        get_issue(config, args)
    elif command == 'list_assigned_issues':
        list_assigned_issues(config, args)
    elif command == 'update_issue':
        update_issue(config, args)
    elif command == 'comment_issue':
        comment_issue(config, args)
    elif command == 'comment_issue_from_file':
        comment_issue_from_file(config, args)
    elif command == 'edit_comment':
        edit_comment(config, args)
    elif command == 'edit_comment_from_file':
        edit_comment_from_file(config, args)
    elif command == 'reply_discussion':
        reply_discussion(config, args)
    elif command == "create_issue":
        create_issue(config, args)
    elif command == "create_issue_in_project":
        create_issue_in_project(config, args)
    elif command == "update_issue_content_in_project":
        update_issue_content_in_project(config, args)
    elif command == "create_issue_link":
        create_issue_link(config, args)
    elif command == "list_milestones":
        list_milestones(config, args)
    elif command == "get_milestone":
        get_milestone(config, args)
    elif command == "update_milestone_description_from_file":
        update_milestone_description_from_file(config, args)
    elif command == "set_issue_milestone":
        set_issue_milestone(config, args)
    elif command == "list_group_milestones":
        list_group_milestones(config, args)
    elif command == "list_group_milestone_issues":
        list_group_milestone_issues(config, args)
    elif command == "set_group_milestone_description":
        set_group_milestone_description(config, args)
    elif command == "list_labels":
        list_labels(config, args)
    elif command == 'create_merge_request':
        create_merge_request(config, args)
    elif command == 'list_wiki':
        list_wiki(config, args)
    elif command == 'list_wiki_full':
        list_wiki_full(config, args)
    elif command == 'get_wiki':
        get_wiki(config, args)
    elif command == 'delete_wiki':
        delete_wiki(config, args)
    elif command == 'list_users':
        list_users(config, args)
    elif command == 'get_user':
        get_user_details(config, args)
    elif command == 'list_user_issues':
        list_user_issues(config, args)
    elif command == 'list_issue_notes':
        list_issue_notes(config, args)
    elif command == 'list_issues_updated_since':
        list_issues_updated_since(config, args)
    elif command == 'list_issue_notes_since':
        list_issue_notes_since(config, args)
    elif command == 'link_issues':
        link_issues(config, args)
    elif command == 'update_issue_description':
        update_issue_description(config, args)
    elif command == 'update_issue_description_from_file':
        update_issue_description_from_file(config, args)
    elif command == 'update_issue_title':
        update_issue_title(config, args)
    elif command == 'get_issue_links':
        get_issue_links(config, args)
    elif command == 'list_projects':
        list_projects(config, args)
    elif command == 'update_merge_request':
        update_merge_request(config, args)
    elif command == 'get_milestone_issues':
        get_milestone_issues(config, args)
    elif command == 'get_issue_full':
        get_issue_full(config, args)
    elif command == 'clear_assignees':
        clear_assignees(config, args)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
