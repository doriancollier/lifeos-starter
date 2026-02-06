# Upgrade Notes

AI-readable instructions for helping users upgrade between versions.

## Purpose

These notes complement migrations (automated code changes) by providing:
- User action items that can't be automated
- Explanations of what changed and why
- Verification steps
- Feature highlights to explore

## How Notes Are Used

During `/system:upgrade`, the AI:
1. Parses all upgrade notes between the old and new version
2. Creates a **TaskList** from "User Action Required" items
3. Guides the user through each task interactively
4. Runs verification steps to confirm success
5. Uses "Notes for AI" for context-aware assistance

**The "User Action Required" section is critical** - each checkbox becomes a tracked task.

## Format

Each file is named after the version being upgraded TO: `v0.11.0.md`

### Template

```markdown
# Upgrade Notes: v0.X.0

## Summary
[One sentence describing the main theme of this upgrade]

## User Action Required
[Things the user must do manually after upgrade - EACH BECOMES A TRACKED TASK]

- [ ] Action item with specific instructions (e.g., "Re-open Obsidian pointing to `workspace/` folder")
- [ ] Another actionable step (e.g., "Run `/daily:plan` to verify daily notes work")

**Guidelines for action items:**
- Be specific and actionable (not "check the system")
- Include the exact command, path, or UI action needed
- Order by dependency (do X before Y if Y depends on X)
- Each item should be independently verifiable

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
