#!/usr/bin/env python3
"""
Digital Wardrobe Operations CLI (closet.py)
Authoritative automation controller for Libre Closet (closet.masrisystems.com)
and the local Obsidian Wardrobe knowledge ecosystem.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Constants & Default Paths ---
DEFAULT_CONFIG_PATH = Path(r"C:\Users\super\.agents\config\closet.env")
DEFAULT_INVENTORY_PATH = Path(r"c:\Users\super\Projects\obsidian\masrisystems-app\content\private\General\Wardrobe\inventory.json")
DEFAULT_CUTOUT_DIR = Path(r"C:\Users\super\Pictures\closet\cutouts")
DEFAULT_CATALOGUE_PATH = Path(r"c:\Users\super\Projects\obsidian\masrisystems-app\content\private\General\Wardrobe\Master Wardrobe Catalogue.md")
DEFAULT_VALUATION_PATH = Path(r"c:\Users\super\Projects\obsidian\masrisystems-app\content\private\General\Wardrobe\Wardrobe Valuation.md")
DEFAULT_BASE_URL = "https://closet.masrisystems.com"

# Standard Libre Closet Category Taxonomy
VALID_CATEGORIES = ["tops", "bottoms", "outerwear", "footwear", "accessories", "bags", "dresses", "other"]
VALID_COLORS = [
    "black", "white", "grey", "beige", "brown", "blue", "green", "red",
    "pink", "orange", "yellow", "purple", "gold", "silver", "pattern", "other"
]


def load_env(config_path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, str]:
    """Loads credentials from closet.env."""
    env = {}
    if not config_path.exists():
        print(f"[!] Warning: Config file not found at {config_path}")
        return env

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get_authenticated_session(base_url: str = DEFAULT_BASE_URL, env: Optional[Dict[str, str]] = None):
    """Establishes an authenticated session with Libre Closet."""
    import requests

    if env is None:
        env = load_env()

    email = env.get("CLOSET_EMAIL")
    password = env.get("CLOSET_PASSWORD")

    if not email or not password:
        raise ValueError("Missing CLOSET_EMAIL or CLOSET_PASSWORD in configuration.")

    session = requests.Session()
    login_res = session.post(
        f"{base_url}/auth/login",
        data={"email": email, "password": password},
        headers={"HX-Request": "true"}
    )

    if login_res.status_code != 200 or "access_token" not in session.cookies:
        raise RuntimeError(f"Authentication failed with status {login_res.status_code}.")

    return session


def process_image_cutout(input_path: Path, output_path: Optional[Path] = None, padding_pct: float = 0.06) -> Path:
    """
    Auto-orients raw photo via EXIF, removes background with rembg U2-Net,
    and crops to bounding box with uniform percentage padding.
    """
    from PIL import Image, ImageOps
    import rembg

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    DEFAULT_CUTOUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = DEFAULT_CUTOUT_DIR / f"{input_path.stem}.png"

    print(f"[*] Processing image: {input_path.name}")
    with Image.open(input_path) as raw:
        # Step 1: Auto-orient by EXIF tag
        img = ImageOps.exif_transpose(raw)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Step 2: Remove background
        print("  - Running rembg U2-Net segmentation...")
        nobg = rembg.remove(img)

        # Step 3: Compute bounding box and apply uniform padding
        bbox = nobg.getbbox()
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            bw = max_x - min_x
            bh = max_y - min_y
            pad = int(max(bw, bh) * padding_pct)

            crop_box = (
                max(0, min_x - pad),
                max(0, min_y - pad),
                min(nobg.width, max_x + pad),
                min(nobg.height, max_y + pad)
            )
            final_img = nobg.crop(crop_box)
        else:
            final_img = nobg

        final_img.save(output_path, "PNG")
        print(f"[+] Cutout saved: {output_path} ({final_img.width}x{final_img.height} px)")

    return output_path


def load_inventory(inv_path: Path = DEFAULT_INVENTORY_PATH) -> List[dict]:
    """Loads machine SSOT inventory.json."""
    if not inv_path.exists():
        return []
    with open(inv_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_inventory(items: List[dict], inv_path: Path = DEFAULT_INVENTORY_PATH):
    """Saves updated inventory.json maintaining clean indentation."""
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved {len(items)} items to {inv_path}")


# --- Command Handlers ---

def cmd_auth_check(args):
    """Checks Libre Closet API connectivity."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    print(f"[*] Connecting to {base_url}...")
    try:
        session = get_authenticated_session(base_url, env)
        res = session.get(f"{base_url}/wardrobe")
        print(f"[+] Authentication successful! (HTTP {res.status_code})")
        print(f"    Target URL: {base_url}")
        print(f"    Account:    {env.get('CLOSET_EMAIL')}")
    except Exception as e:
        print(f"[!] Authentication check failed: {e}")
        sys.exit(1)


