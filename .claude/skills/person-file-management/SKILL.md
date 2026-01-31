---
name: person-file-management
description: Automatically create and update person files when significant information is mentioned. Use when people are mentioned with health info, major life events, or important context worth tracking long-term.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Person File Management Skill

Automatically manages person files in the vault when significant information about people is mentioned in conversations, daily notes, or other contexts.

## When to Use

This skill activates autonomously when:
- People are mentioned with significant new information
- Health information is shared (surgery, diagnosis, appointments)
- Major life events occur (moving, weddings, births, job changes)
- Contact information is provided (email, phone, address)
- Important context is discovered (preferences, communication style)

## Key Locations

- **Professional contacts**: `{{vault_path}}/6-People/Professional/[Company]/[name].md`
- **Personal contacts**: `{{vault_path}}/6-People/Personal/[name].md`
- **Person template**: `{{vault_path}}/3-Resources/Templates/person-template.md`

## Decision Criteria

### AUTO-UPDATE (proceed without asking)

When these types of information are mentioned, automatically update the person's file:

**Health Information:**
- Surgery or major medical procedure
- Diagnosis of condition
- Hospitalization
- Major health changes

**Major Life Events:**
- Moving/relocating to new city or state
- Wedding, engagement, or divorce
- New baby or pregnancy
- Death or serious illness
- Job change (new job, promotion, leaving company)
- Major purchase (house, car)

**Contact Information:**
- New email address
- New phone number
- New physical address
- Updated social media handles

**Example patterns:**
- "Jane Doe is moving to Seattle next month"
- "John Smith had surgery on his knee yesterday"
- "Alex Johnson just got promoted to VP of Engineering"
- "Sarah Miller's new email is sarah@newcompany.com"

### DON'T UPDATE (too trivial)

Skip updating for routine, everyday interactions:

- Casual conversations with frequent contacts ("talked to Jane today")
- Regular work activities ("met with John about the project")
- Everyday tasks completed together ("grabbed coffee with Alex")
- Weather or casual observations ("Sarah mentioned it's hot today")
- Routine check-ins or status updates

**Why:** These don't add meaningful long-term context to the person file.

### ASK USER (middle ground - capture reasoning)

For situations that might be significant but aren't clearly major life events:

**Project Collaborations:**
- Starting to work together on new project
- Joining same team or committee

**Discoveries:**
- Preferences ("John hates cilantro")
- Hobbies or interests ("Sarah loves hiking")
- Communication style observations ("Alex prefers async communication")

**Travel/Plans:**
- Upcoming trips or vacations
- Long-term plans or goals

**Professional Changes:**
- New role or responsibility (not a job change)
- New project or initiative

When asking, use this format:

```
AskUserQuestion: "I learned [[Person Name]] [event/info]. Should I update their person file?

Options:
- "Yes - This is significant" - Add to person file
- "No - Too trivial" - Just keep in daily note

Optional: Why did you choose this? (Your reasoning helps me learn what's significant to you)"
```

**After receiving reasoning:**
1. Thank them: "Thanks! This helps me understand your threshold."
2. If they provide detailed reasoning, suggest: "Should I run `/system:update` to formalize this decision-making pattern for future similar cases?"

## Execution Steps

### Step 1: Detect Significant Information

Scan mentions of people for these signals:

| Signal Type | Pattern Examples |
|-------------|------------------|
| Health | "surgery", "diagnosis", "hospital", "procedure", "medical" |
| Life Events | "moving to", "wedding", "engaged", "new baby", "pregnant", "new job", "hired at", "promoted" |
| Contact | email addresses, phone numbers, "@mentions", addresses |
| Major Purchases | "bought a house", "new car", "purchased" |
| Death/Loss | "passed away", "died", "funeral" |

### Step 2: Extract Person Name

From the text, identify the person being discussed:
- Full names: "Jane Doe", "John Smith"
- First names in context: "Jane said...", "John's surgery..."
- Relationship references: "my boss", "my partner" (resolve to actual name)

