---
description: Weekly relationship check-in with  using State of Union format
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Partner State of Union Command

Guide the user through a **weekly relationship check-in with ** using the State of Union format. This is a structured 60-minute conversation that strengthens connection and prevents issues from building up.

> **Research Basis**: Couples who spend just one hour per week on structured check-ins transform their conflict management. The 5:1 ratio (positive to negative interactions) predicts relationship success with remarkable accuracy.

## Context

- **Template**: `[[partner-state-of-union]]` in `3-Resources/Templates/`
- **Output location**: `5-Meetings/YYYY/MM-Month/SoU-YYYY-MM-DD.md` OR `2-Areas/Personal/Partner/State-of-Union/`
- **Partner research**: `1-Projects/Current/Planning-System/extraction/19-partner-excellence-extraction.md`
- **'s person file**: `6-People/Personal/.md`

## Process

### Step 1: Setup

1. **Get current date**
   ```bash
   date +%Y-%m-%d
   date +%A
   ```

2. **Check when last State of Union occurred**
   - Search for most recent SoU note
   - If more than 7 days, note the gap

3. **Review 's person file** for current context (stressors, recent events, communication preferences)

### Step 2: Pre-Meeting Preparation (For )

Before the meeting with , ask :

**Appreciations Prep**:
Ask: "What are 5 specific things you appreciate about  from this week?"

Prompt if needed:
- "What did she do that made your life easier?"
- "When did she show up for you or ?"
- "What character trait did you admire this week?"
- "What made you grateful to be with her?"
- "What small gesture meant something to you?"

**Format**: Each appreciation should be specific, not generic.
- Bad: "I appreciate that you're a good partner"
- Good: "I appreciate how you handled 's meltdown on Tuesday with such patience"

**Concerns Prep**:
Ask: "Do you have any concerns you'd like to bring up? (Remember: concerns about behaviors, not character)"

**ATTUNE Check**:
Before entering the conversation, remind:
- **A**wareness - Notice your state and 's
- **T**olerance - Accept differences without judgment
- **T**urning toward - Respond to bids for connection
- **U**nderstanding - Seek to understand before being understood
- **N**on-defensive listening - Hear without preparing rebuttals
- **E**mpathy - Feel with, not just for

### Step 3: The Meeting Format

Guide through the four-part structure (60 minutes total):

#### Part 1: Appreciations (10-15 min)

**Purpose**: Build positive emotional bank account. Start with what's working.

**Format**: Each person shares 5 specific appreciations.

 shares first (lead by example):
"I appreciate [specific thing] because [impact/feeling]."

Then  shares 5.

**Coaching**: If appreciations are generic, gently ask: "Can you make that more specific? What exactly did she do?"

**Capture both sets of appreciations.**

#### Part 2: What's Working (10-15 min)

**Purpose**: Reinforce positive patterns in the relationship.

Ask each person: "What's working well in our relationship right now?"

Explore:
- Communication patterns that are helping
- Routines that are serving the relationship
- Ways you're supporting each other's growth
- Areas where you feel connected

**Capture 3-5 items.**

#### Part 3: Concerns (20-25 min)

**Purpose**: Address issues before they fester. This is NOT a complaint session.

**Rules**:
- One concern at a time
- Focus on feelings and needs, not blame
- Use "I feel..." not "You always..."
- Aim for understanding, then agreement

**Format for raising concerns**:
1. **Issue**: What is the specific behavior/situation?
2. **My feelings**: How does this make me feel?
3. **My needs**: What do I need in this area?
4. **Request**: What would help? (specific, actionable)

**Process each concern**:
- Listen to understand (not to respond)
- Reflect back: "What I hear you saying is..."
- Validate feelings (even if you disagree with interpretation)
- Look for agreement or compromise
- Document any agreements reached

**Four Horsemen Watch**:
If any of these appear, gently redirect:
- **Criticism** (character attack) → "Can you focus on the behavior, not her character?"
- **Contempt** (superiority, eye-rolling) → "Let's take a breath. Contempt is toxic."
- **Defensiveness** → "What's your 5% responsibility here?"
- **Stonewalling** (shutting down) → "Do you need a 20-minute break to self-soothe?"

**Capture concerns and agreements.**

#### Part 4: Closing Affirmation (5-10 min)

**Purpose**: End on connection, not problems.

Ask: "What do you love about our relationship? What are you grateful for?"

