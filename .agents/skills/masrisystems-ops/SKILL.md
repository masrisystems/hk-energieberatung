---
name: masrisystems-ops
description: Operations, deployment, testing, content synchronization, and CLI workflows for the Masri Systems flagship platform (masrisystems-app).
---

# Masri Systems Platform Operations (`masrisystems-ops`)

Use this skill whenever running commands, performing database/content synchronization, running tests, optimizing assets, or deploying changes in `masrisystems-app`.

---

## 🧭 1. Local Development & Dev Servers

| Task | Command | Description |
|---|---|---|
| **All-in-one Dev** | `composer run dev` | Spawns Laravel backend, queue worker, and Vite HMR concurrently. |
| **Laravel Server** | `php artisan serve` | Runs local PHP backend server (`http://127.0.0.1:8000`). |
| **Vite Dev Server** | `npm run dev` | Runs Vite frontend with Hot Module Replacement on port `5173`. |
| **Queue Worker** | `php artisan queue:listen` | Processes asynchronous background jobs and email notifications. |

---

## 🧪 2. Code Quality, Testing & Formatting

Always verify your changes with these commands before committing or opening PRs:

```bash
# Run full Pest feature and unit test suites
php artisan test

# Format PHP code using Laravel Pint
vendor/bin/pint

# Run ESLint with auto-fix across TypeScript & Vue components
npm run lint

# Format frontend templates and styles with Prettier
npm run format

# Production bundle check (Vite build)
npm run build
```

---

## 🤖 3. Command Center & Autonomous Agent Fleet

- **Full-Screen Web UI**: Accessible at `/command-center`.
- **Filament Admin Panel**: Accessible at `/administration/command-center` under **Management**.
- **CLI Commands**:
  ```bash
  # Sync all Obsidian Kanban boards (To Do, Ranalp, Velyra, Maison Anthony)
  php artisan command-center:sync-boards --dry-run
  php artisan command-center:sync-boards

  # Dispatch an autonomous ECC Agent to work on a task
  php artisan command-center:agent-run {taskId?} --agent=code-explorer --summary="Finished exploration" --auto-approve
  ```

---

## 🔄 4. Safe Live Database Sync (Local ⇄ Uberspace Live DB)

- **Web GUI**: Accessible at `/administration/database-sync`.
- **Automatic SSH Tunneling**: Automatically opens `127.0.0.1:3307 -> 127.0.0.1:3306` to `masri@gienah.uberspace.de`.
- **CLI Commands**:
  ```bash
  # Inspect table row differences and latency
  php artisan db:sync-status

  # Safe Pull from Live (creates backup in storage/app/backups/ first)
  php artisan db:pull-live --dry-run
  php artisan db:pull-live

  # Safe Push to Live (requires PUSH-LIVE confirmation token)
  php artisan db:push-live --dry-run
  php artisan db:push-live
  ```

---

## 📚 5. Obsidian Content & Pricing Synchronization

Synchronizes dynamic Markdown articles, service definitions, and rate card packages:

```bash
# Sync Obsidian markdown vault notes into database
php artisan obsidian:sync

# Export database models into Markdown notes
php artisan obsidian:export

# Sync pricing tiers and package specifications
php artisan pricing:sync

# Translate Markdown content notes across languages via AI
php artisan obsidian:translate Services --locales=de
```

---

## 🖼️ 6. Image Optimization & Local SEO Geotagging

```bash
# Batch convert raw JPG/PNG assets to WebP
npm run convert:webp

# Embed Oldenburg GPS coordinates and IPTC metadata into images
npm run geotag

# Sync images and media assets to Cloudflare R2 bucket
npm run r2:sync
```

---

## 🚀 7. Production Deployment & Rollback

```bash
# Deploy to production server with atomic staging and health check
bash ship.sh
```

---

## 🚨 MANDATORY RULE: Keep To Do Kanban Updated
Whenever any feature, fix, or enhancement is completed:
1. Update `content/private/To Do Kanban.md`.
2. Move finished items from `🏗️ In Progress` to `✅ Done` with date `✅ YYYY-MM-DD`.
