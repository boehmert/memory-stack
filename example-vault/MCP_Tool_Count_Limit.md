---
id: KB-Example-002
title: MCP Tool Count Limit — Practical Findings
document_type: Knowledge Distillate
tags:
  - engineering
  - mcp
  - tools
  - status/published
aliases: []
up: "[[MOC_Start]]"
related:
  - "[[KB-Example-001]]"
  - "[[KB-Example-003]]"
created_by: human
created: "2026-02-10"
---

# MCP Tool Count Limit — Practical Findings

## Core Insight

When an AI agent has access to too many MCP tools (>30–40), tool selection quality degrades. The model spends tokens reasoning about which tool to use instead of solving the problem. Fewer, well-described tools outperform a large catalogue.

## Details

### The Problem

Each MCP tool definition consumes context window space — typically 200-500 tokens per tool (name, description, input schema). With 50 tools, that's 10k-25k tokens just for tool definitions, leaving less room for actual work.

More critically, the model's tool selection accuracy drops. With 10 tools, it almost always picks the right one. With 40+, it starts picking plausible but wrong tools, or invents tool names that don't exist.

### Practical Limits

| Tool Count | Selection Quality | Context Cost |
|---|---|---|
| 1-10 | Excellent | Negligible |
| 10-20 | Good | Manageable |
| 20-30 | Acceptable | Noticeable |
| 30+ | Degraded | Significant |

### Mitigation Strategies

1. **Profile-based loading**: Only load tools relevant to the current task (e.g. `--profile jira` vs `--profile confluence`)
2. **Clear descriptions**: A good tool description reduces selection errors more than removing tools
3. **Deferred loading**: VS Code supports lazy-loading tools — declare them but only activate on demand
4. **Consolidate**: Merge similar tools (e.g. one `search` tool with a `source` parameter instead of `search_jira`, `search_confluence`, `search_vault`)

## Sources

- Observed in production with Atlassian MCP server (Jira + Confluence combined)
- Anthropic documentation on tool use best practices
