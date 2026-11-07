---
name: steuer-unterlagen-zusammenstellen
description: Stellt Steuerunterlagen für ein oder mehrere Jahre aus der Bürokratia-Ablage zusammen, ordnet sie in die etablierte Kategoriestruktur ein und legt sie unter /home/judah/Steuern/<Jahr>/ ab. Meldet Lücken explizit. Verwenden, wenn Unterlagen für den Steuerberater vorbereitet werden sollen.
---

# steuer-unterlagen-zusammenstellen

## Quellen

| Quelle | Inhalt |
|---|---|
| `/home/judah/buerokratia/Steuern/<Jahr> laufend/` | Bereits vorsortierte Dokumente für dieses Jahr |
| `/home/judah/buerokratia/Ablage/` | Unsortierte Sammlung — nach Jahreszahl im Dateinamen filtern |
| `/home/judah/buerokratia/Ablage/freenet/` | Freenet-Rechnungen als ZIP je Jahr |

Referenzstruktur: letztes abgeschlossenes Jahr unter `buerokratia/Steuern/` — Ordnernamen
und Dateimuster gelten als Vorlage für den Zielordner.

## Ablauf

**Schritt 1 — Zieljahr(e) und Zielort festlegen**

Zielort: `/home/judah/Steuern/<Jahr>/` (anlegen wenn nicht vorhanden).
Referenzjahr: nächstjüngeres Jahr unter `buerokratia/Steuern/` mit vollständiger Struktur.

**Schritt 2 — Referenzstruktur einlesen**

Ordner und Dateimuster des Referenzjahres erfassen. Daraus ergibt sich die
Kategorieliste für den Zielordner.

**Schritt 3 — Quelldokumente identifizieren**

1. Aus `buerokratia/Steuern/<Jahr> laufend/` alle Dateien übernehmen.
2. Aus `buerokratia/Ablage/` alle Dateien filtern, deren Name das Zieljahr enthält
   (Datumspräfix `YYYY-` oder Muster `_YYYY_` / `_YYYY.` / `YYYYMM`).
3. Duplikate: existiert eine Datei bereits aus dem laufenden Ordner, Ablage-Kopie überspringen.
   Bei zwei Ablage-Varianten (z.B. älterer und neuerer Download): vollständigere Variante bevorzugen.

**Schritt 4 — Kategorisierung**

Jede Quelldatei einer Zielkategorie zuordnen:

| Kategorie | Erkennungsmerkmale |
|---|---|
| Root (Jahresordner) | Steuerbescheide, Lohnsteuerbescheinigung, Meldebescheinigung, Renteninformation, Schenkungssteuer, sonstige Jahres-Einmaldokumente |
| `Gehaltsabrechnungen/` | `Gehaltsabrechnung_ME_*` oder `Gehaltsmitteilung_*` |
| `Aufwendungen DataForge/IP-Projects/` | Rechnungen IP-Projects (Muster: `YYYY-MM-DD-20YYNNNNN.pdf`) |
| `Aufwendungen DataForge/Checkdomain/` | Rechnungen Checkdomain (Muster: `YYMM-NNNNNN.pdf`) |
| `Aufwendungen DataForge/Diverse/` | Sonstige DataForge-Betriebsausgaben |
| `DataForge/` | DataForge-Ausgangsrechnungen (`RE-YYYY-*.pdf`) |
| `Kontoauszüge/LZO/` | `Konto_0023148596-Auszug_YYYY_*.pdf` |
| `Kontoauszüge/OLB/` | `432072700_YYYY_Nr*.pdf` |
| `Kontoauszüge/ING/` | `Girokonto_5441005615_*.pdf` oder nummerierte `*_Kontoauszug_YYYYMMDD.pdf` |
| `Kontoauszüge/PayPal AFM/` | `WPP6CDN9T6EK2-MSR-YYYY*.PDF` |
| `Vodafone/` | `*_Rechnung_Kundennr_112028550.pdf` oder `*_Rechnung_weitere_233811634.pdf` |
| `Versicherungen/` | Hausrat, Haftpflicht, sonstige Jahresbescheinigungen |
| `Dienstleistungen/` | Handwerker, Schornsteinfeger, haushaltsnahe Dienstleistungen |
| `Freenet/` | `Rechnungen<YYYY>-freenet.zip` |

Unbekannter Dokumenttyp: Nutzer fragen, nicht raten.

**Schritt 5 — Verzeichnisse anlegen und Dateien kopieren**

Zielordner anlegen (analog Referenzstruktur, nur Kategorien mit tatsächlichen Dokumenten).
Dateien kopieren — Originale in `buerokratia/` bleiben unverändert.

**Schritt 6 — Vollständigkeitsprüfung und Lückenmeldung**

Nach dem Kopieren je Kategorie prüfen:

- Kontoauszüge: Sind alle Monate des Jahres vorhanden? Fehlende Nummern benennen.
- Gehaltsabrechnungen: Alle 12 Monate? Fehlende Monate benennen.
- Vodafone: 12 Monatsrechnungen erwartet? Fehlende melden.
- Lohnsteuerbescheinigung: Vorhanden? (wird meist im Januar des Folgejahres geliefert)

Lücken am Ende der Ausführung gesammelt ausgeben — nicht beim ersten Fund abbrechen.
