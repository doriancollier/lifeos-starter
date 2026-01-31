---
description: Audit existing Claude Code skills for quality and completeness
argument-hint: [skill-name or "all"]
allowed-tools: Read, Glob, Grep
---

# Audit Skills Command

Review Claude Code skills for quality, completeness, and best practices.

## Arguments

- `$ARGUMENTS` - Optional skill name to audit, or "all" for complete audit

## Context

- **Skills directory**: `.claude/skills/`
- **Skill manager skill**: `.claude/skills/skill-manager/SKILL.md`

## Task

Use the skill-manager skill to perform skill audits.

### 1. Identify Skills to Audit

If argument is "all" or not provided:
- List all skills in `.claude/skills/`
- Audit each one

If argument is a skill name:
- Audit only that skill

### 2. For Each Skill, Check:

**Structure**
- [ ] Has SKILL.md file
- [ ] Name in frontmatter matches directory name
- [ ] SKILL.md is < 500 lines (or has progressive disclosure)

**Description Quality**
- [ ] Description exists and is < 1024 chars
- [ ] Description includes capability verbs
- [ ] Description includes domain keywords
- [ ] Description includes "Use when..." triggers

**Content Quality**
- [ ] Has "When to Use" section
- [ ] Has concrete examples
- [ ] Has integration notes (if applicable)
- [ ] Vault paths are current and accurate

**Best Practices**
- [ ] No duplicate functionality with other skills
- [ ] Uses allowed-tools appropriately (if restricted)
- [ ] Multi-file skills have proper linking

### 3. Generate Report

For each skill, output:
```
## [skill-name]

**Status**: [Good / Needs Attention / Critical Issues]

**Checks Passed**: X/Y

**Issues Found**:
- Issue 1: [Description] → [Suggestion]
- Issue 2: [Description] → [Suggestion]

**Recommendations**:
- [Specific improvement suggestion]
```

### 4. Summary

After all skills:
```
## Summary

**Total Skills**: X
**Good**: Y
**Needs Attention**: Z
**Critical**: W

**Top Issues Across Skills**:
1. [Most common issue]
2. [Second most common]
3. [Third most common]

**Recommended Actions**:
1. [Highest priority fix]
2. [Second priority]
```

## Output

- Audit report for each skill
- Summary with actionable recommendations
- Offer to fix critical issues if found
