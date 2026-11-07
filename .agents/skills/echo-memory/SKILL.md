---
name: echo-memory
description: Vier-Palace-Gedächtnissystem (Nexus, Atlas, Evidence, Stream) zur semantischen Wissensspeicherung und sessionübergreifenden Kontextpersistenz.
---

# Skill: echo-memory

Vier-Palace-Gedächtnissystem. Ergänzt das plattformeigene Memory-System
(MEMORY.md bzw. Plattform-Standard). Einrichtung und MCP-Registrierung: `SETUP.md`.

---

## Die vier Palaces

| Name | Zweck | Zugriff |
|---|---|---|
| **Nexus** | Operatives Arbeitsgedächtnis | lesen + schreiben |
| **Atlas** | Kuratiertes, bestätigtes Wissen | lesen |
| **Evidence** | Belegquellen für Atlas | lesen |
| **Stream** | Automatischer Datenzufluss via Pipeline | lesen |

---

## Session-Start

`mempalace_status` aufrufen → Palace-Überblick, PALACE_PROTOCOL (Verhaltensregeln für
diese Session) und AAAK-Spec.

Bestätigung: `Echo Memory geladen. [N Drawers gesamt / "leer"]`

---

## Koexistenz & Routing

Echo Memory ergänzt das plattformeigene Memory-System — beide sind aktiv. Jede Information
hat eine primäre Heimat; bei Bedarf Querverweis statt Doppelpflege.

| Information | Primäre Heimat |
|---|---|
| Kompakte sessionübergreifende Fakten: Präferenzen, Verhaltenskorrekturen, Projektnotizen, Verweise | MEMORY.md / Plattform-Memory — Format und Mechanik der Plattform |
| AAAK-Drawers, Diary, große Bestände, semantisch durchsuchbares Wissen | Palace (Nexus) |

- **Abfragen über vergangene Arbeit:** `mempalace_search` zuerst — der Palace ist die
  Suchquelle; die Quelle (welcher Palace, welches Ergebnis) muss nachvollziehbar sein.
  Dateisystem und externe Quellen danach.
- **Duplikat-Disziplin:** `mempalace_check_duplicate` prüft nur den Palace; für MEMORY.md
  gilt die Plattform-Mechanik — kein synchronisierender Abgleich zwischen den Systemen.

---

## Suchen

`mempalace_search` durchsucht Nexus und Stream parallel (optionale Filter `wing`, `room`;
Nexus-Wings: `YYYYMM`, Stream-Wings: Projekt-Slug). Pflicht vor Aussagen über vergangene
Arbeit, Projekte oder Entscheidungen sowie bei Unsicherheit über Fakten.

---

## Schreiben

Schreibziel ist immer Nexus: `mempalace_add_drawer(wing, room, content)` bei Entscheidungen
und Erkenntnissen mit bleibendem Wert, Projektkontextänderungen und Korrekturen mit Wirkung
über die aktuelle Aufgabe hinaus.

Pflicht-Checkliste:
1. `mempalace_check_duplicate` — Duplikat gefunden → vorhandenen Drawer referenzieren
2. Inhalt in AAAK-Syntax (Spec liefert `mempalace_status`); Drawers sind unveränderlich
3. `wing` = `YYYYMM` des aktuellen Monats, `room` = beschreibender Slug (z. B. `decisions`)

---

## Fehlerverhalten

- MCP-Server nicht erreichbar → sichtbaren Hinweis ausgeben, nicht still übergehen
- Leerer Palace beim ersten Start → erwartet, kein Fehler
