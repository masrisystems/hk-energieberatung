#!/usr/bin/env python3
"""todo_completion — gemeinsame Zielpersonen- und Todo-Abschlusslogik für
ticketbezogene Work-Routine-Schritte.

Wird sowohl vom Artefakt-MCP (`echo-artifacts/tools/artifacts_mcp_server.py`, optionaler
`todo`-Parameter an `create_implementation_plan`/`create_walkthrough`) als auch vom
Work-Routine-MCP-Server (`echo-workroutine/tools/workroutine_mcp_server.py`) importiert.
Kein MCP-Server hängt vom anderen ab — beide hängen ausschließlich von diesem Modul ab.
"""

import json
import random
import re
import sys
from pathlib import Path

_MAESTRO_TOOLS_DIR = Path(__file__).resolve().parents[2] / 'echo-maestro' / 'tools'
if str(_MAESTRO_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_MAESTRO_TOOLS_DIR))

import maestro_client as mc  # noqa: E402

_TICKET_TODO = re.compile(r"^(?P<project>[a-zA-Z0-9._-]+)#(?P<ticket>[^:]+):")


def resolve_todo(base_url: str, todo_uuid: str) -> dict:
    return mc._http_get(base_url, f"todos/{todo_uuid}/agent")


def _meta_fields(body: str) -> dict[str, str]:
    match = re.search(r"(?ms)^##\s*Meta\s*\n(.*?)(?=\n##\s|\Z)", body)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field_match = re.match(r"^-\s*([^:]+?):\s*(.+?)\s*$", line)
        if field_match:
            fields[field_match[1]] = field_match[2]
    return fields


def _frontmatter_fields(body: str) -> dict[str, str]:
    match = re.match(r"(?s)^---\s*\n(.*?)\n---\s*\n?", body)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.+?)\s*$", line)
        if field_match:
            value = field_match[2]
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            fields[field_match[1]] = value
    return fields


def _artifact_fields(body: str) -> dict[str, str]:
    frontmatter = _frontmatter_fields(body)
    normalized: dict[str, str] = {}
    if "ticket" in frontmatter:
        normalized["ticket"] = frontmatter["ticket"]
    if "plan_date" in frontmatter:
        normalized["plan_date"] = frontmatter["plan_date"]
    if "walkthrough_date" in frontmatter:
        normalized["walkthrough_date"] = frontmatter["walkthrough_date"]
    if "status" in frontmatter:
        normalized["status"] = frontmatter["status"]
    if "implementation_plan" in frontmatter:
        normalized["implementation_plan"] = frontmatter["implementation_plan"]
    if normalized:
        return normalized

    meta = _meta_fields(body)
    if "Ticket" in meta:
        normalized["ticket"] = meta["Ticket"]
    if "Plan-Datum" in meta:
        normalized["plan_date"] = meta["Plan-Datum"]
    if "Walkthrough-Datum" in meta:
        normalized["walkthrough_date"] = meta["Walkthrough-Datum"]
    if "Status" in meta:
        normalized["status"] = meta["Status"]
    return normalized


_TERMINAL_PLAN_STATUS = {"DISCARDED", "COMPLETED"}


def find_active_plan(list_plans_fn, view_plan_fn, ticket_system: str, project_uuid: str, ticket_number) -> dict | None:
    """Aktiver Plan eines Tickets: der eine Plan, dessen Status weder DISCARDED noch
    COMPLETED ist. `validate_todo_for_artifact()` erzwingt strukturell, dass es davon
    höchstens einen gibt — kein weiterer Auswahlmechanismus nötig."""
    candidates = json.loads(list_plans_fn(project_uuid, ticket_number))
    if ticket_system == "maestro":
        for c in candidates:
            if c.get("status") not in _TERMINAL_PLAN_STATUS:
                return {"ref": c["uuid"], "status": c.get("status"), "author_id": c.get("author_uuid")}
        return None
    id_field = "file" if ticket_system == "internal" else "note_id"
    for c in candidates:
        text = view_plan_fn(project_uuid, ticket_number, c[id_field])
        fields = _artifact_fields(text)
        if fields.get("status") not in _TERMINAL_PLAN_STATUS:
            return {"ref": c[id_field], "status": fields.get("status"), "author_id": None}
    return None


