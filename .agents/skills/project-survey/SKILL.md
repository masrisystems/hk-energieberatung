---
name: project-survey
description: Erkundet initial ein unbekanntes Projekt in der Breite — Struktur, Stack, Einstiegspunkte — und liefert ein belastbares Lagebild als Basis für Folgephasen. Verwenden zu Beginn einer Projektanalyse.
---

# SKILL: Project Survey

## Schritte

1. **Einstiegspunkte lesen**
   In dieser Reihenfolge, soweit vorhanden:
   - `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
   - `package.json` / `composer.json` / `pyproject.toml` / äquivalent
   - `docker-compose.yml`, `.env.example`, CI-Konfiguration
   - Vorhandene Dokumentation unter `docs/`

   Bei Einsatz mit `document-project` zusätzlich gezielt für das erweiterte
   `overview.md`-Template ermitteln: Projektumfang und Verantwortungsbereich, Architektur,
   Repository-Aufbau, Voraussetzungen, Daten und Persistenz, Integrationen,
   projektspezifische Konventionen, autoritative Quellen je Thema.

2. **Verzeichnisstruktur kartieren**
   Top-Level-Verzeichnisse und ihre erkennbare Funktion festhalten.
   Tiefer nur dort, wo die Struktur unklar ist.

3. **Stack und Abhängigkeiten identifizieren**
   Aus Dependency-Dateien: Hauptpakete, Versionen, erkennbare Architekturmuster.

4. **Einstiegspunkte der Anwendung finden**
   Wo startet die Anwendung? Wo sind Routen oder Controller definiert?

5. **Vorläufige Übersicht notieren**
   Strukturierte Notizen für Folgephasen — noch kein Dokument.

6. **Lücken und Unklarheiten benennen**
   Was konnte nicht aus vorhandenen Quellen erschlossen werden?

7. **Nutzer informieren**
   Kurze Zusammenfassung: Was wurde verstanden? Was ist noch offen?
   Auf Bestätigung warten, bevor Folgephasen beginnen.

## Pflicht-Output bei Einsatz mit `document-project`

`overview.md` nach `projektdoku-standard/templates/overview.md` entsteht am Ende des
Surveys — Voraussetzung bevor der erste DRAFT-Todo im `document-project`-Workflow angelegt wird.

## Pflichtregeln

- MUSS GELTEN: Jedes Verzeichnis wird zunächst in der Breite erkundet; Tiefenanalyse erst in Folgephasen.
- MUSS GELTEN: Jeder erfasste Fakt hat sofort einen Quelleintrag (→ Skill: source-citation).
- MUSS GELTEN: Jede Aussage über die Projektstruktur ist durch Lesen belegt.
