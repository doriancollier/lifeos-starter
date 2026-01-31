---
description: Run pre-mortem exercise on a decision or project
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Skill
argument: Decision or project to analyze
---

# Pre-Mortem Command

Run a structured pre-mortem exercise on the decision or project provided in `$ARGUMENTS`. This uses prospective hindsight to identify risks before they become failures.

> **Core Principle**: Research shows imagining an event has *already occurred* increases accuracy in identifying failure reasons by 30%. We shift from "What might go wrong?" to "It failed. What happened?"

## Context

- **Templates directory**: `3-Resources/Templates/Decisions/`
- **Output location**: Depends on type (see below)
- **Pre-mortem skill**: `.claude/skills/pre-mortem/SKILL.md`
- **Decision frameworks**: `3-Resources/References/decision-frameworks.md`

## Process

### Step 1: Parse Input

If `$ARGUMENTS` is provided, use it as the decision/project.

If not provided, ask: "What decision or project would you like to run a pre-mortem on?"

### Step 2: Determine Type

Ask: "What type of decision is this?"

**Types**:
1. **Individual Decision** - Personal career, financial, strategic choices
   - Template: `[[premortem-individual]]`
   - Time: 30-45 minutes
   - Output: `3-Resources/Decisions/YYYY-MM-DD-[decision-slug].md`

2. **Team/Project Decision** - Collaborative projects, work initiatives
   - Template: `[[premortem-team]]`
   - Time: 60 minutes
   - Output: `1-Projects/Current/[project-name]/premortem.md`

3. **Life Decision** - Major life transitions (relationship, family, relocation, major career change)
   - Template: `[[premortem-life-decision]]`
   - Time: 90 minutes
   - Uses **Double-Barreled Approach** (both failure AND regret scenarios)
   - Output: `3-Resources/Decisions/YYYY-MM-DD-[decision-slug].md`

### Step 3: Setup

1. **State the decision clearly**
   Ask: "In one sentence, what is the decision you're considering?"

2. **Set the future date**
   - Projects: 3-6 months out
   - Individual decisions: 6-12 months out
   - Life decisions: 2-5 years out

   Ask: "What timeframe makes sense for evaluating this? When would you know if it succeeded or failed?"

3. **Note current confidence level**
   Ask: "On a scale of 1-10, how confident are you that this will succeed?"

   If above 8: "High confidence can be a red flag for blind spots. Let's dig deep."

### Step 4: Time Travel (Failure Scenario)

Set the scene with prospective hindsight:

> "It is [future date]. You made this decision, and it has failed spectacularly. You deeply regret this choice. Your life/project/business is worse for it."

**Pause for effect.** Let this sink in.

### Step 5: Generate Failure Reasons

Ask: "In this scenario where it failed, what went wrong? Give me 10-15 specific reasons."

Guide with prompts:
- "What's the most likely reason this fails?"
- "What's the most threatening reason (low probability, catastrophic impact)?"
- "What key assumptions have you made? What if they're wrong?"
- "What external factors could blindside you?"
- "What could YOU do to cause your own failure?"
- **"What are you not talking about?"** (surface the Elephant)

**Push past the obvious** - the first 5 reasons are usually surface-level. The valuable insights come from reasons 6-15.

**Capture 10-15 failure reasons.**

### Step 6: Categorize - Tigers, Paper Tigers, Elephants

Explain the framework:

| Category | Definition | Action |
|----------|------------|--------|
| **Tiger** | Clear threat that will hurt if unaddressed | Mitigation plan immediately |
| **Paper Tiger** | Apparent threat you're not worried about | Acknowledge and monitor |
| **Elephant** | What you're avoiding discussing | Surface and address FIRST |

For each failure reason, ask: "Is this a Tiger, Paper Tiger, or Elephant?"

**Key insight**: Elephants are often the actual causes of failure. Push hard on: "What's the elephant in the room that you're avoiding?"

### Step 7: Double-Barreled Analysis (Life Decisions Only)

For life decisions, run a second scenario:

> "Now let's flip it. It is [future date]. You did NOT make this decision. You played it safe. You deeply regret NOT taking this chance. What did you miss?"

Ask: "In this scenario where you regret NOT acting, what opportunities did you lose?"

**Capture 5-10 regret reasons for inaction.**

This prevents one-sided risk analysis that leads to paralysis.

### Step 8: Probability & Impact Assessment

For each Tiger, assess:

| Risk | Probability (L/M/H) | Impact (L/M/H) | Priority |
|------|---------------------|----------------|----------|
| | | | |

Priority = High probability AND High impact risks first.

### Step 9: Mitigation Strategies

For each Tiger (starting with highest priority), develop mitigations:

Ask for each: "What single action would most reduce this risk?"

Capture:
- **Preventive action**: What stops this from happening?
- **Owner**: Who is responsible?
- **Deadline**: By when?
- **Success metric**: How do we know it worked?
- **Early warning signs**: What signals this risk is materializing?

**Mitigation categories** to consider:
1. Process Improvements
2. Contingency Plans
3. Skill Development
4. Technology/Tools
5. Communication Strategies

### Step 10: Red Flags to Monitor

Based on the risks, identify early warning signs:

Ask: "What signals would tell you this is going wrong before it's too late?"

**Capture 3-5 red flags** with specific, observable triggers.

### Step 11: Decision

