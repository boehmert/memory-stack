---
description: "Save session results and thought process for the next session."
---

# Save Session

Save the current session state as persistent context for the next session.

## What You Do

1. **Update Active Context** — Write `/memories/repo/active-context.md` with the current state
2. **Record Thought Process** — Capture not just WHAT, but WHY

## Steps

### Step 1: Analyze Session

Review the conversation history and extract:

- **Results:** What was concretely achieved? (Files, decisions, insights)
- **Thought Process:** Which alternatives were considered? Why was X chosen over Y?
- **Open Questions:** What is unresolved, needs follow-up or user decision?
- **Next Steps:** What should happen next?

### Step 2: Write Active Context

Update `/memories/repo/active-context.md` with this format:

```markdown
# Active Context

Persistent work context between sessions. Written by `/save-session`, read at session start.

## Current Focus

- [2-4 bullet points: What is being worked on?]

## Recent Results

### Session {DATE}: {Topic}
- **Decision:** [Core decision in one sentence]
- **Thought Process:** [Why this way and not another? Which alternatives were discarded?]
- **Artifacts:** [Which files were created/modified?]

[Keep previous sessions, newest on top, oldest at bottom. No rotation limit.]

## Open Questions

- [Unresolved points that need follow-up]

## Next Steps

- [Concrete next actions]
```

### Step 3: Extract Learnings

Check if individual insights from the session are suitable as durable learnings:
- **Yes** → Additionally write to the matching memory domain via `/remember` logic
- **No** → Active Context is sufficient as a bridge

### Step 4 (optional): Suggest Vault Write-back

Check the session content: Are there insights that...
- are **not only session-specific** (≠ active-context)
- are **not a pure tool/process pattern** (≠ /remember)
- but represent **reusable domain knowledge** — something you'd want to look up in 6 months?

If yes → Suggest explicitly:
```
→ /vault-write [domain] [Title] — [1-sentence justification why it's vault-worthy]
```

If no → Skip this step, no comment.

**Three-way write target split:**
| What | Tool | Target |
|---|---|---|
| Session state, thought process, open questions | `/save-session` | `active-context.md` (ephemeral, rotating) |
| Tool patterns, MCP quirks, processes | `/remember` | `*-memory.md` (persistent, auto-loaded) |
| Distilled domain knowledge with provenance | `/vault-write` | Obsidian Vault (accumulating, searchable via `vault_search`) |

### Rules

- **Brevity over completeness:** Active Context is not a transcript. Max 10 lines per session entry.
- **Thought process is mandatory:** Every decision needs a "why". Without reasoning, there's no transfer value.
- **No rotation:** All session entries are kept. Newest on top, oldest at bottom. The file grows — that's intentional.
- **No secrets:** No tokens, passwords, or personal data.
- **Write immediately:** Don't ask whether to write — just do it. The user explicitly called `/save-session`.

## Completion

After writing: Brief confirmation of what was saved. No prose.
