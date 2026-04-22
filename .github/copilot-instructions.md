# Copilot Instructions

This workspace uses a **three-tier memory system** to give Copilot persistent context across sessions.

## Source of Truth

- Workspace files override chat history and model knowledge.
- When context is insufficient, say so explicitly instead of guessing.

## Memory System

See `.github/instructions/memory-system.instructions.md` for the full specification.

Quick reference:
- `/save-session` — persist session state to `active-context.md`
- `/remember` — store a learning in domain-specific memory
- `/vault-write` — write distilled knowledge to the Obsidian Vault
- `/vault-ingest` — extract knowledge from source documents into the Vault

## Rules

1. Keep outputs concise and direct.
2. Ask for missing details or mark assumptions — never invent.
3. Never expose secrets from `.env`.
4. Stay within scope — no refactoring beyond the task.
