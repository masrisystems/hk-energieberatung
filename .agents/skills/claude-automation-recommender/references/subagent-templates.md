# Subagent Templates

Subagents are specialized agents with their own system prompt, tool allowlist, and fresh context. They live in `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (global).

Each spawn starts cold and re-derives context, so subagents pay off when the work is **wide** (many files to sweep) or **independent** (a perspective the main thread shouldn't hold), not when it's a task the main thread could just do.

## File shape

```markdown
---
name: security-reviewer
description: Audits auth, session, and payment code for vulnerabilities. Use after changes to auth or billing paths.
tools: Read, Glob, Grep, Bash
model: sonnet
---

You are a security reviewer. ...

Report findings ranked by severity. For each: file:line, the concrete
failure scenario, and the minimal fix. Report nothing if nothing is wrong —
do not manufacture findings.
```

`description` is what the main agent matches against when deciding to delegate — write it as *when to use this*, not *what it is*.

Omit `tools` to inherit everything. Restrict it for read-only reviewers so they cannot mutate the repo.

## Templates

**code-reviewer** — signal: >500 files, active PR workflow
> Review the diff for correctness, error handling, and edge cases. Read surrounding code before judging any hunk. Every finding needs a concrete failure scenario (inputs → wrong output). Skip style nits the formatter already handles.
> Tools: `Read, Glob, Grep, Bash`

**security-reviewer** — signal: auth, sessions, payments, file upload, raw SQL
> Audit for injection, broken access control, secrets in code, unsafe deserialization, missing authz on state-changing routes, and IDOR. Trace user input to sink before reporting. Rank by exploitability.
> Tools: `Read, Glob, Grep, Bash`

**test-writer** — signal: thin or absent test suite
> Write tests matching the existing suite's framework and conventions. Cover the failure paths, not just the happy path. Run the suite and iterate until green. Never weaken an assertion to make a test pass.
> Tools: `Read, Write, Edit, Bash, Glob, Grep`

**performance-analyzer** — signal: hot loops, N+1 risk, large data paths
> Find bottlenecks: N+1 queries, unbounded fetches, repeated work in loops, missing indexes, blocking I/O on request paths. Measure or cite the mechanism — no speculative micro-optimizations.
> Tools: `Read, Glob, Grep, Bash`

**ui-reviewer** — signal: component-heavy frontend
> Review components for accessibility (labels, roles, focus order, contrast, keyboard paths), responsive behavior, and loading/error/empty states. Cite the WCAG criterion for each finding.
> Tools: `Read, Glob, Grep`

**api-documenter** — signal: route files, OpenAPI spec
> Read the route definitions and produce/update the OpenAPI spec: paths, params, request/response schemas, auth requirements, error codes. Derive from code, never invent endpoints.
> Tools: `Read, Write, Edit, Glob, Grep`

## Recommending well

- One or two agents that match a real, recurring workload beat a roster of six.
- Read-only reviewers should have `tools` restricted — it's the difference between a review and an unsupervised refactor.
- Note that project agents in `.claude/agents/` are shareable via git; global ones in `~/.claude/agents/` are not.
