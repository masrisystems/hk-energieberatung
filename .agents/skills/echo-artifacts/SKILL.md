---
name: echo-artifacts
description: Bündelt die vier Artefakttypen des Frameworks (Ticket, Implementierungsplan, Walkthrough, Milestone) — ein gemeinsamer MCP-Server, vier Subskills. Einstiegspunkt; enthält selbst keine Arbeitsschritte.
---

# SKILL: Echo Artifacts

Gemeinsame Grundlage für alle vier Artefakttypen: der MCP-Server
`tools/artifacts_mcp_server.py` — je Artefakttyp `create_*`/`list_*`/`view_*`, Ticket
zusätzlich `update_ticket` — sowie die zugehörigen Vorlagen unter `templates/`.

## Subskills

| Artefaktart | Subskill |
|---|---|
| Ticket | `echo-artifacts/tickets` |
| Implementierungsplan | `echo-artifacts/implementation-plans` |
| Walkthrough | `echo-artifacts/walkthroughs` |
| Milestone | `echo-artifacts/milestones` |

Arbeitsschritte, Lebenszyklus und artefakttypspezifische Regeln stehen in der jeweiligen
Subskill-`SKILL.md` — diese Datei lädt keinen davon vor.
