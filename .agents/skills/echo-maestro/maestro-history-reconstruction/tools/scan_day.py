#!/usr/bin/env python3
"""
scan_day.py — Scannt Chat-Log-Dateien nach Aktivität an einem bestimmten Datum
und gibt eine aufbereitete Zusammenfassung aus, die direkt als Grundlage für
Maestro-Tagesberichte verwendet werden kann.

Unterstützte Formate:
  - OpenClaw JSONL (type=session/message/...)
  - Claude Code JSONL (parentUuid/isSidechain/...)

Usage:
  python3 tools/scan_day.py YYYY-MM-DD --logs-path /pfad/zu/logs
  python3 tools/scan_day.py 2026-05-21 --logs-path ~/openclaw/convos
  python3 tools/scan_day.py 2026-05-21 --logs-path ~/convos --verbose
  python3 tools/scan_day.py 2026-05-21 --logs-path ~/convos --summary
  python3 tools/scan_day.py 2026-05-21 --logs-path ~/convos --generate

Wenn --logs-path nicht angegeben: Fallback auf ../sources/convos relativ zum Script.

Filter:
  - OpenClaw-Sessions, die ausschließlich vor 06:00 Lokalzeit aktiv sind, werden
    als Hintergrundprozesse gewertet und übersprungen
  - Nachrichten, die mit bekannten System-Prefixen beginnen, werden herausgefiltert
"""

import json
import os
import sys
import glob
import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo

# ── Konfiguration ─────────────────────────────────────────────────────────────

_DEFAULT_CONVOS_ROOT = os.path.join(os.path.dirname(__file__), "..", "sources", "convos")

# Zeitzone Berlin (UTC+1/UTC+2)
TZ_BERLIN = ZoneInfo("Europe/Berlin")


# ── Format-Erkennung ──────────────────────────────────────────────────────────

def detect_format(first_line: dict) -> str:
    """Erkennt das Format des JSONL-Logs anhand der ersten Zeile."""
    if first_line.get("type") == "session":
        return "openclaw"
    if "parentUuid" in first_line or "isSidechain" in first_line:
        return "claudecode"
    if first_line.get("type") in ("permission-mode", "ai-title"):
        return "claudecode"
    return "unknown"


# ── OpenClaw Parser ───────────────────────────────────────────────────────────

def parse_openclaw(lines: list[str], target_date: str) -> list[dict]:
    """
    Parst OpenClaw JSONL und gibt alle Nachrichten des Zieldatums zurück.
    Format: {timestamp, role, text, clean_text, session_id, source}
    """
    events = []
    session_id = None

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue

        t = obj.get("type", "")

        # Session-ID merken
        if t == "session":
            session_id = obj.get("id")

        # Nachrichten-Typ: type=message, enthält message.role + message.content
        if t == "message":
            ts_raw = obj.get("timestamp", "")
            if not ts_raw:
                continue
            dt = _parse_ts(ts_raw)
            if not dt or dt.strftime("%Y-%m-%d") != target_date:
                continue

            msg = obj.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role not in ("user", "assistant"):
                continue

            raw_text = _extract_text(content)
            if not raw_text:
                continue

            # Für User-Nachrichten: OpenClaw hängt Metadata-Header voran
            # Den echten Inhalt dahinter extrahieren
            clean_text = _strip_openclaw_metadata(raw_text) if role == "user" else raw_text
            if role == "user" and not clean_text:
                continue

            events.append({
                "timestamp": ts_raw,
                "role": role,
                "text": raw_text,
                "clean_text": clean_text,
                "session_id": session_id or obj.get("id", ""),
                "source": "openclaw",
            })

    return events


# ── Claude Code Parser ────────────────────────────────────────────────────────

