---
name: finish-agent-worktree
description: Finish work on a Codex, Claude, or Gemini Git worktree by reviewing and committing the scoped changes, synchronizing with remote main, validating, and safely merging through the repository's main integration worktree. Use when the user says the agent task is finished, asks to merge an agent branch into main, prepare it for deployment, or deploy it after validation.
---

# Finish Agent Worktree

Move completed agent work through a verified handoff without losing concurrent changes or confusing a local merge with deployment.

## Workflow

1. Read the repository instructions and identify its test, build, deployment, and production-verification commands.
2. Inspect the agent worktree's branch, status, diff, and recent commits. Keep unrelated or user-owned changes out of the task commit.
3. Run validation appropriate to the changed surface. Fix failures caused by the task before continuing.
4. Commit the completed task on the agent branch with a clear message. Do not create an empty commit or silently include unrelated files.
5. Run `scripts/finish-agent-worktree.ps1` without `-Apply`. Report any dirty worktree, missing main worktree, branch mismatch, or divergence before mutation.
6. When the user has asked to merge, rerun with `-Apply`. The helper fetches the remote, merges remote main into the clean source branch, updates the clean local main branch without rebasing or resetting, and merges the source branch into main. It aborts a conflicted merge and stops.
7. Run the relevant validation again from the main integration worktree. Report exact commands and results.
8. Push main and run the documented deployment only when the user's request explicitly authorizes those external mutations. Verify the live system before calling the work deployed or production-ready.

Do not stash, reset, force-push, delete branches/worktrees, or guess at conflict resolution. If either worktree becomes dirty after the preview, stop and preserve it. If deployment needs credentials, approval, or a project-specific decision, stop after the verified local merge and request that authority.

## Helper

Preview:

```powershell
& "$HOME\.agents\skills\finish-agent-worktree\scripts\finish-agent-worktree.ps1" `
  -Repository C:\Projects\example-worktrees\claude
```

Merge locally after review:

```powershell
& "$HOME\.agents\skills\finish-agent-worktree\scripts\finish-agent-worktree.ps1" `
  -Repository C:\Projects\example-worktrees\claude `
  -Apply
```

Use `-IntegrationWorktree` when the main worktree cannot be discovered automatically, and `-Remote` or `-MainBranch` when the repository does not use `origin/main`.

## Prompts for the user

Prepare and merge, but do not deploy:

> Use `$finish-agent-worktree`. Review and finish this task, run the relevant checks, commit only the scoped changes, synchronize with `origin/main`, merge it into the local main worktree, validate main, and stop before push or deployment.

Merge and deploy:

> Use `$finish-agent-worktree`. Review and finish this task, run the relevant checks, commit only the scoped changes, synchronize and merge it into main, validate main, then push and run the repository's documented deployment. Verify production before reporting completion.
