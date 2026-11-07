---
name: backlog-refinement
description: Führt einen strukturierten Backlog-Refinement-Lauf durch: Tasks mit offenen Todos aus dem Maestro-Report einzeln vorlegen, gemeinsam besprechen und Entscheidungen sofort nachziehen.
---

# SKILL: Backlog-Refinement

## Einstieg

1. `maestro_report` abrufen, falls nicht bereits im Kontext.
2. Alle Tasks mit mindestens einem offenen Todo extrahieren.
3. Liste dem Nutzer von oben nach unten vorlegen — Reihenfolge aus dem Report beibehalten.

## Pro-Task-Ablauf

Für jeden Task in der Liste:

1. **Vorlegen:** Task-Name und alle offenen Todos nennen.
2. **Kontext ergänzen:** Letzte Aktivität, geschätztes Alter des ältesten Todos, bekannte Abhängigkeiten zu anderen Tasks.
3. **Entscheidungsoptionen anbieten:**
   - **Weiterführen** — bleibt offen; Priorität ggf. anpassen
   - **Schließen** — Task und Todos in Maestro als erledigt oder abgebrochen markieren
   - **Aufteilen** — Task in kleinere, unabhängige Einheiten zerlegen; neue Tasks anlegen
   - **Verschieben** — in Backlog oder auf konkretes Datum; Todos entsprechend anpassen
   - **Ticket anlegen** — wenn aus dem Gespräch eine neue Anforderung entsteht (`echo-artifacts/tickets` laden)
4. **Entscheidung sofort nachziehen:** Maestro-Update direkt nach Bestätigung — kein Sammeln am Ende.

## Abschluss

1. **Zusammenfassung** vorlegen: Anzahl besprochener Tasks, getroffene Entscheidungen (wie viele geschlossen, aufgeteilt, verschoben, Tickets angelegt).
2. **Diary-Eintrag** in Echo Memory anlegen (`echo-memory` laden).

## Pflichtregeln

- MUSS GELTEN: Kein Maestro-Update ohne vorherige Nutzerbestätigung der Entscheidung.
- MUSS GELTEN: Maestro-Nachzug direkt nach jeder Entscheidung — nie am Ende des gesamten Laufs.
- MUSS GELTEN: Keine automatische Entscheidung; der Agent legt vor, der Nutzer entscheidet.