def parse_claudecode(lines: list[str], target_date: str) -> list[dict]:
    """
    Parst Claude Code JSONL und gibt alle Nachrichten des Zieldatums zurück.
    """
    events = []
    session_id = None

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue

        t = obj.get("type", "")

        # Session-ID aus verschiedenen Quellen
        if not session_id:
            session_id = obj.get("sessionId", "")

        # Nachrichten
        if t in ("user", "assistant"):
            ts_raw = obj.get("timestamp", "")
            if not ts_raw:
                continue
            dt = _parse_ts(ts_raw)
            if not dt or dt.strftime("%Y-%m-%d") != target_date:
                continue

            msg = obj.get("message", {})
            role = msg.get("role", t)  # fallback auf type
            content = msg.get("content", "")

            text = _extract_text(content)
            if not text:
                continue

            events.append({
                "timestamp": ts_raw,
                "role": role,
                "text": text,
                "clean_text": text,  # Claude Code hat keine Metadata-Header
                "session_id": session_id or obj.get("uuid", ""),
                "source": "claudecode",
            })

    return events


# ── Text-Extraktion ───────────────────────────────────────────────────────────

def _extract_text(content) -> str:
    """Extrahiert lesbaren Text aus verschiedenen Content-Formaten."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    t = item.get("text", "").strip()
                    if t:
                        parts.append(t)
                elif item.get("type") == "tool_result":
                    # Tool-Results überspringen (kein eigener Inhalt)
                    pass
        return "\n".join(parts)

    return ""


def _strip_openclaw_metadata(text: str) -> str:
    """
    Entfernt den OpenClaw-Metadata-Header (Conversation info / Sender block)
    aus User-Nachrichten und gibt nur den echten Inhalt zurück.

    Typisches Format:
        Conversation info (untrusted metadata):
        ```json
        { ... }
        ```

        [Mon 2026-03-09 20:00 GMT+1] Eigentliche Nachricht hier.

    oder:
        Sender (untrusted metadata):
        ```json
        { ... }
        ```

        [Thu 2026-05-21 19:37 GMT+2] Eigentliche Nachricht hier.
    """
    import re

    # Metadata-Block entfernen: alles bis zum Ende des ```-Blocks
    # Dann den optionalen Zeitstempel-Prefix [Wochentag YYYY-MM-DD HH:MM GMT...] entfernen
    cleaned = text

    # Metadata-Block: von Anfang bis nach dem schließenden ``` entfernen
    if cleaned.startswith(("Conversation info", "Sender (")):
        end_of_block = cleaned.find("```\n\n")
        if end_of_block != -1:
            cleaned = cleaned[end_of_block + 5:].strip()
        else:
            # Fallback: alles nach dem ersten leeren Absatz nach dem ```
            end_of_block = cleaned.find("\n\n", cleaned.find("```"))
            if end_of_block != -1:
                cleaned = cleaned[end_of_block:].strip()

    # Zeitstempel-Prefix entfernen: "[Thu 2026-05-21 19:37 GMT+2] "
    cleaned = re.sub(r'^\[\w{2,4} \d{4}-\d{2}-\d{2} \d{2}:\d{2} GMT[+-]\d+\]\s*', '', cleaned)

    # System-interne Nachrichten erkennen (Cron-Reminder, Memory-Sync etc.)
    for prefix in _SYSTEM_PREFIXES:
        if cleaned.startswith(prefix):
            return ""  # Leer = wird als System-Nachricht behandelt

    return cleaned.strip()


# Bekannte System-Nachrichten-Prefixes (keine echten User-Inhalte)
_SYSTEM_PREFIXES = (
    "System:",
    "System (",
    "__openclaw_memory",
    "Reminder: This is your",
    "A new session was started via /new",
    "Sender (untrusted metadata)",
    "Conversation info (untrusted metadata)",
)


def _is_background_only(events: list[dict]) -> bool:
    """
    Gibt True zurück, wenn diese Session wahrscheinlich ein Hintergrundprozess ist
    (Dreaming, Memory-Sync etc.) und keine echte menschliche Interaktion enthält.

    Kriterien:
    - Alle Nachrichten vor 06:00 Lokalzeit UND erste User-Nachricht ist ein System-Event
    - ODER: Keine einzige User-Nachricht, die nicht mit bekanntem System-Prefix beginnt
    """
    user_events = [e for e in events if e.get("role") == "user"]
    if not user_events:
        return True

    # Prüfen ob alle User-Nachrichten echten Inhalt haben
    # Wichtig: Für OpenClaw clean_text verwenden (nach Metadata-Strip)
    real_user_count = 0
    for e in user_events:
        clean = e.get("clean_text", e.get("text", "")).strip()
        if clean:  # Leerer clean_text = System-Nachricht (von _strip_openclaw_metadata herausgefiltert)
            real_user_count += 1

    if real_user_count == 0:
        return True

    # Prüfen ob alle Nachrichten vor 06:00 Berliner Zeit sind
    all_before_6am = True
    for e in events:
        dt = _parse_ts(e.get("timestamp", ""))
        if dt:
            local = dt.astimezone(TZ_BERLIN)
            if local.hour >= 6:
                all_before_6am = False
                break

    if all_before_6am and real_user_count <= 2:
        return True

    return False


# ── Haupt-Scanner ─────────────────────────────────────────────────────────────

def scan_all_logs(target_date: str, logs_path: str | None = None) -> dict[str, list]:
    """
    Durchsucht alle JSONL-Dateien im angegebenen logs_path nach dem Zieldatum.
    Nutzt grep als schnellen Vorfilter, um nur Dateien vollständig zu lesen,
    die tatsächlich das Zieldatum enthalten.
    Gibt ein Dict {session_key: [events]} zurück.
    """
    import subprocess

    convos_root = logs_path if logs_path else _DEFAULT_CONVOS_ROOT

    sessions = defaultdict(list)

    roots_to_scan = [
        convos_root
    ]

    candidate_files = []
    for root_dir in roots_to_scan:
        if not os.path.exists(root_dir):
            continue
        try:
            result = subprocess.run(
                ["grep", "-rl", "--include=*.jsonl*", target_date, root_dir],
                capture_output=True, text=True, timeout=30
            )
            candidate_files.extend([p.strip() for p in result.stdout.splitlines() if p.strip()])
        except (subprocess.TimeoutExpired, FileNotFoundError):
            candidate_files.extend(glob.glob(os.path.join(root_dir, "**", "*.jsonl*"), recursive=True))

    checked = len(candidate_files)
    hits = 0

    # ── Schritt 2: Nur Treffer-Dateien vollständig parsen ────────────────────
    parsed_sessions = defaultdict(list)
    for jsonl_path in candidate_files:
        # Parser will automatically filter background dreaming logs by content
        try:
            with open(jsonl_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            continue

        if not lines:
            continue

        # Format erkennen
        try:
            first = json.loads(lines[0])
        except (json.JSONDecodeError, IndexError):
            continue

        fmt = detect_format(first)

        # Parsen
        if fmt == "openclaw":
            events = parse_openclaw(lines, target_date)
        elif fmt == "claudecode":
            events = parse_claudecode(lines, target_date)
        else:
            continue

        if not events:
            continue

        # ── Dreaming-Filter: Sessions die ausschließlich als Hintergrundprozesse laufen ──
        if _is_background_only(events):
            continue

        base_uuid = os.path.basename(jsonl_path).split('.')[0]
        rel_path = os.path.relpath(jsonl_path, os.path.dirname(convos_root))
        
        if base_uuid not in parsed_sessions or len(events) > len(parsed_sessions[base_uuid][1]):
            parsed_sessions[base_uuid] = (rel_path, events)

    for base_uuid, (rel_path, events) in parsed_sessions.items():
        hits += 1
        sessions[rel_path].extend(events)

    return dict(sessions), checked, hits


# ── Block-Analyse ─────────────────────────────────────────────────────────────

def analyze_session(session_key: str, events: list[dict]) -> list[dict]:
    """
    Analysiert eine Session, teilt sie bei Pausen von > 30 Minuten in mehrere Blöcke auf,
    und leitet für jeden Block einen prägnanten, professionellen Titel ab.
    Gibt eine Liste von Dicts mit Metadaten und Blöcken zurück.
    """
    if not events:
        return []

    events_sorted = sorted(events, key=lambda e: e["timestamp"])
    
    # ── Sessions nach Inaktivität (>30 Min) aufteilen ───────────────────
    blocks_events = []
    current_block = [events_sorted[0]]
    
    for e in events_sorted[1:]:
        prev_dt = _parse_ts(current_block[-1]["timestamp"])
        curr_dt = _parse_ts(e["timestamp"])
        
        if prev_dt and curr_dt:
            gap = (curr_dt - prev_dt).total_seconds() / 60.0
            if gap > 30.0:
                blocks_events.append(current_block)
                current_block = [e]
            else:
                current_block.append(e)
        else:
            current_block.append(e)
            
    if current_block:
        blocks_events.append(current_block)

    analyzed_blocks = []
    source = events_sorted[0].get("source", "unknown")
    subdir = session_key.split("/")[0] if "/" in session_key else session_key

    for idx, block in enumerate(blocks_events):
        first_ts = block[0]["timestamp"]
        last_ts = block[-1]["timestamp"]
        first_dt = _parse_ts(first_ts)
        last_dt = _parse_ts(last_ts)
        
        duration_min = 5
        if first_dt and last_dt:
            duration_min = int((last_dt - first_dt).total_seconds() / 60)
            if duration_min < 5:
                duration_min = 5

        # ── Themen-Heuristik mit verfeinertem Titel-Mapping ──────────────────
        title = ""
        for e in block:
            if e["role"] == "user":
                clean = e.get("clean_text", e.get("text", "")).strip()
                if not clean:
                    continue
                candidate_lines = [l.strip() for l in clean.splitlines() if l.strip()]
                for line in candidate_lines:
                    if line.startswith("{") or line.startswith("```") or line.startswith("["):
                        continue
                    if len(line) > 10:
                        title = line
                        break
                if title:
                    break

        title = _refine_title(title, block)

        analyzed_blocks.append({
            "session_key": f"{session_key}#block{idx}",
            "source": source,
            "subdir": subdir,
            "first_ts": first_ts,
            "last_ts": last_ts,
            "first_dt": first_dt,
            "last_dt": last_dt,
            "duration_min": duration_min,
            "event_count": len(block),
            "user_messages": sum(1 for e in block if e["role"] == "user"),
            "assistant_messages": sum(1 for e in block if e["role"] == "assistant"),
            "title_hint": title,
            "events": block,
        })

    return analyzed_blocks


def _refine_title(raw_title: str, events: list[dict]) -> str:
    """
    Raffiniert und bereinigt den rohen Titel zu einer prägnanten, professionellen Maestro-Aktivitätsbezeichnung.
    Entfernt Höflichkeitsfloskeln, Einleitungen und formuliert das Ganze als präzise Tätigkeit.
    """
    text = raw_title.strip()
    overhead_patterns = [
        "ich hatte dich gestern abend gebeten",
        "wirf einen blick auf die",
        "wirf einen blick auf",
        "prüfe bitte folgendes",
        "kannst du bitte",
        "kannst du",
        "bitte",
        "hinterlege",
        "lies nun",
        "lies",
        "trage nun",
        "versuche dich"
    ]
    
    text_lower = text.lower()
    for pattern in overhead_patterns:
        if text_lower.startswith(pattern):
            text = text[len(pattern):].strip()
            text = text.lstrip(":,;.- \t\n")
            text_lower = text.lower()

    if text.count('"') >= 2:
        first_quote = text.find('"')
        second_quote = text.find('"', first_quote + 1)
        if second_quote != -1:
            quoted = text[first_quote+1:second_quote].strip()
            if len(quoted) > 5:
                text = quoted

    text = text.strip('"\'.,;:- \t\n')

    if not text:
        return "Interaktion und Analyse"

    if len(text) > 60:
        truncated = text[:60]
        last_space = truncated.rfind(" ")
        if last_space != -1:
            clean_truncated = truncated[:last_space].strip('"\'.,;:- \t\n')
            return clean_truncated + "..."
        return truncated.strip('"\'.,;:- \t\n') + "..."
        
    return text



def _parse_ts(ts: str):
    """Parst ISO-Zeitstempel zu datetime-Objekt in Berliner Lokalzeit."""
    if not ts:
        return None
    try:
        ts_clean = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(TZ_BERLIN)
    except ValueError:
        try:
            dt = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            return dt.astimezone(TZ_BERLIN)
        except ValueError:
            return None


def _fmt_local(dt) -> str:
    """Formatiert UTC-datetime als Berliner Lokalzeit HH:MM."""
    if not dt:
        return "--:--"
    local = dt.astimezone(TZ_BERLIN)
    return local.strftime("%H:%M")


# ── Ausgabe ───────────────────────────────────────────────────────────────────

def print_report(target_date: str, sessions_data: list[dict], verbose: bool, summary_only: bool):
    """Gibt den aufbereiteten Tagesbericht aus."""

    print(f"\n{'='*70}")
    print(f"  Tages-Scan: {target_date}")
    print(f"{'='*70}\n")

    if not sessions_data:
        print("  ❌ Keine Chat-Aktivität gefunden.")
        return

    # Nach Startzeit sortieren
    sessions_sorted = sorted(
        sessions_data,
        key=lambda s: s.get("first_ts", ""),
    )

    # ── Übersicht ─────────────────────────────────────────────────────────────
    print(f"  Gefundene Sessions: {len(sessions_sorted)}\n")
    print(f"  {'Start':<6}  {'Ende':<6}  {'Dauer':>5}  {'Msg':>4}  {'Quelle':<15}  Thema")
    print(f"  {'-'*6}  {'-'*6}  {'-'*5}  {'-'*4}  {'-'*15}  {'-'*40}")

    for s in sessions_sorted:
        start = _fmt_local(s.get("first_dt"))
        end   = _fmt_local(s.get("last_dt"))
        dur   = f"{s.get('duration_min', '?')}m" if s.get("duration_min") is not None else "?"
        msgs  = s.get("event_count", 0)
        src   = s.get("subdir", "")[:15]
        title = s.get("title_hint", "")[:60]
        print(f"  {start}  {end}  {dur:>5}  {msgs:>4}  {src:<15}  {title}")

    if summary_only:
        return

    # ── Detail-Ausgabe pro Session ────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  DETAIL-ANALYSE (Grundlage für Maestro-Einträge)")
    print(f"{'─'*70}")

    for idx, s in enumerate(sessions_sorted, 1):
        start = _fmt_local(s.get("first_dt"))
        end   = _fmt_local(s.get("last_dt"))
        dur   = s.get("duration_min")
        dur_str = f"{dur} min" if dur is not None else "unbekannt"

        print(f"\n[{idx}] {start}–{end} | {dur_str}")
        print(f"     Quelle:    {s.get('session_key', '')}")
        print(f"     Nachr.:    {s.get('user_messages', 0)} User / {s.get('assistant_messages', 0)} Assist.")

        # Maestro-Vorschlag
        start_maestro = _round_to_5min(s.get("first_dt"))
        print(f"\n     ── Maestro-Vorschlag ──────────────────────────────────────")
        print(f"     Eintrag:     Activity")
        print(f"     start_time:  {start_maestro}  (5-min-Raster)")
        print(f"     duration:    {dur} min" if dur else "     duration:    0 (laufend oder unklar)")
        print(f"     name:        {s.get('title_hint', '(bitte benennen)')[:80]}")
        print(f"     task:        (aus Kontext ableiten)")
        print(f"     time_account: (aus GET /time-accounts ableiten)")

        if verbose:
            print(f"\n     ── Nachrichten-Auszug ─────────────────────────────────────")
            events = s.get("events", [])
            shown = 0
            for e in events:
                if shown >= 6:
                    remaining = len(events) - shown
                    print(f"     ... (+{remaining} weitere Nachrichten)")
                    break
                ts_local = _fmt_local(_parse_ts(e["timestamp"]))
                role = "👤" if e["role"] == "user" else "🤖"
                text_preview = e["text"][:200].replace("\n", " ")
                print(f"     {ts_local} {role} {text_preview}")
                shown += 1

    # ── Vollständige Nachrichten-Liste für Analyse ─────────────────────────────
    if verbose:
        print(f"\n{'─'*70}")
        print("  VOLLSTÄNDIGE NACHRICHTENFOLGE (chronologisch)")
        print(f"{'─'*70}\n")

        all_events = []
        for s in sessions_sorted:
            for e in s.get("events", []):
                e["_session_key"] = s.get("session_key", "")
                all_events.append(e)

        all_events_sorted = sorted(all_events, key=lambda e: e["timestamp"])

        for e in all_events_sorted:
            ts_local = _fmt_local(_parse_ts(e["timestamp"]))
            role = "👤 User    " if e["role"] == "user" else "🤖 Assist. "
            src = e.get("_session_key", "")[:30]
            text_preview = e["text"][:300].replace("\n", " ↵ ")
            print(f"  {ts_local}  {role}  [{src}]")
            print(f"           {text_preview}")
            print()


def _round_to_5min(dt) -> str:
    """Rundet datetime auf 5-Minuten-Raster ab und gibt YYYY-MM-DDTHH:MM zurück."""
    if not dt:
        return "??:??"
    local = dt.astimezone(TZ_BERLIN)
    minute = (local.minute // 5) * 5
    rounded = local.replace(minute=minute, second=0, microsecond=0)
    return rounded.strftime("%Y-%m-%dT%H:%M")


# ── Report-Template generieren ────────────────────────────────────────────────

def generate_day_file(target_date: str, sessions_data: list[dict]) -> str:
    """
    Generiert einen vollständigen Tagesbericht im Format von days/YYYY-MM-DD.md.
    Inklusive generierter UUIDs und 15-minütiger Time-Units zur lückenlosen Tagesabdeckung.
    """
    import uuid
    
    chronicle_day_uuid = str(uuid.uuid4())
    person_uuid = "86a3187d-df52-4ec5-9aba-b7112dcdceec" # Antigravity Standard
    try:
        config_path = "/home/ben/misc/maestro/config.json"
        if os.path.exists(config_path):
            with open(config_path) as f:
                conf = json.load(f)
                if "person_uuid" in conf:
                    person_uuid = conf["person_uuid"]
    except:
        pass

    lines = []
    lines.append(f"# Tagesbericht: {target_date}")
    lines.append("")
    lines.append(f"chronicle_day_uuid: {{UUID}}")
    lines.append(f"person_uuid: {person_uuid}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Aktivitäten sortieren
    sessions_sorted = sorted(sessions_data, key=lambda s: s.get("first_ts", ""))
    lines.append(f"## Aktivitäten{' (keine)' if not sessions_sorted else ''}")
    
    activities_list = []
    
    for s in sessions_sorted:
        first_dt = s.get("first_dt")
        last_dt = s.get("last_dt")
        if not first_dt or not last_dt:
            continue
            
        local_start = first_dt.astimezone(TZ_BERLIN)
        minute_start = (local_start.minute // 5) * 5
        start_rounded = local_start.replace(minute=minute_start, second=0, microsecond=0)
        
        local_end = last_dt.astimezone(TZ_BERLIN)
        minute_end = ((local_end.minute + 4) // 5) * 5
        if minute_end >= 60:
            end_rounded = local_end.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            end_rounded = local_end.replace(minute=minute_end, second=0, microsecond=0)
            
        target_date_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        if end_rounded.date() > target_date_dt:
            next_day = target_date_dt + timedelta(days=1)
            end_rounded = datetime(next_day.year, next_day.month, next_day.day, 0, 0, tzinfo=TZ_BERLIN)
            
        dur = int((end_rounded - start_rounded).total_seconds() / 60)
        if dur < 5:
            dur = 5
        
        name = s.get("title_hint", "(bitte benennen)")[:120].strip()
        if not name:
            name = "Interaktion und Analyse"
            
        time_account = "Core"
        subdir_lower = s.get("subdir", "").lower()
        session_key_lower = s.get("session_key", "").lower()
        if "maestro" in subdir_lower or "maestro" in session_key_lower:
            time_account = "Maestro"
        elif "echo" in subdir_lower or "echo" in session_key_lower:
            time_account = "Echo"
        elif "openclaw" in subdir_lower or "openclaw" in session_key_lower:
            time_account = "OpenClaw"
            
        act_uuid = str(uuid.uuid4())
        
        activities_list.append({
            "uuid": act_uuid,
            "start": start_rounded,
            "end": end_rounded,
            "name": name,
            "time_account": time_account
        })
        
        lines.append(f"- {{UUID}} {start_rounded.strftime('%H:%M')}–{end_rounded.strftime('%H:%M')} | {dur} min | {name} | {time_account}")

    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Aufgaben (aktiv)
    lines.append("## Aufgaben (aktiv)")
    lines.append("")
    lines.append("### {UUID} Maestro-Nutzung")
    lines.append("- geplant: --")
    lines.append("- fällig: --")
    lines.append("- dringlichkeit: MED")
    lines.append("- outcome: --")
    lines.append("- zeitkonto: Core")
    lines.append("- zeitkategorie: Agent")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Aufgaben (heute erledigt) (keine)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Chores (keine)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Time-Units (dokumentiert)
    lines.append("## Time-Units (dokumentiert)")
    lines.append("")
    
    start_of_day = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=TZ_BERLIN)
    
    for i in range(96):
        current_time = start_of_day + timedelta(minutes=i * 15)
        current_str = current_time.strftime("%H:%M")
        
        matching_act = None
        for act in activities_list:
            act_start = act["start"]
            act_end = act["end"]
            if act_start <= current_time < act_end:
                matching_act = act
                break
                
        tu_uuid = str(uuid.uuid4())
        
        if matching_act:
            lines.append(f"- {{UUID}} {current_str} | {matching_act['name']} | Agent")
        else:
            hour = current_time.hour
            if hour < 8 or hour >= 22:
                lines.append(f"- {{UUID}} {current_str} | Schlafen | Ruhe")
            else:
                lines.append(f"- {{UUID}} {current_str} | Ruhe | Ruhe")
                
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Time-Units (geplant) (keine)")
    lines.append("")

    return "\n".join(lines)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scannt Chat-Logs nach Aktivität an einem bestimmten Datum."
    )
    parser.add_argument("date", help="Datum im Format YYYY-MM-DD")
    parser.add_argument(
        "--logs-path", "-l", default=None,
        help="Pfad zum Verzeichnis mit JSONL-Log-Dateien (Fallback: ../sources/convos relativ zum Script)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Zeigt vollständige Nachrichtenverläufe"
    )
    parser.add_argument(
        "--summary", "-s", action="store_true",
        help="Nur die Kurzübersicht, kein Detail"
    )
    parser.add_argument(
        "--generate", "-g", action="store_true",
        help="Generiert days/YYYY-MM-DD.md als Rohling"
    )
    args = parser.parse_args()

    target_date = args.date
    logs_path = os.path.expanduser(args.logs_path) if args.logs_path else None

    # Datum validieren
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print(f"❌ Ungültiges Datum: {target_date!r} — erwartet: YYYY-MM-DD")
        sys.exit(1)

    scan_root = logs_path or _DEFAULT_CONVOS_ROOT
    print(f"\n  Scanne {scan_root} für {target_date} ...")
    sessions_raw, checked, hits = scan_all_logs(target_date, logs_path)
    print(f"  Geprüft: {checked} Dateien | Treffer: {hits} Dateien\n")

    # Sessions analysieren
    sessions_data = []
    for key, events in sessions_raw.items():
        analyzed = analyze_session(key, events)
        if analyzed:
            sessions_data.extend(analyzed)

    # Ausgabe
    print_report(target_date, sessions_data, args.verbose, args.summary)

    # Tagesbericht-Rohling generieren
    if args.generate:
        days_dir = os.path.join(os.path.dirname(__file__), "..", "days")
        os.makedirs(days_dir, exist_ok=True)
        out_path = os.path.join(days_dir, f"{target_date}.md")

        if os.path.exists(out_path):
            print(f"\n⚠️  Datei existiert bereits: {out_path}")
            print("   Überschreiben? [j/N] ", end="", flush=True)
            ans = input().strip().lower()
            if ans not in ("j", "ja", "y", "yes"):
                print("   Abgebrochen.")
                sys.exit(0)

        content = generate_day_file(target_date, sessions_data)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ Rohling geschrieben: {out_path}")


if __name__ == "__main__":
    main()
