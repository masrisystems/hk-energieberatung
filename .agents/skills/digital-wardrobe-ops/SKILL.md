---
name: digital-wardrobe-ops
description: Operational controller for Mohamad Masri's self-hosted Libre Closet platform (closet.masrisystems.com) and the local Obsidian wardrobe knowledge base. Automates background removal (rembg), EXIF auto-orientation, garment creation/updating/deletion, outfit choreography, valuation modeling, and 1:1 SSOT synchronization. Eliminates ad-hoc scripting for wardrobe maintenance.
---

# Digital Wardrobe Operations Skill (`digital-wardrobe-ops`)

## 1. Quick Reference & Core Invariants

- **Production Platform:** `https://closet.masrisystems.com`
- **CLI Controller Tool:** `python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py"`
- **Credentials Config:** `C:\Users\super\.agents\config\closet.env` (`CLOSET_EMAIL`, `CLOSET_PASSWORD`, `CLOSET_BASE_URL`)
- **Machine SSOT Inventory:** [`content/private/General/Wardrobe/inventory.json`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/inventory.json)
- **Local Photo Cutouts:** `C:\Users\super\Pictures\closet\cutouts\`
- **Authoritative Vault Documentation Hub:**
  - Master Catalogue: [`content/private/General/Wardrobe/Master Wardrobe Catalogue.md`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/Master%20Wardrobe%20Catalogue.md)
  - Outfit to Event Matrix: [`content/private/General/Wardrobe/Outfit to Event Matrix.md`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/Outfit%20to%20Event%20Matrix.md)
  - Occasion Style Guide: [`content/private/General/Wardrobe/Events and Occasions Style Guide.md`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/Events%20and%20Occasions%20Style%20Guide.md)
  - Styling Persona SSOT: [`content/private/General/Wardrobe/Mohamad Masri — Styling Persona & Wardrobe Blueprint.md`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/Mohamad%20Masri%20%E2%80%94%20Styling%20Persona%20&%20Wardrobe%20Blueprint.md)
  - Financial Asset Valuation: [`content/private/General/Wardrobe/Wardrobe Valuation.md`](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/Wardrobe%20Valuation.md)

---

## 2. Inviolable Operational Rules

1. **Zero-Access Privacy Boundaries (Global Invariant):**
   - Under no circumstances inspect, log, or expose `.env` credentials, private keys, or personal financial documents. Use the centralized `closet.env` file solely through automated scripts.
2. **No Emojis in UI / Artifacts:**
   - Adhere strictly to the clean UI directive: never use emojis in generated documentation, tables, or interface code. Use clean Markdown, Obsidian callouts (`> [!info]`, `> [!tip]`), and vector icons where applicable.
3. **EXIF Orientation Auto-Correction:**
   - Always apply `ImageOps.exif_transpose` on raw camera photos (orientation tag 6 / 90° clockwise rotation) before passing to segmentation models, preventing sideways garment uploads.
4. **Uniform Cutout Padding (6% Ratio):**
   - Segmented garments must be tightly bounded with a uniform 6% breathing margin (`padding_pct=0.06`) relative to the longest dimension, clamped cleanly to image boundaries.
5. **Strict SSOT Parity:**
   - Every change on Libre Closet (`closet.masrisystems.com`) must be instantly mirrored in `inventory.json`. Any addition, price update, or deletion must trigger a valuation recalculation to ensure the 114+ piece price roster remains exact.
6. **Date Timestamp Invariant:**
   - When modifying any Obsidian note, always update the frontmatter field `updated: YYYY-MM-DD` to the current date.

---

## 3. CLI Command Reference (`closet.py`)

Always run the official CLI tool instead of generating throwaway scripts:

### Connectivity & Diagnostics
```powershell
# Verify API connection and authentication status
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" auth-check
```

### Background Removal & Image Processing
```powershell
# Process raw photo into an upright, transparent, padded PNG cutout
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" cutout "C:\Users\super\Downloads\Mobile Devices\photo.jpg"
```

### Adding New Garments
```powershell
# Ingest new piece: segments photo, creates on server, uploads photo, appends to inventory.json
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" add-garment `
  --image "C:\Users\super\Pictures\closet\new_jacket.jpg" `
  --name "Charcoal Double-Breasted Wool Pea Coat" `
  --category "outerwear" `
  --brand "Selected Homme" `
  --color "grey" `
  --size "M" `
  --price-new 180.0 `
  --price-used 55.0 `
  --sync-vault
```

### Updating Existing Garments
```powershell
# Update metadata and/or replace photo
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" update-garment 2 `
  --name "C&A Black Textured Long-Sleeve Crewneck Shirt" `
  --brand "C&A" `
  --category "tops" `
  --image "C:\Users\super\Pictures\closet\20260929_184935.jpg" `
  --price-new 22.0 `
  --price-used 6.0 `
  --sync-vault
