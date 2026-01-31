---
description: Quick view of current goals status and progress
allowed-tools: Read, Grep, Glob
---

# Goals Status Command

Show a quick overview of current goals, their status, and related projects.

## Output

Read the current year file and generate a status report:

### Step 1: Load Data

```bash
# Read year file
cat "{{vault_path}}/2-Areas/Personal/Years/2026.md"

# Get project-goal links
grep -r "supports_goal:" "{{vault_path}}/1-Projects/Current" --include="*.md"
```

### Step 2: Generate Report

Output format:

```markdown
## Goals Status - [Date]

### By Status

**On Track (🟢)**: X goals
**In Progress (🟡)**: X goals
**Not Started (🔴)**: X goals
**At Risk (⚠️)**: X goals
**Complete (✅)**: X goals

### Professional Goals
| Goal | Status | Projects | Progress |
|------|--------|----------|----------|
| [from year file] | | | |

### Relationship Goals
| Relationship | Status | Last Touchpoint |
|--------------|--------|-----------------|
| [from year file] | | |

### Health Goals
| Goal | Status | Progress |
|------|--------|----------|
| [from year file] | | |

### Projects by Goal
| Goal | Active Projects |
|------|-----------------|
| [goal] | [[Project1]], [[Project2]] |

### Unlinked Projects
Projects without `supports_goal` frontmatter:
- [list any]

### Quick Stats
- **Total goals**: X
- **Goals with active projects**: X
- **Goals without projects**: X
- **Opportunities pending**: X (see [[Opportunities-Pipeline]])
```

### Step 3: Highlight Attention Items

If any goals are at risk or stalled:
```markdown
### Needs Attention
- [Goal] - No project linked
- [Goal] - 0% progress after [X weeks]
- [Relationship] - No touchpoint in [X weeks]
```

### Step 4: Monthly Milestone Progress (Planning System 2.0)

**Check progress against monthly milestones:**

For each quarterly rock, identify:
- Current month's milestone (from quarterly plan)
- Progress toward that milestone
- Days remaining in month

```markdown
### Monthly Milestone Progress

| Quarterly Rock | This Month's Milestone | Progress | Days Left |
|----------------|----------------------|----------|-----------|
| [Rock 1] | [Milestone] | [X%] | [N days] |
| [Rock 2] | [Milestone] | [X%] | [N days] |
```

**Milestone Status**:
- On Track: Progress matches time elapsed
- At Risk: Progress lagging behind time elapsed
- Ahead: Progress exceeding expectations

If milestones are missing, prompt: "Your quarterly rocks don't have monthly milestones defined. Would you like to set them now?"

### Step 5: Seasonal Context (Planning System 2.0)

**Surface life season awareness:**

Ask: "What life season are you in? How does it affect these goals?"

**Common seasons**:
- **Building**: High energy, expansion mode, taking on challenges
- **Maintaining**: Steady state, protecting what exists
- **Recovering**: Low energy, healing, renewal focus
- **Transitioning**: Between phases, uncertainty, exploration

**Season-Goal Alignment Check**:
- If Building season but goals are maintenance-focused: "Your goals may be too conservative for this season."
- If Recovering season but goals are aggressive: "These goals may be unsustainable. Consider adjusting expectations."
- If Transitioning: "Flexibility is key. Are any goals creating unnecessary rigidity?"

```markdown
### Seasonal Context

**Current Season**: [Season]
**Season-Goal Alignment**: [Aligned/Misaligned]
**Adjustment Needed**: [None/Consider reducing/Consider expanding]
```

## Usage

Run `/goals:status` for a quick dashboard view.
For interactive review and updates, use `/goals:review`.
