---
description: Complete weekly reflection on pre-aggregated data - light-weight Monday review
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Weekly Reflect Command

Guide the user through a **focused reflection session** on their pre-aggregated weekly document. This is lighter than `/weekly:review` because the data is already captured—we're just adding meaning.

> **Coaching Reminder**: Help them see patterns, celebrate wins, and learn from challenges. Connect insights to their foundation and annual goals.

## Context

- **Weekly documents**: `3-Resources/Planning/Weekly/YYYY-Www.md`
- **Foundation**: `2-Areas/Personal/foundation.md`
- **Annual goals**: `2-Areas/Personal/Years/2026.md`

## When to Use

- **Monday/Tuesday mornings** after daily planning
- When SessionStart hook prompts "Last week's review is ready for reflection"
- Any time user wants to complete weekly reflection

## Reflection Flow

Execute these steps **sequentially**, focusing on meaning-making rather than data gathering.

### Step 1: Locate Weekly Document

1. **Determine last week's file**:
   ```bash
   # Get last week's ISO week
   last_week=$(date -v-7d +%G-W%V)
   weekly_file="{{vault_path}}/3-Resources/Planning/Weekly/${last_week}.md"
   ```

2. **Check if file exists**:
   - If yes: Read it and continue
   - If no: Offer to run `/weekly:review` instead (full data gathering needed)

3. **Check if reflection already complete**:
   - Look for `reflection_complete: true` in frontmatter
   - If complete: Ask if they want to review or update

### Step 2: Present Week Summary

Read the aggregated data and present a brief summary:

```markdown
## Week [W##] Summary

**Tasks**: [X] completed ([Y] A-priorities)
**Fears**: [X] faced / [Y] avoided
**Average Energy**: P: [X]/10 | E: [X]/10 | M: [X]/10 | S: [X]/10
**Daily Habit Compliance**: [X]%
**Weekly Rhythms**: [X]/4 completed
```

**Get health summary for the week**:
```bash
python3 "{{vault_path}}/.claude/scripts/health_sync.py" goals
```

Present health metrics:
```markdown
### Health Metrics

**Ring Closure Rate**: Move [X]/7 | Exercise [X]/7 | Stand [X]/7
**Average Sleep**: [X] hrs (vs 7.5 target)
**Current Streaks**: Move [X] | Exercise [X] | Stand [X] | Steps [X]
**Body Composition**: [current]% → [target]% by Dec 2026
```

Note any standout patterns:
- "Physical energy dropped mid-week"
- "You faced a fear every day!"
- "State of Union didn't happen this week"
- "Sleep averaged under 7 hours—this affects everything"
- "All three rings closed 5/7 days—strong week!"
- "Move streak at 12 days—keep it going!"

### Step 3: Guided Reflection (4 Ls)

Walk through each reflection area conversationally:

#### 3a. What Went Well (Loved)

Ask: **"What went well this week? What are you proud of?"**

Listen for:
- Accomplishments
- Fears faced
- Role wins
- Energy management successes
- **Health wins** — rings closed, streaks maintained, sleep improved

Prompt if needed:
- "Looking at your completed tasks, what stands out?"
- "You faced [X] fear(s). How did that feel?"
- "Your [role] satisfaction was high. What contributed to that?"
- "You closed all three rings [X] days this week. How does that correlate with your energy?"
- "Your sleep average was [X] hrs. Did you notice the impact?"

Capture 3 items in the weekly doc.

#### 3b. What Didn't Go Well (Loathed)

Ask: **"What didn't go well? What frustrated you?"**

Listen for:
- Missed commitments
- Energy drains
- Role neglect
- Avoided fears
- **Health setbacks** — missed rings, broken streaks, poor sleep

Prompt if needed:
- "Your habit compliance dropped to [X]%. What blocked you?"
- "What fears did you avoid? What got in the way?"
- "Which role got neglected? Why?"
- "Your [Move/Exercise] streak broke this week. What happened?"
- "Sleep averaged [X] hrs. What's preventing consistent rest?"
- "You missed rings on [X] days. Is this a pattern worth addressing?"

Capture 3 items in the weekly doc.

#### 3c. What You Learned (Learned)

Ask: **"What did you learn this week? Any insights or patterns?"**

Connect to:
- Recurring challenges
- What worked vs. didn't
- INTJ-specific patterns (need for solitude, grip stress)
- Energy patterns
- **Health-performance correlations** — sleep/activity impact on productivity

