---
type: project
status: 🟢 active
priority: 🟡 medium
area: [[Services/index|Services]]
url: "https://hk-energieberatung.de/"
title: "HK Energieberatung: Sustainable Energy Solutions"
description: "A professional web presence for certified energy consultants in Bremen, focusing on efficiency, sustainability, and government subsidies."
tags: [energy-consulting, web-design, sustainability, bremen, static-site]
category: Professional Services Web Design
---

**Project Progress:** `$= const tasks = dv.current().file.tasks; const total = tasks.length; if (total === 0) { "No tasks found." } else { const completed = tasks.filter(t => t.completed).length; const percent = Math.round((completed / total) * 100); "<progress value='" + percent + "' max='100'></progress> <span style='font-size:smaller;color:var(--text-muted)'>" + percent + "% &nbsp;|&nbsp; " + (total - completed) + " left</span>"; }`


# 🏠 HK Energieberatung: Engineering a Greener Future

*Assets/Img/masrisystems-portfolio-hk-energieberatung-webdesign.webp*


[HK-energieberatung.de](https://hk-energieberatung.de/) is the digital portal for a team of certified energy consultants based in Bremen, Germany. The platform is designed to connect homeowners with expert advice on making residential buildings more efficient, economical, and sustainable.

---

## 💎 Strategic Core Services
The website highlights the firm's comprehensive approach to energy optimization and financial planning for homeowners.

> [!abstract] Certification & Analysis
> - **Energy Performance Certificates:** Professional creation of mandatory legal documents for property sales and rentals.
> - **Hydraulic Balancing:** Technical optimization of heating systems to ensure maximum efficiency and comfort.

> [!success] Subsidy Management
> Expert guidance through the complex landscape of German government grants:
> - **BAFA & KfW Applications:** Full support in securing maximum funding for renovation projects.
> - **iSFP Bonus:** Expertise in the *Individual Renovation Roadmap*, securing an **extra 5% bonus** for clients.

---

## 📊 Transparent Pricing Model
A key feature of the platform is its upfront, transparent cost structure, designed to build immediate trust with potential clients.

| Service | Pricing |
| :--- | :--- |
| **Initial Consultation** | **Free** |
| **Express Consumption Certificate (48h)** | Fixed price **€80** incl. VAT |
| **iSFP Consulting Package** | approx. **€650 – €850** own share after the 50% BAFA grant (single/two-family home) |

---

## 💻 Technical Implementation
To reflect the precision and professionalism of energy consulting, the site is a fast, static, pre-rendered website.

*   **Frontend:** Plain HTML, CSS and JavaScript (no framework, no bundler).
*   **Styling:** Bootstrap 5.3 on the BootstrapMade "iLanding" template, mobile-first.
*   **Shared UI:** Header, footer and contact are pre-rendered into every page by `npm run sync`.
*   **Forms:** PHP mail handler (`forms/contact.php`); hosting on GitHub Pages.

---

> [!question] Need a Professional Web Presence for your Service?
> We help experts in highly regulated fields build trust and reach more clients through technical excellence. [[Strategy Call|Let's discuss your project]].

#energy #consulting #bremen #webdev #sustainability #staticsite
