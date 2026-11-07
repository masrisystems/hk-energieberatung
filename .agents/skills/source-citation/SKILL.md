---
name: source-citation
description: Verbindlicher Standard für Quellenangaben in Analysedokumenten — jede belegte Aussage verweist auf einen Eintrag im Quellregister. Verwenden immer, wenn eine Tatsachenbehauptung in ein Analysedokument aufgenommen wird.
---

# SKILL: Source Citation

## Quellenformat in Dokumenten

**Inline-Zitation** (für Fließtext und Aufzählungen):
```
Das Bestellsystem verarbeitet Zahlungen über drei Kanäle. [Q:001]
```

**Block-Zitation** (für zentrale Belege oder längere Auszüge):
```markdown
> **[BELEGT — Q:001]** `src/Payment/PaymentRouter.php`, Z. 23–31  
> Abgerufen: 2026-03-31 14:23
> ```php
> match ($method) {
>     'invoice' => $this->handleInvoice($order),
>     'budget'  => $this->handleBudget($order),
>     'card'    => $this->handleCard($order),
> }
> ```
```

## Quellregister-Eintrag erstellen

Datei: `docs/analysis/source-registry.md`

```markdown
### Q001
- **Pfad:** `src/Payment/PaymentRouter.php`
- **Zeilen:** 23–31
- **Abgerufen:** 2026-03-31 14:23
- **Snapshot:**
  ```php
  match ($method) {
      'invoice' => $this->handleInvoice($order),
      ...
  }
  ```
- **Verwendet in:** architecture.md (Abschnitt "Zahlungsfluss"), feature-catalog.md (Q:Feature "Zahlung")
- **Änderungslog:** —
```

## Quell-ID vergeben

- Format: `Q:` + dreistellige Nummer, fortlaufend: `Q:001`, `Q:002`, ...
- IDs werden nie wiederverwendet, auch nicht nach Löschung eines Eintrags
- Neue IDs am Ende der Registrierung anfügen

## Änderungen an Quellen protokollieren

Wenn sich Pfad oder Inhalt einer zitierten Quelle ändert:

```markdown
- **Änderungslog:**
  | Datum | Art | Details |
  |-------|-----|---------|
  | 2026-04-15 | Pfad geändert | Verschoben: `src/Payment/` → `app/Payments/` |
  | 2026-04-20 | Inhalt geändert | Methode `handleInvoice` umbenannt in `processInvoice` |
```

Alle Dokumente, die diese Quelle verwenden, sind auf Aktualität zu prüfen und ggf. zu aktualisieren.
Geprüfte Dokumente in der Zeile vermerken: `| ... | Dokumente geprüft: architecture.md ✓ |`

## Schritte bei neuer Quelle

1. Datei lesen, relevante Stelle identifizieren
2. Quell-ID vergeben (nächste freie Nummer)
3. Eintrag in `source-registry.md` anlegen (Pfad, Zeilen, Zeitstempel, Snapshot)
4. Inline-Marker `[Q:XXX]` an der Stelle im Analysedokument setzen
5. Eintrag "Verwendet in" aktuell halten

## Pflichtregeln

- MUSS GELTEN: Jedes `[BELEGT]` hat einen gültigen `Q:`-Verweis im Quellregister.
- MUSS GELTEN: Snapshots entstehen aus aktuellem Dateilesen, nicht aus dem Gedächtnis.
- MUSS GELTEN: Zeitstempel folgen dem Format `YYYY-MM-DD HH:MM`.
- MUSS GELTEN: Das Quellregister ist append-only; bestehende Einträge werden ergänzt, nicht gelöscht.
- MUSS GELTEN: Widersprüchliche Quellen werden beide zitiert; der Widerspruch ist explizit benannt.
