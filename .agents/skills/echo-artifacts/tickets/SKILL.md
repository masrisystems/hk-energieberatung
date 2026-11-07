---
name: tickets
description: Verwaltet Tickets im Ticket-System eines Projekts. Verwenden bei Ticket-Operationen: erstellen, abschließen, verwerfen, umpriorisieren.
---

# SKILL: Tickets

## Projekt und Ticketsystem auflösen

Zielprojekt-UUID: siehe `echo-maestro/maestro-tracking/SKILL.md`, Abschnitt
„Projekt-Kontext".

**Ausgangspunkt ist ein bereits bekanntes GitLab-Issue** (dessen Projekt-ID bekannt ist):
Ticketkontext ist `gitlab`; Maestro-Projekt über
`maestro_list(archetype="projects", filters={"gitlab_project_id": "<id>"})` auflösen.
Kein Treffer oder mehr als ein Treffer: keine Ticketoperation, den Nutzer auf die
fehlende/mehrdeutige Zuordnung hinweisen.

---

## Schritte: Ticket suchen (vor Erstellung)

Bevor ein neues Ticket angelegt wird, immer suchen:

1. **Kandidaten ermitteln**
   MCP-Tool `list_tickets(project)` aufrufen.

2. **5 passendste Kandidaten auswählen**
   Titel und Kurzinhalt überfliegen; die 5 thematisch nächsten bestimmen.
   Kein plausibler Kandidat → direkt zu Schritt 5.

3. **Kandidaten-Beschreibungen lesen**
   Je Kandidat `view_ticket(project, ticket)` aufrufen und auf Übereinstimmung prüfen.

4. **Passendes Ticket gefunden?**
   Dieses Ticket in Commits referenzieren (`(#ID)`) und Walkthrough oder Zusammenfassung anhängen.

5. **Kein passendes Ticket** → neues Ticket erstellen (Schritte unten).

6. **Multi-Repo:** Tickets über "Linked Items" in GitLab verknüpfen (→ `multi-repo-ticket-workflow.md`).

---

## Schritte: Ticket erstellen

1. **Platzierung entscheiden**
   Bei `ticket_system=internal`: Kriterientabelle in `ticketing-config.md` gegen die
   Aufgabe prüfen, Zielordner `open` oder `backlog` bestimmen. Im Zweifel Nutzer fragen.

2. **Ticket anlegen**
   MCP-Tool `create_ticket` aufrufen — `project` (UUID des Maestro-Projektrecords),
   `title` (max. 5 Wörter), `folder` (Ergebnis von Schritt 1; bei `maestro`/`gitlab`
   ungenutzt, aber Pflichtparameter), `type`, `status`, `responsible` sowie die
   Abschnittsinhalte `context`, `goal`, `requirements`, `acceptance_criteria` und optional
   `risks`, `open_questions`, `references`, `first_approach`.

3. **Commit-Referenz merken**
   Für spätere Commits: `(#NNN) ` als Präfix der Commit-Message (ohne führende Nullen).

4. **Committen**
   ```bash
   .agent/skills/echo-artifacts/tickets/tools/commit-ticket.sh <ticket-datei> <commit-message> <author-name> <author-email>
   ```
   Stagt die Ticket-Datei und committet sie zusammen mit bereits anderweitig gestagten
   Änderungen — Commit-Author und -Format gemäß `repo-rules`.

---

## Schritte: Ticket abschließen (internal)

1. Ticket-Datei in `completed/` verschieben (ZWINGEND)
2. Im Ticket-Meta: Status auf `done` setzen, Abschlussdatum eintragen

---

## Schritte: Ticket wiedereröffnen (internal)

Gilt für ein Ticket in `completed/`, dessen Umsetzung fehlerhaft ist:

1. Stand des betroffenen Codes ermitteln und benennen
2. Ticket-Datei nach `open/` verschieben (ZWINGEND)
3. Ticket-Meta: Status auf `revise` setzen
4. Den Mangel im Ticket benennen und beheben; der übrige Inhalt bleibt unverändert
5. Ticket-Meta: Status auf `approved` setzen
6. Weiteren Implementierungsplan für die Korrektur erstellen (→ Skill:
   echo-artifacts/implementation-plans)

---

## Schritte: Ticket verwerfen (internal)

1. Vor dem Verschieben: `## Begründung`-Abschnitt im Ticket ergänzen
   - Warum wird das Ticket verworfen?
   - (Duplikat → Referenz auf anderes Ticket | Kein Fehler → kurze Erklärung | ...)
2. Ticket-Meta: Status auf `discarded` setzen
3. Datei nach `<ticket_path>/discarded/` verschieben (ZWINGEND)

---

## Schritte: Fehlanlage löschen (internal)

Gilt für ein fehlerhaft angelegtes Ticket — keine Alternative zum Verwerfen, sondern die
Korrektur eines Anlagefehlers.

1. Fehlanlage dem Nutzer benennen und explizite Bestätigung einholen, dass es sich um eine
   Fehlanlage handelt
2. Ticket-Datei per `git rm` entfernen
3. Commit mit Bezug auf die entfernte Ticketnummer

---

## Schritte: Ticket zurückweisen (internal)

Gilt für ein Ticket in `proposed`, dessen Idee abgelehnt wird.

1. Vor dem Verschieben: `## Begründung`-Abschnitt im Ticket ergänzen
   - Warum wird die Idee abgelehnt?
   - Die Begründung trägt die Entscheidungsgrundlage, auf die eine spätere
     Wiedervorlage trifft
2. Ticket-Meta: Status auf `rejected` setzen
3. Datei nach `<ticket_path>/discarded/` verschieben (ZWINGEND)

---

## Pflichtregeln

- MUSS GELTEN: Ticket-Invarianten (IDs, Lebenszyklus, Begründungspflicht) folgen dem Regelmodul `ticket-rules`.
- MUSS GELTEN: Das erstellte Ticket enthält alle Pflichtabschnitte des Templates.
- MUSS GELTEN: Bestehende Ticket-Inhalte minimal-invasiv bearbeiten — Template-Abschnitte hinzufügen, besprochene Korrekturen eintragen, Originaltext sonst unverändert.
- MUSS GELTEN: Bei `ticket_system = internal` gilt eine Ticketdateiänderung — Erstellung,
  Korrektur, Statuswechsel, Verschiebung, Referenznachtrag — erst mit dem zugehörigen
  Commit als abgeschlossen, nicht bereits mit dem Speichern der Datei.