---
description: Quarterly retrospective using Sailboat metaphor for strategic alignment
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Quarterly Retrospective Command

Guide the user through a **3-4 hour quarterly retrospective** using the Sailboat metaphor. This is a strategic alignment exercise that surfaces where you're heading, what's propelling you, what's holding you back, and what dangers lie ahead.

> **Coaching Reminder**: Quarterly retrospectives are strategic, not tactical. This is about direction and systems, not individual tasks. Apply the Dalio principle: Pain + Reflection = Progress.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Monthly retros**: `workspace/3-Resources/Reviews/Monthly/`
- **Template**: `[[quarterly-retro]]` in `workspace/3-Resources/Templates/Retrospectives/`
- **Output location**: `workspace/3-Resources/Reviews/Quarterly/YYYY-QX-retro.md`
- **Foundation**: `workspace/2-Areas/Personal/foundation.md`
- **Goals**: `workspace/2-Areas/Personal/goals/`

## Process

Execute these steps **conversationally**, allowing deep exploration. This is not a quick check-in.

### Step 1: Gather Context (20 min)

1. **Get quarter boundaries**
   ```bash
   # Determine current quarter
   date +%Y-%m-%d
   ```

2. **Aggregate quarter data**:
   - Read all 3 monthly retros for the quarter
   - Goals progress across the quarter
   - Project completions and abandonments
   - Key metrics trends
   - Role balance trends

3. **Read foundation document** for mission/vision alignment check

4. **Present summary**:
   ```
   "Q[X] Summary:
   - Monthly scores: [X, Y, Z] → Average: [avg]
   - Projects completed: [X]
   - Goals progress: [summary]
   - Biggest wins from monthly retros: [list]
   - Recurring themes: [patterns]"
   ```

### Step 2: Set the Stage (10 min)

Open with the Dalio principle:
> "Pain + Reflection = Progress. This quarter brought both wins and struggles. Let's extract the lessons and strengthen our systems."

Ask: "What's your overall feeling about this quarter, 1-10?"

Ask: "If this quarter were a chapter in your life story, what would you title it?"

### Step 3: The Sailboat Metaphor (60 min)

Explain the metaphor:
> "Imagine your life/work as a sailboat. We'll examine each element to understand where you are and where you're heading."

#### Island - Where You're Heading (10 min)

Ask: "What destination are you sailing toward? What does 'success' look like by end of next quarter?"

Prompt if needed:
- "What would make Q[X+1] a success?"
- "What would you be proud to have accomplished?"
- "What does your vision call you toward?"

**Capture the destination vision.**

**Alignment check**: Does this align with your mission and vision in foundation.md?

#### Wind - What Propelled You (15 min)

Ask: "What forces moved you forward this quarter? What gave you momentum?"

Categories to explore:
- **People**: Who helped you succeed?
- **Systems**: What processes worked?
- **Habits**: What practices served you?
- **Mindsets**: What mental models helped?
- **Resources**: What tools/assets enabled progress?

**Capture 5-8 wind elements.**

Ask: "Which of these winds can you harness more strongly next quarter?"

#### Anchors - What Held You Back (15 min)

Ask: "What slowed you down or held you in place? What anchors are dragging?"

Categories to explore:
- **People**: Who drained your energy or blocked progress?
- **Systems**: What processes failed?
- **Habits**: What patterns sabotaged you?
- **Mindsets**: What beliefs limited you?
- **Resources**: What was missing?

**Capture 5-8 anchor elements.**

**Coaching moment**: For each anchor, ask: "Is this within your control to cut loose? What's the real cost of keeping this anchor?"

Ask: "Which anchors MUST you cut to reach your destination?"

#### Rocks - Dangers Ahead (10 min)

Ask: "What dangers could sink you next quarter? What rocks lie beneath the surface?"

Prompt if needed:
- "What risks are you avoiding thinking about?"
- "What could blindside you?"
- "What assumptions might be wrong?"
- "What would your pre-mortem reveal?"

**Capture 3-5 rocks.**

For each rock, identify:
- Early warning signs
- Mitigation strategy

#### Sun - What Energizes You (10 min)

