# Goal Bingo Rules

A gamified goal tracking system. Complete goals, earn draws from the prize pool, celebrate wins together.

## Overview

Goal Bingo uses two types of cards:
- **Annual Card** — 5x5 grid of one-time goals (trips, milestones, health appointments)
- **Monthly Cards** — Weekly habit tracking (5 columns x 4-5 rows per month)

## The Prize Pool

All prizes are mixed into a single pool with weighted distribution. Prize tiers are defined in `config.json` under `prizeTiers`:

| Tier | Default Emoji | Typical Quantity | Odds |
|------|---------------|------------------|------|
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
5. Return slip to pool (prizes can be won multiple times)

## Card Types Explained

### Annual Card (5x5)

- One card for the entire year
- Goals are one-time achievements (not recurring)
- Mix of individual and shared goals
- Color-coded by owner (see `config.json` for owner definitions)

### Monthly Card (5 columns x 4-5 rows)

- New card each month
- Columns = weekly recurring goals (same each week)
- Rows = weeks of the month
- Start date is always a Monday
- Tracks habit consistency, not one-time goals

## Owner Color Coding

Owner colors are configured in `config.json`. Each owner has:
- `id`: Unique identifier
- `name`: Display name
- `color`: Hex color code for card cells
- `emoji`: Visual indicator on cards

Example from config:
```json
{
  "id": "person1",
  "name": "Person 1",
  "color": "#F5D0E0",
  "emoji": "👤"
}
```

## Marking Completions

- **Incomplete**: Empty square
- **Complete**: Check mark, X, or stamp
- **Partial credit**: Not allowed — it's complete or it's not

## House Rules

*Add your own rules here as you play:*

- Can you "save" draws for later, or must you draw immediately?
- If you draw a "free BINGO spot" prize, when can you use it?
- Can you trade prizes with each other?

---

**Tip**: The magic of Goal Bingo is the *anticipation*. Even small achievements give you a shot at big prizes. Celebrate every draw together!
