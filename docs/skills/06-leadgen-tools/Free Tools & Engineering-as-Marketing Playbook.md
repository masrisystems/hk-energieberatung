---
title: HK Energieberatung - Free Tools & Engineering-as-Marketing Playbook
client: Ing. Hussein Khashab & Ing. Wajih Tfaili
company: HK Energieberatung
location: Bremen & Aurich, Norddeutschland
last_updated: 2026-08-14
status: Active / In Production
version: 2.1.0
tags:
  - client/hussein-khashab
  - project/hk-energieberatung
  - free-tools
  - engineering-as-marketing
  - interactive-calculators
  - lead-generation
  - beg-reform-2026
  - seo-assets
---

# 🧮 HK Energieberatung – Free Tools & Engineering-as-Marketing Playbook

Dieses Playbook definiert die strategische Konzeption, mathematische Berechnungslogik, Lead-Generation-Architektur und Distribution der interaktiven **Free Tools & Software-Assets** von **HK Energieberatung**.

Durch interaktive Rechner (insbesondere die produktionsreife Web-App `forderrechner.html`) verwandelt HK Energieberatung passive Website-Besucher in hochqualifizierte, beratungsbereite Sanierungs-Leads, sichert sich erstklassige Backlinks und etabliert einen uneinholbaren technologischen Vorsprung gegenüber traditionellen regionalen Energieberatern.

---

## 🎯 1. Die 3 interaktiven Free Tools im Überblick

```
                           [ Interaktive Free Tools Portfolio ]
                                            │
       ┌────────────────────────────────────┼────────────────────────────────────┐
       ▼                                    ▼                                    ▼
[ Tool 1: BEG Fördermittelrechner ]  [ Tool 2: Energieausweis-Check ]  [ Tool 3: Heizkosten-Ersparnis ]
• Datei: forderrechner.html          • Datei: expressausweis.html      • Integration: forderrechner.html
• Ziel: High-Ticket iSFP-Leads       • Ziel: Sofortkauf Verbrauchsausweis • Ziel: Problem-Aware Sanierer
• Nutzen: Live-Zuschuss in Euro      • Nutzen: 60s GEG-Rechtssicherheit  • Nutzen: Jährliche Kostenersparnis
• Typ: Multi-Measure Full-App        • Typ: 3-Klick Decision Tester     • Typ: Multiplikativer Amortisations-Visualizer
```

---

## 🔬 2. Flagship Tool 1: „Interaktiver BAFA & KfW Fördermittel- & Einsparrechner 2026“ (`forderrechner.html`)

* **Dateipfad:** `c:\Users\super\Desktop\Hk Energieberatung\forderrechner.html`
* **Live-URL:** `https://hk-energieberatung.de/forderrechner.html`
* **SEO-Ziel-Keywords:** `bafa förderrechner 2026`, `kfw 458 zuschuss rechner`, `sanierungsförderung berechnen bremen`, `heizungstausch förderung rechner`, `isfp bonus berechnen`
* **Technologie-Stack:** 100% Vanilla JavaScript (Zero Dependencies), Responsive CSS3 Grid & Flexbox, Google Fonts *Nunito / Roboto / Inter* (Site-Design-System), Dynamic Shimmer Progress Bars, Interactive KPI Engine.
* **Gating-Modell:** **Partially Gated** (Echtzeit-Berechnung & Live-Visualisierung 100% frei; ausführlicher PDF-Förderbericht & Terminbuchung zur Fördermittelbeantragung als Lead-Schranke).

```
                      [ Lead Generation Flywheel ]
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
[ 1. Traffic ]             [ 2. Simulation ]            [ 3. Konvertierung ]
Google Ads Search & SEO    Sofortige Live-Berechnung    Klick auf "Förderbericht"
Target: "BAFA Förderrechner" von Zuschuss & Heizkosten   Vorqualifizierter Lead an CRM
```

---

### ⚙️ 2.1 Mathematische Berechnungslogik & BEG-Regelwerk 2026

Der Rechner bildet die aktuellen Richtlinien der **Bundesförderung für effiziente Gebäude (BEG)** exakt ab – inklusive der **BEG-Reform vom 21.07.2026**:

