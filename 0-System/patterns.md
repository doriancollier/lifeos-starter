---
title: "LifeOS Patterns"
created: "2025-12-02"
status: "active"
---

# LifeOS Patterns

Conventions and patterns followed throughout the system.

## Core Principles

### 1. One Source of Truth

Every piece of information lives in exactly one canonical location. Link liberally, but don't duplicate content.

**Good:**
```markdown
See [[Alex Smith]] for relationship details.
```

**Bad:**
```markdown
Alex Smith is the CPO at {{company_1_name}}. They prefer Slack...
(duplicating info that lives in the person file)
```

### 2. Explicit Over Implicit

Make context explicit rather than assuming Claude will figure it out.

**Good:**
```markdown
- [ ] Call passport office - Company: Personal
```

**Bad:**
```markdown
- [ ] Call passport office
(unclear which context this belongs to)
```

### 3. Atomic Notes

Each note focuses on one well-defined concept. Rich linking creates relationships.

### 4. Progressive Disclosure

Start with summary, expand with details. Most important information first.

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Daily notes | `YYYY-MM-DD.md` | `2025-12-02.md` |
| Meeting notes | `YYYY-MM-DD-title.md` | `2025-12-02-product-sync.md` |
| Person files | `FirstName-LastName.md` | `Alex-Smith.md` |
| Projects | `Project-Name.md` | `AssetOps.md` |
| Skills | `skill-name/SKILL.md` | `daily-note/SKILL.md` |
| Commands | `command-name.md` | `plan.md` |
| Agents | `agent-name.md` | `vault-explorer.md` |

### Directories

- Use lowercase with hyphens for multi-word: `recurring-meeting-templates/`
- Exception: PARA directories use Title-Case: `1-Projects/`, `2-Areas/`
- Skill directories match skill name: `.claude/skills/daily-note/`

## Frontmatter Standards

### Required Fields

Every note should have:

```yaml
---
title: "Note Title"
created: "YYYY-MM-DD"
---
```

### Common Optional Fields

```yaml
---
title: "Note Title"
created: "2025-12-02"
updated: "2025-12-02"
status: "active"           # active, archived, draft
company: "{{company_1_name}}"      # {{company_1_name}}, {{company_2_name}}, EMC, Personal
tags: ["tag1", "tag2"]
---
```

### Type-Specific Fields

**Person files:**
```yaml
---
name: "Alex Smith"
company: "{{company_1_name}}"
role: "CPO"
relationship: "boss, colleague"
last_contact: "2025-12-01"
---
```

**Project files:**
```yaml
---
title: "Project Name"
status: "active"           # backlog, active, completed, cancelled
company: "{{company_2_name}}"
supports_goal: "Goal Name"
goal_alignment: "high"     # high, medium, low
---
```

**Meeting notes:**
```yaml
---
title: "Meeting Title"
date: "2025-12-02"
company: "{{company_1_name}}"
attendees: ["Person 1", "Person 2"]
type: "sync"               # sync, planning, decision, review
---
```

## Task Patterns

### Priority System

| Priority | Symbol | Meaning | Daily Limit |
|----------|--------|---------|-------------|
| A | `🔴` | Must complete today | 1-5 (numbered) |
| B | `🟡` | Should complete today | No limit |
| C | `🟢` | Nice to have | No limit |
| Blocked | `🔵` | Waiting on external | N/A |
| Scheduled | `📅` | Future-dated | N/A |

### Task Format

```markdown
- [ ] 🔴1. Task description - Company: Context
- [ ] 🟡 Another task - Company: Context
- [ ] 🟢 Nice to have task
- [ ] 🔵 Blocked: Waiting on X - Company: Context
- [ ] 🟡 Task with due date 📅 2025-12-15
```

### Nested Subtasks

For tracking progress within a task:

```markdown
- [ ] 🔴1. Main task - Company: Personal
  - [x] Subtask completed
  - [ ] Subtask pending
  - [ ] Another subtask
```

## Linking Patterns

### Internal Links

Use Obsidian link syntax:

```markdown
[[Note Name]]              # Basic link
[[Note Name|Display Text]] # Aliased link
[[Note Name#Section]]      # Section link
```

### Person References

Always link to person files:

```markdown
Meeting with [[Alex Smith]] about the roadmap.
```

### Project References

Link to projects for context:

```markdown
This task is part of [[AssetOps]].
```

### Goal-Project Linking

Projects aligned with annual goals should have bidirectional links for navigation:

**Project → Annual Plan** (in `## Related` section):

```markdown
## Related

- [[2026]] - Goal 4: Father Presence
- [[Other-Related-Note]]
```

**Annual Plan → Projects** (after each goal's `**Trade-off**:` line):

```markdown
**Trade-off**: Leadership over "cool friend" dynamic
**Projects**: [[{{child_name}}-Drivers-License]], [[{{child_name}}-Summer-2026]]
```

This complements the frontmatter fields (`supports_goal`, `goal_alignment`) with wikilinks for Obsidian graph navigation and backlink discovery.

## Company Context Pattern

### Identifying Context

Every work-related item should identify its company:

```markdown
- [ ] Task description - Company: {{company_1_name}}
```

### Context Files

Each company has a context file in `2-Areas/`:

```
2-Areas/
├── {{company_1_name}}/context.md
├── {{company_2_name}}/context.md
├── {{company_3_name}}/context.md
└── Personal/context.md
```

### Context Switching

Use `/context:[company]` commands to load company context:

```
/context:ab      # Load {{company_1_name}} context
/context:144     # Load {{company_2_name}} context
/context:emh     # Load {{company_3_name}} context
/context:personal # Load personal context
```

## Callout Patterns

### AI Context Callouts

For information specifically useful to Claude:

```markdown
> [!ai-context]
> Key information that helps AI understand this note's significance.
```

### Standard Obsidian Callouts

```markdown
> [!note]
> General notes

> [!warning]
> Important cautions

> [!tip]
> Helpful suggestions

> [!question]
> Open questions to resolve
```

## Extension Patterns

### Creating a New Skill

1. Create directory: `.claude/skills/[skill-name]/`
2. Create `SKILL.md` with required frontmatter
3. Document when Claude should use it
4. Add to CLAUDE.md skills table

### Creating a New Command

1. Decide on namespace: `daily/`, `meeting/`, `create/`, etc.
2. Create `.claude/commands/[namespace]/[command].md`
3. Include argument documentation
4. Add to CLAUDE.md commands table

### Creating a New Agent

1. Create `.claude/agents/[agent-name].md`
2. Define the agent's purpose and tools
3. Specify when to use it
4. Add to CLAUDE.md agents table

### Creating a New Hook

1. Create script in `.claude/hooks/`
2. Configure in `~/.claude/settings.json`
3. Document the trigger event
4. Add to CLAUDE.md hooks table

## Anti-Patterns

### Don't Do This

1. **Duplicate content** — Link instead of copying
2. **Orphan notes** — Every note should be linked from somewhere
3. **Deep nesting** — Prefer flat structure with links
4. **Inconsistent frontmatter** — Follow the type-specific templates
5. **Missing context** — Always identify company for work items
6. **Overly broad notes** — Split into atomic pieces
7. **Hardcoded dates** — Use relative references when possible
