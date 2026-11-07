---
name: echo-maestro
description: Zentraler Einstieg für alle Maestro-Operationen im echo-Agenten-Framework. Use when eine Maestro-Instanz genutzt werden soll — für Session-Startup, Live-Tracking, einzelne Einträge, Tagesabgleich, historische Rekonstruktion oder allgemeine Maestro-Arbeit. Lädt die zuständigen Sub-Skills nach und führt sie aus.
---

# echo-maestro

## Überblick

Dieser Skill ist der zentrale Einstieg für alle Maestro-Operationen im echo-Framework.

Er selbst enthält die Steuerlogik und Konfigurationspflichten. Für fachliche Details werden die zuständigen Sub-Skills explizit nachgeladen und ausgeführt.

Maestro ist das Zielsystem für Tagesstruktur, Zeiterfassung und Aufgabentracking.

## Pflicht beim Laden dieses Skills

`maestro-access` muss beim Laden von echo-maestro **sofort nachgeladen** werden, bevor irgendein operativer Schritt erfolgt. Es enthält Zugriffsmodell, Write-Pfade, Feldlagen-Bezug (`maestro_skill`), Abrufarten und Relationswerte.

## Sub-Skills nach Bedarf nachladen

Diese Sub-Skills werden nur geladen und ausgeführt, wenn der Anwendungsfall es verlangt. Beim Laden ausführen, nicht nur erwähnen.

| Sub-Skill | Wann laden |
|---|---|
| `maestro-access` | Pflicht beim Laden von echo-maestro — Write-Regeln, Abrufarten, Relationsmodell |
| `maestro-session-startup` | Auf Anforderung (Tagesüberblick) oder wenn der Tagesreport offene Vorsession-Activities zeigt |
| `maestro-tracking` | Bei jeder neuen Nutzeranweisung — Activity-Übergang, Lücken-Erkennung, Task/Todo-Stand pflegen |
| `maestro-chore-bridge` | Wenn ein Maestro-Chore- oder Task-Lauf gestartet, in den Agentenkontext injiziert und semantisch zurückgeschrieben werden soll |
| `maestro-classification` | Entscheiden, was getan wurde und welcher Eintrag + welches Zeitkonto passt |
| `maestro-history-reconstruction` | Historische Logs, Transkripte oder Belege in Maestro überführen |
| `maestro-ticket-intake` | Wenn ein `[TICKET-INTAKE]`-Marker im Kontext erscheint — injizierte Ticket-Anfrage verarbeiten |

## Activity-Naming

Activity-Namen wiederholen nicht das Zeitkonto — es ist im Report separat ausgewiesen.

- Mit Ticket-Bezug: `#NNN — Kurzbeschreibung`
- Ohne Ticket-Bezug: `Kurzbeschreibung`
- Kein Präfix wie `Echo — ...` oder `<Projekt> — ...`

## Live-Tracking-Trigger (Absolut-Gate)

**Gilt ohne Ausnahme — auch nach einem Compact.**
Bei jeder neuen Nutzeranweisung als allererster Schritt, vor jedem anderen Tool-Call:
`maestro-tracking` ausführen. Eintrittskriterium, kein Nachlauf — gilt auch für Analyse, Recherche und kurze Antworten.

Den Ablauf (Fortsetzung vs. Übergang, Activity-Abschluss, Task-/Todo-Pflege) definiert `maestro-tracking`.
