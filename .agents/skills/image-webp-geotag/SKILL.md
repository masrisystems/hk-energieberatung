---
name: image-webp-geotag
description: "Optimizes, sizes, and geotags images: converts Web/Blog assets to WebP and preserves high-quality JPG for Google Business Profile (which rejects WebP), embeds high-precision GPS coordinates (Oldenburg, Germany), injects rich IPTC/EXIF/XMP SEO metadata and business keywords from brand.json, and renames files to clean kebab-case with primary target keywords. Activates globally when user mentions 'tag image', 'optimize image', 'log image', 'geotag image', 'image seo', 'convert to webp', 'geotag', 'exif keywords', or provides an image for local SEO optimization."
metadata:
  version: 1.2.0
---

# Image Optimization & Local SEO Geotagging Skill (`image-webp-geotag`)

This skill defines the automated end-to-end pipeline to transform raw images into high-ranking, performance-optimized, local SEO assets for **Masri Systems**.

## 🎯 Activation Triggers
Activate globally whenever the user says:
- `tag image`
- `optimize image`
- `log image`
- `geotag image`
- `image seo`
- `convert to webp`
- Or provides an image file / screenshot and asks to prepare it for the blog, website, or Google Business Profile (GBP).

---

## 🏗️ Technical Execution Pipeline

When activated with an image and a topic/keyword:

### Step 1: SEO Kebab-Case Filename Generation
Generate a clean, keyword-rich filename following the Masri Systems convention:
```
masrisystems-[category-or-pillar]-[primary-target-keyword]-[geo-optional].[ext]
```
*Examples:*
- Blog WebP: `masrisystems-softwareentwicklung-web-apps-mvp-oldenburg.webp`
- GBP JPG: `masrisystems-gbp-webdesign-landingpage-oldenburg.jpg`

### Step 2: Format & Dimension Routing

> [!important] GBP Format Constraint: JPG / JPEG Only
> Google Business Profile (GBP) rejects `.webp` files. Format routing must be strictly respected:

* **For Blog / Website Assets:**
  - Convert to `.webp` (`quality=85`, `method=6`)
  - Dimensions: `1200x675` (16:9 widescreen)
  - Target Path: `content/Assets/Blog/` and `public/images/`

* **For Google Business Profile (GBP) Assets:**
  - Preserve / save as `.jpg` (`quality=92`, max 4MB) — **Do NOT convert to WebP**
  - Dimensions: `1080x1080` or `1200x1200` (1:1 square)
  - Target Path: `content/Assets/GBP/` and `public/images/gbp/`

### Step 3: GPS Geotagging & IPTC/EXIF Metadata Injection
Execute via ExifTool (`scripts/geotag-images.js` or Node/Python runner) injecting:

```javascript
const GPS_METADATA = {
  GPSLatitude: 53.136829,
  GPSLatitudeRef: 'N',
  GPSLongitude: 8.196328,
  GPSLongitudeRef: 'E',
  GPSAltitude: 12,
  City: 'Oldenburg (Oldb)',
  'Sub-location': 'Nettelbeckstraße 10',
  'Province-State': 'Niedersachsen',
  Country: 'Deutschland',
  CountryCode: 'DE',
  PostalCode: '26131',
  Copyright: '© Masri Systems - Nettelbeckstraße 10, 26131 Oldenburg (Oldb)',
  Artist: 'Masri Systems',
  Byline: 'Masri Systems',
  Credit: 'Masri Systems',
  Source: 'https://masrisystems.com',
  Contact: 'hallo@masrisystems.com | +49 176 31579669',
  Creator: 'Mohamad Masri - Masri Systems',
  CreatorAddress: 'Nettelbeckstraße 10',
  CreatorCity: 'Oldenburg (Oldb)',
  CreatorPostalCode: '26131',
  CreatorCountry: 'Deutschland',
  CreatorWorkEmail: 'hallo@masrisystems.com',
  CreatorWorkTelephone: '+49 176 31579669',
  CreatorWorkURL: 'https://masrisystems.com',
};
```

### Step 4: Semantic Keywords & Description Sourcing
Query `brand.json` and `.agents/keywords.md` to inject relevant primary & secondary keywords into:
- `XPKeywords` / `Keywords`
- `ObjectName` / `Title`
- `ImageDescription` / `Caption-Abstract`
- `Headline`
