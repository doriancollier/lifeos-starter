---
name: meeting-prep
description: Prepare for meetings by gathering context about attendees, related projects, and past discussions. Use before any scheduled meeting or when the user needs to prepare for an interaction.
---

# Meeting Prep Skill

Gathers relevant context before meetings to ensure productive discussions.

## Vault Locations

- **Meeting notes**: `{{vault_path}}/workspace/5-Meetings/YYYY/MM-Month/`
- **People**: `{{vault_path}}/workspace/6-People/`
- **Projects**: `{{vault_path}}/workspace/1-Projects/`
- **Company areas**: `{{vault_path}}/workspace/2-Areas/`

## Meeting Templates by Company

| Company | Template | Key Attendees |
|---------|----------|---------------|
| {{company_1_name}} | `workspace/3-Resources/Templates/art-blocks-meeting.md` | Load from contacts-config.json |
| {{company_2_name}} | `workspace/3-Resources/Templates/144-meeting.md` | Load from contacts-config.json |
| {{company_3_name}} | `workspace/3-Resources/Templates/emh-meeting.md` | {{partner_name}} |
| Personal | `workspace/3-Resources/Templates/personal-meeting.md` | Varies |

## Recurring Meeting Templates

For recurring meetings (weekly syncs, standups, etc.), search for matching templates:

```bash
# Search for recurring meeting templates
find "{{vault_path}}/workspace/3-Resources/Templates" -name "recurring-meeting-*.md" -type f
```

**Template Matching Logic:**
1. Normalize the meeting name (lowercase, remove special chars)
2. Search for templates matching: `recurring-meeting-*[normalized-name]*.md`
3. If found, surface the template with its pre-meeting checklist and agenda structure

**Known Recurring Meeting Templates:**
| Meeting | Template | Schedule |
|---------|----------|----------|
| Engineering Sync | `recurring-meeting-engineering-sync.md` | Monday 11:30 AM CT |
| AssetOps Sync | `recurring-meeting-assetops.md` | Daily (Mon-Fri) 2:30 PM CT |

When preparing for a recurring meeting:
1. **First**: Check if a recurring template exists
2. **If found**: Surface the template's pre-meeting checklist and agenda structure
3. **Include**: Previous meeting notes of the same type (search by meeting name pattern)

## Preparation Workflow

### 1. Identify Attendees
- Look up each person in `workspace/6-People/Professional/` or `workspace/6-People/Personal/`
- Note their role, communication style, and recent interactions

### 2. Find Previous Meetings
```bash
# Find meetings with a specific person
grep -r "attendees:.*Person Name" "{{vault_path}}/workspace/5-Meetings/" --include="*.md"

# Find recent meetings for a company
ls -la "{{vault_path}}/workspace/5-Meetings/2025/"
```

### 3. Gather Project Context
- Find active projects related to meeting topics
- Review recent decisions and action items
- Identify open questions or blockers

### 4. Check for Open Action Items
```bash
# Find action items assigned to an attendee
grep -r "[Attendee Name].*Due:" "{{vault_path}}/workspace/5-Meetings/" --include="*.md"
```

## Information to Gather

### About Each Attendee
- Full name and role
- Communication preferences
- Decision-making authority
- Recent interactions and outcomes
- Open action items they own

### About the Context
- Related projects and their status
- Recent decisions made
- Open questions or blockers
- Strategic context

### From Previous Meetings
- Key decisions made
- Outstanding action items
- Topics that need follow-up
- Patterns in discussions

## Output Format

When preparing for a meeting, provide:

```markdown
## Meeting Prep: [Meeting Title]

### Attendees
- **[Name]** - [Role] - [Key context]

### Previous Meetings
- [Date]: [Key outcome/decision]
- [Date]: [Key outcome/decision]

### Open Action Items
- [ ] [Person]: [Action item] - Due: [date]

### Related Projects
- [[Project Name]] - Status: [status]

### Suggested Agenda Items
1. Follow up on [previous discussion]
2. Decision needed on [topic]
3. Update on [project/initiative]

### Key Questions to Address
- [Question 1]
- [Question 2]
```

## {{company_1_name}} Specific Context

Key people and their focus areas are loaded from `workspace/0-System/config/contacts-config.json`.

To view contacts for meeting prep, check:
- Company contacts in `contacts-config.json` under `companies.company_1.contacts`
- Person files in `workspace/6-People/Professional/`

Active projects to check:
- Current initiatives in `workspace/1-Projects/Current/`
- Company area documents in `workspace/2-Areas/{{company_1_name}}/`

## {{company_2_name}} Specific Context

Key contacts loaded from `contacts-config.json` under `companies.company_2.contacts`.
- Check `workspace/2-Areas/{{company_2_name}}/` for current status

## Integration with Other Skills

- Use **person-context** skill for deeper attendee research
- Use **task-system** skill to find related tasks
- Use **obsidian-open** skill to open relevant notes in Obsidian

## Enhancements

### Pre-Mortem Consideration

For meetings involving major decisions, suggest running a pre-mortem first:

**When to surface pre-mortem prompt:**
- Meeting agenda includes strategic decisions (budget, hiring, partnerships, major pivots)
- Meeting will determine resource allocation
- Meeting involves irreversible or high-stakes choices

**Pre-mortem prompt to suggest:**
> "This meeting involves [major decision]. Before the meeting, consider: 'Imagine it's 6 months from now and this decision failed spectacularly. What went wrong?'"

**Include in meeting prep output:**
```markdown
### Pre-Mortem Consideration

This meeting involves a major decision: [decision description]

Before the meeting, consider these failure scenarios:
- What's the most likely reason this fails?
- What assumptions are we making that might be wrong?
- What are we not talking about? (Elephants)
```

### Strategic Importance Check

During meeting prep, assess whether the meeting advances strategic priorities:

**Questions to surface:**
- "Is this meeting advancing a Big Rock or just handling gravel?"
- "Does this meeting connect to a quarterly priority or is it maintenance?"
- "Could this meeting be shorter, asynchronous, or eliminated entirely?"

**Strategic alignment indicators:**
| Indicator | Big Rock (Strategic) | Gravel (Tactical) |
|-----------|---------------------|-------------------|
| Connects to | Quarterly goals, OKRs | Day-to-day operations |
| Decision scope | Irreversible, high-stakes | Reversible, low-stakes |
| Attendees | Decision-makers | Implementers |
| Outcome | Strategic direction | Task completion |

**Include in meeting prep output:**
```markdown
### Strategic Importance Check

**Strategic alignment**: [High/Medium/Low]
**Rationale**: [Brief explanation of how this meeting connects to Big Rocks]
**Consideration**: [If Low, suggest whether this could be handled async or delegated]
```

### Leverage Assessment for Meeting Prep

Before investing significant time in meeting prep, assess:
- Is this meeting high-leverage (strategic direction, unblocking others, building relationships)?
- Or is this meeting low-leverage (status updates, routine check-ins)?

High-leverage meetings deserve thorough prep; low-leverage meetings can use abbreviated prep.
