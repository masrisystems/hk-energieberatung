---
name: echo-archive
description: Steuert die Echo-Archivierung und lückenlose Protokollierung über das Echo Gateway.
---

# Skill: echo-archive

Steuert die Echo-Archivierung über den Echo Gateway.

## Aktivierungsprüfung — zuerst lesen

`.agent/config.json` lesen → `echo_archive_enabled` prüfen.

- `true` → dieser Skill gilt vollständig für diese Session. `echo_save` nach jeder sichtbaren Assistant-Nachricht aufrufen.
- `false` → **dieser Skill ist inaktiv. Kein `echo_save`-Aufruf in dieser Session.**

Wenn unklar: im Zweifel nicht aufrufen. Nie `echo_save` aufrufen ohne vorherige Prüfung.

---

## MCP-Konfiguration

**Echo Gateway** (Archivierung mit echo_*-Metadaten):
```json
{
  "mcpServers": {
    "echo-archive-gateway": {
      "command": "python3",
      "args": [".agent/tools/echo-gateway/server.py"]
    }
  }
}
```

---

## Archivierungsregel: echo_save

**Nach jeder sichtbaren Assistant-Nachricht an den Nutzer: `echo_save` aufrufen.**
Das ist keine Empfehlung. Das ist eine Ausführungspflicht.

`echo_save` archiviert den **exakten finalen Wortlaut** der tatsächlich gesendeten
Nachricht — keine Paraphrase, keine Zusammenfassung, keine Verdichtung.

```
echo_save(text="<exakter Originaltext der gesendeten Nachricht>", platform="<plattform>")
```

Plattformwert: `"claude-code"` · `"antigravity"` · `"openclaw"`

### Trennung von Text und Metadaten

`text` enthält ausschließlich den Nachrichtentext.
Metadaten (Plattform, Session-ID, Persona, Zeitstempel, Maschine, User) werden
**systemseitig vom Gateway ergänzt** — sie gehören nicht in den Text.

### Was nicht archiviert wird

- Interne Turns ohne sichtbare Assistant-Antwort an den Nutzer
- Reine Tool-Aufrufe ohne begleitenden Antworttextecho_save selbst
- Sehr kurze technische Bestätigungen ohne inhaltlichen Wert ("OK", "Verstanden")

---

## Strukturelle Einschränkung: Agent-initiiertes echo_save

Ein agent-seitig nachbereiteter `echo_save`-Aufruf ist **strukturell unzuverlässig**
für verbatim-Archivierung:

- Der Agent kann den kanonisch final ausgelieferten Output nicht garantiert identisch
  reproduzieren — zwischen Entwurf, Tool-Sequenz und tatsächlicher Auslieferung
  können Abweichungen entstehen.
- Eine agent-seitige Rekonstruktion ist eine Annäherung, kein Verbatim-Abbild.

Für zuverlässige Verbatim-Archivierung ist ein **Runtime-Hook** erforderlich:
der Hook muss nach Finalisierung einer sichtbaren Assistant-Nachricht automatisch
`echo_save` mit genau dem ausgelieferten Text aufrufen — nicht mit einem Entwurf
und nicht mit einer späteren Rekonstruktion.

Bis ein solcher Hook verfügbar ist: Agent ruft `echo_save` mit dem unmittelbar
zuvor gesendeten Text auf. Das ist die beste verfügbare Annäherung, aber kein
Ersatz für einen echten Post-Output-Hook.

---

## Runtime-Anforderung: Post-Output-Hook (OpenClaw)

Für korrekte Verbatim-Archivierung in OpenClaw wird ein Hook benötigt, der:

1. Nach jeder finalisierten und an den Nutzer ausgelieferten Assistant-Nachricht
   automatisch ausgelöst wird
2. Den tatsächlich ausgelieferten Nachrichtentext als `text`-Parameter übergibt
3. `echo_save(text=<finaler_text>, platform="openclaw")` aufruft

OpenClaw-Hook-Konfiguration (sobald verfügbar):
```json
{
  "hooks": {
    "post-assistant-message": {
      "command": "python3",
      "args": [".agent/tools/echo-gateway/hook_save.py"],
      "env": { "PLATFORM": "openclaw" }
    }
  }
}
```

`hook_save.py` würde den Nachrichtentext aus dem Hook-Kontext lesen und
`echo_save` direkt über die Python-API aufrufen (kein MCP-Roundtrip nötig).

**Aktueller Status:** Hook-Mechanismus für OpenClaw nicht verifiziert verfügbar.
Bis zur Verfügbarkeit: agent-seitiger Aufruf als Übergangslösung.

---

## Fehlerverhalten

- Gateway nicht erreichbar → sichtbaren Hinweis ausgeben, **nicht still übergehen**
- `echo_archive_enabled == false` → Gateway antwortet mit Hinweis, kein Abbruch
- `mempalace_echo_palace_path` fehlt → Konfigurationsfehler sichtbar melden
- Archivierung fehlgeschlagen → Hinweis in der Antwort, kein Retry automatisch

---

## Testprotokoll

1. Frische Session starten
2. Inhaltliche Aufgabe stellen, Assistant-Antwort senden
3. `echo_save` mit exaktem Antworttext aufrufen
4. Prüfen:
   ```bash
   python3 -c "
   from mempalace.palace import get_collection
   import json
   config = json.load(open('.agent/config.json'))
   col = get_collection(config['mempalace_echo_palace_path'])
   data = col.get(include=['documents','metadatas'])
   for doc, meta in zip(data['documents'], data['metadatas']):
       print(meta.get('echo_platform'), meta.get('echo_persona'), doc[:80])
   "
   ```
5. Akzeptanzkriterien:
   - Archivierter Text entspricht dem tatsächlich gesendeten Output
   - `echo_persona`, `echo_platform`, `echo_session_id` korrekt gesetzt
   - Kein stilles Fehlschlagen