Optional Gottman-inspired questions:
- "What's one thing you're looking forward to doing together?"
- "How can I support you this week?"
- "Is there anything you need from me that you haven't asked for?"

**Capture closing affirmations.**

### Step 4: Bids for Connection Tracking

Review the week's bids:

Ask: "Thinking about this week, did you turn toward or away from 's bids for connection?"

**Bid examples**:
- "Look at this" (sharing something)
- "How was your day?" (requesting attention)
- Touch, gesture, look (nonverbal bids)
- "What do you think about..." (seeking opinion)

**Target**: Turn toward 86%+ of bids (couples who hit this stay married).

**Capture reflection on bids.**

### Step 5: Action Items

Document any action items from the meeting:

```markdown
## Action Items
- [ ] [Owner] [Action] by [Date]
- [ ] [Owner] [Action] by [Date]
```

**Rules**:
- Each action has one owner
- Each action has a deadline
- Keep actions to 1-3 maximum
- These are relationship priorities—treat them as A-tasks

### Step 6: Schedule Next Meeting

Confirm: "Same time next week?"

Add to calendar if not already recurring.

## Output

Create the State of Union note:

```markdown
---
title: "State of Union - YYYY-MM-DD"
type: state-of-union
date: YYYY-MM-DD
participants: [, ]
---

# State of Union - [Day], [Month] [Date], [Year]

## Appreciations

### 's Appreciations for 
1.
2.
3.
4.
5.

### 's Appreciations for 
1.
2.
3.
4.
5.

## What's Working
-

## Concerns Addressed

### Concern 1: [Topic]
- **Issue**: [Description]
- **Feelings**: [How it made someone feel]
- **Needs**: [What's needed]
- **Agreement Reached**: [Resolution]

### Concern 2: [Topic]
- **Issue**:
- **Feelings**:
- **Needs**:
- **Agreement Reached**:

## Closing Affirmation
- :
- :

## Bids for Connection
**This week's reflection**: [Turn toward rate, notable moments]

## Action Items
- [ ] [Owner] [Action] by [Date]
- [ ]

## Notes
- Next meeting: [Date]
- EMC topics for separate discussion: [if any came up]

---
*"In marriage, small things often." - John Gottman*
```

**Location Options**:
- `5-Meetings/YYYY/MM-Month/SoU-YYYY-MM-DD.md` (if treating as meeting note)
- `2-Areas/Personal/Partner/State-of-Union/YYYY-MM-DD.md` (if keeping separate)

## Interaction Guidelines

- **This is sacred time** - Protect it. Don't rush.
- **Start positive** - Appreciations first, always
- **One concern at a time** - Don't pile on
- **Seek understanding first** - Before agreement
- **Separate EMC from relationship** - Business topics get noted but discussed separately
- **Watch for Horsemen** - Redirect gently if they appear
- **End on connection** - Never end on unresolved conflict
- **Be a role model** -  leads with vulnerability and warmth

## Coaching Prompts

Use these during or after the meeting:

- "Are you treating  as A-priority or just saying you are?"
- "Did you show up with courage AND love, or just efficiency?"
- "Could your appreciation land warmer? More specific?"
- "Are you listening to understand or to respond?"
- "What's your 5% in this concern?"
- "Are you turning toward her bids, or getting lost in work?"

## EMC Business Separation

If business topics come up:
- Acknowledge: "That sounds important for EMC."
- Defer: "Let's note that for a separate EMC meeting."
- Protect: "This time is for us as partners, not business partners."

**Capture any EMC topics** that need separate discussion.

## Examples

**Example Appreciation**:
- "I appreciate how you stayed calm when  had a meltdown at the restaurant on Sunday. I was getting frustrated, and your patience reminded me to breathe. It made me feel like we're a team."

**Example Concern (well-framed)**:
- **Issue**: "When you're on your phone during dinner, I feel disconnected."
- **Feelings**: "I feel like I'm not as important as what's on the screen."
- **Needs**: "I need us to have uninterrupted time to connect each day."
- **Request**: "Could we try phones-away during dinner this week?"

**Example Closing Affirmation**:
- "I'm grateful that we can have these honest conversations. I love that we're building something together. I'm looking forward to our trip next month."

## Related

- [[partner-excellence]] - Research on relationship practices
- [[]] - Partner person file
- [[daily-note]] - Add daily "Did I turn toward?" reflection
- [[monthly-retro]] - Monthly relationship review section
