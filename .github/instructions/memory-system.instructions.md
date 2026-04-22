---
description: "Copilot Memory System: Scopes, Active Context, Session Workflow."
applyTo: "**"
priority: recommended
---

# Copilot Memory System

Rules for the built-in Memory System of VS Code Copilot.

---

## 1. Overview

The Memory System stores information in a **virtual file system** under `/memories/`. These files are **not** in the Git repo and **not** visible in the file explorer — access is exclusively via the Memory Tool (`view`, `create`, `str_replace`, `insert`, `delete`).

**Physical location:** VS Code Workspace Storage (`%APPDATA%/Code/User/workspaceStorage/`). Not portable — memories are tied to the local workspace.

---

## 2. Scopes

| Scope | Path | Lifetime | Auto-Inject |
|---|---|---|---|
| **User** | `/memories/` | Persistent across all workspaces | Yes (first 200 lines) |
| **Repo** | `/memories/repo/` | Persistent, workspace-bound | No (manual read) |
| **Session** | `/memories/session/` | Current conversation only | No (manual read) |

---

## 3. Recommended files in `/memories/repo/`

| File | Purpose | Written by |
|---|---|---|
| `active-context.md` | Work state between sessions: focus, decisions, thought process, open questions | `/save-session` prompt |
| `mcp-memory.md` | MCP server quirks, token issues, workarounds | `/remember` prompt |
| `process-memory.md` | Team processes, planning insights | `/remember` prompt |
| `tools-memory.md` | VS Code, extensions, Copilot behavior | `/remember` prompt |

---

## 4. Session Continuity (Workflow)

```text
Session end:    /save-session  →  active-context.md update
Session start:  Read active-context.md for previous state
Single learning: /remember     →  Write to domain-specific memory file
```

**Rule:** For complex tasks, read `/memories/repo/active-context.md` at session start. It contains the work focus, recent decisions with reasoning, and open questions from previous sessions.

---

## 5. Design Decision

Active Context lives in `/memories/repo/` (virtual) rather than as a physical file in the repo:

- **Pro:** Automatic in the Copilot ecosystem, no Git noise, no risk of accidentally committing work states
- **Con:** Not portable, not versioned, not in backup
- **Mitigation:** Durable learnings are promoted via `/remember` into memory files or via promotion path into `.instructions.md` files
