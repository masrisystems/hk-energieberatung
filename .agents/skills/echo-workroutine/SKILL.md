---
name: echo-workroutine
description: Technische Bedien- und Runtime-Schnittstelle für den ticketbezogenen Work-Routine-Loop. Verwenden beim Ausführen des Workflows `work-routine`.
---

# Skill: echo-workroutine

## MCP-Aufrufe

- `workroutine_next(project_ucid: str | None = None)` — liefert den fachlichen Auftrag zum
  nächsten offenen Ticket-Todo.
- `workroutine_complete(file: str | None = None, result: str | None = None, blocked: str | None = None)`
  — schließt einen Arbeitsschritt ohne Artefaktbezug ab.
- Bei Artefaktbezug (Implementierungsplan bei `approved`, Walkthrough bei `doing`): die von
  `workroutine_next()` ausgegebene `create_implementation_plan(...)`/`create_walkthrough(...)`-Anweisung
  mit deren `todo`-Parameter ausführen — liefert ab und schließt Zuweisung/Status/Todo im selben Aufruf.

## Automatisch durch die Runtime ausgeführte Schritte

`workroutine_next()` führt vor der Auswahl genau einmal den Ereignisabgleich über die
konfigurierten Ticketquellen aus, wählt das nächste offene Ticket-Todo, löst Projekt und
`ticket_system` auf, liest das Ticket und leitet aus Status und vorhandener Planinformation
den konkreten Arbeitsauftrag ab. Bei Status `doing`/`review` bereitet er zusätzlich den
kanonischen Ticket-Branch vor, sofern `git_branching_mode: ticket-branches` konfiguriert ist.

`workroutine_complete()`/die artefaktgekoppelten Abschlussaufrufe führen Ticket-, Zuweisungs-,
Status- und Todo-Operationen entsprechend dem aktuellen Ticketstatus mechanisch aus —
einschließlich der GitLab-Merge-Request-Übergabe nach bestandenem Review.
