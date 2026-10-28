# Footer Redesign Specifications

## Goal
Streamline and balance the site footer structure for HK Energieberatung to remove template boilerplate, ensure equal column height distribution, and provide comprehensive navigation to all key services and locations.

## Design Breakdown (Option A: 4 Balanced Columns)

### Column 1: Company Profile & Contact (`col-lg-4 col-md-6`)
- HK Energieberatung Logo
- Address: `Industriestraße 34, 28199 Bremen - Deutschland`
- Phone: `+49 162 6985115`
- E-Mail: `info@hk-energieberatung.de`
- Social Links: Instagram & LinkedIn
- Google "Preferred Source" button (dark theme)

### Column 2: Navigation & Menü (`col-lg-3 col-md-3`)
- Startseite (`/#hero`)
- Über uns (`about.html`)
- Standort Bremen (`energieberatung-bremen.html`)
- Standort Aurich (`energieberatung-aurich.html`)
- Mediathek (`mediathek.html`)
- Dokumente & Downloads (`dokumente.html`)
- Häufige Fragen (FAQ) (`faq.html`)
- Kontakt (`/#contact`)

### Column 3: Unsere Leistungen (`col-lg-3 col-md-3`)
- Express Verbrauchsausweis (48h) (`expressausweis.html`)
- Fördermittel-Rechner (BEG 2026) (`forderrechner.html`)
- Energieausweise (`/#services`)
- BAFA & KfW Förderungen (`/#features`)
- KfW Kreditanträge (`/#services`)

### Column 4: Erreichbarkeit & Direktkontakt (`col-lg-2 col-md-3`)
- Öffnungszeiten: Montag - Samstag (9:00 Uhr bis 18:00 Uhr)
- WhatsApp-Chat Direct Link (`https://wa.me/491626985115`)

### Copyright & Legal Bar
- Copyright statement
- Impressum & Datenschutz links
- Cookie-Einstellungen link
- Developer credit (Masri Systems)

## Affected Files
- `components/footer.html`
- `assets/js/components.js`
- `scripts/sync-components.js`
- All static HTML pages (`index.html`, `about.html`, `expressausweis.html`, `energieberatung-bremen.html`, `energieberatung-aurich.html`, `mediathek.html`, `faq.html`, `impressum.html`, `datenschutz.html`)