def cmd_cutout(args):
    """Processes a raw photo into a background-removed, padded cutout."""
    input_p = Path(args.image)
    output_p = Path(args.output) if args.output else None
    process_image_cutout(input_p, output_p, padding_pct=args.padding)


def cmd_add_garment(args):
    """Adds a new garment to Libre Closet and appends to inventory.json."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)

    # 1. Process image if provided
    cutout_path = None
    if args.image:
        img_path = Path(args.image)
        if img_path.suffix.lower() == ".png" and "cutouts" in str(img_path).lower():
            cutout_path = img_path
        else:
            cutout_path = process_image_cutout(img_path)

    # 2. Submit Garment Creation to Libre Closet
    cat = args.category.lower()
    if cat not in VALID_CATEGORIES:
        print(f"[!] Warning: Category '{cat}' may not match standard taxonomy {VALID_CATEGORIES}")

    col = args.color.lower()
    payload = {
        "name": args.name,
        "category": cat,
        "brand": args.brand or "",
        "color": col,
        "size": args.size or "",
        "washingDetails": args.washing or "",
        "dateAquired": args.date_acquired or "",
        "notes": args.notes or ""
    }

    print(f"[*] Creating garment '{args.name}' on {base_url}...")
    res = session.post(f"{base_url}/wardrobe", data=payload, allow_redirects=False)
    if res.status_code not in (200, 201, 302, 303):
        print(f"[!] Failed to create garment: HTTP {res.status_code} - {res.text[:300]}")
        sys.exit(1)

    location = res.headers.get("Location", "")
    match = re.search(r"/wardrobe/(\d+)", location)
    if not match:
        print(f"[!] Could not determine created garment ID from Location header: {location}")
        sys.exit(1)

    closet_id = int(match.group(1))
    print(f"[+] Created garment #{closet_id} on Libre Closet.")

    # 3. Upload Photo if cutout available
    if cutout_path and cutout_path.exists():
        print(f"[*] Uploading cutout photo {cutout_path.name} to garment #{closet_id}...")
        with open(cutout_path, "rb") as f:
            res_photo = session.post(
                f"{base_url}/wardrobe/{closet_id}/photo",
                files={"photo": (cutout_path.name, f, "image/png")},
                headers={"HX-Request": "true"}
            )
            if res_photo.status_code in (200, 201):
                print(f"[+] Cutout uploaded successfully (HTTP {res_photo.status_code}).")
            else:
                print(f"[!] Photo upload returned HTTP {res_photo.status_code}: {res_photo.text[:200]}")

    # 4. Append to inventory.json
    inv = load_inventory(DEFAULT_INVENTORY_PATH)
    item_id = cutout_path.stem if cutout_path else f"manual_{closet_id}"

    new_record = {
        "item_id": item_id,
        "item_name": args.name,
        "brand": args.brand or "Unknown",
        "category": args.category.capitalize(),
        "sub_category": args.sub_category or args.category.capitalize(),
        "color_primary": args.color.capitalize(),
        "color_undertone": args.undertone or "",
        "pattern": args.pattern or "Solid",
        "material_texture": args.material or "",
        "fit": args.fit or "Regular",
        "formality": args.formality or "Casual",
        "seasonality": [s.strip() for s in args.seasons.split(",")] if args.seasons else ["All-Season"],
        "cutout_path": str(cutout_path) if cutout_path else "",
        "closet_id": closet_id,
        "estimated_price_new_eur": float(args.price_new or 25.0),
        "estimated_price_used_eur": float(args.price_used or 5.0),
        "currency": "EUR"
    }

    inv.append(new_record)
    save_inventory(inv, DEFAULT_INVENTORY_PATH)

    # 5. Trigger valuation sync if requested
    if args.sync_vault:
        sync_valuation_and_vault()


def cmd_update_garment(args):
    """Updates metadata and/or photo for an existing garment."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)
    closet_id = args.closet_id

    # 1. Update photo if provided
    cutout_path = None
    if args.image:
        img_path = Path(args.image)
        if img_path.suffix.lower() == ".png" and "cutouts" in str(img_path).lower():
            cutout_path = img_path
        else:
            cutout_path = process_image_cutout(img_path)

        print(f"[*] Uploading updated photo for garment #{closet_id}...")
        with open(cutout_path, "rb") as f:
            res_photo = session.post(
                f"{base_url}/wardrobe/{closet_id}/photo",
                files={"photo": (cutout_path.name, f, "image/png")},
                headers={"HX-Request": "true"}
            )
            print(f"[+] Photo upload status: HTTP {res_photo.status_code}")

    # 2. Update Libre Closet metadata if attributes provided
    update_data = {}
    if args.name:
        update_data["name"] = args.name
    if args.category:
        update_data["category"] = args.category.lower()
    if args.brand:
        update_data["brand"] = args.brand
    if args.color:
        update_data["color"] = args.color.lower()
    if args.size:
        update_data["size"] = args.size
    if args.notes:
        update_data["notes"] = args.notes

    if update_data:
        print(f"[*] Updating metadata for garment #{closet_id}...")
        res = session.post(
            f"{base_url}/wardrobe/{closet_id}",
            data=update_data,
            headers={"HX-Request": "true"}
        )
        print(f"[+] Metadata update status: HTTP {res.status_code}")

    # 3. Update inventory.json record
    inv = load_inventory(DEFAULT_INVENTORY_PATH)
    updated = False
    for item in inv:
        if item.get("closet_id") == closet_id:
            if args.name:
                item["item_name"] = args.name
            if args.brand:
                item["brand"] = args.brand
            if args.category:
                item["category"] = args.category.capitalize()
            if args.sub_category:
                item["sub_category"] = args.sub_category
            if args.color:
                item["color_primary"] = args.color.capitalize()
            if args.undertone:
                item["color_undertone"] = args.undertone
            if args.pattern:
                item["pattern"] = args.pattern
            if args.material:
                item["material_texture"] = args.material
            if args.fit:
                item["fit"] = args.fit
            if args.formality:
                item["formality"] = args.formality
            if args.seasons:
                item["seasonality"] = [s.strip() for s in args.seasons.split(",")]
            if args.price_new is not None:
                item["estimated_price_new_eur"] = float(args.price_new)
            if args.price_used is not None:
                item["estimated_price_used_eur"] = float(args.price_used)
            if cutout_path:
                item["cutout_path"] = str(cutout_path)
                item["item_id"] = cutout_path.stem
            updated = True
            break

    if updated:
        save_inventory(inv, DEFAULT_INVENTORY_PATH)
    else:
        print(f"[!] Warning: Garment #{closet_id} not found in inventory.json")

    if args.sync_vault:
        sync_valuation_and_vault()


