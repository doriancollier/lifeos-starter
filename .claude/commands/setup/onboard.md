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

## Phase 0: Dependencies (Automatic)

Before starting the wizard, ensure required Python packages are installed:

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/ensure_dependencies.py"
```

This installs PyYAML if missing. If installation fails (e.g., permissions), inform the user:
- "I need to install a Python package (pyyaml) for configuration. Please run: `pip3 install pyyaml`"
- Wait for confirmation before proceeding

---

## Phase 1: Identity (Required)

Use AskUserQuestion to gather:

1. **Full name**
2. **First name** (for casual references)
3. **Timezone** (provide common options like America/New_York, America/Chicago, America/Denver, America/Los_Angeles, Europe/London, etc.)
4. **Location** (city, state/country)
5. **Primary email address**
6. **Personality type** (optional - MBTI like INTJ, ENFP, or skip)

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

Ask about work contexts (companies, freelance, etc.). For each:
- **Name** - Full company/context name
- **Short ID** - 2-4 chars for folder/command naming (e.g., "ab", "acme")
- **Detection keywords** - Words in meeting titles that indicate this company (product names, project codenames, team names)
- **Role** - User's role at this company

### 2.2 Family Members

Ask about:
- **Partner name** (optional) - For relationship coaching
- **Children names** (optional) - For parenting coaching

### 2.3 Health Interest

Ask: "Do you want to track health data from Apple Health? (Requires Health Auto Export iOS app)"

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

## Phase 2.5: Key Contacts

For each company/work context, collect key contacts:

1. Ask: "Who are the key people you work with at [company]?"
2. For each person mentioned, collect:
   - **Full name**
   - **Role** (optional)
   - **Communication preference** (email, slack, sms, call)

3. Also collect external collaborators (people who span multiple companies)

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

Ask:

1. **Coaching intensity** (1-10 scale)
   - 1-3: Supportive - gentle reminders, celebrates progress
   - 4-6: Balanced - moderate accountability, suggests improvements
   - 7-8: Challenging - pushes limits, questions assumptions
   - 9-10: Relentless - maximum accountability, no excuses accepted

2. **Communication style preference** (direct, warm, balanced)

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

For each integration, explain what it does and ask if the user wants it enabled.

### 4.1 Google Calendar

"Google Calendar integration lets me check your schedule during planning and help manage events. This uses the MCP server (already configured if you followed setup)."

- If enabled: Ask for primary calendar email
- Write to `.user/calendars.yaml`

### 4.2 Apple Health

"Apple Health sync imports your health data (steps, sleep, activity rings) for coaching context. Requires the 'Health Auto Export' iOS app."

- If enabled: Ask for export path (default: `~/Library/Mobile Documents/com~apple~CloudDocs/Health Auto Export`)
- Write to `.user/health.yaml`

### 4.3 macOS Reminders

"Reminders sync creates a bidirectional link between your vault tasks and Apple Reminders, so you can manage tasks from your phone or via Siri."

- If enabled: No additional configuration needed

### 4.4 Email (Mail.app)

"Email reading lets me help triage and summarize emails from Mail.app."

- If enabled: No additional configuration needed

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

Ask about visual customization:

### 5.1 Favorite Color

Ask using AskUserQuestion:

```
question: "What's your favorite color? This can be used to personalize your theme."
header: "Color"
options:
  - label: "Blue (#4a9eff)"
    description: "Professional, calm, trustworthy"
  - label: "Green (#4ade80)"
    description: "Natural, growth, balance"
  - label: "Purple (#a855f7)"
    description: "Creative, unique, sophisticated"
  - label: "Orange (#f97316)"
    description: "Energetic, warm, enthusiastic"
```

If user selects "Other", accept a hex color code.

Store in `.user/identity.yaml`:

```yaml
user:
  favorite_color: "[hex color]"
```

### 5.2 Theme Generation

Ask:

```
question: "Would you like me to create a personalized theme based on your favorite color?"
header: "Theme"
options:
  - label: "Yes, create my theme (Recommended)"
    description: "Generate a custom theme from your color for VS Code and Obsidian"
  - label: "No, use the default midnight theme"
    description: "Use the built-in midnight theme (deep navy with blue accent)"
```

**If yes:**
1. Run the theme generator:
   ```bash
   python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" \
     --from-color "[favorite_color]" --name "personal" --save
   ```
2. This creates a "personal" theme saved to `.user/themes.yaml` and applies it

**If no:**
1. Apply the default midnight theme:
   ```bash
   python "$CLAUDE_PROJECT_DIR/.claude/skills/theme-management/scripts/generate_theme.py" midnight
   ```

---

## Phase 6: Finalization

After collecting all information, execute these steps:

### 6.1 Generate Personalized Files

Run the template injection script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/scripts/inject_placeholders.py" --verbose
```

This generates:
- `CLAUDE.md` from `CLAUDE.template.md`
- `.claude/rules/coaching.md` from `.claude/rules/coaching.template.md`

### 6.2 Configure Hooks

Run the hook configuration script:

```bash
python "$CLAUDE_PROJECT_DIR/.claude/scripts/configure_hooks.py" --verbose
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
