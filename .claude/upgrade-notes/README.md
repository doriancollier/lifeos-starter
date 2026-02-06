# Upgrade Notes

AI-readable instructions for helping users upgrade between versions.

## Purpose

These notes complement migrations (automated code changes) by providing:
- User action items that can't be automated
- Explanations of what changed and why
- Verification steps
- Feature highlights to explore

## Format

Each file is named after the version being upgraded TO: `v0.11.0.md`

### Template

```markdown
# Upgrade Notes: v0.X.0

## Summary
[One sentence describing the main theme of this upgrade]

## User Action Required
[Things the user must do manually after upgrade]

- [ ] Action item 1
- [ ] Action item 2

## Breaking Changes
[Changes that might affect existing workflows]

- **Old behavior**: X
- **New behavior**: Y
- **Migration**: [How to adapt]

## New Features to Explore
[Features the AI should highlight and offer to demonstrate]

- **Feature Name** - Brief description. Try: `/command`

## Configuration Changes
[Any .user/ or other config changes needed]

## Verification
[Steps to confirm the upgrade worked correctly]

## Notes for AI
[Internal guidance for Claude - not shown to user directly]
- When user runs /daily:plan, remind them about X
- If user asks about Y, point to new Z feature
```

## When Notes Are Empty

Not every release needs upgrade notes. Skip for:
- Pure bug fixes with no user-facing changes
- Documentation-only updates
- Internal refactoring
