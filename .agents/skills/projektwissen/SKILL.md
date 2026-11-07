---
name: projektwissen
description: Löst aus einem Maestro-Projekt den Dokumentationseinstieg auf, liest zuerst das Einstiegsdokument und lädt danach ausschließlich die für die konkrete Aufgabe benötigten Detaildokumente. Verwenden bei Projektarbeit, sobald ein Maestro-Projektkontext vorliegt.
---

# Skill: projektwissen

Allgemeiner Navigations- und Lesemechanismus für die nach `projektdoku-standard` erzeugte
Projektdokumentation. Reiner Lesemechanismus — verändert die Dokumentation nicht.

## Ablauf

1. **Projektkontext verwenden**
   Liegt bereits ein vollständiger Maestro-Projektrecord im aktuellen Arbeitskontext vor,
   wird dieser verwendet. Andernfalls wird das aktuelle Projekt über die bestehende
   Projektauflösung des `maestro-tracking` bestimmt.

2. **Dokumentationseinstieg bestimmen**
   `project_directory` über den bestehenden Echo-Maestro-Mechanismus
   (`maestro_client.project_directory()`), `docs_entry_path` aus dem Maestro-Projektrecord.
   Effektiver Einstieg: `<project_directory>/<docs_entry_path>`.

   Ist `docs_entry_path` am Projekt nicht gesetzt, wird dieser Zustand konkret benannt. Der
   Agent arbeitet dann auf Basis der vorhandenen Projektquellen weiter und kann bei einem
   Dokumentationsauftrag den `document-project`-Workflow verwenden.

3. **Einstiegsdokument laden**
   Ist der Inhalt des Einstiegsdokuments bereits durch `onboarding.py` im Sitzungskontext
   vorhanden (bei einem dauerhaft fokussierten Projekt), wird dieser vorhandene Inhalt
   verwendet — kein erneutes Lesen. Andernfalls wird `overview.md` gelesen.

4. **Informationsbedarf aus der Aufgabe bestimmen**
   Die konkrete Aufgabe den im Overview verlinkten Projektbereichen, Dokumenttypen und
   Fachbegriffen zuordnen.

5. **Detaildokumente selektiv laden**
   - Concepts, wenn ein mentales Modell oder eine Architekturbeziehung benötigt wird.
   - Workflows, wenn eine konkrete projektinterne Tätigkeit ausgeführt werden soll.
   - References, wenn exakte Parameter, Strukturen, Konfigurationen oder Schnittstellen
     benötigt werden.
   - Decisions, wenn eine Architektur- oder Constraint-Begründung für die aktuelle Änderung
     relevant ist.
   - `glossary.md` bei unbekannten oder projektspezifisch definierten Begriffen.

6. **Quellenbezug prüfen**
   Hängt eine konkrete Implementierungsentscheidung von einem in der Dokumentation
   zusammengefassten technischen Detail ab, wird die dort ausgewiesene autoritative Quelle
   gelesen.

7. **Mit dem belegten Projektmodell arbeiten**
   Die gelesene Dokumentation dient als Navigations- und Verständnisebene für die aktuelle
   Aufgabe.

## Rangfolge bei Widerspruch

1. Projektdokumentation zur Navigation und zum mentalen Modell verwenden.
2. Die im Dokument ausgewiesene autoritative Quelle lesen, wenn die konkrete Aufgabe von
   einem technischen Detail abhängt.
3. Bei einem Widerspruch den aktuellen Zustand aus der für dieses Thema autoritativen
   Quelle bestimmen.
4. Den Widerspruch als Dokumentationsbedarf behandeln (→ Skill: `document-project`,
   Modus MAINTAIN).

## Pflichtregeln

- MUSS GELTEN: Der Skill liest standardmäßig nicht den gesamten Dokumentationsbaum,
  sondern folgt dem Einstiegspunkt und den für die Aufgabe benötigten Verweisen.
- MUSS GELTEN: Ein bereits im Sitzungskontext vorhandenes Einstiegsdokument wird nicht
  erneut gelesen.
