---
name: release-vorbereitung
description: Bestimmt für eine angegebene Version die vollständige Release-Menge, prüft ihre Abschlussartefakte, legt Changelog-Einträge an, schließt release-fähige Tickets ab und erstellt den Release-Branch. Use when ein Release für ein Projekt und eine Version vorbereitet werden soll.
---

# Skill: Release-Vorbereitung

Eigenständig ladbar — der Workflow `release-vorbereitung` ordnet diese Schritte den Aufrufen
von `echo-maestro` (`maestro-access`), `gitlab-integration` und Git zu.

## Aufruf

Verlangt: Projekt, Release-Version.

## Schritt 1 — Version normalisieren

```bash
python3 .agent/skills/release-vorbereitung/tools/release_utils.py normalize_version "<eingabe>"
```

- Entfernt ein führendes `v`, prüft auf vollständige Semantic Version
  (`MAJOR.MINOR.PATCH`) und bricht bei unvollständigem oder nicht-numerischem Wert mit
  Fehler ab — kein Rundungsversuch.
- Der normalisierte Wert wird für Milestone-Abgleich, Maestro-`versions`-Record und
  Branchname einheitlich verwendet.

## Schritt 2 — Maestro-Version auflösen

- Innerhalb des Projekts über normalisierte `major`/`minor`/`patch`-Werte suchen
  (`maestro_list(archetype="versions", filters={project, major, minor, patch})`).
- Mehrere passende Records: Fehler, keine automatische Zusammenführung.
- Kein passender Record: spätere Anlage mit diesen Werten im Prüfbericht vormerken —
  der Record entsteht erst nach Schritt 5 (bestandene Prüfung der gesamten Release-Menge).

## Schritt 3 — Milestones auflösen

Quelle richtet sich nach `ticket_system` in `.agent/config.json` des Zielprojekts:

- **`gitlab`:** alle Projekt-Milestones (`gitlab-integration list_milestones`).
- **`maestro`:** alle Milestone-Records des Projekts (`maestro_list(archetype="milestones",
  filters={project})`).
- **`internal`:** `list_milestones(project)` (→ `echo-artifacts/milestones`).

In allen drei Fällen: ausdrücklich übergebene Milestones werden unverändert übernommen.
Ohne ausdrückliche Angabe: alle so ermittelten Milestones, deren Name (`gitlab`: `title`;
`maestro`: `name`; `internal`: Feld `milestone`) die vollständige Versionsangabe als
eigenständigen Bestandteil enthält:
```bash
python3 .agent/skills/release-vorbereitung/tools/release_utils.py milestone_matches "<milestone_name>" "<version>"
```
z. B. `2.4.12`, `v2.4.12`, `Release v2.4.12`, `Diverses 2.4.12` passen zu `2.4.12`;
`2.4.1` passt nicht zu `2.4.12`.

Gewählte Milestones vor der Prüfung ausgeben.

## Schritt 4 — Release-Menge bilden

Je gewähltem Milestone die zugehörigen Tickets laden:

- **`gitlab`:** `gitlab-integration get_milestone_issues "<milestone_title>"` (vollständig
  paginiert).
- **`maestro`:** Maestro-Relation `milestones → tickets`.
- **`internal`:** Ticket-Referenzen aus dem Abschnitt `## Tickets` des von
  `view_milestone(project, milestone)` gelieferten Inhalts (→ `echo-artifacts/milestones`).

Vereinigungsmenge über die Ticket-ID bilden (`release_utils.dedupe_tickets` bei
skriptgestützter Zusammenführung mehrerer Listen). Vollständige Ticketliste vor der Prüfung
ausgeben.

## Schritt 5 — Release-Fähigkeitsprüfung

Für jedes Ticket der Release-Menge laden:
- Ticketbeschreibung und strukturierte Ticketfelder — bei `internal` `view_ticket(project,
  ticket)` (→ `echo-artifacts/tickets`; Anforderungen, Akzeptanzkriterien gelten als deren
  eigene Belegquelle; es gibt keine separate Kommentarebene),
- verknüpfte Implementierungspläne und Walkthroughs (bei `internal`:
  `list_implementation_plans`/`view_implementation_plan` und
  `list_walkthroughs`/`view_walkthrough`, → `echo-artifacts/implementation-plans`,
  `echo-artifacts/walkthroughs`; sonst Maestro-Relationen),
- Kommentare/Notes aus dem Ursprungssystem bei `gitlab` (`gitlab-integration
  get_issue_full <iid>`) und `maestro` (Maestro-Notiz-Relationen),
