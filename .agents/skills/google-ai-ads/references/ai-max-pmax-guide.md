# Google AI Max & Performance Max (PMax) 2026 Strategy Guide

## Table of Contents
1. Architectural Overview & 2026 External Roadmap
2. Core Controls: Text Customization (TC) & Keyword-Level URLs
3. Final URL Expansion (FUE) Governance
4. Brand Search Cannibalization Defense
5. First-Party Audience Signals Architecture
6. Value-Based Bidding (VBB) & Offline Conversion Imports
7. High-Converting Asset Group Blueprint

---

## 1. Architectural Overview & 2026 External Roadmap

Google AI Max represents the evolution of Performance Max, giving advertisers more explicit algorithmic steering and text customization while maintaining cross-channel inventory reach (Search, YouTube, Display, Discover, Gmail, Maps).

### 2026 External Roadmap Pillars:
- **Text Customization (TC):** Global and vertical-specific text rules allowing granular control over AI-generated headlines and descriptions.
- **Keyword-Level Destination URLs:** Routing specific matched queries directly to tailored landing page subpaths rather than relying solely on automated domain matching.
- **Enhanced Creatives Text Guidelines:** Enforcing brand voice boundaries, banned claims, and required disclaimers directly in the bidding engine.
- **Geo-Matched Location Reporting:** Granular physical location performance auditing to eliminate wasted spend in untargeted postal codes.

---

## 2. Core Controls: Text Customization (TC) & Keyword-Level URLs

### Text Customization (TC) Rules:
- Prevent hallucinated claims or non-compliant pricing promises by locking specific brand assets (Pillars, Guarantees, Compliance phrases).
- Use TC to swap value propositions based on user intent (e.g., "Fast 4-Week Delivery" for startup searches vs. "DSGVO-Conformity & Security" for enterprise KMU searches).

### Keyword-Level URLs:
- Do not dump all PMax search traffic onto the homepage.
- Map distinct keyword clusters to dedicated landing pages:
  - MVP / Web-System queries -> /services/software-development
  - Local Handwerk / KMU queries -> /services/handwerk or local landing page
  - Retainer / Cloud inquiries -> /services/hosting-care

---

## 3. Final URL Expansion (FUE) Governance

### The Rule of Thumb:
- **Lead Generation & High-Ticket B2B:** **TURN OFF Final URL Expansion (FUE).** Leaving FUE on in B2B sends costly paid traffic to terms of service, blog archives, or obscure subpages with low conversion rates.
- **E-Commerce & Large Catalogs:** Leave FUE ON, but apply strict **URL Exclusion Rules**:
  - Exclude /blog/*, /privacy, /terms, /impressum, /account/*, /cart.
  - Only allow category and product detail URLs.

---

## 4. Brand Search Cannibalization Defense

By default, Google AI Max will bid aggressively on your own brand terms to claim easy, cheap conversions and inflate reported ROAS.

### Mandatory Mitigations:
1. **Brand Exclusion Lists:** Apply an official Google Ads Brand List to your AI Max / PMax campaign containing your exact brand name and misspellings.
2. **Dedicated Brand Search Campaign:** Run a standalone, manual Search campaign for your brand name with exact match keywords ([masri systems]) and Target Impression Share (95%+). This keeps brand CPC low (<0.20 EUR) and forces AI Max to hunt for incrementality.
3. **Account-Level Negative Keywords:** Add non-buyer queries at the account level (login, support, jobs, karriere, gehalt, impressum).

---

## 5. First-Party Audience Signals Architecture

Google AI Max needs seed data to discover high-value lookalikes. Never launch with empty audience signals.

### Priority Signal Stacks:
1. **Customer Match (Tier 1):** Hashed list of paying clients and closed-won leads (emails + phone numbers).
2. **High-Intent Converters (Tier 2):** GA4 audience of users who completed a project calculation or booked a consultation.
3. **Custom Search Intent Segments (Tier 3):** Users who searched for direct competitor brand names or exact high-ticket service queries on Google.
4. **Website Engaged Visitors (Tier 4):** 30-day visitors with session duration > 90 seconds, excluding existing customers.

---

## 6. Value-Based Bidding (VBB) & Offline Conversion Imports

### Why Volume-Based Bidding Fails in B2B:
When bidding for "Maximize Conversions", the AI prioritizes the easiest form fills: students, spam bots, and tire-kickers with 0 EUR budget.

### Value-Based Setup:
- Assign differential values to lead stages:
  - Initial Form Submission: Value = 10 EUR
  - Qualified Discovery Call Completed: Value = 100 EUR
  - Signed Contract / Closed Deal: Value = Actual Deal Value (e.g., 3.200 EUR)
- Use **Offline Conversion Import (OCI)** or Enhanced Conversions for Leads to feed CRM pipeline stages back into Google Ads within 30-60 days.
- Shift bidding strategy from **Maximize Conversions** to **Maximize Conversion Value (tROAS)** once 15+ qualified values are recorded per month.

---

## 7. High-Converting Asset Group Blueprint

For every thematic cluster, provide full asset coverage to prevent automated fallback text:

| Asset Type | Requirement | Strategic Recommendation |
|---|---|---|
| **Headlines** | 5 minimum (up to 15) | Mix of Offer, Pain Point, Social Proof, and Direct Benefit. |
| **Long Headlines** | 5 slots (90 chars) | Full value proposition with risk reversal and proof. |
| **Descriptions** | 4-5 slots | 1 short (60 chars), 3 long (90 chars) addressing core objections. |
| **Landscape Images** | 1.91:1 (min. 3) | Real interface screenshots, staging demos, professional team portraits. |
| **Square Images** | 1:1 (min. 3) | Clean vector illustrations, badges, product mockups. |
| **Portrait Images** | 4:5 / 9:16 (min. 1) | Mobile-first visual framing for YouTube Shorts & Discover. |
| **Logos** | 1:1 and 4:1 | High-res transparent SVG/PNG logos. |
| **Video Assets** | Landscape + Vertical | 15s-30s product demo or client walkthrough. |
