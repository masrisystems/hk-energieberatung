---
name: document-synthesis
description: Führt gesammelte Analysebefunde nach einheitlichem Schema zu einem vollständigen, reviewfähigen Dokument zusammen. Verwenden nach Abschluss einer Analysephase.
---

# SKILL: Document Synthesis

## Schritte

1. **Schema laden**
   Das passende Schema aus `.agent/skills/document-synthesis/analysis-schemas.md` auswählen.

2. **Abschnitte befüllen**
   Jeden Pflichtabschnitt mit Befunden füllen.
   - Jede Aussage: Belegkennzeichnung gemäß Regelmodul `source-discipline` setzen
   - Jedes `[BELEGT]`: `[Q:XXX]`-Verweis auf Quellregister (→ Skill: `source-citation`)
   - Jedes `[OFFEN]`: kurze Begründung, warum keine Quelle gefunden wurde

3. **Lücken explizit machen**
   Pflichtabschnitte ohne Daten erhalten einen `[OFFEN]`-Eintrag mit Begründung — nicht weglassen.

4. **Quellabdeckung prüfen**
   Hat jede Tatsachenbehauptung einen Beleg? Sind alle `Q:`-Verweise im Quellregister vorhanden?

4.5 **Reviewbereit-Gate** (vor Vorlage)
   - [ ] Alle Pflichtabschnitte vorhanden (auch als `[OFFEN]` wenn keine Daten)
   - [ ] Jede Tatsachenbehauptung hat Belegkennzeichnung
   - [ ] Jedes `[BELEGT]` hat `[Q:XXX]`-Verweis
   - [ ] Alle `[Q:XXX]`-Verweise existieren im Quellregister

   Ist eine Checkbox offen: Abschnitt vervollständigen, dann vorlegen.

5. **Dokument vorlegen**
   Dokument dem Nutzer präsentieren. Auf explizites Feedback oder Freigabe warten.

6. **Überarbeitung einarbeiten** (falls nötig)
   Feedback einarbeiten. Neue oder geänderte Belege im Quellregister nachtragen.

7. **Finalisieren**
   Nach expliziter Freigabe: Status im Meta-Abschnitt auf `final` setzen.
   Dokument unter `docs/analysis/<dokumentname>.md` ablegen.

## Pflichtregeln

- MUSS GELTEN: Ein Dokument wird erst als `final` markiert, wenn alle Tatsachenbehauptungen belegt sind.
- Schema-Abweichungen setzen explizite Nutzerfreigabe voraus.
