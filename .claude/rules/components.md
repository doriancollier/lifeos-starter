# Claude Code Components

Reference for all skills, commands, agents, and hooks available in this vault.

## Skills (`.claude/skills/`)

Skills are model-invoked knowledge modules. Claude reads them automatically when context matches.

### Core Skills

| Skill | Purpose |
|-------|---------|
| `daily-note` | Create/navigate daily notes, auto-creation, past day memory routing (within 7 days) |
| `vault-task-system` | A/B/C priority + due dates (📅 YYYY-MM-DD format) |
| `vault-task-sync` | Sync tasks between daily notes and projects |
| `work-logging` | Log progress with subtasks and timestamps |
| `meeting-prep` | Gather context before meetings |
| `person-context` | Relationship and communication info |
| `context-switch` | Switch between company contexts |

### Calendar Skills

| Skill | Purpose |
|-------|---------|
| `calendar-awareness` | Holidays, schedule overview (delegates birthdays) |
| `calendar-management` | Create, modify, delete events |
| `birthday-awareness` | Detect birthdays, create recurring events |
| `daily-timebox` | Create timeboxed focus blocks |

### Planning Skills

| Skill | Purpose |
|-------|---------|
| `planning-cadence` | Connect daily→weekly→monthly→quarterly→annual horizons |
| `strategic-thinking` | Second-order thinking, decision classification |
| `pre-mortem` | Guide pre-mortem exercises for major decisions |
| `energy-management` | Four-dimension energy tracking |
| `project-structure` | Standards for organizing project files and folders |

### Health Skills

| Skill | Purpose |
|-------|---------|
| `health-awareness` | Health data integration and coaching for daily planning |

### Theme Skills

| Skill | Purpose |
|-------|---------|
| `theme-management` | Generate synchronized VS Code + Obsidian themes from color palettes |

### Writing & Documentation Skills

| Skill | Purpose |
|-------|---------|
| `changelog-writing` | Write human-friendly changelog entries and release notes |
| `writing-voice` | Write in {{user_first_name}}'s authentic voice (emails, Slack, SMS, docs) |

### Other Skills

| Skill | Purpose |
|-------|---------|
| `audio-generator` | Generate speech audio using ElevenLabs (TTS, voice presets, SSML) |
| `email-reader` | Read emails from Mail.app via AppleScript |
| `reminders-integration` | Bidirectional sync with macOS Reminders (mobile/Siri access) |
| `person-file-management` | Auto-create/update person files |
| `personal-profile` | Manage owner's personal documents (resume, work history, skills, etc.) |
| `personal-insight` | Capture self-insights to profile |
| `historical-memory` | Capture biographical info |
| `document-generator` | Create printable documents |
| `goals-tracking` | Track goals, manage opportunities |
| `goal-bingo` | Generate Goal Bingo cards |
| `habit-tracker` | Generate monthly habit tracking sheets |
| `product-management` | PRDs, roadmaps, prioritization |
| `inbox-processor` | Identify and route inbox files |
| `project-status` | Track project lifecycle |
| `weekly-review` | Aggregate weekly patterns |
| `weekly-aggregator` | Auto-aggregate daily data into rolling weekly doc (runs during /daily:plan) |
| `obsidian-open` | Open files in Obsidian UI |
| `skill-manager` | Create, review, and maintain Claude Code skills |
| `operations` | Math, date calculations, and reliable computation guidance |
| `proactive-suggestions` | Suggest high-value commands (`/board:advise`, `/system:learn`, `/system:update`) when context matches |
| `orchestration-patterns` | Agent delegation patterns for efficient context management (auto-applied when designing commands) |

### Advisor Skills (for `/board:advise`)

11 domain skills: `advisor-financial`, `advisor-business-strategy`, `advisor-ops-systems`, `advisor-health-energy`, `advisor-relationships`, `advisor-parenting-family`, `advisor-leadership-boundaries`, `advisor-success-execution`, `advisor-decision-frameworks`, `advisor-legal-literacy`, `advisor-librarian-context`

**Full list**: See `workspace/0-System/components/skills.md`

## Commands (`.claude/commands/`)

Commands are user-invoked via `/namespace:command`.

### Daily Workflow

| Command | Purpose |
|---------|---------|
| `/daily:note` | Create/open today's daily note |
| `/daily:plan` | Morning planning workflow (brain dump → calendar review → coached planning) |
| `/daily:tasks` | Review open tasks |
| `/daily:capture [text]` | Quick capture |
| `/daily:timebox` | Create focus blocks |
| `/daily:standup` | Generate standup summary |
| `/daily:eod` | End-of-day review |
| `/update [text]` | Universal smart capture (routes anywhere) |

