---
title: "LifeOS Roadmap"
created: "2025-12-02"
status: "active"
---

# LifeOS Roadmap

Vision and priorities for LifeOS development.

## Vision

LifeOS should be a system that anyone can adopt to manage their life with AI assistance. The core framework is generic; personalization is layered on top.

## Current State (v0.5.0)

### What Exists

**Core Infrastructure:**
- [x] Directory structure (0-8 numbered folders)
- [x] CLAUDE.md configuration
- [x] Hook system (session context, validation, protection)
- [x] AI Coaching persona (Level 10 Relentless Challenger)
- [x] Foundation files (identity, mission, vision, roles)

**Skills (41):**
- [x] Daily workflow (daily-note, task-system, work-logging, task-sync)
- [x] Calendar (calendar-awareness, calendar-management, daily-timebox, birthday-awareness)
- [x] People (person-context, person-file-management, meeting-prep)
- [x] Planning (goals-tracking, project-status, planning-cadence, strategic-thinking, pre-mortem, energy-management)
- [x] Personal Board of Advisors (11 advisor skills)
- [x] Specialized (document-generator, historical-memory, personal-insight, writing-voice)
- [x] External (email-reader, reminders-integration)

**Commands (48):**
- [x] Daily namespace (/daily:note, /daily:plan, /daily:tasks, /daily:timebox, /daily:eod, etc.)
- [x] Meeting namespace (/meeting:prep, /meeting:ab, /meeting:144, /meeting:emh)
- [x] Create namespace (/create:person, /create:project, /create:trip, /create:gifts, /create:bingo)
- [x] Context namespace (/context:ab, /context:144, /context:emh, /context:personal)
- [x] System namespace (/system:ask, /system:update, /system:review, /system:learn)
- [x] Board namespace (/board:advise)
- [x] Goals namespace (/goals:status, /goals:review, /goals:opportunity)
- [x] Planning namespace (/annual:plan, /annual:review, /quarter:plan, /quarter:review, /monthly:plan, /monthly:review, /weekly:review)
- [x] Retro namespace (/retro:weekly, /retro:monthly, /retro:quarterly)
- [x] Other (/project:status, /roadmap:status, /inbox:process, /reminders:refresh, /personal:audit, /strategic:decide, /premortem:run, /partner:stateofunion, /update)

**Agents (13):**
- [x] vault-explorer, task-reviewer, context-isolator
- [x] relationship-manager, research-expert, product-manager, email-processor
- [x] Personal Board personas (5 advisor agents)
- [x] Agent resumption pattern for multi-step workflows

**Hooks (11):**
- [x] session-context-loader, reminders-session-sync, prompt-timestamp
- [x] directory-guard, calendar-protection
- [x] frontmatter-validator, task-format-validator, task-sync-detector, reminders-task-detector
- [x] git-task-sync-detector, auto-git-backup

### What's Missing

**Documentation:**
- [ ] Complete 0-System/ documentation
- [ ] Component guides (skills, commands, agents, hooks)
- [ ] Workflow guides (daily, meeting, calendar)
- [ ] Personalization guide

**Shareability:**
- [ ] Separate personal config from generic system
- [ ] Create starter template
- [ ] Onboarding workflow

---

## Phase 1: Documentation (Mostly Complete)

**Goal:** Complete product documentation so the system is understandable.

### Deliverables

- [x] **Architecture docs** — `0-System/architecture.md`
- [x] **Patterns guide** — `0-System/patterns.md`
- [x] **Component documentation:**
  - [x] Skills guide — `0-System/components/skills.md`
  - [x] Commands guide — `0-System/components/commands.md`
  - [x] Agents guide — `0-System/components/agents.md`
  - [x] Hooks guide — `0-System/components/hooks.md`
  - [x] Templates guide — `0-System/components/templates.md`
- [x] **Workflow guides:**
  - [x] Daily workflow — `0-System/guides/daily-workflow.md`
  - [x] Task management — `0-System/guides/task-management.md`
  - [x] Meeting workflow — `0-System/guides/meeting-workflow.md`
  - [x] Board of Advisors — `0-System/guides/board-advisors.md`
  - [x] Calendar integration — `0-System/guides/calendar-integration.md`
- [x] **Additional guides:**
  - [x] Task sync — `0-System/guides/task-sync.md`
  - [x] Planning horizons — `0-System/guides/planning-horizons.md`
  - [x] Decision making — `0-System/guides/decision-making.md`
  - [x] Thinking frameworks — `0-System/guides/thinking-frameworks.md`
  - [x] Retrospectives — `0-System/guides/retrospectives.md`
  - [x] Personal documents — `0-System/guides/personal-documents.md`

### Success Criteria

A new user can read 0-System/ and understand:
1. What LifeOS is ✓
2. How it's structured ✓
3. How to use each component type ✓
4. How to extend it ✓

---

## Phase 2: Personalization Layer

**Goal:** Cleanly separate personal config from generic system.

### Deliverables

- [ ] **Personalization guide** — How to customize for your context
- [ ] **Template CLAUDE.md** — Generic starting point
- [ ] **Example configurations** — Sample company contexts
- [ ] **Migration guide** — Moving from generic to personalized

### Success Criteria

The system can be cleanly divided into:
1. **Generic core** (shareable)
2. **Personal config** (user-specific)

---

## Phase 3: Starter Kit

**Goal:** Package for others to adopt.

### Deliverables

- [ ] **Starter repository** — Clean starting point
- [ ] **Onboarding workflow** — Guided setup
- [ ] **Quick start guide** — Get running in 30 minutes
- [ ] **Video walkthrough** — Demo of key features

### Success Criteria

Someone new can:
1. Clone the starter repo
2. Follow the onboarding
3. Have a working LifeOS in < 1 hour

---

## Phase 4: Community & Polish

**Goal:** Enable community contribution and polish rough edges.

### Deliverables

- [ ] **Contributing guide** — How to add skills, commands, etc.
- [ ] **Skill marketplace** concept — Share extensions
- [ ] **Bug fixes and refinements**
- [ ] **Performance optimization**

### Success Criteria

- Community can contribute extensions
- Known issues are resolved
- System feels polished

---

## Future Ideas (Backlog)

### Features

- **Voice integration** — Dictate updates
- **Mobile companion** — Quick capture on phone
- **Analytics dashboard** — Track patterns over time
- **Habit tracking** — Goal Bingo automation
- **Email integration** — Process emails into tasks

### Technical

- **Test suite** — Automated testing for hooks
- **Schema validation** — Stricter frontmatter enforcement
- **Performance profiling** — Large vault optimization
- **Multi-vault support** — Work + personal separation

### Integrations

- **Linear** — Sync with project management
- **Slack** — Capture from messages
- **Notion** — Import existing content
- **Todoist/Things** — Task sync

---

## Version History

| Version | Date | Milestone |
|---------|------|-----------|
| 0.5.0 | 2026-01-31 | Upgrade system with version checking |
| 0.4.0 | 2025-12-31 | User/system separation, template injection |
| 0.3.0 | 2025-12-03 | Task sync system, context isolator agent |
| 0.2.0 | 2025-12-03 | File inbox system, task extraction |
| 0.1.0 | 2025-12-02 | Initial productization started |

See [Changelog](changelog.md) for detailed changes.
