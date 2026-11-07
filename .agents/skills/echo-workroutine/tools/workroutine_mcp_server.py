#!/usr/bin/env python3
"""
workroutine_mcp_server.py — MCP-Server für den mechanischen Ticket-Todo-Loop der
`work-routine` im echo-Framework (#308, #322, #370).

Zwei Tools:
  workroutine_next      — nächstes offenes Ticket-Todo, leitet den konkreten Arbeitsauftrag ab
  workroutine_complete   — schließt einen ticketbezogenen Arbeitsschritt ohne Artefaktbezug ab
                          (Ticketbeschreibung, Beanstandungs-/Prüfergebnis-Übergabe)

Artefaktbezogene Abschlüsse (Implementierungsplan bei `approved`, Walkthrough bei `doing`)
laufen seit #322 nicht mehr über `workroutine_complete`, sondern direkt über
`create_implementation_plan`/`create_walkthrough` (Artefakt-MCP) mit deren optionalem
`todo`-Parameter — `workroutine_next` gibt dafür die Todo-UUID mit aus. Ermittlung von
aktivem Plan/Walkthrough läuft über `todo_completion.find_active_plan`/`find_active_walkthrough`
auf Basis von `list_implementation_plans`/`view_implementation_plan`/`list_walkthroughs`/
`view_walkthrough` aus dem Artefakt-MCP; die Planfreigabe über dessen `update_implementation_plan`.

Zielpersonen-Ermittlung und Todo-Abschluss teilt sich dieser Server mit dem Artefakt-MCP
über `todo_completion.py`.

MCP-Eintrag in .mcp.json:
  {
    "mcpServers": {
      "echo-workroutine": {
        "command": "python3",
        "args": [".agent/skills/echo-workroutine/tools/workroutine_mcp_server.py"]
      }
    }
  }

Voraussetzungen:
  python3 -m pip install fastmcp
"""

import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
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
_MAESTRO_TOOLS_DIR = _AGENT_DIR / 'skills' / 'echo-maestro' / 'tools'

if str(_MAESTRO_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_MAESTRO_TOOLS_DIR))

import maestro_client as mc  # noqa: E402

mcp = FastMCP("echo-workroutine")

_NO_STATUS_LABEL = "kein Statuslabel"
_TERMINAL_NO_AGENT_STATUSES = {"testing", "done", "rejected", "discarded"}


def _with_project(cmd_text: str, project_ucid: str | None) -> str:
    if project_ucid is None:
        return cmd_text
    return re.sub(r'workroutine_complete\(', f'workroutine_complete(project_ucid="{project_ucid}", ', cmd_text)


