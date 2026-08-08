# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static marketing website for HK Energieberatung (energy consulting, Bremen & Aurich, Germany). Plain HTML/CSS/JS — no framework, no bundler, no build-time compilation of assets. Based on the BootstrapMade "iLanding" template, using Bootstrap 5.3.2.

## Commands

```bash
npm run sync   # (alias: npm run build) — bakes components/*.html into all target pages
```

There is no test suite, linter, or dev server script defined in `package.json`. To preview, open the HTML files directly or serve the directory with any static file server (VS Code Live Server is configured in `.vscode/settings.json`, port 5501).

## Architecture

### Dual-mode component system (important — read before editing header/footer/contact)

Shared UI (`components/header.html`, `components/footer.html`, `components/contact.html`) is **pre-rendered directly into every page's HTML**, not loaded purely at runtime. This is deliberate, for SEO and zero-JS-dependent rendering:

- `scripts/sync-components.js` reads the component files and injects them between marker comments (`<!-- START: HEADER_COMPONENT --> ... <!-- END: HEADER_COMPONENT -->`, same pattern for `FOOTER_COMPONENT` and `CONTACT_COMPONENT`) in each file listed in its `TARGET_FILES` array.
- `assets/js/components.js` also renders header/footer/contact/map client-side into `#header-component` / `#footer-component` / `#contact-component` divs as a runtime fallback/enhancement, and sets the active nav link based on `window.location.pathname`.
- **Workflow:** edit `components/header.html`, `components/footer.html`, or `components/contact.html`, then run `npm run sync` to propagate the change into all target pages. Do not hand-edit the pre-rendered header/footer/contact blocks inside individual page files — they'll be overwritten on the next sync (and a GitHub Action, `.github/workflows/sync-components.yml`, auto-runs the sync and commits the result whenever `components/**` changes on push).
- When adding a new page that should share header/footer/contact, add its filename to `TARGET_FILES` in `scripts/sync-components.js`.
- Adding a new nav target requires a corresponding `else if` branch in `customizeHeader()` in `scripts/sync-components.js` to mark it active.

### Pages and structure

- Top-level `*.html` files are the site's pages (`index.html`, `about.html`, `faq.html`, `energieberatung-bremen.html`, `energieberatung-aurich.html`, `expressausweis.html`, `mediathek.html`, `dokumente.html`, `impressum.html`, `datenschutz.html`, `data-protection.html`, `agb.html`, `service-details.html`, `starter-page.html`).
- `assets/css/main.css`, `assets/js/main.js` — main site styles/behavior (template-provided, Bootstrap-based).
- `assets/vendor/` — third-party libraries (Bootstrap, etc.).
- `assets/dokumente/` — downloadable documents surfaced via the INFOTHEK/dokumente hub.
- `forms/contact.php` — server-side contact form handler (PHP mail, honeypot spam trap, required-field and email validation). Requires a PHP-capable host; not used by the static GitHub Pages deploy itself.

### Deployment

`.github/workflows/static.yml` deploys the entire repository as-is to GitHub Pages on every push to `master`. There is no separate build/compile step in that workflow — `npm run sync` must already have been run (and committed) or the sync workflow must have handled it, since GitHub Pages serves the pre-rendered HTML directly.
