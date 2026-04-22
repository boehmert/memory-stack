---
description: "Search order, Vault tools, and rules for the long-term knowledge base."
applyTo: "**"
priority: recommended
---

# Vault Knowledge Base & Search

Rules for knowledge retrieval — Vault, workspace files, and external systems.

---

## 1. Search Order (Required)

1. `vault_search` / `vault_context` — Vault first (long-term curated knowledge)
2. Workspace files — local project knowledge
3. External systems — Confluence, Jira, etc. as needed

---

## 2. Vault MCP Server (`vault-mcp`)

Curated Obsidian vault with documents on processes, architecture decisions, and domain knowledge.

### Vault Tools

| Tool | Purpose |
|---|---|
| `vault_search` | Full-text search (English keywords work best) |
| `vault_context` | LLM-ready context block for prompt enrichment |
| `vault_get` | Load single document by `doc_id` |
| `vault_list` | List all documents, filterable by tag/type |
| `vault_related` | Traverse linked documents via `related:` / `up:` |
| `vault_write` | Write new document with frontmatter |

### Usage Rules

- Formulate search queries in English (vault is predominantly English)
- Always cite **document ID and title** as source
- Flag uncertainties for `Draft` documents
- Contradictions between Vault and workspace files: **workspace wins** (more current)
- **Do not ask whether to search the vault** — just do it
