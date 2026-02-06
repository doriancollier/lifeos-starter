---
name: person-context
description: Understand relationships, communication styles, and interaction history with people. Use when preparing to interact with someone, looking up a person's details, or managing professional relationships.
---

# Person Context Skill

Manages information about people and relationships within the vault.

## Vault Locations

- **Professional contacts**: `{{vault_path}}/workspace/6-People/Professional/`
  - {{company_1_name}} team: `workspace/6-People/Professional/Art-Blocks/`
- **Personal contacts**: `{{vault_path}}/workspace/6-People/Personal/`
- **Person template**: `{{vault_path}}/workspace/3-Resources/Templates/person-template.md`
- **People MOC**: `{{vault_path}}/workspace/7-MOCs/People-Network.md`

## Person Note Structure

Each person note contains:

### YAML Frontmatter
```yaml
name: "Person Name"
title: "Job Title"
company: "Company Name"
relationship: "boss/colleague/friend/family/client/partner"
communication_preference: "Slack/email/phone/text"
meeting_frequency: "weekly/monthly/as-needed"
last_interaction: "YYYY-MM-DD"
type: "person"
```

### Main Sections
1. **Basic Information** - Contact details, professional context
2. **Relationship Context** - How you know them, history
3. **Communication Style & Preferences** - How they like to communicate
4. **Current Projects & Involvement** - Active collaborations
5. **Personal Notes & Context** - Strengths, interests, important context
6. **Interaction History** - Recent interactions, key conversations
7. **Future Planning** - Relationship goals, action items
8. **AI Context Notes** - Important patterns for AI to remember

## Key People Reference

Key people are loaded dynamically from `workspace/0-System/config/contacts-config.json`.

### Company Contacts
Find in `contacts-config.json` under:
- `companies.company_1.contacts` → {{company_1_name}} team
- `companies.company_2.contacts` → {{company_2_name}} contacts
- `collaborators` → Cross-company collaborators

### Personal
| Name | File | Relationship |
|------|------|--------------|
| {{partner_name}} | Partner person file | Partner |
| {{child_name}} | Child person file | Child |

## Finding Person Information

### Search for a person by name
```bash
find "{{vault_path}}/workspace/6-People" -iname "*name*" -type f
```

### Get person's communication preference
```bash
grep "communication_preference:" "{{vault_path}}/workspace/6-People/Professional/[Company]/[person-file].md"
```

### Find all interactions with a person
```bash
# In meeting notes
grep -r "[Person Name]" "{{vault_path}}/workspace/5-Meetings/" --include="*.md" -l

# In daily notes
grep -r "[Person Name]" "{{vault_path}}/workspace/4-Daily/" --include="*.md" -l
```

### Find action items involving a person
```bash
grep -r "- \[ \].*[Person Name]" "{{vault_path}}/" --include="*.md"
```

## Communication Insights

When preparing to interact with someone, consider:

1. **Preferred channel** - Slack, email, phone, text
2. **Communication style** - Formal, informal, direct, collaborative
3. **Best times** - When they're most responsive
4. **Information preferences** - High-level vs detailed

## Relationship Strength Indicators

Track relationship health through:
- Frequency of interactions
- Quality of recent conversations
- Open action items
- Shared project involvement

## Creating New Person Notes

1. Copy template from `workspace/3-Resources/Templates/person-template.md`
2. Save to appropriate directory:
   - Professional: `workspace/6-People/Professional/[Company]/[name].md`
   - Personal: `workspace/6-People/Personal/[name].md`
3. Fill in known information
4. Add initial AI context notes

## Integration

- Links to meeting notes where they appear
- Links to projects they're involved in
- Referenced in daily notes when interactions occur
- Connected through the People-Network MOC
