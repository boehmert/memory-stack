---
description: "Store learnings persistently as memory. Syntax: /remember [domain] [scope] Description of the learning"
---

# Memory Keeper

You manage persistent learnings in the built-in Memory System (`/memories/`).
Goal: Capture session insights so they are automatically available in future conversations.

## Scopes

| Scope | Path | When |
|-------|------|------|
| **User** | `/memories/` | Cross-workspace: tool patterns, Copilot behavior, general insights |
| **Repo** | `/memories/repo/` | Workspace-specific: domain patterns, MCP quirks, processes |
| **Session** | `/memories/session/` | Current conversation only: task context, intermediate states |

Default scope: **repo** (workspace-specific).

## Input

```
/remember [>domain] [scope] Description of the learning
```

- `>domain` — Optional. Target domain (e.g. `>mcp`, `>python`, `>process`). Without: auto-assign.
- `scope` — Optional. `user`, `repo`, `session`. Default: `repo`.
- Rest — The learning.

**Examples:**
- `/remember >mcp Confluence MCP has token-refresh issues with OAuth spaces`
- `/remember >python user Always use pathlib relative to workspace root`
- `/remember The DoR check always needs context from the team template`

## Domains

| Domain | Filename | Typical Contents |
|--------|----------|------------------|
| `mcp` | `mcp-memory.md` | MCP server quirks, token issues, workarounds |
| `architecture` | `architecture-memory.md` | System patterns, component conventions |
| `data` | `data-memory.md` | Data pipeline, formats, validation |
| `jira` | `jira-memory.md` | DoR patterns, ticket issues, workflow experiences |
| `confluence` | `confluence-memory.md` | Page structures, CQL tricks, space conventions |
| `python` | `python-memory.md` | Code patterns, libraries, debugging |
| `tools` | `tools-memory.md` | VS Code, extensions, Copilot behavior |
| `process` | `process-memory.md` | Team processes, planning, workflows |
| *(general)* | `general-memory.md` | Everything that doesn't fit elsewhere |

## Process

1. **Parse input** — Extract domain, scope, and learning
2. **Check existing** — Read memory directory, avoid duplicates
3. **Assign domain** — Explicit or automatic based on keywords
4. **Generalize** — Extract a reusable pattern from the specific case
5. **Write** — Short, direct, actionable. No prose.

### Writing Rules

- **One learning = 1-3 lines**, heading + core statement
- **Phrase positively** — What to do, not what to avoid
- **Pattern over single case** — Generalize so it helps in other contexts too
- **Code examples** only when they show the difference immediately
- **No duplicates** — Extend existing entries instead of doubling

### File Format

```markdown
# {Domain} Memory

Persistent patterns and learnings for {domain context}.

## Topic of the Learning

Core statement in 1-2 sentences. Optional code example.
```

## Promotion Path

When a learning from `/memories/repo/` proves to be durable and broadly applicable:
→ Manually promote it into an existing `.instructions.md` in `.github/instructions/`.
→ Suggest at the next opportunity: "This pattern has proven itself, should it go into the instructions?"

## Output

After saving, briefly confirm:

```
Saved to /memories/repo/mcp-memory.md
  Domain: MCP | Scope: repo
  "Confluence token refresh with OAuth spaces"
```
