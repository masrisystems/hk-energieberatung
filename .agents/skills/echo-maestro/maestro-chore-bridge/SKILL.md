---
name: maestro-chore-bridge
description: Startet einen Maestro-Chore- oder Task-Lauf, injiziert die Rückgabe in den Agentenkontext und schreibt bestätigte Abschlüsse semantisch zurück. Use when ein externer Auslöser oder Script-Pfad einen konkreten Chore-/Task-Lauf in Echo ausführen soll.
---

# Maestro Chore Bridge

## Zweck

Schmaler Bridge-Pfad zwischen Maestro als führendem System und dem Echo-/OpenClaw-Agentenlauf.

Maestro bestimmt den Lauf, legt Task/Todos an oder liefert einen bestehenden offenen Lauf zurück.
Der Agent konsumiert nur die Rückgabe und schreibt bestätigte Fortschritte semantisch zurück.

## Verbindliche Regeln

- kein lokaler Datumsabruf für Chore-Start oder Chore-Abschluss
- kein freies `status = DONE` für Todos
- keine lokale Task-/Todo-Anlage
- Writeback nur über die semantischen Wrapper `maestro_todo_complete`, `maestro_task_complete`, `maestro_chore_run_complete`

## Start-Einstiege

### Chore

- `maestro_chore_start("")` → `now`
- `maestro_chore_start("YYYY-MM-DD")` → datumsgesteuert
- `maestro_chore_start("<uuid>")` → bekannter Chore

### Task

- `maestro_task_start(task_uuid)` → bekannter Task

## Ablauf

1. Passenden Einstieg aufrufen
2. Rückgabe prüfen
3. Bei `found: false` sofort beenden — kein weiterer Agentenlauf
4. Bei `found: true` `task`, `todos`, `workflow` und ggf. `chore` als kanonischen Arbeitsauftrag in den Agentenkontext übernehmen
5. Agent arbeitet schrittweise
6. Bestätigte Todo-Abschlüsse sofort via `maestro_todo_complete(todo_uuid)` zurückschreiben
7. Nach vollständiger Abarbeitung zuerst `maestro_task_complete(task_uuid)`, danach `maestro_chore_run_complete(task_uuid)`

## Rückgabe-Vertrag

- `found`
- `source` (`new_task` oder `existing_task`; bei Task-Start task-spezifische Quelle aus Maestro)
- `task`
- `todos`
- `workflow`
- bei Chore-Starts zusätzlich `chore`

## Cron-/Script-Handoff

Ein externer Auslöser übergibt an Echo nur den semantischen Einstieg:

- leer / `now`
- ein Datum `YYYY-MM-DD`
- eine bekannte `chore_uuid`
- eine bekannte `task_uuid`

Alle ableitbaren Werte bleiben auf der Maestro-Seite bzw. im `maestro_mcp_server.py`.
