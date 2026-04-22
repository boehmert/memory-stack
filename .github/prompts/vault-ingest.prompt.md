---
name: Vault Ingest
description: "Read a source file and distill 1-3 Knowledge Distillates into the Vault. Syntax: /vault-ingest [path] [domain]"
mode: agent
---

# Vault Ingest

Process a source file and extract distilled, reusable Knowledge Distillates for the Obsidian Vault.

## When to Use

When a source file contains relevant knowledge that:
- is too large or too raw to use directly
- will be repeatedly referenced
- gains utility through distillation

**Typical sources:**
- Articles and documents (Word, Markdown, PDF extracts)
- Meeting transcripts and notes
- Research results, external reports
- Documentation exports

## Input

```
/vault-ingest [path to source file] [domain]
```

**Examples:**
- `/vault-ingest inbox/docs/article-on-context-engineering.md engineering`
- `/vault-ingest inbox/meetings/2026-04-sprint-review.md process`

---

## Steps

### 1. Read Source File

Read the specified file completely.

**Immediate checks:**
- Does the file contain personal data (names, email addresses)? → Anonymize or flag
- Does it contain confidential data that shouldn't be committed? → Note that the vault is local (no Git risk)

### 2. Identify Snippet Candidates

Analyze the content: Which sections are **vault-worthy**?

Criteria:
- Reusable in future sessions
- Self-contained and understandable without the source file
- Not purely session-specific or ephemeral

**Threshold:** 1-3 snippets per source file. Better too few than too many weak snippets.

If no vault-worthy content is found → communicate clearly and abort.

### 3. Determine source_type Tag

| Source file type | Tag |
|---|---|
| Transcript, meeting notes | `source/meeting-extract` |
| External paper, article | `source/deep-research` |
| Issue tracker or wiki export | `source/system-export` |
| Manually written document | `source/human` |
| LLM-generated document | `source/llm-generated` |

### 4. Write Snippets to the Vault

For each candidate: Use the `vault_write` MCP tool.

| Parameter | Value |
|---|---|
| `title` | Title of the snippet |
| `body` | Distilled content with structure: Core Insight → Details → Relevance → Sources |
| `tags` | Domain tag + source tag + topical tags |
| `document_type` | `Knowledge Distillate` |
| `up` | `[[MOC_Start]]` |
| `related` | Wikilinks to related vault documents |
| `created_by` | `copilot` |

**Body structure:**
```markdown
# {Title}

## Core Insight
[1-3 sentences]

## Details
[More detailed explanation, context, examples]

## Relevance
[Why relevant for the project?]

## Sources
- Source file: {path}
- [Additional sources]
```

### 5. Sensitivity Check

Before completion, explicitly report:
- Were personal data found and handled?
- Does the snippet contain confidential information? (Vault is local, but check sensitivity anyway)

### 6. Completion

```
Ingest completed: {N} snippets created
  Source: {path}
  Created: {ID-1}, {ID-2}, ...
  Status: draft — searchable via vault_search
```

---

## Quality Note

Ingest snippets receive the tag `confidence/medium`. This is correct — the source file is the evidence, not the knowledge itself.
