---
name: google-ai-ads
description: End-to-end strategy, setup, auditing, and troubleshooting for Google Ads, Performance Max (PMax), and Google AI Max campaigns. Use when users ask about Google Ads, AI Max, Performance Max, PPC advertising, ad campaign failures, ROAS/CPA optimization, conversion tracking diagnosis, offer-led ad copy, or landing page message-match.
---

# google-ai-ads

Expert guidance and diagnostic workflows for high-ROI Google Ads, Performance Max, and Google AI Max advertising campaigns.

## Core Premise: The Conversion Hierarchy

In any digital acquisition system, technical features and visual styling cannot save a weak value proposition. Success adheres strictly to this hierarchy:

```text
┌────────────────────────────────────────────────────────┐
│  #1. THE IRRESISTIBLE OFFER (The Engine of Conversion) │
├────────────────────────────────────────────────────────┤
│  #2. AUDIENCE TARGETING & MESSAGE MATCH                │
├────────────────────────────────────────────────────────┤
│  #3. COPYWRITING, HOOKS & OBJECTION HANDLING           │
├────────────────────────────────────────────────────────┤
│  #4. UX FLOW, PAGE SPEED & FRICTIONLESS CHECKOUT       │
├────────────────────────────────────────────────────────┤
│  #5. VISUAL DESIGN & TECHNICAL FEATURES (The Bottom)   │
└────────────────────────────────────────────────────────┘
```

> **The Invariant:** If the offer is weak, the entire campaign is **Nutzlos (Useless)**, no matter how elegant the code, how fast the site loads, or how advanced the Google AI algorithm is.

---

## 1. The 8-Pillar Campaign Failure Diagnostic Matrix

When evaluating why a Google Ads or AI Max campaign is underperforming, match symptoms against the 8 pillars:

| Pillar | If Missing, Campaign Becomes... | Primary Symptom |
|---|---|---|
| **1. Irresistible Offer** | **Nutzlos (Useless)** | Good clicks, zero conversions. Visitors inspect but never commit. |
| **2. Conv. Tracking** | **Blind** | Algorithm bids erratically, spend spikes or drops, zero attribution. |
| **3. Goals & KPIs** | **Ziellos (Aimless)** | Ad budget burns without knowing target CPA, breakeven, or LTV margin. |
| **4. Campaign Structure**| **Fragmentiert (Fragmented)** | Keyword cannibalization, diluted budget, asset groups fighting each other. |
| **5. Targeting Defense** | **Streuverluste (Wasted Spend)** | Clicks from irrelevant locations, jobs, support searches, competitors. |
| **6. Creatives & Copy** | **Unauffaellig (Unnoticeable)** | Sub-2% CTR, "Poor" Ad Strength, bland corporate copy with zero hook. |
| **7. Bids & Budgets** | **Ineffizient (Inefficient)** | Capped high performers, overpaying low intent, aggressive smart bid reset. |
| **8. Landing Page & UX** | **Ineffektiv (Ineffective)** | LCP > 1.5s, mobile bounce > 70%, ad promise doesn't match H1 headline. |

*For in-depth diagnostic procedures and step-by-step remediation, consult [references/failure-matrix.md](references/failure-matrix.md).*

---

## 2. Irresistible Offer Architecture (The #1 Driver)

Before touching keyword bids or creative copy, verify the offer using the **Alex Hormozi Value Equation**:

$$\text{Perceived Value} = \frac{\text{Dream Outcome} \times \text{Perceived Likelihood of Achievement}}{\text{Time Delay} \times \text{Effort \& Sacrifice}}$$

### Offer Construction Rules:
1. **Never Sell Hours or Code:** Sell business outcomes (*"Sub-800ms Customer Portal That Saves 30h/Month"*, not *"Laravel Development Services"*).
2. **Stack Risk Reversals:**
   - 3-Stage Milestone Payments (e.g. 30% Start / 40% Staging / 30% Final Release).
   - Core Web Vitals Guarantee (free performance optimization if mobile LCP > 1.2s).
   - 60-Day Post-Launch Warranty.
3. **Offer High-Value, Low-Friction Entry Points:**
   - Replace generic *"Contact Us"* with an interactive *Project Cost Estimator* or *Free 5-Minute Video Code/Site Audit*.
4. **Package Concrete Bonus Stacks:**
   - Include turn-key cloud setup, DSGVO compliance suite, and automated daily backups as baked-in bonuses.

---

## 3. Google AI Max & Performance Max (PMax) Standards

For tactical campaign setup and 2026 roadmap controls, observe these standard operating procedures:

### A. Final URL Expansion (FUE) Governance
- **Lead Generation & High-Ticket B2B:** Disable Final URL Expansion. Traffic must land strictly on approved, high-converting dedicated landing pages.
- **E-Commerce Catalogs:** Enable FUE only with strict URL exclusion rules (excluding blog posts, imprint, privacy policy, and account pages).

### B. Brand Search Protection
- Always attach an official **Brand Exclusion List** to PMax/AI Max campaigns.
- Run a separate, manual Search campaign for brand queries with exact match ([Brand Name]) to preserve low CPCs and measure true incremental conversions.

### C. Text Customization (TC) & Keyword-Level URLs
- Leverage 2026 Text Customization features to enforce brand guidelines and prevent algorithmic hallucinations.
- Use Keyword-Level URLs to route technical search queries directly to matching service silos rather than the homepage.

### D. First-Party Audience Signals
- Seed the AI with Customer Match lists (hashed client emails), high-value past converters, and custom search intent segments targeting specific competitor solutions.

*For detailed architectural specs, consult [references/ai-max-pmax-guide.md](references/ai-max-pmax-guide.md).*

---

## 4. Landing Page Execution Rules (Message Match & Speed)

Even the best ad cannot survive an ineffective landing page:
1. **Strict Message Match:** The exact headline, promise, or hook displayed in the winning ad creative must appear in the landing page H1 above the fold.
2. **Speed Budget:** Largest Contentful Paint (LCP) must remain under **1.0 second**. Zero cumulative layout shift (CLS).
3. **Mobile-First UX:** 60-70% of ad clicks occur on mobile devices. Ensure primary CTA buttons and form fields are thumb-accessible without zooming.
4. **Zero UI Emojis:** Use clean vector SVGs, Lucide icons, or Heroicons for social proof and visual indicators. Never use amateurish emojis in professional UI design.

---

## 5. Diagnostic Audit Routine

When asked to audit or fix an underperforming Google Ads account:

1. **Audit the Offer First:** Is the value proposition compelling, or is it a generic commodity asking for commitment without risk reversal?
2. **Audit Conversion Actions:** Are primary conversions firing on real business actions? Is Enhanced Conversions active? Is Consent Mode v2 compliant?
3. **Inspect Search Terms & Negatives:** Review search terms report for wasted spend on job searches, login queries, or competitor freebies. Add account-level negatives.
4. **Evaluate Landing Page Message Match & LCP:** Test URL on mobile via Lighthouse or DevTools; confirm H1 matches ad copy verbatim.
5. **Review Asset Variety:** Check Ad Strength in PMax/AI Max. Ensure all 15 headlines, 5 descriptions, landscape, square, portrait, and video assets are present.
6. **Check Bid Constraints & Learning Phase:** Ensure Target CPA is not set lower than 80% of historical average during the initial 30-conversion ramp-up.
