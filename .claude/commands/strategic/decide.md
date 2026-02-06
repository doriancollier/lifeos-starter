---
description: Guided strategic decision-making with door-type analysis
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
argument: Decision to analyze
---

# Strategic Decision Command

Guide the user through a **structured strategic decision-making process** for the decision provided in `$ARGUMENTS`. This command determines whether a decision is a one-way or two-way door and applies the appropriate framework.

> **Core Principle**: "Some decisions are reversible, and some are not. Make reversible decisions quickly; make irreversible decisions deliberately." - Jeff Bezos (paraphrased)

## Context

- **Decision frameworks**: `workspace/3-Resources/References/decision-frameworks.md`
- **Templates**: `workspace/3-Resources/Templates/Decisions/`
- **Board of Advisors**: `/board:advise`
- **Pre-mortem**: `/premortem:run`

## Process

### Step 1: Parse Input

If `$ARGUMENTS` is provided, use it as the decision.

If not provided, ask: "What decision are you facing?"

### Step 2: Clarify the Decision

Ask: "In one clear sentence, what is the decision you need to make?"

Good format: "[Action/Choice] that would [outcome]"
Example: "Leave my current role to join a startup that would give me equity and leadership experience."

### Step 3: Determine Door Type

Explain the framework:

> **One-Way Door (Type 1)**: Irreversible or very hard to reverse. The world changes fundamentally once you walk through.
>
> **Two-Way Door (Type 2)**: Easily reversible with minimal cost. You can walk back through if it doesn't work.

Ask: "Can you easily reverse this decision if it doesn't work out?"

**Assessment questions**:
- What would it cost (money, time, relationships) to undo this?
- Would undoing it restore you to your current state?
- Would key opportunities be lost if you reversed?
- Could you run a smaller experiment first?

**Classify the decision**:

| Characteristics | One-Way Door | Two-Way Door |
|-----------------|--------------|--------------|
| Reversibility | Very hard or impossible | Easy with low cost |
| Stakes | High | Low to moderate |
| Information needed | More (70-90%) | Less (50-70%) |
| Examples | Quitting a job, having kids, major investment | New feature, hiring (with trial), testing a project |

**Output**: "This is a [One-Way/Two-Way] Door because [reasoning]."

### Step 4A: One-Way Door Process

**Time**: 45-90 minutes
**Template**: `[[strategic-decision-one-way]]`

#### Stakes Assessment

Ask: "What's at stake? What do you stand to gain or lose?"

| Dimension | Upside | Downside |
|-----------|--------|----------|
| Financial | | |
| Career/Opportunity | | |
| Relationships | | |
| Health/Energy | | |
| Time | | |

#### First Principles Check

Ask: "What assumptions are you making? Which might not be true?"

Prompt:
- "Why do you believe this will work?"
- "What's the conventional wisdom here? Is it right?"
- "If you started from scratch, would you design it this way?"

**Capture 3-5 key assumptions.**

#### Asymmetric Opportunity Evaluation

**Step 1: Calculate Maximum Downside**
Ask: "What's the absolute worst outcome? How long would recovery take?"

**Ruin Check**: Would failure wipe you out financially, reputationally, or energetically?
- If ANY dimension shows ruin risk → **Automatic NO**

**Step 2: Assess Upside Potential**
Ask: "What's the realistic best outcome? Does success create compounding returns?"

**Step 3: Check Asymmetry Ratio**

| Ratio | Assessment | Guidance |
|-------|------------|----------|
| < 1:1 | Negative asymmetry | Decline |
| 1:1 - 3:1 | Modest | Needs strong justification |
| 3:1 - 10:1 | Good asymmetry | Serious consideration |
| > 10:1 | Excellent | Strong candidate |

**Step 4: Survival Test**
"Can you survive the worst case?" No = do not proceed.

#### Pre-Mortem Integration

Ask: "Have you done a pre-mortem on this?"

If no, offer: "Should we run `/premortem:run` now? For one-way doors, I strongly recommend it."

If yes, review the Tigers and Elephants identified.

#### Second-Order Thinking

| Order | Question | Effect |
|-------|----------|--------|
| 1st | What happens immediately? | [capture] |
| 2nd | What chain reactions follow? (1-3 years) | [capture] |
| 3rd | What long-term effects emerge? (3-10 years) | [capture] |

