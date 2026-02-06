---
description: Audit personal profile documents for completeness
argument-hint: "[category]"
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Personal Audit Command

Check which personal profile documents exist and their completeness.

## Arguments

- `$ARGUMENTS` — Optional category to audit: `professional`, `financial`, `health`, `emergency`, or `all` (default)

## Task

### Step 1: Check Document Existence

Check for each document in the personal profile registry:

**Identity Documents** (Core):
- `workspace/2-Areas/Personal/foundation.md`
- `workspace/2-Areas/Personal/biography.md`
- `workspace/2-Areas/Personal/context.md`
- `workspace/2-Areas/Personal/daily-practice.md`
- `workspace/2-Areas/Personal/Roles/` (check for at least one file)

**Professional Documents**:
- `workspace/2-Areas/Personal/resume.md`
- `workspace/2-Areas/Personal/work-history.md`
- `workspace/2-Areas/Personal/education.md`
- `workspace/2-Areas/Personal/skills.md`

**Financial Documents**:
- `workspace/2-Areas/Personal/assets-and-equity.md`
- `workspace/2-Areas/Personal/legal-entities.md`

**Health Documents**:
- `workspace/2-Areas/Personal/medical-history.md`

**Emergency Documents**:
- `workspace/2-Areas/Personal/emergency-contacts.md`
- `workspace/2-Areas/Personal/insurance-summary.md`

### Step 2: Check Document Quality

For each existing document, check:
1. Has valid frontmatter with `modified` date
2. Has content beyond just template placeholders
3. Key sections are populated (not just headers)

Rate each as:
- ✅ **Complete** — Document exists and is well-populated
- ⚠️ **Incomplete** — Document exists but needs work
- ❌ **Missing** — Document doesn't exist

### Step 3: Report Results

Present audit results in this format:

```markdown
## Personal Profile Audit

### Identity Documents
| Document | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| Foundation | ✅ | 2025-XX-XX | |
| Biography | ✅ | 2025-XX-XX | |
| Context | ✅ | 2025-XX-XX | |
| Daily Practice | ✅ | 2025-XX-XX | |
| Roles | ✅ | - | X role files |

### Professional Documents
| Document | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| Resume | ✅/⚠️/❌ | date | notes |
| Work History | ✅/⚠️/❌ | date | notes |
| Education | ✅/⚠️/❌ | date | notes |
| Skills | ✅/⚠️/❌ | date | notes |

### Financial Documents
| Document | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| Assets & Equity | ✅/⚠️/❌ | date | notes |
| Legal Entities | ✅/⚠️/❌ | date | notes |

### Health Documents
| Document | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| Medical History | ✅/⚠️/❌ | date | notes |

### Emergency Documents
| Document | Status | Last Modified | Notes |
|----------|--------|---------------|-------|
| Emergency Contacts | ✅/⚠️/❌ | date | notes |
| Insurance Summary | ✅/⚠️/❌ | date | notes |

---

### Summary
- **Complete**: X/14
- **Incomplete**: X/14
- **Missing**: X/14

### Recommendations
1. [Most important action]
2. [Next action]
3. [Next action]
```

### Step 4: Offer Actions

Based on findings, offer:

1. **If documents are missing**: "Would you like me to create any of the missing documents?"
2. **If documents are incomplete**: "Would you like to work on completing [document]?"
3. **If documents are stale** (modified > 6 months ago): "Some documents haven't been updated recently. Review them?"

## Output Format

The audit should be clear and actionable:
- Visual status indicators (✅/⚠️/❌)
- Last modified dates to show freshness
- Specific recommendations prioritized by importance
- Offer concrete next steps

## Category Filtering

If a category argument is provided, only audit that category:
- `professional` — Resume, Work History, Education, Skills
- `financial` — Assets & Equity, Legal Entities
- `health` — Medical History
- `emergency` — Emergency Contacts, Insurance Summary
- `all` — Everything (default)

## Related

- [Personal Documents Guide](workspace/0-System/guides/personal-documents.md)
- [Personal Profile Skill](/.claude/skills/personal-profile/SKILL.md)
