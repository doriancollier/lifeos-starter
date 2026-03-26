# Chief of Staff — Agent Template

An agent template that turns your AI into a personal chief of staff. It plans your day, preps your meetings, tracks your goals, coaches you through decisions, and holds you accountable across every role you play.

> **This is a template repository.** Click "Use this template" to create your own private copy, completely independent with no connection back to this repo.

## What It Does

Once loaded, your agent can:

- **Plan your day** — Guided morning planning and end-of-day review
- **Manage your tasks** — A/B/C priority system with due dates and blocking dependencies
- **Prep your meetings** — Pull context on attendees, projects, and past discussions
- **Coach you** — Configurable coaching persona that challenges assumptions and surfaces patterns
- **Advise on decisions** — Convene a Personal Board of Advisors for multi-perspective deliberation
- **Track your goals** — Weekly reviews, quarterly rocks, annual themes
- **Manage your calendar** — Smart scheduling with travel time and conflict detection
- **Know your people** — Relationship context, communication styles, interaction history
- **Monitor your energy** — Four-dimension energy tracking for sustainable performance
- **Learn and improve** — The system codifies what works through `/system:learn` sessions

## Getting Started

### As a User

1. Click **"Use this template"** → **"Create a new repository"**
2. Name it (e.g., `my-chief-of-staff`) and set to **Private**
3. Clone your new repo and open it as an Obsidian vault
4. Run Claude Code in the directory — onboarding starts automatically

The first-run wizard configures:
- Your identity (name, timezone, location)
- Companies and areas you manage
- Coaching intensity preferences
- Calendar and integration settings

### As a Contributor

1. **Fork** this repository
2. Clone your fork locally
3. Create a feature branch
4. Make changes and test with placeholder values
5. Submit a PR

Please don't include personal data in PRs.

## Directory Structure

```

├── 0-Inbox/          # Drop files here for processing
├── 0-System/         # System documentation and config
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
| `/goals:status` | Check progress on your goals |
| `/system:ask` | Ask how to do something |

## Documentation

- [Getting Started](0-System/guides/getting-started.md) — First steps after onboarding
- [Daily Workflow](0-System/guides/daily-workflow.md) — Daily planning and review
- [Task Management](0-System/guides/task-management.md) — Priority system details
- [Full Architecture](0-System/README.md) — Complete system reference

## Requirements

- [Obsidian](https://obsidian.md/) (free)
- [Claude Code](https://claude.ai/code) CLI
- Node.js 18+
- Python 3.8+

## Optional Integrations

- Google Calendar (OAuth setup during onboarding)
- macOS Reminders (for mobile task access)
- Health Auto Export (iOS health data)

## Philosophy

Your chief of staff will:
- Challenge your assumptions before accepting them
- Surface patterns between what you commit to and what you actually do
- Hold you accountable without judgment
- Celebrate when your actions match who you say you want to be
- Protect your renewal time — rest is not weakness

## License

MIT License — use freely, attribution appreciated.

## Privacy Note

When you use this template, you get a completely independent repository with no history or connection to the original. After personalization, your repo will contain sensitive information — **keep it private** and back up regularly.
