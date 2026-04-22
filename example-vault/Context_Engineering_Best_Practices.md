---
id: KB-Example-001
title: Context Engineering Best Practices
document_type: Knowledge Distillate
tags:
  - engineering
  - context-engineering
  - best-practices
  - status/published
aliases: []
up: "[[MOC_Start]]"
related:
  - "[[KB-Example-002]]"
created_by: human
created: "2026-01-15"
---

# Context Engineering Best Practices

## Core Insight

Context engineering is the discipline of structuring your codebase, instructions, and workflow so that AI coding assistants receive the right information at the right time. It's not about more context — it's about better context.

## Details

### File Path as Signal

AI assistants use file paths to infer intent. `src/auth/middleware.ts` communicates more than `src/utils/m.ts`. Choose paths that describe what the code does.

### Colocate Related Code

Keep components, tests, types, and helpers together. When one search finds everything related to a feature, the AI can reason about the full picture.

### Explicit Types Over Inference

Type annotations are context. `function getUser(id: string): Promise<User>` tells the AI more than `function getUser(id)`. Every annotation is a hint about the domain model.

### Strategic Comments

At the top of complex modules, describe the flow or purpose briefly. These comments act as anchors — the AI reads them first and uses them to frame the rest of the file.

### Open Tabs as Context

VS Code Copilot uses open tabs as context signals. Working on authentication? Keep auth-related files open. This is free context injection.

## Sources

- Practical experience with GitHub Copilot in large codebases
- VS Code Copilot documentation on context management