### Step 3: Check if Person File Exists

```bash
# Search for existing person file (case-insensitive)
find "{{vault_path}}/6-People" -iname "*[person-name]*" -type f
```

**Results:**
- **File found**: Proceed to Step 5 (update existing)
- **No file found**: Proceed to Step 4 (create new)

### Step 4: Create New Person File

If no file exists, use AskUserQuestion:

```
AskUserQuestion: "I don't have a file for [[Name]]. Should I create one?

Options:
- "Yes - Professional contact" - I'll ask which company
- "Yes - Personal contact" - Create in Personal directory
- "No - Not significant enough" - Skip file creation
- "Remind me later" - Ask again next time"
```

**If Professional selected**, follow up:

```
AskUserQuestion: "Which company is [[Name]] associated with?

Options:
- "{{company_1_name}}"
- "{{company_2_name}}"
- "{{company_3_name}}"
- "Other" - User will specify
```

**Then create file:**

1. Read template: `{{vault_path}}/3-Resources/Templates/person-template.md`
2. Create file path:
   - Professional: `6-People/Professional/[Company]/[firstname-lastname].md`
   - Personal: `6-People/Personal/[firstname-lastname].md`
3. Populate with known information:
   - Name in title and frontmatter
   - Company/relationship context
   - The significant information that triggered creation
   - Reference to source: "Captured from [[YYYY-MM-DD daily note]]"
4. Confirm: "Created person file for [[Name]] in [location]"

### Step 5: Update Existing Person File

When person file exists and decision criteria are met:

**For AUTO-UPDATE categories:**
1. Read the person file
2. Identify appropriate section:
   - Health info → "Personal Notes" or create "Health" section
   - Life events → "Important Dates & Events" or "Personal Notes"
   - Contact info → Update frontmatter fields and "Communication Style & Preferences"
   - Job changes → "Role" in frontmatter and "Personal Notes"
3. Add new information with timestamp and source:
   ```markdown
   - [New info] (from [[YYYY-MM-DD daily note]])
   ```
4. Update `modified` date in frontmatter
5. Confirm: "Updated [[Name]]'s file with [category] information"

**For ASK cases:**
1. Present AskUserQuestion (format above)
2. If "Yes", proceed with update
3. If "No", skip update
4. If reasoning provided, capture it for process improvement

### Step 6: Cross-Reference

After creating or updating a person file:

1. **In the person file**: Add reference to source
   ```markdown
   - [Information] (from [[YYYY-MM-DD daily note]])
   ```

2. **In the daily note**: Link to person file
   ```markdown
   [[Person Name]] [context with information]
   ```

## Integration with Other Processes

- **`/update` command**: Automatically uses this skill when people are mentioned
- **`/meeting:prep` command**: Can update person files after significant meetings
- **`/create:person` command**: Manual creation follows same patterns
- **General conversations**: This skill activates whenever significant person info is shared

## Examples

### Example 1: Auto-Update (Health - Surgery)

**Input:** "Jane Doe has surgery scheduled for December 15th at 9am"

**Actions:**
1. ✅ Detect: Health information (surgery) → AUTO-UPDATE
2. ✅ Find person file: `6-People/Personal/jane-doe.md`
3. ✅ Update file:
   ```markdown
   ## Personal Notes

   - Surgery scheduled for December 15th at 9am (from [[2025-11-28 daily note]])
   ```
4. ✅ Update `modified: "2025-11-28"` in frontmatter
5. ✅ Confirm: "Updated [[Jane Doe]]'s file with health information"

### Example 2: Auto-Update (Life Event - Moving)

**Input:** "John Smith is moving to Seattle next month for the new role"

**Actions:**
1. ✅ Detect: Major life event (moving + job change) → AUTO-UPDATE
2. ✅ Find person file: `6-People/Professional/{{company_1_name}}/john-smith.md`
3. ✅ Update file:
   ```markdown
   ## Personal Notes

   - Moving to Seattle next month for new role (from [[2025-11-28 daily note]])
   ```