def find_active_walkthrough(
    list_walkthroughs_fn, view_walkthrough_fn, ticket_system: str, project_uuid: str,
    ticket_number, active_plan_ref,
) -> dict | None:
    """Aktiver Walkthrough: der zeitlich letzte Walkthrough, dessen implementation_plan-Bezug
    auf active_plan_ref verweist. Ohne aktiven Plan gibt es keinen aktiven Walkthrough."""
    if active_plan_ref is None:
        return None
    candidates = json.loads(list_walkthroughs_fn(project_uuid, ticket_number))
    if ticket_system == "maestro":
        matching = [c for c in candidates if c.get("implementation_plan_uuid") == active_plan_ref]
        if not matching:
            return None
        latest = max(matching, key=lambda c: c["walkthrough_date"])
        return {"ref": latest["uuid"], "author_id": latest.get("author_uuid")}
    id_field = "file" if ticket_system == "internal" else "note_id"
    best = None
    for c in candidates:
        text = view_walkthrough_fn(project_uuid, ticket_number, c[id_field])
        fields = _artifact_fields(text)
        if fields.get("implementation_plan") != active_plan_ref:
            continue
        if best is None or fields.get("walkthrough_date", "") >= best["walkthrough_date"]:
            best = {"ref": c[id_field], "author_id": None, "walkthrough_date": fields.get("walkthrough_date", "")}
    return best


def _user_external_id(project: dict, ops) -> str:
    for ra in project.get("role_assignments", []):
        if ra.get("role") == "Nutzer":
            return ops.person_external_id(project, ra["person_uuid"])
    raise RuntimeError(f'Keine Rollenzuordnung "Nutzer" in Projekt {project["uuid"]} hinterlegt.')


def _review_handoff_target(project: dict, ops, ticket: dict, artefact_type: str) -> str:
    reviewer_role = next(
        (ra["reviewer_role"] for ra in project.get("review_assignments", []) if ra["artefact_type"] == artefact_type),
        None,
    )
    if not reviewer_role:
        return _user_external_id(project, ops)

    candidates = [ra["person_uuid"] for ra in project.get("role_assignments", []) if ra["role"] == reviewer_role]
    author_external_id = str(ticket["assignees"][0]["id"]) if ticket["assignees"] else None

    remaining = [p for p in candidates if str(ops.person_external_id(project, p)) != author_external_id]
    if not remaining:
        return _user_external_id(project, ops)
    return ops.person_external_id(project, random.choice(remaining))


def _complaint_target(ticket: dict) -> str:
    assigned_by = ticket["assigned_by"]
    if assigned_by is None:
        raise RuntimeError("Keine zuweisende Person für die aktuelle Zuweisung gefunden.")
    return assigned_by


def _close_todo(base_url: str, todo_uuid: str) -> None:
    mc._post_raw(base_url, f"todos/{todo_uuid}", mc._form_fields({"status": "DONE"}))


def validate_todo_for_artifact(
    todo_record: dict, project_ucid: str, ticket_number, artifact_type: str, ticket: dict,
    active_plan: dict | None,
) -> None:
    """Prüft, ob `todo_record` zu `project_ucid`/`ticket_number` gehört und der aktuelle
    Ticketstatus `artifact_type` erwartet. Wirft `RuntimeError` mit der konkreten
    Abweichung, liefert sonst `None`."""
    if todo_record.get("status"):
        raise RuntimeError(f'Todo {todo_record["uuid"]} ist bereits abgeschlossen.')

    match = _TICKET_TODO.match(todo_record.get("name", ""))
    if not match:
        raise RuntimeError(f'Todo {todo_record["uuid"]} trägt keinen Ticket-Präfix ("{todo_record.get("name")}").')
    if match["project"] != project_ucid or match["ticket"] != str(ticket_number):
        raise RuntimeError(
            f'Todo {todo_record["uuid"]} gehört zu {match["project"]}#{match["ticket"]}, '
            f'nicht zu {project_ucid}#{ticket_number}.'
        )

    status = ticket["status"]
    if artifact_type == "implementation-plan":
        if status != "approved":
            raise RuntimeError(f'Ticketstatus {status!r} erwartet keinen Implementierungsplan.')
        if active_plan is not None:
            raise RuntimeError(f'Ticket #{ticket_number} hat bereits einen aktiven Plan.')
    elif artifact_type == "walkthrough":
        if status != "doing":
            raise RuntimeError(f'Ticketstatus {status!r} erwartet keinen Walkthrough.')
    else:
        raise RuntimeError(f'Unbekannter Artefakttyp {artifact_type!r} für Todo-Abschluss.')


def complete_ticket_todo(
    base_url: str, ops, project: dict, ticket_number, ticket: dict, todo_record: dict, artifact_type: str
) -> None:
    """Nach erfolgter Artefakt-Ablieferung aufrufen: Zuweisung, ggf. Statusübergang und
    Todo-Abschluss."""
    if artifact_type == "implementation-plan":
        target = _review_handoff_target(project, ops, ticket, "PLAN")
        ops.write_assignee(project, ticket_number, target)
    elif artifact_type == "walkthrough":
        target = _review_handoff_target(project, ops, ticket, "IMPLEMENTATION")
        ops.write_assignee(project, ticket_number, target)
        ops.write_status(project, ticket_number, "review")
    else:
        raise RuntimeError(f'Unbekannter Artefakttyp {artifact_type!r} für Todo-Abschluss.')

    _close_todo(base_url, todo_record["uuid"])
