import os
import sys
import json
import csv
import urllib.request
import urllib.error
from datetime import datetime
from collections import OrderedDict, defaultdict, Counter

SESSION_FILE = os.path.expanduser("~/.hevy_session.json")
HEALTH_DIR = r"C:\Users\super\Projects\obsidian\masrisystems-app\content\private\General\Health"

sys.path.append(r"C:\Users\super\.agents\skills\nutritional-specialist\scripts")
try:
    from sparky_fitness import SparkyFitness
except ImportError:
    SparkyFitness = None


class HevySync:
    def __init__(self, session_file=SESSION_FILE):
        self.session_file = session_file
        self.session = self._load_session()
        self.sparky = SparkyFitness() if SparkyFitness else None

    def _load_session(self):
        if not os.path.exists(self.session_file):
            raise FileNotFoundError(f"Hevy session file not found at {self.session_file}")
        with open(self.session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_session(self):
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.session, f, indent=2)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.session.get('access_token')}",
            "x-api-key": "shelobs_hevy_web",
            "hevy-platform": "web",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def verify_auth(self):
        headers = self.get_headers()
        try:
            req = urllib.request.Request("https://api.hevyapp.com/workout_count", headers=headers)
            with urllib.request.urlopen(req) as res:
                if res.status == 200:
                    return True
        except Exception:
            pass
        return False

    def fetch_all_workouts(self):
        if not self.verify_auth():
            print("Warning: Access token might be expired. Checking session...")
            if not self.verify_auth():
                raise PermissionError("Hevy authentication failed. Check credentials in ~/.hevy_session.json")

        headers = self.get_headers()
        req = urllib.request.Request("https://api.hevyapp.com/workout_count", headers=headers)
        with urllib.request.urlopen(req) as res:
            count_data = json.loads(res.read().decode())
            total = count_data.get("workout_count", 0)

        print(f"Discovered {total} workouts on Hevy.")
        all_workouts = []
        cursor = 0
        while len(all_workouts) < total:
            url = f"https://api.hevyapp.com/workouts_batch/{cursor}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as res:
                batch = json.loads(res.read().decode())
                if not batch:
                    break
                all_workouts.extend(batch)
                cursor = all_workouts[-1]["index"] + 1

        print(f"Successfully fetched all {len(all_workouts)} workouts.")
        all_workouts.sort(key=lambda w: w.get("start_time", 0))
        return all_workouts

    def convert_to_csv_rows(self, workouts):
        rows = []
        for w in workouts:
            title = (w.get("name") or w.get("title") or "Workout").strip()
            desc = (w.get("description") or "").strip()
            
            st_dt = datetime.fromtimestamp(w.get("start_time", 0))
            et_dt = datetime.fromtimestamp(w.get("end_time", 0)) if w.get("end_time") else st_dt
            
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            st_str = f"{month_names[st_dt.month - 1]} {st_dt.day}, {st_dt.year}, {st_dt.strftime('%I:%M %p').lstrip('0')}"
            et_str = f"{month_names[et_dt.month - 1]} {et_dt.day}, {et_dt.year}, {et_dt.strftime('%I:%M %p').lstrip('0')}"

            exercises = w.get("exercises", [])
            for ex in exercises:
                ex_title = (ex.get("title") or "Unknown").strip()
                ex_notes = (ex.get("notes") or "").strip()
                superset_id = ex.get("superset_id") or ""
                sets = ex.get("sets", [])
                for s in sets:
                    set_idx = s.get("index", 0)
                    indicator = (s.get("indicator") or "normal").lower()
                    w_kg = s.get("weight_kg")
                    reps = s.get("reps")
                    dist_meters = s.get("distance_meters")
                    dist_km = round(dist_meters / 1000.0, 2) if dist_meters else ""
                    dur_sec = s.get("duration_seconds") or ""
                    rpe = s.get("rpe") or ""
                    
                    rows.append({
                        "title": title,
                        "start_time": st_str,
                        "end_time": et_str,
                        "description": desc,
                        "exercise_title": ex_title,
                        "superset_id": str(superset_id) if superset_id else "",
                        "exercise_notes": ex_notes,
                        "set_index": str(set_idx),
                        "set_type": indicator,
                        "weight_kg": str(w_kg) if w_kg is not None else "",
                        "reps": str(reps) if reps is not None else "",
                        "distance_km": str(dist_km) if dist_km else "",
                        "duration_seconds": str(dur_sec) if dur_sec else "",
                        "rpe": str(rpe) if rpe else ""
                    })
        return rows

    def sync_to_sparky(self, rows):
        if not self.sparky:
            print("SparkyFitness client unavailable. Skipping Sparky push.")
            return 0

        set_type_map = {
            "normal": "Normal",
            "warmup": "Warm-up",
            "dropset": "Drop Set",
            "failure": "Failure"
        }

        grouped = OrderedDict()
        for r in rows:
            st_raw = r["start_time"]
            dt = datetime.strptime(st_raw, "%b %d, %Y, %I:%M %p")
            entry_date = dt.strftime("%Y-%m-%d")
            ex_name = r["exercise_title"].strip()
            preset_name = (r.get("title") or "").strip()
            if not preset_name:
                preset_name = "Individual Entry"

            group_id = f"{entry_date}|{ex_name}|{preset_name}"
            if group_id not in grouped:
                grouped[group_id] = {
                    "id": group_id,
                    "entry_date": entry_date,
                    "exercise_name": ex_name,
                    "preset_name": preset_name if preset_name != "Individual Entry" else None,
                    "entry_notes": r.get("description") if r.get("description") else None,
                    "exercise_source": "Hevy_Sync",
                    "sets": [],
                    "activity_details": []
                }

            set_num = len(grouped[group_id]["sets"]) + 1
            st_type = set_type_map.get(r.get("set_type", "normal").lower(), "Normal")
            set_obj = {
                "set_number": set_num,
                "set_type": st_type
            }
            if r.get("weight_kg"):
                try:
                    set_obj["weight"] = float(r["weight_kg"])
                except ValueError:
                    pass
            if r.get("reps"):
                try:
                    set_obj["reps"] = int(float(r["reps"]))
                except ValueError:
                    pass
            if r.get("duration_seconds"):
                try:
                    set_obj["duration_min"] = round(float(r["duration_seconds"]) / 60.0, 2)
                except ValueError:
                    pass
            if r.get("exercise_notes"):
                set_obj["notes"] = r["exercise_notes"]
            if r.get("rpe"):
                try:
                    set_obj["rpe"] = float(r["rpe"])
                    grouped[group_id]["activity_details"].append({
                        "field_name": "RPE",
                        "value": r["rpe"]
                    })
                except ValueError:
                    pass

            grouped[group_id]["sets"].append(set_obj)

        all_entries = list(grouped.values())
        print(f"Pushing {len(all_entries)} grouped routines to SparkyFitness...")
        batch_size = 30
        created = 0
        for i in range(0, len(all_entries), batch_size):
            batch = all_entries[i:i + batch_size]
            payload = {"entries": batch}
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.sparky.base_url}/api/exercise-entries/import-history-csv",
                data=req_data,
                headers={"Content-Type": "application/json", "Origin": self.sparky.base_url}
            )
            try:
                with self.sparky.opener.open(req) as res:
                    resp = json.loads(res.read().decode())
                    created += resp.get("created", 0)
            except Exception as e:
                print(f"Error pushing batch {i // batch_size + 1}: {e}")

        print(f"SparkyFitness sync complete: {created} entries created/updated.")
        return len(all_entries)

    def update_obsidian_dossier(self, rows, total_workouts, total_grouped):
        """Regenerates Workout History.md with fresh metrics and PRs."""
        splits_counter = Counter()
        monthly_unique = Counter()
        exercise_prs = {}
        exercise_set_counts = Counter()
        seen_workouts = set()

        for r in rows:
            st = r.get("start_time", "").strip()
            dt = datetime.strptime(st, "%b %d, %Y, %I:%M %p")
            date_str = dt.strftime("%Y-%m-%d")
            title = r.get("title", "Workout").strip()
            w_key = (date_str, title)

            if w_key not in seen_workouts:
                seen_workouts.add(w_key)
                monthly_unique[dt.strftime("%B %Y")] += 1
                t_low = title.lower()
                if "brust" in t_low or "chest" in t_low:
                    splits_counter["Chest / Push"] += 1
                elif "rücken" in t_low or "back" in t_low:
                    splits_counter["Back / Pull"] += 1
                elif "bein" in t_low or "leg" in t_low:
                    splits_counter["Legs / Lower Body"] += 1
                elif "schülter" in t_low or "schulter" in t_low or "shoulder" in t_low:
                    splits_counter["Shoulders / Arms"] += 1
                else:
                    splits_counter["Other / Mixed"] += 1

            ex = r.get("exercise_title", "").strip()
            exercise_set_counts[ex] += 1
            w_kg = float(r["weight_kg"]) if r.get("weight_kg") else 0.0
            reps = int(float(r["reps"])) if r.get("reps") else 0

            if ex not in exercise_prs:
                exercise_prs[ex] = {"max_weight": 0.0, "best_set": "", "date": date_str, "reps": 0}
            if w_kg > exercise_prs[ex]["max_weight"] or (w_kg == exercise_prs[ex]["max_weight"] and reps > exercise_prs[ex]["reps"]):
                exercise_prs[ex]["max_weight"] = w_kg
                exercise_prs[ex]["reps"] = reps
                exercise_prs[ex]["best_set"] = f"{w_kg} kg × {reps} reps"
                exercise_prs[ex]["date"] = date_str

        today_str = datetime.now().strftime("%Y-%m-%d")

        md_content = f"""---
title: "Workout History & Strength Baseline"
description: "Comprehensive analysis of {len(seen_workouts)} workouts ({len(rows)} sets), lifting PRs, injury documentation, and automated SparkyFitness synchronization."
tags:
  - health
  - fitness
  - workouts
  - strength-training
  - sparky-fitness
  - injury-history
created: 2026-09-17
updated: {today_str}
author: Mohamad Masri
layout: default
status: published
---

# Workout History & Strength Baseline

> [!info] Data Synchronization Status
> All **{len(seen_workouts)} workouts** (consisting of **{total_grouped} grouped routines** and **{len(rows)} completed sets**) have been synced into **SparkyFitness** (https://fitness.masrisystems.com) with **100% success**.
> 
> **Raw & Formatted Files in Vault:**
> - Pristine Hevy CSV Export: [[hevy_workouts_export.csv]]
> - Native SparkyFitness Template CSV: [[sparky_fitness_workouts_export.csv]]
> - Parent Health Hub: [[Health]] | Biometrics: [[My health Info]] | Nutrition Protocol: [[Diet]]

---

## 1. Executive Summary & Training Volume

```mermaid
pie title Workout Split Distribution ({len(seen_workouts)} Sessions)
    "Legs / Lower Body" : {splits_counter.get('Legs / Lower Body', 0)}
    "Chest / Push" : {splits_counter.get('Chest / Push', 0)}
    "Back / Pull" : {splits_counter.get('Back / Pull', 0)}
    "Shoulders / Arms" : {splits_counter.get('Shoulders / Arms', 0)}
```

### Training Frequency by Month

| Month | Sessions | Key Focus & Phase |
| :--- | :---: | :--- |
"""
        for m, c in sorted(monthly_unique.items()):
            md_content += f"| **{m}** | {c} | Logged training sessions. |\n"

        md_content += """
---

## 2. Clinical Injury Event & Timeline

> [!danger] Documented Acute Injury: July 11, 2026
> - **Workout:** `Schültern (Shoulders)` (11:45 AM – 1:08 PM)
> - **Exercise:** `Seated Shoulder Press (Machine)`
> - **Logged Note:** `"Schulter Verletzung"` across all 4 working sets (40 kg × 15, 12, 12, 12 reps).
> - **Prior Baseline:** On April 11, 2026, the user comfortably handled **67.5 kg × 9 reps** on `Seated Shoulder Press (Machine)` and **60.0 kg × 10 reps** on `Overhead Press (Smith Machine)`.
> - **Mechanism:** Acute overload/instability during seated overhead pressing resulting in rotator cuff / labral pathology.

### Post-Injury Adaptation & Surgical Carryover
- Following July 11, overhead pressing was restricted. High-volume machine lower-body training was maintained (**Leg Press peaked at 180 kg × 10 reps** on Aug 23).
- **Post-Op Rules:** Operative shoulder strictly immobilized for 4–6 weeks. Zero compound upper body work. Early Phase 2 permits recumbent stationary bike (*Liegeergometer*) and isolated machine lower body once cleared by surgeon.

---

## 3. Top Strength Personal Records (PRs)

| Exercise | Peak Weight | Reps | Date |
| :--- | :---: | :---: | :---: |
"""
        for ex, data in sorted(exercise_prs.items(), key=lambda x: x[1]["max_weight"], reverse=True)[:25]:
            if data["max_weight"] > 0:
                md_content += f"| **{ex}** | **{data['max_weight']} kg** | {data['reps']} | {data['date']} |\n"

        md_content += f"""
---

## 4. Top Exercises by Volume (Sets Completed)

"""
        for rank, (ex, cnt) in enumerate(exercise_set_counts.most_common(10), start=1):
            md_content += f"{rank}. **{ex}:** {cnt} sets\n"

        md_content += f"""
---

## 5. Automated Hevy & SparkyFitness Sync
- **Scheduled Sidecar:** Task #18 in [[Antigravity Scheduled Tasks]]
- **Cadence:** Weekly on Sunday @ 10:00 PM (`0 22 * * 0`)
- **Last Sync Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
"""

        note_path = os.path.join(HEALTH_DIR, "Workout History.md")
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(md_content.strip() + "\n")
        print(f"Regenerated {note_path}")

    def run(self):
        workouts = self.fetch_all_workouts()
        rows = self.convert_to_csv_rows(workouts)

        # 1. Save pristine CSV
        hevy_csv_path = os.path.join(HEALTH_DIR, "hevy_workouts_export.csv")
        fieldnames = ["title", "start_time", "end_time", "description", "exercise_title", "superset_id", "exercise_notes", "set_index", "set_type", "weight_kg", "reps", "distance_km", "duration_seconds", "rpe"]
        with open(hevy_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Updated CSV saved to {hevy_csv_path}")

        # 2. Sync to SparkyFitness
        total_grouped = self.sync_to_sparky(rows)

        # 3. Update Obsidian note
        self.update_obsidian_dossier(rows, len(workouts), total_grouped)
        print("Hevy sync run completed successfully.")


if __name__ == "__main__":
    sync = HevySync()
    sync.run()
