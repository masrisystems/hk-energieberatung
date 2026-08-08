# Über Uns Page Redesign & Image Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone `about.html` page matching the `aboutus.jpeg` mockup, rename and integrate new image assets, update location cards in `energieberatung-aurich.html`, update `index.html#about`, and enable component synchronization in `scripts/sync-components.js`.

**Architecture:** A static HTML page (`about.html`) following Bootstrap 5 styling and `assets/css/main.css` design system. Pre-rendered header, footer, and contact sections injected via `scripts/sync-components.js`.

**Tech Stack:** HTML5, CSS3, Bootstrap 5, Vanilla JS, Node.js (build/sync script).

---

### Task 1: Rename Image Assets

**Files:**
- Rename: `assets/img/hkboardjpeg.jpeg` $\rightarrow$ `assets/img/about-banner.jpg`
- Rename: `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (1).jpeg` $\rightarrow$ `assets/img/aurich-sign-board.jpg`
- Rename: `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (2).jpeg` $\rightarrow$ `assets/img/aurich-center.jpg`
- Rename: `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM (3).jpeg` $\rightarrow$ `assets/img/bremen-stadtmusikanten.jpg`
- Rename: `assets/img/WhatsApp Image 2026-08-08 at 12.02.07 PM.jpeg` $\rightarrow$ `assets/img/bremen-marktplatz.jpg`

- [ ] **Step 1: Rename files in assets/img/**

```powershell
Rename-Item -Path "assets\img\hkboardjpeg.jpeg" -NewName "about-banner.jpg"
Rename-Item -Path "assets\img\WhatsApp Image 2026-08-08 at 12.02.07 PM (1).jpeg" -NewName "aurich-sign-board.jpg"
Rename-Item -Path "assets\img\WhatsApp Image 2026-08-08 at 12.02.07 PM (2).jpeg" -NewName "aurich-center.jpg"
Rename-Item -Path "assets\img\WhatsApp Image 2026-08-08 at 12.02.07 PM (3).jpeg" -NewName "bremen-stadtmusikanten.jpg"
Rename-Item -Path "assets\img\WhatsApp Image 2026-08-08 at 12.02.07 PM.jpeg" -NewName "bremen-marktplatz.jpg"
```

- [ ] **Step 2: Verify all 5 renamed files exist**

```powershell
Test-Path "assets\img\about-banner.jpg", "assets\img\aurich-sign-board.jpg", "assets\img\aurich-center.jpg", "assets\img\bremen-stadtmusikanten.jpg", "assets\img\bremen-marktplatz.jpg"
```

- [ ] **Step 3: Commit image asset renaming**

```bash
git add assets/img/
git commit -m "refactor: rename uploaded image assets to descriptive names"
```

---

### Task 2: Update Component Synchronizer (`scripts/sync-components.js`)

**Files:**
- Modify: `scripts/sync-components.js`

- [ ] **Step 1: Add about.html to TARGET_FILES and customizeHeader**

In `scripts/sync-components.js`, update `TARGET_FILES`:
```javascript
const TARGET_FILES = [
  'index.html',
  'about.html',
  'energieberatung-aurich.html',
  'expressausweis.html',
  'mediathek.html',
  'impressum.html',
  'datenschutz.html'
];
```

And in `customizeHeader`:
```javascript
  if (targetPage === 'index.html') {
    customized = customized.replace('data-page="index.html#hero"', 'data-page="index.html#hero" class="active"');
  } else if (targetPage === 'about.html') {
    customized = customized.replace('data-page="about.html"', 'data-page="about.html" class="active"');
    customized = customized.replace('data-page="index.html#about"', 'data-page="index.html#about" class="active"');
  } else if (targetPage === 'energieberatung-aurich.html') {
```

- [ ] **Step 2: Update `components/header.html` navigation item**

In `components/header.html`, update the link for ÜBER UNS:
```html
<li><a href="about.html" data-page="about.html">ÜBER UNS</a></li>
```

- [ ] **Step 3: Commit component synchronizer changes**

```bash
git add scripts/sync-components.js components/header.html
git commit -m "feat: register about.html in component synchronizer and update nav header link"
```

---

### Task 3: Create `about.html` Page

**Files:**
- Create: `about.html`
- Modify: `assets/css/main.css` (if custom styles needed for location collage cards)

- [ ] **Step 1: Add custom styles for location composite cards to `assets/css/main.css`**

Add at end of `assets/css/main.css`:
```css
/* Dual Image Location Cards for About Us & Standorte */
.location-dual-card {
  background: var(--surface-color);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  text-decoration: none;
  display: block;
  height: 100%;
}

