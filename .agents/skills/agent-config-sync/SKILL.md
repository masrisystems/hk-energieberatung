---
name: agent-config-sync
description: Maintain and synchronize the shared user-level skills and global rules used by Codex, Claude Code, and Gemini CLI. Use when adding, migrating, validating, linking, or diagnosing cross-agent skills and instructions. Do not use for ordinary project configuration that belongs to only one agent.
---

# Shared Agent Configuration

Use `C:\Users\super\.agents` as the portable source of truth.

## Workflow

1. Run `scripts/sync.ps1` without arguments and review its dry-run report.
2. Resolve reported physical-file or divergent-link conflicts before applying changes.
3. Run `scripts/sync.ps1 -Apply` only when the requested changes are authorized.
4. Validate the resulting skills and instruction entrypoints.

The synchronizer creates missing Claude and Codex skill junctions and maintains marked shared-rule sections. It preserves Codex's `.system` directory, backs up changed rule files, and does not delete or overwrite conflicting skill directories.

Use `-MigrateLegacyRules` only for an explicitly authorized first migration. It replaces legacy global rule content while preserving Gemini's managed memory block when present.
