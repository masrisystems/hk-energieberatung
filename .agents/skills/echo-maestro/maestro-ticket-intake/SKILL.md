---
name: maestro-ticket-intake
description: >
  Verarbeitet eine injizierte Ticket-Anfrage: prüft Projekt-Konsistenz, gleicht gegen
  Duplikate und Projekt-Code ab, legt ein Maestro-Ticket an oder ergänzt ein bestehendes
  und weist es dem anfragenden Nutzer zu. Laden wenn ein [TICKET-INTAKE]-Marker im Kontext
  erscheint.
---

# Skill: maestro-ticket-intake

## Eintrittsgate

**Kein Ticket ohne identifizierbares Projekt.**

Ist kein Projekt eindeutig bestimmbar — weder aus dem injizierten Kontext noch aus dem
Gesprächskontext — an den anfragenden Nutzer zurückfragen. Nicht raten, kein Default-Projekt.

## Hook-Vertrag: injizierte Felder

Ein externer Trigger injiziert `[TICKET-INTAKE]` mit folgenden Feldern in den Prompt:

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `nutzer` | ja | Anfragender Nutzer (vom System gesetzt) |
| `projekt` | nein | Projektkontext (sofern bekannt) |
| `typ` | nein | Bug / Feature / Doku / Chore / … |
| `beschreibung` | ja | Freitext des Anliegens |

## Ablauf

### Schritt 1 — Anfrage lesen

Injizierte Felder aus dem Kontext extrahieren: Nutzer, Projekt, Typ, Beschreibung.
Fehlt `beschreibung`: Rückfrage, kein Weitermachen.

### Schritt 2 — Projekt-Konsistenz prüfen

Maestro-Projekte abrufen (`maestro_list` / `maestro_skill(archetype="projects")`).
Prüfen ob das genannte Projekt zur Beschreibung passt.
Bei Diskrepanz: Befund an den Nutzer melden — **nicht still korrigieren**.

### Schritt 3 — Duplikat- und Ergänzungsprüfung

Offene Tickets des Projekts abrufen (gefiltert nach `status=PROPOSED,DOING,REVIEW`,
`per_page` klein halten). Beschreibung gegen diese Tickets abgleichen:
- Trifft die Beschreibung ein bestehendes Ticket → Ergänzungstext formulieren, kein Duplikat anlegen
- Kein Match → neue Ticket-Beschreibung entwerfen

### Schritt 4 — Code-Abgleich

Repo-Pfad des Projekts aus Maestro oder Kontext ermitteln.
Reihenfolge:
1. Projektdokumentation lesen (sofern vorhanden, z.B. `AGENTS.md` / `docs/`)
2. Relevante Code-Stellen lesen — tief genug für eine verlässliche Ersteinschätzung
Beschreibungstext auf dieser Basis erstellen oder in bestehendes Ticket einarbeiten.

### Schritt 5 — Ticket anlegen oder ergänzen

**Neu:** `maestro_create(archetype="tickets")` mit `status=PROPOSED`, Pflichtfeldern aus
`maestro_skill(archetype="tickets")` und strukturierten Feldern (context, goal, requirements).

**Ergänzung:** `maestro_update` auf bestehendes Ticket, Ergänzungstext in passendes Feld.

Zuweisung: anfragenden Nutzer als Assignee setzen (Identity via `identities`-Archetype).
Kein autonomes Schließen, Freigeben oder Abarbeiten — nur Anlage/Ergänzung + Zuweisung.

## Abgrenzung

- Feldschemata und Enum-Werte kommen aus `maestro_skill` / `maestro-access` — nicht hier wiederholen
- Allgemeines Maestro-Zugriffmodell: `maestro-access`
