# Plugins Reference

A plugin bundles skills, subagents, hooks, slash commands, and MCP server configs into one installable unit. Use plugins for team-wide standardization; use loose skills for one-off local workflows.

## Managing plugins

```bash
# Browse and install interactively
/plugin

# Add a marketplace, then install from it
/plugin marketplace add <owner/repo>
/plugin install <plugin-name>@<marketplace>
```

Installed plugins live under `~/.claude/plugins/`. Their skills appear alongside local ones and are invoked the same way.

## Commonly useful bundles

| Signal | Plugin | Contents |
|---|---|---|
| General productivity | **anthropic-agent-skills** | docx / xlsx / pptx / pdf, skill-creator, scheduling |
| Building UI | **frontend-design** | visual design direction, typography, non-templated layouts |
| Authoring skills/plugins | **plugin-dev** | skill-development, scaffolding, validation |
| Standardizing commits | **commit-commands** | conventional-commit workflow |
| Feature workflows | **feature-dev** | plan → implement → review pipeline |
| Writing hooks | **hookify** | translates "always do X" rules into hook config |
| Building MCP servers | **mcp-builder** | MCP scaffolding and protocol guidance |

## Authoring one

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json      # name, version, description, author
├── skills/<name>/SKILL.md
├── agents/<name>.md
├── commands/<name>.md
└── hooks/hooks.json
```

A marketplace is a repo with `.claude-plugin/marketplace.json` listing the plugins it serves. Point a team at one marketplace and every member gets the same tooling.

## Recommending well

- Recommend a plugin over individual skills when the user would otherwise be hand-copying three or more related pieces.
- Recommend authoring one only when there's a team to standardize — for a solo repo, loose skills in `.claude/skills/` are less overhead.
- Check what's already installed before recommending; duplicated skills with overlapping descriptions make triggering worse, not better.