**10-10-10 Rule**:
- How will you feel in 10 minutes?
- How will you feel in 10 months?
- How will you feel in 10 years?

#### Advisor Consultation

For major one-way doors, ask: "Should we consult the Board of Advisors?"

If yes, invoke `/board:advise [decision summary]`

If no, ask: "Who else should you consult before deciding?"

#### Via Negativa Check

Ask: "Before adding this, what problem are you solving? Could you solve it by REMOVING something instead?"

Often the best decision is subtraction, not addition.

#### One Reason Rule

Ask: "What's the ONE reason this is the right choice?"

If they list multiple reasons: "Multiple reasons often means you're convincing yourself. What's the single strongest reason?"

> "If you need more than one reason to do something, just don't do it." - Taleb

#### Foundation Alignment

Read foundation.md and check:
- Does this align with your identity?
- Does this serve your mission?
- Does this move toward your vision?
- Does this honor your principles?

If misaligned: "This doesn't seem to align with [specific element]. Is this a values conflict or an evolution of values?"

#### Decision Quality Checklist

Before deciding:
- [ ] Is this really a one-way door? (Or can I convert to two-way with smaller experiment?)
- [ ] Have I done a pre-mortem?
- [ ] Is the upside-to-downside ratio at least 3:1?
- [ ] Can I survive the worst case?
- [ ] Have I thought from first principles (not just copying)?
- [ ] Have I considered 2nd and 3rd order effects?
- [ ] Does this align with my mission and values?
- [ ] Have I consulted the right people?
- [ ] Am I confident, not overconfident?
- [ ] Am I using many reasons to justify? (red flag)

#### Decision

Present options:
- [ ] **Proceed** - Analysis supports moving forward
- [ ] **Proceed with modifications** - Specify changes
- [ ] **Convert to two-way door** - Run smaller experiment first
- [ ] **Delay until** - Specify condition
- [ ] **Decline** - Risks outweigh benefits

---

### Step 4B: Two-Way Door Process

**Time**: 15-30 minutes
**Template**: `[[strategic-decision-two-way]]`

#### Quick Inversion

Ask: "What would guarantee failure with this decision?"

Capture 3-5 failure modes.

Check: "Are you doing any of these things? If not, you're probably fine."

#### Reversibility Confirmation

