---
description: Create a new trip planning project
argument-hint: trip-name (e.g., "January Wedding Trip")
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Create Trip Command

Creates a new trip planning project in `/1-Projects/Current/` using the trip planning template.

## Arguments

- `$ARGUMENTS` - The name of the trip (e.g., "January Wedding Trip", "Paris Vacation 2025")

## Task

### Step 1: Parse the Trip Name

Extract the trip name from `$ARGUMENTS`. If no name provided, ask the user.

Convert to a folder-friendly format:
- "January Wedding Trip" → `January-Wedding-Trip`
- "Paris Vacation 2025" → `Paris-Vacation-2025`

### Step 2: Create the Project Folder

Create the project folder at:
```
{{vault_path}}/1-Projects/Current/[Trip-Name]/
```

### Step 3: Read the Template

Read the trip planning template:
```
{{vault_path}}/3-Resources/Templates/trip-planning.md
```

### Step 4: Create the Trip Note

Create the main trip note at:
```
{{vault_path}}/1-Projects/Current/[Trip-Name]/[Trip-Name].md
```

Replace template placeholders:
- `{{title}}` → Trip name
- `{{date}}` → Today's date
- Update `type: template` → `type: project`
- Update `status: planning`

### Step 5: Gather Initial Details

Use AskUserQuestion to collect:
1. **Destination**: Where are you going?
2. **Travel Dates**: When are you traveling?
3. **Travelers**: Who is going?
4. **Purpose**: What's the occasion? (vacation, wedding, business, etc.)

Update the Trip Overview section with these details.

### Step 6: Add to Daily Note (Optional)

If the trip is within the next 30 days, add a task to today's daily note:
```
- [ ] 📅 Start planning [[Trip-Name]] - travel on [date]
```

### Step 7: Update Life Events Timeline

Read and update `/7-MOCs/Life-Events-Timeline.md`:

1. Calculate days until trip departure
2. Determine which timeframe section (This Week / Next 30 Days / Next 90 Days / Beyond 90 Days)
3. Add entry in appropriate section:
   ```markdown
   ### ✈️ [Trip Name] - [Dates]
   - **Type**: Travel + [Purpose if wedding/event]
   - **Status**: X days away
   - **Project**: [[Trip-Name]]
   - **Destination**: [Destination]
   - **Travelers**: [Travelers]
   - **Key Dependencies**:
     - [Critical items from pre-travel checklist if urgent]
   ```
4. Update "Last Updated" date in timeline frontmatter and header
5. If trip is within 90 days, also add to Project Status Overview table

**Example:**
```markdown
### 🌴 January Wedding Trip - January 23-25, 2026
- **Type**: Travel + Social Event
- **Status**: 58 days away
- **Project**: [[January-Wedding-Trip]]
- **Destination**: Los Cabos, Mexico
- **Travelers**: {{user_first_name}} & {{partner_name}}
- **URGENT Dependencies**:
  - 🔴 Arrange childcare for {{child_name}}
  - 🔴 Board Zoey at SkyBlue Kennels
  - 🔴 Book flights
```

### Step 8: Output Summary

```markdown
## Trip Created: [Trip Name]

**Location**: `/1-Projects/Current/[Trip-Name]/`

### Trip Details
- **Destination**: [destination]
- **Dates**: [dates]
- **Travelers**: [travelers]
- **Purpose**: [purpose]

### Next Steps
1. Fill in the Pre-Travel Checklist
2. Start booking flights and accommodations
3. Create packing list

Would you like me to:
- [ ] Open the trip note in Obsidian?
- [ ] Add specific booking information?
- [ ] Create calendar events for travel dates?
```

## Edge Cases

- **No trip name provided**: Ask for one
- **Trip already exists**: Warn and ask to open existing or create new
- **Very short notice trip**: Highlight urgent checklist items
