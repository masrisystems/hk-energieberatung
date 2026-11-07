#!/usr/bin/env python3
"""
setup_workflow_chore.py — legt einen Maestro-Workflow samt Workflow-Steps, Chore und
ChoreDateRange für den ausführenden Agenten an.

Verwendung:
  python3 setup_workflow_chore.py <spec.json>

Die Spec-Datei ist projektspezifisch (z.B. im jeweiligen Workflow-Repo abgelegt, nicht im
Echo-Framework) und enthält keine agentenspezifischen Absolutpfade — Workflow-`instructions`
referenzieren nur den relativen Konventionspfad `.openclaw/workspace/<projekt>/...`.

Läuft mit den Maestro-Zugangsdaten des ausführenden Agenten (`.agent/config.json` bzw.
`.agents/config.json`) — Chore und ChoreDateRange werden dadurch server-seitig automatisch
dem ausführenden Agenten zugeordnet (`get_effective_person_uuid()`/`get_effective_owner_uuid()`
in Maestro), nicht manuell mitgegeben.

Chore/Task und Workflow sind über `record_relations` verknüpft (many_to_many, keine FK-Spalte
auf chores/tasks — ein Kern-Archetype darf nicht hart an das optionale workflows-Paket
gebunden sein). Die Verknüpfung entsteht daher über einen separaten Attach-Aufruf
(`POST /chores/{uuid}/relations/workflow/attach`), nicht als Feld im Create-Formular.

Spec-Format:
{
  "workflow": {"name": str, "description": str, "instructions": str, "schedule": <json-wert>},
  "steps": [{"step_key": str, "name": str, "description": str, "sort_order": int}, ...],
  "chore": {"name": str},
  "chore_date_range": {"start_date": "YYYY-MM-DD" | "today", "end_date": "YYYY-MM-DD" | null}
}
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


def _find_agent_dir(start: Path) -> Path:
    for p in (start, *start.parents):
        if p.name in (".agent", ".agents"):
            return p
    raise RuntimeError(
        f"Kein .agent-/.agents-Verzeichnis in den Elternpfaden von {start} gefunden."
    )


def _load_maestro_config(agent_dir: Path) -> dict:
    cfg_path = agent_dir / "config.json"
    if not cfg_path.exists():
        raise RuntimeError(f"{cfg_path} nicht gefunden.")
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    maestro = data.get("maestro") or {}
    base_url = maestro.get("base_url")
    if not base_url:
        raise RuntimeError(f"maestro.base_url fehlt in {cfg_path}.")
    return maestro


def _obtain_token(base_url: str, agent_uuid: str, password: str) -> str:
    url = f"{base_url}/api/auth/token"
    payload = json.dumps({"agent_uuid": agent_uuid, "password": password}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())["token"]


def _resolve_token(maestro_cfg: dict, base_url: str) -> str:
    if maestro_cfg.get("token"):
        return maestro_cfg["token"]
    agent_uuid = maestro_cfg.get("agent_uuid")
    password = maestro_cfg.get("password")
    if not agent_uuid or not password:
        raise RuntimeError(
            "Weder maestro.token noch maestro.agent_uuid/password in config.json gesetzt."
        )
    return _obtain_token(base_url, agent_uuid, password)


class _NoRedirect(urllib.request.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response

    https_response = http_response


def _post_form(base_url: str, token: str, archetype: str, fields: dict[str, Any]) -> str:
    """POST /{archetype}, gibt die neu angelegte UUID zurück (aus dem Redirect-Location-Header)."""
    url = f"{base_url}/{archetype}"
    form: dict[str, str] = {}
    for key, value in fields.items():
        if value is None:
            continue
        form[key] = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    data = urllib.parse.urlencode(form).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Bearer {token}")

    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(req, timeout=10) as resp:
            location = resp.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        raise RuntimeError(f"POST {url} -> {e.code} {e.reason}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"POST {url} -> {e.reason}")

    try:
        segment = location.split(f"/{archetype}/")[1].split("/")[0].split("?")[0]
    except IndexError:
        segment = ""
    if not segment or segment in ("create", "json"):
        raise RuntimeError(
            f"Anlage von '{archetype}' fehlgeschlagen (Redirect: {location or 'keiner'})."
        )
    return segment


def _post_attach(base_url: str, token: str, archetype: str, identifier: str, relation_name: str, target_uuid: str) -> None:
    """POST /{archetype}/{identifier}/relations/{relation_name}/attach — many_to_many-Verknuepfung
    (record_relations). Fuer many_to_many-Relationen wie `workflow` auf chores/tasks nicht ueber
    das generische Create-Formular setzbar (build_resource_data kennt nur belongs_to-FK-Aliasing)."""
    url = f"{base_url}/{archetype}/{identifier}/relations/{relation_name}/attach"
    data = urllib.parse.urlencode({"target_uuid": target_uuid}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", f"Bearer {token}")
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(req, timeout=10):
            pass
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        raise RuntimeError(f"POST {url} -> {e.code} {e.reason}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"POST {url} -> {e.reason}")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Verwendung: {sys.argv[0]} <spec.json>", file=sys.stderr)
        return 2

    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    agent_dir = _find_agent_dir(Path(__file__).resolve())
    maestro_cfg = _load_maestro_config(agent_dir)
    base_url = maestro_cfg["base_url"]
    token = _resolve_token(maestro_cfg, base_url)

    workflow_fields = dict(spec["workflow"])
    workflow_uuid = _post_form(base_url, token, "workflows", workflow_fields)
    print(f"workflow angelegt: {workflow_uuid}")

    for step in spec["steps"]:
        step_fields = dict(step)
        step_fields["workflow"] = workflow_uuid
        step_uuid = _post_form(base_url, token, "workflow-steps", step_fields)
        print(f"workflow-step angelegt: {step_uuid} ({step.get('step_key')})")

    chore_fields = dict(spec["chore"])
    chore_uuid = _post_form(base_url, token, "chores", chore_fields)
    print(f"chore angelegt: {chore_uuid}")

    _post_attach(base_url, token, "chores", chore_uuid, "workflow", workflow_uuid)
    print(f"chore <-> workflow verknuepft (record_relations)")

    date_range = dict(spec["chore_date_range"])
    if date_range.get("start_date") == "today":
        date_range["start_date"] = date.today().isoformat()
    date_range["chore"] = chore_uuid
    date_range_uuid = _post_form(base_url, token, "chore-date-ranges", date_range)
    print(f"chore-date-range angelegt: {date_range_uuid}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
