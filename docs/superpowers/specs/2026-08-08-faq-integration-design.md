# Design Spec: FAQ Section & Dedicated FAQ Hub (`faq.html`)

## Goal
Implement the 25 comprehensive FAQs from `assets/FAQ-EN~1.HTM.html` into `index.html#faq` and create a dedicated `faq.html` page, complete with category groupings, interactive graphics (Einsparpotenzial bar chart & Energieeffizienzklassen A+-H scale), Bootstrap icons, and pre-rendered header/footer/contact/map components matching `assets/css/main.css`.

## Architecture & Structural Breakdown

### 1. `assets/css/main.css` Extensions
- Style `.faq-chart-card` and `.faq-scale-card` matching design system variables (`--heading-color`, `--accent-color`, `--surface-color`, `.light-background`).
- Style `.faq-category-header` with category icons, titles, and smooth accordion toggle triggers.
- Style `.faq-bar-fill` and `.faq-scale-seg` for visual charts.

### 2. `faq.html` Page Layout
- **Header Component**: Injected via `components/header.html` with active nav link.
- **Page Title Banner**: "Häufige Fragen (FAQ)" header banner with lead intro text.
- **Visual Chart 1 ("Ihr Einsparpotenzial")**: Stat highlight box (bis zu 60% Einsparung) and animated bar chart (Fenstertausch, Hydraulischer Abgleich, Dachdämmung, Fassadendämmung, Wärmepumpe, Komplettsanierung).
- **FAQ Accordion Categories**:
  1. 💡 Allgemeines zur Energieberatung (5 questions)
  2. 📋 Energieausweis (5 questions + **Visual Chart 2: Energieeffizienzklassen A+ bis H**)
  3. 💰 Fördermittel: iSFP, BAFA, KfW (6 questions)
  4. 🔧 Sanierung & Technik (6 questions)
  5. 🤝 Ablauf, Kosten & Zusammenarbeit (3 questions)
- **Contact Component**: Pre-rendered from `components/contact.html`.
- **Map Component**: Google Maps iframe embed.
- **Footer Component**: Pre-rendered from `components/footer.html`.

### 3. `index.html#faq` Section Upgrade
- Refactor `<section id="faq">` in `index.html` to present the 5 categories with smooth Bootstrap accordion behavior and a link/button to `faq.html` for full details.

### 4. Component Synchronization & Nav
- Add `'faq.html'` to `TARGET_FILES` in `scripts/sync-components.js`.
- Update `customizeHeader()` in `scripts/sync-components.js` and `components/header.html` dropdowns/links as applicable.
