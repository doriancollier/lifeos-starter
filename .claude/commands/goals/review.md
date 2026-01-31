---
description: Weekly goals review - check progress, surface stalled goals, review opportunities
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

# Goals Review Command

Perform a weekly review of goals, projects, and opportunities. Use this on Mondays or at the end of each week.

## Context

- **Year file**: `/2-Areas/Personal/Years/2026.md`
- **Opportunities**: `/7-MOCs/Opportunities-Pipeline.md`
- **Projects**: `/1-Projects/Current/`

## Review Flow

### Step 1: Load Current Goals

Read the current year file to understand active goals:

```bash
cat "{{vault_path}}/2-Areas/Personal/Years/2026.md"
```

Present a summary of:
- Total goals by category
- Goals by status (🔴 Not Started, 🟡 In Progress, 🟢 On Track)
- Any goals marked ⚠️ At Risk

### Step 2: Check Project-Goal Alignment

Find all current projects and their goal links:

```bash
grep -r "supports_goal:" "{{vault_path}}/1-Projects/Current" --include="*.md"
```

Present:
- Projects by goal they support
- Any projects without `supports_goal` frontmatter (unlinked)
- Any goals with no active projects

Ask: "Any projects you want to link to goals, or goals that need projects created?"

### Step 3: Check for Stalled Goals

Identify goals that may be stalled:
- Status is 🔴 Not Started with no projects
- Projects exist but no activity in 2+ weeks (based on file modification time)
- Progress hasn't changed

Ask about each stalled goal: "What's blocking progress on [Goal]? Should we adjust, create a project, or acknowledge it's deferred?"

### Step 4: Review Opportunities Pipeline

Read the opportunities pipeline:

```bash
cat "{{vault_path}}/7-MOCs/Opportunities-Pipeline.md"
```

Present:
- Opportunities awaiting evaluation
- Opportunities under consideration

For each in "Awaiting Evaluation":
- Apply the focus filter (NFT + Physical + AI)
- Ask if it needs board deliberation or quick decision

Ask: "Any of these ready to decide? Should we run `/board:advise` on any?"

### Step 5: Update Relationship Touchpoints

Check the Relationship Goals table:
- Which relationships haven't had a touchpoint in 2+ weeks?
- Prompt to update "Last Touchpoint" for any recently engaged

Ask: "Any relationship touchpoints to update from this week?"

### Step 6: Update Goal Progress

For any goals that have progressed:
1. Update the status column (🔴→🟡→🟢)
2. Update the progress percentage
3. Add any new projects to the Projects column

### Step 7: Pareto & Leverage Analysis

**Before generating summary, analyze effectiveness:**

#### Pareto Check

Ask: "Which 20% of goal-related activities created 80% of progress this week?"

- Review completed tasks from the week
- Identify high-impact activities vs. busy work
- "What activities should you do MORE of?"
- "What activities should you STOP doing?"

Present:
```markdown
### Pareto Analysis

**High-Impact Activities (Top 20%)**:
- [Activity] → [Impact on goal]
- [Activity] → [Impact on goal]

**Low-Impact Activities (Bottom 80%)**:
- [Activity] - Consider eliminating or delegating
```

#### Leverage Assessment

For each goal with progress, ask:
- "Was this high-leverage (builds systems, compounds) or low-leverage (one-time output)?"
- "Which goals had the highest leverage activities this week?"

```markdown
### Leverage Assessment

| Goal | Activity | Leverage Level |
|------|----------|----------------|
| [Goal] | [Activity] | High/Medium/Low |
```

**Coaching**: If most activities are low-leverage, challenge: "You're trading time for output. What system could you build instead?"

#### Retrospective Insights

Ask:
- "What patterns emerged this week?"
- "Any breakthrough insights?"
- "What surprised you?"

Capture any significant learnings for future reference.

### Step 8: Generate Summary

Output a summary in this format:

```markdown
## Weekly Goals Review - [Date]

### Progress This Week
- [Goals that moved forward]

### Stalled Items
- [Goals or projects with no movement]

### Pareto Insights
- **Top 20% activities**: [List high-impact activities]
- **Bottom 80% to reconsider**: [List low-impact activities]

### Leverage Assessment
- **Highest leverage goal**: [Goal] - [Why]
- **Leverage opportunity**: [Where to build systems]

### Opportunities
- [X] in pipeline
- [X] need evaluation
- [X] under consideration

### Relationship Check-ins
- [Any touchpoints needed]

### Patterns & Insights
- [Key patterns observed]
- [Breakthrough insights]

### Next Actions
- [Specific actions from review]
```

## Output

By the end, the user should have:
1. Updated goal statuses in the year file
2. Opportunities evaluated or flagged for board review
3. Relationship touchpoints updated
4. Clear next actions for the coming week
5. Pareto analysis of high-impact vs. low-impact activities
6. Leverage assessment for goal-related work
7. Captured patterns and insights
