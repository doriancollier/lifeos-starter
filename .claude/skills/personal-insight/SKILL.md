---
name: personal-insight
description: Detect and capture substantive personal insights to maintain {{user_first_name}}'s personal profile. Use when conversations reveal new information about strengths, weaknesses, patterns, fears, or decision-making tendencies.
allowed-tools: Read, Edit, Grep, Glob, AskUserQuestion
---

# Personal Insight Skill

Automatically detect and capture substantive personal insights to keep {{user_first_name}}'s personal profile current and accurate.

## Purpose

{{user_first_name}}'s personal profile (`workspace/2-Areas/Personal/context.md` → "About Me" section) should evolve over time as new insights emerge from:
- Retrospectives and reviews
- Board of Advisors deliberations
- Casual conversation and updates
- Feedback on decisions and outcomes

This skill defines **when** and **how** to update the profile.

## What Qualifies as a Substantive Personal Insight

### Update the profile when {{user_first_name}} reveals:

**Strengths (new or refined)**
- "I realized I'm actually good at..."
- Demonstrated capability that wasn't previously documented
- Feedback from others about a strength

**Weaknesses / Blind Spots (new or refined)**
- "I keep doing X and it doesn't work..."
- Pattern recognition about self-sabotage
- Honest admission of a limitation

**Fears & Concerns**
- "I'm worried that..."
- "What if I'm..."
- Expressed anxiety about patterns or outcomes

**Decision-Making Patterns**
- "When I do X, things go well..."
- "I notice I always..."
- "That worked because..." / "That failed because..."

**Historical Patterns**
- New examples of what worked or didn't
- Connections between past and present behavior

**Network & Assets Changes**
- New key relationships formed
- Relationships that have changed significance
- New assets or resources

**Working Style Discoveries**
- "I work better when..."
- "I've learned I need..."
- Environmental or process preferences

### Do NOT update for:

- Temporary moods or feelings
- One-off events without pattern significance
- Opinions about external things (not self-insight)
- Information already captured
- Trivial preferences

## How to Update

### Location
Edit: `workspace/2-Areas/Personal/context.md` → "About Me (Personal Profile)" section

### Format
- Use the existing structure (Strengths, Weaknesses, Fears, etc.)
- Keep entries concise: `**Label** — Brief explanation`
- Add new items to the appropriate section
- Refine existing items if the new insight deepens understanding
- Update the "Last updated" date at the bottom

### Example Updates

**New strength discovered:**
```markdown
### Strengths
...existing items...
- **Synthesizing complex information** — Can take disparate inputs and find patterns others miss
```

**Refined weakness:**
```markdown
### Weaknesses / Blind Spots
- **"Waiting" pattern** — Tendency to wait for something to be done before moving forward; may be procrastination or fear. *Update: Often triggered when feeling uncertain about direction.*
```

**New historical pattern:**
```markdown
### Historical Patterns (What's Worked Before)
...existing items...
- **2026 board deliberation on X** — Taking time to get multiple perspectives led to better decision
```

## Integration Points

### With `/update` Command
The `/update` command already routes content to appropriate locations. When processing an update that contains self-reflective content, also consider updating the personal profile.

**Triggers in `/update`:**
- "I realized..."
- "I'm noticing a pattern..."
- "I keep..."
- "I'm worried about..."
- "What works for me is..."
- Feedback on a past decision

### With Board Deliberations
After board sessions, the synthesis often contains insights about {{user_first_name}}'s patterns or tendencies. The Board Chair should flag any substantive insights for profile updates.

### With Retrospectives
Annual and quarterly retrospectives are prime sources of personal insight. When processing retrospectives, actively extract profile-worthy insights.

## Proactive Detection

When Claude detects potential personal insight in conversation:

1. **Recognize the insight** — Note internally that this seems substantive
2. **Confirm if appropriate** — For significant additions, briefly confirm: "That sounds like an important insight about yourself. Should I add it to your personal profile?"
3. **Update silently for minor refinements** — Small clarifications to existing items don't need confirmation
4. **Always update the timestamp** — `*Last updated: YYYY-MM-DD*`

## Guardrails

- **Never remove insights** without explicit request — Profile should grow, not shrink
- **Preserve {{user_first_name}}'s voice** — Use his framing when possible
- **Don't over-update** — Not every conversation contains profile-worthy insights
- **Don't psychoanalyze** — Capture what {{user_first_name}} says about himself, don't infer
- **Ask when uncertain** — If unsure whether something is substantive, ask