4. ✅ Potentially update location field if present in frontmatter
5. ✅ Confirm: "Updated [[John Smith]]'s file with relocation and job information"

### Example 3: Ask User (Middle Ground - Preference)

**Input:** "Found out Alex Johnson really hates cilantro"

**Actions:**
1. ⚠️ Detect: Preference discovery → ASK USER
2. ❓ AskUserQuestion:
   ```
   "I learned [[Alex Johnson]] hates cilantro. Should I update their person file?

   Options:
   - Yes - This is significant
   - No - Too trivial

   Why did you choose this? (helps me learn)"
   ```
3. **User selects "No - Too trivial"** and provides reasoning: "Food preferences aren't important unless they're allergies or we're planning events together"
4. ✅ Skip update
5. ✅ Suggest: "Thanks! Should I run `/system:update` to formalize that food preferences (non-allergies) are too trivial unless event planning?"

### Example 4: Auto-Update (Contact Info)

**Input:** "Sarah Miller's new email is sarah.miller@newcompany.com"

**Actions:**
1. ✅ Detect: Contact information → AUTO-UPDATE
2. ✅ Find person file: `6-People/Professional/{{company_2_name}}/sarah-miller.md`
3. ✅ Update frontmatter or contact section:
   ```yaml
   ---
   email: "sarah.miller@newcompany.com"
   modified: "2025-11-28"
   ---
   ```
4. ✅ Add note in body:
   ```markdown
   ## Communication Style & Preferences

   - Email updated to sarah.miller@newcompany.com (from [[2025-11-28 daily note]])
   ```
5. ✅ Confirm: "Updated [[Sarah Miller]]'s file with new email address"

### Example 5: Don't Update (Trivial Conversation)

**Input:** "Had a quick sync with Jane about the project status"

**Actions:**
1. ❌ Detect: Routine work activity → DON'T UPDATE
2. ✅ Skip person file update (too trivial)
3. ✅ Daily note still captures: "Had a quick sync with [[Jane Doe]] about the project status"
4. ✅ No confirmation needed (silent skip)

### Example 6: Create New Person File

**Input:** "Met with Dr. Robert Chen today about the referral. He's the endocrinologist at Austin Diabetes Center."

**Actions:**
1. ✅ Detect: Significant context (medical professional, new relationship)
2. ❌ No existing file found for "Robert Chen"
3. ❓ AskUserQuestion:
   ```
   "I don't have a file for [[Dr. Robert Chen]]. Should I create one?

   Options:
   - Yes - Professional contact
   - Yes - Personal contact
   - No - Not significant enough
   - Remind me later"
   ```
4. **User selects: "Yes - Professional contact"**
5. ❓ AskUserQuestion:
   ```
   "Which company is [[Dr. Robert Chen]] associated with?

   Options:
   - {{company_1_name}}
   - {{company_2_name}}
   - {{company_3_name}}
   - Other"
   ```
6. **User selects: "Other" and types "Austin Diabetes Center"**
7. ✅ Read person template
8. ✅ Create: `6-People/Professional/AustinDiabetesCenter/robert-chen.md`
9. ✅ Populate with known info:
   ```markdown
   ---
   title: "Dr. Robert Chen"
   type: "person"
   company: "Austin Diabetes Center"
   role: "Endocrinologist"
   relationship: "Medical Provider"
   tags: ["professional", "healthcare"]
   created: "2025-11-28"
   modified: "2025-11-28"
   ---

   # Dr. Robert Chen

   ## Relationship Context

   - **Professional**: Endocrinologist at Austin Diabetes Center
   - **Role**: Medical provider - endocrinology
   - **First Contact**: Referral consultation (from [[2025-11-28 daily note]])
   ```
10. ✅ Confirm: "Created person file for [[Dr. Robert Chen]] in 6-People/Professional/AustinDiabetesCenter/"

## Best Practices

