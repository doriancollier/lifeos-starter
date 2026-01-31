---
title: "Skills"
created: "2025-12-02"
status: "active"
---

# Skills

Skills are specialized knowledge modules that Claude reads automatically when the context matches.

## How Skills Work

Skills are **model-invoked** — you don't explicitly call them. Claude detects when a skill is relevant and reads its instructions.

```
User: "Help me prepare for my meeting with Alex"
       ↓
Claude detects: meeting prep context
       ↓
Reads: meeting-prep skill + person-context skill
       ↓
Applies combined knowledge to respond
```

## Skill Structure

Skills live in `.claude/skills/[skill-name]/SKILL.md`:

```
.claude/skills/
├── daily-note/
│   └── SKILL.md
├── task-system/
│   └── SKILL.md
└── meeting-prep/
    └── SKILL.md
```

### SKILL.md Format

```markdown
---
description: "Brief description for skill discovery"
---

# Skill Name

## When to Activate

Describe the contexts where this skill applies.

## Instructions

Detailed instructions for Claude when this skill is active.

## Examples

Show example inputs and expected behavior.
```

## Skill Categories

### Daily Workflow

| Skill | Purpose |
|-------|---------|
| `daily-note` | Create and navigate daily notes (includes energy assessment, role awareness) |
| `vault-task-system` | A/B/C priority task management (includes leverage filtering, strategic lens) |
| `vault-task-sync` | Bidirectional sync between daily notes and projects |
| `work-logging` | Log progress with subtasks and timestamps (includes leverage assessment) |

### Calendar

| Skill | Purpose |
|-------|---------|
| `calendar-awareness` | Holidays, schedule overview, quarterly retreat scheduling (delegates birthdays) |
| `calendar-management` | Create, modify, end calendar events (includes protected time concepts) |
| `daily-timebox` | Create timeboxed focus blocks (includes 90-minute sprint structure) |
| `birthday-awareness` | Detect and manage birthday events |

### People

| Skill | Purpose |
|-------|---------|
| `person-context` | Relationship and communication info |
| `person-file-management` | Auto-create/update person files (includes learning profile for EF support) |
| `meeting-prep` | Gather context before meetings (includes pre-mortem consideration) |

### Planning

| Skill | Purpose |
|-------|---------|
| `goals-tracking` | Track goals and opportunities (includes first principles filter, asymmetry evaluation) |
| `project-status` | Project lifecycle management |
| `project-structure` | Standards for organizing project files and folders (naming, structure, templates) |
| `weekly-review` | Aggregate weekly patterns (includes Pareto check, energy audit, role check-in) |
| `weekly-aggregator` | Auto-aggregate daily data into rolling weekly doc |
| `context-switch` | Switch between company contexts |
| `planning-cadence` | Connect daily to weekly to monthly to quarterly to annual horizons |
| `strategic-thinking` | Second-order thinking, decision classification |
| `pre-mortem` | Guide pre-mortem exercises for major decisions and project starts |
| `energy-management` | 4-dimension energy tracking (physical, emotional, mental, spiritual) |

### Content

| Skill | Purpose |
|-------|---------|
| `historical-memory` | Capture biographical info |
| `personal-insight` | Detect and capture personal insights (routes breakthrough insights) |
| `personal-profile` | Manage owner's personal documents (resume, work history, etc.) |
| `document-generator` | Create printable documents |
| `goal-bingo` | Generate Goal Bingo cards |
| `habit-tracker` | Generate monthly habit tracking sheets |
| `writing-voice` | Write in {{user_first_name}}'s authentic voice (includes warmth prompts for INTJ communication) |

### Product

| Skill | Purpose |
|-------|---------|
| `product-management` | PM frameworks for PRDs, roadmaps, prioritization |

### File Processing

| Skill | Purpose |
|-------|---------|
| `inbox-processor` | Identify and route files in inbox |

### Health

| Skill | Purpose |
|-------|---------|
| `health-awareness` | Health data integration and coaching for daily planning (rings, sleep, body composition) |

### External Integrations

| Skill | Purpose |
|-------|---------|
| `audio-generator` | Generate speech audio using ElevenLabs (TTS, voice presets, SSML) |
| `email-reader` | Read emails from Mail.app via AppleScript |
| `reminders-integration` | Bidirectional sync with macOS Reminders (mobile/Siri) |

### Utilities

| Skill | Purpose |
|-------|---------|
| `obsidian-open` | Open files in Obsidian UI |
| `skill-manager` | Create, review, and maintain Claude Code skills |
| `operations` | Math, date calculations, and reliable computation |
| `proactive-suggestions` | Suggest `/board:advise`, `/system:learn`, `/system:update` when context matches |

### Advisor Skills

| Skill | Domain |
|-------|--------|
| `advisor-financial` | Personal finance |
| `advisor-business-strategy` | Business strategy |
| `advisor-ops-systems` | Operations |
| `advisor-health-energy` | Health and energy |
| `advisor-relationships` | Relationships |
| `advisor-parenting-family` | Family |
| `advisor-leadership-boundaries` | Leadership |
| `advisor-success-execution` | Execution |
| `advisor-decision-frameworks` | Decision-making |
| `advisor-legal-literacy` | Legal awareness |
| `advisor-librarian-context` | Context retrieval |

## Creating a New Skill

1. **Create directory:** `.claude/skills/[skill-name]/`
2. **Create SKILL.md** with frontmatter and instructions
3. **Test** by prompting Claude with relevant context
4. **Document** in CLAUDE.md skills table

### Template

```markdown
---
description: "One-line description for discovery"
---

# [Skill Name]

## Purpose

What this skill helps Claude do.

## When to Activate

- Trigger context 1
- Trigger context 2
- User asks about X

## Instructions

### Step 1: [Action]

Details...

### Step 2: [Action]

Details...

## Key Files

- `path/to/relevant/file.md`
- `path/to/another/file.md`

## Examples

**User:** "Example prompt"
**Expected behavior:** What Claude should do

## Notes

Additional context or caveats.
```

## Best Practices

1. **Be specific** about activation contexts
2. **Include examples** of expected behavior
3. **Reference key files** Claude should read
4. **Keep focused** — one skill per domain
5. **Link to other skills** when they should work together
