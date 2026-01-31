---
name: goals-tracking
description: Track goals, review progress, and manage opportunities. Use during weekly planning, goal reviews, or when capturing new opportunities that need evaluation.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Goals Tracking Skill

Manages the goals system including annual goals, goal-project linkage, and opportunity pipeline.

## Goals Location

**Source of Truth**: Year files in `/2-Areas/Personal/Years/`
- `2025.md` - Theme: "About Experimentation"
- `2026.md` - Theme: "Nothing New"

**Supporting Files**:
- `/7-MOCs/Opportunities-Pipeline.md` - Opportunity tracking and evaluation
- `/1-Projects/Current/2026-Annual-Planning/2026-Goals-Draft.md` - Working draft for 2026

## Goal Categories

### Professional Goals
- Personal Brand, Legal Structures, Career direction
- Company-specific: {{company_1_name}}, EMC, {{company_2_name}}
- Consulting/Income goals

### Relationship Goals
- Family: [[{{partner_name}}]], [[{{child_name}} {{user_last_name}}]]
- Professional: Key colleagues (see contacts-config.json)
- Personal: Friends, extended family

### Health & Wellness Goals
- Exercise, meditation, weight
- Energy management

### Financial Goals
- Income targets, expense reduction
- Legal/tax items

### Skill Development Goals
- Areas to deepen (per "Nothing New")
- Knowledge areas

## Goal Structure (in Year Files)

```markdown
## Goals

### [Category] Goals

| Goal | Key Results | Status | Projects | Progress |
|------|-------------|--------|----------|----------|
| Goal Name | Measurable outcomes | 🔴🟡🟢 | [[Links]] | X% |

### Relationship Goals (per "Nothing New")

| Relationship | 2026 Investment | Success Metric | Last Touchpoint |
|--------------|-----------------|----------------|-----------------|
| [[Person]] | Investment plan | What success looks like | Date |
```

## Project-Goal Linkage

Projects should include goal attribution in frontmatter:

```yaml
---
title: "Project Name"
supports_goal: "Personal Brand Established"
goal_alignment: "high"  # high, medium, low
---
```

### Finding Projects by Goal

```bash
grep -r "supports_goal:" "{{vault_path}}/1-Projects/Current" --include="*.md"
```

### Finding Unlinked Projects

```bash
# Projects without supports_goal frontmatter
for f in {{vault_path}}/1-Projects/Current/*/*.md; do
  grep -L "supports_goal:" "$f" 2>/dev/null
done
```

## Weekly Goals Review

During Monday `/daily:plan` or dedicated weekly review:

### 1. Check Goal Progress
- Read current year file
- Note any goals with movement this week
- Flag stalled goals (no progress in 2+ weeks)

### 2. Review Project-Goal Alignment
- Are current projects advancing goals?
- Any projects that should be paused/stopped?
- Any goals with no active projects?

### 3. Process Opportunity Pipeline
- Check `/7-MOCs/Opportunities-Pipeline.md`
- Any opportunities awaiting evaluation?
- Prompt for `/board:advise` if significant ones pending

### 4. Update Progress
- Update goal status/progress in year file
- Update "Last Touchpoint" for relationship goals
- Move completed goals to done state

## Opportunity Handling

When user mentions a new opportunity:

### 1. Capture
Add to Opportunities-Pipeline.md under "Awaiting Evaluation"

### 2. Quick Alignment Check
Against focus filter (2026: NFT + Physical + AI):
- **High** (2-3 pillars): Priority consideration
- **Medium** (1 pillar): Needs careful evaluation
- **Low** (0 pillars): Suggest declining or deferring

### 3. Evaluation Path
- Simple/clear: Decide immediately
- Significant: Suggest `/board:advise`

### 4. Decision Recording
- Move to appropriate section in pipeline
- If accepted, create project with `supports_goal` frontmatter
- If declined, document reason

## Focus Filter (2026)

**Focus Filter** - Configure your focus pillars during onboarding:

| Pillar | Examples |
|--------|----------|
| Pillar 1 | (Configure during onboarding) |
| Pillar 2 | (Configure during onboarding) |
| Pillar 3 | (Configure during onboarding) |

## Integration Points

### With `/daily:plan`
- Surface goals with upcoming deadlines
- Mention opportunities awaiting evaluation
- Check relationship goal touchpoints

### With `/update`
- Detect opportunity mentions → add to pipeline
- Detect goal progress → suggest updating year file

### With `/board:advise`
- Major opportunities trigger board deliberation
- Board sessions link back to opportunity pipeline
- Decisions recorded in both places

### With Project Creation
- New projects prompted for `supports_goal`
- `goal_alignment` auto-suggested based on focus filter

## Goal Status Indicators