Prompt if needed:
- "You hit [habit] 7/7 days. What made that sustainable?"
- "Looking at your energy dips, what's the pattern?"
- "What would you tell yourself at the start of this week?"
- "On days you closed all rings, how was your productivity?"
- "Did sleep correlate with your physical energy ratings?"
- "Your best days this week—did they share any health patterns?"

Capture 3 insights in the weekly doc.

#### 3d. What You Wish Was Different (Longed For)

Ask: **"What do you wish had been different? What will you do differently?"**

Connect to:
- Specific behavior changes
- System improvements
- Boundary setting
- Recovery needs

Prompt if needed:
- "If you could replay this week, what's one thing you'd change?"
- "What system or process would have helped?"
- "What will you stop, start, or continue?"

Capture 3 items in the weekly doc.

### Step 4: Role Check-In

Present the role satisfaction data (if captured) or ask:

```markdown
| Role | Attention | Satisfaction | One Insight |
|------|-----------|--------------|-------------|
| Provider | | /10 | |
| Father | | /10 | |
| Partner | | /10 | |
| Self | | /10 | |
```

Ask:
- **"Which role got the most attention? Least?"**
- **"Where did one role enrich another?"**
- **"Which role needs more attention next week?"**

**Known bias check**: "Did you over-prioritize professional work again?"

### Step 5: Big 3 Assessment

Review this week's Big 3 from the weekly doc:

Ask for each:
- Was it completed?
- If not, why? (Blocked, deprioritized, too ambitious?)
- Did it become "gravel"?

**Coaching**: If Big 3 items consistently get deferred, challenge: "Are you setting Big 3s you actually believe in? Or are they aspirational?"

### Step 6: Set Next Week's Big 3

Ask: **"What are your 3 most important priorities for next week?"**

For each Big 3:
- **Validate scope**: "Is this achievable in a week, or should we scope it down?"
- **Connect to quarterly**: "Which quarterly rock does this advance?"
- **Anticipate blockers**: "What might get in the way?"

Capture in the weekly doc under "Next Week's Big 3".

**Cascade check**: "Do these Big 3 connect to your monthly theme? Quarterly rocks?"

### Step 7: Capture Patterns & Carry Forward

Ask:
- **"Any patterns you want to track?"** (Energy, productivity, relationships, fears)
- **"Anything to carry forward to next week?"** (Tasks, conversations, decisions)

Capture in the appropriate sections of the weekly doc.

### Step 8: Finalize Document

1. **Update frontmatter**:
   ```yaml
   status: "complete"
   reflection_complete: true
   ```

2. **Add any final notes**

3. **Confirm completion**:
   ```markdown
   ✅ Weekly reflection complete for [Week]

   **Key Takeaways**:
   - [Loved highlight]
   - [Key learning]
   - [Next week focus]

   **Next Week's Big 3**:
   1. [Big 3 #1]
   2. [Big 3 #2]
   3. [Big 3 #3]
   ```

### Step 9: Transition to Daily Planning

If running before daily planning:

Ask: **"Ready to plan today? Your Big 3 for the week are set."**

If yes: Transition to `/daily:plan` with weekly context loaded.

## Interaction Guidelines

- **Be a coach, not a clerk** — draw out insights, don't just record
- **Celebrate wins** — this isn't just about problems
- **Connect to identity** — "That took courage" / "That's the provider showing up"
- **Keep it focused** — aim for 15-20 minutes total
- **Make it meaningful** — shallow reflection is wasted time

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No weekly doc exists | Offer `/weekly:review` instead |
| Doc exists but no daily data | Note gaps, proceed with what's available |
| Reflection already complete | Ask if they want to review/update |
| Mid-week reflection | Note it's partial, proceed with available data |

## Integration

- **From `/daily:plan`**: Called when Monday morning and last week's doc ready
- **From SessionStart hook**: Prompted when last week's doc needs reflection
- **Standalone**: User can run anytime

## Output

By the end, user should have:
1. **Completed 4 Ls reflection** — Loved, Loathed, Learned, Longed For
2. **Role check-in complete** — attention, satisfaction, insights
3. **Big 3 assessed** — this week's reviewed
4. **Next week's Big 3 set** — connected to quarterly goals
5. **Patterns captured** — for future awareness
6. **Carry forward items** — nothing lost
7. **Document marked complete** — `reflection_complete: true`
