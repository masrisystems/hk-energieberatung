# Hooks Patterns

Hooks are shell commands the harness runs on tool lifecycle events. They live in `.claude/settings.json` (project), `.claude/settings.local.json` (project, untracked), or `~/.claude/settings.json` (global).

Because the *harness* runs them, hooks are the only way to guarantee a behavior happens every time — instructions in CLAUDE.md are advisory, hooks are enforced.

## Events

| Event | Fires | Typical use |
|---|---|---|
| `PreToolUse` | Before a tool runs | Block edits to protected files, require confirmation |
| `PostToolUse` | After a tool succeeds | Format, lint, type-check, run tests |
| `UserPromptSubmit` | On each user message | Inject context (branch, ticket, env) |
| `Stop` | When Claude finishes a turn | Notify, summarize, run a final check |
| `SessionStart` | Session begins | Load project state |

Exit code `2` from a `PreToolUse` hook blocks the tool call; stderr is fed back as feedback.

## Shape

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\"" }
        ]
      }
    ]
  }
}
```

`matcher` is a regex over the tool name. The hook receives the tool call as JSON on stdin; useful fields are exposed as env vars.

## Patterns

**Auto-format on edit** — signal: `.prettierrc`, `pyproject.toml [tool.black]`, `rustfmt.toml`
```json
{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "npx prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null || true" }] }
```

**Type-check after edits** — signal: `tsconfig.json`
```json
{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "npx tsc --noEmit" }] }
```
Only worth it on small/medium projects; on large ones it adds seconds to every edit. Prefer running it at `Stop` instead.

**Lint on edit** — signal: `eslint.config.js`, `.ruff.toml`
```json
{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "npx eslint --fix \"$CLAUDE_TOOL_INPUT_FILE_PATH\" || true" }] }
```

**Block secret/lockfile edits** — signal: `.env*` present, `package-lock.json`
```json
{
  "matcher": "Edit|Write",
  "hooks": [{ "type": "command", "command": "case \"$CLAUDE_TOOL_INPUT_FILE_PATH\" in *.env|*.env.*|*.pem|*id_rsa*) echo 'Refusing to edit secrets file' >&2; exit 2;; esac" }]
}
```

**Run related tests after edit** — signal: `tests/`, `__tests__/`, `*_test.go`
```json
{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "npm test -- --findRelatedTests \"$CLAUDE_TOOL_INPUT_FILE_PATH\" --passWithNoTests" }] }
```

**Turn-end gate** — cheaper than per-edit, catches the same class of problems
```json
{ "hooks": { "Stop": [{ "hooks": [{ "type": "command", "command": "npm run check" }] }] } }
```

## Recommending well

- Every hook costs latency on every matching tool call. Recommend the cheapest event that catches the problem: `Stop` over `PostToolUse` for whole-project checks.
- Always append `|| true` to advisory hooks so a formatter crash doesn't derail the session — except for hooks whose whole point is to block.
- Windows: these commands run through the configured shell; prefer cross-platform node/npx invocations over POSIX-only shell syntax when the team is mixed.
- Pair a hook recommendation with the `permissions.allow` entries it needs.
