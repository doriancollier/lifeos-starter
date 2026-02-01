---
description: First-run setup wizard to personalize LifeOS
allowed-tools: AskUserQuestion, Read, Write, Edit, Bash, Glob
---

# Onboarding Wizard

Guide the user through personalizing their LifeOS instance. All user configuration is stored in `.user/` directory.

## Overview

This wizard collects user information and writes it to YAML configuration files in `.user/`, then runs scripts to generate personalized system files.

**Configuration files created:**
- `.user/identity.yaml` - Name, timezone, personality, family
- `.user/companies.yaml` - Company definitions with contacts
- `.user/coaching.yaml` - Coaching intensity and preferences
- `.user/integrations.yaml` - Which integrations are enabled
- `.user/health.yaml` - Health export settings (if enabled)
- `.user/calendars.yaml` - Calendar configuration (if enabled)

**Generated files:**
- `CLAUDE.md` - From `CLAUDE.template.md`
- `.claude/rules/coaching.md` - From `.claude/rules/coaching.template.md`
- `.claude/settings.json` - Hook configuration

---

## Questioning Guidelines

**CRITICAL**: Follow these rules for ALL questions throughout onboarding:

### When to Use AskUserQuestion Tool

Use `AskUserQuestion` when there are sensible options to choose from:
- Yes/no decisions
- Multiple choice selections (timezone, coaching level, integrations)
- Preference selections with clear options

### When to Ask in Plain Text

