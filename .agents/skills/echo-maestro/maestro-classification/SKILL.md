---
name: maestro-classification
description: Klassifizierungs-Skill für Maestro-Einträge. Use when entschieden werden muss, was gerade getan wurde und in welchen Maestro-Eintrag das gehört — also: welcher Entry-Typ, welches Zeitkonto, welche Kategorie.
---

# Maestro Classification

## Überblick

Dieser Skill beantwortet die Frage: **„Was habe ich gemacht — und in welchen Bereich fällt das?"**

Er liefert keinen eigenen Write-Pfad, sondern die Entscheidungsgrundlage. Das eigentliche Schreiben erfolgt danach über `maestro-access`.

---

## Entscheidungsbaum: Welcher Entry-Typ?

### 1. Habe ich aktiv Zeit aufgewendet?
→ **Activity**

Weiter: War es einer klar zuordenbaren Maestro-Task?
- Ja → taskgebundene Activity (Feld `task` setzen)
- Nein / unklar → tasklose Activity

### 2. Ist dabei ein eigenständiger Arbeitsgegenstand entstanden, der über mehrere Sessions hinweg verfolgt werden soll?
→ **Task** (zusätzlich oder statt Activity, wenn noch kein passender Task existiert)

### 3. Gibt es einen explizit formulierten offenen nächsten Schritt?
→ **Todo** (immer taskgebunden; kein eigenes TimeAccount)

### 4. Soll geplante oder category-basierte Zeit abgedeckt werden — nicht direkte Arbeit?
→ **Time-Unit** (15-Minuten-Slot, category-basiert)

---

## Entscheidungsbaum: Welches Zeitkonto?

Konto über `maestro_refs()` auflösen und anhand von Name und Beschreibung auswählen. Nur weglassen, wenn definitiv kein passendes Konto existiert.

Typische Zuordnungsprinzipien:
- Entwicklungsarbeit → Konto für Entwicklung/Engineering
- Planungs- und Konzeptionsarbeit → Konto für Planung/Conception
- Interne Verwaltung / Meetings → entsprechendes Konto
- Wenn unsicher: das allgemeinste passende Konto wählen, nicht weglassen

---

## Entscheidungsbaum: Welche Zeitkategorie?

Zeitkategorien werden primär bei **Time-Units** benötigt.

Kategorie über `maestro_refs()` auflösen (vor allem bei Time-Units) und anhand von Name und Beschreibung auswählen.

Bei Activities: optional; Kategorie kann über das Zeitkonto implizit abgedeckt sein.

---

## Grenzen dieses Skills

- Was als „klar zuordenbarer Task" gilt, entscheidet der direkte Chatkontext — kein Raten
- Welche konkreten Zeitkonten existieren, ist instanzabhängig — immer per `maestro_refs()` prüfen
- Welche Kategorien existieren, ist instanzabhängig — per `maestro_refs()` prüfen wenn nötig
- Dieser Skill trifft keine Entscheidungen über die fachliche Korrektheit von Zeitkonten — das ist Nutzersache

---

## Verbindliche Regeln

- Entscheidung immer aus direktem Kontext ableiten, nicht aus Annahmen
- Nur Activity anlegen, wenn direkte Evidenz für geleistete Arbeit vorliegt
- Nur Task anlegen, wenn ein eigenständiger stabiler Arbeitsgegenstand klar erkennbar ist
- Zeitkonto nicht weglassen, solange ein passendes existiert

---

## Referenzen

- `../maestro-access/SKILL.md`
- `../maestro-tracking/SKILL.md`
