---
name: parallel-agent-worktrees
description: Create or inspect isolated Git worktrees for Codex, Gemini, and Claude when multiple AI agents need to work on one repository in parallel without sharing working files or branches.
---

# Parallel Agent Worktrees

Give each agent a separate directory and branch while retaining one shared Git object database.

## Workflow

1. Inspect `git status --short --branch`, `git worktree list`, and the proposed base ref. Do not reconcile, reset, pull, or rebase a divergent branch unless the user separately authorizes it.
2. Tell the user that uncommitted and untracked files are not copied into new worktrees.
3. Run `scripts/setup-agent-worktrees.ps1` without `-Apply` and review its preview.
4. Run the same command with `-Apply` only after creation is authorized.
5. Validate with `git worktree list` and `git -C <worktree> status --short --branch`.
6. Keep registered worktrees current with `scripts/sync-agent-worktrees.ps1`: preview first, then apply. The helper fetches the remote once and merges its main branch into each clean agent branch.

By default, the script centralizes worktrees under `C:\Users\super\worktrees\<repository-name>` (e.g. `C:\Users\super\worktrees\velyra`, `C:\Users\super\worktrees\masrisystems-app`) or sibling `<repository-name>-worktrees`, uses the exact committed `HEAD` as the base, and creates `codex/<task>`, `gemini/<task>`, and `claude/<task>` branches. Pass `-BaseRef origin/main` only when a fetched remote base is explicitly wanted. Pass `-DestinationRoot` to override.

Example:

```powershell
& "$HOME\.agents\skills\parallel-agent-worktrees\scripts\setup-agent-worktrees.ps1" `
  -Repository C:\Users\super\velyra `
  -Task workspace

& "$HOME\.agents\skills\parallel-agent-worktrees\scripts\setup-agent-worktrees.ps1" `
  -Repository C:\Projects\example `
  -Task checkout-redesign `
  -Apply
```

Never reuse one branch across worktrees. Do not delete existing worktrees or branches automatically. If an expected destination exists but is not already the matching registered worktree, stop and report it.

An agent may switch from its bootstrap branch to another branch under the same prefix, such as `claude/homepage`. Preserve that active branch. Never synchronize an agent directory when its branch does not match the expected `<agent>/*` prefix.

## Freshness

Run at the beginning of a working session and before handoff or integration:

```powershell
& "$HOME\.agents\skills\parallel-agent-worktrees\scripts\sync-agent-worktrees.ps1" `
  -Repository C:\Projects\example

& "$HOME\.agents\skills\parallel-agent-worktrees\scripts\sync-agent-worktrees.ps1" `
  -Repository C:\Projects\example `
  -Apply
```

Preview mode uses the current remote-tracking ref without fetching. Apply mode fetches `origin`, refuses dirty worktrees, merges `origin/main` with a merge commit when needed, and aborts a conflicted merge before continuing to the next worktree. Do not stash, reset, rebase, or resolve conflicts automatically.
