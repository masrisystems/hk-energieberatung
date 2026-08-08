# Design Spec: Über Uns Page Redesign & Image Assets Integration

## Goal
Implement the new "Über uns" (About Us) page (`about.html`) based on the `aboutus.jpeg` design mockup, rename and integrate new location and banner image assets, update `energieberatung-aurich.html` location cards, update `index.html#about` section for consistency, and integrate component synchronization via `scripts/sync-components.js`.

## Image Assets Mapping & Renaming
- `assets/img/hkboardjpeg.jpeg` $\rightarrow$ `assets/img/about-banner.jpg`
- `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (1).jpeg` $\rightarrow$ `assets/img/aurich-sign-board.jpg`
- `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (2).jpeg` $\rightarrow$ `assets/img/aurich-center.jpg`
- `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (3).jpeg` $\rightarrow$ `assets/img/bremen-stadtmusikanten.jpg`
- `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM.jpeg` $\rightarrow$ `assets/img/bremen-marktplatz.jpg`

## Page Architecture & Layout (`about.html`)
1. **Header Component**: Synchronized using `components/header.html` with "ÜBER UNS" active.
2. **Page Title Header**: "Über Uns" centered page title banner.
3. **Hero Section ("Unser Team")**:
   - Subtitle: "Erfahren Sie mehr"
   - Title: "Unser Team"
   - Body copy describing founder background in civil engineering (Bauingenieurwesen).
   - Button: "Kostenloses Erstgespräch" linking to `#contact`.
   - Right Column: Scaffolding banner image (`assets/img/about-banner.jpg`).
4. **Founders Section ("Unsere Gründer")**:
   - Light blue surface container (`color-mix` / light-background).
   - Title: "Unsere Gründer".
   - 2 Founder cards:
     - Ing. Hussein Kashab (Bauingenieur und Energieberater).
     - Ing. Wajih Tfaili (Bauingenieur und Energieberater).
5. **Qualifications & Expertise Section ("Was wir mitbringen")**:
   - Title: "Was wir mitbringen".
   - 3 bullet points with custom icons (Fundierte Bau-Expertise, Zertifizierte Spezialisierung, Modernste Analyse-Technik).
   - Closing summary text: "Kurz gesagt: Wir kombinieren den geschulten Blick des Bauingenieurs mit der Präzision moderner Software, um das Maximum aus Ihrem Gebäude herauszuholen."
   - Right Column: Founders photo (`assets/img/about-secondary.png`).
6. **Contact Component**: Pre-rendered from `components/contact.html`.
7. **Standorte Section ("Unsere Standorte")**:
   - Title: "Unsere Standorte".
   - 2 side-by-side location cards:
     - **Standort Bremen**: Dual image layout (`bremen-stadtmusikanten.jpg` + `bremen-marktplatz.jpg`).
     - **Standort Aurich**: Dual image layout (`aurich-sign-board.jpg` + `aurich-center.jpg`).
8. **Map Component**: Embedded Google Map for Bremen office location.
9. **Footer Component**: Pre-rendered from `components/footer.html`.

## Component Synchronization (`scripts/sync-components.js`)
- Add `'about.html'` to `TARGET_FILES` array.
- Update `customizeHeader()` logic to mark `about.html` link active when on `about.html`.
- Run `node scripts/sync-components.js` to pre-render headers, footers, and contact sections across all HTML pages.

## Updates to Existing Pages
1. `energieberatung-aurich.html`: Update the Standort Bremen & Standort Aurich switcher cards to display the new location images.
2. `index.html`: Update `<section id="about">` to match the refreshed copy and design structure from `aboutus.jpeg`.
3. `components/header.html`: Update navigation item "ÜBER UNS" to point to `about.html` (or `index.html#about` anchor as appropriate).

## Design System & Styling Rules
- Use existing Bootstrap 5 grid & utility classes.
- Maintain CSS variables from `assets/css/main.css` (`--accent-color`, `--heading-color`, `--surface-color`, etc.).
- Ensure responsive breakpoints (mobile, tablet, desktop) and smooth AOS animation delays (`data-aos="fade-up"`).
