---
name: personal-profile
description: Manage the vault owner's personal profile documents. Use when the user asks about their resume, work history, skills, medical info, or other personal documents. Also activates when relevant information surfaces that should be captured in personal documents.
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

# Personal Profile Skill

Manages the vault owner's personal profile documents—the comprehensive set of documents that capture who {{user_first_name}} is professionally, financially, medically, and for emergency preparedness.

## When to Use

This skill activates when:

1. **User asks about personal documents**: "What's in my resume?", "Do I have my medical history documented?"
2. **User needs a document created**: "I need to update my resume", "Create my work history"
3. **Information surfaces that belongs in a personal document**: Career updates, equity changes, medical events, new skills
4. **Audit is requested**: "What personal documents am I missing?", `/personal:audit`
5. **During annual planning**: Review and update personal documents for accuracy

## Document Registry

### Identity Documents (Core - Already Exist)

| Document | Path | Purpose |
|----------|------|---------|
| Foundation | `workspace/2-Areas/Personal/foundation.md` | Mission, vision, principles |
| Biography | `workspace/2-Areas/Personal/biography.md` | Life narrative |
| Context | `workspace/2-Areas/Personal/context.md` | Current life context |
| Daily Practice | `workspace/2-Areas/Personal/daily-practice.md` | Daily affirmations |
| Roles | `workspace/2-Areas/Personal/Roles/*.md` | Role-based identity |

### Professional Documents

| Document | Path | Template |
|----------|------|----------|
| Resume | `workspace/2-Areas/Personal/resume.md` | `workspace/3-Resources/Templates/personal/resume-template.md` |
| Work History | `workspace/2-Areas/Personal/work-history.md` | `workspace/3-Resources/Templates/personal/work-history-template.md` |
| Education | `workspace/2-Areas/Personal/education.md` | `workspace/3-Resources/Templates/personal/education-template.md` |
| Skills | `workspace/2-Areas/Personal/skills.md` | `workspace/3-Resources/Templates/personal/skills-template.md` |

### Financial Documents

| Document | Path | Template |
|----------|------|----------|
| Assets & Equity | `workspace/2-Areas/Personal/assets-and-equity.md` | `workspace/3-Resources/Templates/personal/assets-template.md` |
| Legal Entities | `workspace/2-Areas/Personal/legal-entities.md` | `workspace/3-Resources/Templates/personal/legal-entities-template.md` |

### Health Documents

| Document | Path | Template |
|----------|------|----------|
| Medical History | `workspace/2-Areas/Personal/medical-history.md` | `workspace/3-Resources/Templates/personal/medical-history-template.md` |

### Emergency Documents

| Document | Path | Template |
|----------|------|----------|
| Emergency Contacts | `workspace/2-Areas/Personal/emergency-contacts.md` | `workspace/3-Resources/Templates/personal/emergency-contacts-template.md` |
| Insurance Summary | `workspace/2-Areas/Personal/insurance-summary.md` | `workspace/3-Resources/Templates/personal/insurance-template.md` |

## Behaviors

### Detecting Information for Personal Documents

When conversation reveals information that belongs in a personal document:

**AUTO-UPDATE (proceed without asking)**:
- New job or role change → Update resume.md and work-history.md
- Equity change (grant, vest, exit) → Update assets-and-equity.md
- Major medical event → Update medical-history.md
- New certification or degree → Update education.md
- Insurance policy change → Update insurance-summary.md
- New business entity → Update legal-entities.md

**ASK FIRST**:
- New skill claimed → "Should I add {{skill}} to your skills inventory?"
- Emergency contact change → "Should I update your emergency contacts?"
- Career accomplishment → "This seems significant. Add to work history?"

**DON'T UPDATE**:
- Trivial mentions of work activities
- Passing references to health (not events)
- Speculation about future changes

### Creating Missing Documents

When a document doesn't exist and is needed:

1. Read the appropriate template from `workspace/3-Resources/Templates/personal/`
2. Pre-fill with known information from other sources:
   - `biography.md` for career/education history
   - `context.md` for healthcare/insurance info
   - Person files for emergency contacts
3. Create the document in `workspace/2-Areas/Personal/`
4. Notify user: "Created {{document}}. Please review and complete the sections I couldn't fill."

### Auditing Documents

When running an audit (via `/personal:audit` or user request):

1. Check existence of each document in the registry
2. For existing documents, check for completeness signals:
   - Has frontmatter with `modified` date
   - Has content beyond template placeholders
   - Key sections are populated
3. Report status for each category
4. Offer to create missing documents

### Updating Documents

When updating an existing document:

1. Read the current document
2. Find the appropriate section for the new information
3. Add the information with context
4. Update the `modified` date in frontmatter
5. Confirm: "Updated {{document}} with {{summary}}"

## Integration Points

### With `personal-insight` Skill

`personal-insight` manages the "About Me" section in `context.md` (self-knowledge: patterns, strengths, weaknesses).

`personal-profile` manages structured documents (resume, work history, etc.).

These complement each other:
- `personal-insight` → Who you are internally
- `personal-profile` → Who you are externally/practically

### With `/update` Command

When `/update` contains personal profile information, route to appropriate document:
- Career update → work-history.md, resume.md
- Health update → medical-history.md
- Financial update → assets-and-equity.md

### With Annual Planning

During annual planning (`/goals:review`, year file creation):
- Prompt review of personal documents
- Suggest updates based on year's accomplishments
- Ensure documents reflect current state

## Examples

### Example 1: User Asks About Resume

**User**: "What's in my resume?"

**Action**:
1. Read `workspace/2-Areas/Personal/resume.md`
2. Summarize contents
3. Offer: "Would you like to update anything?"

### Example 2: Career Information Surfaces

**User**: "I just accepted a new consulting role at Company X"

**Action**:
1. Recognize career update
2. Update resume.md with new role
3. Update work-history.md with role entry
4. Confirm: "Updated your resume and work history with the new role at Company X"

### Example 3: Document Missing

**User**: "Can you add my new skill in Blender to my profile?"

**Action**:
1. Check for skills.md
2. If missing: "You don't have a skills inventory yet. Want me to create one?"
3. If exists: Add Blender with proficiency level

### Example 4: Audit Request

**User**: "/personal:audit"

**Action**:
1. Check each document in registry
2. Report:
   ```
   Personal Profile Audit

   ✅ Identity Documents (5/5)
   ✅ Professional Documents (4/4)
   ⚠️ Financial Documents (1/2) - Missing: legal-entities.md
   ✅ Health Documents (1/1)
   ⚠️ Emergency Documents (1/2) - Missing: emergency-contacts.md

   Would you like me to create the missing documents?
   ```

## Guardrails

- **Don't overwrite user content** — Add to documents, don't replace
- **Respect privacy** — Financial and health docs are sensitive
- **Keep documents maintainable** — Don't add excessive detail
- **Update timestamps** — Always update `modified` in frontmatter
- **Cross-reference** — Link between related documents

## Full Guide

See `workspace/0-System/guides/personal-documents.md` for complete documentation of the personal document system.
