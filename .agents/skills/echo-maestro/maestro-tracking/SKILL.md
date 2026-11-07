---
name: maestro-tracking
description: Live-Tracker für Maestro während einer aktiven Session. Use when bei einer neuen Nutzeranweisung geprüft werden soll, ob die laufende Aktivität fortgeführt oder abgeschlossen werden muss — und Maestro entsprechend kurz und direkt aktualisiert werden soll.
---

# Maestro Session Live Tracker

## Ausführungszeitpunkt — Absolut

**Dieser Skill wird als allererster Schritt ausgeführt, bevor irgendein anderer Tool-Call erfolgt.**

Der erste Session-Turn führt ausschließlich den Session-Start durch — kein `maestro_tracking`-Aufruf.
Ab dem zweiten Nutzer-Turn mit Arbeitskontext ist `maestro_tracking` der erste Tool-Aufruf des Turns.

**Vor dem ersten Maestro-Tool-Call:** `.agent/skills/echo-maestro/maestro-access/SKILL.md` laden,
falls nicht im Kontext. Dieser Schritt ist nicht parallelisierbar — kein anderer Tool-Call im
selben Batch.

## Verbindliche Regeln

- nur direkt belegte positive Evidenz verwenden
- **Leitprinzip: lieber einen Eintrag zu viel als gar keinen** — Exaktheit kann im Review korrigiert werden, fehlende Einträge nicht

---

## Kontext-Integrität

Sind Operating Model oder Profession nicht nachweisbar im Sitzungskontext: `onboarding`
vollständig ausführen, bevor weitergearbeitet wird.

---

## Schritt 1 — Neue Activity oder Fortsetzung?

Maßgeblich ist der Arbeitsgegenstand (Ticket, Vorgang oder klar abgegrenzte
Fragestellung) — nicht Projekt oder Zeitkonto.

| Situation | Entscheidung |
|---|---|
| Gleicher Arbeitsgegenstand und gleiches Zeitkonto wie laufende Activity | Fortsetzung |
| Anderer Arbeitsgegenstand oder anderes Zeitkonto — auch bei sonst gleichem Thema | Übergang |
| Unsicher | Übergang — neue Activity, Exaktheit korrigiert das Review |

Diese fachliche Einschätzung trifft der Agent. Zeitabruf, 5-Minuten-Rasterung, Abgleich mit
einer bereits offenen Activity und die Entscheidung Fortsetzen/Aktualisieren/Schließen+Neuanlegen
übernimmt
`maestro_tracking(name, time_account, activity_type=None, task=None, description=None, ticket_number=None, project=None)`.
Der Agent liefert nur den gewünschten Namen — bei Fortsetzung unverändert, bei Übergang den
Namen für den neuen Themenblock — sowie `time_account` und ggf. `activity_type`/`task`/
`description`/`ticket_number`/`project`.

