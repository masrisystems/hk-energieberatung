---
name: implementierung
description: Einen freigegebenen Implementierungsplan Schritt für Schritt ausführen, dabei dokumentieren und committen.
---

# SKILL: Implementierung

## Schritte

1. **Ticket-Ziel-Recheck**
   Abschnitte "Ziel" und "Anforderungen" des aktiven Tickets direkt vor dem ersten Edit
   nochmals lesen — nicht aus dem Gedächtnis. Das Ticket-Ziel ist die einzige bindende Referenz.

2. **Architektur-Check vor erstem Edit**
   Für jede neue Datei oder Funktion prüfen, ob ein bestehendes Modul denselben Zweck erfüllt.
   Ist ein bestehendes Modul vorhanden: nutzen, nicht neu erstellen.
   Wird dennoch neu erstellt: Begründung im Arbeitslog dokumentieren.

3. **Phasen-Loop**
   Das einmalige `Cowabunga` für den vollständig vorgelegten Implementierungsplan
   autorisiert dessen gesamte unveränderte Umsetzung. Für jede Plan-Phase:
   1. Phase umsetzen
   2. Direkt committen — Branch-Vorlauf inklusive (→ repo-rules)
   3. Ergebnis als Fortschritt melden

   Eine erneute Freigabe ist nur erforderlich, wenn der freigegebene Plan sachlich
   geändert werden muss oder eine neue Produkt- beziehungsweise Architekturentscheidung
   entsteht.

   Ergebnis jeder Phase im Arbeitslog festhalten.

   **Commit-Granularität:** Ein Commit pro Plan-Phase — nicht pro Micro-Schritt innerhalb
   einer Phase, nicht erst am Ende aller Phasen.

4. **Abweichungen dokumentieren**
   Jede Abweichung vom Plan sofort im Arbeitslog festhalten (Was? Warum? Konsequenz?).

   | Art | Beispiel | Behandlung |
   |---|---|---|
   | Klein | Dateiname leicht anders | Dokumentieren, weiter |
   | Mittel | Anderer technischer Ansatz nötig | Dokumentieren + Nutzer informieren |
   | Groß | Feature verhält sich anders als geplant | Stopp → Nutzer befragen → Plan neu |
   | Architekturentscheidung | Grundlegende Struktur muss geändert werden | Stopp → eskalieren |

5. **Neue Probleme erkennen**
   Entdeckte Folgeprobleme → Skill: ticket-followup.
   Nicht stillschweigend mitlösen.

6. **Abschluss**
   - Todos und operative Maestro-Artefakte sauber schließen
   - Walkthrough erstellen und Commit-Referenzen anbinden (→ Skill: walkthrough)
   - Ticket-System aus dem für diese Aufgabe aufgelösten Maestro-Projektdatensatz
     bestimmen (Feld `ticket_system`; Auflösung siehe
     `.agent/skills/echo-maestro/maestro-tracking/SKILL.md`, Abschnitt
     „Projekt-Kontext")
   - Bei `ticket_system = internal`: Ticket-Abschluss gemäß Skill `echo-artifacts/tickets`
     („Schritte: Ticket abschließen") ausführen und zusammen mit der Umsetzung
     committen (Festlegung aus #178). Vor diesem Schritt wird der Umsetzungsblock
     nicht als vollständig abgeschlossen gemeldet.
   - Bei `ticket_system = gitlab` oder `maestro` übernimmt der zuständige
     Ticket-Skill den Abschluss.
   - Ticket und Task in Maestro abschließen; Arbeitslog abschließen (Ende-Zeitstempel)

## Pflichtregeln

- MUSS GELTEN: Scope-Erweiterungen werden als Folge-Ticket erfasst.
- MUSS GELTEN: Bei Architekturzweifeln pausiert die Umsetzung und der Agent eskaliert.
