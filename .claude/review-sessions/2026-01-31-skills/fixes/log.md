# Fixes Applied

**Date**: 2026-01-31
**Session**: Skills Review

## Changes Made

### 1. Added YAML frontmatter to `writing-voice`

The skill was missing frontmatter entirely. Added:
```yaml
---
name: writing-voice
description: Write messages and documents in the vault owner's authentic voice...
---
```

### 2. Added `allowed-tools` declarations

Added explicit tool restrictions to 9 skills:

| Skill | Tools Added |
|-------|-------------|
| `context-switch` | Read, Grep, Glob |
| `goals-tracking` | Read, Write, Edit, Grep, Glob |
| `inbox-processor` | Read, Write, Glob, Bash |
| `personal-insight` | Read, Edit, Grep, Glob, AskUserQuestion |
| `planning-cadence` | Read, Grep, Glob |
| `pre-mortem` | Read, Write, Edit, Grep, Glob, AskUserQuestion |
| `product-management` | Read, Write, Edit, Grep, Glob |
| `weekly-aggregator` | Read, Write, Edit, Grep, Glob |
| `weekly-review` | Read, Grep, Glob |

## Not Changed

The following skills were flagged but already had `allowed-tools`:
- `birthday-awareness` - already has comprehensive tool list
- `historical-memory` - already has allowed-tools
- `person-file-management` - already has allowed-tools

## Deferred

The following suggestions were not addressed (low priority):
- `orchestration-patterns` activation triggers - description is adequate
- Template placeholders in `writing-voice` - these are intentional configuration prompts
- Adding more examples to complex skills
