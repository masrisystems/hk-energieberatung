# Ticketing-Konfiguration

Dieses Dokument beschreibt, wie ein Agent das aktive Ticket-System eines Projekts
bestimmt und wie er damit umgeht.

---

## Systeme

### `internal` — Dateibasiertes Ticket-System

Tickets sind Markdown-Dateien im Ticket-Verzeichnis des Projekts.
Das Verzeichnis enthält vier Unterordner:

```
<ticket_path>/
  open/       ← Aktive Tickets (dringend, in Bearbeitung, Blocker)
  backlog/    ← Geplante Tickets für spätere Bearbeitung
  completed/  ← Abgeschlossene Tickets
  discarded/  ← Verworfene Tickets (Duplikat, kein Fehler, nicht mehr gewünscht, ...)
```

**Ticket-Dateiname:** `NNN_kebab-case-titel.md`
- `NNN` ist die fortlaufende Ticket-ID (nullaufgefüllt, mindestens 3 Stellen)
- Beispiele: `001_setup-datenbank.md`, `042_fix-login-redirect.md`

**Commit-Referenz:** `(#NNN) ` als Präfix der Commit-Message (ohne führende Nullen)

---

### `gitlab` — GitLab Issues

Tickets werden als Issues im konfigurierten GitLab-Projekt geführt — es entstehen keine
Dateien unter `<ticket_path>/`. Zugriffs- und Schreibgrundlage ist
`.agent/skills/gitlab-integration/SKILL.md`.

---

### `maestro` — Maestro-Ticketsystem

Tickets, Implementierungspläne und Walkthroughs leben als strukturierte Records in der
konfigurierten Maestro-Instanz — es entstehen keine Dateien unter `<ticket_path>/`.
Zugriffs- und Schreibgrundlage ist
`.agent/skills/echo-maestro/maestro-access/SKILL.md`; Feldlagen und Statuswerte liefert
`maestro_skill(<archetype>)` zur Laufzeit.

---

## Platzierung neuer Tickets

| Kriterium | Ziel-Ordner |
|-----------|-------------|
| Blocker für ein Ticket in `open/` | `open/` |
| Dringend oder für aktuellen Sprint nötig | `open/` |
| Sinnvoll, aber nicht sofort nötig | `backlog/` |
| Zweiter Meinung des Nutzers nötig | `backlog/` (oder fragen) |

Im Zweifel: Nutzer entscheiden lassen.

---

## Ticket-Lifecycle (internal)

```
Neu → open/ oder backlog/
open/ → completed/    (nach Walkthrough und Nutzer-Freigabe)
open/ → discarded/    (mit Begründung im Ticket)
backlog/ → open/      (wenn Priorität steigt oder Sprint beginnt)
backlog/ → discarded/ (mit Begründung im Ticket)
open/|backlog/ → gelöscht (Fehlanlage, nach Nutzerbestätigung)
```

Ein Ticket wird nie gelöscht — nur verschoben — außer bei einer vom Nutzer bestätigten
Fehlanlage.
Der Inhalt eines verworfenen Tickets enthält immer eine `## Begründung`-Sektion.
