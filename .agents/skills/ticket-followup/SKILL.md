---
name: ticket-followup
description: Erfasst während der Umsetzung entdeckte Folgeprobleme als eigene Tickets, ohne den aktuellen Scope zu erweitern. Verwenden, sobald ein eigenständiges Problem sichtbar wird.
---

# SKILL: Ticket Followup

## Schritte

1. **Problem benennen**
   Klares, präzises Bild: Was ist das Problem? Warum ist es ein eigenes Ticket?

2. **Ticket erstellen**
   Schema: `.agent/skills/echo-artifacts/templates/ticket.md`. Status: `PROPOSED`.

3. **Referenz setzen**
   Im Folge-Ticket: Referenz auf das auslösende Ticket.
   Im aktuellen Arbeitslog: Hinweis auf das neue Folge-Ticket.

4. **Nutzer informieren**
   Kurz kommunizieren: Ticket-ID, betroffenes Thema, Begründung für separate Bearbeitung.

5. **Weiterarbeiten**
   Zurück zum aktuellen Ticket.

## Pflichtregeln

- MUSS GELTEN: Jedes angelegte Folge-Ticket ist vollständig formuliert.
- Im Zweifel wird ein Folge-Ticket angelegt.
- Ein Folgeproblem qualifiziert für ein eigenes Ticket, wenn es eigenständig lösbar und außerhalb des aktuellen Ticket-Scopes liegt.
- Das laufende Ticket bleibt aktiv, sofern das Folgeproblem kein Blocker ist.
