---
name: sparky-fitness-ops
description: Operational controller for SparkyFitness deployment, workout/food logging, container management, and AI provider maintenance. Eliminates repetitive script generation.
---

# SparkyFitness Operations Skill

## 1. Quick Reference & Core Constants

- **Target App:** `https://fitness.masrisystems.com` (Oracle Cloud VPS: `158.101.162.138`)
- **SSH Target:** `opc@158.101.162.138` (Key: `C:\Users\super\.ssh\ssh-key-2026-09-13.key`)
- **Docker Container:** `sparkyfitness-server-tdgslqbqhgxxznsokm7gfpun`
- **CLI Tool:** `python "C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py"`
- **Active User:** Mohamad Masri (`b45f07a7-2def-49d6-840d-ad5bcaab09f6`)
- **Active AI Provider:** Omniroute (`aa83074f-add4-44f5-bad8-7bf59ffa616b`), model `openai/gpt-4o`
- **Omniroute Full URL:** `https://router.masrisystems.com/v1/chat/completions`

---

## 2. Inviolable Operational Rules

1. **Never SSH as `ubuntu`:** Always use `opc`. All remote Docker commands require `sudo`.
2. **Zero-Defect Calorie Formula:**
   - Calculation: `(quantity / serving_size) * base_calories`
   - **Rule:** Always pass the exact weight in grams as `quantity`. Never send `quantity=1` for gram-based items.
3. **Custom AI URL Rule:**
   - SparkyFitness `custom` service type posts to `custom_url` **verbatim** (it does not append `/chat/completions`).
   - If adjusting AI settings, ensure the path ends with `/chat/completions` to prevent HTTP 405.
4. **Dual Service ID Sync:**
   - Both `active_ai_service_id` and `active_vision_ai_service_id` must point to the identical working vision-capable provider ID.

---

## 3. Standard Execution Shortcuts (Run directly, do NOT write custom code)

### Server Diagnostics & Lifecycle
```bash
# Check recent AI errors (filters out health pings)
ssh -i C:\Users\super\.ssh\ssh-key-2026-09-13.key opc@158.101.162.138 "sudo docker logs sparkyfitness-server-tdgslqbqhgxxznsokm7gfpun --since 20m 2>&1 | grep -v '/api/health'"

# Restart application container
ssh -i C:\Users\super\.ssh\ssh-key-2026-09-13.key opc@158.101.162.138 "sudo docker restart sparkyfitness-server-tdgslqbqhgxxznsokm7gfpun"
```

### Logging Food & Workouts

```bash
# Daily nutrition summary
python "C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py" summary

# Audit and fix deflated calorie entries
python "C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py" audit --fix

# Interactive or parameterized food log
python "C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py" log-food
```

---

## 4. API Direct Reference (When bypassing UI)

* **List Providers:** `GET /api/chat/ai-service-settings`
* **Set Active Models:** `PUT /api/user-preferences`
```json
{
  "active_ai_service_id": "aa83074f-add4-44f5-bad8-7bf59ffa616b",
  "active_vision_ai_service_id": "aa83074f-add4-44f5-bad8-7bf59ffa616b"
}
```

* **Log Preset Workout:** `POST /api/exercise-preset-entries`
```json
{
  "workout_preset_id": "<preset_id>",
  "entry_date": "YYYY-MM-DD"
}
```
