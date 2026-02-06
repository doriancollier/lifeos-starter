---
description: Annual planning - set yearly theme and 3-5 goals aligned with your mission
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Annual Plan Command

Guide the user through creating their comprehensive annual year plan. This builds on the annual review and connects to their foundation.

> **Coaching Reminder**: You are a Relentless Challenger. Challenge the "same but more" fallacy. Every new goal requires a trade-off. Connect goals to mission and vision. Theme must apply to ALL life domains.

## Context

- **Foundation**: `workspace/2-Areas/Personal/foundation.md`
- **Review input**: `workspace/2-Areas/Personal/Years/[YEAR-1]-Retrospective.md`
- **Previous year**: `workspace/2-Areas/Personal/Years/[YEAR-1].md`
- **Output**: `workspace/2-Areas/Personal/Years/[YEAR].md`
- **Template reference**: `workspace/3-Resources/Templates/Planning/annual-year.md`
- **Time investment**: 2-4 hours (can be spread across sessions)

## Arguments

- `$ARGUMENTS` - Optional: Year to plan (defaults to next year or current if early January)

## Output Document Structure

The annual year document follows this structure (see template for details):

1. **Quick Reference** — Scannable summary with theme, goals, key dates
2. **Year Context** — Life situation, family context, key dates
3. **Theme** — Decision filter with narrative arc and practical applications
4. **Vision** — December 31 success description for each goal
5. **Anti-Goals** — Explicit commitments of what NOT to do
6. **Rhythms** — Daily/Weekly/Monthly/Quarterly/Annual cadences
7. **Annual Goals** — 3-5 goals with embedded WOOP, milestones, strategy
8. **Role Balance** — How you'll show up in each life role
9. **Warning Signs** — Red flags and failure mode pre-mortem
10. **Projects** — Active projects and how they serve the theme
11. **Key Relationships** — People to invest in
12. **Opportunities** — Framework for evaluating new opportunities
13. **Q1 Priorities** — Detailed current quarter focus
14. **Quarterly Plans** — Links to Q1-Q4 breakdown files
15. **Changelog** — Track significant updates

## Process

### Step 1: Setup & Context Loading

1. **Determine planning year**
   - If provided, use that year
   - Otherwise: if Dec/Jan, plan upcoming year

2. **Load essential context**:
   - Read `workspace/2-Areas/Personal/foundation.md` (mission, vision, principles)
   - Read previous year's retrospective (`[YEAR-1]-Retrospective.md`)
   - Read previous year's plan if exists (`[YEAR-1].md`)
   - Check for any existing year context files

3. **Summarize learnings**:
   Present key insights from the review:
   - Top wins to build on
   - Key lessons learned
   - Energy patterns (deposits/drains)
   - Role balance gaps
   - Foundation alignment issues

### Step 2: Year Context

Before goals, establish the year's context:

**Gather information about**:
- Family/dependent situation (ages, grades, milestones)
- Major life events expected
- Work/business transitions
- Key dates already known
- Previous year's theme and how it concluded

This becomes the **Year Context** section.

### Step 3: Vision Casting

Ask: "Close your eyes for a moment. It's December 31st of [YEAR]. You're looking back on an incredible year. What happened? What did you accomplish? How do you feel?"

Let them paint the picture. Listen for:
- What domains appear? (Health, relationships, career, growth)
- What emotions surface?
- What's conspicuously absent?

**Coaching**: "I notice you didn't mention [absent domain]. Is that intentional?"

Capture rich descriptions for each goal area — this becomes the **Vision** section.

### Step 4: Annual Theme Selection

The theme is a decision filter for the entire year.

Present the concept:
- "Your theme is a single word or phrase that guides ALL decisions this year."
- "Unlike goals (pass/fail), themes are flexible—they can be interpreted many ways."
- "This theme creates a narrative arc from last year."

Ask: "What word or phrase captures what this year needs to be about?"

**Prompt exploration**:
- "Looking at [previous year's theme], what's the natural next chapter?"
- "What would help you show up as the person you're becoming?"
- "What would make you proud to say this year was 'The Year of [X]'?"

**Validation questions**:
- "Does this apply to your health? Your relationships? Your work? Your family?"
- "When an opportunity comes, can you ask 'Does this align with [theme]?'"
- "What's the decision filter question this theme creates?"

Capture:
- Theme name
- Narrative arc (previous year → this year)
- What it means in practice
- Decision filter question
- Practical applications

### Step 5: Anti-Goals

This is as important as the goals.

Ask: "What GOOD things are you explicitly saying NO to this year?"

**Coaching prompts**:
- "What opportunities, if offered, should you decline?"
- "What habits or activities need to stop to make room?"
- "What would distract you from your theme?"
- "What patterns from last year should you explicitly avoid?"

Aim for 6-8 anti-goals with rationale for each.

### Step 6: Set 3-5 Annual Goals

**Critical constraint**: Maximum 5 goals. Force ruthless prioritization.

For each goal:

1. **Identify the domain and name**

2. **Connect to purpose**
   Ask: "Why does this matter? How does it serve your mission/vision?"