Ask: "What gives you energy and joy? What makes the journey worthwhile?"

Prompt if needed:
- "What activities put you in flow?"
- "What relationships nurture you?"
- "What parts of your work do you love?"
- "What made you feel alive this quarter?"

**Capture 5-8 sun elements.**

**Key insight**: The sun elements are non-negotiables. Protect these fiercely.

### Step 4: Pain + Reflection Analysis (30 min)

Following the Dalio principle, examine the quarter's biggest pains.

#### Identify the Pains

Ask: "What were the 3-5 biggest pains, failures, or setbacks this quarter?"

For each pain:
- What happened?
- What did it reveal about your systems/approaches?
- What principle or lesson can you extract?

#### Extract Principles

For each pain, ask: "What principle would prevent this in the future?"

Format: **If [situation], then [action/response].**

Example:
- Pain: "Missed deadline because I over-committed"
- Principle: "If I'm tempted to say yes to a new commitment, then I must first identify what I'll say no to."

**Capture 2-3 new principles.**

### Step 5: Goals Review (20 min)

Review each active goal:

| Goal | Start of Q | End of Q | Status | Notes |
|------|-----------|----------|--------|-------|
| | | | On Track / Behind / Completed / Abandoned | |

For each goal, ask:
- "Is this still the right goal?"
- "What's blocking progress?"
- "Should this continue, pivot, or be abandoned?"

**Coaching moment**: Sunk cost check - "Would you start this goal today, knowing what you know now?"

### Step 6: Role Balance (15 min)

Quarterly role assessment:

| Role | Q Average | Trend | Sustainability |
|------|-----------|-------|----------------|
| Father | | ↑↓→ | Yes/No |
| Partner | | | |
| Professional (AB) | | | |
| Professional (144) | | | |
| Professional (EMC) | | | |
| Self | | | |

Ask: "Which role is most out of balance? What would bring it back into alignment?"

**Key question**: "Are you enjoying the journey, or just surviving it?"

### Step 7: Strategic Alignment (20 min)

Check alignment with foundation:

#### Identity Check
Read foundation.md identity statement.
Ask: "Did your actions this quarter reflect this identity? Where did you show up as this person? Where did you fail to?"

#### Mission Check
Read foundation.md mission statement.
Ask: "Did this quarter serve your mission? What would make next quarter more aligned?"

#### Vision Check
Read foundation.md vision statement.
Ask: "Are you on track toward this vision? What course corrections are needed?"

#### Principles Check
Ask: "Which principles did you honor? Which did you violate? What needs reinforcement?"

### Step 8: Generate Insights & Actions (20 min)

#### Key Insights
Based on the full retrospective, ask: "What are the 3-5 biggest insights from this quarter?"

#### Systemic Changes
Ask: "What SYSTEMS need to change, not just behaviors?"

Categories:
- Process changes
- Habit changes
- Environment changes
- Relationship changes
- Tool/resource changes

#### Actions for Next Quarter
Ask: "What 3-5 strategic actions will define next quarter?"

**Action Item Format:**
```
| Action | Category | Impact (1-10) | Deadline | Success Metric |
|--------|----------|---------------|----------|----------------|
```

Rules:
- Maximum 5 actions
- Focus on systemic changes, not individual tasks
- Each must trace to a sailboat element or pain analysis
- Include at least one "anchor to cut"

### Step 9: Close (15 min)

#### Create Next Quarter Theme
Ask: "If next quarter has a theme or mantra, what is it?"

#### Schedule Key Dates
- Monthly retros for next quarter
- Quarterly retro for next quarter (schedule 2 years out)
- Key milestones and deadlines

#### Final Summary

```markdown
## Quarterly Retrospective Summary - Q[X] [Year]

**Overall Quarter Score**: X/10
**Chapter Title**: "[their title]"
**Next Quarter Theme**: "[mantra]"

**Destination (Island)**: [vision summary]

**Winds to Harness**:
1. [top wind]
2. [second wind]

**Anchors to Cut**:
1. [top anchor]
2. [second anchor]

**Rocks to Navigate**:
1. [top risk + mitigation]

**Principles Extracted**:
1. If [X], then [Y]

**Strategic Actions**:
1. [action 1]
2. [action 2]
3. [action 3]
```