- verknüpfte Commit- und Testangaben als Belege.

Prüfergebnis je Ticket — ausschließlich beleggebunden, keine Annahme ohne Fundstelle:
- `release-fähig`: Todos geschlossen, Walkthrough- und Commit-Referenz vorhanden.
- `nicht release-fähig`: mindestens eine der Voraussetzungen fehlt oder ein offener
  Arbeitspunkt ist dokumentiert.

Ergebnis enthält je Ticket ausschließlich die dafür relevanten Belege und den Wert.

**Abbruchregel:** Sobald ein Ticket `nicht release-fähig` ist, endet der Skill nach Ausgabe
des vollständigen Prüfberichts. Bis dahin: keine Versionsanlage, keine Changelog-Einträge,
keine Änderung an Bearbeitern, Status, Labels, Ticketzuständen oder Branches.

## Schritt 6 — Changelog-Einträge (nur bei bestandener Gesamtprüfung)

- Vorhandene, bereits mit der Version und dem jeweiligen Ticket verknüpfte
  `version-changes`-Records laden (Feldbeschreibung: `maestro_skill(archetype="version-changes")`).
  Für eine bereits erfasste Änderung entsteht kein zweiter Eintrag.
- Für jede tatsächlich enthaltene Änderung eines release-fähigen Tickets einen
  `version-changes`-Record anlegen mit:
  - Relation zu Ticket und normalisierter Maestro-Version,
  - Relation zu Implementierungsplan und Walkthrough, sofern vorhanden,
  - `category` als fachlich passende Überschrift (z. B. `Allgemein`,
    `Fehlerbehebungen`, konkret betroffener Produktbereich),
  - `group`: `user`, `admin`, `tech` oder `all` — entwicklerbezogene Änderungen als `tech`,
  - `text_line`: knappe, verständliche Beschreibung.

## Schritt 7 — Abschlusssequenz

Reihenfolge für alle Tickets der Release-Menge:
1. Vorgemerkten `versions`-Record anlegen, sofern er fehlt (Schritt 2); Changelog-Einträge
   aus Schritt 6 anlegen bzw. vervollständigen.
2. Alle Bearbeiter entfernen — `gitlab-integration clear_assignees <iid>` bei `gitlab`,
   Maestro-Relation `assignees` lösen bei `maestro`; bei `internal` entfällt dieser Schritt
   (Ticketdatei kennt kein Assignee-Feld, nur `Verantwortlich`, das die Umsetzung dokumentiert
   und bestehen bleibt).
3. Status setzen: `DONE` in Maestro (falls das Projekt Maestro nutzt), Label `Done` in
   GitLab bei `ticket_system: gitlab`; bei `internal` das Meta-Feld `Status:` auf `done`.
4. Ticket im jeweils führenden System abschließen — bei `internal` die Ticketdatei nach
   `docs/tickets/completed/` verschieben (→ `echo-artifacts/tickets`); vorhandenen verknüpften
   Ticketstand im anderen System nachziehen.
5. Release-Branch erstellen (`release_utils.branch_name` liefert `release/<normalisierte-version>`) — Basis ist der aktuelle
   `develop`-Stand des verifizierten Projekt-Repositories. Vor dem ersten schreibenden
   Schritt dieses Punkts prüfen: Arbeitsbaum ohne nicht zugeordnete Änderungen,
   `release/<normalisierte-version>` existiert noch nicht. Kein Push.

**Fehlerregel:** Schlägt eine einzelne Operation dieser Sequenz fehl, stoppt der Skill an
dieser Stelle. Ausgabe: Ticket, Zielsystem, Operation, unveränderte Fehlermeldung, sowie
Liste der bis dahin bereits erfolgreich ausgeführten Operationen.

## Referenzen

- Deterministische Hilfsfunktionen (Versionsnormalisierung, Milestone-Namensabgleich,
  Dedup, Branchname): `tools/release_utils.py`.
- Write-Mechanik, Abrufarten, Feldlagen: `echo-maestro/maestro-access`.
- GitLab-Befehle: `gitlab-integration` (`get_milestone_issues`, `get_issue_full`,
  `clear_assignees`, `update_issue`, `list_milestones`).
- Archetype-Felder: `maestro_skill(archetype="milestones"|"versions"|"version-changes")`.
- Milestones bei `ticket_system: internal`: `echo-artifacts/milestones`.
- Ticket-Systemwahl: `echo-artifacts/tickets/ticketing-config.md`.
