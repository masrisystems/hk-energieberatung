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

> [!important] One file per asset — never write the same image to two directories
> `masrisystems-app/public/images/` is the **single local home** for every generated asset. It is the
> only directory served on masrisystems.com (`/images/...`) and the only one `storage:r2-sync` maps to
> the R2 `images/` prefix that the blog and social pipelines read from. Do **not** also copy into
> `content/Assets/**` or a repo-root `images/` folder — those were duplicate trees and have been removed.
> Full layout reference: `masrisystems-app/docs/19-images-layout.md`.

* **For Blog / Website Assets (16:9 hero):**
  - `.webp` (`quality=85`, `method=6`), `1200x675` — this is what the blog body embeds.
  - `.jpg` (`quality=92`), `1200x675` — the OG-preview / social fallback twin of the same image.
  - Target Path: `masrisystems-app/public/images/` — **one copy each, nowhere else.**

* **For Google Business Profile / Social Assets (1:1 square):**
  - Save as `.jpg` (`quality=92`, max 4MB) — **Do NOT convert to WebP.** GBP rejects WebP.
  - Dimensions: `1080x1080` or `1200x1200` (1:1 square)
  - Target Path: `masrisystems-app/public/images/gbp/` — **one copy, nowhere else.**

The 16:9 `.jpg` and the 1:1 `.jpg` are different crops, not duplicates — keep both when a post needs
a square social asset. Everything else is a duplicate and does not get written.

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

### Step 5: Publish to Cloudflare R2

Nothing is usable by the blog or the social CSVs until it is on R2. From `masrisystems-app/`:

```bash
php artisan storage:r2-sync --dir=public/images
```

Uploads `public/images/**` to the R2 `images/` prefix, skipping files already there (`--force` to
overwrite a regenerated asset under the same name, `--dry-run` to preview). Resulting public URLs:

```
https://pub-342a3c651bc946c795585c46f7161a33.r2.dev/images/<name>.webp   # blog body
https://pub-342a3c651bc946c795585c46f7161a33.r2.dev/images/<name>.jpg    # OG / social fallback
https://pub-342a3c651bc946c795585c46f7161a33.r2.dev/images/gbp/<name>.jpg # GBP / IG / FB square
```

Verify before handing the URL to anything else:

```bash
curl -sI <url>   # expect 200 + content-type: image/webp or image/jpeg
```
