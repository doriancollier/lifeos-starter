---
name: context-switch
description: Help switch mental context between different companies and work areas. Use when transitioning from one company's work to another, or when needing to understand the current state of a specific work context.
allowed-tools: Read, Grep, Glob
---

# Context Switch Skill

Helps transition between different work contexts (companies/areas) by loading relevant information and state.

## Work Contexts

### {{company_1_name}}
- **Area folder**: `2-Areas/{{company_1_name}}/`
- **Key people**: Load from `contacts-config.json` → `companies.company_1.contacts`

### {{company_2_name}}
- **Area folder**: `2-Areas/{{company_2_name}}/`
- **Key people**: Load from `contacts-config.json` → `companies.company_2.contacts`

### {{company_3_name}}
- **Area folder**: `2-Areas/{{company_3_name}}/`
- **Key people**: {{partner_name}}

### Personal
- **Area folder**: `2-Areas/Personal/`
- **Key people**: {{partner_name}} (partner), {{child_name}} (child)
- **Focus areas**: Family, health/wellness, personal development

## Context Loading Process

When switching to a context:

### 1. Load Area Overview
```bash
ls "{{vault_path}}/2-Areas/[Company]/"
```

### 2. Check Active Projects
```bash
ls "{{vault_path}}/1-Projects/Current/" | grep -i "[company]"
```

### 3. Find Recent Activity
```bash
# Recent meetings
ls -la "{{vault_path}}/5-Meetings/2025/" | tail -5

# Recent mentions in daily notes
grep -r "[Company]" "{{vault_path}}/4-Daily/" --include="*.md" | tail -10
```

### 4. Check Open Tasks
```bash
grep -r "Company: [Company]" "{{vault_path}}/4-Daily/" --include="*.md" | grep "- \[ \]"
```

### 5. Review Key People
Read the relevant people files to refresh on relationships and open items.

## Context Summary Template

When loading a context, provide:

```markdown
## [Company] Context

### Current State
- **Active projects**: [list]
- **Open tasks**: [count and top priorities]
- **Recent meetings**: [last 2-3]

### Key People
- [Name]: [Role] - [Any urgent items]

### Today's Priorities
1. [Priority 1]
2. [Priority 2]

### Pending Decisions
- [Decision needed]

### Blockers
- [Any blocked items]
```

## Mental Model Differences

Each context has its own pace and communication style. Configure these during onboarding based on your specific work contexts.

### {{company_1_name}} Mode
- Configure during `/setup:onboard`

### {{company_2_name}} Mode
- Configure during `/setup:onboard`

### {{company_3_name}} Mode
- Configure during `/setup:onboard`

### Personal Mode
- Think: Family first, self-care, long-term growth
- Pace: Intentional, not rushed
- Focus: Presence and wellbeing

## Transition Checklist

When switching contexts:
- [ ] Save current context state (any notes or decisions)
- [ ] Review new context's open items
- [ ] Check for any urgent matters
- [ ] Adjust mental model for the context
- [ ] Identify the top 1-2 priorities