3. **Define success criteria**
   Ask: "How will you know you succeeded? What are the measurable outcomes?"

4. **Develop strategy** (if applicable)
   What levers will you pull? What's the approach?

5. **Break into quarterly milestones**
   Ask: "What would 'on track' look like at end of Q1? Q2? Q3? Q4?"

6. **Identify the trade-off**
   Ask: "**What are you putting down to pick this up?**"

7. **Create WOOP** (embedded under the goal):
   - **Wish**: The goal
   - **Outcome**: The emotional/practical benefit when achieved
   - **Obstacle**: The internal obstacle most likely to interfere (YOU control)
   - **Plan**: "When [obstacle], then I will [response]"
   - **Accountability**: External accountability mechanism

8. **Link related files and projects**

### Step 7: Rhythms

Establish the recurring commitments that compound over time:

**Daily**:
- Non-negotiable habits (no exceptions)
- High-impact habits (prioritize)

**Weekly**:
- Relationship rhythms (partner check-in, child time)
- Review rhythms
- Health rhythms

**Monthly**:
- Financial review
- Goals pulse check

**Quarterly**:
- Goal review
- Rocks review
- Quarter-specific focus areas

**Annual**:
- Year-end reflection checklist
- Reflection questions for December

### Step 8: Role Balance Check

Reference the roles from foundation.md:

For each role:
- Rate last year (1-10)
- Set target for this year
- Define key intention

**Coaching**: Surface the professional over-prioritization bias:
- "Last year's review showed [pattern]. Is this year's plan addressing it?"
- "I notice X of your 5 goals are professional. Is that intentional?"

### Step 9: Warning Signs & Failure Modes

**Red Flags**: Identify 4-6 warning signs that require immediate action
- What it means
- Required response

**Pre-Mortem**: If the year fails, what happened?
- Identify 4-6 failure modes
- Assess probability
- Define prevention strategy

**Reconvene Triggers**: When to seek help or reassess

### Step 10: Projects, Relationships, Opportunities

**Projects**: How existing projects serve the theme
- No new ventures unless explicitly part of goals
- Focus on deepening, not expanding

**Relationships**: Key people to invest in
- Link to goals
- Define milestones

**Opportunities**: Create the evaluation framework
- Decision filter application
- Alignment check for known opportunities

### Step 11: Q1 Priorities

Detail the first quarter:
- Month-by-month focus
- Week-by-week priorities if relevant
- Priority stack (numbered)
- Critical context
- Capacity overflow guidance
- What's on hold

### Step 12: Create the Document

Write to `workspace/2-Areas/Personal/Years/[YEAR].md` using the structure from the template.

**Frontmatter**:
```yaml
---
title: "[YEAR] - [Theme]"
type: year-planning
year: [YEAR]
theme: "[Theme]"
status: active
partner: "[[]]"
created: [today]
modified: [today]
goals:
  - "Goal 1 Name"
  - "Goal 2 Name"
  - "Goal 3 Name"
  - "Goal 4 Name"
  - "Goal 5 Name"
---
```

### Step 13: Commitment Ritual

Close with a commitment:

Ask: "Say your theme out loud. Say your top goal out loud."

Coaching send-off:
- "You've set a clear direction. The theme of [X] will guide your decisions."
- "Remember: Every goal required a trade-off. Honor those anti-goals."
- "Your first quarterly plan is ready to be created. Run `/quarter:plan` to translate these into 90-day rocks."

## Output

By the end, the user should have:
1. **Comprehensive year document** at `workspace/2-Areas/Personal/Years/[YEAR].md`
2. **Annual theme** that serves as a decision filter for all domains
3. **3-5 annual goals** with embedded WOOP, quarterly milestones, and strategies
4. **Anti-goals** of explicit declines
5. **Rhythms** for all planning horizons
6. **Role intentions** with professional bias checked
7. **Warning signs and failure modes** identified
8. **Q1 priorities** detailed and actionable
9. **Readiness** to proceed to quarterly planning

## Interaction Guidelines

- **Challenge the "same but more" fallacy** — Force trade-offs for every addition
- **Theme must be universal** — If it only applies to work, push back
- **Maximum 5 goals** — Don't allow goal creep
- **WOOP is embedded** — Each goal has its own WOOP, not a separate section
- **Connect to foundation** — Reference mission/vision throughout
- **Role balance** — Surface professional over-prioritization
- **Make it concrete** — Vague goals become measurable milestones
- **Create narrative arc** — Connect this year's theme to last year's
- **Include context** — Life situation grounds the goals in reality

## Multi-Session Support

This process can span multiple sessions. Track progress:
- Save drafts to `workspace/8-Scratch/annual-plan-draft-[YEAR].md`
- Resume by reading the draft and continuing
- Move to final location when complete

## Examples

```
/annual:plan
# Plans next year (or current if early January)

/annual:plan 2027
# Plans 2027 specifically
```

## Related

- `/annual:review` — Complete BEFORE annual planning
- `/quarter:plan` — Create after annual plan is complete
- `[[annual-year]]` — Template reference (3-Resources/Templates/Planning/)
