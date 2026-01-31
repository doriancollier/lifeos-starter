---
title: "Commands"
created: "2025-12-02"
status: "active"
---

# Commands

Slash commands are explicit actions triggered by the user.

## How Commands Work

Commands are **user-invoked** — you explicitly type them to trigger a workflow.

```
User: /daily:plan
       ↓
Command file loaded as prompt
       ↓
Claude executes the workflow
       ↓
Produces structured output
```

## Command Structure

Commands live in `.claude/commands/[namespace]/[name].md`:

```
.claude/commands/
├── daily/          # Daily workflow (plan, tasks, eod, etc.)
├── tasks/          # Task management (due)
├── meeting/        # Meeting prep and notes (prep, create, ab, sync, process)
├── create/         # Create notes (person, project, trip, gifts, bingo)
├── context/        # Load company context (load, ab, personal)
├── system/         # System management (ask, update, review, learn)
├── skill/          # Skill management (create, audit, list)
├── board/          # Board of Advisors (advise)
├── goals/          # Goals management (status, review, opportunity)
├── project/        # Project management (status)
├── roadmap/        # Product roadmaps (status)
├── inbox/          # Inbox processing (process)
├── reminders/      # Reminders integration (refresh)
├── personal/       # Personal profile (audit)
├── annual/         # Annual planning (plan, review)
├── quarter/        # Quarterly planning (plan, review)
├── monthly/        # Monthly planning (plan, review)
├── weekly/         # Weekly review (review, reflect)
├── health/         # Health data (sync)
├── retro/          # Retrospectives (weekly, monthly, quarterly)
├── premortem/      # Pre-mortem exercises (run)
├── strategic/      # Strategic decisions (decide)
├── partner/        # Relationship (stateofunion)
└── update.md       # Universal smart capture
```

## Command Namespaces

### Daily (`/daily:*`)

| Command | Purpose |
|---------|---------|
| `/daily:note` | Create/open today's daily note |
| `/daily:plan` | Morning planning workflow (brain dump → calendar review → horizon connections → coached planning) |
| `/daily:tasks` | Review open tasks |
| `/daily:capture [text]` | Quick capture to daily note |
| `/daily:timebox` | Create timeboxed focus blocks |
| `/daily:standup` | Generate standup summary |
| `/daily:eod` | End-of-day review (includes micro-retro) |

### Tasks (`/tasks:*`)

| Command | Purpose |
|---------|---------|
| `/tasks:due` | Show tasks by due date (overdue, today, upcoming) |

### Meeting (`/meeting:*`)

| Command | Purpose |
|---------|---------|
| `/meeting:sync` | Import meetings from SuperNormal |
| `/meeting:process [path]` | Process meeting notes with AI context, extract insights |
| `/meeting:prep [name]` | Prepare context for meeting |
| `/meeting:create [company] [title]` | Create meeting note for any company (ab, 144, emh, personal) |
| `/meeting:ab [title]` | Shortcut: Create {{company_1_name}} meeting note |

### Create (`/create:*`)

| Command | Purpose |
|---------|---------|
| `/create:person [name]` | Look up or create person note |
| `/create:project [name]` | Create new project |
| `/create:trip [name]` | Create trip planning project |
| `/create:gifts [occasion]` | Create gift planning project |
| `/create:bingo [year] [month?]` | Generate Goal Bingo cards |
| `/create:habits [month] [year?]` | Generate monthly habit tracker |
| `/create:song [name]` | Create song project with lyrics/prompts structure |

### Context (`/context:*`)

| Command | Purpose |
|---------|---------|
| `/context:load [company]` | Load context for any company (ab, 144, emh, personal) |
| `/context:ab` | Shortcut: Load {{company_1_name}} context |
| `/context:personal` | Shortcut: Load personal context |

### System (`/system:*`)

| Command | Purpose |
|---------|---------|
| `/system:ask [question]` | Ask how to do something |
| `/system:update [description]` | Add/update processes |
| `/system:review [area]` | Review processes |
| `/system:learn [topic]` | Learn through experimentation, codify results |
| `/system:inject` | Regenerate CLAUDE.md and coaching.md from templates |
| `/system:configure-hooks` | Regenerate settings.json from .user/integrations.yaml |
| `/system:upgrade` | Full upgrade workflow (inject + configure-hooks) |

