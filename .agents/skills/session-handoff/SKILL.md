---
name: session-handoff
description: Generates a comprehensive, lossless context handoff summary of a chat session to smoothly transfer work to a new conversation, another AI agent (Antigravity, Claude, ChatGPT, Cursor, Copilot, Codex), or another engineer.
---

# 🔄 Session & Agent Handoff Skill

Use this skill whenever concluding a chat session, preparing to switch models or conversations, or migrating work to a new AI agent, harness, or tool. This skill produces a structured, high-fidelity context packet that eliminates hallucinations, prevents repeating completed work, and gives the next agent an immediate roadmap on where to continue.

---

## 🎯 When to Use This Skill

- Switching to a fresh chat session (e.g. context window getting full, compacted, or slow).
- Moving work from Antigravity to another agent (e.g., Claude Code, Cursor, ChatGPT, GitHub Copilot, Codex).
- Handing over in-progress development to another developer or teammate.
- Pausing work for the day to resume seamlessly tomorrow.
- User asks:
  - _"Summarize what we did so I can start a new chat"_
  - _"Create a handoff prompt for another agent"_
  - _"Export our session context"_
  - _"Give me a continuation prompt for Claude/ChatGPT/Cursor"_
  - _"Where did we leave off?"_
  - _"Prepare handoff"_

---

## 📋 Information Gathering Protocol

Before composing the handoff, the agent **MUST** inspect the actual state of the workspace:

1. **Git State & Branch**:
   - Check current branch, status, and modified/staged files:
     ```bash
     git status -s
     git branch --show-current
     ```
2. **Recent Diffs & Changes**:
   - Review recent diffs or log entries if necessary:
     ```bash
     git diff --stat
     ```
3. **Session Logs & Ticket / Task Context**:
   - Identify active issue/ticket ID (e.g., Jira, GitHub issue), user problem, business requirement, and relevant doc/spec paths.
4. **Environment & Testing Status**:
   - Verify if linters passed, dev servers are running, or tests are pending.

---

## 🏗️ Standard Handoff Structure

When activated, produce the handoff formatted in the following standardized sections:

```markdown
# 📦 Agent & Session Handoff: [Ticket ID / Feature Name / Task]

**Date / Timestamp:** YYYY-MM-DD HH:mm  
**Active Branch:** `feature/...` (or main)  
**Target Environment:** Local Dev / Docker / Staging / Production  

---

## 1. 🎯 Objective & Background

- **Primary Goal:** High-level description of what we set out to achieve in this session.
- **Ticket / Context:** `[TICKET-ID / Task]` with brief description of user problem / business requirement.
- **Key Constraints:** Architectural boundaries, library requirements, or specific invariants (e.g. "Do not touch schema X", "Use bun, never npm", "Squash & merge").

---

## 2. 🛠️ What Has Been Implemented (Completed Work)

List all completed changes with exact file paths and line references where appropriate:

- **`path/to/file1.ext`**:
  - Added `FunctionName()` to handle X.
  - Implemented responsive styles for mobile viewports (< 768px).
- **`path/to/file2.ext`**:
  - Fixed race condition in Y.
  - Updated store mutation for Z.

---

## 3. 🧠 Key Architectural Decisions & Rationale

- **Decision 1:** Why approach A was chosen over approach B.
- **Technical Gotchas Discovered:** Any quirks in dependencies, API nuances, indexing, or framework reactivity.
- **Discarded Solutions:** What failed or was rejected so the next agent doesn't repeat the mistake.

---

## 4. 🚧 Current State & Work in Progress

- **Working Status:** What is currently functional and verified.
- **Incomplete Items:** What was started but not finished before closing this session.
- **Known Blockers / Edge Cases:** Edge cases that still need test coverage or edge-case handling.
- **Lint / Build Status:** Linting & build status (Clean / Pending fixes).

---

## 5. 🚀 Immediate Next Steps & Continuation Plan

Step-by-step instructions for the incoming agent in exact chronological order:

1. **[Next Step 1]**: File to edit -> exact change to apply.
2. **[Next Step 2]**: Run command `...` to verify.
3. **[Next Step 3]**: Prepare PR / commit changes.

---

## 6. 🧪 Verification & Testing Commands

- **Dev Server:** `npm run dev` / `bun run dev` / `cargo run` (URL / port)
- **Linting & Tests:** Commands to run unit tests and linters.
- **Manual Test Flow:** Step-by-step UI actions or curl requests to reproduce and test.

---

## 7. 📋 Copy-Paste Kickoff Prompt for the Next Agent

_(Enclosed in a ready-to-copy code block that can be directly pasted into a fresh chat window)_
```

---

## 🤖 Optimized Agent-to-Agent Kickoff Snippet Template

Always provide a self-contained, copy-pasteable block at the very end of the handoff response formatted like this:

````markdown
```markdown
# 🚀 Context Continuation & Handoff Prompt

You are taking over an in-progress development task. Here is the full context of what has been done, current state, and exact next steps.

### 📌 Project & Environment Context

- **Project:** <Project Name & Tech Stack>
- **Branch:** `<current-branch-name>`
- **Ticket / Task:** `<TICKET-ID / Task Description>`

### 🛠️ Completed Work

- `<file-path-1>`: Implemented <summary of changes>.
- `<file-path-2>`: Refactored <summary of changes>.

### 🚧 Current State & Paused Location

- We just finished: `<last completed item>`.
- The workspace is currently on branch `<branch-name>` with the above changes.
- Linters/tests status: `<passed / needs run>`.

### 🎯 Your Exact Next Task

1. Open `<target-file-path>`.
2. Implement `<specific-function-or-behavior>` following the existing pattern in `<reference-file>`.
3. Verify by running `<lint-or-test-command>`.

Please acknowledge this context briefly and proceed directly with Step 1.
```
````

---

## 💡 Best Practices for High-Quality Handoffs

1. **Be Specific with Paths & Symbols:** Always cite exact relative or absolute file paths (e.g. `src/components/ProductCard.tsx`), method names, and variable names rather than vague descriptions like "the product component".
2. **Include Command-Line Verifications:** Include the exact commands the next agent should run to build, test, and verify.
3. **Mention Unspoken Rules:** Remind the incoming agent of project rules (e.g., package manager preference, time tracking, testing requirements).
4. **Preserve Momentum:** Ensure the next agent doesn't have to spend tokens re-exploring already solved problems.