## Output

When updating the profile, briefly note what was added:

```
Updated personal profile:
- Added to Strengths: [item]
- Refined in Weaknesses: [item]
```

This keeps {{user_first_name}} aware of how his profile is evolving.

## Enhancements

### Retrospective Insight Routing

Retrospectives (daily, weekly, monthly, quarterly, annual) are prime sources of personal insight. Breakthrough insights from retros should be captured in the personal profile.

**What qualifies as a retrospective breakthrough insight:**
- Pattern recognition across multiple reviews ("I notice I always...")
- Root cause discoveries from Five Whys analysis
- Identity-level realizations ("Who I became this year...")
- Principle refinements from tested experiences
- Fear/avoidance patterns surfaced
- Energy patterns that reveal working style

**Triggers during retrospective processing:**
- "This keeps happening because..."
- "I realized my pattern of..."
- "What I learned about myself..."
- "My assumption was wrong about..."
- "What actually works for me is..."
- Pain + Reflection = Progress moments

**Routing logic:**
1. Daily micro-retro: Rarely produces profile-worthy insights (tactical level)
2. Weekly retro: Occasionally surfaces patterns worth capturing
3. Monthly/Quarterly retro: Frequently produces profile-worthy insights
4. Annual retro: Almost always produces profile-worthy insights
5. Pain + Reflection moments: High signal for personal insight

**After any retrospective that surfaces breakthrough insights:**
> "This retrospective revealed [insight about yourself]. Should I add this to your personal profile?"

### Pattern Recognition Across Retrospectives

Track recurring themes that appear across multiple retrospectives:

**What to watch for:**
- Same weakness appearing in different contexts
- Recurring avoidance patterns
- Repeated success patterns (what works)
- Energy drains that persist
- Growth edges that resist progress

**When multiple retros show the same pattern:**
1. Surface the pattern explicitly: "I've noticed this theme in your last 3 reviews..."
2. Suggest profile update with elevated importance
3. Consider whether this indicates a growth edge needing focused attention

**Profile update format for patterns:**
```markdown
### Recurring Patterns (from retrospectives)

- **[Pattern name]** — [Description]. First noted [date], confirmed [dates].
  - Contexts where this shows up: [list]
  - What triggers it: [if known]
  - What helps: [if known]
```

### Growth Edge Tracking by Role

The personal profile should track growth edges organized by life role:

**Roles to track:**
- **Provider** - Financial, career, work ethic growth edges
- **Father** - Parenting, {{child_name}} relationship growth edges
- **Partner** - {{partner_name}} relationship, communication growth edges
- **Self** - Health, energy, personal development growth edges
- **Professional** - Work style, leadership, collaboration growth edges

**Profile section to maintain:**
```markdown
## Growth Edges by Role

### Provider
- [Growth edge]: [Context and progress]

### Father
- [Growth edge]: [Context and progress]
- Listening over lecturing: Ongoing work to let {{child_name}} lead conversations

### Partner
- [Growth edge]: [Context and progress]
- INTJ warmth in communication: Adding explicit appreciation

### Self
- [Growth edge]: [Context and progress]

### Professional
- [Growth edge]: [Context and progress]
```

**Update triggers:**
- Role-specific retrospective questions surface patterns
- Failure mode proximity assessments reveal drift
- Board of Advisors deliberations highlight role-specific growth areas
- Explicit feedback on role performance

**Integration with role failure modes:**
Cross-reference `workspace/3-Resources/References/role-failure-modes.md` when updating growth edges:
- If proximity rating > 6 on any failure mode, flag as active growth edge
- Track movement toward or away from failure modes over time

### Retrospective-to-Profile Pipeline

Create a systematic flow from retrospectives to profile updates:

**During retrospective processing:**
1. Complete the retrospective (daily/weekly/monthly/quarterly/annual)
2. Identify any breakthrough insights about self
3. Check if insight is already in profile (avoid duplication)
4. If new or refined: Add to appropriate profile section
5. If pattern across retros: Elevate to "Recurring Patterns" section
6. Update role-specific growth edges if relevant
7. Update `*Last updated: YYYY-MM-DD*` timestamp

**Profile sections fed by retrospectives:**
| Retro Type | Primary Profile Sections |
|------------|-------------------------|
| Daily micro | Rarely updates profile |
| Weekly | Working Style, Decision Patterns |
| Monthly | Weaknesses, Historical Patterns |
| Quarterly | All sections, Growth Edges |
| Annual | Identity-level sections, Recurring Patterns |
