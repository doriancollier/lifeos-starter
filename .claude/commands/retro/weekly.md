---
description: Weekly retrospective using 3 Ls format (Liked, Learned, Lacked)
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Weekly Retrospective Command

Guide the user through a **15-minute weekly retrospective** using the 3 Ls format (Liked, Learned, Lacked). This is a quick pattern recognition exercise focused on the past week.

> **Coaching Reminder**: This is reflection, not self-judgment. Apply the Prime Directive: "Everyone did the best they could given what they knew at the time." Focus on learning, not blame.

## Context

- **Daily notes directory**: `{{vault_path}}/4-Daily/`
- **Template**: `[[weekly-retro]]` in `workspace/3-Resources/Templates/Retrospectives/`
- **Output location**: Add to current week's Friday daily note under "## Weekly Retrospective" OR create standalone if running on weekend

## Process

Execute these steps **conversationally**, gathering input for each section.

### Step 1: Gather Context

1. **Get current date and week boundaries**
   ```bash
   date +%Y-%m-%d  # Today
   date -v-sun +%Y-%m-%d  # Start of week (Sunday)
   ```

2. **Scan this week's daily notes** for patterns:
   - Completed tasks (victories)
   - Incomplete tasks (patterns of avoidance)
   - Energy levels
   - Fears faced
   - Mood trends

3. **Present a brief summary**:
   - "This week you completed X tasks, faced Y fears, and had Z meetings."
   - Note any chronic carryover tasks

### Step 2: Set the Stage (2 min)

Open with Prime Directive:
> "Regardless of what we discover, we understand that you did the best you could given what you knew, your energy, and the situation at hand. This is about learning, not judgment."

Ask: "What's your overall feeling about this week, 1-10?"

If below 5, acknowledge: "Low weeks happen. Let's understand what drained you and what we can learn."

### Step 3: Liked - Wins (4 min)

Ask: "What went well this week? What are you proud of?"

Prompt if needed:
- "What tasks felt satisfying to complete?"
- "What relationships strengthened?"
- "What fears did you face successfully?"
- "What systems worked well?"

**Capture 3-5 specific wins.**

### Step 4: Learned - Discoveries (4 min)

Ask: "What did you learn this week—about yourself, your work, or life?"

Prompt if needed:
- "What patterns do you notice in your successes?"
- "What patterns do you notice in your struggles?"
- "What surprised you?"
- "What would you tell your past self from Monday?"

**Capture 2-4 specific learnings.**

### Step 5: Lacked - Gaps (3 min)

Ask: "What was missing this week? What didn't work?"

Prompt if needed:
- "What resources or support did you need but not have?"
- "What systems broke down?"
- "What did you avoid that you shouldn't have?"
- "Where did the Four Horsemen show up?" (for relationship context)

**Capture 2-4 specific gaps.**

**Coaching moment**: If the same gap appears week after week, call it out: "This has come up before. What's the root cause? What would actually fix this?"

### Step 6: Generate Insights (2 min)

Based on the 3 Ls, surface patterns:

Ask: "Looking at these together, what ONE insight stands out?"

Connect to identity/mission if relevant:
- "How does this relate to protecting what matters?"
- "What would the person you're becoming do differently?"

### Step 7: Action Items for Next Week (2 min)

Ask: "What 1-3 specific actions will you take next week based on this?"

**Action Item Format:**
```
- [ ] [Action] by [Day] → [Success metric]
```

Rules:
- Maximum 3 actions (fewer is better)
- Each must have clear owner ({{user_first_name}}), deadline, and success metric
- If no one commits to an action, discard it

### Step 8: Close

Summarize:
```markdown
## Weekly Retrospective Summary

**Overall Week Score**: X/10
**Top Win**: [biggest Liked item]
**Key Learning**: [most important Learned item]
**Focus for Next Week**: [primary action]
```

Closing prompt:
- "Good reflection. Now let's make next week better."

## Output

Create or update the weekly retro section:

```markdown
## Weekly Retrospective - Week of YYYY-MM-DD

**Overall Score**: X/10

### Liked (Wins)
1.
2.
3.

### Learned (Discoveries)
1.
2.

### Lacked (Gaps)
1.
2.

### Key Insight
[One sentence insight]

### Actions for Next Week
- [ ] [Action] by [Day] → [Metric]
- [ ]
```

**Location**:
- If Friday: Add to today's daily note
- If weekend: Add to Friday's daily note
- If missing Friday note: Create standalone in `workspace/3-Resources/Reviews/Weekly/`

## Interaction Guidelines

- **Keep it to 15 minutes** - This is a quick check-in, not deep analysis
- **Celebrate wins first** - Start positive before addressing gaps
- **One action is enough** - Don't let them overcommit
- **Connect to patterns** - Reference previous weeks if available
- **Blameless** - Focus on "what allowed this" not "why did I fail"

## Examples

**Example Liked**:
- Completed the roadmap doc on Wednesday - felt in flow
- Had a great State of Union with {{partner_name}} - felt connected
- Faced the difficult conversation with contractor - was hard but proud

**Example Learned**:
- I'm more productive in the morning before Slack
- When I skip Daily Practice, my whole day suffers
- I need more buffer time between meetings

**Example Lacked**:
- Didn't protect lunch breaks - ate at desk 4/5 days
- Avoided the budget conversation again
- No solo time for recharge

**Example Action**:
- [ ] Block 12-1pm as protected lunch by Monday → No lunch meetings this week