Present the decision options:

Ask: "Based on this analysis, what's your decision?"

- [ ] **Proceed as planned** - Risks are manageable, mitigations in place
- [ ] **Proceed with modifications** - Specify what changes
- [ ] **Delay until** - Specify what condition must be met
- [ ] **Abandon** - Risks outweigh potential benefits

**Coaching moment**: If they're proceeding despite significant unmitigated Tigers, challenge: "You've identified serious risks without clear mitigations. Is this confidence or overconfidence?"

### Step 12: Commitments (If Proceeding)

If proceeding, capture commitments:

Ask: "What do you commit to?"
- Specific actions from mitigation strategies
- Red flags to monitor
- Checkpoint date for review

**Time limit reminder**: Pre-mortems should end in decisions. If no decision is made, the pre-mortem becomes procrastination disguised as planning.

### Step 13: Integration

**For projects**: Link pre-mortem to project file and add mitigation tasks to daily notes.

**For decisions**: Add checkpoint review to calendar.

**Offer**: "Would you like me to bring this to the Board of Advisors for additional perspective on blind spots?"

If yes, invoke the `board:advise` skill with pre-mortem summary.

## Output

### Individual Decision Pre-Mortem
```markdown
---
title: "Pre-Mortem: [Decision]"
type: premortem
category: individual
date: YYYY-MM-DD
decision: "[decision statement]"
status: [proceed/proceed-modified/delay/abandon]
confidence_before: X
confidence_after: Y
---

# Pre-Mortem: [Decision]

**Decision Being Considered**: [Description]
**Timeline**: Decision by [date] | Outcome evaluation by [future date]
**Initial Confidence**: X/10

## Pre-Mortem Scenario
> It is [future date]. This has failed spectacularly. You deeply regret this choice.

## Failure Reasons
1.
2.
3.
...
10.

## Categorization

### Tigers (Real threats requiring action)
-

### Paper Tigers (Not actually worrying)
-

### Elephants (Avoiding thinking about)
-

## Probability & Impact Assessment

| Risk | Probability | Impact | Priority |
|------|-------------|--------|----------|
| | L/M/H | L/M/H | |

## Mitigation Strategies

| Risk | Preventive Action | Owner | Deadline | Success Metric |
|------|-------------------|-------|----------|----------------|
| | | | | |

## Early Warning Signs
- Red flag 1: [observable trigger]
- Red flag 2: [observable trigger]
- Red flag 3: [observable trigger]

## Decision
- [x] [Selected option]

**Final Confidence**: Y/10

## Commitments (If Proceeding)
- I commit to: [action]
- I will monitor: [red flags]
- Checkpoint date: [date]

---
*Pre-mortem completed: YYYY-MM-DD*
```

### Life Decision Pre-Mortem (adds Double-Barreled section)
```markdown
## Double-Barreled Analysis

### If I Do This and It Fails
[Failure reasons from Step 5]

### If I DON'T Do This and Regret It
1.
2.
3.
...

### Balance Assessment
[Which scenario carries more weight?]
```

### Location

- **Individual/Life decisions**: `3-Resources/Decisions/YYYY-MM-DD-[decision-slug].md`
- **Team/Project decisions**: `1-Projects/Current/[project-name]/premortem.md`

## Interaction Guidelines

- **Create psychological safety** - This is about preparing, not catastrophizing
- **Push past surface answers** - The valuable insights are in reasons 6-15
- **Surface the Elephant** - Ask repeatedly: "What are we not talking about?"
- **Time limit** - 30 min individual, 60 min team, 90 min life decisions
- **End in decision** - Pre-mortems that don't end in decisions are procrastination
- **Connect to Stoic practice** - This is premeditatio malorum made actionable
- **Challenge overconfidence** - High confidence without mitigations is a red flag

## Coaching Triggers

Use these prompts during the pre-mortem:

- "Is this confidence or overconfidence?"
- "What would your future self regret about this?"
- "What elephant is in the room you're not discussing?"
- "What assumption would hurt most if it's wrong?"
- "What would you tell your best friend to avoid here?"

## Examples

**Example Failure Reasons (Career Change)**:
1. New role doesn't match expectations
2. Skills don't transfer as well as hoped
3. Company culture is toxic
4. Economic downturn leads to layoffs (LIFO)
5. Miss the relationships from current role
6. Imposter syndrome becomes paralyzing
7. Health insurance gap causes issues
8. Family stress from transition period
9. **Elephant**: Not ready to leave comfort zone, using external reasons to avoid admitting fear
10. Realize too late the grass wasn't greener

**Example Mitigation**:
| Risk | Preventive Action | Owner | Deadline | Success Metric |
|------|-------------------|-------|----------|----------------|
| Skills don't transfer | Complete relevant certification before transition | {{user_first_name}} | Mar 15 | Cert in hand |
| Health insurance gap | Research COBRA and marketplace options, budget 6 months | {{user_first_name}} | Feb 1 | Plan documented |
| Imposter syndrome | Line up mentor at new company before starting | {{user_first_name}} | Before start | Mentor confirmed |

**Example Double-Barreled (Life Decision)**:
- **If I do this and fail**: Wasted 2 years, financial setback, embarrassment
- **If I don't do this and regret**: Forever wonder "what if", stay stuck in unfulfilling situation, regret playing it safe when I had the chance