#### A. Heizungstausch (KfW Heizungsförderung 458)
Die Förderung für regenerative Heizsysteme (Wärmepumpe, Biomasse, Fernwärmeanschluss) errechnet sich additiv aus mehreren Bausteinen:

1. **Grundförderung:** $30\%$ für alle Eigentümer (auch Vermieter).
2. **Klimageschwindigkeitsbonus:** $+16\%$ bei Austausch einer funktionstüchtigen Öl-, Kohle-, Nachtspeicher- oder mindestens 20 Jahre alten Gasheizung (nur für selbstnutzende Eigentümer).
3. **Einkommensbonus:** Gestaffelter Zuschuss für selbstnutzende Eigentümer anhand des zu versteuernden Haushaltsjahreseinkommens:
   * Bei Haushalten **ohne minderjährige Kinder**:
     - $\le 30.000\text{ €}$: $+40\%$ Bonus
     - $30.001\text{ €} - 40.000\text{ €}$: $+30\%$ Bonus
     - $40.001\text{ €} - 50.000\text{ €}$: $+10\%$ Bonus
   * Bei Haushalten **mit mindestens einem minderjährigen Kind** (Erhöhung der Freigrenzen um $+10.000\text{ €}$ je Stufe):
     - $\le 40.000\text{ €}$: $+40\%$ Bonus
     - $40.001\text{ €} - 50.000\text{ €}$: $+30\%$ Bonus
     - $50.001\text{ €} - 60.000\text{ €}$: $+10\%$ Bonus
4. **Höchstfördersatz (Kappungsgrenze):**
   * Maximal $70\%$ (ohne Einkommensbonus).
   * Maximal $80\%$ (bei greifender Einkommensförderung).
5. **Förderfähige Höchstkosten für Heizungstausch (degressiv nach Wohneinheiten):**
   $$\text{MaxKosten}_{\text{Heizung}} = 28.000\text{ €} + (N_{\text{WE 2..6}} \times 15.000\text{ €}) + (N_{\text{WE 7+}} \times 8.000\text{ €})$$

---

#### B. Einzelmaßnahmen Gebäudehülle, Fenster & Anlagentechnik (BAFA BEG EM)
Für Dämmung (Fassade, Dach, Kellerdecke, oberste Geschossdecke), Fenstertausch, Außentüren und Anlagentechnik (Lüftung mit WRG, hydraulischer Abgleich, Rohrdämmung) gilt:

1. **Basisfördersatz:** $15\%$ der förderfähigen Ausgaben.
2. **Förderfähige Höchstgrenze:** $60.000\text{ €}$ je Wohneinheit und Kalenderjahr.
3. **BEG-Reform vom 21.07.2026 (Splitting des iSFP-Bonus):**
   * Liegt ein **individueller Sanierungsfahrplan (iSFP)** vor, erhöht sich der Fördersatz um $+5\%$ (auf $20\%$), jedoch **ausschließlich für den Kostenanteil oberhalb von 30.000 €**!
   * Mathematische Zuschussformel für Einzelmaßnahmen:
     $$\text{Zuschuss}_{\text{EM}} = (\min(\text{Invest}_{\text{EM}}, 30.000\text{ €}) \times 0{,}15) + (\max(0, \min(\text{Invest}_{\text{EM}}, 60.000\text{ €}) - 30.000\text{ €}) \times 0{,}20)$$
   * **Praxis-Beispiel bei 60.000 € Investition mit iSFP:**
     - $30.000\text{ €} \times 15\% = 4.500\text{ €}$
     - $30.000\text{ €} \times 20\% = 6.000\text{ €}$
     - **Gesamtzuschuss:** $10.500\text{ €}$ (effektiver Mischfördersatz: $17{,}5\%$).
   * Der Rechner blendet bei Überschreiten der $30.000\text{ €}$-Schwelle automatisch eine dynamische Erläuterungsbox ein, die dem Nutzer die exakte Aufteilung transparent vorrechnet.

---

