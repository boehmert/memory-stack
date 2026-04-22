---
name: Vault Write
description: "Distill knowledge from the session and persist it in the Obsidian Vault via vault_write. Syntax: /vault-write [domain] [Title]"
mode: agent
---

# Vault Write

Distill an insight from the session and persist it as a Knowledge Distillate in the Obsidian Vault — with full provenance.

## When to Use

Use this prompt when an insight:
- is **not only session-specific** (→ for that: `/save-session`)
- is **not a pure tool pattern** (→ for that: `/remember`)
- but represents **reusable domain knowledge** that will enrich future sessions

## Input

```
/vault-write [domain] [Title]
```

**Domains → Tags:**

| Domain | Vault Tag |
|---|---|
| `engineering` | `engineering` |
| `architecture` | `architecture` |
| `process` | `process` |
| `data` | `data` |
| `personal` | `personal` |

**Examples:**
- `/vault-write engineering Context Engineering Best Practices`
- `/vault-write architecture SHACL Validation Pattern for Controlled Vocabularies`

---

## Steps

### 1. Distill Content

Extract the core insight from the conversation:
- No chat context references ("as mentioned above...")
- No padding
- Directly usable as a reference snippet
- With concrete examples or sources where available

Body structure:

```markdown
# {Title}

## Core Insight

[1-3 sentences: What is the central finding?]

## Details

[More detailed explanation, context, examples]

## Relevance

[Why is this relevant for the project?]

## Sources

[Links, documentation pages, file paths]
```

### 2. Write to the Vault

Use the `vault_write` MCP tool with these parameters:

| Parameter | Value |
|---|---|
| `title` | Exact title of the snippet |
| `body` | The distilled content (Markdown, without frontmatter) |
| `tags` | Domain tag + topical tags (e.g. `["engineering", "context-engineering", "best-practices"]`) |
| `document_type` | `Knowledge Distillate` |
| `up` | `[[MOC_Start]]` |
| `related` | Wikilinks to related documents (e.g. `["[[KB-2026-001]]"]`) |
| `created_by` | `copilot` |

**Notes:**
- The ID is generated automatically (`KB-YYYYMMDDHHMMSS`)
- The filename is derived automatically from the title
- The frontmatter is assembled by the tool

### 3. Completion

Show the user:
```
{ID} created: {Title}
  Tags: {tags}
  Status: draft — searchable in the vault via vault_search
```

---

## Rules

- **Always use `vault_write`** — never create files directly in the vault
- **Tags over folders** — the vault is flat, organization happens through tags and wikilinks
- **Confidence not in frontmatter** — instead as a tag (`confidence/high`, `confidence/medium`)
- **Sources as tag or in body** — cite sources in the body under ## Sources
