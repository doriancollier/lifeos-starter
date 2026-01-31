---
title: "LifeOS Personalization"
created: "2025-12-02"
status: "draft"
---

# LifeOS Personalization

How to customize LifeOS for your context.

> [!note]
> This guide is a draft. It will be expanded as part of Phase 2 of the roadmap.

## Overview

LifeOS separates **generic system** from **personal configuration**:

| Layer | What It Contains | Shareable? |
|-------|-----------------|------------|
| 0-System/ | Product documentation | Yes |
| .claude/ | Skills, commands, agents, hooks | Mostly |
| CLAUDE.md | Your identity and context | No |
| 2-Areas/ | Your companies and responsibilities | No |
| 6-People/ | Your relationships | No |

## CLAUDE.md Configuration

The primary personalization point is `CLAUDE.md`. This file tells Claude who you are and how to work with you.

### Required Sections

**Repository Overview:**
```markdown
## Repository Overview

This is an Obsidian vault serving as a personal knowledge management
system and AI agent memory for [Your Name].
```

**User Context:**
```markdown
## Key Contexts

### Companies
- **[Company 1]**: Description and your role
- **[Company 2]**: Description and your role

### User Context
- Name: [Your Name]
- Location: [City, State] ([Timezone])
- Working style: [Your preferences]
```

### Optional Sections

- Personal profile reference
- Key people
- Custom workflows
- Integration notes

## Company Contexts

Each company/life area gets a context file in `2-Areas/`:

```
2-Areas/
├── [Company1]/
│   └── context.md
├── [Company2]/
│   └── context.md
└── Personal/
    └── context.md
```

### Context File Template

```markdown
---
title: "[Company] Context"
type: "company-context"
---

# [Company] Context

## Overview
What this company/area is about.

## Key People
- [[Person 1]] - Role
- [[Person 2]] - Role

## Current Focus
What you're working on here.

## Processes
How work gets done.

## AI Guidance
> [!ai-context]
> Notes to help Claude understand this context.
```

## Calendar Configuration

If using Google Calendar integration:

1. List your calendars in CLAUDE.md
2. Define calendar selection logic
3. Set up context windows for timeboxing

## Extending the System

### Adding Personal Skills

Create skills in `.claude/skills/` that are specific to your workflow.

### Custom Commands

Add commands in `.claude/commands/` for your repeated actions.

### Personal Agents

Define agents in `.claude/agents/` for your complex workflows.

---

## Migration Path

> [!note]
> Detailed migration guide coming in Phase 2.

For now:

1. Start with the generic template
2. Fill in CLAUDE.md with your context
3. Create company context files
4. Set up person files for key relationships
5. Begin using daily notes
