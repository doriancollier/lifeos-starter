---
title: "LifeOS Architecture"
created: "2025-12-02"
status: "active"
---

# LifeOS Architecture

This document describes how LifeOS is structured and how its components interact.

## Layers

LifeOS has six distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                 USER CONFIGURATION                       │
│         (.user/ - preserved during upgrades)             │
├─────────────────────────────────────────────────────────┤
│                    USER CONTEXT                          │
│         (CLAUDE.md - generated from templates)           │
├─────────────────────────────────────────────────────────┤
│                   IDENTITY LAYER                         │
│    (2-Areas/Personal/ - foundation, roles, practice)     │
├─────────────────────────────────────────────────────────┤
│                    CONTENT LAYER                         │
│     (1-Projects, 2-Areas, 4-Daily, 5-Meetings, etc.)    │
├─────────────────────────────────────────────────────────┤
│                  EXTENSION LAYER                         │
│        (.claude/ - skills, commands, agents, hooks)      │
├─────────────────────────────────────────────────────────┤
│               DOCUMENTATION & TEMPLATES                  │
│     (0-System/, CLAUDE.template.md, coaching.template)   │
└─────────────────────────────────────────────────────────┘
```

### Layer 0: User Configuration (.user/)

Your personal configuration that survives system upgrades:
- `identity.yaml` — Name, timezone, personality, family
- `companies.yaml` — Company definitions with contacts
- `coaching.yaml` — Coaching intensity and preferences
- `integrations.yaml` — Which integrations are enabled (Reminders, Health, etc.)
- `health.yaml` — Health export path and targets
- `calendars.yaml` — Calendar configuration

**Key property:** Never modified by system upgrades.

**How it works:**
```
.user/*.yaml ──┬──> inject_placeholders.py ──> CLAUDE.md
               │
               └──> configure_hooks.py ──> .claude/settings.json
```

**Commands:**
- `/system:inject` — Regenerate CLAUDE.md from templates
- `/system:configure-hooks` — Regenerate settings.json
- `/system:upgrade` — Full upgrade workflow

### Layer 1: Documentation & Config (0-System/)

Product documentation and system configuration:
- Architecture and patterns
- Component documentation (skills, commands, agents, hooks)
- User guides (daily workflow, task management, calendar, etc.)
- Roadmap and changelog

**Note:** User-specific configuration now lives in `.user/` (Layer 0), not in `0-System/`.

**Shareable:** Yes — core docs are generic.

### Layer 2: Extensions (.claude/)

The implementation layer that makes LifeOS work:

| Component | Invocation | Purpose |
|-----------|------------|---------|
| **Skills** | Model-invoked | Specialized knowledge Claude reads automatically |
| **Commands** | User-invoked | Slash commands for explicit actions |
| **Agents** | Tool-invoked | Autonomous task executors |
| **Hooks** | Event-triggered | Lifecycle automation |

**Shareable:** Mostly — core components are generic, some need personalization.

### Layer 3: Content (1-8 directories)

Your actual content organized by the PARA method:

| Directory | Purpose | PARA Category |
|-----------|---------|---------------|
| `1-Projects/` | Active work with end dates | Projects |
| `2-Areas/` | Ongoing responsibilities | Areas |
| `3-Resources/` | Reference materials | Resources |
| `4-Daily/` | Daily notes | (Time-based) |
| `5-Meetings/` | Meeting notes | (Time-based) |
| `6-People/` | Relationship management | Resources |
| `7-MOCs/` | Maps of Content | Resources |
| `8-Scratch/` | Temporary workspace | (Inbox) |

**Shareable:** No — this is your personal content.

### Layer 4: Identity (2-Areas/Personal/)

Your personal foundation and identity:
- `foundation.md` — Identity statements, mission, vision, principles, commandments
- `daily-practice.md` — The core Daily Practice audio script
- `Roles/` — Individual role documents with character aspirations and growth edges
- `context.md` — Decision-making patterns, about me

**Key files:**
- `foundation.md` — Who you are and what you stand for
- `Roles/Father.md`, `Roles/Husband.md`, `Roles/Professional.md`, etc.

**Shareable:** No — this is your identity.

### Layer 5: User Context (CLAUDE.md + .claude/rules/)

Quick reference, coaching persona, and modular rules:
- `CLAUDE.md` — Core identity, structure, quick references (~160 lines)
- `.claude/rules/` — Detailed instructions loaded automatically:
  - `coaching.md` — Full coaching questions and prompts (~200 lines)
  - `components.md` — Complete skills, commands, agents, hooks tables (~240 lines)
  - `questioning.md` — AskUserQuestion defaults, option quality, recommendations (~100 lines)

This modular structure keeps CLAUDE.md lean while providing comprehensive guidance through rule files that Claude loads automatically.

**Shareable:** Template yes, content no.

## Information Flow

```
                    ┌──────────────┐
                    │    User      │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │      CLAUDE.md          │
              │   (context injection)   │
              └────────────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌────▼────┐
    │ Commands │      │  Skills   │     │  Hooks  │
    │ (user)   │      │ (model)   │     │ (event) │
    └────┬────┘      └─────┬─────┘     └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │    Agents    │
                    │ (autonomous) │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │     Content Layer       │
              │ (Projects, Daily, etc.) │
              └─────────────────────────┘
```

## Component Interaction Model

### Skills (Model-Invoked)

Skills are knowledge modules that Claude reads autonomously when the context matches.

```
User: "What's on my calendar today?"
       ↓
Claude detects calendar-related context
       ↓
Reads calendar-awareness skill
       ↓
Applies skill instructions to respond
```

**Key characteristics:**
- Claude decides when to use them
- Provide specialized knowledge
- No explicit user invocation

### Commands (User-Invoked)

Slash commands are explicit actions triggered by the user.

```
User: "/daily:plan"
       ↓
Command file loaded as prompt
       ↓
Claude executes the workflow
       ↓
Produces structured output
```

**Key characteristics:**
- User explicitly invokes
- Defined workflows
- Predictable outcomes

### Agents (Tool-Invoked)

Agents are spawned via the Task tool for complex, isolated work.

```
Claude: needs deep vault exploration
       ↓
Spawns vault-explorer agent
       ↓
Agent works autonomously
       ↓
Returns results to main Claude
```

**Key characteristics:**
- Separate context window
- Autonomous execution
- Returns final report

**Orchestrator Pattern:**
Commands can act as orchestrators, delegating context-heavy analysis to agents while keeping user interaction in main context. See the `orchestration-patterns` skill for detailed guidance on when and how to use this pattern.

### Hooks (Event-Triggered)

Hooks run automatically at lifecycle events.

```
Event: SessionStart
       ↓
session-context-loader.py runs
       ↓
Today's context injected
       ↓
Claude starts with awareness
```

**Key characteristics:**
- Deterministic execution
- Can block operations
- No Claude involvement in trigger

## Directory Enforcement

LifeOS enforces content placement through the `directory-guard` hook:

| Content Type | Required Location |
|--------------|-------------------|
| Daily notes | `4-Daily/` |
| Meeting notes | `5-Meetings/YYYY/MM-Month/` |
| Person files | `6-People/` |
| Templates | `3-Resources/Templates/` |
| Projects | `1-Projects/` |

This ensures consistency and predictable AI navigation.

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ SessionStart                                             │
│  ├─ session-context-loader.py                           │
│  │   └─ Today's tasks, meetings, energy, focus areas    │
│  ├─ reminders-session-sync.py                           │
│  │   └─ Pull Reminders completions to daily note        │
│  └─ health-session-sync.py                              │
│      └─ Sync health data from Health Auto Export        │
├─────────────────────────────────────────────────────────┤
│ UserPromptSubmit                                         │
│  ├─ prompt-timestamp.py                                 │
│  └─ Current time injected                               │
├─────────────────────────────────────────────────────────┤
│ PreToolUse                                               │
│  ├─ directory-guard.py (Write/Edit)                     │
│  │   └─ BLOCKS wrong directory writes                   │
│  └─ calendar-protection.py (Calendar)                   │
│      └─ BLOCKS unconfirmed event changes                │
├─────────────────────────────────────────────────────────┤
│ PostToolUse                                              │
│  ├─ frontmatter-validator.py (Write/Edit)               │
│  ├─ task-format-validator.py (Write/Edit)               │
│  ├─ task-sync-detector.py (Write/Edit)                  │
│  │   └─ Queue task syncs for reconciliation             │
│  └─ reminders-task-detector.py (Write/Edit)             │
│      └─ Push new tasks to macOS Reminders               │
└─────────────────────────────────────────────────────────┘
```

## Extension Points

LifeOS is designed for extension:

1. **New Skills** — Add to `.claude/skills/[name]/SKILL.md`
2. **New Commands** — Add to `.claude/commands/[namespace]/[name].md`
3. **New Agents** — Add to `.claude/agents/[name].md`
4. **New Hooks** — Add to `.claude/hooks/` and configure in settings
5. **New Templates** — Add to `3-Resources/Templates/`

See [Patterns](patterns.md) for conventions when extending.

## Infrastructure Layer (Future)

Beyond the core vault layers, LifeOS includes infrastructure for background processing and multi-channel access:

### Background Tasks (tasks/)

Scheduled processes that run independently via launchd:

| Component | Purpose |
|-----------|---------|
| `tasks/heartbeat/` | Periodic vault health checks |
| `tasks/cron/` | Scheduled automation jobs (future) |
| `tasks/oneshot/` | Deferred one-time tasks (future) |

### Data Management

External data flows through three directories:

| Directory | Purpose | Git? | Backup? |
|-----------|---------|------|---------|
| `integrations/` | Import scripts and connectors | Yes | Yes |
| `data/` | Imported external data | No | Yes |
| `state/` | Ephemeral runtime state | No | No |

**Data flow:**
```
External Source → integrations/[name]/importer → data/[name]/
                                    ↓
                         .claude/skills/ reads data
```

### Gateway (Future)

Multi-channel access layer:
```
gateway/
├── src/
│   ├── server/      # REST API + WebSocket
│   └── channels/    # Channel adapters (web, telegram, slack)
```

### User Extensions

User-added functionality mirrors core structure:
```
extensions/
├── skills/          # User skills
├── commands/        # User commands
├── channels/        # User channel adapters
├── tasks/           # User background tasks
└── integrations/    # User data integrations
```

See [guides/directory-structure.md](guides/directory-structure.md) for complete architecture details.