**Activity benennen und verknüpfen:** Der Name ist die Aktivität selbst — kein Projekt-,
Workspace- oder Ticketpräfix; die kanonische Präfixbildung übernimmt das Tool über
`ticket_number`/`project` (siehe `maestro-access`). Der Name benennt den konkreten
Arbeitsgegenstand — Artefakt, Datei oder Thema —, nicht nur die Verarbeitungsphase
(„Implementieren", „Plan erstellen", „Umsetzen") und nicht die bei gesetztem
`ticket_number` bereits im Präfix enthaltene Ticketnummer. `task`-Feld sofort mitgeben,
sobald die zugehörige Task bekannt ist.

**Existiert keine laufende Activity und liegt noch kein Aufgabenkontext vor** (reiner
Session-Start ohne Nutzeranweisung): `maestro_tracking`-Aufruf auslassen; beim nächsten
Prompt mit Kontext aufrufen. Aufgabenkontext bekannt → Aufruf VOR dem ersten Arbeitsschritt.
Kein Lesen, Schreiben oder Analysieren davor.

Zeigt der Tagesreport offene Activities aus Vorsessions (`duration = 0`, `start_time` vor dieser
Session): `maestro-session-startup` zur Auflösung laden.

**Projekt-Kontext:** Ist `maestro.focus_project_uuid` gesetzt, liefert bereits der
parameterlose `onboarding.py`-Aufruf (Stufe 1) den Maestro-Projektdatensatz mechanisch
(Branch A, #200) — kein Agenten-Schritt nötig, außer der Projekt-Root ist trotzdem nicht im
Kontext sichtbar (z. B. `focus_project_uuid` nicht gesetzt, oder Kontext nach Compact
verloren). In diesem Fall Auflösung wiederholen — in dieser Priorität:
A. `maestro.focus_project_uuid` gesetzt → `maestro_record(archetype="projects", identifier=<uuid>)`
B. Kein `focus_project_uuid`, aber Projekt aus Kontext ableitbar → `maestro_list(archetype="projects", filters={"slug": "<slug>"}, per_page=1)`
C. Weder A noch B → weiter ohne Projektkontext
Der Record führt das lokale Projektverzeichnis im Feld `project_directory`. Diesen Wert
entnehmen — keinen Pfad aus Bestandteilen zusammensetzen.
`docs_entry_path` gesetzt → Skill `projektwissen` laden und ausführen.

Branch B löst nicht mehr nur nach einem erkannten Compact aus, sondern sobald der Nutzer
ein Projekt erstmals im Gesprächsverlauf benennt und noch keine Projekt-Root-Information im
Kontext sichtbar ist.

---

## Schritt 2 — Task-Stand pflegen

Wenn der Agent an einer Task arbeitet:

- **Task anlegen**: `maestro_create(archetype="tasks", fields={...})`
- **Task-Beschreibung aktualisieren**: `maestro_update(archetype="tasks", identifier="<id>", fields={...})`
- **Todos abschließen**: `maestro_update(archetype="todos", identifier="<id>", fields={"status": "DONE"})`
- **Neue Todos anlegen**: `maestro_create(archetype="todos", fields={...})`
  - Todos zu Beginn jedes Arbeitsblocks anlegen — nicht rückwirkend nach erledigter Arbeit
- **Task-Verknüpfung** an Activity setzen (`task`-Feld), sobald klar ist welche Task gemeint ist
- **Todo-Disziplin:** Genau ein Todo ist zu jedem Zeitpunkt aktiv in Bearbeitung. Ein Todo gilt
  erst als erledigt, wenn der beschriebene Schritt wirklich erreicht und kurz geprüft ist;
  Teilfortschritt reicht nicht für DONE. Kein Sammeltodo für unabhängige Schritte.

---

## Schritt 3 — Abschluss-Sequenz nach Commit

Nach einem abschließenden Commit — sofort ausführen, nicht beim nächsten Nutzer-Prompt:

**Todo-Check:** Alle im aktuellen Kontext bekannten offenen Todos — aus dem Tagesreport,
aus Task-Records, aus dem Sitzungsverlauf — gegen die geleistete Arbeit prüfen. Erfüllte
Todos sofort abschließen. Gilt unabhängig davon, ob die Activity ein `task`-Feld gesetzt hat.

1. **Activity schließen:** `maestro_tracking_close()` — übernimmt Zeitabruf und
   5-Minuten-Rasterung. Immer.
2. **Kein Task** → fertig.
3. **Task ohne Todos** → Arbeit insgesamt abgeschlossen? Wenn ja: `outcome=DONE` setzen.
4. **Task mit Todos, alle DONE** → `outcome=DONE` setzen.
5. **Task mit Todos, noch offene** → Activity schließen, Task offen lassen. Offene Todos **nicht ignorieren** — explizit sichtbar halten.

„Abschließender Commit" = der Commit enthält alle geplanten Änderungen für diesen Arbeitsblock.

---

## Write-Regeln (Session-Ebene)

Write-Mechanik (Kommandos, Feldlagen aus `maestro_skill`, Abrufarten, Schreib-Bestätigung) steht in
`maestro-access`. Session-bezogene Write-Regeln:

- **Status:** die laufende Activity ist aus dem Sessionverlauf bekannt; Abrufarten und Statusquelle
  (kein Listenabruf zur Statusklärung) stehen in `maestro-access`.
- **Fortsetzung/Übergang (Schritt 1):** Zeitabruf, Rasterung und Update-vs-Neuanlage übernimmt
  `maestro_tracking` — kein manueller `date`-Aufruf, keine manuelle Rundung durch den Agenten.
- **Abschluss-Sequenz (Schritt 3):** beim letzten belegten Zeitpunkt schließen, nicht bei „jetzt";
  aktuelle Systemzeit vor diesem Write abrufen — nie aus dem Kontext schätzen.
- **Task/Todo:** Task nur bei stabilem eigenständigem Arbeitsgegenstand ohne passenden Bestand anlegen;
  Todo nur bei explizit formuliertem nächsten Schritt, taskgebunden, handlungsorientiert. Beschreibung
  nur ändern, wenn sich der Stand tatsächlich geändert hat.

---

## Referenzen

- `../maestro-access/SKILL.md`