### Tasks

| Command | Purpose |
|---------|---------|
| `/vault-tasks:due` | Show tasks by due date (overdue, today, upcoming) |

### Meetings

| Command | Purpose |
|---------|---------|
| `/meeting:sync` | Import meetings from SuperNormal |
| `/meeting:process` | Process meeting with AI context, extract insights |
| `/meeting:prep [name]` | Prepare context for meeting |
| `/meeting:create [company] [title]` | Create meeting note for any company |
| `/meeting:ab [title]` | Shortcut: Create {{company_1_name}} meeting note |

### Context & Creation

| Command | Purpose |
|---------|---------|
| `/context:load [company]` | Load context for any company (ab, 144, emh, personal) |
| `/context:ab`, `/context:personal` | Shortcut commands |
| `/create:person [name]` | Look up or create person note |
| `/create:project [name]` | Create new project |
| `/create:trip [name]` | Create trip planning project |
| `/create:gifts [occasion]` | Create gift planning project |
| `/create:bingo [year] [month?]` | Generate Goal Bingo cards |
| `/create:habits [month] [year?]` | Generate monthly habit tracker |
| `/create:song [name]` | Create song project with lyrics/prompts structure |

### Setup

| Command | Purpose |
|---------|---------|
| `/setup:onboard` | First-run setup wizard to personalize LifeOS |

### Theme

| Command | Purpose |
|---------|---------|
| `/theme:set [name]` | Apply a theme (preset or custom) |
| `/theme:create [name]` | Create a custom theme palette interactively |
| `/theme:edit [name]` | Modify an existing palette |
| `/theme:from-color [hex]` | Generate theme from favorite color |

### Reminders

| Command | Purpose |
|---------|---------|
| `/reminders:refresh` | Bidirectional sync with macOS Reminders app |

### Personal Profile

| Command | Purpose |
|---------|---------|
| `/personal:audit` | Audit personal documents for completeness |

### Changelog

| Command | Purpose |
|---------|---------|
| `/changelog:backfill` | Populate [Unreleased] from commits since last tag |

### System & Goals

| Command | Purpose |
|---------|---------|
| `/system:ask [question]` | Ask how to do something |
| `/system:review [area]` | Review processes |
| `/system:update [description]` | Add/update processes |
| `/system:learn [topic]` | Learn capabilities through experimentation, codify results |
| `/system:inject` | Regenerate CLAUDE.md and coaching.md from templates |
| `/system:configure-hooks` | Regenerate settings.json from .user/integrations.yaml |
| `/system:upgrade` | Fetch updates from upstream, apply safely with rollback |
| `/system:release [type]` | Auto-detect version (spawns analysis agent), create release with tag and optional GitHub Release |
| `/goals:status` | Goals dashboard |
| `/goals:review` | Weekly goals review |
| `/goals:opportunity [desc]` | Evaluate new opportunity |
| `/project:status` | Portfolio dashboard |
| `/roadmap:status` | Product roadmap across companies |
| `/board:advise [question]` | Convene Personal Board of Advisors |
| `/inbox:process` | Process inbox files |

### Skills

| Command | Purpose |
|---------|---------|
| `/skill:create [name]` | Create a new Claude Code skill |
| `/skill:audit [name]` | Audit skill(s) for quality |
| `/skill:list` | List all skills with descriptions |

### Extensions

| Command | Purpose |
|---------|---------|
| `/extensions:sync` | Sync extensions from `extensions/` to `.claude/` via symlinks |
| `/extensions:list` | Show registered extensions and their status |
| `/extensions:enable [name]` | Enable a disabled extension |
| `/extensions:disable [name]` | Disable an extension without uninstalling |

### Planning

| Command | Purpose |
|---------|---------|
| `/annual:plan` | Set annual goals and theme |
| `/annual:review` | Year-end reflection and learning |
| `/quarter:plan` | Set quarterly rocks |
| `/quarter:review` | Quarterly reflection |
| `/monthly:plan` | Monthly planning |
| `/monthly:review` | Monthly reflection |
| `/weekly:review` | Weekly review workflow |
| `/weekly:reflect` | Light-weight Monday reflection on pre-aggregated weekly data |

### Health

| Command | Purpose |
|---------|---------|
| `/health:sync [days]` | Sync health data from Health Auto Export and show status |

### Heartbeat

