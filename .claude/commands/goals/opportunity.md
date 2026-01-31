---
description: Capture and evaluate a new opportunity against the focus filter
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Capture Opportunity Command

Capture a new opportunity and route it through the evaluation process.

## Arguments

- `$ARGUMENTS` - Description of the opportunity (e.g., "new consulting client for AI project")

## Process

### Step 1: Parse the Opportunity

Extract from the user's input:
- **Description**: What is the opportunity?
- **Source**: Where did it come from? (person, meeting, email, idea)
- **Potential value**: What could this lead to?

### Step 2: Quick Alignment Check

Apply the focus filter (NFT + Physical + AI):

| Pillar | Aligned? |
|--------|----------|
| NFT (digital ownership, blockchain, generative art, Web3) | Yes/No |
| Physical (3D printing, manufacturing, e-commerce, tangible goods) | Yes/No |
| AI (automation, agents, intelligent systems) | Yes/No |

**Alignment Score**:
- 2-3 pillars = High
- 1 pillar = Medium
- 0 pillars = Low

### Step 2b: Decision Framework Analysis (Planning System 2.0)

**For Medium and High alignment opportunities, apply these additional filters:**

#### Asymmetric Returns Check

1. **Asymmetry Ratio**: "What's the downside vs upside potential?"
   - Calculate: Maximum loss vs. realistic gain
   - Target: At least 3:1 upside-to-downside ratio
   - If ratio < 3:1: Flag as "modest asymmetry - needs strong other justification"

2. **Ruin Risk Check**: "Could this cause catastrophic harm if it fails?"
   - Financial ruin? (Would failure wipe out savings or income?)
   - Reputational ruin? (Would failure damage key relationships or reputation?)
   - Energy ruin? (Would failure lead to severe burnout?)
   - **If ANY dimension shows ruin risk = AUTOMATIC NO**

#### Second-Order Consequences

Ask: "What happens in 2nd and 3rd order?"

| Order | Question | Timeframe |
|-------|----------|-----------|
| 1st | What happens immediately? | Now - 1 month |
| 2nd | What chain reactions follow? | 1-3 years |
| 3rd | What long-term effects emerge? | 3-10 years |

Apply the 10-10-10 Rule:
- "How will you feel in 10 minutes?"
- "How will you feel in 10 months?"
- "How will you feel in 10 years?"

#### Optionality Assessment

Ask: "Does this create or close off future options?"
- **Creates options**: Opens new doors, builds skills, expands network
- **Closes options**: Locks in commitments, narrows focus, consumes capacity

"Can you exit early if it's not working?" (Two-way vs one-way door)

**Present summary**:
```markdown
## Decision Framework Analysis

**Asymmetry Ratio**: [X:1] - [Good/Modest/Poor]
**Ruin Risk**: [None/Low/FLAGGED]
**Second-Order Effects**: [Summary]
**Optionality**: [Creates/Neutral/Closes]
**Door Type**: [One-way/Two-way]

**Framework Recommendation**: [Proceed/Proceed with caution/Decline/Needs board deliberation]
```

### Step 3: Route Based on Alignment

**High Alignment**:
- Add to "Awaiting Evaluation" in pipeline
- Ask if it needs board deliberation or quick decision
- If quick decision: proceed to accept/decline
- If board needed: suggest `/board:advise`

**Medium Alignment**:
- Add to "Awaiting Evaluation"
- Flag as needing careful evaluation
- Suggest board deliberation for significant commitment

**Low Alignment**:
- Inform user this doesn't align with 2026 focus
- Ask: "Add to 'Not Aligned' (decline) or 'Future Exploration' (defer to 2027+)?"
- Update pipeline accordingly

### Step 4: Update Pipeline

Read the opportunities pipeline:
```
/7-MOCs/Opportunities-Pipeline.md
```

Add the new opportunity to the appropriate section with:
- Description
- Source
- Date captured (today)
- Alignment score
- Action needed

### Step 5: If Quick Accept

If the user decides to accept and it's a clear decision:

1. Ask what goal this supports
2. Suggest creating a project with `/create:project [name]`
3. Remind to add `supports_goal:` frontmatter

### Step 6: Output Confirmation

```markdown
## Opportunity Captured

**Description**: [description]
**Alignment**: [High/Medium/Low] ([X]/3 pillars)
**Added to**: [section in pipeline]
**Next step**: [action needed]

[If applicable: Link to board session or new project]
```

## Examples

**Input**: `/goals:opportunity new client wants AI chatbot for real estate`
- Alignment: AI (yes), Physical (no), NFT (no) = Medium
- Action: Add to Awaiting Evaluation, suggest board deliberation if significant

**Input**: `/goals:opportunity Etsy seller wants custom 3D printed game pieces`
- Alignment: AI (maybe), Physical (yes), NFT (possible) = High
- Action: Add to Awaiting Evaluation, likely can quick-accept

**Input**: `/goals:opportunity friend wants help with their food truck`
- Alignment: None (not NFT, Physical goods, or AI)
- Action: Suggest "Not Aligned" or "Future Exploration"
