---
name: maestro-history-reconstruction
description: Rekonstruiere belegte Aktivitäten aus historischen Quellen in Maestro-geeignete Vorschläge und Einträge. Use when historische Logs, Transkripte oder andere Quellen in `tasks`, `todos`, `activities` und `time-units` übersetzt werden sollen, ohne unbelegte Tätigkeiten zu erfinden.
---

# Maestro History Reconstruction

## Überblick

Dieser Skill übersetzt historische Evidenz in Maestro-taugliche Einträge.

Er ist streng evidenzbasiert und Maestro-spezifisch. Er dient nicht der allgemeinen Forgeron-Nutzung.

## Verbindliche Regeln

- Activities nur bei direkter relevanter Evidenz.
- Mindestdauer für eigenständige Activity: 5 Minuten.
- Kürzere Mikrovorgänge nur sinnvoll gebündelt.
- Unbelegte oder nur abgeleitete Zeit erzeugt keine Activity.
- Solche Zeit darf aber category-basierte TimeUnits für Tagesabdeckung erzeugen.
- Gleiche Themenlinie darf über mehrere getrennte Activities mit demselben Titel laufen, wenn dazwischen eine echte Lücke liegt.
- Oberste Priorität bei der Rekonstruktion hat das korrekte Zeitraster im 5-Minuten-Raster.
- Eine vom Nutzer explizit gewünschte Verdichtung oder Rasterverschiebung für die Dokumentation darf den quellennahen Zeitblock bewusst auf einen anderen, klar benannten Maestro-Slot abbilden.
- Tasklose Activities sind erlaubt.
- TimeUnits bleiben ohne TimeAccounts.
- Session-Logs sind eine Quelle der Wahrheit, nicht die einzige.

## Ziel

Aus Rohmaterial entstehen:
- belastbare Eintragsvorschläge
- klare Trennung zwischen belegter Activity und abgeleiteter TimeUnit
- spätere operative Writes über die laufende Maestro-Instanz

## Tool: scan_day.py

Dieses Tool scannt Chat-Log-Dateien (OpenClaw JSONL, Claude Code JSONL) nach Aktivität an einem Datum und erzeugt strukturierte Aktivitätsvorschläge.

```
python3 tools/scan_day.py YYYY-MM-DD --logs-path /pfad/zu/logs
python3 tools/scan_day.py 2026-05-21 --logs-path ~/convos --verbose
python3 tools/scan_day.py 2026-05-21 --logs-path ~/convos --generate
```

**Wann verwenden:**
- Historische Tage rekonstruieren, für die Maestro-Einträge fehlen
- Completion-Evidence für offene Aktivitäten suchen (z. B. beim Session-Startup)
- Tagesbericht-Rohlinge generieren (`--generate`)

**Wann NICHT verwenden:**
- Laufende Aktivität aktualisieren
- Todo abhaken oder Aufgabe bearbeiten
- Jede andere Live-Tracking-Operation

Konfiguration: `logs_path` in `.agent/config.json` (optional — wenn nicht gesetzt, muss `--logs-path` angegeben werden)

## Referenzen

- `references/evidence-rules.md`
- `references/reconstruction-workflow.md`
- `references/maestro-mapping.md`
- `references/test-mode.md`
