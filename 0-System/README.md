---
title: "LifeOS"
version: "0.5.0"
created: "2025-12-02"
updated: "2026-01-31"
status: "active"
---

# LifeOS

**Life Operating System** — An AI coaching system for personal and professional success.

> **Definition of Success**: "Becoming someone strong, loving, and courageous enough to protect what matters, while fully enjoying the journey."

## What is LifeOS?

LifeOS is an Obsidian vault architecture combined with Claude Code extensions (skills, commands, agents, hooks) that creates an **AI-coached system** for bridging the gap between your philosophy and daily action:

- **Level 10 Coaching** — A relentless challenger with 95+ prompts across 10 categories, asking hard questions, holding you accountable, and celebrating identity-consistent action
- **Planning Hierarchy** — Connected horizons from Annual → Quarterly → Monthly → Weekly → Daily, ensuring daily actions serve your mission
- **Thinking Frameworks** — First principles, inversion, second-order thinking, systems thinking, and mental models for better decisions
- **Strategic Decisions** — One-way vs two-way door classification, pre-mortems, asymmetric return evaluation
- **Retrospectives** — Structured reflection at daily, weekly, monthly, quarterly, and annual levels
- **Energy Management** — Four-dimension tracking (physical, emotional, mental, spiritual) with oscillation principles
- **Role Balance** — Track attention across roles (Father, Husband, Professional, Self) with failure mode awareness
- **Fear Tracking** — Daily fear commitment, facing, and logging to build courage systematically
- **Task Management** — Priority-based daily planning with A/B/C tasks and leverage filtering
- **Multi-Context Work** — Seamlessly switch between companies, projects, and life areas
- **Meeting Workflow** — Preparation, capture, and follow-up automation
- **Personal Board of Advisors** — Multi-perspective deliberation on important decisions
- **Calendar Integration** — Smart scheduling with context-aware timeboxing

## Core Philosophy

1. **Identity-First** — You are a thermostat, not a thermometer; set your state, don't react
2. **AI as Coach** — Claude Code acts as a Level 10 Relentless Challenger, not just an assistant
3. **One Source of Truth** — Each piece of information lives in exactly one place
4. **Structure Enables Freedom** — Clear organization reduces cognitive load
5. **Fear is the Compass** — Everything you want is on the other side of fear
6. **Renewal is Success** — Rest is not laziness; protect recovery time

## Quick Start

### For New Users

1. Clone the LifeOS template repository
2. Run `/setup:onboard` — The guided wizard will:
   - Gather your name, timezone, and preferences
   - Set up your companies and life areas
   - Configure your coaching intensity
   - Create your personal foundation
3. Start with `/daily:plan` for your first coached planning session
4. See [Getting Started Guide](guides/getting-started.md) for next steps

### Manual Setup (Alternative)

If you prefer manual configuration:
1. Edit files in `.user/` directory (identity, companies, coaching, integrations)
2. Run `/system:inject` to generate CLAUDE.md from templates
3. Run `/system:configure-hooks` to set up hooks based on your integrations
4. Set up your foundation in `2-Areas/Personal/foundation.md`
5. Create role documents in `2-Areas/Personal/Roles/`

### For Existing Users

See [Architecture](architecture.md) for system structure and [Patterns](patterns.md) for conventions.

### Key Files

| File | Purpose |
|------|---------|
| `.user/` | Your configuration (identity, integrations, coaching) - preserved during upgrades |
| `CLAUDE.md` | Generated from template using your `.user/` config |
| `CLAUDE.template.md` | Template for CLAUDE.md (updated during system upgrades) |
| `2-Areas/Personal/foundation.md` | Your identity, mission, vision, principles |
| `2-Areas/Personal/Roles/` | Individual role documents with growth edges |

## Documentation

### Core Concepts

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | How LifeOS is structured |
| [Patterns](patterns.md) | Conventions and patterns we follow |
| [Personalization](personalization.md) | How to customize for your context |
| [Roadmap](roadmap.md) | Future vision and priorities |
| [Changelog](changelog.md) | Version history |

### Components

| Component | Description |
|-----------|-------------|
| [Skills](components/skills.md) | Specialized knowledge modules (model-invoked) |
| [Commands](components/commands.md) | Slash commands for quick actions (user-invoked) |
| [Agents](components/agents.md) | Autonomous task executors (tool-invoked) |
| [Hooks](components/hooks.md) | Event-triggered automation (lifecycle events) |
| [Templates](components/templates.md) | Note templates for consistency |

### Workflow Guides

| Guide | Description |
|-------|-------------|
| [Daily Workflow](guides/daily-workflow.md) | Morning planning to evening review |
| [Task Management](guides/task-management.md) | The A/B/C priority system |
| [Task Sync](guides/task-sync.md) | Bidirectional sync between daily notes and projects |
| [Meeting Workflow](guides/meeting-workflow.md) | Prep → capture → follow-up |
| [Board of Advisors](guides/board-advisors.md) | Multi-perspective decision making |
| [Calendar Integration](guides/calendar-integration.md) | Smart scheduling and timeboxing |
| [Planning Horizons](guides/planning-horizons.md) | Annual → Quarterly → Monthly → Weekly → Daily |
| [Thinking Frameworks](guides/thinking-frameworks.md) | Mental models for better decisions |
| [Decision Making](guides/decision-making.md) | Structured decision processes |
| [Retrospectives](guides/retrospectives.md) | Learning from experience |
| [Getting Started](guides/getting-started.md) | New user onboarding |
| [Versioning & Upgrades](guides/versioning.md) | Version system and upgrade process |

## Self-Learning System

LifeOS can learn new capabilities through experimentation and codify them into the system:

```
/system:learn [what to learn]
```

**Examples**:
- `/system:learn learn how to interact with contacts using applescript`
- `/system:learn we successfully created calendar events with travel time - codify this`

**How it works**:
1. **Proactive mode**: Experiments to discover working approaches
2. **Retrospective mode**: Codifies behaviors that already worked
3. **Automatic logging**: Tracks learnings in `0-System/config/learning-log.md`

See [Learning Log](config/learning-log.md) for history of learned capabilities.

## Directory Structure

```
/
├── .user/             # YOUR CONFIG (preserved during upgrades)
│   ├── identity.yaml  # Name, timezone, personality
│   ├── companies.yaml # Company definitions
│   ├── coaching.yaml  # Coaching preferences
│   └── integrations.yaml # Enabled integrations
├── 0-System/          # LifeOS documentation (you are here)
├── 1-Projects/        # Active work with end dates
├── 2-Areas/           # Ongoing responsibilities (no end date)
├── 3-Resources/       # Reference materials
├── 4-Daily/           # Daily notes (YYYY-MM-DD.md)
├── 5-Meetings/        # Meeting notes by date
├── 6-People/          # Relationship management
├── 7-MOCs/            # Maps of Content
├── 8-Scratch/         # Temporary workspace
├── .claude/           # Claude Code extensions
│   ├── skills/        # Specialized knowledge
│   ├── commands/      # Slash commands
│   ├── agents/        # Autonomous agents
│   ├── hooks/         # Event automation
│   └── scripts/       # Configuration scripts
├── CLAUDE.template.md # Template (updated during upgrades)
└── CLAUDE.md          # Generated from template
```

## Version

Current version: **0.5.0**

See [Changelog](changelog.md) for version history and [Roadmap](roadmap.md) for planned features.

## Contributing

LifeOS is currently in development. See the [System-Productization](../1-Projects/Current/System-Productization/System-Productization.md) project for active work.

---

*LifeOS — Run your life, don't let it run you.*
