---
title: "Personal Documents"
created: "2025-12-29"
status: "active"
---

# Personal Documents

This guide defines the canonical document types for the vault owner's personal profile. A complete personal profile enables Claude to help with professional opportunities, financial planning, health management, and emergency preparedness.

## Overview

Personal documents live in `2-Areas/Personal/` and fall into five categories:

| Category | Purpose | Documents |
|----------|---------|-----------|
| **Identity** | Who you are | foundation, biography, context, daily-practice, roles |
| **Professional** | Your career | resume, work-history, education, skills |
| **Financial** | Your assets | assets-and-equity, legal-entities |
| **Health** | Your wellbeing | medical-history |
| **Emergency** | Your safety net | emergency-contacts, insurance-summary |

## Document Types

### Identity Documents (Who You Are)

These documents define your identity, values, and life narrative.

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| Foundation | `foundation.md` | Mission, vision, principles, commandments | Core |
| Biography | `biography.md` | Life narrative by chapters | Core |
| Context | `context.md` | Current life context, family, healthcare | Core |
| Daily Practice | `daily-practice.md` | Daily affirmation script | Core |
| Roles | `Roles/*.md` | Role-based identity documents | Core |

**Template**: N/A (these are unique documents)

---

### Professional Documents (Your Career)

These documents capture your professional history and capabilities.

| Document | Path | Purpose |
|----------|------|---------|
| Resume | `resume.md` | Professional summary for opportunities |
| Work History | `work-history.md` | Detailed role breakdowns with accomplishments |
| Education | `education.md` | Schools, degrees, certifications, self-directed learning |
| Skills | `skills.md` | Technical and soft skills inventory |

**Templates**: `3-Resources/Templates/personal/`

#### Resume (`resume.md`)

A concise professional summary suitable for sharing with potential employers, partners, or collaborators.

**Key sections**:
- Professional summary (2-3 sentences)
- Current roles
- Career highlights
- Core competencies
- Contact information

**When to update**: After significant role changes, major accomplishments, or annually.

#### Work History (`work-history.md`)

Detailed breakdown of each professional role with accomplishments, lessons learned, and context.

**Key sections**:
- Role entries with dates, title, company
- Key accomplishments per role
- Technologies/skills used
- Lessons learned
- Reason for leaving

**When to update**: After leaving a role or achieving significant milestones.

#### Education (`education.md`)

Formal and self-directed learning history.

**Key sections**:
- Formal education (schools, degrees, dates)
- Certifications and credentials
- Self-directed learning (courses, books, podcasts)
- Skills in development

**When to update**: After completing courses, certifications, or significant learning milestones.

#### Skills (`skills.md`)

Comprehensive inventory of technical and soft skills.

**Key sections**:
- Technical skills by category (languages, tools, platforms)
- Product/business skills
- Soft skills
- Skills in development
- Skills to acquire

**When to update**: After gaining proficiency in new skills or during annual review.

---

### Financial Documents (Your Assets)

These documents track ownership, equity, and business structures.

| Document | Path | Purpose |
|----------|------|---------|
| Assets & Equity | `assets-and-equity.md` | Ownership stakes, investments, income streams |
| Legal Entities | `legal-entities.md` | LLCs, corporations, business structures |

**Templates**: `3-Resources/Templates/personal/`

#### Assets & Equity (`assets-and-equity.md`)

Consolidated view of ownership and financial position.

**Key sections**:
- Equity stakes (company, percentage, vesting, valuation)
- Real property
- Investment accounts
- Income streams
- Liabilities

**When to update**: After equity changes, property transactions, or quarterly review.

**Privacy note**: This document may contain sensitive financial information. Consider what level of detail is appropriate.

#### Legal Entities (`legal-entities.md`)

Business structures and their status.

**Key sections**:
- Active entities (name, type, state, purpose)
- Dormant/dissolved entities
- Registered agent information
- Annual filing requirements

**When to update**: After forming, dissolving, or changing entity status.

---

### Health Documents (Your Wellbeing)

These documents track medical history for continuity of care.

| Document | Path | Purpose |
|----------|------|---------|
| Medical History | `medical-history.md` | Personal health records |