#### C. Multiplikatives Heizkosten- und Energieeinsparungsmodell
Um unlogische Additionen (>100% Einsparung) zu vermeiden, nutzt der Rechner ein physikalisch korrektes **multiplikatives Restwärmebedarfs-Modell**:

$$\text{Restkosten}_{\text{neu}} = \text{Heizkosten}_{\text{aktuell}} \times \prod_{i \in \text{aktiv}} (1 - s_i)$$

$$\text{Ersparnis in Euro/Jahr} = \text{Heizkosten}_{\text{aktuell}} - \text{Restkosten}_{\text{neu}}$$

$$\text{Prozentuale Gesamtersparnis} = \left(1 - \prod_{i \in \text{aktiv}} (1 - s_i)\right) \times 100$$

##### Einsparmatrix je Einzelmaßnahme ($s_i$):
| Kategorie | Maßnahme / Sub-Technik | Standard-Kosten | Einsparfaktor ($s_i$) |
| :--- | :--- | :---: | :--- |
| **Heizungstausch** | Wärmepumpe | 22.000 € | Öl: 45% · Gas: 35% · Nachtspeicher: 55% |
| **Heizungstausch** | Biomasse (Pellet / Hackschnitzel) | 19.000 € | Öl: 35% · Gas: 25% · Nachtspeicher: 40% |
| **Heizungstausch** | Fernwärmeanschluss | 12.000 € | Öl: 30% · Gas: 20% · Nachtspeicher: 35% |
| **Fassadendämmung** | WDVS (Vollwärmeschutz außen) | 18.000 € | 20% |
| **Fassadendämmung** | Einblasdämmung (Kerndämmung) | 6.000 € | 15% |
| **Fassadendämmung** | Innendämmung (z. B. Denkmalschutz)| 12.000 € | 14% |
| **Dachdämmung** | Aufsparrendämmung | 20.000 € | 16% |
| **Dachdämmung** | Zwischensparrendämmung | 9.000 € | 12% |
| **Dachdämmung** | Flachdachdämmung | 14.000 € | 13% |
| **Keller & Decken**| Kellerdeckendämmung | 5.000 € | 7% |
| **Keller & Decken**| Perimeterdämmung (Bodenplatte) | 9.000 € | 5% |
| **Keller & Decken**| Oberste Geschossdeckendämmung | 3.500 € | 6% |
| **Fenster & Türen**| 3-fach Wärmeschutzverglasung | 14.000 € | 10% |
| **Fenster & Türen**| Außentüren erneuern | 4.000 € | 2% |
| **Anlagentechnik** | Lüftungsanlage mit WRG | 9.000 € | 5% |
| **Anlagentechnik** | Heizungsoptimierung (Hydr. Abgl.) | 1.500 € | 10% |
| **Anlagentechnik** | Dämmung von Heizungsrohren | 800 € | 3% |

---

### 🎨 2.2 UI/UX Design System & Komponenten (`forderrechner.html`)

* **Typografie:** Google Font `League Spartan` (Gewichte 400, 500, 600, 700, 800) – passend zum modernen Corporate Design von HK Energieberatung.
* **Farbpalette:**
  - Primär/Marke: `--mint: #abd8c3`, `--mint-mid: #62b78f`, `--mint-deep: #387a5b`
  - Kontrast/Texte: `--navy: #1e2a4a`
  - Akzente/Warnungen: `--amber: #d97706`
  - Hintergründe/Karten: `--bg: #f8faf9`, `--card: #ffffff`, `--border: #e6ece8`
* **Layout:**
  - **Linke Spalte (Inputs):** Allgemeine Gebäudedaten, Range Slider, interaktive Toggles für Selbstnutzer/Kind/iSFP, einklappbare Maßnahmengruppen mit dynamischen Zählern.
  - **Rechte Spalte (Sticky Results):** Große Gesamtzuschuss-Zahl, 4er KPI-Grid (Investition, Ø Fördersatz, Eigenanteil, Anzahl Maßnahmen), Shimmer-Balken, Vorher/Nachher-Heizkosten-Säulendiagramm.
