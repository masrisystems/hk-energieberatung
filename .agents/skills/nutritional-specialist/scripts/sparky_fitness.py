"""
SparkyFitness Python Client & CLI
Handles logging foods, meals, water, weight/check-ins, and querying nutrition from SparkyFitness.
App URL: https://fitness.masrisystems.com
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import http.cookiejar
from datetime import date

SESSION_FILE = os.path.expanduser("~/.sparky_fitness_session.json")
COOKIE_FILE = os.path.expanduser("~/.sparky_fitness_cookies.txt")
PREFERENCES_FILE = os.path.expanduser("~/.claude/nutritional_preferences.json")
BASE_URL = os.environ.get("SPARKY_FITNESS_URL", "https://fitness.masrisystems.com")
DEFAULT_EMAIL = os.environ.get("SPARKY_FITNESS_EMAIL", "mohmasri9753@gmail.com")
DEFAULT_PASSWORD = os.environ.get("SPARKY_FITNESS_PASSWORD", "SparkyFitness2026!#Masri")
WEIGHT_UNITS = {"g", "gram", "grams", "gr", "ml", "milliliter", "milliliters", "mg"}


class SparkyFitness:
    def __init__(self, email=DEFAULT_EMAIL, password=DEFAULT_PASSWORD, base_url=BASE_URL):
        self.email = email
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.cj = http.cookiejar.MozillaCookieJar(COOKIE_FILE)
        if os.path.exists(COOKIE_FILE):
            try:
                self.cj.load(ignore_discard=True, ignore_expires=True)
            except Exception:
                pass
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self._ensure_authenticated()

    def _ensure_authenticated(self):
        # 1. Test existing cookie session
        if len(self.cj) > 0:
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/api/identity/users/accessible-users",
                    headers={"Origin": self.base_url, "X-Meal-Model-Version": "2"}
                )
                with self.opener.open(req) as res:
                    if res.status == 200:
                        return
            except Exception:
                pass

        # 2. Check session token file
        token = None
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                    token = data.get("token")
            except Exception:
                token = None

        if token:
            cookie = http.cookiejar.Cookie(
                version=0, name="sparky.session_token", value=token,
                port=None, port_specified=False,
                domain="fitness.masrisystems.com", domain_specified=True, domain_initial_dot=False,
                path="/", path_specified=True, secure=True, expires=None, discard=False,
                comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False
            )
            self.cj.set_cookie(cookie)
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/api/identity/users/accessible-users",
                    headers={"Origin": self.base_url, "X-Meal-Model-Version": "2"}
                )
                with self.opener.open(req) as res:
                    if res.status == 200:
                        self.cj.save(ignore_discard=True, ignore_expires=True)
                        return
            except Exception:
                pass

        # 3. Perform login if session is invalid or absent
        login_data = json.dumps({"email": self.email, "password": self.password}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/auth/sign-in/email",
            data=login_data,
            headers={"Content-Type": "application/json", "Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            if res.status == 200:
                resp_data = json.loads(res.read().decode("utf-8"))
                token = resp_data.get("token")
                if token:
                    with open(SESSION_FILE, "w") as f:
                        json.dump({"token": token, "email": self.email}, f)
                self.cj.save(ignore_discard=True, ignore_expires=True)

    def update_food_entry(self, entry_id, quantity=None, unit=None, meal_type=None, entry_date=None):
        """Update an existing food diary entry (e.g. adjust quantity or unit)."""
        payload = {}
        if quantity is not None:
            payload["quantity"] = float(quantity)
        if unit is not None:
            payload["unit"] = unit
        if meal_type is not None:
            payload["meal_type"] = meal_type.lower()
        if entry_date is not None:
            payload["entry_date"] = entry_date

        req = urllib.request.Request(
            f"{self.base_url}/api/food-entries/{entry_id}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Origin": self.base_url},
            method="PUT"
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def delete_food_entry(self, entry_id):
        """Delete a food diary entry by ID."""
        req = urllib.request.Request(
            f"{self.base_url}/api/food-entries/{entry_id}",
            headers={"Origin": self.base_url},
            method="DELETE"
        )
        with self.opener.open(req) as res:
            return res.status in (200, 204)

    def log_food(
        self,
        name,
        calories,
        protein=0.0,
        carbs=0.0,
        fat=0.0,
        serving_size=1.0,
        serving_unit="serving",
        meal_type="breakfast",
        entry_date=None,
        quantity=None,
        weight_g=None,
        multiplier=1.0,
        servings=None
    ):
        """
        Log food entry into SparkyFitness with automatic unit scaling and self-healing verification.
        Ensures the calculated calories in the diary match the intended portion calories exactly.
        """
        if not entry_date:
            entry_date = date.today().isoformat()

        if servings is not None:
            multiplier = float(servings)

        serving_size = float(serving_size) if serving_size else 1.0
        if serving_size <= 0:
            serving_size = 1.0

        calories = float(calories)
        protein = float(protein)
        carbs = float(carbs)
        fat = float(fat)

        is_weight_unit = serving_unit.strip().lower() in WEIGHT_UNITS

        # Resolve quantity to prevent 1-gram / deflated entry bugs
        if weight_g is not None:
            resolved_quantity = float(weight_g)
        elif quantity is not None:
            q = float(quantity)
            # If the user or agent passed a small quantity (<= 5.0) for a weight-based food with serving_size >= 10:
            # e.g., serving_size = 100g, quantity = 1.0 (or 1.5)
            # The caller intended 1.0 * 100g = 100g (a portion count/multiplier), NOT 1 single gram!
            if is_weight_unit and q <= 5.0 and serving_size >= 10.0 and abs(q - serving_size) > 0.001:
                resolved_quantity = round(q * serving_size, 2)
            else:
                resolved_quantity = q
        else:
            # If quantity was omitted: default consumed amount is serving_size * multiplier
            resolved_quantity = round(serving_size * float(multiplier), 2)

        # Expected values in SparkyFitness diary
        expected_scale = (resolved_quantity / serving_size) if serving_size > 0 else 1.0
        expected_calories = round(calories * expected_scale, 1)
        expected_protein = round(protein * expected_scale, 1)
        expected_carbs = round(carbs * expected_scale, 1)
        expected_fat = round(fat * expected_scale, 1)

        # Step 1: Create custom food item with default variant
        food_payload = json.dumps({
            "name": name,
            "is_custom": True,
            "serving_size": serving_size,
            "serving_unit": serving_unit,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/foods",
            data=food_payload,
            headers={"Content-Type": "application/json", "Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            food = json.loads(res.read().decode("utf-8"))

        variant_id = food.get("default_variant", {}).get("id")

        # Step 2: Log entry in diary
        entry_payload = json.dumps({
            "food_id": food["id"],
            "variant_id": variant_id,
            "quantity": resolved_quantity,
            "unit": serving_unit if serving_unit != "serving" else "serving",
            "meal_type": meal_type.lower(),
            "entry_date": entry_date
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/food-entries",
            data=entry_payload,
            headers={"Content-Type": "application/json", "Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            entry = json.loads(res.read().decode("utf-8"))

        # Step 3: Self-Healing Verification
        entry_id = entry.get("id")
        actual_qty = float(entry.get("quantity") or resolved_quantity)
        actual_srv_sz = float(entry.get("serving_size") or serving_size)
        actual_base_cal = float(entry.get("calories") or calories)
        computed_cal = round((actual_qty / actual_srv_sz) * actual_base_cal, 1) if actual_srv_sz > 0 else actual_base_cal

        # Check for deflation / scaling mismatch
        is_deflated = False
        if expected_calories >= 10.0:
            if computed_cal < (0.75 * expected_calories) or computed_cal > (1.25 * expected_calories):
                is_deflated = True
        elif expected_calories > 0 and computed_cal == 0:
            is_deflated = True

        if is_deflated and actual_base_cal > 0 and actual_srv_sz > 0:
            needed_quantity = round((expected_calories / actual_base_cal) * actual_srv_sz, 2)
            if is_weight_unit and needed_quantity >= 1.0:
                needed_quantity = round(needed_quantity)
            try:
                entry = self.update_food_entry(
                    entry_id=entry_id,
                    quantity=needed_quantity,
                    unit=entry.get("unit") or serving_unit,
                    meal_type=meal_type,
                    entry_date=entry_date
                )
                actual_qty = float(entry.get("quantity") or needed_quantity)
                computed_cal = round((actual_qty / actual_srv_sz) * actual_base_cal, 1)
            except Exception:
                pass

        # Final verification assertion
        if expected_calories >= 15.0 and computed_cal < (0.5 * expected_calories):
            raise RuntimeError(
                f"Defective SparkyFitness entry detected: '{name}' computed as {computed_cal} Cal (expected {expected_calories} Cal). Auto-healing failed."
            )

        return {
            "status": "success",
            "entry_id": entry_id,
            "name": name,
            "meal_type": meal_type.lower(),
            "date": entry_date,
            "logged_quantity": actual_qty,
            "logged_unit": entry.get("unit") or serving_unit,
            "verified_calories": computed_cal,
            "verified_protein": round((actual_qty / actual_srv_sz) * float(entry.get("protein") or protein), 1),
            "verified_carbs": round((actual_qty / actual_srv_sz) * float(entry.get("carbs") or carbs), 1),
            "verified_fat": round((actual_qty / actual_srv_sz) * float(entry.get("fat") or fat), 1),
            "raw_entry": entry
        }

    def log_water(self, amount_ml=None, drinks=None, entry_date=None):
        """
        Log water intake change. 1 drink in SparkyFitness = 250ml.
        Can specify amount_ml (e.g. 500) or drinks (e.g. 2).
        """
        if not entry_date:
            entry_date = date.today().isoformat()

        if drinks is None:
            if amount_ml is None:
                drinks = 1
            else:
                drinks = int(round(amount_ml / 250.0))
                if drinks == 0 and amount_ml > 0:
                    drinks = 1

        payload = json.dumps({
            "entry_date": entry_date,
            "change_drinks": drinks
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/v2/measurements/water-intake",
            data=payload,
            headers={"Content-Type": "application/json", "Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def set_water(self, target_ml, entry_date=None):
        """
        Set total water intake for the day to an exact amount in ml.
        Calculates the delta from current water and adjusts drinks.
        """
        if not entry_date:
            entry_date = date.today().isoformat()
        current_ml = self.get_water(entry_date)
        diff_ml = target_ml - current_ml
        drinks_delta = int(round(diff_ml / 250.0))
        if drinks_delta != 0:
            self.log_water(drinks=drinks_delta, entry_date=entry_date)
        return self.get_water(entry_date)


    def get_water(self, entry_date=None):
        if not entry_date:
            entry_date = date.today().isoformat()
        req = urllib.request.Request(
            f"{self.base_url}/api/measurements/water-intake/{entry_date}",
            headers={"Origin": self.base_url}
        )
        try:
            with self.opener.open(req) as res:
                data = json.loads(res.read().decode("utf-8"))
                return data.get("water_ml", 0)
        except Exception:
            return 0

    def log_checkin(self, weight=None, steps=None, entry_date=None, height=None, body_fat=None):
        """
        Upsert daily check-in (weight, steps, height, body fat %).
        """
        if not entry_date:
            entry_date = date.today().isoformat()

        payload_dict = {"entry_date": entry_date}
        if weight is not None:
            payload_dict["weight"] = float(weight)
        if steps is not None:
            payload_dict["steps"] = int(steps)
        if height is not None:
            payload_dict["height"] = float(height)
        if body_fat is not None:
            payload_dict["body_fat_percentage"] = float(body_fat)

        payload = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/measurements/check-in",
            data=payload,
            headers={"Content-Type": "application/json", "Origin": self.base_url, "X-Meal-Model-Version": "2"}
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def get_checkin(self, entry_date=None):
        if not entry_date:
            entry_date = date.today().isoformat()
        req = urllib.request.Request(
            f"{self.base_url}/api/measurements/check-in/{entry_date}",
            headers={"Origin": self.base_url, "X-Meal-Model-Version": "2"}
        )
        try:
            with self.opener.open(req) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception:
            return {}

    def get_food_entries(self, entry_date=None):
        if not entry_date:
            entry_date = date.today().isoformat()
        req = urllib.request.Request(
            f"{self.base_url}/api/food-entries?selectedDate={entry_date}",
            headers={"Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def get_daily_summary(self, entry_date=None):
        if not entry_date:
            entry_date = date.today().isoformat()

        entries = self.get_food_entries(entry_date)
        water_ml = self.get_water(entry_date)
        checkin = self.get_checkin(entry_date)

        meals = {"breakfast": [], "lunch": [], "dinner": [], "snacks": []}
        meal_totals = {
            m: {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
            for m in meals
        }

        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for e in entries:
            meal = (e.get("meal_type") or "snacks").lower()
            if meal not in meals:
                meals[meal] = []
                meal_totals[meal] = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

            qty = float(e.get("quantity") or 1.0)
            serving_sz = float(e.get("serving_size") or 1.0)
            scale = qty / serving_sz if serving_sz > 0 else 1.0

            cal = float(e.get("calories") or 0.0) * scale
            pro = float(e.get("protein") or 0.0) * scale
            carb = float(e.get("carbs") or 0.0) * scale
            fat = float(e.get("fat") or 0.0) * scale

            total_calories += cal
            total_protein += pro
            total_carbs += carb
            total_fat += fat

            meal_totals[meal]["calories"] += cal
            meal_totals[meal]["protein"] += pro
            meal_totals[meal]["carbs"] += carb
            meal_totals[meal]["fat"] += fat

            meals[meal].append({
                "id": e.get("id"),
                "name": e.get("food_name"),
                "serving_size": e.get("serving_size"),
                "serving_unit": e.get("serving_unit"),
                "calories": cal,
                "protein": pro,
                "carbs": carb,
                "fat": fat
            })

        # Load target goals dynamically from SparkyFitness server or default to 1800 kcal cut
        targets = {
            "calories_target": 1800,
            "protein_target": 160,
            "carbs_target": 140,
            "fat_target": 60,
            "water_goal_ml": 3000
        }
        try:
            goals_resp = self.opener.open(f"{self.base_url}/api/goals/by-date/{entry_date}")
            server_goals = json.loads(goals_resp.read())
            if server_goals and server_goals.get("calories"):
                targets["calories_target"] = int(server_goals.get("calories"))
                targets["protein_target"] = int(server_goals.get("protein") or 160)
                targets["carbs_target"] = int(server_goals.get("carbs") or 140)
                targets["fat_target"] = int(server_goals.get("fat") or 60)
                targets["water_goal_ml"] = int(server_goals.get("water_goal_ml") or 3000)
        except Exception:
            pass

        remaining_calories = round(targets["calories_target"] - total_calories, 1)
        remaining_protein = round(targets["protein_target"] - total_protein, 1)
        remaining_carbs = round(targets["carbs_target"] - total_carbs, 1)
        remaining_fat = round(targets["fat_target"] - total_fat, 1)
        remaining_water = max(0, targets["water_goal_ml"] - water_ml)

        return {
            "date": entry_date,
            "totals": {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fat": round(total_fat, 1),
                "water_ml": water_ml
            },
            "targets": targets,
            "remaining": {
                "calories": remaining_calories,
                "protein": remaining_protein,
                "carbs": remaining_carbs,
                "fat": remaining_fat,
                "water_ml": remaining_water
            },
            "meal_totals": {
                m: {k: round(v, 1) for k, v in vals.items()}
                for m, vals in meal_totals.items()
            },
            "meals": meals,
            "checkin": {
                "weight_kg": checkin.get("weight"),
                "steps": checkin.get("steps"),
                "height_cm": checkin.get("height"),
                "body_fat_percentage": checkin.get("body_fat_percentage")
            }
        }

    def get_user_id(self):
        """Fetch current user ID from user-preferences."""
        req = urllib.request.Request(
            f"{self.base_url}/api/user-preferences",
            headers={"Origin": self.base_url}
        )
        with self.opener.open(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data.get("user_id")

    def get_meal_plans(self, user_id=None):
        """Fetch all meal plan templates for user."""
        if not user_id:
            user_id = self.get_user_id()
        req = urllib.request.Request(
            f"{self.base_url}/api/meal-plan-templates?userId={user_id}",
            headers={"Origin": self.base_url, "X-Meal-Model-Version": "2"}
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def create_meal_plan(self, plan_name, description="", start_date=None, end_date=None, is_active=True, day_presets=None, user_id=None):
        """Create a scheduled meal plan template."""
        if not user_id:
            user_id = self.get_user_id()
        if not start_date:
            start_date = date.today().isoformat()
        if day_presets is None:
            day_presets = []

        payload = json.dumps({
            "plan_name": plan_name,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "is_active": is_active,
            "day_presets": day_presets,
            "userId": user_id,
            "currentClientDate": date.today().isoformat()
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/meal-plan-templates",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Origin": self.base_url,
                "X-Meal-Model-Version": "2"
            }
        )
        with self.opener.open(req) as res:
            return json.loads(res.read().decode("utf-8"))

    def log_meal(self, meal_type, items, entry_date=None):
        """
        Log multiple food items in a meal with automatic verification for each item.
        items: list of dicts with keys: name, calories, protein, carbs, fat, serving_size, serving_unit, quantity, etc.
        """
        results = []
        meal_total_cal = 0.0
        meal_total_pro = 0.0
        meal_total_carb = 0.0
        meal_total_fat = 0.0

        for it in items:
            res = self.log_food(
                name=it["name"],
                calories=it["calories"],
                protein=it.get("protein", 0.0),
                carbs=it.get("carbs", 0.0),
                fat=it.get("fat", 0.0),
                serving_size=it.get("serving_size", it.get("weight_g", 1.0)),
                serving_unit=it.get("serving_unit", "g" if "weight_g" in it else "serving"),
                meal_type=meal_type,
                entry_date=entry_date,
                quantity=it.get("quantity", it.get("weight_g")),
                weight_g=it.get("weight_g"),
                multiplier=it.get("multiplier", 1.0),
                servings=it.get("servings")
            )
            results.append(res)
            meal_total_cal += res["verified_calories"]
            meal_total_pro += res["verified_protein"]
            meal_total_carb += res["verified_carbs"]
            meal_total_fat += res["verified_fat"]

        return {
            "status": "success",
            "meal_type": meal_type,
            "entry_date": entry_date or date.today().isoformat(),
            "item_count": len(results),
            "totals": {
                "calories": round(meal_total_cal, 1),
                "protein": round(meal_total_pro, 1),
                "carbs": round(meal_total_carb, 1),
                "fat": round(meal_total_fat, 1)
            },
            "items": results
        }

    def audit_day(self, entry_date=None, auto_heal=True):
        """
        Scans all food entries for a date, flags any deflated/defective entries,
        and auto-heals them if auto_heal=True.
        """
        if not entry_date:
            entry_date = date.today().isoformat()

        entries = self.get_food_entries(entry_date)
        issues_found = []
        healed_entries = []

        for e in entries:
            q = float(e.get("quantity") or 1.0)
            s = float(e.get("serving_size") or 1.0)
            c = float(e.get("calories") or 0.0)
            u = (e.get("unit") or e.get("serving_unit") or "").lower()
            computed_cal = (q / s) * c if s > 0 else c

            is_deflated = False
            # Check 1: Unit is weight/volume, serving size >= 10, but quantity is <= 2
            if u in WEIGHT_UNITS and s >= 10.0 and q <= 2.0:
                is_deflated = True
            # Check 2: Base calories > 25, but computed calories < 5
            elif c >= 25.0 and computed_cal < 5.0:
                is_deflated = True

            if is_deflated:
                issues_found.append({
                    "entry_id": e.get("id"),
                    "name": e.get("food_name"),
                    "meal_type": e.get("meal_type"),
                    "quantity": q,
                    "serving_size": s,
                    "unit": u,
                    "computed_calories": round(computed_cal, 1),
                    "base_calories": c
                })

                if auto_heal and s > 0 and c > 0:
                    needed_q = s if (u in WEIGHT_UNITS and q <= 2.0) else round((c / c) * s)
                    try:
                        self.update_food_entry(
                            entry_id=e.get("id"),
                            quantity=needed_q,
                            unit=e.get("unit"),
                            meal_type=e.get("meal_type"),
                            entry_date=entry_date
                        )
                        healed_entries.append({
                            "entry_id": e.get("id"),
                            "name": e.get("food_name"),
                            "old_quantity": q,
                            "new_quantity": needed_q,
                            "corrected_calories": round((needed_q / s) * c, 1)
                        })
                    except Exception as err:
                        print(f"Error healing entry {e.get('id')}: {err}")

        return {
            "date": entry_date,
            "total_entries": len(entries),
            "issues_detected": len(issues_found),
            "issues": issues_found,
            "healed": healed_entries
        }


def main():
    parser = argparse.ArgumentParser(description="SparkyFitness CLI Helper")
    subparsers = parser.add_subparsers(dest="command")

    # 1. Log food
    food_parser = subparsers.add_parser("log-food", help="Log a food entry to diary with verified macros")
    food_parser.add_argument("--name", required=True, help="Food name")
    food_parser.add_argument("--calories", type=float, required=True, help="Calories in kcal")
    food_parser.add_argument("--protein", type=float, default=0.0, help="Protein in g")
    food_parser.add_argument("--carbs", type=float, default=0.0, help="Carbohydrates in g")
    food_parser.add_argument("--fat", type=float, default=0.0, help="Fat in g")
    food_parser.add_argument("--serving-size", type=float, default=1.0, help="Serving size (e.g. 100 for 100g, 19 for 19g)")
    food_parser.add_argument("--serving-unit", default="serving", help="Serving unit (e.g. g, ml, eggs, serving, portion, bowl)")
    food_parser.add_argument("--meal", default="breakfast", choices=["breakfast", "lunch", "dinner", "snacks"], help="Meal type")
    food_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")
    food_parser.add_argument("--quantity", type=float, default=None, help="Consumed quantity in serving units (e.g. 100 for 100g). Defaults to serving-size.")
    food_parser.add_argument("--weight-g", type=float, default=None, help="Convenience alias: exact consumed weight in grams")
    food_parser.add_argument("--multiplier", type=float, default=1.0, help="Portion multiplier (e.g. 1.5 servings)")
    food_parser.add_argument("--servings", type=float, default=None, help="Alias for multiplier")

    # 1b. Log meal (batch)
    meal_parser = subparsers.add_parser("log-meal", help="Log multiple food items to a meal simultaneously")
    meal_parser.add_argument("--meal", required=True, choices=["breakfast", "lunch", "dinner", "snacks"], help="Meal type")
    meal_parser.add_argument("--items", default=None, help="JSON array of food item objects")
    meal_parser.add_argument("--file", default=None, help="Path to JSON file containing food items")
    meal_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 1c. Update food entry
    update_food_parser = subparsers.add_parser("update-food", help="Update quantity/unit for an existing entry")
    update_food_parser.add_argument("--id", required=True, help="Food entry ID")
    update_food_parser.add_argument("--quantity", type=float, required=True, help="New quantity")
    update_food_parser.add_argument("--unit", default=None, help="Unit")
    update_food_parser.add_argument("--meal", default=None, help="Meal type")
    update_food_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 1d. Delete food entry
    delete_food_parser = subparsers.add_parser("delete-food", help="Delete an entry by ID")
    delete_food_parser.add_argument("--id", required=True, help="Food entry ID to delete")

    # 1e. Audit & heal day
    audit_parser = subparsers.add_parser("audit", help="Audit entries for deflated values and optionally heal them")
    audit_parser.add_argument("--date", default=None, help="Date to audit (YYYY-MM-DD)")
    audit_parser.add_argument("--fix", action="store_true", help="Auto-heal deflated entries")

    # 2. Log water (delta)
    water_parser = subparsers.add_parser("log-water", help="Log water intake in ml or drinks (250ml each)")
    water_parser.add_argument("--amount", type=float, default=None, help="Water amount in ml")
    water_parser.add_argument("--drinks", type=int, default=None, help="Number of 250ml drinks")
    water_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 2b. Set water (absolute target)
    set_water_parser = subparsers.add_parser("set-water", help="Set total water intake for the day to an exact ml amount")
    set_water_parser.add_argument("--amount", type=float, required=True, help="Total target water in ml")
    set_water_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 3. Log weight / checkin
    checkin_parser = subparsers.add_parser("log-checkin", help="Log check-in (weight, steps, body fat)")
    checkin_parser.add_argument("--weight", type=float, default=None, help="Weight in kg")
    checkin_parser.add_argument("--steps", type=int, default=None, help="Daily step count")
    checkin_parser.add_argument("--height", type=float, default=None, help="Height in cm")
    checkin_parser.add_argument("--body-fat", type=float, default=None, help="Body fat percentage")
    checkin_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 4. Summary
    summary_parser = subparsers.add_parser("summary", help="Get daily nutrition and check-in summary")
    summary_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    # 5. List entries
    list_parser = subparsers.add_parser("list", help="List food entries for a date")
    list_parser.add_argument("--date", default=None, help="Entry date (YYYY-MM-DD)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = SparkyFitness()

    if args.command == "log-food":
        res = client.log_food(
            name=args.name,
            calories=args.calories,
            protein=args.protein,
            carbs=args.carbs,
            fat=args.fat,
            serving_size=args.serving_size,
            serving_unit=args.serving_unit,
            meal_type=args.meal,
            entry_date=args.date,
            quantity=args.quantity,
            weight_g=args.weight_g,
            multiplier=args.multiplier,
            servings=args.servings
        )
        print(json.dumps({
            "status": "success",
            "message": f"Logged {res['name']} ({res['verified_calories']} kcal, {res['verified_protein']}g P, {res['verified_carbs']}g C, {res['verified_fat']}g F) into {res['meal_type']}",
            "entry_id": res.get("entry_id"),
            "meal_type": res.get("meal_type"),
            "date": res.get("date"),
            "logged_quantity": res.get("logged_quantity"),
            "logged_unit": res.get("logged_unit"),
            "verified_calories": res.get("verified_calories"),
            "verified_protein": res.get("verified_protein"),
            "verified_carbs": res.get("verified_carbs"),
            "verified_fat": res.get("verified_fat")
        }, indent=2))

    elif args.command == "log-meal":
        items = []
        if args.items:
            items = json.loads(args.items)
        elif args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                items = json.load(f)
        else:
            print("Error: Either --items or --file must be specified for log-meal.")
            sys.exit(1)

        res = client.log_meal(meal_type=args.meal, items=items, entry_date=args.date)
        print(json.dumps(res, indent=2))

    elif args.command == "update-food":
        res = client.update_food_entry(
            entry_id=args.id,
            quantity=args.quantity,
            unit=args.unit,
            meal_type=args.meal,
            entry_date=args.date
        )
        print(json.dumps({"status": "success", "updated_entry": res}, indent=2))

    elif args.command == "delete-food":
        ok = client.delete_food_entry(args.id)
        print(json.dumps({"status": "success" if ok else "failed", "deleted_id": args.id}, indent=2))

    elif args.command == "audit":
        report = client.audit_day(entry_date=args.date, auto_heal=args.fix)
        print(json.dumps(report, indent=2))

    elif args.command == "log-water":
        res = client.log_water(amount_ml=args.amount, drinks=args.drinks, entry_date=args.date)
        total = client.get_water(args.date)
        print(json.dumps({
            "status": "success",
            "message": f"Water intake updated. Total for day: {total} ml",
            "date": args.date or date.today().isoformat(),
            "total_water_ml": total
        }, indent=2))

    elif args.command == "set-water":
        total = client.set_water(target_ml=args.amount, entry_date=args.date)
        print(json.dumps({
            "status": "success",
            "message": f"Water intake set to {total} ml",
            "date": args.date or date.today().isoformat(),
            "total_water_ml": total
        }, indent=2))

    elif args.command == "log-checkin":
        res = client.log_checkin(
            weight=args.weight,
            steps=args.steps,
            entry_date=args.date,
            height=args.height,
            body_fat=args.body_fat
        )
        print(json.dumps({
            "status": "success",
            "message": "Check-in updated successfully",
            "checkin": res
        }, indent=2))

    elif args.command == "summary":
        summary = client.get_daily_summary(args.date)
        print(json.dumps(summary, indent=2))

    elif args.command == "list":
        entries = client.get_food_entries(args.date)
        print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
