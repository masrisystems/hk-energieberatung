---
name: maestro-session-startup
description: Maestro-Tagesüberblick auf Anforderung — Tagesstand laden, offene Vorsession-Aktivitäten auflösen, Arbeitsblock verankern. Use when der Nutzer einen Tagesüberblick anfordert oder der Tagesreport offene Aktivitäten aus Vorsessions zeigt, die aufgelöst werden müssen.
---

# Maestro Tagesüberblick & Vorsession-Auflösung

## Gate-Check (Pflicht vor allem anderen)

`maestro-access` im Kontext sichtbar? Falls nicht: zuerst nachladen.

---

## Schritt 1 — Tagesstand abrufen

Beide Abrufe **parallel** und **unabhängig voneinander**.

```
maestro_report(date="{heute}", max_chars=6000)
maestro_report(date="{gestern}", max_chars=6000)
```

**404 oder Verbindungsfehler** auf einem der beiden Abrufe → kein Abbruch; mit den verfügbaren Daten des anderen Tages fortfahren.
Wenn beide leer oder nicht erreichbar → direkt zu Schritt 4.

---

## Schritt 2 — Überblick ausgeben

Kompakte Ausgabe an den Nutzer (1–3 Zeilen):

```
Maestro-Stand: Letzte Aktivität "[Name]" ([start_time]), [N] aktive Tasks, [N] offene Todos.
```

Wenn heute noch keine Einträge und gestern nichts Offenes: `Maestro: kein offener Stand.`

---

## Schritt 3 — Offene Aktivitäten klären

**Definition offen:** `duration = 0` und `start_time` liegt vor dem Start dieser Session.

Für jede offene Aktivität (chronologisch, älteste zuerst):

```
Offene Aktivität "[Name]" seit [start_time].
Soll ich damit fortfahren, oder wurde sie abgeschlossen?

  [a] Fortführen in dieser Session
  [b] Abgeschlossen — [Endzeit]
  [c] Offen lassen
```

| Antwort | Aktion |
|---------|--------|
| [a] Fortführen | Keine Änderung; Activity als laufend in Session merken |
| [b] Abgeschlossen | `maestro_update(archetype="activities", identifier="<id>", fields={"duration": "<minuten>"})` — Endzeit auf 5-Min-Raster aufrunden, nur `duration` setzen |
| [c] Offen lassen | Keine Änderung |

---

## Schritt 4 — Laufende Activity identifizieren

Gibt es nach der Auflösung eine Activity mit `duration = 0`, die in dieser Session weitergeführt wird?
→ Diese Activity als **laufend** in der Session merken (UUID und `time_account` cachen).

Gibt es keine laufende Activity?
→ **Keine neue Activity anlegen.** `maestro-tracking` legt die Activity beim ersten
konkreten Nutzerauftrag an — dann ist der Name aus dem Kontext ableitbar.

Time-Accounts vorab laden: `maestro_refs()`.

---

## Verbindliche Regeln

- Kein Write ohne Nutzerantwort
- Tagesabdeckung nur auf explizite Anfrage schreiben

---

## Referenzen

- `../maestro-access/SKILL.md`
- `../maestro-tracking/SKILL.md`