def _load_todo_completion_module():
    todo_file = Path(__file__).parent / 'todo_completion.py'
    spec = importlib.util.spec_from_file_location('todo_completion', todo_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_todo_completion = _load_todo_completion_module()
_TICKET_TODO = _todo_completion._TICKET_TODO


def _load_operations_module(ticket_system: str):
    ops_file = Path(__file__).parent / 'ticket_systems' / f'{ticket_system}.py'
    spec = importlib.util.spec_from_file_location(f"ticket_source_operations_{ticket_system}", ops_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_intake_module():
    intake_file = Path(__file__).parent / 'intake_ticket_sources.py'
    spec = importlib.util.spec_from_file_location("intake_ticket_sources", intake_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_artifacts_module():
    artifacts_file = Path(__file__).resolve().parents[2] / 'echo-artifacts' / 'tools' / 'artifacts_mcp_server.py'
    spec = importlib.util.spec_from_file_location('artifacts_mcp_server', artifacts_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_config() -> dict:
    return json.loads((_AGENT_DIR / "config.json").read_text(encoding="utf-8"))


# ── Ticket-Todo-Loop (#308, #322) ───────────────────────────────────────────


def _records(result) -> list:
    return result if isinstance(result, list) else result.get("data", [])


def _load_project(base_url: str, project_ucid: str) -> dict:
    result = mc._http_get(base_url, f"projects/agent?ucid={project_ucid}&per_page=1")
    records = _records(result)
    if not records:
        raise RuntimeError(f"Kein Maestro-Projekt mit ucid {project_ucid!r} gefunden.")
    return mc._http_get(base_url, f"projects/{records[0]['uuid']}/agent")


def _ticket_todo_ops(project_ucid: str, ticket_number: str, base_url: str) -> tuple[dict, object]:
    project = _load_project(base_url, project_ucid)
    ops = _load_operations_module(project["ticket_system"])
    return project, ops


def _is_open_todo(todo: dict) -> bool:
    return not todo.get("status")


def _first_open_ticket_todo(chronicle_day: dict, project_ucid: str | None = None) -> dict | None:
    for todo in chronicle_day.get("todos", []):
        if not _is_open_todo(todo):
            continue
        match = _TICKET_TODO.match(todo.get("name", ""))
        if not match:
            continue
        if project_ucid is not None and match["project"] != project_ucid:
            continue
        return todo
    return None


def _comments_since_assignment(ticket: dict) -> list[dict]:
    """Alle Kommentare, die nach der aktuellen Zuweisung entstanden sind — unabhängig vom Autor."""
    assigned_at = ticket["assigned_at"]
    if assigned_at is None:
        return []
    cutoff = datetime.fromisoformat(assigned_at)
    return [c for c in ticket["comments"] if datetime.fromisoformat(c["created_at"]) > cutoff]


def _format_comments(comments: list[dict]) -> str:
    if not comments:
        return "(keine Rückmeldung hinterlegt)"
    return "\n\n".join(f"--- {c['created_at']} von {c['author_name']} ---\n{c['body']}" for c in comments)


def _commit_refs(ticket: dict) -> list[str]:
    pattern = re.compile(r"\(#\d+\)\s*[0-9a-f]{7,40}|[0-9a-f]{7,40}")
    refs: list[str] = []
    for text in [ticket["description"]] + [c["body"] for c in ticket["comments"]]:
        refs.extend(pattern.findall(text or ""))
    return refs


_UMLAUT_MAP = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def _canonical_ticket_branch(ticket_type: str, ticket_number: str, title: str) -> str:
    prefix = "bugfix" if ticket_type == "bug" else "feature"
    normalized = title.lower().translate(_UMLAUT_MAP)
    normalized = unicodedata.normalize("NFKD", normalized).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return f"{prefix}/{ticket_number}-{normalized}"


def _run_git(repo, *args) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} fehlgeschlagen: {result.stderr.strip()}")
    return result.stdout.strip()


def _git_ref_exists(repo, ref) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def _load_onboarding_module():
    path = _AGENT_DIR / "scripts" / "onboarding.py"
    spec = importlib.util.spec_from_file_location("onboarding", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _prepare_ticket_branch(project: dict, ticket_type: str, ticket_number: str, title: str) -> str:
    repo = mc.project_directory(project)
    branch = _canonical_ticket_branch(ticket_type, ticket_number, title)

    _run_git(repo, "fetch", "origin")
    local_exists = _git_ref_exists(repo, branch)
    remote_exists = _git_ref_exists(repo, f"origin/{branch}")
    current = _run_git(repo, "branch", "--show-current")

    if local_exists:
        if current != branch:
            _run_git(repo, "checkout", branch)
    elif remote_exists:
        _run_git(repo, "checkout", "-b", branch, f"origin/{branch}")
    else:
        _run_git(repo, "checkout", "-b", branch)

    if remote_exists:
        _run_git(repo, "pull", "origin", branch)

    verified = _run_git(repo, "branch", "--show-current")
    if verified != branch:
        raise RuntimeError(
            f"Branch-Vorbereitung fehlgeschlagen: aktiver Branch ist {verified!r}, erwartet {branch!r}."
        )
    return branch


@mcp.tool()
def workroutine_next(project_ucid: str | None = None) -> str:
    """Wählt das nächste offene Ticket-Todo aus dem heutigen ChronicleDay und leitet daraus
    den konkreten Arbeitsauftrag ab. Führt vorab den Ereignisabgleich aus."""
    artifacts = _load_artifacts_module()
    intake = _load_intake_module()
    intake.run_intake(project_ucid=project_ucid)

    base_url = mc._find_maestro_url()
    date = datetime.now().date().isoformat()
    day = mc._http_get(base_url, f"chronicle-days/{date}/agent")

    while True:
        todo = _first_open_ticket_todo(day, project_ucid)
        if todo is None:
            return "Keine offenen Ticket-Todos."

        match = _TICKET_TODO.match(todo["name"])
        cur_project_ucid, ticket_number = match["project"], match["ticket"]
        project, ops = _ticket_todo_ops(cur_project_ucid, ticket_number, base_url)
        ticket = ops.read_ticket(project, ticket_number)
        status = ticket["status"]

        if status not in _TERMINAL_NO_AGENT_STATUSES:
            break

        _todo_completion._close_todo(base_url, todo["uuid"])
        todo["status"] = "DONE"

    project_ucid = cur_project_ucid

    if status == _NO_STATUS_LABEL:
        ops.write_comment(project, ticket_number, "Kein Label - Auftrag unklar.")
        ops.write_assignee(project, ticket_number, _todo_completion._user_external_id(project, ops))
        _todo_completion._close_todo(base_url, todo["uuid"])
        return f"{project_ucid}#{ticket_number}: kein Statuslabel — Nutzer zugewiesen, Todo abgeschlossen."

    plan_comment = _todo_completion.find_active_plan(
        artifacts.list_implementation_plans, artifacts.view_implementation_plan,
        project["ticket_system"], project["uuid"], ticket_number,
    )
    plan_author_id = plan_comment["author_id"] if plan_comment else None
    walkthrough_comment = _todo_completion.find_active_walkthrough(
        artifacts.list_walkthroughs, artifacts.view_walkthrough,
        project["ticket_system"], project["uuid"], ticket_number,
        plan_comment["ref"] if plan_comment else None,
    )
    commit_refs = _commit_refs(ticket)
    triggering = _comments_since_assignment(ticket)
    current_assignee = ticket["assignees"][0] if ticket["assignees"] else None

    if status in ("doing", "review"):
        onboarding = _load_onboarding_module()
        branching_mode = onboarding.resolve_git_branching_mode(_load_config(), project)
        if branching_mode == "ticket-branches":
            _prepare_ticket_branch(project, ticket["type"], ticket_number, ticket["title"])

    if status == "draft":
        work = "Ticket vollständig ausarbeiten."
        complete_cmd = f'workroutine_complete(file="<ticket.md>")'
    elif status == "proposed":
        work = "Ticket prüfen."
        complete_cmd = (
            'workroutine_complete(result="passed") '
            'oder workroutine_complete(result="failed", file="<beanstandungen.md>")'
        )
    elif status == "revise":
        work = f"Im Ticket vermerkte Beanstandungen bearbeiten: {_format_comments(triggering)}"
        complete_cmd = 'workroutine_complete(file="<ticket.md>")'
    elif status == "approved" and not plan_comment:
        work = "Implementierungsplan erstellen."
        complete_cmd = (
            f'create_implementation_plan(project="{project["uuid"]}", ticket="{ticket_number}", '
            f'todo="{todo["uuid"]}", ...) — liefert ab und schließt Zuweisung/Todo im selben Aufruf ab.'
        )
    elif status == "approved" and plan_author_id == (current_assignee["id"] if current_assignee else None):
        work = f"Plan ({plan_comment['ref']}) anhand der im Ticket vermerkten Beanstandungen überarbeiten: {_format_comments(triggering)}"
        complete_cmd = (
            f'create_implementation_plan(project="{project["uuid"]}", ticket="{ticket_number}", '
            f'todo="{todo["uuid"]}", ...) — liefert ab und schließt Zuweisung/Todo im selben Aufruf ab.'
        )
    elif status == "approved":
        work = f"Plan ({plan_comment['ref']}) prüfen."
        complete_cmd = (
            'workroutine_complete(result="passed") '
            'oder workroutine_complete(result="failed", file="<beanstandungen.md>")'
        )
    elif status == "doing":
        if not plan_comment:
            raise RuntimeError(
                f"{project_ucid}#{ticket_number}: Status 'doing' ohne auffindbaren aktiven Plan "
                f"(kein Implementierungsplan mit Status ungleich DISCARDED/COMPLETED gefunden)."
            )
        artifacts.update_implementation_plan(project["uuid"], ticket_number, plan_comment["ref"], status="APPROVED")
        work = f"Freigegebenen Plan ({plan_comment['ref']}) umsetzen bzw. im Ticket vermerkte Beanstandungen nachbessern: {_format_comments(triggering)}"
        complete_cmd = (
            f'create_walkthrough(project="{project["uuid"]}", ticket="{ticket_number}", '
            f'todo="{todo["uuid"]}", implementation_plan="{plan_comment["ref"]}", ...) — '
            f'liefert ab und schließt Zuweisung/Status/Todo im selben Aufruf ab.'
        )
    elif status == "review":
        work = "Übergebene Implementierung anhand von Ticket, freigegebenem Plan, Walkthrough, Commitreferenzen und Kommentaren prüfen."
        complete_cmd = (
            'workroutine_complete(result="passed") '
            'oder workroutine_complete(result="failed", file="<beanstandungen.md>")'
        )
    else:
        return f"{project_ucid}#{ticket_number}: Status {status!r} erfordert keinen Agentenschritt."

    complete_cmd = _with_project(complete_cmd, project_ucid)

    parts = [
        f"── {project_ucid}#{ticket_number}: {ticket['title']} ──",
        ticket["web_url"],
        "",
        "Beschreibung:",
        ticket["description"],
        "",
        "Kommentarverlauf:",
    ]
    for c in ticket["comments"]:
        parts.append(f"--- {c['created_at']} von {c['author_name']} ---")
        parts.append(c["body"])
    parts.append("")
    if plan_comment:
        parts.append(f"Aktiver Plan: {plan_comment['ref']}")
    if walkthrough_comment:
        parts.append(f"Walkthrough: {walkthrough_comment['ref']}")
    if commit_refs:
        parts.append(f"Commitreferenzen: {', '.join(commit_refs)}")
    docs_entry_path = project.get("docs_entry_path")
    if docs_entry_path:
        parts.append(f"Projektwissen: {mc.project_directory(project) / docs_entry_path}")
    else:
        parts.append("Projektwissen: nicht hinterlegt")
    parts.append("")
    parts.append("Arbeitsauftrag:")
    parts.append(work)
    parts.append("")
    parts.append("Abschluss:")
    parts.append(complete_cmd)
    parts.append(_with_project(
        "Ist dieser Schritt technisch nicht ausführbar oder erfordert er eine fachliche "
        'Entscheidung, die nicht dem Agenten zusteht: workroutine_complete(blocked="<Begründung>")',
        project_ucid,
    ))
    return "\n".join(parts)


@mcp.tool()
def workroutine_complete(file: str | None = None, result: str | None = None, blocked: str | None = None, project_ucid: str | None = None) -> str:
    """Schließt einen ticketbezogenen Arbeitsschritt ohne Artefaktbezug ab (Ticketbeschreibung
    bei `draft`/`revise`, Beanstandungs-/Prüfergebnis-Übergabe bei `proposed`/`approved`/`review`).
    Für `approved` ohne aktiven Plan und für `doing` (Implementierungsplan bzw. Walkthrough)
    `create_implementation_plan`/`create_walkthrough` mit `todo`-Parameter verwenden — dort
    laufen Ablieferung, Zuweisung, Statusübergang und Todo-Abschluss im selben Aufruf.
    `blocked`: technischer Fehler oder eine dem Agenten nicht zustehende fachliche
    Entscheidung — schreibt Kommentar, Nutzer-Zuweisung und Todo-Abschluss in einem Aufruf.
    `project_ucid`: bindet die Todo-Auswahl an dasselbe Projekt wie der zugehörige
    `workroutine_next(project_ucid=...)`-Schritt — ohne Angabe projektübergreifend wie bisher."""
    base_url = mc._find_maestro_url()
    date = datetime.now().date().isoformat()
    day = mc._http_get(base_url, f"chronicle-days/{date}/agent")

    todo = _first_open_ticket_todo(day, project_ucid)
    if todo is None:
        raise RuntimeError("Kein offenes Ticket-Todo gefunden.")

    match = _TICKET_TODO.match(todo["name"])
    project_ucid, ticket_number = match["project"], match["ticket"]
    project, ops = _ticket_todo_ops(project_ucid, ticket_number, base_url)
    ticket = ops.read_ticket(project, ticket_number)
    status = ticket["status"]

    if blocked:
        target = _todo_completion._user_external_id(project, ops)
        ops.write_assignee(project, ticket_number, target)
        ops.write_comment(project, ticket_number, blocked)
        _todo_completion._close_todo(base_url, todo["uuid"])
        return f"{project_ucid}#{ticket_number}: blockiert — Nutzer zugewiesen, Todo abgeschlossen."

    def _file_text() -> str:
        if not file:
            raise RuntimeError("workroutine_complete für diesen Status erfordert file.")
        return Path(file).read_text(encoding="utf-8")

    if status in ("draft", "revise"):
        target = _todo_completion._review_handoff_target(project, ops, ticket, "TICKET")
        ops.write_assignee(project, ticket_number, target)
        ops.write_description(project, ticket_number, file)
        new_status = "proposed"
        ops.write_status(project, ticket_number, new_status)

    elif status == "proposed":
        if result == "passed":
            target = _todo_completion._user_external_id(project, ops)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, "Ticket geprüft: bestanden.")
            new_status = "proposed"
        else:
            target = _todo_completion._complaint_target(ticket)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, _file_text())
            new_status = "revise"
            ops.write_status(project, ticket_number, new_status)

    elif status == "approved":
        if result == "passed":
            target = _todo_completion._user_external_id(project, ops)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, "Plan geprüft: bestanden.")
            new_status = "approved"
        elif result == "failed":
            target = _todo_completion._complaint_target(ticket)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, _file_text())
            new_status = "approved"
        else:
            raise RuntimeError(
                f"{project_ucid}#{ticket_number}: Plan-Ablieferung erfolgt über "
                f'create_implementation_plan(project="{project["uuid"]}", ticket="{ticket_number}", '
                f'todo="{todo["uuid"]}", ...), nicht über workroutine_complete.'
            )

    elif status == "doing":
        raise RuntimeError(
            f"{project_ucid}#{ticket_number}: Walkthrough-Ablieferung erfolgt über "
            f'create_walkthrough(project="{project["uuid"]}", ticket="{ticket_number}", '
            f'todo="{todo["uuid"]}", ...), nicht über workroutine_complete.'
        )

    elif status == "review":
        if result == "passed":
            if project["ticket_system"] == "gitlab":
                branch = _canonical_ticket_branch(ticket["type"], ticket_number, ticket["title"])
                ops.verify_remote_branch(project, branch)
                mr = ops.ensure_merge_request(project, branch, f"#{ticket_number} {ticket['title']}")
                comment = f"Review bestanden. Merge Request: !{mr['iid']} {mr['web_url']}"
            else:
                comment = "Review bestanden."
            target = _todo_completion._user_external_id(project, ops)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, comment)
            new_status = "testing"
            ops.write_status(project, ticket_number, new_status)
        else:
            target = _todo_completion._complaint_target(ticket)
            ops.write_assignee(project, ticket_number, target)
            ops.write_comment(project, ticket_number, _file_text())
            new_status = "doing"
            ops.write_status(project, ticket_number, new_status)

    else:
        raise RuntimeError(f"workroutine_complete() nicht anwendbar auf Status {status!r}.")

    _todo_completion._close_todo(base_url, todo["uuid"])
    return f"{project_ucid}#{ticket_number}: {status} → {new_status}, Todo abgeschlossen."


if __name__ == "__main__":
    mcp.run(transport="stdio")
