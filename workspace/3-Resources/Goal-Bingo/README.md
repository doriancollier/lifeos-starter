---
title: "Goal Bingo"
type: index
created: 2026-01-03
---

# Goal Bingo

A gamified goal tracking system for {{user_first_name}}, [[{{partner_name}}]], and [[{{child_name}} {{user_last_name}}|{{child_name}}]].

## Quick Links

### Documentation
- [[rules]] — How to play, earning draws, prize pool mechanics
- [[prizes]] — Current prize pool (all tiers)
- [[prize-slips]] — Checklist for creating physical prize slips

### Configuration
- [[bingo-goals]] — Goals for annual and monthly cards (in 2-Areas/Personal/)

### Generated Cards
- [[3-Resources/Documents/Printables/|Printables Folder]] — Generated cards ready to print

### Archives
- [[Bingo-Annual-2025.pdf]] — 2025 Annual Card
- [[Bingo-Monthly-2025.png]] — 2025 Monthly Cards
- [[prizes-2025-original]] — Original 2025 prize list (inbox import)

## Generating Cards

Use the `/create:bingo` command:

```
/create:bingo 2026           # Generate 2026 Annual Card
/create:bingo 2026 january   # Generate January 2026 Monthly Card
```

## Skill & Configuration

The Goal Bingo skill lives in `.claude/skills/goal-bingo/` and contains:

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill instructions for Claude |
| `config.json` | **Owners, colors, paths** — edit this to customize |
| `rules.md` | Game rules (shareable version) |
| `card-generation.md` | Detailed HTML/CSS generation reference |
| `bingo-card-template.html` | HTML template with placeholders |

### Customizing Owners

Edit `.claude/skills/goal-bingo/config.json` to add/remove/modify owners:

```json
{
  "owners": [
    { "id": "partner", "name": "{{partner_name}}", "color": "#F5D0E0", "emoji": "👩🏾" },
    { "id": "user", "name": "{{user_first_name}}", "color": "#D0E8F5", "emoji": "👨🏾" },
    { "id": "child", "name": "{{child_name}}", "color": "#F5E0D0", "emoji": "👦🏾" },
    { "id": "parents", "name": "Parents", "color": "#D0F5D8", "emoji": "👩🏾👨🏾" }
  ]
}
```

## Current Color Coding

*Defined in config.json — this table is for quick reference:*

| Owner | Color | Hex | Emoji |
|-------|-------|-----|-------|
| {{partner_name}} | Pink | #F5D0E0 | 👩🏾 |
| {{user_first_name}} | Blue | #D0E8F5 | 👨🏾 |
| {{child_name}} | Orange | #F5E0D0 | 👦🏾 |
| Parents | Green | #D0F5D8 | 👩🏾👨🏾 |
