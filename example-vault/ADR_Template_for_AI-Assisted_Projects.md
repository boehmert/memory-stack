---
id: KB-Example-003
title: ADR Template for AI-Assisted Projects
document_type: Knowledge Distillate
tags:
  - architecture
  - adr
  - template
  - status/published
aliases: []
up: "[[MOC_Start]]"
related:
  - "[[KB-Example-001]]"
created_by: human
created: "2026-03-01"
---

# ADR Template for AI-Assisted Projects

## Core Insight

Architecture Decision Records (ADRs) serve double duty in AI-assisted workflows: they document decisions for humans AND provide structured context for AI agents. An ADR with clear status, constraints, and alternatives helps the AI avoid re-proposing rejected ideas.

## Details

### Recommended Template

```markdown
---
id: ADR-001
title: "Decision Title"
status: PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED
created: 2026-01-01
supersedes: null
superseded_by: null
---

# ADR-001: Decision Title

## Status
PROPOSED

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Constraints
- What technical constraints apply?
- What organizational constraints apply?
- What timeline constraints apply?

## Alternatives Considered
### Alternative A
- Pro: ...
- Con: ...

### Alternative B
- Pro: ...
- Con: ...

## Consequences
What becomes easier or harder as a result of this decision?

## Review Notes
[Added during review — captures discussion points and concerns]
```

### Why This Matters for AI

- **Status field**: Prevents the AI from suggesting approaches that were already rejected
- **Constraints section**: Gives the AI guardrails without needing to re-derive them
- **Alternatives Considered**: Shows the decision space — the AI can reference these instead of re-exploring
- **YAML frontmatter**: Machine-readable, searchable via vault tools

## Sources

- Michael Nygard's original ADR proposal
- Adapted for AI-assisted workflows based on practical experience
