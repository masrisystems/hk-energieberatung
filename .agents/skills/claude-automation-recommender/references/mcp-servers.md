# MCP Server Reference

MCP (Model Context Protocol) servers give Claude Code tools for external systems: databases, browsers, issue trackers, cloud providers, live docs.

## Install patterns

```bash
# Add a server from the registry / by command
claude mcp add <name> -- <command> [args...]

# Project-scoped (checked into repo, shared with team)
claude mcp add --scope project <name> -- <command>

# User-scoped (available in every project)
claude mcp add --scope user <name> -- <command>

# Inspect / debug
claude mcp list
claude --mcp-debug
```

Project-scoped servers are written to `.mcp.json` at the repo root. Check that file in so the team shares the same setup.

`.mcp.json` shape:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

## Signal → server map

| Codebase signal | Server | What it unlocks |
|---|---|---|
| Any popular framework/library in deps | **context7** | Version-accurate live docs, kills hallucinated APIs |
| React/Vue/Angular/Next, any UI | **Playwright** | Drive a real browser, screenshot, assert on rendered DOM |
| `@supabase/*` in deps | **Supabase** | Query tables, inspect schema, run migrations |
| `convex` in deps | **Convex** | Deployment introspection, run queries/mutations, env vars, logs |
| `pg`, `mysql2`, `psycopg`, raw SQL | **Postgres/MySQL MCP** | Schema introspection + read queries during development |
| `prisma/schema.prisma` | **Prisma / DB MCP** | Schema-aware query and migration help |
| `.github/workflows/`, GitHub remote | **GitHub** | Issues, PRs, review comments, Actions runs |
| Linear/Jira ticket refs in commits | **Linear / Atlassian** | Read and update issues without leaving the session |
| `Dockerfile`, `docker-compose.yml` | **Docker** | Container/list/logs/exec |
| Terraform, CDK, `aws-sdk` | **AWS** | Inspect cloud resources |
| `@sentry/*` in deps | **Sentry** | Pull real stack traces into debugging |
| Slack-heavy team | **Slack** | Post build/deploy summaries |
| Long-running multi-session project | **Memory** | Persist context across sessions |

## Recommending well

- Only recommend a server whose signal you actually found in the repo. Name the file that proved it.
- Prefer one high-leverage server over five plausible ones.
- Flag prerequisites explicitly: `gh` CLI auth for GitHub, a browser install for Playwright, an API token env var for hosted services.
- Never recommend that credentials be pasted into config by Claude — point the user at env vars they set themselves.
- For servers not in this list, search the web for `<library> MCP server` before concluding none exists.