| Command | Purpose |
|---------|---------|
| `/heartbeat:install` | Install and start the launchd agent |
| `/heartbeat:status` | Check launchd status, show recent run history |
| `/heartbeat:trigger` | Run heartbeat check manually |
| `/heartbeat:ack [type] [duration]` | Suppress an alert temporarily |

### Retrospectives

| Command | Purpose |
|---------|---------|
| `/retro:weekly` | Weekly retrospective (3 Ls format) |
| `/retro:monthly` | Monthly retrospective (4 Ls format) |
| `/retro:quarterly` | Quarterly retrospective (Sailboat format) |

### Strategic & Relationship

| Command | Purpose |
|---------|---------|
| `/strategic:decide` | Guided strategic decision-making |
| `/premortem:run` | Run pre-mortem on decision/project |
| `/partner:stateofunion` | Weekly relationship check-in |

**Full list**: See `workspace/0-System/components/commands.md`

## Agents (`.claude/agents/`)

Agents are spawned via Task tool for complex, isolated tasks.

| Agent | Purpose |
|-------|---------|
| `context-isolator` | Run data-heavy ops in isolated context (calendar views, large searches) |
| `vault-explorer` | Deep vault search and navigation |
| `task-reviewer` | Task management analysis |
| `meeting-processor` | Process meeting transcripts with user context |
| `relationship-manager` | People intelligence |
| `research-expert` | Focused research tasks |
| `product-manager` | PRD and roadmap generation |
| `email-processor` | Email triage, inbox processing, summarization |
| `system-reviewer` | Parallel system component review (spawned by /system:review) |

### Board of Advisors Agents

| Agent | Role |
|-------|------|
| `persona-board-chair` | Orchestrator, synthesis |
| `persona-strategic-operator` | Business, wealth |
| `persona-relationships-guardian` | Family, trust |
| `persona-health-steward` | Sustainability, energy |
| `persona-execution-coach` | Action, discipline |

### Agent Resumption (Multi-Step Workflows)

Some agents (like `persona-board-chair`) pause for Q&A and must be resumed. When resuming:

1. **Extract Session Directory** from the agent's response
2. **Pass it explicitly** in the resume prompt:
   ```
   SESSION DIRECTORY (USE THIS - DO NOT CREATE NEW):
   /full/path/to/session/
   ```
3. **Never let resumed agents create new directories** — they should continue in the existing one

Failure to pass session state causes duplicate directories and fragmented session files.

**Full list**: See `workspace/0-System/components/agents.md`

## Hooks (`.claude/hooks/`)

Hooks run automatically at lifecycle events.

| Hook | Event | Purpose |
|------|-------|---------|
| `version-check.py` | SessionStart | Check for LifeOS updates |
| `session-context-loader.py` | SessionStart | Load today's context |
| `reminders-session-sync.py` | SessionStart | Pull Reminders completions to daily note |
| `health-session-sync.py` | SessionStart | Sync health data from Health Auto Export |
| `prompt-timestamp.py` | UserPromptSubmit | Add current time |
| `directory-guard.py` | PreToolUse (Write) | **BLOCKS** wrong directories |
| `calendar-protection.py` | PreToolUse (Calendar) | **BLOCKS** unconfirmed changes |
| `frontmatter-validator.py` | PostToolUse | Validate YAML |
| `task-format-validator.py` | PostToolUse | Validate tasks |
| `table-format-validator.py` | PostToolUse | Validate table formatting |
| `task-sync-detector.py` | PostToolUse | Queue task syncs |
| `reminders-task-detector.py` | PostToolUse | Push tasks to Reminders app |
| `git-task-sync-detector.sh` | Git post-commit (manual) | Detect external task changes |
| `changelog-populator.py` | Git post-commit | Auto-populate changelog from conventional commits |
| `auto-git-backup.sh` | SessionEnd | Auto-commit changes with summary |

**Setup**: See `.claude/hooks/README.md`

## Upgrade Notes (`.claude/upgrade-notes/`)

Per-version AI guidance for helping users through upgrades.

| File | Purpose |
|------|---------|
| `README.md` | Template and format documentation |
| `v{X.Y.Z}.md` | Upgrade notes for specific version |

Each upgrade notes file contains:
- **User Action Required** - Checkbox items that become tracked tasks
- **Breaking Changes** - What changed and how to adapt
- **New Features** - Highlights to explore
- **Verification** - Steps to confirm success
- **Notes for AI** - Internal guidance (not shown to user)

During `/system:upgrade`, the AI creates tasks from action items and guides users through each one interactively.
