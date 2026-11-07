# echo-memory — Einrichtung

Setup-Referenz für das Vier-Palace-Gedächtnissystem. Session-Verhalten: `SKILL.md`.

---

## Aktivierung

1. `.agent/config.json` → `echo_memory_enabled: true`
2. Palace-Pfade in `memory.mempalace.*` auf vorhandene Verzeichnisse zeigen lassen
   (Standard: `/opt/echo-agents/memory/{atlas,evidence,stream,nexus}`)
3. `echo-memory-gateway`-MCP-Server registrieren (siehe unten)

---

## MCP-Registrierung je Plattform

Einziger MCP-Server für alle Plattformen:

```json
{
  "mcpServers": {
    "echo-memory-gateway": {
      "command": "python3",
      "args": [".agent/tools/echo-memory-gateway/server.py"]
    }
  }
}
```

- **Claude Code:** `.mcp.json` im Projekt-Root.
- **OpenClaw:** `openclaw mcp set echo-memory-gateway
  '{"command":"python3","args":["/absoluter/pfad/zum/projekt/.agent/tools/echo-memory-gateway/server.py"]}'`
  — alten Server bei Bedarf mit `openclaw mcp unset <name>` entfernen.
- **Antigravity:** wird von `echo-init` automatisch in `.agent/mcp_config.json` registriert.

---

## Gateway-Verhalten

- Das Gateway durchsucht Nexus und Stream parallel; Atlas und Evidence sind Teil der
  Architektur, werden aktuell aber nicht aktiv durchsucht.
- Schreiben geht technisch erzwungen nur nach Nexus — für Atlas, Evidence und Stream
  existiert kein Write-Tool.
