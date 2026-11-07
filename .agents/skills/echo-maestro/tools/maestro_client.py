#!/usr/bin/env python3
"""maestro_client — Transport-/Auth-Layer für die Maestro-API.

Reines `urllib`/`json`, keine Fremdabhängigkeit — im Unterschied zu
`maestro_mcp_server.py` (das dieses Modul importiert) ohne `fastmcp`-Voraussetzung.
Damit auch von Scripts ohne MCP-Laufzeit nutzbar (z.B. `onboarding.py`, per
`importlib.util.spec_from_file_location` geladen — Muster aus
`scripts/sync_session_logs.py::load_filter_module`).

Token-Cache: `.maestro/auth-token.json` im Agent-Verzeichnis — von MCP-Server und
jedem ladenden Script gemeinsam genutzt, kein Konflikt bei paralleler Nutzung.
"""

import json
import re
import urllib.request
import urllib.parse
from pathlib import Path

# Agent-Verzeichnis: im Antigravity-Setup wird der Literal '.agent' vom Finalize-sed auf '.agents'
# umgeschrieben (#065) — derselbe Code funktioniert in beiden Layouts.
_AGENT_DIR = Path(__file__).parents[4] / '.agent'

_CACHE_DIR = _AGENT_DIR / '.maestro'


def _cache_path(name: str) -> Path:
    return _CACHE_DIR / f'{name}.json'


def _load_agent_auth() -> tuple:
    cfg = _AGENT_DIR / 'config.json'
    if cfg.exists():
        data = json.loads(cfg.read_text())
        m = data.get('maestro', {})
        return m.get('agent_uuid'), m.get('password'), m.get('token')
    return None, None, None


def current_agent_person_uuid(base_url: str) -> str:
    agent_uuid, _, _ = _load_agent_auth()
    if not agent_uuid:
        raise RuntimeError('maestro.agent_uuid nicht in .agent/config.json gefunden.')
    record = _http_get(base_url, f'agents/{agent_uuid}/agent')
    person_uuid = record.get('person_uuid')
    if not person_uuid:
        raise RuntimeError(f'Agent {agent_uuid} trägt kein person_uuid.')
    return person_uuid


def _obtain_token(base_url: str, agent_uuid: str, password: str) -> str:
    url = f"{base_url}/api/auth/token"
    payload = json.dumps({'agent_uuid': agent_uuid, 'password': password}).encode()
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['token']


def _bearer_token(base_url: str) -> str | None:
    agent_uuid, password, login_token = _load_agent_auth()
    if login_token:
        # Maestro #228: vorab erzeugtes Login-Token ist bereits ein gültiger,
        # nicht ablaufender Bearer — kein Tausch, kein Cache nötig.
        return login_token
    if not agent_uuid or not password:
        return None
    tok_path = _cache_path('auth-token')
    if tok_path.exists():
        try:
            cached = json.loads(tok_path.read_text(encoding='utf-8'))
            token = cached.get('token')
            if token:
                return token
        except (json.JSONDecodeError, OSError):
            pass
    return _refresh_token(base_url, agent_uuid, password)


def _refresh_token(base_url: str, agent_uuid: str, password: str) -> str:
    """Holt einen neuen Session-Token und ersetzt den Cache. Gültigkeit wird nicht lokal
    vorberechnet — ein 401 auf eine authentifizierte Anfrage ist der einzige Anlass
    für einen erneuten Aufruf dieser Funktion. Gilt nur für den Passwort-Login-Pfad;
    ein konfiguriertes Login-Token wird nie getauscht (siehe `_bearer_token`)."""
    token = _obtain_token(base_url, agent_uuid, password)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path('auth-token').write_text(json.dumps({'token': token}), encoding='utf-8')
    return token


def _auth_headers(base_url: str) -> dict:
    agent_uuid, password, login_token = _load_agent_auth()
    token = login_token or _bearer_token(base_url)
    return {'Authorization': f'Bearer {token}'} if token else {}


def _invalidate_token_cache() -> None:
    tok_path = _cache_path('auth-token')
    if tok_path.exists():
        tok_path.unlink()


def _coerce_form_value(value) -> str:
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def _form_fields(fields: dict) -> dict[str, str]:
    return {k: _coerce_form_value(v) for k, v in fields.items()}


def _find_maestro_url() -> str:
    cfg = _AGENT_DIR / 'config.json'
    if cfg.exists():
        data = json.loads(cfg.read_text())
        url = data.get('maestro', {}).get('base_url')
        if url:
            return url.rstrip('/')
    raise RuntimeError('maestro.base_url nicht in .agent/config.json gefunden')