### Skills (`/skill:*`)

| Command | Purpose |
|---------|---------|
| `/skill:create [name]` | Create a new Claude Code skill |
| `/skill:audit [name]` | Audit skill(s) for quality and best practices |
| `/skill:list` | List all skills with descriptions and metrics |

### Board (`/board:*`)

| Command | Purpose |
|---------|---------|
| `/board:advise [question]` | Convene Personal Board of Advisors (includes pre-mortem exercises) |

### Goals (`/goals:*`)

| Command | Purpose |
|---------|---------|
| `/goals:status` | Quick goals dashboard |
| `/goals:review` | Weekly goals review |
| `/goals:opportunity [description]` | Evaluate new opportunity (includes asymmetry evaluation) |

### Project (`/project:*`)

| Command | Purpose |
|---------|---------|
| `/project:status` | Portfolio dashboard with progress, health, and deadlines |

### Roadmap (`/roadmap:*`)

| Command | Purpose |
|---------|---------|
| `/roadmap:status` | Product roadmap dashboard across all companies |

### Inbox (`/inbox:*`)

| Command | Purpose |
|---------|---------|
| `/inbox:process` | Process files in inbox - identify, route, and organize |

### Reminders (`/reminders:*`)

| Command | Purpose |
|---------|---------|
| `/reminders:refresh` | Bidirectional sync with macOS Reminders app |

### Personal (`/personal:*`)

| Command | Purpose |
|---------|---------|
| `/personal:audit` | Audit personal documents for completeness |

See `0-System/guides/personal-documents.md` for the personal document system.

### Universal

| Command | Purpose |
|---------|---------|
| `/update [text]` | Smart capture — routes to appropriate places |

### Annual (`/annual:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/annual:review` | Year-end reflection and learning | annual-review |
| `/annual:plan` | Set annual goals and theme | annual-plan |

### Quarter (`/quarter:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/quarter:review` | Quarterly reflection | quarterly-review |
| `/quarter:plan` | Set quarterly rocks | quarterly-plan |

### Monthly (`/monthly:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/monthly:review` | Monthly reflection | monthly-review |
| `/monthly:plan` | Monthly planning | monthly-plan |

### Weekly (`/weekly:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/weekly:review` | Weekly review workflow | weekly-review-planning |
| `/weekly:reflect` | Light-weight Monday reflection on pre-aggregated data | weekly rolling doc |

### Health (`/health:*`)

| Command | Purpose |
|---------|---------|
| `/health:sync [days]` | Sync health data from Health Auto Export and show status |

### Retro (`/retro:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/retro:weekly` | Weekly retrospective (3 Ls) | weekly-retro |
| `/retro:monthly` | Monthly retrospective (4 Ls) | monthly-retro |
| `/retro:quarterly` | Quarterly retrospective (Sailboat) | quarterly-retro |

### Premortem (`/premortem:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/premortem:run` | Run pre-mortem on decision/project | premortem-* |

### Strategic (`/strategic:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/strategic:decide` | Guided strategic decision-making | strategic-decision-* |

### Partner (`/partner:*`)

| Command | Purpose | Template |
|---------|---------|----------|
| `/partner:stateofunion` | Weekly relationship check-in | partner-state-of-union |

## Creating a New Command

1. **Choose namespace** or create new one
2. **Create file:** `.claude/commands/[namespace]/[name].md`
3. **Document arguments** at the top
4. **Write the prompt** that Claude will execute
5. **Add to CLAUDE.md** commands table

### Template

```markdown
# [Command Name]

[Brief description of what this command does]

## Arguments

- `arg1` - Description of first argument
- `arg2` (optional) - Description of optional argument

## Task

[Detailed instructions for Claude to follow]

### Step 1: [Action]

[Details...]

### Step 2: [Action]

[Details...]

## Output Format

[Describe expected output structure]

## Examples

```
/namespace:command arg1 arg2
```
```

## Best Practices

1. **Clear arguments** — Document required vs optional
2. **Structured output** — Define expected format
3. **Error handling** — What if inputs are missing?
4. **Idempotency** — Running twice shouldn't break things
5. **User feedback** — Confirm actions taken