.location-dual-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.location-dual-images {
  display: flex;
  height: 220px;
  gap: 4px;
  overflow: hidden;
}

.location-dual-images img {
  width: 50%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.location-dual-card:hover .location-dual-images img {
  transform: scale(1.05);
}

.location-dual-title {
  padding: 18px 20px;
  text-align: center;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--heading-color);
  margin: 0;
  background: var(--surface-color);
}
```

- [ ] **Step 2: Create `about.html` with all page sections**

Create `about.html` containing HTML head, pre-rendered Header placeholder, "Über Uns" section title, "Unser Team" section, "Unsere Gründer" section, "Was wir mitbringen" section, Contact component placeholder, "Unsere Standorte" section with dual cards, Google Maps embed section, and Footer component placeholder.

- [ ] **Step 3: Verify structure of `about.html`**

Ensure all sections, data-aos attributes, image paths (`assets/img/about-banner.jpg`, `assets/img/Profilbild.png`, `assets/img/Profilbild 2.png`, `assets/img/about-secondary.png`, `assets/img/bremen-stadtmusikanten.jpg`, `assets/img/bremen-marktplatz.jpg`, `assets/img/aurich-sign-board.jpg`, `assets/img/aurich-center.jpg`) are correct.

- [ ] **Step 4: Commit `about.html` creation and CSS updates**

```bash
git add about.html assets/css/main.css
git commit -m "feat: add about.html page structure and dual location card styles"
```

---

### Task 4: Update `energieberatung-aurich.html` Location Cards

**Files:**
- Modify: `energieberatung-aurich.html:400-420`

- [ ] **Step 1: Replace single image location cards with dual location cards in `energieberatung-aurich.html`**

Update lines 400-420 of `energieberatung-aurich.html` to use `.location-dual-card` with the new location images for Bremen and Aurich.

- [ ] **Step 2: Commit `energieberatung-aurich.html` updates**

```bash
git add energieberatung-aurich.html
git commit -m "feat: update location switcher cards in energieberatung-aurich.html with new location images"
```

---

### Task 5: Update `<section id="about">` in `index.html`

**Files:**
- Modify: `index.html:178-266`

- [ ] **Step 1: Update `<section id="about">` in `index.html`**

Update `<section id="about">` text and layout in `index.html` to match the refreshed founder & engineering expertise copy from `aboutus.jpeg`.

- [ ] **Step 2: Commit `index.html` updates**

```bash
git add index.html
git commit -m "feat: update about section in index.html for visual and copy consistency"
```

---

### Task 6: Synchronize Components and Verify Build

**Files:**
- Executed via: `node scripts/sync-components.js`

- [ ] **Step 1: Execute static component synchronizer script**

```powershell
node scripts\sync-components.js
```

- [ ] **Step 2: Verify component markers across all target HTML files**

Verify `about.html`, `index.html`, `energieberatung-aurich.html`, `expressausweis.html`, `mediathek.html`, `impressum.html`, `datenschutz.html` contain updated `<!-- START: HEADER_COMPONENT -->` and `<!-- START: FOOTER_COMPONENT -->`.

- [ ] **Step 3: Commit pre-rendered component updates**

```bash
git add .
git commit -m "build: pre-render and sync components across all pages including about.html"
```
