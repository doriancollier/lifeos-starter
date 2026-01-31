---
description: First-run setup wizard to personalize LifeOS
---

# Onboarding Wizard

Guide the user through personalizing their LifeOS instance.

## Phase 1: Identity (Required)

Use AskUserQuestion to gather:
1. Full name
2. Timezone (provide common options)
3. Personality type (optional - MBTI or skip)
4. Location (city, state/country)

## Phase 2: Life Areas

Ask about:
1. Work contexts (companies, freelance, etc.)
   - For each:
     - Name and role
     - **Short ID** (2-4 chars for folder/command naming, e.g., "ab", "acme")
     - **Detection keywords** (words/phrases in meeting titles that indicate this company - e.g., product names, project codenames, team names)
     - Key people
2. Personal/family members to track
   - Partner name (optional)
   - Children names (optional)
3. Health tracking interest (yes/no)

## Phase 2.5: Key Contacts

For each company/work context, collect key contacts:
1. Ask: "Who are the key people you work with at [company]?"
2. For each person mentioned, collect:
   - Full name
   - Role (optional)
   - Communication preference (email, slack, sms, call)
3. Also collect external collaborators (people you work with across companies)

**Format for collection:**
```
Name: Alex Smith
Role: CTO
Preferred contact: Slack
```

This information powers meeting prep, relationship management, and the meeting sync script.

## Phase 3: Coaching Preferences

Ask:
1. Coaching intensity (1-10 scale)
   - 1-3: Gentle suggestions
   - 4-6: Balanced accountability
   - 7-10: Relentless challenger
2. Preferred communication style (direct, warm, balanced)

## Phase 4: Integrations (Optional)

Ask about:
1. Google Calendar - Do they want calendar integration?
2. Apple Health - Do they want health data sync?
3. macOS Reminders - Do they want task sync to Reminders?

## After Gathering Information

1. Update `/0-System/config/user-config.md` with their answers
2. Update `/CLAUDE.md` - replace placeholders with actual values
3. Update `/.claude/rules/coaching.md` - personalize
4. Create company context files in `/2-Areas/` for each company
5. Create `/2-Areas/Personal/foundation.md` with their info
6. **Update `/0-System/config/contacts-config.json`** with collected contacts:
   - For each company, set `id` (short ID) and `keywords` (detection keywords array)
   - Add company contacts under `companies.<company_id>.contacts[]`
   - Add collaborators under `collaborators[]`
   - Add partner under `personal.partner`
   - Add children under `personal.children[]`
   - Each contact needs: `name`, `aliases` (lowercase variations), `role`, `communicationPreference`
7. Optionally create person files in `/6-People/` for key contacts
8. Set `onboarding_complete: true` in user-config.md

## Completion Message

After setup, tell them:
- "LifeOS is now personalized for you!"
- Suggest running `/daily:plan` to start their first day
- Point them to `/0-System/guides/getting-started.md` for help
