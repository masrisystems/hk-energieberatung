---
name: GitLab Integration
description: Interact with a GitLab instance — read and manage issues, merge requests, comments, wiki, and cross-project links via a Python script.
---

# GitLab Integration Skill

This skill provides access to a GitLab instance via the REST API.
The primary interface is the Python script `scripts/query_gitlab.py`.

## Configuration

Connection settings are read from **`.agent/config.json`** (primary location):

```json
{
  "gitlab_url": "https://gitlab.example.com",
  "gitlab_project_id": "42",
  "private_token": ""
}
```

- **`gitlab_url`** — Base URL of the GitLab instance
- **`gitlab_project_id`** — Default project ID (used when no `--project_id` flag is given)
- **`private_token`** — Personal Access Token; determines the identity used for API actions (comments, assignments) AND Git over HTTPS

> [!IMPORTANT]
> The Git Commit Author (set via `git config` or `--author`) is separate from the GitLab API Actor.
> The `private_token` must belong to the agent's account to ensure actions appear under the correct identity.
> Never commit a real token to the repository — set it manually after init.

**Fallback:** If `gitlab_url` or `private_token` are missing in `.agent/config.json`, the script
falls back to `.agent/skills/gitlab-integration/config.json`.
When credentials are found there, migrate them to `.agent/config.json` — the skill-local file is
not the canonical location.

To look up available project IDs:
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_projects "search term"
```

## Multi-Project Support

Any command can target a different project by appending `--project_id <id>`:

```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issues --project_id 29
```

---

## Usage

### Issues

**List open issues** (optionally filter by keyword or label):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issues
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issues "search term"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issues --label "Doing"
```

**List issues assigned to the authenticated user** (projektübergreifend, mit Projekt-ID je Issue):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_assigned_issues
```

**Get issue details:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_issue <iid>
```

**List issues changed since a timestamp** (Assignees und Labels je Issue):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issues_updated_since 2026-08-02T14:00:00Z
```

**Create issue (default project):**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py create_issue "Titel" "Beschreibung"
```

**Create issue in a specific project:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py create_issue_in_project <project_id> "Titel" "Beschreibung"
```

**Update issue (labels, assignee, state):**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue <iid> add_label "Doing"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue <iid> remove_label "Doing"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue <iid> assign_user "Name"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue <iid> close
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue <iid> reopen
```

**Labels des Projekts auflisten** (Name, Farbe, Beschreibung):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_labels
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_labels --project_id <id>
```

**Update issue title or description:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue_title <iid> "New Title"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue_description <iid> "New description" --repo <pfad-zum-projekt-repo>
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue_description_from_file <iid> path/to/file.md --repo <pfad-zum-projekt-repo>
```

**Update issue in a specific project:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_issue_content_in_project <project_id> <iid> "Neuer Titel" "Neue Beschreibung"
```

### Comments & Discussions

**Add a comment:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py comment_issue <iid> "Comment text"
```

**Add a comment from a file:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py comment_issue_from_file <iid> path/to/file.md
```

**Edit an existing comment:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py edit_comment <iid> <note_id> "New text" --repo <pfad-zum-projekt-repo>
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py edit_comment_from_file <iid> <note_id> path/to/file.md --repo <pfad-zum-projekt-repo>
```

**Reply to a discussion thread:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py reply_discussion <iid> <discussion_id> "Reply text"
```

**List all non-system notes on an issue:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issue_notes <iid>
```

**List notes created after a timestamp:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_issue_notes_since <iid> 2026-08-02T14:00:00Z
```

### Issue Links

**Link two issues within the default project:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py link_issues <source_iid> <target_iid>
```

**Link issues across projects:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py create_issue_link <source_project_id> <source_iid> <target_project_id> <target_iid>
```

**Get linked issues:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_issue_links <iid>
```

### Merge Requests

**Create a merge request:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py create_merge_request <source_branch> <target_branch> "Title" "Description"
```

**Update MR state:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_merge_request <iid> close
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_merge_request <iid> reopen
```

### Users & Projects

**Search users:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_users "search term"
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_user <user_id>
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_user_issues <user_id>
```

**Search projects:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_projects "search term"
```

### Wiki

```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_wiki
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_wiki_full
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_wiki <slug>
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py delete_wiki <slug>
```

---

## Milestones

```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_milestones
```

