---
title: HK Energieberatung - Automatisierte E-Mail-Sequenzen & Lifecycle Drip-Kampagnen
client: Hussein Khashab & Wajih Tfaili
company: HK Energieberatung
location: Bremen, Norddeutschland
last_updated: 2026-08-08
status: Active
tags:
  - client/hussein-khashab
  - project/hk-energieberatung
  - emails
  - email-automation
  - lead-nurture
  - customer-journey
  - lifecycle-marketing
---

# 📧 HK Energieberatung – Automatisierte E-Mail-Sequenzen & Lifecycle Drips

Dieses Dokument definiert alle automatisierten E-Mail-Funnels und Transaktions-Sequenzen für **HK Energieberatung**. Die E-Mails sind darauf ausgelegt, eingegangene Website-Leads zu qualifizieren, Vertrauen aufzubauen, den 48h-Expressausweis-Prozess reibungslos zu begleiten und Bestandskunden für lukrative Sanierungsfahrpläne (iSFP) und BAFA/KfW-Förderungen zu gewinnen.

---

## 🗺️ 1. Übersicht der 3 Kern-Funnels

```
                                [ Website-Interaktion ]
                                           │
       ┌───────────────────────────────────┼───────────────────────────────────┐
       ▼                                   ▼                                   ▼
 [ Flow 1: Inbound Lead Nurture ]   [ Flow 2: Expressausweis 48h ]    [ Flow 3: Download-Center Nurture ]
 • Trigger: Kontaktformular         • Trigger: Ausweis-Bestellung     • Trigger: Checklisten-Download
 • Ziel: Fester Vor-Ort-Termin      • Ziel: PDF-Lieferung & Up-Sell   • Ziel: Lead zum iSFP konvertieren
 • Dauer: 4 E-Mails über 7 Tage     • Dauer: 3 E-Mails über 8 Tage    • Dauer: 3 E-Mails über 8 Tage
```

---

## 🚀 Flow 1: Inbound Lead Nurture & Erstberatungs-Terminierung
* **Trigger:** Formularübermittlung auf [[index.html|Startseite]], Bremen, Aurich oder Über uns.
* **Ziel:** Bestätigung der Anfrage, Vorqualifikation der Immobilie und verbindliche Terminvereinbarung für das kostenlose Erstgespräch.
* **Exit-Bedingung:** Termin ist gebucht oder Kunde antwortet direkt.

---

### 📩 E-Mail 1: Sofortige Bestätigung & Vorbereitungs-Checkliste
* **Versand:** Sofort nach Formularabsendung (0 Minuten)
* **Betreff:** `Ihre Anfrage bei HK Energieberatung – Nächste Schritte`
* **Vorschautext:** `Wir haben Ihre Nachricht erhalten. Hier ist die kurze Übersicht für Ihr kostenloses Erstgespräch.`