def cmd_delete_garment(args):
    """Deletes a garment from Libre Closet and inventory.json."""
    closet_id = args.closet_id
    if not args.force:
        confirm = input(f"Are you sure you want to permanently delete Garment #{closet_id}? (y/N): ")
        if confirm.lower() != "y":
            print("Aborted.")
            return

    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)

    print(f"[*] Deleting garment #{closet_id} from {base_url}...")
    res = session.delete(f"{base_url}/wardrobe/{closet_id}", headers={"HX-Request": "true"})
    print(f"[+] Server delete response: HTTP {res.status_code}")

    inv = load_inventory(DEFAULT_INVENTORY_PATH)
    orig_len = len(inv)
    inv = [i for i in inv if i.get("closet_id") != closet_id]
    if len(inv) < orig_len:
        save_inventory(inv, DEFAULT_INVENTORY_PATH)
        print(f"[+] Removed garment #{closet_id} from inventory.json.")
    else:
        print(f"[!] Garment #{closet_id} was not in inventory.json.")

    if args.sync_vault:
        sync_valuation_and_vault()


def cmd_list_garments(args):
    """Lists cataloged garments with optional filters."""
    inv = load_inventory(DEFAULT_INVENTORY_PATH)
    if args.category:
        inv = [i for i in inv if i.get("category", "").lower() == args.category.lower()]
    if args.brand:
        inv = [i for i in inv if args.brand.lower() in i.get("brand", "").lower()]
    if args.search:
        q = args.search.lower()
        inv = [i for i in inv if q in i.get("item_name", "").lower() or q in i.get("brand", "").lower() or q in i.get("color_primary", "").lower()]

    print(f"\n--- Wardrobe Inventory ({len(inv)} items) ---")
    print(f"{'ID':<6} | {'Brand':<18} | {'Category':<12} | {'MSRP':<8} | {'Resale':<8} | {'Item Name'}")
    print("-" * 85)
    for x in sorted(inv, key=lambda i: i.get("closet_id", 0)):
        cid = f"#{x.get('closet_id')}"
        brand = x.get('brand', '')[:17]
        cat = x.get('category', '')[:11]
        p_new = f"{x.get('estimated_price_new_eur', 0):.2f} €"
        p_used = f"{x.get('estimated_price_used_eur', 0):.2f} €"
        name = x.get('item_name', '')
        print(f"{cid:<6} | {brand:<18} | {cat:<12} | {p_new:<8} | {p_used:<8} | {name}")


