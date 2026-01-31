---
name: historical-memory
description: Capture and organize historical/biographical information with follow-up questions. Activates when past events, life milestones, or "X years ago" expressions are mentioned. Routes information to biography, timeline, or person files appropriately.
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

# Historical Memory Skill

Automatically captures and organizes historical/biographical information when mentioned in conversations, ensuring life history is properly documented and queryable.

## When to Use

This skill activates autonomously when:
- Relative time expressions are used: "X years ago", "back when I...", "before I..."
- Life milestones are mentioned: moves, jobs, relationships, births, deaths
- Historical facts are shared: "I used to...", "I was..."
- Past events are referenced without full context

## Key Locations

- **Biography**: `{{vault_path}}/2-Areas/Personal/biography.md`
- **Life Timeline MOC**: `{{vault_path}}/7-MOCs/Life-Timeline.md`
- **Person files**: `{{vault_path}}/6-People/`
- **Google Sheet (primary)**: https://docs.google.com/spreadsheets/d/1Qhwyi37rkhLQOUpVYF7dUtygG2PQjbNffzkfkEU8FWA/edit?gid=0#gid=0

## Core Principle

**The Google Sheet is the primary source of truth for detailed historical data.** Obsidian files (biography.md, Life-Timeline.md) contain summaries for AI access. When new historical information is captured:

1. Add summary to appropriate Obsidian file
2. Remind user to update Google Sheet with full details
3. Ask follow-up questions to build complete picture

## Temporal Expression Parsing

When relative time expressions are detected, calculate the actual year:

| Expression | Calculation | Example (if today is 2025) |
|------------|-------------|---------------------------|
| "X years ago" | Current year - X | "10 years ago" → 2015 |
| "in my 20s" | Birth year + 20-29 | 1978 + 20 = 1998-2007 |
| "when {{child_name}} was born" | 2010 | Known anchor |
| "before I moved to Austin" | Before Sept 2019 | Known anchor |
| "during my JibJab years" | 2014-2019 | Known era |
| "when I sold HelloSanta" | Early 2014 | Known anchor |

**Known temporal anchors** (from biography):
- Born: April 27, 1978
- {{child_name}} born: May 16, 2010
- HelloSanta sold: Early 2014
- Moved to Austin: September 7, 2019
- Bought {{company_3_name}}: January 21, 2021
- Mom passed: June 10, 2023

## Follow-up Question Templates

When historical information is incomplete, ask follow-up questions to build context.

### For Career Events

```
AskUserQuestion: "I'm capturing this career milestone. A few questions to complete the picture:

1. What year(s) was this?
2. What was your role/title?
3. Who else was involved (co-founders, colleagues)?
4. What was the outcome?

Options:
- Answer all questions (I'll type details)
- Just the basics (year and role)
- Skip - I'll update the Google Sheet myself"
```

### For Moves/Relocations

```
AskUserQuestion: "I'm capturing this relocation. To complete the record:

1. What year did you move?
2. What was the address (if you remember)?
3. Who moved with you?
4. What prompted the move?

Options:
- Answer all questions
- Just year and location
- Skip - I'll update the Google Sheet"
```

### For Relationships/People

```
AskUserQuestion: "I'm noting this person/relationship. To build context:

1. How did you meet?
2. What year was this?
3. What's the current status of this relationship?

Options:
- Answer all questions
- Just the basics
- Skip for now"
```

### For Life Milestones

```
AskUserQuestion: "I'm capturing this milestone. For the record:

1. What year was this?
2. Who was involved?
3. Why was this significant?

Options:
- Answer all questions
- Just year and basic facts
- Skip"
```

## Execution Steps

### Step 1: Detect Historical Information

Scan for signals that historical/biographical information is being shared:

| Signal Type | Pattern Examples |
|-------------|------------------|
| Relative time | "X years ago", "back in", "when I was", "before I" |
| Life events | "moved to", "worked at", "married", "divorced", "born", "died", "sold", "started" |
| Era references | "during my JibJab years", "when I was at", "in my 20s" |
| People from past | Names not in active context, "used to know", "worked with" |

### Step 2: Calculate Actual Dates

Parse relative expressions using temporal anchors:

```python
# Pseudocode for relative time parsing
def parse_relative_time(expression, reference_date=today):
    if "years ago" in expression:
        years = extract_number(expression)
        return reference_date.year - years

    if "when {{child_name}} was born":
        return 2010

    if "before Austin" or "in LA":
        return "pre-2019"

    # ... other patterns
```

### Step 3: Classify Information Type

Determine where this information belongs:

| Type | Destination | Example |
|------|-------------|---------|
| Career event | biography.md (Career section) + person files | "sold my company" |
| Move/Location | biography.md (era chapter) + Life-Timeline | "moved to Austin" |
| Relationship | Person file + biography.md | "met Alex" |
| Family event | biography.md + Life-Timeline + person files | "{{child_name}} was born" |
| Personal milestone | biography.md (relevant chapter) | "thyroid cancer" |

### Step 4: Check Existing Information

Before adding, verify it's not already documented:

```bash
# Search biography for existing mention
grep -i "[key terms]" "{{vault_path}}/2-Areas/Personal/biography.md"

# Search Life-Timeline
grep -i "[key terms]" "{{vault_path}}/7-MOCs/Life-Timeline.md"
```

### Step 5: Ask Follow-up Questions

If information is incomplete, use appropriate template to gather full context.

**When to ask:**
- Year is unknown or ambiguous
- People involved aren't clear
- Context/significance isn't explained
- Multiple interpretations possible

**When NOT to ask:**
- Information is already complete
- It's a minor detail
- User has explicitly said they'll update the Sheet

### Step 6: Update Obsidian Files

Based on classification, update appropriate file(s):

**For biography.md:**
- Find relevant era/chapter
- Add new information in appropriate section
- Update `modified` date

**For Life-Timeline.md:**
- Add row to timeline table if significant enough
- Update era section if needed

**For person files:**
- Add to "Shared History" or "Timeline" section
- Update relationship context if needed

### Step 7: Remind About Google Sheet

Always conclude with:

```
"I've added this to [file(s)]. Remember to update your Life Timeline Google Sheet with the full details when you have a chance: [link]"
```

## Integration with /update Command

When `/update` is used with historical content:

1. **Detect historical nature** → Activate this skill
2. **Parse temporal expressions** → Calculate actual dates
3. **Route appropriately**:
   - Today's events → Daily note (existing behavior)
   - Historical events → biography.md + reminder for Sheet
   - Future plans → Life-Events-Timeline or Years files
4. **Ask follow-ups** if information is incomplete
5. **Cross-reference** person files as needed

## Examples

### Example 1: "I sold my company to JibJab 10 years ago"

**Detection**: Career event + relative time ("10 years ago")

**Calculation**: 2025 - 10 = 2015... but we know from biography it was early 2014. Correct with known data.

**Check**: Biography already has HelloSanta chapter with accurate info.

**Action**: Confirm existing information is complete. No update needed.

**Response**: "I have the company acquisition documented in your biography. Is there anything to add or correct?"

### Example 2: "We moved to Austin from Los Angeles 5 years ago"

**Detection**: Move/relocation + relative time ("5 years ago")

**Calculation**: 2025 - 5 = 2020... but biography says September 7, 2019.

**Check**: Biography has this documented in Austin Era chapter.

**Action**: Confirm and note slight date discrepancy (5 years is approximate).

**Response**: "I have your Austin move documented as September 7, 2019 - about 6 years ago. You moved with {{partner_name}} and later {{child_name}} joined. Is that accurate?"

### Example 3: "I used to work with a guy named Marcus at Bizseed"

**Detection**: Person + career + past tense

**Check**: Search person files - no Marcus found. Check biography - Bizseed mentions Shane Shamloo but not Marcus.

**Action**: New information! Ask follow-up.

**Response**:
```
AskUserQuestion: "I don't have Marcus in my records from the Bizseed era. Should I create a person file?

Options:
- Yes, create person file - I'll provide details
- No, not significant enough to track
- Just note in biography - minor connection"
```

### Example 4: "Back when I was doing 3D animation work..."

**Detection**: Career + vague past reference

**Calculation**: From biography, 3D Greetings was 1999-2001.

**Action**: Use this context for the conversation but don't necessarily update files unless new information is shared.

**Response**: "That would be during your 3D Greetings years (1999-2001), right? What are you thinking about from that time?"

## Best Practices

1. **Don't duplicate everything** - The Google Sheet has full details. Obsidian has summaries.
2. **Use known anchors** - Cross-reference relative times with documented events.
3. **Ask strategically** - Only ask follow-ups for significant incomplete information.
4. **Cross-reference people** - Historical events often involve people who should have files.
5. **Respect privacy** - Some historical details are in "Private" column of Sheet for a reason.
6. **Connect eras** - Help user see how past connects to present.

## Error Handling

### Conflicting Dates
If user says something that conflicts with documented timeline:
- Gently note the discrepancy
- Ask which is correct
- Update if needed

### Unknown Era
If event doesn't fit known eras:
- Ask for clarification on timing
- May need to add new era to biography

### Duplicate Information
If information is already documented:
- Confirm it's accurate
- Ask if anything needs updating
- Don't create duplicates