| Status | Meaning |
|--------|---------|
| 🔴 Not Started | Goal defined but no action taken |
| 🟡 In Progress | Active work happening |
| 🟢 On Track | Progress meets expectations |
| ✅ Complete | Goal achieved |
| ⚠️ At Risk | Behind schedule or blocked |
| 🚫 Abandoned | Decided not to pursue |

## Key Files

- Year goals: `/2-Areas/Personal/Years/2026.md`
- Working draft: `/1-Projects/Current/2026-Annual-Planning/2026-Goals-Draft.md`
- Opportunities: `/7-MOCs/Opportunities-Pipeline.md`
- Life events: `/7-MOCs/Life-Events-Timeline.md`

## Related Skills

- `project-status` - Project lifecycle management
- `weekly-review` - Weekly pattern aggregation
- `advisor-*` - Domain expertise for board deliberations

---

## Enhancements

These evaluation frameworks integrate with [[decision-frameworks]] and [[planning-horizons]] to ensure goals and opportunities pass rigorous strategic filters.

### First Principles Filter

Before accepting any new goal or opportunity, apply the fundamental question:

**"What would I do if starting completely from scratch today?"**

| Question | Purpose |
|----------|---------|
| Why do I want this? (Ask 5 times) | Expose root motivation vs. inherited expectation |
| Am I copying what others do or reasoning from fundamentals? | Distinguish innovation from analogy |
| What assumptions am I making that might not be true? | Surface hidden constraints |
| Is this goal grounded in what I genuinely want or what's expected? | Authentic vs. social goals |
| What's the fundamental need this goal serves? | Function vs. form clarity |

**Application**: Use during annual goal-setting (deep), quarterly reviews (moderate), and when evaluating significant new opportunities.

See [[first-principles-extraction]] for the complete framework.

### Asymmetry Evaluation

For all opportunities, calculate the downside vs. upside ratio. Seek opportunities with at least 3:1 asymmetry.

**Evaluation Steps:**

1. **Calculate Maximum Downside**
   - What is the absolute worst outcome?
   - How long would recovery take?
   - **Ruin Check**: Would failure wipe out financially, reputationally, or energetically?

2. **Assess Upside Potential**
   - What is the realistic best outcome?
   - Does success create compounding returns?
   - What doors does this open?

3. **Check Asymmetry Ratio**

| Ratio | Assessment | Action |
|-------|------------|--------|
| < 1:1 | Negative asymmetry | Decline |
| 1:1 - 3:1 | Modest | Needs strong other justification |
| 3:1 - 10:1 | Good asymmetry | Serious consideration |
| > 10:1 | Excellent | Strong candidate |

**The One Reason Rule**: If you need more than one reason to do something, you might be convincing yourself. Obvious decisions need only one good reason.

See [[asymmetric-returns-extraction]] for the complete framework.

### Second-Order Thinking

Before committing to any goal, map the chain reactions:

| Order | Question | Timeframe |
|-------|----------|-----------|
| 1st | What happens immediately? | Now - 1 month |
| 2nd | What chain reactions follow? | 1-3 years |
| 3rd | What long-term effects emerge? | 3-10 years |

**Key Questions:**
- "And then what?" (Keep asking until you've mapped 3 orders)
- "If I pursue this consistently, what will my life look like in 10 years?"
- "What does this compound into over time?"
- "Is this first-order negative but second-order positive?" (Many worthwhile pursuits are)

**The 10-10-10 Rule:**
- How will I feel in **10 minutes**?
- How will I feel in **10 months**?
- How will I feel in **10 years**?

### Ruin Risk Check

**Automatic disqualification**: If any dimension shows ruin risk, this is an automatic NO.

**Ask for every opportunity:**
- "Is there any chance this could cause catastrophic harm?"
- "Can I survive the worst case?"
- "Would failure wipe me out financially, reputationally, or energetically?"

**The Rule**: Never take bets with unlimited downside, regardless of how favorable the odds appear. Survival is the primary objective.

**Specific Checks:**
- Financial ruin: Could this destroy savings or income sources?
- Reputation ruin: Could this permanently damage professional standing?
- Energy ruin: Could this cause burnout or health crisis?
- Relationship ruin: Could this damage key relationships irreparably?

### Optionality Assessment

Evaluate whether goals create or foreclose future options:

**Questions to Ask:**
- "Does this create future options or close them off?"
- "Can I exit early if it's not working?"
- "Am I committing to a rigid plan or to principles/agents that can adapt?"

**Optionality Principles:**
- Prefer goals that open doors over those that close them
- Maintain the right (not obligation) to take future action
- Strategic flexibility beats rigid commitment in uncertain environments
- "You don't have to be right that often" if you have favorable asymmetries

**Via Negativa Check**: Before adding a new goal, ask:
- "What problem am I trying to solve by adding this?"
- "Could I solve that problem by removing something instead?"

See [[decision-frameworks]] for the complete evaluation framework.
