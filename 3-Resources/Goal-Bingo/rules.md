---
title: "Goal Bingo Rules"
type: reference
created: 2026-01-03
modified: 2026-01-03
---

# Goal Bingo Rules

A gamified goal tracking system for {{user_first_name}}, [[{{partner_name}}]], and [[{{child_name}} {{user_last_name}}|{{child_name}}]]. Complete goals, earn draws from the prize pool, celebrate wins together.

> [!info] Skill Reference
> The shareable/configurable version of these rules lives in `.claude/skills/goal-bingo/rules.md`. Owner colors are defined in `.claude/skills/goal-bingo/config.json`.

## Overview

Goal Bingo uses two types of cards:
- **Annual Card** — 5x5 grid of one-time goals (trips, milestones, health appointments)
- **Monthly Cards** — Weekly habit tracking (5 columns x 4-5 rows per month)

## The Prize Pool

All prizes are mixed into a single pool with weighted distribution:

| Tier | Emoji | Quantity in Pool | Odds |
|------|-------|------------------|------|
| Small | 🟢 | ~15 prizes | High chance |
| Medium | 🔵 | ~10 prizes | Medium chance |
| Big | 🟣 | ~9 prizes | Low chance |

**The fun part**: Every draw has the *potential* to be a big prize. You never know what you'll get!

## Earning Draws

### From Monthly Cards (Weekly Habits)

| Achievement | Draws Earned |
|-------------|--------------|
| Complete a row (1 week, all 5 habits) | 1 draw |
| Complete a column (1 habit, all weeks) | 1 draw |
| Complete a diagonal | 1 draw |
| Blackout (entire card) | 3 draws |

### From Annual Card (One-Time Goals)

| Achievement | Draws Earned |
|-------------|--------------|
| Complete a row (5 goals) | 2 draws |
| Complete a column (5 goals) | 2 draws |
| Complete a diagonal (5 goals) | 2 draws |
| Blackout (entire card) | 5 draws |

*Note: Adjust draw amounts as desired — these are starting suggestions.*

## How to Play

### Setup (Start of Year)
1. Print Annual Card and post visibly
2. Print January Monthly Card
3. Prepare prize pool (write prizes on slips, put in jar/bowl)

### During the Year
1. **Mark completions** — Check off goals as you achieve them
2. **Celebrate lines** — When you complete a row/column/diagonal, do a draw!
3. **Monthly refresh** — Print new monthly card, archive the old one

### Prize Draws
1. Mix up the prize pool
2. Draw without looking
3. Read prize aloud and celebrate
4. Redeem prize within reasonable timeframe
5. Return prize slip to pool (prizes can be won multiple times)

## Card Types Explained

### Annual Card (5x5)

- One card for the entire year
- Goals are one-time achievements (not recurring)
- Mix of individual and shared goals
- Color-coded by owner:
  - Pink (#F5D0E0) = {{partner_name}} 👩🏾
  - Blue (#D0E8F5) = {{user_first_name}} 👨🏾
  - Orange (#F5E0D0) = {{child_name}} 👦🏾
  - Green (#D0F5D8) = Parents 👩🏾👨🏾

### Monthly Card (5 columns x 4-5 rows)

- New card each month
- Columns = weekly recurring goals (same each week)
- Rows = weeks of the month
- Start date is always a Monday
- Tracks habit consistency, not one-time goals

## Marking Completions

- **Incomplete**: Empty square
- **Complete**: Check mark, X, or stamp
- **Partial credit**: Not allowed — it's complete or it's not

## House Rules

*Add your own rules here as you play:*

- [ ] Can you "save" draws for later, or must you draw immediately?
- [ ] If you draw a "free BINGO spot" prize, when can you use it?
- [ ] Can you trade prizes with each other?

## Files & Resources

- [[bingo-goals]] — Goals and prizes configuration
- [[3-Resources/Goal-Bingo/prizes|Prize Pool]] — Current prize list
- [[3-Resources/Documents/Templates/bingo-card.html|Card Template]] — HTML for generating cards

---

> [!tip] Making It Fun
> The magic of Goal Bingo is the *anticipation*. Even small achievements give you a shot at big prizes. Celebrate every draw together!
