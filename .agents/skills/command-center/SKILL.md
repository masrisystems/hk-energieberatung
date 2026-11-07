---
name: command-center
description: Manage, operate, and extend the Masri Systems Command Center, Live Database Sync engine, and Obsidian Kanban board synchronization within masrisystems-app.
---

# Command Center & Database Sync Engine (`command-center`)

Use this skill whenever working on, interacting with, or troubleshooting the **Command Center**, **Autonomous Agent Dispatcher**, **Live Database Remote Sync**, or **Kanban Board Synchronizer** in `masrisystems-app`.

---

## 🚨 MANDATORY RULE: Kanban Board Updates
**Whenever a new feature is built, a bug is fixed, or any functional changes are made to `masrisystems-app`:**
1. You **MUST** update `content/private/To Do Kanban.md`.
2. Move relevant completed tasks from `🏗️ In Progress` or `🚀 Today` to `✅ Done` with completion date (`✅ YYYY-MM-DD`).
3. For client-specific work, update the corresponding client board under `content/private/Work/MasriGMBH/Kunden/`.

---

## 🧭 1. Command Center Architecture

The Command Center provides a single pane of glass for engineering, planning, agent orchestration, and deliverable tracking.

- **Filament Admin Integration**: Embedded inside `/administration/command-center` under the **Management** navigation group.
- **Standalone Web Application**: Available full-screen at `/command-center`.
- **Desktop Companion**: Located at `$env:PROJECTS\command-center` (Electron + React) sharing the exact same `project-tracker.json` state.

### Key Views
1. **Swimlane View** (`Tabs/SwimLane.vue`): Strategic multi-week timeline with dynamic week headers, vertical NOW line indicator, phase bands, domain lanes, and progress ring nodes.
2. **Task Board View** (`Tabs/TaskBoard.vue`): 5-column tactical Kanban (`todo`, `in_progress`, `review`, `done`, `blocked`) with drag-and-drop and filter pills.
3. **Agent Hub View** (`Tabs/AgentHub.vue`): Active agent roster, 68+ ECC agent catalog browser, 43+ global skills hub, live searchable activity feed, and 1-click context generator.
4. **Calendar View** (`Tabs/Calendar.vue`): 7-day Monday–Sunday deliverable matrix.

---

## 🤖 2. ECC Autonomous Agent Fleet & Execution

- **Catalog Service**: `App\Services\AgentCatalogService.php` dynamically loads all 68+ ECC agents from `~/.agents/catalogs/ecc/agents/*.md` and 43+ portable skills from `~/.agents/skills/*/SKILL.md`.
- **Autonomous Dispatch Service**: `App\Services\AutonomousAgentService.php` fuses task acceptance criteria, constraints, and context files into an agent brief.
- **Artisan Dispatch Command**:
  ```bash
  # Dispatch autonomous agent to execute a task
  php artisan command-center:agent-run {taskId?} --agent=code-explorer --summary="Exploration complete" --auto-approve
  ```

---

## 🔄 3. Safe Live Database Sync (Local ⇄ Live)

Enables seamless bi-directional database synchronization between local development (SQLite/MySQL) and live production (Uberspace MariaDB/MySQL).

### Automated SSH Tunneling
`DatabaseSyncService` automatically detects if the live server is on Uberspace (`gienah.uberspace.de`) and opens an SSH port-forward tunnel (`127.0.0.1:3307 -> 127.0.0.1:3306`) seamlessly in the background using SSH keys.

### Commands:
```bash
# Check connectivity and table row differences
php artisan db:sync-status

# Preview incoming live data
php artisan db:pull-live --dry-run

# Safe Pull from Live (creates timestamped backup in storage/app/backups/ first)
php artisan db:pull-live

# Safe Push to Live (requires PUSH-LIVE confirmation token)
php artisan db:push-live
```

### Filament UI:
- Open `/administration/database-sync` to view connection latency, table row matrices, and trigger 1-click backups and synchronization.

---

## 📋 4. Daily Board Synchronization

- **Board Config**: `command-center.boards.json` maps Obsidian Kanban markdown files (`To Do Kanban.md`, `Kanban Ranalp.md`, `kanban Velyra.md`, `Kanban Maisonanthony.md`) to tracker milestones.
- **Sync Command**:
  ```bash
  php artisan command-center:sync-boards --dry-run
  php artisan command-center:sync-boards
  ```
- **Scheduler**: Automatically scheduled in `routes/console.php` to run daily at `00:00`.
