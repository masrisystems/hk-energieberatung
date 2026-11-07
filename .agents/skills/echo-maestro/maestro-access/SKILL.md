---
name: maestro-access
description: Zugriffs- und Schreibgrundlage für eine laufende Maestro-Instanz — Transport, Write-Pfade, Feldlagen über `maestro_skill`, Abrufarten und Relationswerte. Use when eine Maestro-Resource gelesen oder geschrieben werden soll. Einzige Heimat der Write-Regeln; andere Maestro-Skills verweisen hierher.
---

# Maestro Access

## Überblick

Gemeinsame Grundlage für Zugriff auf und Schreiben in eine laufende Maestro-Instanz. Dieser Skill ist
die **einzige Heimat der Write-Regeln** — andere Maestro-Skills verweisen hierher und ergänzen nur ihr Eigenes.

## Verbindliche Regeln (Zugriff)

- nur mit laufender Maestro-Instanz arbeiten
- Zugriff ausschließlich über die MCP-Tools: `maestro_list`, `maestro_record`, `maestro_create`, `maestro_update`, `maestro_tracking`, `maestro_tracking_close`, `maestro_report`, `maestro_skill`, `maestro_archetypes`, `maestro_refs`, `maestro_chore_start`, `maestro_task_start`, `maestro_todo_complete`, `maestro_task_complete`, `maestro_chore_run_complete`
- Instanz nicht erreichbar: keinen Startversuch auslösen, keine lokale Ersatzannahme treffen
- keine Datenbankzugriffe; keine UI-Klickfolgen als Ersatz für echte HTTP-Action-Pfade

## Schreiben

- Anlegen: `maestro_create(archetype="<archetype>", fields={...})`
- Ändern: `maestro_update(archetype="<archetype>", identifier="<uuid>", fields={...})`
- beide liefern als Bestätigung den frisch abgerufenen Datensatz — keine weitere Verifikation nötig
- optionale Felder nur senden, wenn ein echter Wert gesetzt werden soll
- `maestro_create` und `maestro_update` immer sequenziell — nie parallel in einem Turn; Nutzer kann nach jedem Call eingreifen

**Activities:** `maestro_tracking(name, time_account, activity_type=None, task=None,
description=None, ticket_number=None, project=None)` ist der bevorzugte Weg für
Activity-Writes während einer Session — das Tool übernimmt Zeitabruf, 5-Minuten-Rasterung,
die Entscheidung Fortsetzen/Aktualisieren/Schließen+Neuanlegen sowie die kanonische
Namensbildung selbst; der Agent liefert nur die fachliche Einschätzung (roher Name ohne
Präfix, ggf. `time_account`/`activity_type`/`task`/`description`/`ticket_number`/`project`).
Mit `ticket_number` speichert das Tool `#<ticket_number>: <name>`; ist zusätzlich `project`
gesetzt und dessen Name weicht vom Zeitkontonamen ab, `<projekt>#<ticket_number>: <name>`.
`project` ohne `ticket_number` sowie ein `name` mit bereits enthaltener Ticketnummer oder
(bei gesetztem `project`) enthaltenem Projektnamen werden abgelehnt.
`maestro_tracking_close()` schließt die laufende Activity ohne Folgethema, ebenfalls mit
automatischem Zeitabruf/5-Minuten-Rasterung.
Der Agent baut dafür keine eigene Zeitlogik oder Schattenzustände; injizierte Hinweise zur
aktuellen Activity-Lage werden als Arbeitsgrundlage verwendet.
`maestro_create`/`maestro_update` bleiben für `activities` als Fallback für Sonderfälle bestehen
(z.B. nachträgliche Korrektur einer bereits geschlossenen Activity).

## Feldlagen aus `maestro_skill`

Welche Felder erlaubt sind (Pflicht/optional), die Enum-Werte, Relationsregeln und Schreib-Nebeneffekte
je Archetype liefert `maestro_skill(<archetype>)`.

