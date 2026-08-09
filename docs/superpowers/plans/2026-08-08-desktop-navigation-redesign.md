# Desktop Navigation Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-structure and streamline the desktop header navigation bar to eliminate overcrowding, remove redundant links, and optimize spacing across desktop screens.

**Architecture:** Update central component templates (`header.html` and `components.js`), adjust desktop navigation CSS rules (`main.css`), and update all hardcoded static HTML header navigation blocks for consistency.

**Tech Stack:** HTML5, Vanilla JavaScript, Vanilla CSS (Bootstrap grid system).

---

### Task 1: Update Central Header Component & CSS

**Files:**
- Modify: `components/header.html`
- Modify: `assets/js/components.js:29-54`
- Modify: `assets/css/main.css:255-270`

- [ ] **Step 1: Update `components/header.html`**

Update `components/header.html` to reflect the 5 top-level items structure:

```html
<header id="header" class="header d-flex align-items-center fixed-top">
  <div class="header-container container-fluid container-xl position-relative d-flex align-items-center justify-content-between">

    <a href="index.html" class="logo d-flex align-items-center me-auto me-xl-0">
      <img src="assets/img/logo.jpeg" alt="HK Energieberatung Logo" class="img-fluid">
    </a>

    <nav id="navmenu" class="navmenu">
      <ul>
        <li><a href="about.html" data-page="about.html">ÜBER UNS</a></li>
        <li class="dropdown"><a href="index.html#services" data-page="index.html#services"><span>LEISTUNGEN</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
          <ul>
            <li><a href="expressausweis.html">Express Verbrauchsausweis (48h)</a></li>
            <li><a href="index.html#services">Energieausweise</a></li>
            <li><a href="index.html#features">BAFA & KfW Förderungen</a></li>
            <li><a href="index.html#services">Hydraulischer Abgleich</a></li>
            <li><a href="index.html#services">KfW Kreditanträge</a></li>
          </ul>
        </li>
        <li class="dropdown"><a href="#" data-page="standorte"><span>STANDORTE</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
          <ul>
            <li><a href="index.html#contact" data-page="index.html#contact">Standort Bremen</a></li>
            <li><a href="energieberatung-aurich.html" data-page="energieberatung-aurich.html">Standort Aurich</a></li>
          </ul>
        </li>
        <li><a href="mediathek.html" data-page="mediathek.html">MEDIATHEK</a></li>
        <li><a href="index.html#contact" data-page="index.html#contact">KONTAKT</a></li>
      </ul>
      <i class="mobile-nav-toggle d-xl-none bi bi-list"></i>
    </nav>

    <a class="btn-getstarted btn-hk btn-hk-sm" href="index.html#contact">Jetzt kontaktieren</a>

  </div>
</header>
```

- [ ] **Step 2: Update `assets/js/components.js` `renderHeader()`**

Update `assets/js/components.js` lines 29-54:

```javascript
          <nav id="navmenu" class="navmenu">
            <ul>
              <li><a href="${isPage('about.html') ? 'about.html' : isPage('index.html') ? '#about' : 'index.html#about'}" class="${isPage('about.html') ? 'active' : ''}">ÜBER UNS</a></li>
              <li class="dropdown"><a href="${isPage('index.html') ? '#services' : 'index.html#services'}"><span>LEISTUNGEN</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
                <ul>
                  <li><a href="expressausweis.html" class="${isPage('expressausweis.html') ? 'active' : ''}">Express Verbrauchsausweis (48h)</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">Energieausweise</a></li>
                  <li><a href="${isPage('index.html') ? '#features' : 'index.html#features'}">BAFA & KfW Förderungen</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">Hydraulischer Abgleich</a></li>
                  <li><a href="${isPage('index.html') ? '#services' : 'index.html#services'}">KfW Kreditanträge</a></li>
                </ul>
              </li>
              <li class="dropdown"><a href="#" class="${isPage('energieberatung-aurich.html') ? 'active' : ''}"><span>STANDORTE</span> <i class="bi bi-chevron-down toggle-dropdown"></i></a>
                <ul>
                  <li><a href="${isPage('index.html') ? '#contact' : 'index.html#contact'}">Standort Bremen</a></li>
                  <li><a href="energieberatung-aurich.html" class="${isPage('energieberatung-aurich.html') ? 'active' : ''}">Standort Aurich</a></li>
                </ul>
              </li>
              <li><a href="${isPage('index.html') ? '#mediathek' : 'mediathek.html'}" class="${isPage('mediathek.html') ? 'active' : ''}">MEDIATHEK</a></li>
              <li><a href="${isPage('index.html') ? '#contact' : 'index.html#contact'}">KONTAKT</a></li>
            </ul>
            <i class="mobile-nav-toggle d-xl-none bi bi-list"></i>
          </nav>
```

- [ ] **Step 3: Update CSS styling in `assets/css/main.css`**

In `assets/css/main.css`, update `.navmenu a` styling:

```css
  .navmenu a,
  .navmenu a:focus {
    color: var(--nav-color);
    padding: 14px 12px;
    font-size: 15px;
    font-family: var(--nav-font);
    font-weight: 500;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    white-space: nowrap;
    transition: 0.3s;
  }
```

- [ ] **Step 4: Commit Task 1**

```bash
git add components/header.html assets/js/components.js assets/css/main.css
git commit -m "refactor(nav): streamline desktop header component and optimize nav spacing"
```

---

### Task 2: Update Static HTML Page Headers

**Files:**
- Modify: `index.html`
- Modify: `about.html`
- Modify: `expressausweis.html`
- Modify: `energieberatung-aurich.html`
- Modify: `energieberatung-bremen.html`
- Modify: `mediathek.html`
- Modify: `faq.html`
- Modify: `impressum.html`
- Modify: `datenschutz.html`
- Modify: `data-protection.html`
- Modify: `service-details.html`
- Modify: `starter-page.html`

- [ ] **Step 1: Update `<nav id="navmenu">` in all static `.html` files**

Replace the existing `<nav id="navmenu">...</nav>` block in each HTML file with the streamlined navigation structure matching `components/header.html`.

- [ ] **Step 2: Commit Task 2**

```bash
git add *.html
git commit -m "refactor(nav): update static page header navbars to match streamlined structure"
```

---

### Task 3: Visual Verification & Project Logs Update

**Files:**
- Modify: `C:\Users\super\Desktop\obsidian\masrisystems-app\content\private\Work\MasriGMBH\Kunden\Hussein Khashab\Kanban Hk Energieberatung.md`

- [ ] **Step 1: Test Navigation Responsiveness in Browser**

Verify that header renders cleanly without text wrapping at 1200px, 1366px, 1440px, and 1920px widths. Verify mobile menu toggle and dropdown popups function correctly.

- [ ] **Step 2: Update Kanban Log Rule (AGENTS.md Rule 1)**

Update `Kanban Hk Energieberatung.md` with completed work summary:
- Streamlined desktop navigation from 8 overcrowded items to 5 clean top-level items.
- Consolidated Expressausweis and BAFA/KfW Förderungen under `Leistungen` dropdown.
- Optimized padding and font sizes for high readability without wrapping.

- [ ] **Step 3: Commit Task 3**

```bash
git add .
git commit -m "docs: update kanban roadmap log for desktop navigation redesign"
```
