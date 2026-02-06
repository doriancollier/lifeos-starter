---
description: Create a gift planning project for an occasion
argument-hint: occasion-name (e.g., "Christmas 2025")
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# Create Gifts Command

Creates a new gift planning project in `workspace/1-Projects/Current/` using the gift planning template.

## Arguments

- `$ARGUMENTS` - The occasion name (e.g., "Christmas 2025", "Mom's Birthday", "Wedding Gift")

## Task

### Step 1: Parse the Occasion Name

Extract the occasion from `$ARGUMENTS`. If no name provided, ask the user.

Convert to a folder-friendly format:
- "Christmas 2025" → `Christmas-2025`
- "Mom's Birthday" → `Moms-Birthday`

### Step 2: Create the Project Folder

Create the project folder at:
```
{{vault_path}}/1-Projects/Current/[Occasion-Name]-Gifts/
```

### Step 3: Read the Template

Read the gift planning template:
```
{{vault_path}}/3-Resources/Templates/gift-planning.md
```

### Step 4: Create the Gift Planning Note

Create the main note at:
```
{{vault_path}}/1-Projects/Current/[Occasion-Name]-Gifts/gift-list.md
```

Replace template placeholders:
- `{{title}}` → "[Occasion] Gifts"
- Update `type: template` → `type: project`
- Update `occasion:` with the occasion name
- Update `date:` with the occasion date (if known)

### Step 5: Gather Initial Details

Use AskUserQuestion to collect:
1. **Occasion Date**: When is this? (helps calculate shipping deadlines)
2. **Budget**: What's your total budget?
3. **Recipients**: Who are you buying for? (can add more later)

### Step 6: Calculate Key Dates

Based on occasion date, calculate and fill in:
- **2 weeks before**: Last day for standard shipping
- **1 week before**: Last day for expedited shipping
- **3 days before**: Emergency local shopping only

### Step 7: Pre-populate Recipients (if known)

For common occasions:
- **Christmas**: Suggest {{partner_name}}, {{child_name}}, family members from People notes
- **Birthday**: Suggest the birthday person

### Step 8: Update Life Events Timeline

Read and update `workspace/7-MOCs/Life-Events-Timeline.md`:

1. Calculate days until occasion
2. Determine which timeframe section based on occasion date
3. Add entry in appropriate section:
   ```markdown
   ### 🎄 [Occasion] - [Date]
   - **Type**: Holiday + Gift-Giving
   - **Status**: X days away
   - **Project**: [[Occasion-Gifts]]
   - **Budget**: [budget]
   - **Shipping Deadline**: [2 weeks before date] (Z days)
   - **Recipients**: [count] people
   - **Status**: [X gifts purchased/wrapped/shipped]
   ```
4. Update "Last Updated" date in timeline frontmatter and header
5. If shipping deadline is within 30 days, emphasize urgency

**Example:**
```markdown
### 🎄 Christmas 2025 - December 25
- **Type**: Holiday + Gift-Giving
- **Status**: 29 days away
- **Project**: [[Christmas-2025-Gifts]]
- **Budget**: $1,000
- **Shipping Deadline**: December 11 (15 days - URGENT)
- **Recipients**: {{partner_name}}, {{child_name}}, Leilani, Kyrie, Nevaeh
- **Status**: ⚠️ No gifts purchased yet
```

### Step 9: Output Summary

```markdown
## Gift Planning Created: [Occasion]

**Location**: `workspace/1-Projects/Current/[Occasion]-Gifts/`

### Details
- **Occasion**: [occasion]
- **Date**: [date]
- **Budget**: [budget]
- **Recipients**: [count] people

### Key Deadlines
- Standard shipping by: [date]
- Expedited shipping by: [date]
- Occasion: [date]

### Next Steps
1. Add gift ideas for each recipient
2. Set individual budgets
3. Start shopping!

Would you like me to:
- [ ] Open the gift list in Obsidian?
- [ ] Add specific recipients now?
- [ ] Create calendar reminders for deadlines?
```

## Edge Cases

- **No occasion provided**: Ask for one
- **Already exists**: Warn and offer to open existing
- **Past date**: Warn that occasion has passed
- **Very soon**: Highlight shipping deadlines urgently
