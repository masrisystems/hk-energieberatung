"""
EverShelf CLI & Kitchen Integration Client
Authoritative tool for pulling, updating, and pushing kitchen inventory and shopping lists
directly to EverShelf (https://kitchen.masrisystems.com).
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# Windows console encoding safeguard
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = os.environ.get("EVERSHELF_URL", "https://kitchen.masrisystems.com").rstrip("/")
API_URL = f"{BASE_URL}/api/index.php"

# Map user-friendly locations to EverShelf internal DB codes
LOCATIONS = {
    "fridge": "frigo",
    "kühlschrank": "frigo",
    "frigo": "frigo",
    "pantry": "dispensa",
    "vorrat": "dispensa",
    "dispensa": "dispensa",
    "freezer": "freezer",
    "tiefkühltruhe": "freezer",
    "gefrierfach": "freezer",
}


def call_api(action, method="GET", body=None, params=None):
    url = f"{API_URL}?action={action}"
    if params:
        for k, v in params.items():
            url += f"&{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}"

    headers = {
        "User-Agent": "EverShelf-Chef-Agent/1.0",
        "X-EverShelf-Request": "1",
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"status": resp.status, "raw": content}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return {"error": f"HTTP {e.code}", "details": err_body}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────────────────────
# 1. PULL (Read Live EverShelf Data)
# ─────────────────────────────────────────────────────────────

def pull_inventory(as_json=False):
    res = call_api("inventory_list")
    inv = res.get("inventory", [])
    if as_json:
        print(json.dumps(inv, indent=2, ensure_ascii=False))
        return

    if not inv:
        print("EverShelf inventory is currently empty.")
        return

    print(f"📦 EverShelf Inventory ({len(inv)} items at {BASE_URL}):\n")
    print(f"{'ID':<4} | {'Location':<10} | {'Name':<24} | {'Qty':<10} | {'Expiry':<12} | {'Brand'}")
    print("-" * 75)
    for it in inv:
        loc = it.get("location", "unknown")
        name = it.get("name", "Unknown")[:23]
        qty = f"{it.get('quantity', 0)} {it.get('unit', '')}".strip()
        expiry = it.get("expiry_date") or "-"
        brand = it.get("brand") or "-"
        print(f"{it.get('id', 0):<4} | {loc:<10} | {name:<24} | {qty:<10} | {expiry:<12} | {brand}")


def pull_shopping(as_json=False):
    res = call_api("shopping_list")
    purchase = res.get("purchase", [])
    if as_json:
        print(json.dumps(purchase, indent=2, ensure_ascii=False))
        return

    if not purchase:
        print("EverShelf shopping list is currently empty.")
        return

    print(f"🛒 EverShelf Shopping List ({len(purchase)} items at {BASE_URL}):\n")
    for idx, it in enumerate(purchase, 1):
        spec = f" — {it['specification']}" if it.get("specification") else ""
        print(f"  {idx}. [ ] {it.get('name', 'Item')}{spec}")


# ─────────────────────────────────────────────────────────────
# 2. PUSH (Add to Shopping List or Inventory)
# ─────────────────────────────────────────────────────────────

def push_shopping(items):
    payload = {"items": []}
    for it in items:
        entry = {"name": it["name"]}
        if "spec" in it and it["spec"]:
            entry["specification"] = it["spec"]
        payload["items"].append(entry)

    res = call_api("shopping_add", method="POST", body=payload)
    if res.get("success"):
        print(f"✅ Added {res.get('added', 0)} item(s) to EverShelf shopping list (Skipped: {res.get('skipped', 0)}).")
    else:
        print("❌ Error adding to shopping list:", res)


def push_inventory(name, qty, unit="g", location="frigo", expiry=None, brand=""):
    loc_code = LOCATIONS.get(location.lower(), location)
    
    # 1. Check if product exists in catalog or create it
    prod_res = call_api("products_search", params={"q": name})
    products = prod_res.get("products", []) if isinstance(prod_res, dict) else []
    
    prod_id = None
    for p in products:
        if p.get("name", "").lower() == name.lower():
            prod_id = p.get("id")
            break

    if not prod_id:
        # Create product in catalog
        save_res = call_api("product_save", method="POST", body={
            "name": name,
            "brand": brand or "",
            "category": "altro",
            "unit": unit,
            "default_quantity": qty,
        })
        prod_id = save_res.get("id")

    if not prod_id:
        print("❌ Could not create or find product ID for:", name)
        return

    # 2. Add inventory item
    inv_payload = {
        "product_id": prod_id,
        "quantity": float(qty),
        "location": loc_code,
        "unit": unit,
        "expiry_date": expiry or None,
    }
    inv_res = call_api("inventory_add", method="POST", body=inv_payload)
    if inv_res.get("success") or inv_res.get("id"):
        print(f"✅ Added to EverShelf [{loc_code}]: {qty} {unit} {name} (Expiry: {expiry or 'none'})")
    else:
        print("❌ Error adding to inventory:", inv_res)


# ─────────────────────────────────────────────────────────────
# 3. UPDATE (Consume / Modify Inventory or Shopping)
# ─────────────────────────────────────────────────────────────

def update_consume(name_or_id, qty, location=None):
    # If integer, use item id directly
    inv_res = call_api("inventory_list")
    inv = inv_res.get("inventory", [])

    target = None
    try:
        item_id = int(name_or_id)
        for it in inv:
            if it.get("id") == item_id:
                target = it
                break
    except ValueError:
        for it in inv:
            if it.get("name", "").lower() == str(name_or_id).lower():
                target = it
                break

    if not target:
        print(f"❌ Item '{name_or_id}' not found in current EverShelf inventory.")
        return

    item_id = target["id"]
    current_qty = float(target.get("quantity", 0))
    deduct_qty = float(qty)

    if deduct_qty >= current_qty:
        # Consume completely
        res = call_api("inventory_use", method="POST", body={
            "id": item_id,
            "product_id": target.get("product_id"),
            "use_all": True,
            "location": target.get("location"),
        })
        print(f"✅ Consumed all {current_qty} {target.get('unit')} of '{target.get('name')}' (Depleted).")
    else:
        # Partial deduction via inventory_update
        new_qty = current_qty - deduct_qty
        res = call_api("inventory_update", method="POST", body={
            "id": item_id,
            "quantity": new_qty,
            "location": target.get("location"),
        })
        print(f"✅ Consumed {deduct_qty} {target.get('unit')} of '{target.get('name')}'. New balance: {new_qty} {target.get('unit')}.")


def update_shopping_remove(item_names):
    payload = {"items": [{"name": n} for n in item_names]}
    res = call_api("shopping_remove", method="POST", body=payload)
    if res.get("success"):
        print(f"✅ Removed {len(item_names)} item(s) from shopping list.")
    else:
        print("❌ Error removing shopping items:", res)


# ─────────────────────────────────────────────────────────────
# CLI ROUTER
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EverShelf Live Kitchen Manager CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. PULL
    p_pull = subparsers.add_parser("pull", help="Pull live inventory or shopping list from EverShelf")
    p_pull.add_argument("--inventory", action="store_true", help="Pull inventory list")
    p_pull.add_argument("--shopping", action="store_true", help="Pull shopping list")
    p_pull.add_argument("--json", action="store_true", help="Output raw JSON")

    # 2. PUSH
    p_push = subparsers.add_parser("push", help="Push items to shopping list or inventory")
    p_push.add_argument("--shopping", nargs="+", help="Items to add to shopping list (e.g. 'Skyr:Lidl 500g' or 'Brokkoli')")
    p_push.add_argument("--inventory", action="store_true", help="Add an item to inventory")
    p_push.add_argument("--name", help="Item name for inventory")
    p_push.add_argument("--qty", type=float, help="Quantity")
    p_push.add_argument("--unit", default="g", help="Unit (g, kg, ml, l, pcs)")
    p_push.add_argument("--location", default="frigo", help="Location (fridge, pantry, freezer)")
    p_push.add_argument("--expiry", help="Expiry date (YYYY-MM-DD)")
    p_push.add_argument("--brand", default="", help="Brand name")

    # 3. UPDATE
    p_upd = subparsers.add_parser("update", help="Update stock, consume ingredients, or remove shopping items")
    p_upd.add_argument("--consume", help="Item name or ID to consume")
    p_upd.add_argument("--qty", type=float, default=1.0, help="Amount to consume")
    p_upd.add_argument("--shopping-remove", nargs="+", help="Item name(s) to remove from shopping list")

    args = parser.parse_args()

    if args.subcommand == "pull":
        if args.shopping:
            pull_shopping(as_json=args.json)
        else:
            pull_inventory(as_json=args.json)

    elif args.subcommand == "push":
        if args.shopping:
            items = []
            for raw in args.shopping:
                if ":" in raw:
                    name, spec = raw.split(":", 1)
                    items.append({"name": name.strip(), "spec": spec.strip()})
                else:
                    items.append({"name": raw.strip(), "spec": ""})
            push_shopping(items)
        elif args.inventory:
            if not args.name or args.qty is None:
                print("❌ --name and --qty required for inventory push")
                return
            push_inventory(args.name, args.qty, args.unit, args.location, args.expiry, args.brand)

    elif args.subcommand == "update":
        if args.consume:
            update_consume(args.consume, args.qty)
        elif args.shopping_remove:
            update_shopping_remove(args.shopping_remove)


if __name__ == "__main__":
    main()
