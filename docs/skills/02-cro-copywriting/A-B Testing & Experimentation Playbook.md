---
title: HK Energieberatung - A/B Testing & Growth Experimentation Playbook
client: Hussein Khashab & Wajih Tfaili
company: HK Energieberatung
location: Bremen, Norddeutschland
last_updated: 2026-08-08
status: Active
tags:
  - client/hussein-khashab
  - project/hk-energieberatung
  - ab-testing
  - cro
  - growth-experiments
  - conversion-optimization
---

# 🧪 HK Energieberatung – A/B Testing & Experimentation Playbook

Dieses Playbook dokumentiert das systematische Wachstums- und Experimentier-Framework für die Website von **HK Energieberatung** ([hk-energieberatung.de](https://hk-energieberatung.de/)). Es dient als Handlungsleitfaden zur statistisch fundierten Steigerung der Conversion-Rate auf [[index.html|Startseite]], Expressausweis, Standort-Seiten (Bremen, Aurich) und Kontaktflows.

---

## 🎯 1. Conversion-Ziele & Funnel-Architektur

Die Website verfolgt **3 primäre Conversion-Pfade**:

```
                                  [ Website-Besucher ]
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        ▼                                   ▼                                   ▼
 [ Pfad 1: High-Ticket ]           [ Pfad 2: Low-Ticket ]             [ Pfad 3: Sofortkontakt ]
 Sanierungsberatung & iSFP         Express-Verbrauchsausweis         WhatsApp-Chat & Telefon
 • Ziel: Lead-Formular (#contact)  • Ziel: Online-Kauf (ab 79 €)      • Ziel: Direkter Klick
 • Wert: 650 € - 3.500 € Honorar   • Wert: Sofortiger Cashflow        • Wert: Schnelle Vorqualifikation
```

---

## 📊 2. Priorisierte Experiment-Backlog-Matrix (ICE-Scoring)

Jedes Experiment wird nach der **ICE-Methode** (Impact, Confidence, Ease) von 1 bis 10 bewertet:
$$\text{ICE-Score} = \frac{\text{Impact} + \text{Confidence} + \text{Ease}}{3}$$

| ID         | Experiment-Fokus                                                           | Primäre Zielmetrik                          | Impact | Confidence | Ease | **ICE-Score** | Status    |
| :-----------| :---------------------------------------------------------------------------| :--------------------------------------------| :------:| :----------:| :----:| :-------------:| :---------:|
| **EXP-01** | **Hero Section: Spezifisches Nutzenversprechen & Dual-CTA**                | Formular-Starts & Express-Klicks            | 9      | 8          | 9    | **8.7**       | 🟢 Bereit  |
| **EXP-02** | **Expressausweis-Banner: Value-CTA („ab 79 €“) statt „Klicke hier“**       | Klickrate zu `expressausweis.html`          | 8      | 9          | 9    | **8.7**       | 🟢 Bereit  |
| **EXP-03** | **dena-Qualitätssiegel & 100% Fördergarantie Above-the-Fold**              | Absprungrate (Bounce) & Erstgespräch-CTR    | 8      | 8          | 8    | **8.0**       | 🟡 Geplant |
| **EXP-04** | **Stats-Row: Garantierte Förderquoten („Bis zu 70%“) statt Bulletpoints**  | Scroll-Tiefe & Formular-Absendungen         | 7      | 8          | 9    | **8.0**       | 🟡 Geplant |
| **EXP-05** | **Kontaktformular: 2-Schritt-Mikro-Formular statt langem Standard-Form**   | Formular-Abschlussrate (`lead_form_submit`) | 9      | 7          | 7    | **7.7**       | ⚪ Backlog |
| **EXP-06** | **Floating WhatsApp Chat: Pulsierender Hilfetext („In 2 Min. antworten“)** | WhatsApp-Interaktionen (`wp_chat_click`)    | 7      | 8          | 8    | **7.7**       | ⚪ Backlog |

---

## 🔬 3. Detaillierte Experiment-Spezifikationen

---

### 🧪 EXP-01: Hero Section – Spezifisches Nutzenversprechen & Dual-CTA

#### Hypothese:
> **Weil** Besucher der Startseite innerhalb von 3 Sekunden die konkrete finanzielle Ersparnis und zwei unterschiedliche Handlungspfade (Sanierungsberatung vs. schneller Ausweis) benötigen,  
> **glauben wir**, dass eine zahlenbasierte Überschrift (*„Bis zu 70% Förderung sichern“*) in Kombination mit einem **Dual-CTA** (*„Kostenloses Erstgespräch“* + *„Expressausweis in 48h (79 €)“*)  
> **die Gesamtzahl der Anfragen um mindestens +25% steigern wird**.  
> **Wir wissen, dass dies zutrifft, wenn** die Klickrate auf die Hero-Aktionsbuttons von ~4.2% auf >6.5% ansteigt.

#### Varianten-Spezifikation:
* **Control (A):**
  - **H1:** `Ihre Energieberater in Norddeutschland`
  - **H2:** `Jetzt Energie sparen & Förderung sichern!`
  - **CTA:** Einzellink `[ Kostenloses Erstgespräch ]`
* **Variant (B):**
  - **H1:** `Bis zu 70% staatliche Förderung für Ihre Sanierung sichern`
  - **H2:** `Zertifizierte Energieeffizienz-Experten & Bauingenieure in Bremen & ganz Norddeutschland. Wir erstellen Ihren iSFP-Sanierungsfahrplan und sichern maximale Zuschüsse.`
  - **Dual CTA:**
    - Primär: `<a href="#contact" class="btn btn-hk btn-hk-lg">Kostenlose Erstberatung anfragen</a>`
    - Sekundär: `<a href="expressausweis.html" class="btn btn-hk btn-hk-lg btn-hk-outline">Expressausweis in 48h (ab 79 €) →</a>`

---

### 🧪 EXP-02: Expressausweis-Banner – Action- & Preistransparenter CTA

#### Hypothese:
> **Weil** der Text *„Klicke hier“* generisch wirkt und weder den Festpreis noch die Bearbeitungszeit kommuniziert,  
> **glauben wir**, dass ein transparenter, nutzenorientierter Button (*„Jetzt Expressausweis in 48h bestellen – ab 79 €“*)  
> **die Klickrate auf `expressausweis.html` um mindestens +35% erhöht**.

#### Varianten-Spezifikation:
* **Control (A):**
  ```html
  <a href="expressausweis.html" class="btn btn-hk btn-hk-md">Klicke hier <i class="bi bi-arrow-right ms-1"></i></a>
  ```
* **Variant (B):**
  ```html
  <a href="expressausweis.html" class="btn btn-hk btn-hk-md">
    <span>Jetzt Expressausweis in 48h beantragen – ab 79 €</span>
    <i class="bi bi-arrow-right ms-2"></i>
  </a>
  ```

---

### 🧪 EXP-03: Above-the-Fold Social Proof & dena-Zertifikatssiegel

#### Hypothese:
> **Weil** Vertrauen und offizielle dena-Akkreditierung bei Sanierungsentscheidungen (10.000 € – 80.000 €) das stärkste Kaufkriterium sind,  
> **glauben wir**, dass die prominente Einbindung des dena-Siegels und der Berufsbezeichnung *„Bauingenieure & Energieeffizienz-Experten des Bundes“* direkt im Hero-Bereich  
> **die Absprungrate (Bounce Rate) um -15% senkt** und die Vertrauensmetriken stärkt.

#### Varianten-Spezifikation:
* **Control (A):**
  - Company-Badge: `<div class="company-badge"><i class="bi bi-gear-fill"></i> Wir arbeiten für Ihren Erfolg</div>`
* **Variant (B):**
  - Company-Badge: `<div class="company-badge"><i class="bi bi-patch-check-fill text-success"></i> Offiziell zertifizierte dena Energieeffizienz-Experten des Bundes</div>`
  - Trust-Row direkt unter den Buttons: `✓ 100% Förderquote • ✓ Anfahrt inklusive • ✓ Kostenlose Erstberatung`

---

## 📈 4. Messplan & Tracking-Architektur

### Event-Definitionen für Google Analytics 4 (GA4) & Tag Manager:

> **Implementierungsstand:** Aktuell sind nur `ab_test_impression` (`assets/js/ab-test.js`, Experiment `landing_v1_vs_v2`) und `generate_lead` (`assets/js/main.js`, Formular-Absendung) live. Die unten gezeigten Events `experiment_impression`, `hero_cta_primary_click`, `express_cta_click` und `lead_form_submitted` sind **geplantes Soll-Tracking** und noch nicht implementiert.

```javascript
// 1. Event beim Laden der Test-Variante
gtag('event', 'experiment_impression', {
  'experiment_id': 'exp01_hero_dual_cta',
  'variant_id': 'variant_b'
});

// 2. Event beim Klick auf Hero Primär-CTA
gtag('event', 'hero_cta_primary_click', {
  'button_text': 'Kostenlose Erstberatung anfragen',
  'experiment_id': 'exp01_hero_dual_cta',
  'variant_id': 'variant_b'
});

// 3. Event beim Klick auf Expressausweis-CTA
gtag('event', 'express_cta_click', {
  'location': 'hero_dual_cta',
  'experiment_id': 'exp01_hero_dual_cta',
  'variant_id': 'variant_b'
});

// 4. Primary Conversion Event (Lead-Formular)
gtag('event', 'lead_form_submitted', {
  'form_id': 'kontaktForm',
  'service_interest': 'iSFP_Sanierung',
  'experiment_id': 'exp01_hero_dual_cta',
  'variant_id': 'variant_b'
});
```

---

## 📐 5. Stichprobengröße & Statistische Signifikanz

Zur Vermeidung von *False Positives* (Alpha-Fehler) und dem *Peeking-Problem* gelten folgende Parameter:

* **Signifikanzniveau ($\alpha$):** $95\%$ ($p < 0.05$)
* **Power ($1 - \beta$):** $80\%$
* **Baseline Conversion-Rate:** $\approx 3.0\%$
* **Minimum Detectable Effect (MDE):** $+25\%$ relative Steigerung (Ziel: $\ge 3.75\%$)
* **Benötigte Stichprobengröße:** **ca. 2.400 Besucher pro Variante** (Gesamt: 4.800 Sessions).
* **Feste Laufzeit:** 2 bis 4 Kalenderwochen (vollständige Zyklen inklusive Wochenenden).

> [!IMPORTANT]
> **Anti-Peeking-Regel:** Tests dürfen vor Erreichen der vollen Stichprobengröße nicht vorzeitig gestoppt werden, auch wenn Zwischenergebnisse nach wenigen Tagen einen scheinbaren Gewinner zeigen.

---

## 💻 6. Client-Side A/B Testing Snippet (Zero-Flicker)

Dieses modulare Script kann direkt über `assets/js/main.js` oder den Google Tag Manager eingebunden werden:

```javascript
/**
 * HK Energieberatung - Lightweight A/B Testing Engine
 */
(function initABTesting() {
  const EXP_KEY = 'hk_exp_hero_v1';
  let variant = localStorage.getItem(EXP_KEY);

  if (!variant) {
    variant = Math.random() < 0.5 ? 'control' : 'variant_b';
    localStorage.setItem(EXP_KEY, variant);
  }

  // Event an GA4 senden
  if (typeof gtag === 'function') {
    gtag('event', 'experiment_view', {
      'experiment_name': 'exp01_hero_headline_cta',
      'variant': variant
    });
  }

  // DOM-Mutationen nur für Variante B anwenden
  if (variant === 'variant_b') {
    document.addEventListener('DOMContentLoaded', function() {
      const heroHeadline = document.querySelector('#hero h1');
      const heroSub = document.querySelector('#hero h2');
      const heroButtons = document.querySelector('.hero-buttons');
      const companyBadge = document.querySelector('.company-badge');

      if (companyBadge) {
        companyBadge.innerHTML = '<i class="bi bi-patch-check-fill me-2 text-success"></i> Zertifizierte dena Energieeffizienz-Experten des Bundes';
      }
      if (heroHeadline) {
        heroHeadline.textContent = 'Bis zu 70% staatliche Förderung sichern';
      }
      if (heroSub) {
        heroSub.innerHTML = 'Zertifizierte Energieberater & Bauingenieure in <span class="accent-text">Bremen & Norddeutschland</span>';
      }
      if (heroButtons) {
        heroButtons.innerHTML = `
          <a href="#contact" class="btn btn-hk btn-hk-lg me-2 mb-2">Kostenlose Erstberatung anfragen</a>
          <a href="expressausweis.html" class="btn btn-hk btn-hk-lg btn-hk-outline mb-2">Expressausweis in 48h (ab 79 €) →</a>
        `;
      }
    });
  }
})();
```

---

## 🔄 7. Experimentation Cadence & Playbook-Rhythmus

1. **Wöchentlich (15 Min.):** Überprüfung der technischen Guardrail-Metriken (Formularfehler, Ladezeiten, Bounce-Rates).
2. **2-wöchentlich / Monatsende:** Statistische Auswertung des abgeschlossenen Tests.
3. **Gewinner-Rollout:** Bei statistischer Signifikanz ($p < 0.05$) wird die Gewinner-Variante fest in den HTML-Quellcode (`index.html`) überführt und das nächste Experiment aus dem Backlog aktiviert.

---

## 🔗 Verknüpfte Dokumente
- [[CRO|CRO-Audit & Conversion-Analyse]]
- [[Conversion-Copywriting-Konzept 'StartSeite'|Conversion-Copywriting Konzept]]
- [[HK Energieberatung - Unternehmensprofil & Brand Context|Unternehmensprofil & Brand Context]]
- [[Kanban Hk Energieberatung|Projekt Kanban Board]]
