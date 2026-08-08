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
- Button: Jetzt Starten

Total: 8 top-level links + logo + CTA button.

## Proposed Navigation Structure (Option A)
- Logo (serves as primary home link)
- ÜBER UNS
- LEISTUNGEN ▾
  - Express Verbrauchsausweis (48h)
  - Energieausweise
  - BAFA & KfW Förderungen
  - Hydraulischer Abgleich
  - KfW Kreditanträge
- STANDORTE ▾
  - Standort Bremen (`index.html#contact`)
  - Standort Aurich (`energieberatung-aurich.html`)
- MEDIATHEK
- KONTAKT
- Button: Jetzt Starten

Total: 5 top-level links + logo + CTA button.

## Technical Changes

### 1. Central Header Component (`components/header.html` & `assets/js/components.js`)
- Remove top-level `ENERGIEBERATUNG` link.
- Move top-level `EXPRESSAUSWEIS (48H)` and `FÖRDERUNGEN` inside the `LEISTUNGEN` dropdown.
- Update top-level link list to 5 clean links (`ÜBER UNS`, `LEISTUNGEN`, `STANDORTE`, `MEDIATHEK`, `KONTAKT`).

### 2. Styling (`assets/css/main.css`)
- Adjust `.navmenu a` padding to `12px 14px` (from `18px 15px`).
- Adjust font size to `15px` for optimal legibility.
- Ensure proper alignment and flex behavior inside `.header-container`.

### 3. Static HTML Pages
- Update hardcoded header menus across HTML files (`index.html`, `about.html`, `expressausweis.html`, `energieberatung-aurich.html`, `energieberatung-bremen.html`, `mediathek.html`, `faq.html`, `impressum.html`, `datenschutz.html`, `data-protection.html`, `service-details.html`, `starter-page.html`) to maintain consistency across the site.

## Verification
- Verify layout renders cleanly without wrapping at screen widths: 1200px, 1366px, 1440px, and 1920px.
- Verify dropdown interaction (hover on desktop, tap on touch).
- Verify mobile navigation toggles correctly.
