---
name: overnight-server-mode
description: Prepare a Windows laptop for unattended overnight or 24/7 server-style operation by gracefully closing nonessential desktop apps while preserving Antigravity, scheduled work, Windows services, and uncertain background processes.
---

# Overnight Server Mode

Reduce interactive desktop load without disrupting scheduled automation or risking unsaved work.

This skill is for Windows. It does not shut down Windows, change sleep or lid settings, stop services, disable security software, alter scheduled tasks, or guarantee hardware lifespan.

## Safety contract

- Treat installing or invoking this skill as permission to audit only. Before closing anything, create a fresh plan and obtain explicit confirmation of that exact plan ID.
- Never terminate by executable name alone. Never use broad `Stop-Process`, `taskkill /IM`, WMI termination, service stops, or process-tree killing.
- Preserve Antigravity and sidecar scheduling. The helper protects processes whose identity contains Antigravity, Gemini sidecar, `language_server`, `multicall schedule`, `agentapi`, or sidecar markers, plus their relevant process tree.
- Preserve Windows services, security processes, the shell, the invoking AI's process chain, user-specified exceptions, and every headless or uncertain background process.
- The AI currently running the skill must remain alive long enough to deliver the report. Afterward, the user may close that AI host manually unless it is Antigravity or another required scheduler host.
- Close only interactive processes with visible top-level windows. Use `CloseMainWindow()` so applications can save state or show their normal unsaved-work prompt.
- If a process refuses to close, changes identity, becomes protected, or no longer has a visible window, leave it running and report it. This skill has no force-close mode.
- A new plan and confirmation are required after expiry, a changed PID identity, or any protection ambiguity.

## Workflow

1. Ask whether any additional applications must remain open. Add their executable names with `-PreserveProcessName`; do not guess that a background process is disposable.
2. Generate a plan:

   ```powershell
   & "$HOME\.agents\skills\overnight-server-mode\scripts\Enter-OvernightServerMode.ps1" -Action Audit
   ```

   To add exceptions:

   ```powershell
   & "$HOME\.agents\skills\overnight-server-mode\scripts\Enter-OvernightServerMode.ps1" `
     -Action Audit `
     -PreserveProcessName @('my-dashboard', 'my-backup-client')
   ```

3. Show the user the candidate windows, protected processes, preserved background-process summary, plan path, and plan ID. Warn that closing editors or terminals can stop unsaved or active work even when the close request is graceful.
4. Only after the user explicitly approves that plan ID, apply the saved plan:

   ```powershell
   & "$HOME\.agents\skills\overnight-server-mode\scripts\Enter-OvernightServerMode.ps1" `
     -Action Apply `
     -PlanPath '<path printed by Audit>' `
     -ConfirmPlanId '<plan ID printed by Audit>'
   ```

5. Report each outcome separately: closed, still running, close not accepted, identity changed, newly protected, or already exited. Never describe a close request as successful unless the process actually exited.
6. Recheck Antigravity/scheduler protection after the close pass. If scheduled-task execution itself matters, verify the real task or sidecar runtime evidence; an intact process or enabled schedule alone does not prove a run completed.

## Laptop-health boundary

Software cleanup can reduce resource use but cannot make continuous laptop operation harmless. Keep ventilation unobstructed, use a firm surface, use the manufacturer's battery charge-limit feature when available, and monitor sustained heat with the manufacturer's supported tooling. Treat sleep, lid-close, charging, BIOS, fan, and power-plan changes as a separate user decision; do not change them under this skill.

## Escalation boundary

Headless CLIs, hidden Electron helpers, terminals without a closeable window, and unknown background processes are report-only. If the user wants one of them stopped, identify its exact ownership, parent chain, command, and active-work risk, then request separate approval for that exact target. Do not expand this skill into unattended generic process cleanup.
