---
name: projektdoku-standard
description: Definiert und wendet den Projektdokumentations-Standard des Echo-Frameworks an. Verwenden, wenn Projektdokumentation nach dem Diataxis-Schema angelegt, erweitert oder geprüft werden soll.
---

# projektdoku-standard

## Zweck

Dieser Skill beschreibt die verbindliche Struktur für KI-agententaugliche Projektdokumentation
im Echo-Framework. Er wird aktiviert, wenn Dokumentation angelegt, erweitert oder migriert wird.

Die vollständige Spezifikation (Ablageort, Frontmatter-Schema, Splitting- und Verlinkungsregeln)
steht in `templates/spec.md`.

## Navigation: Wie ein Agent in die Doku einsteigt

1. `overview.md` lesen — Projektzweck, Stack, Hauptbereiche
2. Je nach Bedarf in den passenden Typ-Ordner navigieren:
   - Mentales Modell fehlt → `concepts/`
   - Konkrete Aufgabe → `workflows/`
   - Exakte Parameter/Felder → `reference/`
   - Constraint verstehen → `decisions/`
3. Unbekannter Begriff → `glossary.md`

## Dokumenttypen

| Typ | Frage | Pflichtabschnitte |
|---|---|---|
| concept | Was ist X und warum? | Kurzbeschreibung · Worum geht es · Wann/warum relevant · Kerninhalt · Bezüge |
| workflow | Wie erledige ich X? | Zweck · Voraussetzungen · Schritte · Ergebnis · Häufige Fehler |
| reference | Welche Felder hat X? | Definition · Felder/Parameter-Tabelle · Einschränkungen · Minimalbeispiel |
| decision | Warum so gebaut? | Kontext · Optionen · Entscheidung · Konsequenzen |

`overview.md` und `glossary.md` folgen eigenen Templates; kein `type`-Feld.

## Initialsurvey-Pflicht

Nach jedem `project-survey` entsteht als Pflicht-Output `overview.md`. Kein anderes
Dokument wird angelegt bevor `overview.md` existiert.

## Templates

| Datei | Verwendung |
|---|---|
| `templates/spec.md` | Verbindliche Spezifikation (Ablageort, Frontmatter, Regeln) |
| `templates/overview.md` | Einstiegsdokument |
| `templates/glossary.md` | Schlüsselbegriffe |
| `templates/concept.md` | Konzept-Dokument |
| `templates/workflow.md` | Workflow-Dokument |
| `templates/reference.md` | Referenz-Dokument |
| `templates/decision.md` | Architekturentscheidung |

## Abgrenzung

| Skill/Workflow | Aufgabe |
|---|---|
| `project-survey` | Ist-Zustand erkunden — kein Doku-Output außer `overview.md` |
| `projektdoku-standard` (dieser Skill) | Struktur kennen und anwenden |