```

### Deleting Garments
```powershell
# Delete from Libre Closet and remove from inventory.json
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" delete-garment 15 --force --sync-vault
```

### Listing & Searching Inventory
```powershell
# List all items filtered by brand or search term
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" list-garments --brand "Puma"
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" list-garments --search "hoodie"
```

### Managing Outfits
```powershell
# Inspect an existing outfit and its linked wardrobe pieces
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" get-outfit 17

# Create a new outfit on Libre Closet
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" create-outfit `
  --name "Autumn Evening City Walk" `
  --items "outerwear:93,tops:86,bottoms:91,footwear:104,accessories:95"

# Update an existing outfit's pieces or name
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" update-outfit 17 `
  --name "Volleyball & Active Sport: Puma Athletic Set" `
  --items "outerwear:44,tops:6,bottoms:8,footwear:99"

# Delete an outfit
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" delete-outfit 25 --force
```

### Financial Valuation & Vault Sync
```powershell
# Recalculate MSRP and resale values and regenerate Wardrobe Valuation.md
python "C:\Users\super\.agents\skills\digital-wardrobe-ops\scripts\closet.py" sync-valuation
```

---

## 4. End-to-End Operational Workflows

### Workflow A: Ingesting New Garment Batches (e.g. from Mobile Devices)
1. **Locate Files:** Identify new photos in `C:\Users\super\Downloads\Mobile Devices\` or `C:\Users\super\Pictures\closet\`.
2. **Inspect & Tag:** Inspect garment details (brand tags, material, cut, neck label, wash tags).
3. **Execute Ingestion:** Run `closet.py add-garment` for each piece with realistic MSRP and used resale pricing.
4. **Update Master Catalogue:** Add the piece to the appropriate category section in `Master Wardrobe Catalogue.md`.
5. **Sync Valuation:** Run `closet.py sync-valuation` to regenerate `Wardrobe Valuation.md` and update totals.

### Workflow B: Replacing / Correcting an Existing Garment
1. **Identify Existing ID:** Lookup `closet_id` in `inventory.json` or via `closet.py list-garments --search "<name>"`.
2. **Execute Update:** Run `closet.py update-garment <id> --image "<new_photo>" --name "<corrected_name>" --brand "<brand>" ... --sync-vault`.
3. **Review Linked Outfits:** Inspect outfits linked to this ID via `closet.py get-outfit <id>`. If the garment changed form factor (e.g. sleeveless tank changed to long-sleeve winter shirt), realign affected outfits using `closet.py update-outfit`.
4. **Audit Markdown Files:** Use grep to check for references to the old item name in `Outfit to Event Matrix.md`, `Events and Occasions Style Guide.md`, and `Mohamad Masri — Styling Persona & Wardrobe Blueprint.md`, and update them accordingly.

### Workflow C: Decommissioning / Deleting a Garment
1. **Check Dependencies:** Verify whether the garment is referenced in active outfits (`closet.py get-outfit`).
2. **Reassign Outfits:** Swap the garment out of any linked outfits before deleting.
3. **Delete:** Execute `closet.py delete-garment <id> --force --sync-vault`.
4. **Clean Catalogue:** Remove the garment row from `Master Wardrobe Catalogue.md`.

---

## 5. Libre Closet HTMX & REST Endpoint Specifications

When lower-level script integration is necessary, interact with the server using these raw endpoint contracts:

* **Authentication:**
  - `POST /auth/login`
  - Body: `{"email": "<CLOSET_EMAIL>", "password": "<CLOSET_PASSWORD>"}`
  - Header: `HX-Request: true`
  - Result: HTTP 200 with session cookie (`access_token`).

* **Create Garment:**
  - `POST /wardrobe`
  - Body (form data): `name`, `category`, `brand`, `color`, `size`, `washingDetails`, `dateAquired`, `notes`
  - Result: HTTP 302 Redirect to `/wardrobe/{id}`.

* **Upload Garment Photo:**
  - `POST /wardrobe/{id}/photo`
  - Body (multipart): `photo: (filename.png, binary_stream, "image/png")`
  - Header: `HX-Request: true`
  - Result: HTTP 200/201.

* **Update Garment Metadata:**
  - `POST /wardrobe/{id}`
  - Body (form data): `name`, `category`, `brand`, `color`, `size`, `notes`, `washingDetails`, `dateAquired`
  - Header: `HX-Request: true`
  - Result: HTTP 200.

* **Delete Garment:**
  - `DELETE /wardrobe/{id}`
  - Header: `HX-Request: true`
  - Result: HTTP 200.

* **Create Outfit:**
  - `POST /outfits`
  - Body (multi-value list): `("returnTo", "/outfits")`, pairs of `("category", cat)` and `("garmentId", gid)`, `("name", name)`, `("scheduleDate", "")`
  - Result: HTTP 302 Redirect to `/outfits/{id}`.

* **Update Outfit:**
  - `POST /outfits/{id}`
  - Body: Same multi-value structure with `returnTo: /outfits/{id}`.
  - Header: `HX-Request: true`
  - Result: HTTP 200.

* **Delete Outfit:**
  - `DELETE /outfits/{id}`
  - Header: `HX-Request: true`
  - Result: HTTP 200.