* **Micro-Interactions:** Sanfte CSS Transitions (`cubic-bezier(.22,1,.36,1)`), Shimmer-Animationen auf den Förderbalken, dynamische Anpassung von Text-Kontrastfarben auf aktiven Balken.

---

## ⚡ 3. Tool 2: „GEG-Energieausweis-Check (60-Sekunden-Selector)“

* **SEO-Ziel-Keywords:** `energieausweis pflicht prüfen`, `welcher energieausweis für mein haus`, `verbrauchsausweis oder bedarfsausweis test`
* **Platzierung:** Auf `expressausweis.html` und als interaktiver Teaser auf `index.html`.
* **3-Klick Decision Engine:**
  1. *Frage 1:* Wie viele Wohneinheiten hat das Gebäude? ($\ge 5\text{ WE} \to$ **Verbrauchsausweis zulässig** ✅).
  2. *Frage 2:* Wann wurde der Bauantrag gestellt? (Nach 01.11.1977 $\to$ **Verbrauchsausweis zulässig** ✅).
  3. *Frage 3:* Wurde bei Baujahr vor 1977 die Wärmeschutzverordnung 1977 nachträglich erfüllt? (Ja $\to$ **Verbrauchsausweis zulässig** ✅).
* **Sofort-Aktion:** Grüner Erfolgs-Badge + Direkt-CTA zur Online-Bestellung des Expressausweises in 48h für 79 €.

---

## 📉 4. Tool 3: „Sanierungs- & CO₂-Einsparrechner“

* **Fokus:** Visualisierung der 10-Jahres-Amortisation und CO₂-Reduktion für umweltbewusste Sanierer.
* **Ausgabe-KPIs:**
  - Jährliche Heizkosten-Ersparnis in Euro (€)
  - Kumulierte 10-Jahres-Ersparnis inklusive prognostizierter CO₂-Preisanstiege
  - Jährlich eingesparte Tonnen CO₂

---

## 💻 5. Embeddable JavaScript Widget (Zero-Dependency)

Für die nahtlose Einbindung eines schnellen Fördermittel-Teasers auf Unterseiten (`about.html`, `energieberatung-bremen.html`, `energieberatung-aurich.html`):