1. **Always cross-reference**: Link person files to daily notes and vice versa
2. **Update modification dates**: Keep frontmatter `modified` field current
3. **Be specific**: "Surgery on knee" is better than "surgery"
4. **Capture source**: Always note where information came from
5. **Preserve context**: Include enough detail to remember why it mattered
6. **Learn from feedback**: When user provides reasoning, suggest process improvements

## Edge Cases

### Multiple People with Same Name

If search returns multiple matches:
1. Present options to user
2. Include distinguishing context (company, role)
3. Ask which person they meant

### Ambiguous Significance

If unsure whether information is significant:
- Default to ASK USER
- Capture their reasoning
- Learn for future similar cases

### Missing Person Template

If template doesn't exist:
1. Warn user: "Person template not found at expected location"
2. Create minimal file structure manually
3. Suggest: "You may want to create a person template at 3-Resources/Templates/person-template.md"

### Conflicting Information

If new information conflicts with existing data:
- Add as new entry with timestamp
- Don't delete old information (shows history)
- Let user decide which is current

## Enhancements

### Learning Profile (For {{child_name}} Specifically)

{{child_name}}'s person file (`6-People/Personal/{{child_name}}.md`) should maintain an extended Learning Profile section:

**Required tracking for {{child_name}}:**
```markdown
## Learning Profile

### Diagnoses
- ADHD
- NVLD (Nonverbal Learning Disability)
- Dyscalculia

### Executive Function Context
- EF development can lag 30% behind peers (at 15, EF may align with 10-11 year old)
- What looks like "low motivation" is often neurodevelopmental reality, not character flaw
- Traditional "should" motivation typically fails

### Learning Style
- [Track discoveries about how {{child_name}} learns best]
- [What formats/approaches click vs. don't]

### ADHD Motivators (What Works)
Frame challenges using these five brain motivators:
1. **Novelty** - New, different, exciting approaches
2. **Urgency** - Deadlines, time pressure
3. **Interest** - Connected to passions/curiosity
4. **Competition** - Games, challenges, rankings
5. **Enjoyment** - Fun, play, humor

### EF Strategies That Work
- [Document what helps]
- [What external scaffolding is effective]

### EF Strategies That Don't Work
- [Document what doesn't help]
- [What creates shame vs. support]

### Current Challenges
- [Track active struggles]
- [Areas needing support]
```

**When to update Learning Profile:**
- After conversations with {{child_name}} that reveal learning insights
- After feedback from Sarah about school/tutoring
- After observing what helps vs. doesn't during father-son time
- After EF support conversations (template in father-excellence research)

### Executive Function Support Strategies

When updating any child's person file who has EF challenges, consider tracking:

**External Scaffolding Approaches:**
- Break tasks into collaborative checklists (2-3 steps at a time)
- Use visual timers and progress trackers
- Provide body doubles (working alongside)
- Create routine and predictability
- Use external memory aids (written lists, reminders)

**Interest-Based Motivation:**
- Connect tasks to genuine interests where possible
- Use gamification and challenges
- Create urgency when natural interest is low
- Build in novelty and variety
- Celebrate process, not just outcomes

**What to Avoid:**
- Judging by neurotypical standards
- Creating shame through frustration
- Expecting intrinsic motivation for uninteresting tasks
- Over-monitoring (enable independence with scaffolding)

### Communication Preferences

For all person files, track how each person prefers to receive information:

**Fields to capture:**
```markdown
## Communication Preferences

### Preferred Channel
- [Primary: Email/Slack/SMS/Call/In-person]
- [Secondary: ]

### Timing Preferences
- [Best time to reach them]
- [Response time expectations]

### Communication Style
- [Direct vs. contextual]
- [Prefers written vs. verbal]
- [Detail level: high-level vs. granular]
- [How they handle difficult feedback]

### What Works
- [Approaches that land well]

### What Doesn't Work
- [Approaches to avoid]
```

**Update triggers:**
- Observing communication patterns over time
- Explicit preferences shared by the person
- Feedback on past communications
- Relationship dynamics discoveries
