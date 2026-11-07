---
name: milestones
description: Verwaltet Milestones eines Projekts. Verwenden bei Milestone-Operationen: erstellen, Tickets zuordnen, abschließen.
---

# SKILL: Milestone Management

## Speicherort

Bei einem Projekt mit dateibasiertem Ticketsystem liegen Milestones als Markdown unter
`docs/milestones/`, eine Datei je Milestone — keine Unterordner, keine Lebenszyklus-Trennung
wie bei Tickets. Der Lebenszyklus steckt im Feld `status` (`OPEN` / `RELEASED`).

**Dateiname:** der Versionswert selbst (z. B. `2.4.12.md`), sonst eine kurze
kebab-case-Kurzform des Titels.

## Milestone anlegen

MCP-Tool `create_milestone` aufrufen — `project` (UUID des Maestro-Projektrecords), `name`,
`description`, `target_date` sowie optional `version` und `tickets` (Ticket-Referenzen
`#NNN` als Markdown-Liste, eine je Zeile).

## Ticket einem Milestone zuordnen

Referenz (`#NNN`) im Abschnitt `## Tickets` der Milestone-Datei ergänzen — ein Ticket kann
in mehreren Milestone-Dateien referenziert sein.

## Milestone abschließen

`status` im Meta-Block auf `RELEASED` setzen, sobald das zugehörige Release durchgeführt
wurde (→ `release-vorbereitung`). Die Datei bleibt unter `docs/milestones/` liegen — Milestones
werden nicht verschoben oder gelöscht.

## Milestones einer Version auflösen (für `release-vorbereitung`)

1. `list_milestones(project)` aufrufen, je Treffer bei Bedarf `view_milestone(project, milestone)`.
2. Namensabgleich gegen die normalisierte Version wie bei GitLab/Maestro:
   ```bash
   python3 .agent/skills/release-vorbereitung/tools/release_utils.py milestone_matches "<milestone-feld>" "<version>"
   ```
   Geprüft wird das `milestone`-Feld (Titel), nicht der Dateiname.
3. Release-Menge: Vereinigungsmenge der `## Tickets`-Referenzen aller passenden Dateien,
   dedupliziert über die Ticket-ID.

## Pflichtregeln

- MUSS GELTEN: Das erstellte Milestone enthält alle Pflichtabschnitte des Templates.
- Ticket-Referenzen sind Ticket-IDs (`#NNN`) aus `docs/tickets/` — keine freien Titel.