def cmd_get_outfit(args):
    """Fetches outfit details and linked garments from Libre Closet."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)

    res = session.get(f"{base_url}/outfits/{args.outfit_id}")
    if res.status_code != 200:
        print(f"[!] Failed to fetch Outfit #{args.outfit_id}: HTTP {res.status_code}")
        return

    g_ids = re.findall(r'href="/wardrobe/(\d+)"', res.text)
    names = re.findall(r'<h1[^>]*>([^<]*)</h1>', res.text)
    outfit_name = names[0].strip() if names else f"Outfit #{args.outfit_id}"

    print(f"\n--- Outfit #{args.outfit_id}: {outfit_name} ---")
    print(f"Linked Garment IDs: {g_ids}")

    inv = {i.get("closet_id"): i for i in load_inventory(DEFAULT_INVENTORY_PATH)}
    for gid_str in g_ids:
        gid = int(gid_str)
        if gid in inv:
            item = inv[gid]
            print(f"  • #{gid:<3} [{item.get('category')}] {item.get('brand')} — {item.get('item_name')}")
        else:
            print(f"  • #{gid:<3} (External or uncataloged item)")


def cmd_update_outfit(args):
    """Updates an existing outfit's name and linked garments."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)
    outfit_id = args.outfit_id

    # Item pairs: category:garmentId, e.g. "tops:6,bottoms:8,outerwear:44,footwear:99"
    payload = [("returnTo", f"/outfits/{outfit_id}")]
    for pair in args.items.split(","):
        pair = pair.strip()
        if ":" in pair:
            cat, gid = pair.split(":", 1)
            payload.append(("category", cat.strip().lower()))
            payload.append(("garmentId", gid.strip()))
        else:
            print(f"[!] Error: Invalid item pair format '{pair}'. Expected 'category:id'")
            sys.exit(1)

    payload.append(("name", args.name))
    payload.append(("scheduleDate", args.date or ""))

    print(f"[*] Updating Outfit #{outfit_id} on {base_url}...")
    res = session.post(f"{base_url}/outfits/{outfit_id}", data=payload, headers={"HX-Request": "true"})
    print(f"[+] Outfit update status: HTTP {res.status_code}")


def cmd_create_outfit(args):
    """Creates a new outfit on Libre Closet."""
    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)

    payload = [("returnTo", "/outfits")]
    for pair in args.items.split(","):
        pair = pair.strip()
        if ":" in pair:
            cat, gid = pair.split(":", 1)
            payload.append(("category", cat.strip().lower()))
            payload.append(("garmentId", gid.strip()))
        else:
            print(f"[!] Error: Invalid item pair format '{pair}'. Expected 'category:id'")
            sys.exit(1)

    payload.append(("name", args.name))
    payload.append(("scheduleDate", args.date or ""))

    print(f"[*] Creating outfit '{args.name}' on {base_url}...")
    res = session.post(f"{base_url}/outfits", data=payload, allow_redirects=False)
    loc = res.headers.get("Location", "")
    match = re.search(r'/outfits/(\d+)', loc)
    if match:
        print(f"[+] Created outfit #{match.group(1)}: {args.name}")
    else:
        print(f"[+] Outfit created (status {res.status_code}, Location: {loc})")


