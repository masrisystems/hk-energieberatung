# Analyse-Schemata

Einheitliche Dokumentenstruktur für alle Ausgaben der Analysis-Rolle.
Kein Agent darf eigene abweichende Formate einführen.

Ablageort für alle Analysedokumente: `docs/analysis/`
Quellenstandard: `.agent/skills/source-citation/SKILL.md`

---

## Meta-Block (Pflicht in jedem Analysedokument)

```markdown
## Meta
- **Projekt:**        [Projektname]
- **Dokument:**       [Dokumenttyp]
- **Analysiert am:**  YYYY-MM-DD
- **Agent:**          [Agent-Name]
- **Quellregister:**  `docs/analysis/source-registry.md`
- **Status:**         draft | in-review | final
- **Letzte Änderung:** YYYY-MM-DD
```

---

## 1. Projektübersicht (`project-overview.md`)

```markdown
# Projektübersicht: [Projektname]

[Meta-Block]

## Zweck und Problemstellung
<!-- Was ist das Kernproblem, das dieses Projekt löst? Für wen? -->

## Zielgruppe
<!-- Wer nutzt das System? Welche Rollen gibt es? -->

## Kernanforderungen
<!-- Was muss das System leisten? (aus Anforderungsdokumenten oder Code erschlossen) -->

## Funktionsumfang (Überblick)
<!-- Hauptfunktionsbereiche — keine Feature-Liste, nur Domänen -->
<!-- Details: feature-catalog.md -->

## Technologiestack
| Schicht | Technologie | Version | Quelle |
|---------|------------|---------|--------|
| Backend | | | [Q:XXX] |
| Frontend | | | [Q:XXX] |
| Datenbank | | | [Q:XXX] |
| Deployment | | | [Q:XXX] |

## Systemgrenzen
<!-- Was gehört zum System, was liegt außerhalb? -->
<!-- Externe Systeme, APIs, Dienste — Details: dependency-map.md -->

## Bekannte Einschränkungen und Besonderheiten
<!-- Auffälligkeiten, bekannte technische Schulden, ungewöhnliche Entscheidungen -->

## Offene Fragen
<!-- Was konnte nicht vollständig belegt werden? -->
- [ ] [OFFEN] Begründung
```

---

## 2. Feature-Katalog (`feature-catalog.md`)

```markdown
# Feature-Katalog: [Projektname]

[Meta-Block]

## Übersicht der Domänen
<!-- Kurze Auflistung aller dokumentierten Domänen mit Zeilenverweis -->

---

## Domäne: [Domänenname]

### Feature: [Featurename]

- **Beschreibung:** [Was macht dieses Feature?] [BELEGT/SCHLUSSFOLGERUNG/VERMUTET/OFFEN]
- **Einstiegspunkt:** `[Pfad/Datei]` [Q:XXX]
- **Verhalten:**
  - [Schritt oder Aspekt] [Q:XXX]
  - [Schritt oder Aspekt] [Q:XXX]
- **Abhängigkeiten:** [andere Features, externe Systeme]
- **Bekannte Sonderfälle:** [Edge Cases, die im Code explizit behandelt werden] [Q:XXX]
- **Offene Fragen:** [Was ist unklar?]

<!-- Weitere Features der Domäne folgen demselben Schema -->
```

---

## 3. Architektur (`architecture.md`)

```markdown
# Architektur: [Projektname]

[Meta-Block]

## Architekturmuster
<!-- Welches Muster liegt vor? (MVC, Hexagonal, Monolith, Microservices, ...) -->
[BELEGT/SCHLUSSFOLGERUNG] [Q:XXX]

## Schichten / Layering
<!-- Wie ist das System vertikal aufgeteilt? -->

## Komponenten

### [Komponentenname]
- **Verantwortlichkeit:** [Q:XXX]
- **Technologie / Framework:**
- **Ort im Projekt:** `[Pfad]`
- **Schnittstellen nach außen:**
  - Konsumiert: [andere Komponente]
  - Stellt bereit: [andere Komponente]
- **Besonderheiten:**

<!-- Weitere Komponenten folgen demselben Schema -->

## Datenfluss

### [Flussname, z.B. "Bestellprozess"]
```
[Komponente A] → [Komponente B] → [Komponente C]
```
[Beschreibung des Flusses] [Q:XXX]

## Querschnittsthemen
<!-- Auth, Logging, Error Handling, Caching — wie ist das gelöst? -->

## Architekturentscheidungen
<!-- Warum wurden bestimmte Entscheidungen getroffen? (wenn aus Code/Docs erschließbar) -->

## Offene Fragen
```

