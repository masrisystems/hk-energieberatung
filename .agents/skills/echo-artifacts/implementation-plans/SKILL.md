---
name: implementation-plans
description: Erstellt einen strukturierten Implementierungsplan, prüft seine Umsetzungsreife und legt ihn dem Nutzer zur Freigabe vor. Verwenden vor jeder Implementierung.
---

# SKILL: Implementation Planning

## Schritte

1. **Kontext verstehen**
   MCP-Tool `view_ticket(project, ticket)` aufrufen. Existiert kein Ticket: erst eines anlegen oder vorschlagen (→ Skill: echo-artifacts/tickets).

2. **Ausgangslage erfassen**
   Relevante Teile des Systems lesen, um den Ist-Zustand zu verstehen.

3. **Plan formulieren**
   Inhalt der Abschnitte Ausgangslage, Umsetzungsziel, Betroffene Bereiche, Ansatz und
   Verifikationsplan bestimmen. Der Verifikationsplan beschreibt eine Entwicklungsprüfung —
   automatisierte Tests, statische Prüfungen oder lokal reproduzierbare Prüfschritte anhand
   der konkret betroffenen Dateien, Zustände, Datenflüsse und Ausführungspfade. Keine
   Nutzer-, Abnahme-, Live-, Datenbank- oder Produktionsprüfung.

4. **Plan anlegen**
   MCP-Tool `create_implementation_plan` aufrufen — `project` (UUID des
   Maestro-Projektrecords), `ticket`, `title` sowie `initial_situation`,
   `implementation_goal`, `affected_areas`, `approach` und `verification_plan`.
   Logbuch-Eintrag: `Erstellt`.

5.5 **Umsetzungsreif-Gate** (vor Plan-Vorlage)
   - [ ] Alle Annahmen durch Code-Lesen bestätigt — keine Spekulation
   - [ ] Keine offenen Architektur- oder Produktentscheidungen im Plan
   - [ ] Keine Prüf- oder Verifikationsschritte als Plan-Phasen
   - [ ] Keine Formulierungen, welche die exakte Umsetzung offen lassen ("entweder X oder Y durchführen")
   - [ ] Kein Ansatz-Schritt und kein Verifikationsplan-Punkt verlangt eine neu zu schreibende Testdatei oder eine Erweiterung bestehender Testinfrastruktur
   - [ ] Kein Ansatz-Schritt und kein Verifikationsplan-Punkt beschreibt eine Nutzer-,
         Abnahme-, Live-, Datenbank- oder Produktionsprüfung

   Checkbox „Spekulation" oder „Prüfschritte" offen: Plan vervollständigen.
   Checkbox „offene Entscheidung" offen: Entscheidungsfrage an Nutzer eskalieren —
   Plan wird erst nach Auflösung vorgelegt.
   Checkbox „Testdatei/Testinfrastruktur" offen: aus dem Plan entfernen — ausnahmslos, auch
   auf Nutzerwunsch. Eine vom Nutzer tatsächlich gewollte neue Testdatei ist ein eigenständiges
   Umsetzungsziel und gehört als eigener, vom Nutzer benannter Ansatz-Punkt in den Plan, nicht
   als Verifikationsmittel.
   Checkbox „nachgelagerte Prüfung" offen: aus dem Plan entfernen — eine noch ausstehende
   nachgelagerte Prüfung gehört als offener Punkt ins Walkthrough (→ Skill:
   echo-artifacts/walkthroughs), nicht als Verifikationsmittel in den Plan.

6. **Plan vorlegen**
   Plan vollständig präsentieren. Auf Freigabe warten (→ planning-gate).

7. **Überarbeitung einarbeiten** (falls nötig)
   Nutzer-Änderungen übernehmen. Alle geänderten oder neu eingeführten technischen Behauptungen
   (Dateinamen, Klassen, Methoden, Aufrufstellen) durch Code-Lesen bestätigen.
   Logbuch-Eintrag: `Überarbeitet`.

8. **Freigabe bestätigen**
   Logbuch-Eintrag: `Ausführung (Start)`.

9. **Abschluss**
   Nach dem letzten Umsetzungsschritt: Logbuch-Eintrag `Abgeschlossen`.

## Plan an externen Tickets

Gilt für Pläne, die als Kommentar an einem Ticket eines externen Ticketsystems liegen.

1. Plan als Note anhängen (`comment_issue_from_file`).

Prüfung und Freigabe laufen über die Prüfübergabe der aktiven Quelle.

Korrekturbedarf an einem fremden Plan wird nicht selbst eingearbeitet — er geht als
Kommentar an den Plan-Autor (→ `gitlab-integration`, Abschnitt „Autorschaft").

## Pflichtregeln

- MUSS GELTEN: Der Plan wird erst vorgelegt, wenn alle Checkboxen in Schritt 5.5 erfüllt sind.
- MUSS GELTEN: Der erstellte Plan enthält alle Pflichtabschnitte des Templates.
- Überarbeitungen (Schritt 7) unterliegen demselben Verifikationsstandard wie die Erstversion — keine neuen technischen Behauptungen ohne Code-Beleg.
- Planänderungen nach Freigabe setzen ein erneutes Review voraus.
- Pflichtabschnitte des Plan-Schemas gemäß `templates/artifact-schema.md` werden EXAKT verwendet.