Closing prompt:
- "You've done the deep work. You know where you're going, what's helping, what's hindering, and what dangers lie ahead. Now sail with intention."

## Output

Create the quarterly retro document:

```markdown
---
title: "Q[X] [Year] Retrospective"
type: retrospective
period: quarterly
date: YYYY-MM-DD
overall_score: X
chapter_title: "[title]"
next_quarter_theme: "[theme]"
---

# Q[X] [Year] Retrospective

**Overall Score**: X/10
**Chapter Title**: "[title]"

## The Sailboat

### Island - Destination
[Vision for next quarter]

### Wind - What Propelled You
1.
2.
3.
4.
5.

**Winds to harness more**: [list]

### Anchors - What Held You Back
1.
2.
3.
4.
5.

**Anchors to cut**: [list]

### Rocks - Dangers Ahead
| Risk | Early Warning Signs | Mitigation |
|------|---------------------|------------|
| | | |

### Sun - What Energizes You
1.
2.
3.
4.
5.

## Pain + Reflection

### Biggest Pains/Failures
1. **[Pain]**: [What happened, what it revealed]
2. **[Pain]**: [What happened, what it revealed]
3. **[Pain]**: [What happened, what it revealed]

### Principles Extracted
1. If [situation], then [action]
2. If [situation], then [action]

## Goals Review

| Goal | Progress | Status | Next Steps |
|------|----------|--------|------------|
| | | | |

## Role Balance

| Role | Quarter Average | Trend | Sustainability | Notes |
|------|-----------------|-------|----------------|-------|
| Father | | | | |
| Partner | | | | |
| Professional | | | | |
| Self | | | | |

**Role needing most attention**: [role]

## Strategic Alignment

### Identity: [Aligned/Needs Work]
[Notes]

### Mission: [Aligned/Needs Work]
[Notes]

### Vision: [On Track/Course Correction Needed]
[Notes]

### Principles Honored/Violated
- Honored: [list]
- Violated: [list]

## Key Insights
1.
2.
3.

## Systemic Changes Needed
1.
2.
3.

## Strategic Actions for Next Quarter

| Action | Category | Impact | Deadline | Success Metric |
|--------|----------|--------|----------|----------------|
| | | | | |

## Next Quarter

**Theme**: "[mantra]"

**Monthly retros scheduled**:
- [ ] [Month 1 - last Friday]
- [ ] [Month 2 - last Friday]
- [ ] [Month 3 - last Friday]

**Next quarterly retro**: [date]

---
*"Pain + Reflection = Progress" - Ray Dalio*
```

**Location**: `workspace/3-Resources/Reviews/Quarterly/YYYY-QX-retro.md`

## Interaction Guidelines

- **Allow 3-4 hours** - This is a strategic session, not a quick check
- **Schedule in advance** - Don't try to fit this into a busy day
- **Use the metaphor** - The sailboat framing makes abstract concepts concrete
- **Go deep on pain** - The Pain + Reflection section is where real learning happens
- **Strategic, not tactical** - Focus on systems and direction, not individual tasks
- **Connect to foundation** - Everything should trace back to identity, mission, vision
- **INTJ consideration** - Trust the pattern recognition (Ni), but include emotional/relational elements
- **Schedule ahead** - Before closing, schedule quarterly retros for the next 2 years

## Examples

**Example Wind**:
- Morning deep work routine (protected focus time)
- Weekly State of Union with {{partner_name}}
- Collaboration partners
- Claude Code system for task management

**Example Anchor**:
- Saying yes to too many commitments
- Checking Slack during focus blocks
- Not delegating enough at EMC
- Skipping exercise when stressed

**Example Rock**:
- EMC cash flow if sales don't improve
- Burnout if work/life balance continues declining
- Relationship strain if partner role stays neglected

**Example Principle**:
- If I'm considering a new commitment, then I must identify what existing commitment I'll reduce.
- If my energy drops below 5/10 two days in a row, then I take a half-day for recovery.