**Templates**: `3-Resources/Templates/personal/`

#### Medical History (`medical-history.md`)

Personal health timeline and current status.

**Key sections**:
- Major health events (surgeries, diagnoses, hospitalizations)
- Current medications
- Allergies
- Current providers
- Preventive care schedule
- Family health history (relevant conditions)

**When to update**: After medical events, medication changes, or provider changes.

**Privacy note**: This document contains protected health information. Store appropriately.

---

### Emergency Documents (Your Safety Net)

These documents ensure preparedness for emergencies.

| Document | Path | Purpose |
|----------|------|---------|
| Emergency Contacts | `emergency-contacts.md` | POA, emergency info, key contacts |
| Insurance Summary | `insurance-summary.md` | Policy details across all insurance types |

**Templates**: `3-Resources/Templates/personal/`

#### Emergency Contacts (`emergency-contacts.md`)

Critical information for emergencies.

**Key sections**:
- Emergency contacts (name, relationship, phone, priority)
- Medical power of attorney
- Financial power of attorney
- Digital executor / account access
- Important document locations
- Emergency procedures

**When to update**: After relationship changes, POA updates, or annually.

#### Insurance Summary (`insurance-summary.md`)

Consolidated insurance policy information.

**Key sections**:
- Health insurance (policy, group, member ID, coverage)
- Life insurance
- Auto insurance
- Property/renters insurance
- Umbrella/liability
- Policy renewal dates

**When to update**: After policy changes or annually at renewal.

---

## Completeness Audit

Use `/personal:audit` to check which documents exist and their completeness.

### Minimum Viable Profile

At minimum, a complete personal profile should include:

**Required (Core)**:
- [ ] Foundation (`foundation.md`)
- [ ] Biography (`biography.md`)
- [ ] Context (`context.md`)

**Recommended (Professional)**:
- [ ] Resume (`resume.md`)
- [ ] Skills (`skills.md`)

**Recommended (Emergency)**:
- [ ] Emergency Contacts (`emergency-contacts.md`)
- [ ] Insurance Summary (`insurance-summary.md`)

**Optional but Valuable**:
- [ ] Work History (`work-history.md`)
- [ ] Education (`education.md`)
- [ ] Assets & Equity (`assets-and-equity.md`)
- [ ] Legal Entities (`legal-entities.md`)
- [ ] Medical History (`medical-history.md`)

---

## Integration

### With `personal-profile` Skill

The `personal-profile` skill helps Claude:
- Know what documents should exist
- Audit document completeness
- Create missing documents from templates
- Update documents when relevant information surfaces
- Route information to the correct document

### With `personal-insight` Skill

The `personal-insight` skill updates the "About Me" section in `context.md`. The two skills complement each other:
- `personal-insight`: Captures self-knowledge (patterns, strengths, weaknesses)
- `personal-profile`: Manages document structure and completeness

### With Annual Planning

During annual planning (`2-Areas/Personal/Years/`), review personal documents for:
- Accuracy of current information
- Completeness of historical records
- Updates needed based on year's changes

---

## Creating New Documents

When creating a new personal document:

1. **Use the template**: Copy from `3-Resources/Templates/personal/[type]-template.md`
2. **Place correctly**: Save to `2-Areas/Personal/[name].md`
3. **Fill core sections**: Populate required sections first
4. **Add to context**: Update `context.md` if the document adds family/healthcare info
5. **Link appropriately**: Cross-reference from related documents

---

## Best Practices

1. **Keep documents current** — Stale information is worse than no information
2. **Be honest** — These are for your benefit, not external presentation
3. **Balance detail and maintainability** — Too much detail becomes hard to update
4. **Protect sensitive info** — Consider privacy for financial and health data
5. **Review annually** — Use annual planning to audit and update

---

## Related

- [Personal Insight Skill](/.claude/skills/personal-insight/SKILL.md) — Capturing self-knowledge
- [Personal Profile Skill](/.claude/skills/personal-profile/SKILL.md) — Document management
- [Personal Audit Command](/.claude/commands/personal/audit.md) — Completeness check
- [Templates](../components/templates.md) — Template documentation