def project_directory(record: dict) -> Path:
    """Lokales Projektverzeichnis: Projekte-Root des Agenten und `local_path` des Records.

    Fokussiertes Projekt: das Verzeichnis, in dem der `.agent`-Ordner liegt.
    """
    maestro_config = json.loads((_AGENT_DIR / 'config.json').read_text()).get('maestro', {})
    if maestro_config.get('focus_project_uuid'):
        return _AGENT_DIR.parent
    return Path(maestro_config['project_root']) / record['local_path']


def _http_get(base_url: str, path: str) -> object:
    url = f"{base_url}/{path.lstrip('/')}"
    req = urllib.request.Request(
        url, headers={'Accept': 'application/json', **_auth_headers(base_url)}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _http_post_json(base_url: str, path: str, fields: dict | None = None) -> object:
    url = f"{base_url}/{path.lstrip('/')}"
    data = urllib.parse.urlencode(fields or {}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    for k, v in _auth_headers(base_url).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _post_raw(base_url: str, path: str, fields: dict) -> str:
    """Sendet POST, folgt einem Erfolgs-Redirect (Maestro beantwortet einen erfolgreichen
    Store damit) automatisch und gibt den Seiteninhalt der dabei tatsächlich erreichten
    Response zurück. Ein echter Fehlercode (4xx/5xx) läuft ungehandelt durch urllibs
    Standardmechanismus als Exception durch — keine eigene Fehlerklassifizierung."""
    url = f"{base_url}/{path.lstrip('/')}"
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    for k, v in _auth_headers(base_url).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()


_UUID_ROW = re.compile(
    r'<td[^>]*>UUID</td>\s*<td[^>]*>\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\s*</td>'
)


def _identifier_from_content(content: str, archetype: str) -> str:
    """Identifier aus dem Seiteninhalt der nach dem Store-Redirect erreichten Show-Seite
    (Systemfelder-Sektion, Label „UUID" — identisch für jeden Archetype). Leitet Maestro
    stattdessen zur Create-Seite um (ungültige Felddaten), fehlt dort die Systemfelder-Zeile
    eines existierenden Datensatzes — dann lauter Fehler statt Fehlinterpretation."""
    match = _UUID_ROW.search(content)
    if not match:
        raise RuntimeError(f'Store auf "{archetype}" wurde nicht ausgeführt (keine UUID im Ergebnis gefunden).')
    return match.group(1)


_SEGMENT_FORBIDDEN = set('/?#&= \t\n')


def _segment(value: str, label: str) -> str:
    """Validiert einen einzelnen Routenbestandteil (Archetype oder Identifier)."""
    value = str(value).strip()
    if not value or any(c in _SEGMENT_FORBIDDEN for c in value):
        raise RuntimeError(f'Ungültiger {label}: {value!r} — einzelner Name ohne Pfadzeichen erwartet.')
    return value


def _record_markdown(rec: object) -> str:
    """Flaches Agent-JSON eines Einzelsatzes als Markdown."""
    if not isinstance(rec, dict):
        return str(rec)
    archetype = rec.get('archetype', 'record')
    title = rec.get('name') or rec.get('title') or rec.get('uuid', '')
    lines = [f'## {archetype}: {title}', '']
    for key, value in rec.items():
        if key == 'archetype':
            continue
        if isinstance(value, dict):
            name, uuid = value.get('name'), value.get('uuid')
            if name or uuid:
                lines.append(f'- {key}: {name} (`{uuid}`)')
            else:
                lines.append(f'- {key}: {json.dumps(value, ensure_ascii=False)}')
        elif isinstance(value, list):
            lines.append(f'- {key}:')
            for item in value:
                if isinstance(item, dict):
                    nm = item.get('name') or item.get('title') or item.get('uuid')
                    line = f'  - {nm} (`{item.get("uuid")}`)'
                    if item.get('status'):
                        line += f' — status: {item["status"]}'
                    lines.append(line)
                else:
                    lines.append(f'  - {item}')
        else:
            lines.append(f'- {key}: {value}')
    return '\n'.join(lines)


def _fetch_record_markdown(base_url: str, archetype: str, identifier: str) -> str:
    record = _http_get(base_url, f'{archetype}/{identifier}/agent')
    if archetype == 'projects' and isinstance(record, dict):
        record['project_directory'] = str(project_directory(record))
    return _record_markdown(record)
