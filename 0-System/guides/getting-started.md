# Getting Started with LifeOS

Welcome to LifeOS — your AI-coached life operating system.

## Automatic First-Run Setup

When you start Claude Code in this vault for the first time, the onboarding wizard starts automatically. You don't need to do anything — just answer the questions to personalize your vault.

**How it works:**
- The `session-context-loader` hook detects `onboarding_complete: false` in `0-System/config/user-config.md`
- Claude automatically invokes `/setup:onboard` before responding to any input
- Once complete, the flag is set to `true` and normal sessions begin

**If you need to re-run setup:** Set `onboarding_complete: false` in `0-System/config/user-config.md`

## First Steps (After Onboarding)

1. **Start Your First Day**: `/daily:plan`
   - Creates today's daily note
   - Guides you through morning planning

2. **Learn the Basics**:
   - Tasks use priority symbols: 🔴 (must do), 🟡 (should do), 🟢 (nice to have)
   - Capture anything quickly with `/update [text]`
   - End your day with `/daily:eod`

## Key Commands

| Command | Purpose |
|---------|---------|
| `/daily:plan` | Start your day with guided planning |
| `/daily:eod` | End-of-day review and tomorrow prep |
| `/update [text]` | Quick capture anything |
| `/create:project` | Start a new project |
| `/meeting:prep [name]` | Prepare for a meeting |
| `/board:advise` | Get advice from your Personal Board |

## Directory Structure

- `0-Inbox/` — Drop files here for processing
- `1-Projects/` — Active, backlog, and completed work
- `2-Areas/` — Ongoing responsibilities by company/area
- `3-Resources/` — Templates, docs, reference material
- `4-Daily/` — Daily notes (auto-created)
- `5-Meetings/` — Meeting notes
- `6-People/` — Contact and relationship info

## Getting Help

- `/system:ask [question]` — Ask how to do something
- Check `0-System/guides/` for detailed documentation
- See `0-System/README.md` for full architecture

## Philosophy

LifeOS is designed to help you bridge the gap between your philosophy and daily action. The coaching persona will:
- Challenge your assumptions
- Hold you accountable (without judgment)
- Celebrate wins that align with your identity
- Protect your renewal time

Adjust coaching intensity in your config if needed.

---

If onboarding didn't start automatically, run `/setup:onboard` to begin.