Confirm the exit path:
- "If this doesn't work, how do you reverse it?"
- "What's the cost of reversing?" (time, money, relationships)
- "What's the trigger for reversing?" (when would you know it's not working)

#### 70% Information Rule

Ask: "Do you have at least 70% of the information you'd want?"

- If yes: **Decide now**
- If no: "What specific information is missing? Can you get it in 24-48 hours?"

For two-way doors, waiting for 100% information is a mistake.

#### Decision

Ask: "What's your decision?"

Set review trigger: "When will you evaluate if this is working?"

---

### Step 5: Capture and Next Steps

#### If Proceeding

Capture:
- **The decision** (clear statement)
- **Key reasons** (1-2 main reasons)
- **First action** (immediate next step)
- **Review date** (when to evaluate)
- **Kill criteria** (what would make you reverse)

Add first action to daily note as A-priority.

#### If Delaying

Capture:
- **The condition** to be met before deciding
- **Deadline** for condition (don't wait indefinitely)
- **Who owns** getting the information/condition met

Add follow-up to calendar.

#### If Declining

Capture:
- **The decision** (clear "no")
- **Key reasons** (why not)
- **What would change your mind** (future reconsideration triggers)

Close the loop—declined decisions are still decisions.

## Output

### One-Way Door Decision Document
```markdown
---
title: "Strategic Decision: [Decision]"
type: strategic-decision
door_type: one-way
date: YYYY-MM-DD
status: [proceed/proceed-modified/delay/decline]
---

# Strategic Decision: [Decision]

**Decision Statement**: [Clear one-sentence description]
**Door Type**: One-Way (irreversible)
**Date**: YYYY-MM-DD

## Stakes Assessment

| Dimension | Upside | Downside |
|-----------|--------|----------|
| Financial | | |
| Career | | |
| Relationships | | |
| Health/Energy | | |
| Time | | |

## Key Assumptions
1.
2.
3.

## Asymmetric Evaluation

**Maximum Downside**: [description]
**Recovery Time**: [timeframe]
**Ruin Risk**: Yes/No

**Realistic Upside**: [description]
**Compounding Returns**: Yes/No

**Asymmetry Ratio**: X:1 - [assessment]

**Survival Test**: Can survive worst case? Yes/No

## Pre-Mortem Summary
**Tigers**: [key risks]
**Elephants**: [avoided topics]
**Mitigations**: [key actions]

## Second-Order Effects

| Order | Effect |
|-------|--------|
| 1st (immediate) | |
| 2nd (1-3 years) | |
| 3rd (3-10 years) | |

**10-10-10**: [summary]

## Foundation Alignment
- Identity: [Aligned/Conflict]
- Mission: [Aligned/Conflict]
- Vision: [Aligned/Conflict]
- Principles: [Aligned/Conflict]

## Via Negativa Check
Could I solve this by removing instead of adding? [response]

## One Reason
The single best reason: [reason]

## Decision Quality Checklist
- [ ] One-way door confirmed
- [ ] Pre-mortem completed
- [ ] Ratio at least 3:1
- [ ] Worst case survivable
- [ ] First principles thinking applied
- [ ] 2nd/3rd order effects considered
- [ ] Foundation aligned
- [ ] Right people consulted
- [ ] Not overconfident

## Decision
**Status**: [Proceed/Proceed with modifications/Delay/Decline]

**Reasoning**: [brief explanation]

## If Proceeding
- **First Action**: [immediate next step]
- **Review Date**: [when to evaluate]
- **Kill Criteria**: [what would make you reverse]

## If Delaying
- **Condition**: [what must be met]
- **Deadline**: [by when]
- **Owner**: [who's responsible]

## Advisors Consulted
- [Name]: [input summary]

---
*Decision recorded: YYYY-MM-DD*
```

### Two-Way Door Decision Document
```markdown
---
title: "Strategic Decision: [Decision]"
type: strategic-decision
door_type: two-way
date: YYYY-MM-DD
status: [proceed/delay/decline]
---

# Strategic Decision: [Decision]

**Decision Statement**: [Clear one-sentence description]
**Door Type**: Two-Way (reversible)
**Date**: YYYY-MM-DD

## Quick Inversion
What would guarantee failure:
1.
2.
3.

**Check**: Am I doing any of these? [response]

## Reversibility
- **Exit Path**: [how to reverse]
- **Reversal Cost**: [time/money/relationships]
- **Trigger for Reversal**: [when would you know]

## Information Check
- Have 70%+ information? Yes/No
- Missing information: [what]
- Can get in 24-48h? Yes/No

## Decision
**Status**: [Proceed/Delay/Decline]

## Next Steps
- **First Action**: [immediate next step]
- **Review Date**: [when to evaluate]
- **Kill Criteria**: [what would make you reverse]

---
*Decision recorded: YYYY-MM-DD*
```

**Location**: `workspace/3-Resources/Decisions/YYYY-MM-DD-[decision-slug].md`

## Interaction Guidelines

- **Categorize first** - Don't apply one-way thinking to two-way doors (or vice versa)
- **Convert when possible** - Many one-way doors can become two-way with smaller experiments
- **70% for two-way** - Don't over-analyze reversible decisions
- **Deep for one-way** - Take time, consult others, run pre-mortem
- **One reason rule** - If they list many reasons, they're rationalizing
- **Foundation alignment** - Major decisions must trace to identity/mission/vision
- **Set review dates** - Every decision needs a checkpoint

## Coaching Prompts

- "Is this really irreversible, or could you run a smaller experiment first?"
- "What's the ONE reason this is right?"
- "Can you survive the worst case?"
- "Is this confidence or overconfidence?"
- "Does this align with protecting what matters?"
- "What would the person you're becoming do?"
- "Are you adding when you should be subtracting?"

## Examples

**Example One-Way Door**:
- Leaving current job to start a company
- Having a child
- Buying a house
- Ending a partnership
- Major investment (>10% of assets)

**Example Two-Way Door**:
- Trying a new morning routine
- Testing a product feature
- Hiring with a trial period
- Starting a side project
- Changing a process/workflow

**Example Conversion** (One-Way to Two-Way):
- Original: "Quit job to start company"
- Converted: "Start company as nights/weekends project for 6 months to validate, then quit if it has traction"