> Hallo Herr/Frau {{nachname}},
> 
> vielen Dank für Ihre Anfrage über unsere Website!
> 
> Wir haben Ihre Angaben zu Ihrer Immobilie in **{{wohnort}}** erhalten. Einer unserer Energieberater (Ing. Hussein Khashab oder Ing. Wajih Tfaili) prüft Ihre Eckdaten bereits und meldet sich innerhalb von 24 Stunden telefonisch bei Ihnen, um das kostenlose Erstgespräch abzustimmen.
> 
> **Damit wir das maximale Förderpotenzial für Sie berechnen können, legen Sie bitte folgende Unterlagen bereit (falls vorhanden):**
> - Letzte 3 Heizkostenabrechnungen (Gas, Öl, Fernwärme oder Strom)
> - Baujahr des Gebäudes und der Heizungsanlage
> - Baupläne / Grundrisse oder Wohnflächenberechnung
> 
> Falls Sie vorab dringende Fragen haben oder uns Pläne direkt senden möchten, antworten Sie einfach auf diese E-Mail oder schreiben Sie uns per WhatsApp unter [+49 162 6985115](https://wa.me/491626985115).
> 
> Wir freuen uns darauf, Ihr Einsparpotenzial aufzudecken!
> 
> Herzliche Grüße  
> **Ihr Team von HK Energieberatung**  
> *Zertifizierte dena Energieeffizienz-Experten & Bauingenieure*  
> Industriestraße 34, 28199 Bremen • [hk-energieberatung.de](https://hk-energieberatung.de/)

---

### 📩 E-Mail 2: Der +5% Förderbonus (iSFP Hebel)
* **Versand:** Tag 2 (nach 48 Stunden, falls noch kein Termin fixiert wurde)
* **Betreff:** `So sichern Sie sich 50% BAFA-Zuschuss + 5% Extra-Förderung`
* **Vorschautext:** `Warum sich der individuelle Sanierungsfahrplan (iSFP) für fast jedes Wohngebäude sofort rechnet.`

> Hallo Herr/Frau {{nachname}},
> 
> viele Eigentümer fragen uns vor dem ersten Gespräch: *„Lohnt sich ein Sanierungsfahrplan für mein Haus überhaupt?“*
> 
> **Die klare Antwort lautet: Ja – und zwar aus zwei konkreten Gründen:**
> 
> 1. **50% staatlicher Zuschuss:** Die Bundesregierung übernimmt die Hälfte der Kosten für die Erstellung unseres Sanierungsfahrplans durch das BAFA. Ihr Eigenanteil ist dadurch minimal.
> 2. **Der +5% iSFP-Bonus:** Sobald Sie innerhalb von 15 Jahren eine Sanierungsmaßnahme umsetzen (z. B. Fenstertausch, Dach- oder Fassadendämmung), erhalten Sie **5% mehr Zuschuss vom Staat** als ohne Fahrplan. Bei 30.000 € Sanierungskosten sind das **1.500 € geschenktes Geld extra**.
> 
> In unserem kostenlosen Erstgespräch zeigen wir Ihnen exakt, welche Fördertöpfe der BAFA und KfW für Ihre Immobilie infrage kommen.
> 
> 👉 **[Kostenloses Erstgespräch telefonisch abstimmen: +49 162 6985115](tel:+491626985115)**
> 
> Beste Grüße  
> **Hussein Khashab**  
> *Geschäftsführer & Bauingenieur*

---

### 📩 E-Mail 3: Praxisbeispiel & Vertrauensbeweis
* **Versand:** Tag 4
* **Betreff:** `Praxisbeispiel: Über 60% Heizkosten gespart & 28.400 € Förderung erhalten`
* **Vorschautext:** `Ein kurzer Einblick in ein typisches Sanierungsprojekt aus unserer Region.`

> Hallo Herr/Frau {{nachname}},
> 
> *(Hinweis: Das Beispiel ist ein Platzhalter. Vor Versand durch ein reales, vom Kunden freigegebenes Projekt ersetzen oder als „Beispielrechnung“ kennzeichnen.)*
> 
> Sanierungen wirken auf den ersten Blick oft unübersichtlich und teuer. Deshalb möchten wir Ihnen ein reales Beispiel einer Familie aus dem Bremer Umland zeigen:
> 
> **Ausgangslage:**
> - Einfamilienhaus, Baujahr 1978, alte Gas-Heizung, ungedämmtes Dachgeschoss.
> - Jährliche Heizkosten: ca. 3.400 €.
> 
> **Unsere Begleitung:**
> 1. Erstellung des individuellen Sanierungsfahrplans (50% BAFA-Zuschuss).
> 2. Gezielte Dachdämmung mit 20% BAFA-Zuschuss (inkl. 5% iSFP-Bonus).
> 3. Umstieg auf eine moderne Wärmepumpe mit 55% KfW-Zuschuss.
> 
> **Das Ergebnis:**
> - **28.400 € Gesamtförderung** direkt auf das Konto des Eigentümers ausgezahlt.
> - **Über 60% jährliche Einsparung** bei den Energiekosten.
> - Massive Wertsteigerung der Immobilie.
> 
> Wollen Sie wissen, wie diese Rechnung für Ihr Haus aussieht?
> 
> Antworten Sie einfach kurz mit **„Ja“** auf diese E-Mail – wir rufen Sie zur gewünschten Uhrzeit an.
> 
> Viele Grüße  
> **Wajih Tfaili**  
> *Bauingenieur & Energieeffizienz-Experte*

---

### 📩 E-Mail 4: Die 3 größten Fehler beim Heizungs- & Sanierungsstart
* **Versand:** Tag 7 (Abschluss des Nurture-Funnels)
* **Betreff:** `Vermeiden Sie diesen teuren Fehler bei BAFA & KfW Förderungen`
* **Vorschautext:** `Warum Handwerker-Aufträge vor dem Förderantrag bares Geld kosten.`

> Hallo Herr/Frau {{nachname}},
> 
> heute ein sehr wichtiger Experten-Tipp, der Eigentümern jedes Jahr Tausende Euro rettet:
> 
> ⚠️ **Der häufigste Fehler:** Handwerkerangebote unterschreiben, *bevor* die Förderanträge (BAFA / KfW) offiziell bewilligt oder die technischen Projektbeschreibungen (tpB) durch einen zertifizierten Energieberater erstellt wurden.
> 
> Wer den Vertrag vorab ohne Förder-Klausel unterschreibt, verliert in den meisten Fällen den **kompletten Anspruch auf staatliche Zuschüsse**.
> 
> Wenn Sie in den nächsten 12 Monaten Modernisierungen planen, lassen Sie uns vorab unverbindlich sprechen, damit alle Fristen und Förderrichtlinien gewahrt bleiben.
> 
> 📞 Rufen Sie uns einfach direkt an: **+49 162 6985115** oder schreiben Sie uns kurz per Mail.
> 
> Herzliche Grüße  
> **Hussein Khashab & Wajih Tfaili**  
> *HK Energieberatung*

---

## ⚡ Flow 2: Post-Purchase & Up-Sell: Expressausweis (48h Service)
* **Trigger:** Erfolgreiche Übermittlung des Expressausweis-Formulars auf expressausweis.html.
* **Ziel:** Bestätigung, 48h-Fulfillment, Übergabe des fertigen PDF-Verbrauchsausweises und Up-Selling für iSFP / energetische Sanierung.

---

### 📩 E-Mail 1: Eingangsbestätigung & Datenprüfung
* **Versand:** Sofort nach Formular-Abschluss
* **Betreff:** `Auftragsbestätigung: Ihr Expressausweis (48h) wird geprüft`
* **Vorschautext:** `Wir haben Ihre Daten erhalten. Die Erstellung Ihres rechtssicheren Energieausweises läuft.`

> Hallo {{vorname}} {{nachname}},
> 
> vielen Dank für Ihre Bestellung des Express-Verbrauchsausweises bei HK Energieberatung!
> 
> **Die Daten zu Ihrem Gebäude ({{gebaeude_adresse}}) sind bei unseren Bauingenieuren eingegangen.**
> 
> **So geht es jetzt weiter:**
> 1. **Plausibilitätsprüfung:** Wir prüfen Ihre Heizkostenabrechnungen und Gebäudedaten gemäß Gebäudeenergiegesetz (GEG).
> 2. **DIBt-Registrierung:** Ihr Energieausweis wird offiziell beim Deutschen Institut für Bautechnik (DIBt) registriert und erhält eine offizielle Registriernummer.
> 3. **Lieferung:** Sie erhalten Ihren fertigen, rechtssicheren Energieausweis innerhalb von **48 Stunden als PDF** direkt an diese E-Mail-Adresse.
> 
> Sollten Rückfragen zu den Abrechnungszeiträumen oder Fotos auftreten, melden wir uns direkt bei Ihnen.
> 
> Herzliche Grüße  
> **Ihr Ausweis-Team von HK Energieberatung**

---

### 📩 E-Mail 2: Bereitstellung des fertigen Energieausweises (PDF)
* **Versand:** Nach Fertigstellung (garantiert innerhalb von 48h)
* **Betreff:** `Ihr Energieausweis für {{gebaeude_adresse}} liegt bereit (PDF)`
* **Vorschautext:** `Ihr offizieller Verbrauchsausweis nach GEG ist fertiggestellt und beigefügt.`

> Hallo {{vorname}} {{nachname}},
> 
> Ihr offizieller Energie-Verbrauchsausweis für die Liegenschaft **{{gebaeude_adresse}}** wurde erfolgreich erstellt, beim DIBt registriert und ist dieser E-Mail als PDF-Dokument beigefügt.
> 
> **Wichtige Eckdaten zu Ihrem Ausweis:**
> - **Ausweis-Typ:** Verbrauchsausweis nach Gebäudeenergiegesetz (GEG)
> - **Gültigkeit:** 10 Jahre ab Ausstellungsdatum
> - **Pflichtangaben bei Inseraten:** Nutzen Sie die im Ausweis ausgewiesenen Kennwerte (Effizienzklasse & Endenergieverbrauch) für Ihre Immobilienanzeigen.
> 
> Ihre Rechnung mit ausgewiesener Mehrwertsteuer finden Sie ebenfalls im Anhang.
> 
> Wir bedanken uns herzlich für Ihr Vertrauen!
> 
> Beste Grüße  
> **Ing. Hussein Khashab & Ing. Wajih Tfaili**  
> *HK Energieberatung*

---

### 📩 E-Mail 3: Up-Sell: Sanierungspotenzial & +5% iSFP-Bonus
* **Versand:** 7 Tage nach Erhalt des Energieausweises
* **Betreff:** `Energieeffizienzklasse verbessern & Sanierungszuschüsse nutzen?`
* **Vorschautext:** `Wie Sie den Energiewert Ihres Gebäudes gezielt steigern und bis zu 70% Förderung sichern.`

> Hallo {{vorname}} {{nachname}},
> 
> Sie haben vor einer Woche Ihren Energieausweis für **{{gebaeude_adresse}}** erhalten.
> 
> Auf Seite 4 Ihres Ausweises haben wir Ihnen bereits erste Modernisierungsempfehlungen zusammengestellt. Falls Sie oder der zukünftige Käufer/Mieter über Maßnahmen wie Heizungserneuerung, Fenstertausch oder Dämmung nachdenken:
> 
> **Wussten Sie, dass der Bund diese Maßnahmen mit bis zu 70% bezuschusst?**
> 
> Mit unserem **individuellen Sanierungsfahrplan (iSFP)** erhalten Sie:
> - Eine maßgeschneiderte Sanierungs-Roadmap für Ihr Gebäude.
> - **50% Kostenerstattung** für die Beratung durch das BAFA.
> - **+5% Extraförderung** auf alle späteren Sanierungsschritte.
> 
> Wenn Sie Ihr Gebäude fit für die Zukunft machen möchten, beraten wir Sie gerne in einem kurzen, unverbindlichen Gespräch.
> 
> 👉 **[Jetzt kostenlose Erstberatung anfragen](https://hk-energieberatung.de/#contact)**
> 
> Viele Grüße  
> **Hussein Khashab**

---

## 📑 Flow 3: Download-Center Nurture (Dokumente & Checklisten)
* **Trigger:** Download einer PDF-Checkliste oder eines Förderleitfadens auf dokumente.html.
* **Ziel:** Download-Interessenten in qualifizierte Beratungs-Leads konvertieren.

---

### 📩 E-Mail 1: Bereitstellung des Downloads & Kurzüberblick
* **Versand:** Sofort nach Formulareingabe auf `dokumente.html`
* **Betreff:** `Ihr Download: Sanierungs-Checkliste & Förderübersicht 2026`
* **Vorschautext:** `Hier ist Ihr PDF-Leitfaden für BAFA & KfW Förderungen von HK Energieberatung.`

> Hallo {{vorname}},
> 
> vielen Dank für Ihr Interesse! Hier ist Ihr direkter Download-Link:
> 
> 📄 **[Download: HK Energieberatung Sanierungs-Checkliste (PDF)](https://hk-energieberatung.de/dokumente.html)**
> 
> **Die wichtigsten 3 Punkte aus dem Leitfaden auf einen Blick:**
> 1. Für Heizungstausch sind über die KfW 458 bis zu 70% Zuschuss möglich.
> 2. Gebäudehülle (Dach, Wand, Fenster) wird über das BAFA mit bis zu 20% gefördert (inkl. iSFP-Bonus).
> 3. Der iSFP selbst wird zu 50% vom Staat bezuschusst.
> 
> Haben Sie Fragen zu konkreten Maßnahmen an Ihrem Gebäude? Antworten Sie einfach auf diese Mail!
> 
> Herzliche Grüße  
> **Ihr Team von HK Energieberatung**

---

### 📩 E-Mail 2: Kostenlose Fördermittel-Vorprüfung
* **Versand:** Tag 4 nach Download
* **Betreff:** `Welche Förderquote passt zu Ihrem Baujahr?`
* **Vorschautext:** `Lassen Sie uns unverbindlich prüfen, welche BAFA/KfW-Töpfe für Sie bereitstehen.`

> Hallo {{vorname}},
> 
> die Förderlandschaft in Deutschland ändert sich schnell. Welche Programme sich für Ihr Gebäude am meisten lohnen, hängt stark vom Baujahr, der aktuellen Heizung und den geplanten Maßnahmen ab.
> 
> Als zertifizierte Energieeffizienz-Experten bieten wir Eigentümern in Bremen und Niedersachsen eine **kostenlose Fördermittel-Vorprüfung** an:
> - Wir analysieren kurz Ihre Gebäudedaten.
> - Wir berechnen Ihren maximalen Zuschuss (BAFA / KfW).
> - Wir zeigen Ihnen den schnellsten Weg zur Auszahlung.
> 
> 👉 **[Kostenlose Fördermittel-Vorprüfung anfragen](https://hk-energieberatung.de/#contact)**
> 
> Beste Grüße  
> **Wajih Tfaili**

---

### 📩 E-Mail 3: Einladung zum Vor-Ort-Erstgespräch
* **Versand:** Tag 8 nach Download
* **Betreff:** `Sollen wir Ihr Haus gemeinsam anschauen?`
* **Vorschautext:** `Kostenloses Erstgespräch, Anfahrt inklusive – ganz unverbindlich.`

> Hallo {{vorname}},
> 
> haben Sie die Checkliste schon durchgesehen? Wenn Sie möchten, schauen wir uns Ihr Gebäude in einem kostenlosen Erstgespräch gemeinsam an – die Anfahrt ist bundesweit inklusive.
> 
> 👉 **[Kostenloses Erstgespräch anfragen](https://hk-energieberatung.de/#contact)**
> 
> Beste Grüße  
> **Hussein Khashab**

---

## 📊 2. Key Performance Indicators (KPI-Benchmarks)

| Kennzahl | Ziel-Benchmark (B2C & B2B Immobilien) | Optimierungshebel |
| :--- | :---: | :--- |
| **Öffnungsrate (Open Rate)** | **$\ge 48\%$** | Personalisierte, konkrete Betreffzeilen (z. B. mit Adressbezug) |
| **Klickrate (CTR)** | **$\ge 8.5\%$** | Ein klarer Button / Textlink pro E-Mail |
| **Antwortrate (Reply Rate)** | **$\ge 5.0\%$** | Frage-Endung (*„Sollen wir kurz sprechen?“*) |
| **Abmelderate (Unsubscribe)** | **$\le 0.4\%$** | Hohe Relevanz, Mehrwert vor Verkaufsdruck |

---

## 🔗 Verknüpfte Dokumente
- [[B2B Cold Email & Kooperations-Outreach Playbook|B2B Cold Outreach Playbook]]
- [[A-B Testing & Experimentation Playbook|A/B Testing & Conversion Playbook]]
- [[HK Energieberatung - Unternehmensprofil & Brand Context|Unternehmensprofil & Brand Context]]
- [[Kanban Hk Energieberatung|Projekt Kanban Board]]