def cmd_delete_outfit(args):
    """Deletes an outfit from Libre Closet."""
    outfit_id = args.outfit_id
    if not args.force:
        confirm = input(f"Are you sure you want to permanently delete Outfit #{outfit_id}? (y/N): ")
        if confirm.lower() != "y":
            print("Aborted.")
            return

    env = load_env(args.config)
    base_url = env.get("CLOSET_BASE_URL", DEFAULT_BASE_URL)
    session = get_authenticated_session(base_url, env)

    print(f"[*] Deleting Outfit #{outfit_id} from {base_url}...")
    res = session.delete(f"{base_url}/outfits/{outfit_id}", headers={"HX-Request": "true"})
    print(f"[+] Server delete response: HTTP {res.status_code}")


def sync_valuation_and_vault():
    """Recalculates wardrobe asset values and regenerates Obsidian valuation documentation."""
    items = load_inventory(DEFAULT_INVENTORY_PATH)
    if not items:
        print("[!] No items in inventory.json.")
        return

    cats = {}
    total_new = 0.0
    total_used = 0.0

    for x in items:
        cat = x.get("category", "Other")
        p_new = float(x.get("estimated_price_new_eur", 0.0))
        p_used = float(x.get("estimated_price_used_eur", 0.0))
        if cat not in cats:
            cats[cat] = {"count": 0, "new": 0.0, "used": 0.0}
        cats[cat]["count"] += 1
        cats[cat]["new"] += p_new
        cats[cat]["used"] += p_used
        total_new += p_new
        total_used += p_used

    # Build Top 10 rows
    top_items = sorted(items, key=lambda x: x.get('estimated_price_new_eur', 0.0), reverse=True)[:10]
    top_rows = []
    for idx, x in enumerate(top_items, 1):
        top_rows.append(
            f"| **{idx}** | #{x.get('closet_id')} | **{x.get('brand')}** | {x.get('item_name')} | {x.get('category')} | **{x.get('estimated_price_new_eur'):.2f} €** | **{x.get('estimated_price_used_eur'):.2f} €** |"
        )

    # Build All 114+ rows
    all_rows = []
    for x in sorted(items, key=lambda item: item.get('closet_id', 0)):
        all_rows.append(
            f"| #{x.get('closet_id')} | {x.get('item_name')} | {x.get('brand')} | {x.get('category')} | {x.get('color_primary', '')} | {x.get('estimated_price_new_eur', 0.0):.2f} € | {x.get('estimated_price_used_eur', 0.0):.2f} € |"
        )

    content = f"""---
title: "Wardrobe Valuation & Financial Asset Summary"
description: "Realistic retail MSRP and conservative secondhand resale valuation for all {len(items)} cataloged wardrobe pieces in Mohamad Masri's digital closet."
tags:
  - wardrobe
  - valuation
  - inventory
  - personal-finance
  - libre-closet
created: 2026-09-27
updated: 2026-09-29
author: Mohamad Masri
layout: default
status: published
---

# Wardrobe Valuation & Financial Asset Summary

> [!info] **Valuation Scope & Realistic Market Baseline**
> - **Total Cataloged Pieces:** {len(items)} pieces *(Complete Multi-Category Portfolio)*
> - **Total Replacement Value (Retail MSRP New):** **{total_new:,.2f} €** (avg. {total_new/len(items):.2f} € / piece)
> - **Realistic Secondhand Resale Value (Vinted / Kleinanzeigen):** **{total_used:,.2f} €** (avg. {total_used/len(items):.2f} € / piece)
> - **Depreciation Ratio:** Real-world pre-owned liquidation yields ~{total_used/total_new*100:.1f}% of original retail MSRP after market depreciation and platform fees.
> - **SSOT Data Source:** [inventory.json](file:///c:/Users/super/Projects/obsidian/masrisystems-app/content/private/General/Wardrobe/inventory.json)

---

## 1. Executive Summary & Category Breakdown

```mermaid
pie title Wardrobe Resale Value Share (Pre-Owned Liquidation)
    "Tops ({cats.get('Tops', {}).get('count', 0)} items)" : {int(cats.get('Tops', {}).get('used', 0))}
    "Footwear ({cats.get('Footwear', {}).get('count', 0)} pairs)" : {int(cats.get('Footwear', {}).get('used', 0))}
    "Accessories ({cats.get('Accessories', {}).get('count', 0)} items)" : {int(cats.get('Accessories', {}).get('used', 0))}
    "Outerwear ({cats.get('Outerwear', {}).get('count', 0)} items)" : {int(cats.get('Outerwear', {}).get('used', 0))}
    "Bottoms ({cats.get('Bottoms', {}).get('count', 0)} items)" : {int(cats.get('Bottoms', {}).get('used', 0))}
    "Bags ({cats.get('Bags', {}).get('count', 0)} items)" : {int(cats.get('Bags', {}).get('used', 0))}
```

| Category | Item Count | Total New Value (MSRP) | Realistic Used Resale | Avg. New / Piece | Realistic Avg. Used |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tops** *(T-Shirts, Polos, Sweaters, Hoodies, Shirts)* | {cats.get('Tops', {}).get('count', 0)} | **{cats.get('Tops', {}).get('new', 0):,.2f} €** | **{cats.get('Tops', {}).get('used', 0):,.2f} €** | {cats.get('Tops', {}).get('new', 0)/cats.get('Tops', {}).get('count', 1):.2f} € | {cats.get('Tops', {}).get('used', 0)/cats.get('Tops', {}).get('count', 1):.2f} € |
| **Bottoms** *(Jeans, Chinos, Cargo Pants, Joggers, Shorts)* | {cats.get('Bottoms', {}).get('count', 0)} | **{cats.get('Bottoms', {}).get('new', 0):,.2f} €** | **{cats.get('Bottoms', {}).get('used', 0):,.2f} €** | {cats.get('Bottoms', {}).get('new', 0)/cats.get('Bottoms', {}).get('count', 1):.2f} € | {cats.get('Bottoms', {}).get('used', 0)/cats.get('Bottoms', {}).get('count', 1):.2f} € |
| **Outerwear** *(Pea Coat, Sherpa Trucker, Windbreakers, Puffer, Bombers)* | {cats.get('Outerwear', {}).get('count', 0)} | **{cats.get('Outerwear', {}).get('new', 0):,.2f} €** | **{cats.get('Outerwear', {}).get('used', 0):,.2f} €** | {cats.get('Outerwear', {}).get('new', 0)/cats.get('Outerwear', {}).get('count', 1):.2f} € | {cats.get('Outerwear', {}).get('used', 0)/cats.get('Outerwear', {}).get('count', 1):.2f} € |
| **Footwear** *(Chelsea Boots, Minimalist Court, Retro Mid-Tops, Running)* | {cats.get('Footwear', {}).get('count', 0)} | **{cats.get('Footwear', {}).get('new', 0):,.2f} €** | **{cats.get('Footwear', {}).get('used', 0):,.2f} €** | {cats.get('Footwear', {}).get('new', 0)/cats.get('Footwear', {}).get('count', 1):.2f} € | {cats.get('Footwear', {}).get('used', 0)/cats.get('Footwear', {}).get('count', 1):.2f} € |
| **Accessories** *(Hugo Boss Watch, Niche Fragrances, Scarves, Beanies, Caps)* | {cats.get('Accessories', {}).get('count', 0)} | **{cats.get('Accessories', {}).get('new', 0):,.2f} €** | **{cats.get('Accessories', {}).get('used', 0):,.2f} €** | {cats.get('Accessories', {}).get('new', 0)/cats.get('Accessories', {}).get('count', 1):.2f} € | {cats.get('Accessories', {}).get('used', 0)/cats.get('Accessories', {}).get('count', 1):.2f} € |
| **Bags** *(Uniqlo Crossbody Shoulder Bag, Bench Utility Sling)* | {cats.get('Bags', {}).get('count', 0)} | **{cats.get('Bags', {}).get('new', 0):,.2f} €** | **{cats.get('Bags', {}).get('used', 0):,.2f} €** | {cats.get('Bags', {}).get('new', 0)/cats.get('Bags', {}).get('count', 1):.2f} € | {cats.get('Bags', {}).get('used', 0)/cats.get('Bags', {}).get('count', 1):.2f} € |
| **Total Wardrobe Portfolio** | **{len(items)}** | **{total_new:,.2f} €** | **{total_used:,.2f} €** | **{total_new/len(items):.2f} €** | **{total_used/len(items):.2f} €** |

---

## 2. Top 10 Most Valuable Pieces (Retail vs. Real Resale)

These anchor pieces hold the highest individual replacement cost and resale liquidity:

| Rank | ID | Brand | Item Name | Category | New (MSRP) | Realistic Resale |
| :---: | :---: | :--- | :--- | :--- | :---: | :---: |
""" + "\n".join(top_rows) + f"""

---

## 3. Valuation Methodology & Resale Liquidity Insights

> [!tip] **Depreciation & Secondary Market Heuristics**
> 1. **Outerwear & Heavy Tailoring (Selected Homme, Selected Pea Coat, Sherpa):** Highest resale retention (25% – 30% of MSRP). Cold-weather staples retain structural and thermal value.
> 2. **Premium Timepieces & Fragrances (Hugo Boss Chronograph, Purple Ruby, Khamrah):** Niche and luxury fragrances liquidate rapidly on fragrance enthusiast boards at 40% – 50% of bottle retail.
> 3. **Footwear (Chelsea Boots, Retro Sneakers):** Pre-owned footwear depreciates heavily (15% – 25% of retail) due to personal sole wear, except pristine or deadstock sneakers.
> 4. **Athletic & Gym Staples (Gymshark, Puma, Nike):** High-volume items trade on Vinted consistently between 4,00 € and 10,00 € per piece regardless of initial retail.
> 5. **High-Street Casuals (H&M, Primark, Zara, SMOG):** Minimal resale liquidity (2,00 € – 4,00 € per piece). Primary value exists in personal wear utility.
> 6. **Designer / Premium Labels (Polo Ralph Lauren, Lacoste, Calvin Klein):** Tops and vintage denim hold reliable ceilings at 18,00 € – 24,00 €.

---

## 4. Complete {len(items)}-Piece Inventory Price Roster

| ID | Item Name | Brand | Category | Color | MSRP New | Realistic Used |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
""" + "\n".join(all_rows) + "\n"

    with open(DEFAULT_VALUATION_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Regenerated {DEFAULT_VALUATION_PATH} ({len(content)} bytes).")


def cmd_sync_valuation(args):
    """CLI trigger for valuation sync."""
    sync_valuation_and_vault()


def main():
    parser = argparse.ArgumentParser(description="Digital Wardrobe Operations Controller (closet.py)")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to closet.env")
    subparsers = parser.add_subparsers(dest="subcommand", required=True, help="Subcommand to execute")

    # auth-check
    p_auth = subparsers.add_parser("auth-check", help="Check Libre Closet connectivity and authentication")
    p_auth.set_defaults(func=cmd_auth_check)

    # cutout
    p_cut = subparsers.add_parser("cutout", help="Remove background, auto-orient, and crop raw garment photo")
    p_cut.add_argument("image", help="Path to raw image file")
    p_cut.add_argument("--output", "-o", help="Optional explicit output path")
    p_cut.add_argument("--padding", "-p", type=float, default=0.06, help="Uniform bounding box padding ratio (default 0.06)")
    p_cut.set_defaults(func=cmd_cutout)

    # add-garment
    p_add = subparsers.add_parser("add-garment", help="Add new garment to Libre Closet and inventory.json")
    p_add.add_argument("--name", required=True, help="Item name")
    p_add.add_argument("--category", required=True, help="Category (tops, bottoms, outerwear, footwear, accessories, bags)")
    p_add.add_argument("--brand", default="Unknown", help="Brand name")
    p_add.add_argument("--color", default="other", help="Primary color")
    p_add.add_argument("--image", help="Path to photo (raw or cutout)")
    p_add.add_argument("--sub-category", help="Specific sub-category")
    p_add.add_argument("--undertone", help="Color undertone description")
    p_add.add_argument("--pattern", default="Solid", help="Pattern (Solid, Striped, Plaid, etc.)")
    p_add.add_argument("--material", help="Material and texture description")
    p_add.add_argument("--fit", default="Regular", help="Fit (Regular, Slim, Relaxed, Oversized)")
    p_add.add_argument("--formality", default="Casual", help="Formality level description")
    p_add.add_argument("--seasons", help="Comma-separated seasons (e.g. 'Fall,Winter,Spring')")
    p_add.add_argument("--size", help="Size tag (e.g. M, L, 32, Relaxed Fit)")
    p_add.add_argument("--washing", help="Washing instructions")
    p_add.add_argument("--date-acquired", help="Date acquired (YYYY-MM-DD)")
    p_add.add_argument("--notes", help="Item notes")
    p_add.add_argument("--price-new", type=float, default=25.0, help="MSRP New in EUR")
    p_add.add_argument("--price-used", type=float, default=5.0, help="Pre-Owned Resale in EUR")
    p_add.add_argument("--sync-vault", action="store_true", help="Sync Obsidian valuation and metrics")
    p_add.set_defaults(func=cmd_add_garment)

    # update-garment
    p_upd = subparsers.add_parser("update-garment", help="Update garment metadata and/or photo")
    p_upd.add_argument("closet_id", type=int, help="Libre Closet Garment ID")
    p_upd.add_argument("--name", help="New item name")
    p_upd.add_argument("--brand", help="New brand name")
    p_upd.add_argument("--category", help="New category")
    p_upd.add_argument("--sub-category", help="New sub-category")
    p_upd.add_argument("--color", help="New primary color")
    p_upd.add_argument("--undertone", help="New undertone")
    p_upd.add_argument("--pattern", help="New pattern")
    p_upd.add_argument("--material", help="New material")
    p_upd.add_argument("--fit", help="New fit")
    p_upd.add_argument("--formality", help="New formality")
    p_upd.add_argument("--seasons", help="New comma-separated seasons")
    p_upd.add_argument("--size", help="New size")
    p_upd.add_argument("--notes", help="New notes")
    p_upd.add_argument("--image", help="New photo path to process and upload")
    p_upd.add_argument("--price-new", type=float, help="Updated MSRP New in EUR")
    p_upd.add_argument("--price-used", type=float, help="Updated Pre-Owned Resale in EUR")
    p_upd.add_argument("--sync-vault", action="store_true", help="Sync Obsidian valuation and metrics")
    p_upd.set_defaults(func=cmd_update_garment)

    # delete-garment
    p_del = subparsers.add_parser("delete-garment", help="Delete garment from Libre Closet and inventory.json")
    p_del.add_argument("closet_id", type=int, help="Libre Closet Garment ID")
    p_del.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    p_del.add_argument("--sync-vault", action="store_true", help="Sync Obsidian valuation and metrics")
    p_del.set_defaults(func=cmd_delete_garment)

    # list-garments
    p_list = subparsers.add_parser("list-garments", help="List cataloged wardrobe items")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--brand", help="Filter by brand substring")
    p_list.add_argument("--search", help="Search keyword across name, brand, color")
    p_list.set_defaults(func=cmd_list_garments)

    # get-outfit
    p_o_get = subparsers.add_parser("get-outfit", help="Get outfit details and linked garments")
    p_o_get.add_argument("outfit_id", type=int, help="Libre Closet Outfit ID")
    p_o_get.set_defaults(func=cmd_get_outfit)

    # create-outfit
    p_o_new = subparsers.add_parser("create-outfit", help="Create new outfit on Libre Closet")
    p_o_new.add_argument("--name", required=True, help="Outfit name")
    p_o_new.add_argument("--items", required=True, help="Comma-separated category:id pairs (e.g. tops:6,bottoms:8,footwear:99)")
    p_o_new.add_argument("--date", help="Optional scheduled date (YYYY-MM-DD)")
    p_o_new.set_defaults(func=cmd_create_outfit)

    # update-outfit
    p_o_upd = subparsers.add_parser("update-outfit", help="Update outfit on Libre Closet")
    p_o_upd.add_argument("outfit_id", type=int, help="Libre Closet Outfit ID")
    p_o_upd.add_argument("--name", required=True, help="Outfit name")
    p_o_upd.add_argument("--items", required=True, help="Comma-separated category:id pairs (e.g. tops:6,bottoms:8,footwear:99)")
    p_o_upd.add_argument("--date", help="Optional scheduled date (YYYY-MM-DD)")
    p_o_upd.set_defaults(func=cmd_update_outfit)

    # delete-outfit
    p_o_del = subparsers.add_parser("delete-outfit", help="Delete outfit from Libre Closet")
    p_o_del.add_argument("outfit_id", type=int, help="Libre Closet Outfit ID")
    p_o_del.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    p_o_del.set_defaults(func=cmd_delete_outfit)

    # sync-valuation
    p_val = subparsers.add_parser("sync-valuation", help="Recalculate asset values and update Wardrobe Valuation.md")
    p_val.set_defaults(func=cmd_sync_valuation)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
