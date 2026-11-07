# Reconstruction Workflow

## Ziel

Aus belegten Quellen (Chat-Logs, Git-Commits, Tickets) einen standardkonformen, datenbank-kompatiblen Tageseintrag für Maestro erzeugen — ohne unbelegte Tätigkeiten zu erfinden.

---

## Schritt-für-Schritt

1. Quelle und Zeitraum festlegen
2. Positive Evidenz extrahieren (nur direkt belegte Tätigkeiten)
3. Benachbarte kompatible Mikroereignisse bei Bedarf zu sinnvollen Blöcken bündeln
4. Entscheiden: Task, Todo, Activity, TimeUnit oder keines davon
5. Belegte Arbeit und abgeleitete Tagesabdeckung strikt trennen
6. Ergebnis so formulieren, dass es direkt über Maestro-Actions geschrieben werden kann

---

## Zeitraster-Regeln (verbindlich)

- **Startzeiten abrunden** auf das nächste 5-Minuten-Raster: `19:27` → `19:25`
- **Endzeiten aufrunden** auf das nächste 5-Minuten-Raster: `22:08` → `22:10`
- Jedes Zeitintervall muss ein exaktes Vielfaches von 5 Minuten sein
- **Keine Überschneidungen**: Zeitfenster von Aktivitäten dürfen sich nicht überlappen; bei engen Übergängen Folgestart ggf. um 5 Minuten verschieben

---

## Tagesgrenzen

Aktivitäten dürfen **niemals über Mitternacht (00:00) hinweggehen**.

Grenzüberschreitende Blöcke müssen exakt um 00:00 Uhr geteilt werden:
- Block A endet um `00:00`
- Block B beginnt am Folgetag um `00:00`

---

## Tagesabdeckung via Time-Units

Für lückenlose Tagesabdeckung gelten 96 Time-Units pro Tag (4 × 15 Minuten × 24 Stunden), lückenlos von `00:00` bis `23:45`.

Abdeckungsregeln für unbelegte Zeitfenster:
- Nachtzeiten (typisch `00:00–08:00` und `22:00–24:00`) → Schlaf-Kategorie
- Tages-Downtime ohne Aktivität → Ruhe-Kategorie
- Aktive Arbeitsphasen → entsprechendes Zeitkonto

---

## Qualitätskriterien für Aktivitätstitel

- Kurz, prägnant, im Imperativ- oder Substantivstil
- Keine abgeschnittenen Texte oder Auslassungspunkte
- Kein Systemrauschen (periodische Cronjobs, Memory-Syncs, Control-UI-Benachrichtigungen) als Aktivität erfassen
- Wenn ein Zitat den Titel bildet: das erste zitierte Element vollständig extrahieren, ohne `...`

---

## Authentizitätsregel

- Nur tatsächlich belegte Tätigkeiten aufführen — keine Platzhalter oder Standardeinträge
- Belegte Arbeit und abgeleitete Tagesabdeckung im Ergebnis klar trennen

---

## Standard-Tagesbericht-Template

```markdown
# Tagesbericht: YYYY-MM-DD

chronicle_day_uuid: {UUID}
person_uuid: {PERSON_UUID}

---

## Aktivitäten
- {UUID} HH:MM–HH:MM | X min | Aktivitäts-Name | Zeitkonto

---

## Aufgaben (aktiv)

### {UUID} Task-Name
- geplant: --
- fällig: --
- dringlichkeit: [LOW/MED/HIGH]
- outcome: --

---

## Aufgaben (heute erledigt) (keine)

---

## Chores (keine)

---

## Time-Units (dokumentiert)
- {UUID} 00:00 | Schlafen | Ruhe
- {UUID} 00:15 | Schlafen | Ruhe
...
- {UUID} 23:45 | Schlafen | Ruhe

---

## Time-Units (geplant) (keine)
```
