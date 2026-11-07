---
name: walkthroughs
description: Erstellt nach einer Implementierungsaufgabe einen kompakten Ergebnisbericht mit Zusammenfassung, Änderungsliste und Abweichungen. Verwenden am Ende jeder Umsetzung.
---

# SKILL: Walkthrough

## Schritte

1. **Inhalte bestimmen** — Zusammenfassung, Umgesetzte Änderungen, Technische Details,
   Abweichungen, Tests & Review, Offene Punkte, Erkenntnisse & Reflexion
2. **Walkthrough anlegen:** MCP-Tool `create_walkthrough` aufrufen — `project` (UUID des
   Maestro-Projektrecords), `ticket`, `title`, die Abschnittsinhalte und optional
   `implementation_plan`.

## Bestehende Pläne/Walkthroughs nachschlagen

`list_implementation_plans`/`view_implementation_plan` für den referenzierten
Implementierungsplan; `list_walkthroughs`/`view_walkthrough` für die Duplikatprüfung
gegen einen bereits vorhandenen Walkthrough desselben Tickets.

## Pflichtregeln

- MUSS GELTEN: Jede Planabweichung ist im Walkthrough vollständig dokumentiert.
- MUSS GELTEN: Jede noch ausstehende Nutzer-, Abnahme-, Live-, Datenbank- oder
  Produktionsprüfung steht im Abschnitt „Offene Punkte" mit zuständiger Person und
  konkreter Handlung.
- Ticket-Abschluss setzt einen vorhandenen Walkthrough voraus