Ask directly in your response (no tool) when the answer requires free-form text:
- Names (user's name, partner's name, children's names, company names)
- Email addresses
- Locations (city, state/country)
- Any unique personal information

### Intelligent Defaults

- Always mark a recommended option with "(Recommended)" at the end of the label
- Choose defaults based on:
  - Most common user choice (e.g., "America/Chicago" for US Central)
  - Platform detection (macOS → enable Reminders, Calendar)
  - Balanced/moderate options when uncertain (e.g., coaching level 7)

### One Question at a Time

- Ask each question individually, wait for response
- Don't batch multiple questions unless they're tightly related
- After each answer, confirm understanding before moving on

---

## Phase 0: Dependencies (Automatic)

Before starting the wizard, ensure required Python packages are installed:

```bash
python3 ./.claude/scripts/ensure_dependencies.py
```

This installs PyYAML if missing. If installation fails (e.g., permissions), inform the user:
- "I need to install a Python package (pyyaml) for configuration. Please run: `pip3 install pyyaml`"
- Wait for confirmation before proceeding

---

## Phase 1: Identity (Required)

Ask each question **one at a time** in this order:

### 1.1 Full Name (Plain Text)

Ask directly: "What's your full name?"

Do NOT use AskUserQuestion - this requires free-form text input.

### 1.2 First Name (Infer or Confirm)

**Intelligent default**: Extract from full name automatically.

Ask for confirmation only if ambiguous (e.g., "J. Robert Smith" → ask which name they prefer).

### 1.3 Timezone (AskUserQuestion)

Use AskUserQuestion with common options. Detect likely timezone from system if possible.

```
question: "What timezone are you in?"
header: "Timezone"
options:
  - label: "America/Chicago - Central Time (Recommended)"
    description: "US Central timezone (CST/CDT)"
  - label: "America/New_York - Eastern Time"
    description: "US Eastern timezone (EST/EDT)"
  - label: "America/Denver - Mountain Time"
    description: "US Mountain timezone (MST/MDT)"
  - label: "America/Los_Angeles - Pacific Time"
    description: "US Pacific timezone (PST/PDT)"
```

Note: User can select "Other" to enter a different timezone.

### 1.4 Location (Plain Text)

Ask directly: "What city and state/country are you located in?"

Do NOT use AskUserQuestion - this requires free-form text input.

### 1.5 Email Address (Plain Text)

Ask directly: "What's your primary email address?"

Do NOT use AskUserQuestion - this requires free-form text input.

### 1.6 Personality Type (AskUserQuestion - Optional)

```
question: "Do you know your personality type? This helps tailor coaching style."
header: "Personality"
options:
  - label: "Skip for now (Recommended)"
    description: "You can add this later in .user/identity.yaml"
  - label: "INTJ"
    description: "Architect - strategic, independent, analytical"
  - label: "ENTJ"
    description: "Commander - decisive, ambitious, strategic"
  - label: "INFJ"
    description: "Advocate - insightful, principled, compassionate"
```

Note: User can select "Other" to enter a different MBTI type.

**After collecting, write to `.user/identity.yaml`:**

```yaml
user:
  name: "[Full name]"
  first_name: "[First name]"
  birthdate: ""  # Can be added later
  location: "[Location]"
  timezone: "[Timezone]"
  email: "[Email]"
  work_email: ""  # Can be added later
  personality_type: "[Type or empty]"

family:
  partner_name: ""  # Collected in Phase 2
  children:
    - name: ""

communication:
  style: "balanced"

onboarding:
  complete: false
  completed_at: ""
```

---

## Phase 2: Life Areas

### 2.1 Work Contexts

#### 2.1.1 Number of Work Contexts (AskUserQuestion)

```
question: "How many work contexts do you have? (companies, freelance clients, side projects)"
header: "Work"
options:
  - label: "1 - Single company/focus (Recommended)"
    description: "One primary work context"
  - label: "2 - Two contexts"
    description: "e.g., full-time job + side project"
  - label: "3 - Three contexts"
    description: "e.g., multiple companies or clients"
  - label: "0 - Personal use only"
    description: "No work contexts, just personal life management"
```

#### 2.1.2 For Each Work Context (Plain Text)

For each context, ask these questions directly (no AskUserQuestion):

1. "What's the full name of your company/context?" (e.g., "Acme Corporation")
2. "What short ID should I use for folders and commands? (2-4 characters)" (e.g., "acme")

**Intelligent defaults**:
- Auto-generate short ID from company name (first 2-4 chars, lowercase)
- Confirm the suggested ID: "I'll use 'acme' as the short ID. Is that okay?"

#### 2.1.3 Detection Keywords (Plain Text - Optional)

Ask: "Are there any keywords in meeting titles that indicate this company? (product names, project codenames, team names) - or press Enter to skip"

**Intelligent default**: Skip if user presses Enter. Can be added later.

### 2.2 Family Members

#### 2.2.1 Partner (AskUserQuestion first, then Plain Text if yes)

```
question: "Do you have a partner you'd like relationship coaching for?"
header: "Partner"
options:
  - label: "Yes"
    description: "Enable relationship-focused coaching prompts"
  - label: "No / Skip (Recommended)"
    description: "Skip relationship coaching for now"
```

If yes, ask in plain text: "What's your partner's name?"

#### 2.2.2 Children (AskUserQuestion first, then Plain Text if yes)

```
question: "Do you have children you'd like parenting coaching for?"
header: "Children"
options:
  - label: "Yes"
    description: "Enable parenting-focused coaching prompts"
  - label: "No / Skip (Recommended)"
    description: "Skip parenting coaching for now"
```

If yes, ask in plain text: "What are your children's names? (comma-separated if multiple)"

**After collecting, update `.user/identity.yaml` family section and write `.user/companies.yaml`:**

```yaml
companies:
  company_1:
    name: "[Company 1 name]"
    id: "[short-id]"
    keywords: ["keyword1", "keyword2"]
    contacts: []

  company_2:
    name: "[Company 2 name or empty]"
    id: ""
    keywords: []
    contacts: []

  company_3:
    name: "[Company 3 name or empty]"
    id: ""
    keywords: []
    contacts: []

collaborators: []

personal:
  id: "personal"
  keywords: ["personal", "family", "home"]
```

---

## Phase 2.5: Key Contacts (Optional - Can Skip)

### 2.5.1 Ask If They Want to Add Contacts (AskUserQuestion)

```
question: "Would you like to add key contacts for your work contexts now?"
header: "Contacts"
options:
  - label: "Skip for now (Recommended)"
    description: "You can add people later with /create:person"
  - label: "Yes, add key contacts"
    description: "Add important colleagues and collaborators now"
```

### 2.5.2 If Adding Contacts (Plain Text)

For each company, ask: "Who are the 2-3 key people you work with at [company]? (names only, comma-separated)"

For each person mentioned:
1. Ask role in plain text: "What's [name]'s role?" (optional, can skip)
2. Ask communication preference using AskUserQuestion:

```
question: "How do you usually communicate with [name]?"
header: "Comms"
options:
  - label: "Slack (Recommended)"
    description: "Primary communication via Slack"
  - label: "Email"
    description: "Primary communication via email"
  - label: "Text/SMS"
    description: "Primary communication via text"
  - label: "Phone call"
    description: "Primary communication via calls"
```

**Update `.user/companies.yaml` with contacts:**

```yaml
companies:
  company_1:
    contacts:
      - name: "Alex Smith"
        role: "CTO"
        email: ""
        aliases: ["alex", "alex smith"]
        communication_preference: "slack"
```

---

## Phase 3: Coaching Preferences

### 3.1 Coaching Intensity (AskUserQuestion)

```
question: "How intense should the coaching be? Higher = more accountability and challenge."
header: "Intensity"
options:
  - label: "Level 7 - Challenging (Recommended)"
    description: "Pushes limits, questions assumptions, holds you accountable"
  - label: "Level 5 - Balanced"
    description: "Moderate accountability, suggests improvements gently"
  - label: "Level 3 - Supportive"
    description: "Gentle reminders, celebrates progress, minimal pushback"
  - label: "Level 9 - Relentless"
    description: "Maximum accountability, no excuses accepted, tough love"
```

### 3.2 Communication Style (AskUserQuestion)

```
question: "What communication style do you prefer?"
header: "Style"
options:
  - label: "Balanced (Recommended)"
    description: "Mix of directness and warmth depending on context"
  - label: "Direct"
    description: "Straight to the point, efficient, minimal softening"
  - label: "Warm"
    description: "More supportive tone, encouraging language"
```

**Write to `.user/coaching.yaml`:**

```yaml
coaching:
  intensity: [1-10]
  style_label: "[Supportive/Balanced/Challenging/Relentless]"

role_priorities:
  emergency:
    - child
    - partner
    - work
  default: "balance"
  biases:
    - "Over-prioritizes professional work"

personality_coaching:
  notes: []  # Can be populated based on personality type

question_emphasis:
  - planning
  - decision-making
  - energy

integration_points:
  before_meetings: true
  before_a_priorities: true
  before_skipping_tasks: true
  after_interactions: false
```

---

## Phase 4: Integration Configuration

Ask about each integration one at a time using AskUserQuestion.

**Platform detection**: If on macOS, recommend enabling Reminders and Email. If Google Calendar MCP is configured, recommend enabling Calendar.

### 4.1 Google Calendar (AskUserQuestion)

```
question: "Enable Google Calendar integration? This lets me check your schedule during planning and help manage events."
header: "Calendar"
options:
  - label: "Yes, enable Calendar (Recommended)"
    description: "Requires Google Calendar MCP server to be configured"
  - label: "No, skip Calendar"
    description: "Won't check calendar during planning"
```

If enabled, ask in plain text: "What's your primary calendar email address?"

Write to `.user/calendars.yaml`.

### 4.2 Apple Health (AskUserQuestion)

```
question: "Enable Apple Health sync? This imports health data (steps, sleep, activity rings) for coaching context."
header: "Health"
options:
  - label: "No, skip Health (Recommended)"
    description: "Requires 'Health Auto Export' iOS app - can enable later"
  - label: "Yes, enable Health sync"
    description: "Import health metrics from iPhone via iCloud"
```

If enabled:
- **Intelligent default**: Use `~/Library/Mobile Documents/com~apple~CloudDocs/Health Auto Export`
- Confirm: "I'll look for health data in the default iCloud location. Is that correct?"
- Only ask for custom path if user says the default won't work

Write to `.user/health.yaml`.

### 4.3 macOS Reminders (AskUserQuestion)

```
question: "Enable macOS Reminders sync? This creates a two-way link between vault tasks and Apple Reminders for mobile access and Siri."
header: "Reminders"
options:
  - label: "Yes, enable Reminders (Recommended)"
    description: "Manage tasks from iPhone, Apple Watch, or Siri"
  - label: "No, skip Reminders"
    description: "Tasks stay only in the vault"
```

No additional configuration needed if enabled.

### 4.4 Email - Mail.app (AskUserQuestion)

```
question: "Enable email reading from Mail.app? This lets me help triage and summarize emails."
header: "Email"
options:
  - label: "Yes, enable Email (Recommended)"
    description: "Read and triage emails from Mail.app"
  - label: "No, skip Email"
    description: "Won't access email"
```

No additional configuration needed if enabled.

**Write to `.user/integrations.yaml`:**

```yaml
integrations:
  reminders:
    enabled: [true/false]
    description: "Bidirectional sync with macOS Reminders"
    hooks:
      - reminders-session-sync.py
      - reminders-task-detector.py
    requirements:
      - "macOS with Reminders app"

  health:
    enabled: [true/false]
    description: "Sync health metrics from Apple Health"
    hooks:
      - health-session-sync.py
    requirements:
      - "Health Auto Export iOS app"

  calendar:
    enabled: [true/false]
    description: "Google Calendar integration via MCP"
    hooks: []
    requirements:
      - "Google Calendar MCP server"

  email:
    enabled: [true/false]
    description: "Read emails from Mail.app"
    hooks: []
    requirements:
      - "macOS with Mail.app"

  supernormal:
    enabled: false
    description: "Import meeting transcripts"
    hooks: []
    requirements:
      - "SuperNormal account"

core_hooks:
  - session-context-loader.py
  - prompt-timestamp.py
  - directory-guard.py
  - frontmatter-validator.py
  - task-format-validator.py
  - table-format-validator.py
  - task-sync-detector.py
  - auto-git-backup.sh
```

---

## Phase 5: Theme Preferences

### 5.1 Theme Setup (AskUserQuestion)

```
question: "Would you like to set up a personalized color theme for VS Code and Obsidian?"
header: "Theme"
options:
  - label: "Use default midnight theme (Recommended)"
    description: "Deep navy with blue accents - looks great, no setup needed"
  - label: "Yes, pick my own color"
    description: "Choose a color to generate a custom theme"
```

### 5.2 If Custom Theme - Favorite Color (AskUserQuestion)

Only ask if user chose custom theme:

```
question: "What color would you like your theme based on?"
header: "Color"
options:
  - label: "Blue (#4a9eff) (Recommended)"
    description: "Professional, calm, trustworthy"
  - label: "Green (#4ade80)"
    description: "Natural, growth, balance"
  - label: "Purple (#a855f7)"
    description: "Creative, unique, sophisticated"
  - label: "Orange (#f97316)"
    description: "Energetic, warm, enthusiastic"
```

If user selects "Other", ask in plain text: "What hex color code would you like? (e.g., #ff5733)"

Store in `.user/identity.yaml`:

```yaml
user:
  favorite_color: "[hex color]"
```

### 5.3 Generate Theme

**If custom theme:**
```bash
python3 .claude/skills/theme-management/scripts/generate_theme.py \
  --from-color "[favorite_color]" --name "personal" --save
```

**If default theme:**
```bash
python3 .claude/skills/theme-management/scripts/generate_theme.py midnight
```

---

## Phase 6: Finalization

After collecting all information, execute these steps:

### 6.1 Generate Personalized Files

Run the template injection script:

```bash
python ./.claude/scripts/inject_placeholders.py --verbose
```

This generates:
- `CLAUDE.md` from `CLAUDE.template.md`
- `.claude/rules/coaching.md` from `.claude/rules/coaching.template.md`

### 6.2 Configure Hooks

Run the hook configuration script:

```bash
python ./.claude/scripts/configure_hooks.py --verbose
```

This generates `.claude/settings.json` with appropriate hooks based on enabled integrations.

### 6.3 Create Initial Files

1. **Create company context files** in `/2-Areas/` for each company
2. **Create `/2-Areas/Personal/foundation.md`** with identity and values
3. **Optionally create person files** in `/6-People/` for key contacts

### 6.4 Mark Onboarding Complete

Update `.user/identity.yaml`:

```yaml
onboarding:
  complete: true
  completed_at: "[ISO timestamp]"
```

---

## Completion Message

After setup, tell them:

```markdown
## LifeOS is now personalized for you!

### Configuration Summary

**Identity**: [Name] ([Timezone])
**Companies**: [List of companies]
**Coaching**: Level [N] [Style Label]
**Integrations**: [List of enabled integrations]

### Files Created

- `.user/*.yaml` - Your configuration (preserved during upgrades)
- `CLAUDE.md` - Personalized from template
- `.claude/rules/coaching.md` - Personalized coaching
- `.claude/settings.json` - Hook configuration

### Next Steps

1. Run `/daily:plan` to start your first day
2. Check `0-System/guides/getting-started.md` for help
3. Use `/system:ask [question]` if you need guidance

### Changing Settings Later

- Edit files in `.user/` directly
- Run `/system:inject` to regenerate CLAUDE.md
- Run `/system:configure-hooks` to update hooks
```

---

## Error Handling

If any phase fails:
1. Log the error clearly
2. Offer to retry that phase
3. Allow skipping optional phases (Phases 2.5, 4)
4. Ensure partial progress is saved to `.user/` files

If scripts fail:
1. Check that `.user/` files are valid YAML
2. Check that template files exist
3. Provide manual instructions as fallback
