# Desktop Navigation Redesign Specifications

## Goal
De-clutter and streamline the desktop navigation bar for HK Energieberatung to prevent text wrapping, overcrowded headers, and redundant menu items on desktop displays.

## Current Navigation Structure
- Logo
- ENERGIEBERATUNG (Home hero anchor link)
- ÜBER UNS
- STANDORTE ▾
- EXPRESSAUSWEIS (48H)
- FÖRDERUNGEN
- LEISTUNGEN ▾
- MEDIATHEK
- KONTAKT
- Button: Jetzt kontaktieren

Total: 8 top-level links + logo + CTA button.

## Implemented Navigation Structure
- Logo (serves as primary home link)
- ÜBER UNS (`about.html`)
- LEISTUNGEN ▾
  - Express Verbrauchsausweis (48h)
  - Fördermittel-Rechner (BEG 2026)
  - Energieausweise
  - BAFA & KfW Förderungen
  - Sanierungsfahrplan (iSFP)
  - KfW Kreditanträge
- STANDORTE ▾
  - Standort Bremen (`energieberatung-bremen.html`)
  - Standort Aurich (`energieberatung-aurich.html`)
- INFOTHEK ▾
  - Fördermittel-Rechner, Mediathek, Dokumente, FAQ
- KONTAKT (`/#contact`)
- Button: Jetzt kontaktieren

Total: 5 top-level links + logo + CTA button.

## Technical Changes

### 1. Central Header Component (`components/header.html` & `assets/js/components.js`)
- Remove top-level `ENERGIEBERATUNG` link.
- Move top-level `EXPRESSAUSWEIS (48H)` and `FÖRDERUNGEN` inside the `LEISTUNGEN` dropdown.
- Update top-level link list to 5 clean links (`ÜBER UNS`, `LEISTUNGEN`, `STANDORTE`, `INFOTHEK`, `KONTAKT`).

### 2. Styling (`assets/css/main.css`)
- Adjust `.navmenu a` padding to `14px 12px` (from `18px 15px`).
- Adjust font size to `15px` for optimal legibility.
- Ensure proper alignment and flex behavior inside `.header-container`.

### 3. Static HTML Pages
- Update hardcoded header menus across HTML files (all pages in `TARGET_FILES` of `scripts/sync-components.js`, updated via `npm run sync`) to maintain consistency across the site.

## Verification
- Verify layout renders cleanly without wrapping at screen widths: 1200px, 1366px, 1440px, and 1920px.
- Verify dropdown interaction (hover on desktop, tap on touch).
- Verify mobile navigation toggles correctly.
