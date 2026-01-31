# LifeOS Starter Template

A personal operating system powered by Obsidian + Claude Code. Combines knowledge management, AI coaching, and automated workflows to bridge the gap between philosophy and daily action.

## Features

- **AI Coaching**: Configurable coaching persona that challenges assumptions and holds you accountable
- **Task Management**: A/B/C priority system with due dates and blocking dependencies
- **Daily Workflows**: Guided morning planning (`/daily:plan`) and EOD review (`/daily:eod`)
- **Meeting Support**: Prep, notes, and follow-up workflows
- **Personal Board of Advisors**: Multi-perspective deliberation on important decisions
- **Calendar Integration**: Google Calendar sync with smart defaults
- **Self-Learning**: System improves through `/system:learn` sessions

## Quick Start

1. **Clone this repo** into your Obsidian vaults directory
2. **Open in Obsidian** as a vault
3. **Start Claude Code** in the vault directory
4. **Onboarding starts automatically** — answer the questions to personalize

The first-run wizard configures:
- Your identity (name, timezone, location)
- Companies/areas you work with
- Coaching intensity preferences
- Calendar and integration settings

## Directory Structure

```
/
├── 0-Inbox/          # Drop files here for processing
├── 0-System/         # LifeOS documentation and config
├── 1-Projects/       # Active work (Current/, Backlog/, Completed/)
├── 2-Areas/          # Ongoing responsibilities by company
├── 3-Resources/      # Templates, docs, reference material
├── 4-Daily/          # Daily notes (YYYY-MM-DD.md)
├── 5-Meetings/       # Meeting notes
├── 6-People/         # Contact and relationship info
├── 7-MOCs/           # Maps of Content
└── 8-Scratch/        # Temporary workspace
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `/daily:plan` | Start your day with guided planning |
| `/daily:eod` | End-of-day review |
| `/update [text]` | Quick capture anything |
| `/create:project` | Start a new project |
| `/meeting:prep` | Prepare for a meeting |
| `/board:advise` | Convene your Personal Board of Advisors |
| `/system:ask` | Ask how to do something |

## Documentation

- `0-System/guides/getting-started.md` — First steps after onboarding
- `0-System/guides/daily-workflow.md` — Daily planning and review
- `0-System/guides/task-management.md` — Priority system details
- `0-System/README.md` — Full architecture reference

## Requirements

- [Obsidian](https://obsidian.md/) (free)
- [Claude Code](https://claude.ai/code) CLI
- Node.js (for some hooks)
- Python 3.8+ (for hooks)

## Optional Integrations

- Google Calendar (OAuth setup during onboarding)
- macOS Reminders (for mobile task access)
- Health Auto Export (iOS health data)

## Philosophy

LifeOS helps you become "someone strong, loving, and courageous enough to protect what matters, while fully enjoying the journey."

The coaching persona will:
- Challenge your assumptions
- Surface patterns between commitments and actions
- Hold you accountable without judgment
- Celebrate identity-consistent wins
- Protect your renewal time

## License

MIT License — use freely, attribution appreciated.

## Privacy Note

This template creates a private vault for personal data. After personalization, your vault will contain sensitive information. Keep it private and back up regularly.
