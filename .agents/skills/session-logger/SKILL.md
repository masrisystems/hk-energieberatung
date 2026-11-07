---
name: session-logger
description: Logs coding progress to per-project gemini-scribe logs and automates Kimai time tracking (copy-paste snippet, CSV import, or 1-click direct Kimai REST API booking). Use when concluding a work session, tracking hours, or when the user asks to "log session", "book time in kimai", or "track work".
---

# Session & Kimai Time Tracking Automation

Use this skill when concluding a work session, tracking development time across projects under `C:\Users\super\Projects`, or when the user asks to log/sync hours to Kimai.

---

## ⚙️ 1. Setup Personal Kimai API (One-Time)

To enable direct 1-click REST API time booking without opening a browser:

1. **Create Config File:**
   ```powershell
   Copy-Item "C:\Users\super\.agents\config\kimai.env.example" "C:\Users\super\.agents\config\kimai.env"
   ```
2. **Obtain API Password in Kimai:**
   - Log into your Kimai instance.
   - Go to **Profile** (top right) $\rightarrow$ **Edit Profile** $\rightarrow$ **API** tab.
   - Set an **API password** and click **Save**.
3. **Configure `C:\Users\super\.agents\config\kimai.env`:**
   ```bash
   KIMAI_URL="https://kimai.your-domain.com"
   KIMAI_USER="your-username-or-email"
   KIMAI_TOKEN="your-api-password"
   ```
4. **Test Connection & View Project IDs:**
   ```powershell
   pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1" -Test
   ```
   *(Pings the API, confirms authentication, and prints all your available Project IDs and Activity IDs).*

---

## 🚀 2. Quick Workflows for Any Project in `C:\Users\super\Projects`

The scripts automatically detect the current repository/directory name and branch context.

### Workflow A: Log Session + 1-Click Direct Kimai Booking
Logs the work to the session scribe log AND books it straight into Kimai:

```powershell
# In PowerShell (specify hours and summary):
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\log-session.ps1" -Summary "Refactored caching and API error handling" -Post -Hours 2

# Or Bash:
bash "$HOME/.agents/skills/session-logger/scripts/log-session.sh" --post --hours 2 "Refactored caching and API error handling"
```

### Workflow B: Standalone Kimai Booking (`kimai-sync`)
Book time without writing to a local scribe log:

```powershell
# Book 1.5 hours on the current project:
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1" -Post -Hours 1.5 -Summary "Implemented webhook handlers"

# Book with custom time window:
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1" -Post -Begin "09:00" -End "12:30" -Summary "Frontend component wiring"

# Override specific project/activity:
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1" -Post -Project 12 -Activity 5 -Hours 3 -Summary "Database performance optimization"
```

### Workflow C: Scribe Log Only (with Copy-Paste Snippet)
If you prefer not to book via API immediately, log progress and get a formatted copy-paste snippet:

```powershell
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\log-session.ps1" -Summary "Added unit tests for payment integration"
```

### Workflow D: Export CSV Import File
Generate a CSV file to bulk import into Kimai (under **Zeiten / Stundenzettel $\rightarrow$ Import**):

```powershell
pwsh -File "C:\Users\super\.agents\skills\session-logger\scripts\kimai-sync.ps1" -Csv -Hours 4 -Summary "Sprint feature development"
```

---

## 📁 3. Scribe Directory Resolution

1. **Obsidian Work Folders:** If the project has an Obsidian client folder under `masrisystems-app/content/private/Work/...`, logs are routed to `.../gemini-scribe/<YYYY-MM-DD>-session.md`.
2. **Standalone Projects:** In any project under `C:\Users\super\Projects\<project>`, logs default to `<repo-root>/private/gemini-scribe/` or the directory set in `$env:KIMAI_SCRIBE_DIR`.

---

## 📋 4. Log Entry Format

Each session log appends:
```markdown
### 🕒 HH:MM — Branch: <branch> (Ticket: <ticket-if-present>)
- **Summary:** <what was accomplished>
- **Kimai Note:** [<ticket-or-project>] <summary>
```
