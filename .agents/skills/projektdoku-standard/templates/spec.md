# projektdoku-standard — Verbindliche Spezifikation

## Ablageort und Ordnerstruktur

`<slug>` ist für Maestro-Projekte deren `ucid`. Der Pfad ist relativ zum `project_directory`
des dokumentierten Maestro-Projekts zu verstehen.

```
docs/knowledge/projects/<slug>/agents/
  overview.md          ← Pflicht; kein type-Feld
  glossary.md          ← Pflicht; kein type-Feld
  concepts/
    [<domain>/]        ← optionale Domain-Ebene (eine Ebene max.)
      <slug>.md
  workflows/
    [<domain>/]
      <slug>.md
  reference/
    [<domain>/]        ← Domain-Ebene empfohlen bei heterogenem Inhalt
      <slug>.md
  decisions/           ← optional; nur bei dokumentationswürdigen Architekturentscheidungen
    YYYY-MM-DD-<slug>.md
  legacy/              ← optional; veraltete Dokumente mit status: deprecated
    <slug>.md
```

Dateinamen: kebab-case, keine Nummerierung.

## Dokumenttypen

| Typ | Frage | Agent liest ihn wenn... |
|---|---|---|
| concept | Was ist X und warum existiert es so? | Er das mentale Modell noch nicht hat |
| workflow | Wie erledige ich Aufgabe X? | Er konkret etwas tun will |
| reference | Was sind die exakten Felder/Parameter von X? | Er präzise Details braucht |
| decision | Warum wurde X so gebaut? | Er eine Constraint verstehen muss |

## Interne Dokumentstruktur

| Typ | Pflichtabschnitte |
|---|---|
| concept | Kurzbeschreibung · Worum geht es · Wann/warum relevant · Kerninhalt · Bezüge |
| workflow | Zweck · Voraussetzungen · Schritte · Ergebnis · Häufige Fehler |
| reference | Definition · Felder/Parameter-Tabelle · Einschränkungen · Minimalbeispiel |
| decision | Kontext · Optionen · Entscheidung · Konsequenzen |

## Frontmatter-Schema

```yaml
---
type: concept|workflow|reference|decision  # Pflicht (außer overview.md und glossary.md)
id: <kebab-case>                            # Pflicht; eindeutig im Projekt
title: <Titel>                              # Pflicht
last_updated: YYYY-MM-DD                   # Pflicht
last_verified: YYYY-MM-DD                  # Pflicht für overview, glossary, concept, workflow, reference, decision
keywords: []                               # optional; Sucheinstieg
related: []                                # optional; Pfadliste für maschinenlesbare Querverweise
read_if: ""                                # optional; Aktivierungshinweis
do_not_read_if: ""                         # optional; Ausschlusshinweis
file_path: []                              # optional; Quelldatei(en) als Liste
status: deprecated                         # optional; Pflicht für Dateien in legacy/
---
```

`overview.md` und `glossary.md` verwenden kein `type`-Feld.

`last_updated` bezeichnet die letzte inhaltliche Änderung am Dokument. `last_verified`
bezeichnet das Datum, an dem der Inhalt zuletzt gegen seine maßgeblichen Projektquellen
geprüft wurde — beide Felder werden unabhängig voneinander gepflegt.

## Dateiorganisation

- Flach oder eine Domain-Ebene je Typ — harte Regel; keine tiefere Verschachtelung.
- `reference/` darf zusätzlich eine weitere Ebene haben (z. B. `entities/`, `configuration/`).
- `decisions/` immer mit Datum-Präfix: `YYYY-MM-DD-<slug>.md`.

## Querverlinkung

Inline-Markdown-Links für inhaltliche Verweise. `related`-Frontmatterfeld nur wenn der
Querverweis maschinenlesbar sein muss.

## Splitting-Regel

Ein Dokument beschreibt eine Zuständigkeit. Deckt ein Dokument zwei unabhängige Konzepte
oder zwei unabhängige Workflows ab, wird es aufgeteilt.

## Rollentrennung

| Skill | Aufgabe |
|---|---|
| `project-survey` | Projektverzeichnis erkunden, Ist-Zustand erfassen — kein Doku-Output |
| `projektdoku-standard` | Zielstruktur kennen und anwenden; `overview.md` ist Pflicht-Output des Initialsurveys |
