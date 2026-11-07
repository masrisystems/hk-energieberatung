---
name: git-time-extractor
description: Use when extracting work sessions, calculating engineering hours, generating timesheets, or categorizing client tickets and deliverables from git commit history.
---

# Git Time & Ticket Extractor

## Overview

A robust system to analyze any Git repository's commit history, automatically filter bot noise, cluster commits into contiguous work sessions, calculate accurate engineering hours, organize work into client-ready feature packages / tickets, and generate sanitized Markdown and CSV timesheets.

---

## When to Use

- When a client asks for a detailed breakdown of work done, completed features, or ticket deliverables over a specific period or all time.
- When generating timesheets, hourly reports, or **Kimai** time-tracking entries from Git history.
- When billing a client and preparing proof of work / performance records (*Leistungsnachweis*).
- When reconciling Jira / GitHub issues or Obsidian Kanban boards against real executed Git commits.

### When NOT to Use
- Do NOT use for real-time task tracking while working (use `echo-workroutine` or `log-session` for live in-session logging).
- Do NOT use on non-git directories.

---

## ⚖️ Critical Compliance & Legal Rules

> [!CAUTION]
> **Employment & Overlap Protection Rule (Default Behavior):**
> Many developers have strict employment or core-hours contracts. **NEVER expose specific daytime clock timestamps** (e.g. `09:30 – 11:45`, `14:15:30`, exact commit timestamps) in client timesheets or exported logs unless explicitly requested by the user.
> 
> **Always sanitize output by default:**
> 1. Report **total daily hours** (e.g. `2.88 Hours`) and **work units** (e.g. `Unit 1: 2.88 h`).
> 2. Report **total package hours** (e.g. `TICKET-01: 23.50 h`).
> 3. Report **monthly and overall project hours**.
> 4. Keep commit dates (e.g. `2026-06-02`) and commit hashes, but omit the time of day.

---

## 🚀 Step-by-Step Workflow

### 1. Extract Git Commits
Run `git log` with ISO strict dates and delimiters across all branches:

```bash
git log --all --since="YYYY-MM-DD" --until="YYYY-MM-DD" --date=iso-strict --pretty=format:"COMMIT_SEP%h||%H||%an||%ae||%ad||%s||%b"
```

- Exclude automated dependency bots (`dependabot`, `renovate`, `github-actions[bot]`).
- Deduplicate by commit hash if commits appear across multiple merged branches.

### 2. Session Clustering & Effort Calculation
Cluster human commits into contiguous work sessions using the standard formula:

```
1. Group commits by calendar day (in the relevant local timezone, e.g. Europe/Berlin).
2. For each day, iterate through chronological commits:
   - If (commit[i].time - commit[i-1].time) <= 90 minutes:
     -> Add to current work session.
   - If gap > 90 minutes:
     -> Close current session and start a new work session.
3. Calculate estimated effort for each session:
   - elapsedMinutes = commit[last].time - commit[first].time
   - estimatedMinutes = Math.max(elapsedMinutes + 30, commitCount * 25)
     (Accounts for development, testing, linting, and PR review prior to each commit)
   - estimatedHours = estimatedMinutes / 60
```

### 3. Classify Work into Feature Packages / Tickets
Group commits logically into **5–10 structured client tickets** by analyzing commit subjects, bodies, and touched components:
- **ID & Code:** Sequential ticket IDs (`TICKET-01`, `TICKET-02` or `[PROJECT]-01`).
- **Domain / Category:** E.g., *Frontend / UX*, *Backend / API*, *DevOps / CI-CD*, *Legal & Compliance*, *QA / Static Analysis*.
- **Summary & Business Value:** Clear 1–2 sentence non-technical summary of what this accomplished for the client.
- **Key Deliverables:** Bullet list of concrete features, components, and fixes delivered.
- **Effort Allocation:** Total hours and percentage of overall milestone.

### 4. Output Generation

Produce two distinct sheets:

1. **Sheet 1: Tickets & Deliverables Report (`TICKETS_...`):**
   - Executive summary table with status, commit counts, and total hours per ticket.
   - Monthly effort distribution table.
   - Deep-dive per ticket with business value, deliverables, and sample commit logs.

2. **Sheet 2: Timings & Work Session Log (`TIMINGS_...`):**
   - Day-by-day activity log with daily total hours, completed work units, and Kimai copy-paste blocks.
   - Total hours per month and full project total.

3. **Spreadsheet CSV Exports:**
   - `tickets_...`.csv (Ticket_ID, Package_Code, Package_Title, Category, Status, Commits_Count, Total_Hours, Summary, Key_Deliverables).
   - `timings_...`.csv (Date, Work_Unit, Commits_Count, Effective_Hours, Activities_Summary).

### 5. Persistence & Kanban Sync
- Save reports in a dedicated folder under the client's Obsidian directory:
  `<Obsidian-Vault>/content/private/Work/MasriGMBH/Kunden/<ClientName>/Reports & Timings (<DateRange>)/`.
- Add an entry to the client's Kanban board under `## Done`.

---

## 🛠️ Automated CLI Script

A ready-to-use Node.js CLI script is included in `scripts/extract-timings.js`:

```bash
# Run on current repository for all time
node ~/.agents/skills/git-time-extractor/scripts/extract-timings.js --repo . --client "Client Name" --project "Project Name"

# Run for a specific date range and output to client directory
node ~/.agents/skills/git-time-extractor/scripts/extract-timings.js --repo "C:/path/to/repo" --since "2026-06-01" --until "2026-09-02" --out-dir "C:/path/to/obsidian/client/reports"
```

---

## 📋 Kimai Timesheet Standard Format

Always format Kimai entries cleanly for instant copy-pasting:

```text
[PROJECT-NAME] Development & Delivery (YYYY-MM-DD) [X.XX h]: Feature 1; Bugfix 2; Component refactor 3 (+N items)
```