**Issues eines Milestones laden** (vollständig paginiert, Titel exakt wie in GitLab):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_milestone_issues "<milestone_title>"
```

**Einen Milestone mit seiner Beschreibung laden:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_milestone <milestone_id>
```

**Beschreibung eines Milestones aus einer Datei setzen:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py update_milestone_description_from_file <milestone_id> path/to/file.md
```
Der Dateiinhalt ersetzt die bisherige Beschreibung vollständig.

**Ein bestehendes Issue einem Milestone zuordnen:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py set_issue_milestone <iid> <milestone_id>
```

**Gruppen-Milestones auflisten** (aktive Milestones einer Gruppe):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_group_milestones <group_id>
```

**Issues eines Gruppen-Milestones laden** (projektübergreifend, mit Projekt-ID je Issue):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py list_group_milestone_issues <group_id> <milestone_id>
```

**Beschreibung eines Gruppen-Milestones aus einer Datei setzen:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py set_group_milestone_description <group_id> <milestone_id> path/to/file.md
```
Der Dateiinhalt ersetzt die bisherige Beschreibung vollständig.

---

## Issue vollständig laden

**Issue inklusive aller Notes in einem Aufruf** (vollständig paginiert):
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py get_issue_full <iid>
```

---

## Bearbeiter leeren

**Alle Bearbeiter eines Issues entfernen:**
```bash
python3 .agent/skills/gitlab-integration/scripts/query_gitlab.py clear_assignees <iid>
```

---

## Pagination

`list_issues`, `list_issues_updated_since`, `list_milestones`, `list_issue_notes`,
`list_issue_notes_since`, `get_milestone_issues` und die Notes
aus `get_issue_full` folgen dem `Link`-Header der GitLab-API und aggregieren alle Seiten —
das Ergebnis ist bei keinem dieser Befehle auf die erste Ergebnisseite begrenzt.

---

## Originalfassungen

Vor jeder Änderung einer Ticketbeschreibung oder einer Note sichert das Skript die bisherige
Fassung als Markdown-Datei im Projekt-Repository:

| Geändert wird | Ablage |
|---|---|
| Ticketbeschreibung | `<repo>/docs/original/tickets/` |
| Note (z.B. ein Implementierungsplan) | `<repo>/docs/original/plans/` |

Der Dateiname lautet `YYYY-MM-DD_HH-MM-SS_<iid>_<titel-in-kebab-case>.md`. Am Ticket entsteht
dabei kein Kommentar.

Betroffen sind `update_issue_description`, `update_issue_description_from_file`,
`edit_comment` und `edit_comment_from_file`. Alle vier verlangen
`--repo <pfad-zum-projekt-repo>`; fehlt das Argument, brechen sie ab, ohne etwas zu ändern.
Ist der Pfad des Projekt-Repositorys nicht bekannt, wird er zuvor über den Projektdatensatz in
Maestro aufgelöst.

---

## Autorschaft

Notes anderer Autoren werden nicht bearbeitet. Wer Korrekturbedarf an einer fremden Note
feststellt — insbesondere an einem fremden Implementierungsplan —, dokumentiert ihn als
eigenen Kommentar und weist das Issue dem Autor zu
(`update_issue <iid> assign_user "<Name>"`). Die Fortführung des Artefakts liegt beim
Autor.

---

## Status-Label-Zuordnung

Ein Label wird ausschließlich gesetzt oder entfernt, nachdem es über den
Maestro-Projektdatensatz aufgelöst wurde:

1. `maestro_record(archetype="projects", identifier="<projekt-uuid>")` aufrufen.
2. Im Feld `status_labels` den Eintrag zum Echo-Status der auszuführenden Operation lesen.
3. Genau diesen Labelnamen an `update_issue <iid> add_label` übergeben. Trägt das Issue
   bereits das Label eines anderen Status desselben Projekts, wird dieses zuvor über
   `update_issue <iid> remove_label` entfernt.

Trägt `status_labels` zum Echo-Status keinen Eintrag, unterbleibt die Labeländerung und
der Vorgang wird mit dem betroffenen Status und Projekt benannt. Ohne
Maestro-Projektdatensatz unterbleibt die Labeländerung ebenfalls.

Labelnamen stehen in keinem Skill, keinem Workflow und keinem Skript des Frameworks.

---

## Extending the Skill

When a required GitLab operation is not yet available:
1. Add a new function and command to `scripts/query_gitlab.py`
2. Document the new command in this SKILL.md