```javascript
/**
 * HK Energieberatung - Mini Förderrechner Teaser Widget
 * Kann container-basiert in components.js gerendert werden.
 */
function renderFundingCalculatorWidget(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="calculator-card p-4 rounded-4 shadow-sm border" style="background: var(--surface-color, #ffffff); border-color: var(--border, #e6ece8);">
      <div class="d-flex align-items-center gap-2 mb-3">
        <span style="background: #abd8c3; color: #1e2a4a; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">💶</span>
        <h4 class="mb-0 fw-bold" style="color: #1e2a4a;">Fördermittel-Schnellrechner</h4>
      </div>
      <div class="mb-3">
        <label class="form-label fw-bold small text-muted">Geplante Investition:</label>
        <div class="d-flex justify-content-between fw-bold mb-1"><span id="w-invest-val">30.000 €</span></div>
        <input type="range" class="form-range" id="w-calc-invest" min="5000" max="60000" step="5000" value="30000" style="accent-color: #62b78f;">
      </div>
      <div class="mb-3">
        <label class="form-label fw-bold small text-muted">Maßnahme:</label>
        <select class="form-select" id="w-calc-type" style="border-radius: 10px;">
          <option value="0.70">Heizungstausch (bis zu 70% KfW)</option>
          <option value="0.175">Dämmung / Fenster mit iSFP (bis 20% BAFA)</option>
          <option value="0.15">Dämmung / Fenster ohne iSFP (15% BAFA)</option>
        </select>
      </div>
      <div class="p-3 rounded-3 text-center my-3" style="background: rgba(171,216,195,0.35); border: 1px solid rgba(56,122,91,0.25);">
        <span class="small d-block text-muted">Geschätzter staatlicher Zuschuss:</span>
        <h3 class="fw-bold mb-0" id="w-calc-result" style="color: #387a5b;">21.000 €</h3>
      </div>
      <div class="d-grid gap-2">
        <a href="forderrechner.html" class="btn btn-hk btn-hk-primary w-100">Zum vollständigen Förderrechner →</a>
      </div>
    </div>
  `;

  const slider = document.getElementById('w-calc-invest');
  const select = document.getElementById('w-calc-type');
  const resultDisplay = document.getElementById('w-calc-result');
  const investDisplay = document.getElementById('w-invest-val');

  function update() {
    const invest = parseFloat(slider.value) || 0;
    const rate = parseFloat(select.value) || 0;
    const grant = Math.round(invest * rate);
    investDisplay.textContent = invest.toLocaleString('de-DE') + ' €';
    resultDisplay.textContent = grant.toLocaleString('de-DE') + ' €';
  }

  slider.addEventListener('input', update);
  select.addEventListener('change', update);
  update();
}
```

---

## 📈 6. Free-Tool Evaluation Scorecard & ROI-Analyse

| Bewertungskriterium | Score (1-5) | Begründung & Praxiswert |
| :--- | :---: | :--- |
| **Suchnachfrage (Search Demand)** | 5 / 5 | Enorm hohes monatliches Suchvolumen nach KfW-/BAFA-Fördersätzen und Heizungsrechnern. |
| **Zielgruppen-Passung (ICP Match)** | 5 / 5 | Wer konkrete Investitionssummen kalkuliert, ist Eigentümer mit akuter Sanierungsabsicht. |
| **Differenzierung vs. Wettbewerb** | 5 / 5 | Konkurrenten bieten nur statische Tabellen; HK bietet eine vollwertige Multi-Maßnahmen-Simulation. |
| **Natürlicher Pfad zum Produkt (iSFP)** | 5 / 5 | Der Rechner beweist live den finanziellen Mehrwert des iSFP (+5% Bonus ab 30.000 €). |
| **Umsetzbarkeit & Wartungsaufwand** | 5 / 5 | Standalone Vanilla HTML5/CSS3/JS, keine externen Server-Kosten, extrem schnelle Ladezeiten (<300ms). |
| **Backlink- & Virality-Potenzial** | 4 / 5 | Hohe Relevanz für Immobilienportale, Baufinanzierer, Handwerker und regionale Foren. |
| **GESAMT-SCORE** | **29 / 30** | 🏆 **Höchste Priorität für Go-to-Market & Paid Ads Verlinkung** |

---

## 🚀 7. Distributions- & Promotion-Roadmap

1. **Google Ads Kampagnen:**
   - Einbindung von `https://hk-energieberatung.de/forderrechner.html` als direkte **Sitelink-Erweiterung** in der Kampagne `GOOG_Search_iSFP-Sanierung_Bremen-Nord`.
   - Setup einer dedizierten Anzeigengruppe für High-Intent-Suchbegriffe wie *"bafa förderung rechner 2026"* und *"kfw zuschuss wärmepumpe berechnen"*.
2. **On-Site Navigation & Header:**
   - Verlinkung des Rechners unter dem Header-Menüpunkt `Infothek` und `Leistungen`.
   - Footer-Prominenz in der Spalte `Unsere Dienstleistungen & Tools`.
3. **Lokales Partner-Netzwerk (Co-Marketing):**
   - Bereitstellung des Mini-Widgets für lokale Handwerksbetriebe (Sanitär/Heizung/Dachdecker) in Bremen und Aurich zur Einbindung auf deren Websites als Mehrwert-Rechner.
4. **Google Search Console & Schema.org:**
   - JSON-LD Structured Data als `SoftwareApplication` / `WebApplication` für Rich-Snippets in den Google-Suchergebnissen.

---

## 🔗 Verknüpfte Dokumente
- [[Paid Ads Strategy & Kampagnen-Playbook|Paid Ads Strategy & Kampagnen-Playbook]]
- [[Lead Magnet Portfolio & Gating-Strategie|Lead Magnet Portfolio & Gating-Strategie]]
- [[A-B Testing & Experimentation Playbook|A/B Testing Framework]]
- [[HK Energieberatung - Unternehmensprofil & Brand Context|Unternehmensprofil & Brand Context]]
- [[Kanban Hk Energieberatung|Projekt Kanban Board]]
