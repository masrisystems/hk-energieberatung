# FAQ Section Integration & Dedicated FAQ Hub (`faq.html`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 25 FAQs from `assets/FAQ-EN~1.HTM.html` into an upgraded `index.html#faq` section and build a dedicated `faq.html` page with 5 categories, interactive graphics (Einsparpotenzial & Effizienzklassen scale), and component synchronization.

**Architecture:** Static HTML pages (`faq.html` & `index.html`) using Bootstrap 5 grid/accordions and `assets/css/main.css` design system. Pre-rendered header, footer, contact, and map components via `scripts/sync-components.js`.

**Tech Stack:** HTML5, CSS3, Bootstrap 5, Vanilla JS, Node.js.

---

### Task 1: Add FAQ & Graphics Styling to `assets/css/main.css`

**Files:**
- Modify: `assets/css/main.css`

- [ ] **Step 1: Add FAQ chart cards, energy scale, and category header CSS to `assets/css/main.css`**

Add at end of `assets/css/main.css`:
```css
/* FAQ Visual Graphics & Category Styling */
.faq-chart-card,
.faq-scale-card {
  background: var(--surface-color);
  border-radius: 16px;
  padding: 28px 30px;
  margin: 15px 0 35px;
  box-shadow: 0 6px 24px rgba(45, 70, 94, 0.07);
}

.faq-chart-card h3,
.faq-scale-card h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--heading-color);
  margin-bottom: 4px;
}

.faq-chart-card .chart-sub,
.faq-scale-card .chart-sub {
  font-size: 0.85rem;
  color: color-mix(in srgb, var(--default-color), transparent 40%);
  margin-bottom: 20px;
}

.faq-stat-highlight {
  display: flex;
  align-items: center;
  gap: 16px;
  background: color-mix(in srgb, var(--accent-color), white 60%);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.faq-stat-highlight .stat-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.faq-stat-highlight .stat-number {
  font-family: var(--heading-font);
  font-weight: 800;
  font-size: 1.5rem;
  color: var(--heading-color);
  line-height: 1.2;
}

.faq-stat-highlight .stat-text {
  font-size: 0.85rem;
  color: color-mix(in srgb, var(--default-color), transparent 20%);
}

.faq-bar-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.faq-bar-label {
  width: 170px;
  font-family: var(--nav-font);
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--heading-color);
  flex-shrink: 0;
}

.faq-bar-track {
  flex: 1;
  background: color-mix(in srgb, var(--default-color), transparent 93%);
  border-radius: 8px;
  height: 22px;
  overflow: hidden;
}

.faq-bar-fill {
  height: 100%;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--heading-color);
}

.faq-scale-bar {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  height: 42px;
}

.faq-scale-seg {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-family: var(--heading-font);
  font-weight: 800;
  font-size: 0.9rem;
}

.faq-cat-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 30px;
  margin-bottom: 16px;
}

.faq-cat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--accent-color), white 40%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.faq-cat-head h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--heading-color);
  margin: 0;
}
```

- [ ] **Step 2: Commit CSS changes**

```bash
git add assets/css/main.css
git commit -m "feat: add FAQ charts and category header styles to main.css"
```

---

### Task 2: Create `faq.html` Dedicated Page Hub

**Files:**
- Create: `faq.html`

- [ ] **Step 1: Build `faq.html` with all 25 FAQs and 2 visual graphics**

Create `faq.html` featuring:
- Pre-rendered Header placeholder (`<!-- START: HEADER_COMPONENT -->`).
- Page Title section: "Häufige Fragen (FAQ)".
- Intro lead paragraph explaining the 5 categories.
- Einsparpotenzial Grafik card.
- 5 Category sections (Allgemeines zur Energieberatung, Energieausweis with Energieeffizienzklassen scale, Fördermittel, Sanierung & Technik, Ablauf & Kosten).
- Pre-rendered Contact component placeholder (`<!-- START: CONTACT_COMPONENT -->`).
- Pre-rendered Map component iframe.
- Pre-rendered Footer component placeholder (`<!-- START: FOOTER_COMPONENT -->`).
- JS accordion interactivity script matching `main.js`.

- [ ] **Step 2: Commit `faq.html` creation**

```bash
git add faq.html
git commit -m "feat: create dedicated faq.html hub with 25 questions and 2 visual graphics"
```

---

### Task 3: Update Component Synchronizer & Header Link (`scripts/sync-components.js`)

**Files:**
- Modify: `scripts/sync-components.js`
- Modify: `components/header.html`
- Modify: `components/footer.html`

- [ ] **Step 1: Register `faq.html` in `scripts/sync-components.js`**

Add `'faq.html'` to `TARGET_FILES` and handle `faq.html` in `customizeHeader()`.

- [ ] **Step 2: Add FAQ link to Footer component (`components/footer.html`)**

In `components/footer.html`, add `<li><a href="faq.html">Häufige Fragen (FAQ)</a></li>` under Nützliche Links.

- [ ] **Step 3: Commit synchronizer and footer updates**

```bash
git add scripts/sync-components.js components/footer.html
git commit -m "feat: register faq.html in component synchronizer and add footer link"
```

---

### Task 4: Upgrade `<section id="faq">` in `index.html`

**Files:**
- Modify: `index.html:812-950`

- [ ] **Step 1: Upgrade `<section id="faq">` in `index.html`**

Replace lines 812-950 in `index.html` with the 5 categorized FAQ accordions, visual graphics, and a call-to-action button linking to `faq.html` ("Alle 25 Fragen & Grafiken ansehen").

- [ ] **Step 2: Commit `index.html` updates**

```bash
git add index.html
git commit -m "feat: upgrade homepage FAQ section with 5 categories and link to faq.html"
```

---

### Task 5: Pre-render Components and Verify

**Files:**
- Executed via: `node scripts/sync-components.js`

- [ ] **Step 1: Run component synchronizer**

```powershell
node scripts\sync-components.js
```

- [ ] **Step 2: Commit pre-rendered changes**

```bash
git add .
git commit -m "build: pre-render and sync components across all pages including faq.html"
```