- Die Ausgabe von `maestro_skill(<archetype>)` muss vor jedem Aufruf im aktuellen Kontext sichtbar sein, der Feldnamen, Enum-Werte oder Wertformen dieses Archetypes nennt — beim Schreiben wie beim Lesen, `maestro_list` mit `filters` eingeschlossen; ist sie es nicht (neuer Archetype oder nach einem Compact), einmal abrufen. Ein Abruf deckt alle weiteren Aufrufe desselben Archetypes.
- Felder, Enum-Werte und Wertformen nie aus Record-Payloads, aus Erinnerung oder aus altem Chat ableiten.

## Abrufarten

- `maestro_skill(<archetype>)` — Schema (Felder, Enums, Regeln, Nebeneffekte).
- `maestro_report` — Tagesstand: vorhandene Records, aktive Tasks, offene Todos, jeweils mit
  UUID. Immer mit Standard-Limit aufrufen, außer der volle Bericht ist explizit nötig.
  Einmal je Arbeitsblock abrufen und lokal weiterverwenden — die eigenen Maestro-Daten ändert
  niemand sonst; erneut abrufen nach eigenen Writes oder auf Nutzerhinweis.
- UUID offener Todos und Tasks ausschließlich aus `maestro_report` auflösen.
- `maestro_list(archetype, filters, per_page)` — gefilterte Liste; Status- und Dublettenklärung
  über `maestro_report`. Records ohne gesetzten Status gelten als offen und tragen kein
  `status`-Feld.
- `maestro_record(archetype, identifier)` — ein gezielt benötigter Einzeldatensatz, Relationen
  aufgelöst (Markdown).

## Relationswerte aus der Instanz

Das Schema nennt, *welche* Relationsfelder es gibt — die **Werte** (UUIDs) stammen aus der Instanz:

- Stammdaten-Relationen (time-accounts, time-categories, activity-types) über `maestro_refs()` auflösen; der aufgelöste Wert gilt für die ganze Session.
- Übrige Relationen (z.B. task, endeavour) je Write frisch über gezieltes `maestro_list`/`maestro_report` auflösen.

Aus der Antwort das Feld `uuid` verwenden (bei activity-types die `ucid`).

## Tasks

- Vor jeder Task-Anlage `maestro_report` prüfen. Liegt ein Task gleichen Arbeitsgegenstands offen, diesen nutzen.

## Todos

- **Live-Abhak-Pflicht:** Todo sofort nach Erledigung des entsprechenden Schritts abhaken — nicht am Ende des Tickets
- **`modus`:** nur beim Create setzen; Wert ist eine UCID (`IMPLEMENT`, `ANALYSE`, `QUESTION`, …) — keine UUID; beim Update nicht senden
- **Abschluss:** `maestro_todo_complete(todo_uuid)` — der Wrapper sendet `status = DONE`; der Server setzt `finished_at` selbst

## Chore-/Task-Läufe

- **Chore-Start:** `maestro_chore_start(identifier="")` für `now`, `maestro_chore_start("YYYY-MM-DD")` für Datum, `maestro_chore_start("<uuid>")` für bekannten Chore
- **Task-Start:** `maestro_task_start(task_uuid)` wenn der Auslöser bereits eine Task-UUID kennt
- **Task-Abschluss:** `maestro_task_complete(task_uuid)` statt freier `outcome`-/`finished_at`-Payloads
- **Chore-Fulfillment:** `maestro_chore_run_complete(task_uuid)` — der Server liest `chore_uuid`, `chore_date` und Person-Kontext aus den gespeicherten Task-Metadaten

## Formulierungsrichtlinie für Maestro-Einträge

- den Nutzer bei Bedarf mit der bekannten bestätigten Identität benennen
- über mich selbst nicht in der dritten Person schreiben
- Formulierungen knapp, konkret und nachvollziehbar halten
