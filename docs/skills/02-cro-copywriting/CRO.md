
# 📈 Conversion Rate Optimization (CRO) Audit: `index.html`

Ziel der Startseite ist die Generierung von qualifizierten Sanierungs-Leads (Einfamilien-/Mehrfamilienhausbesitzer) und direkten Expressausweis-Bestellungen.

---

## 🔍 Die 5 größten Conversion-Bremsen auf `index.html`

### 1. ⚠️ Schwache Hero-Value-Proposition (Above the Fold)
* **Aktueller Zustand**: Die Überschrift *„Ihre Energieberater in Norddeutschland – Jetzt Energie sparen & Förderung sichern!“* ist generisch. Sie sagt dem Besucher nicht in den ersten 5 Sekunden, **wie viel Geld** er spart oder **welche konkrete Förderung** er erhält.
* **CRO-Verlust**: Besucher springen ab, weil der wirtschaftliche Hebel (bis zu 70% KfW / 50% BAFA) nicht sofort greifbar ist.
* **Optimierung**: Spezifische Zahlen und offizielle Zertifizierung direkt in die `<h1>` setzen.

---

### 2. 🛡️ Fehlende Vertrauensbeweise & Qualitätssiegel im oberen Sichtbereich
* **Aktueller Zustand**: Das offizielle **dena-Zertifikatssiegel** ist im Footer platziert. Im Hero-Bereich gibt es nur eine abstrakte SVG-Grafik (`undraw_smart-home`).
* **CRO-Verlust**: Bei Investitionen von 10.000 € bis 80.000 € (Heizung/Sanierung) ist **Vertrauen das Kriterium Nr. 1**.
* **Optimierung**: Offizielles Siegel (*„dena Energieeffizienz-Experten für Förderprogramme des Bundes“*) und die geschützten Titel *„Bauingenieure“* direkt im Header/Hero verankern.

---

### 3. 🎯 Fehlende Handlungs-Hierarchie (Dual CTA)
* **Aktueller Zustand**: Es gibt nur einen einzigen Button (*„Kostenloses Erstgespräch“*).
* **CRO-Verlust**: Besucher haben zwei unterschiedliche Absichten:
  1. **Großes Vorhaben / Sanierungsplanung**: Brauchen Beratung (Erstgespräch / iSFP).
  2. **Dringende Pflicht / Vermietung / Verkauf**: Brauchen **sofort** einen Energieausweis.
* **Optimierung**: **Zwei klare Pfade anbieten**:
  - `[ Kostenloses Erstgespräch anfordern ]` *(Primärer Button)*
  - `[ Expressausweis in 48h bestellen → ]` *(Sekundärer Button)*

---

### 4. 💰 Förder-Tabs (`#features`): Zu technisch, zu wenig Nutzen-Fokus
* **Aktueller Zustand**: In den Tabs für *iSFP*, *BAFA* und *KfW* stehen informative Texte, aber die **konkreten Euro- & Prozent-Zuschüsse** stechen optisch nicht hervor.
* **Optimierung**: Jedes Tab mit einer **Highlight-Kennzahl** ausstatten (z. B. `50% BAFA-Zuschuss`, `+5% iSFP-Bonus`, `Bis zu 70% Heizungstausch`).

---

### 5. 📝 Kontaktformular: Mangelnde Reassurance bei der Absendung
* **Aktueller Zustand**: Der Button heißt *„Nachricht senden“* und es fehlen direkte Garantien gegen Spam/Wartezeit.
* **Optimierung**:
  - Button-Text: `Kostenloses Erstgespräch anfragen →`
  - Trust-Zeile direkt unter dem Button: `🔒 100% kostenfrei & unverbindlich • Rückmeldung garantiert innerhalb von 24 Stunden • Keine Weitergabe von Daten`

---

## 🚀 Sofort umsetzbare Quick Wins (Top 3)

```diff
--- a/index.html (Hero-Bereich)
+++ b/index.html (Optimierter Hero-Bereich)

- <div class="company-badge mb-4"><i class="bi bi-gear-fill me-2"></i> Wir arbeiten für Ihren Erfolg</div>
- <h1 class="mb-4">Ihre Energieberater in Norddeutschland</h1>
- <h2 class="mb-2 text-base">Jetzt Energie sparen & <br><span class="accent-text">Förderung sichern!</span></h2>

+ <div class="company-badge mb-4"><i class="bi bi-patch-check-fill me-2" style="color: #66A66D;"></i> Zertifizierte dena Energieeffizienz-Experten</div>
+ <h1 class="mb-3" style="font-size: 2.5rem; font-weight: 800; line-height: 1.2;">Bis zu 70% staatliche Förderung sichern & Heizkosten dauerhaft senken</h1>
+ <p class="lead mb-4 text-muted" style="font-size: 1.1rem;">Unabhängige Energieberatung & Sanierungsfahrpläne (iSFP) durch Bauingenieure in Bremen & Norddeutschland. 50% BAFA-Zuschuss auf Ihr Gutachten.</p>

  <div class="hero-buttons mt-4 d-flex flex-wrap gap-3">
-   <a href="#contact" class="btn btn-hk btn-hk-lg me-0 me-sm-2 mx-1">Kostenloses Erstgespräch</a>
+   <a href="#contact" class="btn btn-hk btn-hk-lg">Kostenloses Erstgespräch anfordern</a>
+   <a href="expressausweis.html" class="btn btn-hk-outline btn-hk-lg">Expressausweis (48h) <i class="bi bi-arrow-right ms-1"></i></a>
  </div>
```

---

## 🧪 Empfohlene A/B-Tests

| Test-ID | Element | Variante A (Kontrolle) | Variante B (Challenger) | Ziel-Metrik |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | Hero Headline | *„Ihre Energieberater in Norddeutschland“* | *„Bis zu 70% Förderung sichern & Heizkosten dauerhaft senken“* | Scroll-Tiefe & Formular-Absendungen (+25%) |
| **EXP-02** | Hero CTA | Nur *„Kostenloses Erstgespräch“* | Dual CTA: *„Erstgespräch“* + *„Expressausweis (48h)“* | Klickrate auf Kern-Aktionen (+35%) |
| **EXP-03** | Formular-Button | *„Nachricht senden“* | *„Kostenloses Erstgespräch unverbindlich anfragen“* | Formular-Abschlussrate (+18%) |

---

### 🛠️ Nächster Schritt:
Möchtest du, dass wir diese **CRO-Optimierungen (Hero-Text, Dual CTA, Trust-Signale und Formular-Reassurance)** direkt in [`index.html`](file:///c:/Users/super/Desktop/Hk%20Energieberatung/index.html) einarbeiten?