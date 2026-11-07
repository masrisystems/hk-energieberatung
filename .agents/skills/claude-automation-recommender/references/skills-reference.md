# Skills Reference

A skill is packaged expertise: instructions plus optional templates, scripts, and examples, loaded on demand. Lives at `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (global).

## Frontmatter

```yaml
---
name: create-migration
description: Scaffold and validate a database migration. Use when adding, altering, or dropping tables or columns.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep   # optional; omit to inherit all
disable-model-invocation: true                        # user-only (/create-migration)
---
```

| Goal | Frontmatter |
|---|---|
| Both Claude and user can invoke | omit both flags (default) |
| User-only — side effects like deploy, commit, send | `disable-model-invocation: true` |
| Claude-only — background knowledge, conventions | `user-invocable: false` |

`description` is the whole triggering mechanism when Claude invokes it. Write it as *when to reach for this*, and include the words a user would actually type. A vague description means the skill never fires.

## Layout

```
.claude/skills/api-doc/
├── SKILL.md              # instructions — keep it short, link the rest
├── references/
│   └── openapi-style.md  # loaded only when the workflow needs it
├── templates/
│   └── endpoint.yaml
└── scripts/
    └── validate.mjs
```

Keep `SKILL.md` lean — it's what gets read first. Push detail into `references/` and link to it, so the skill costs little until the depth is needed.

## Custom skills worth creating

| Signal in repo | Skill | Invocation | Bundle |
|---|---|---|---|
| Route/controller files | **api-doc** | both | OpenAPI template |
| `migrations/` dir | **create-migration** | user-only | naming rules + validation script |
| Test suite present | **gen-test** | user-only | example test in the house style |
| `components/` library | **new-component** | user-only | component + story + test templates |
| PR workflow / CI gates | **pr-check** | user-only | checklist, runs the same gates as CI |
| Tagged releases | **release-notes** | user-only | git-log-to-changelog script |
| Distinct house style | **project-conventions** | Claude-only | naming, error handling, layering rules |
| New devs onboarding | **setup-dev** | user-only | prereq check script |
| Repetitive deploy steps | **deploy** | user-only (side effects!) | runbook |

## Skills vs. the alternatives

- **CLAUDE.md** — always loaded, so it must stay small. Put universal rules here, everything else in a skill.
- **Skill** — loaded on demand. Right for anything that only matters sometimes.
- **Subagent** — separate context window. Right when the work is wide or needs an independent perspective.
- **Hook** — enforced by the harness. Right when "every time, no exceptions" is the requirement; a skill can be skipped, a hook cannot.

## Recommending well

- Recommend a skill when you can point at a workflow the user (or their team) repeats. If it's a one-off, it's just a prompt.
- Mark anything with side effects `disable-model-invocation: true`.
- Say whether it belongs in the project (`.claude/`, shareable via git) or globally (`~/.claude/`, personal).