---

## 4. Datenmodell (`data-model.md`)

```markdown
# Datenmodell: [Projektname]

[Meta-Block]

## Überblick
<!-- Welche Datenbanktypen? Wie viele zentrale Entitäten? -->

## Entitäten

### [Entitätsname]
- **Tabelle / Collection:** `[name]` [Q:XXX]
- **Beschreibung:** [Wofür steht diese Entität?]
- **Attribute:**
  | Feld | Typ | Pflicht | Beschreibung | Quelle |
  |------|-----|---------|--------------|--------|
  | `id` | int | ja | Primärschlüssel | [Q:XXX] |
- **Relationen:**
  | Relation | Typ | Ziel-Entität | Details | Quelle |
  |----------|-----|-------------|---------|--------|
- **Besonderheiten / Constraints:**

## Übergreifende Datenbankkonventionen
<!-- Naming, Timestamps, Soft Deletes, etc. -->
```

---

## 5. API-Katalog (`api-catalog.md`)

```markdown
# API-Katalog: [Projektname]

[Meta-Block]

## Überblick
<!-- REST / GraphQL / RPC? Versionierung? Auth-Mechanismus? -->

## Endpunkte

### [HTTP-Methode] [/pfad]
- **Zweck:** [Q:XXX]
- **Authentifizierung:** [keine | Bearer | Session | ...]
- **Request:**
  - Parameter: `[param]` ([Typ], [Pflicht?]) — [Beschreibung]
  - Body:
    ```json
    { "beispiel": "struktur" }
    ```
- **Response (Erfolg):**
  ```json
  { "beispiel": "antwort" }
  ```
- **Response (Fehler):** [HTTP-Status] — [Bedeutung]
- **Quelle:** [Q:XXX]

<!-- Weitere Endpunkte folgen demselben Schema -->
```

---

## 6. Abhängigkeiten (`dependency-map.md`)

```markdown
# Abhängigkeiten: [Projektname]

[Meta-Block]

## Externe Pakete

| Paket | Version | Zweck | Kritisch | Quelle |
|-------|---------|-------|----------|--------|
| [Name] | [Version] | [Beschreibung] | ja/nein | [Q:XXX] |

## Externe Systeme und Integrationen

| System | Art | Zweck | Quelle |
|--------|-----|-------|--------|
| [Name] | API / Dienst / DB / ... | [Beschreibung] | [Q:XXX] |

## Interne Paket-Abhängigkeiten
<!-- Sub-Repos, Vendor-Pakete, eigene Libraries -->

## Bekannte Risiken
<!-- Veraltete Abhängigkeiten, fehlende Updates, Security-relevantes -->
```

---

## 7. Quellregister (`source-registry.md`)

```markdown
# Quellregister: [Projektname]

## Meta
- **Projekt:** [Projektname]
- **Erstellt am:** YYYY-MM-DD
- **Letzte Aktualisierung:** YYYY-MM-DD
- **Gesamtquellen:** [Anzahl]

---

## Quellen

### Q001
- **Pfad:** `[relativer/pfad/zur/datei.ext]`
- **Zeilen:** [von]–[bis]  *(oder: gesamte Datei)*
- **Abgerufen:** YYYY-MM-DD HH:MM
- **Snapshot:**
  ```[sprache]
  [Inhalt zum Zeitpunkt des Abrufs]
  ```
- **Verwendet in:** [dokument.md (Abschnitt)], [dokument2.md]
- **Änderungslog:**
  | Datum | Art | Details | Dokumente geprüft |
  |-------|-----|---------|-------------------|
  | *(leer bei Erstanlage)* | | | |

---

## Änderungslog (Übersicht)

| Datum | Quellen-ID | Art der Änderung | Details |
|-------|-----------|-----------------|---------|
```

---

*Logbuch-Status für Analysedokumente:* `draft` | `in-review` | `final`
*Belegkennzeichnungen:* `[BELEGT]` · `[SCHLUSSFOLGERUNG]` · `[VERMUTET]` · `[OFFEN]`
