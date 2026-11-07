---
name: ticket-review
description: Prüft und normalisiert ein Ticket auf Vollständigkeit, Qualität und Umsetzbarkeit. Verwenden, bevor ein Ticket als `approved` markiert wird.
---

# SKILL: Ticket Review

## Schritte

1. **Einordnung**
   - Ist die Aufgabe valide?
   - Ist sie ausreichend beschrieben?
   - Ist sie abgrenzbar?
   - Existiert bereits ein ähnliches Ticket?

2. **Qualitätsprüfung** (Checkliste)
   - [ ] Ziel klar
   - [ ] ≥ 2 Akzeptanzkriterien
   - [ ] Risiken benannt
   - [ ] Umfang eindeutig aus Ziel und Anforderungen erkennbar
   - [ ] Keine Überschneidung mit offenem Ticket

3. **Entscheidung treffen**
   Das Ticket wird:
   - **Bestätigt** → Status: `approved`
   - **Korrigiert** → Fehlende Teile ergänzen, Status bleibt `proposed`
   - **Zusammengeführt** → Mit bestehendem Ticket mergen, dieses ablehnen
   - **Aufgeteilt** → In mehrere Tickets zerlegen
   - **Zurückgewiesen** → Status: `rejected` mit den Gründen der Ablehnung
   - **Verworfen** → Status: `discarded` mit Begründung

4. **Initialplan ergänzen** (optional, bei approved)
   Grobe erste Umsetzungsidee im Ticket-Abschnitt "Erste Umsetzungsidee" hinterlegen — Startpunkt für den Entwickler.

5. **Ergebnis kommunizieren**
   Entscheidung mit Begründung dem Nutzer mitteilen.

## Pflichtregeln

- MUSS GELTEN: Jede Freigabe (Status `approved`) setzt vollständige Qualitätsprüfung (Schritt 2) voraus.
- MUSS GELTEN: Widersprüche, Lücken und Risiken sind explizit benannt, bevor das Ticket ein Ergebnis erhält.
- MUSS GELTEN: Schritt 4 entfällt bei instabilen Anforderungen.
