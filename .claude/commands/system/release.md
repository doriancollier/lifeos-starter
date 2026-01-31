---
description: Create a new LifeOS release with version bump, changelog update, git tag, and optional GitHub Release
argument-hint: [patch|minor|major|X.Y.Z] [--dry-run]
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion, Task
---

# System Release Command (Orchestrator)

Create a new LifeOS release by bumping the version, updating the changelog, creating a git tag, and optionally publishing a GitHub Release.

This command operates as an **orchestrator** that:
- Runs quick pre-flight checks in main context
- Delegates context-heavy analysis to a subagent (keeps main context clean)
- Handles user interaction and git operations in main context

## Arguments

- `$ARGUMENTS` - Optional bump type or explicit version, plus optional flags:
  - *(no argument)* - **Auto-detect** version bump from changelog and commits
  - `patch` - Force patch version (0.5.0 → 0.5.1)
  - `minor` - Force minor version (0.5.0 → 0.6.0)
  - `major` - Force major version (0.5.0 → 1.0.0)
  - `X.Y.Z` - Explicit version number (e.g., `0.7.0`)
  - `--dry-run` - Show what would happen without making changes

## Semantic Versioning

| Bump Type | When to Use | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking changes to user config or workflows | 0.5.0 → 1.0.0 |
| **MINOR** | New features, backward compatible | 0.5.0 → 0.6.0 |
| **PATCH** | Bug fixes, documentation updates | 0.5.0 → 0.5.1 |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN CONTEXT (Orchestrator)              │
│                                                             │
│  Phase 1: Parse arguments                                   │
│  Phase 2: Pre-flight checks (git status, branch, VERSION)   │
│           ↓                                                 │
│  Phase 3: If auto-detect needed → spawn analysis agent      │
│           ↓                                                 │
│  Phase 4: Present recommendation, get user confirmation     │
│  Phase 5: Execute release (VERSION, changelog, git)         │
│  Phase 6: Report results                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼ (only if auto-detect)
┌─────────────────────────────────────────────────────────────┐
│              SUBAGENT: Release Analyzer                     │
│              (context-isolator, model: haiku)               │
│                                                             │
│  - Read changelog [Unreleased] section                      │
│  - Get commits since last tag                               │
│  - Analyze patterns (feat:, fix:, BREAKING, etc.)           │
│  - Return structured recommendation                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Parse Arguments

Parse `$ARGUMENTS` to determine:
- **Bump type**: `patch`, `minor`, `major`, explicit version, or **auto** (default)
- **Dry run**: Whether `--dry-run` flag is present

---

## Phase 2: Pre-flight Checks

Run these quick validation checks in main context:

```bash
# Check 1: Working directory is clean
git status --porcelain
```

If output is not empty, **STOP** and report:
```
## Cannot Release: Uncommitted Changes

You have uncommitted changes in the working directory:
[list files]

Please commit or stash your changes before releasing:
- `git add . && git commit -m "your message"`
- Or: `git stash`
```

```bash
# Check 2: On main branch
git branch --show-current
```

If not `main`, **STOP** and report:
```
## Cannot Release: Not on Main Branch

You are on branch `[branch]`. Releases must be created from `main`.

Switch to main: `git checkout main`
```

```bash
# Check 3: Read current version
cat VERSION
```

```bash
# Check 4: Get latest tag for comparison
git describe --tags --abbrev=0 2>/dev/null || echo "none"
```

```bash
# Check 5: Quick check that changelog has [Unreleased] content
# Extract [Unreleased] section and count entries
sed -n '/## \[Unreleased\]/,/## \[/p' 0-System/changelog.md | grep -c "^- " || echo "0"
```

If `[Unreleased]` section appears empty (0 entries):

1. **Check for commits since last tag**:
   ```bash
   git log $(git describe --tags --abbrev=0 2>/dev/null || echo "")..HEAD --oneline | wc -l
   ```

2. **If commits exist but changelog is empty**, report:
   ```
   ## Warning: Changelog Empty but Commits Exist

   The [Unreleased] section has no entries, but there are [N] commits since the last release.

   This may indicate:
   - Commits did not use conventional commit format (feat:, fix:, etc.)
   - The changelog-populator git hook is not installed

   **Options:**
   1. Install the git hook: `.claude/scripts/install-git-hooks.sh`
   2. Manually add entries to `0-System/changelog.md`
   3. Let me draft entries from commit messages (proceed to analysis)
   ```

   Use AskUserQuestion:
   ```
   header: "Empty Changelog"
   question: "No changelog entries found. How would you like to proceed?"
   options:
     - label: "Draft entries from commits (Recommended)"
       description: "I'll analyze commits and draft changelog entries for your review"
     - label: "Cancel and add entries manually"
       description: "Exit so you can populate [Unreleased] yourself"
     - label: "Proceed anyway (empty release)"
       description: "Create release with empty changelog (not recommended)"
   ```

   If user selects "Draft entries from commits":
   - Run the analysis agent (Phase 3) with additional instruction to draft entries
   - Present drafted entries for user approval before proceeding
   - If approved, update the changelog before continuing

3. **If no commits exist**, **STOP** and report:
   ```
   ## Cannot Release: No Changes

   Both the [Unreleased] section and commit history are empty since the last release.
   There's nothing to release.
   ```

---

## Phase 3: Version Analysis

### If explicit bump type provided (patch/minor/major/X.Y.Z)

Skip analysis, calculate next version directly:

| Current | Bump Type | Next |
|---------|-----------|------|
| 0.5.0 | patch | 0.5.1 |
| 0.5.0 | minor | 0.6.0 |
| 0.5.0 | major | 1.0.0 |

Proceed to Phase 4.

### If auto-detect needed (no bump type)

**Spawn a context-isolator agent** to analyze changes and recommend version bump.

This keeps the main context clean by offloading the changelog parsing and commit analysis.

```
Task tool:
  subagent_type: context-isolator
  model: haiku
  description: "Analyze changes for release"
  prompt: |
    ## Release Analysis Task

    Analyze the changes since the last release and recommend a version bump.

    **Current version:** [from VERSION file]
    **Last tag:** [from git describe]

    ### Step 1: Read Changelog

    Read the [Unreleased] section from `0-System/changelog.md`:
    - Extract content between `## [Unreleased]` and the next `## [` heading
    - Note which sections have content: Added, Changed, Fixed, Removed, Deprecated

    ### Step 2: Get Commits

    Run: `git log [last_tag]..HEAD --oneline`
    - Count commits by type (feat:, fix:, docs:, chore:, etc.)
    - Look for BREAKING CHANGE or ! markers

    ### Step 3: Apply Detection Rules

    **MAJOR signals (any of these):**
    - Changelog contains "BREAKING" or "Breaking"
    - "### Removed" section has content
    - Commits contain "BREAKING CHANGE:" or "!" after type (e.g., "feat!:")

    **MINOR signals (any of these):**
    - "### Added" section has content
    - Commits contain "feat:" or "feat("

    **PATCH (default):**
    - Only "### Fixed" or "### Changed" with minor changes
    - Only "fix:", "docs:", "chore:" commits

    ### Step 4: Return Structured Result

    Return your analysis in this EXACT format:

    ```
    RECOMMENDED_BUMP: [MAJOR|MINOR|PATCH]
    NEXT_VERSION: [X.Y.Z]

    CHANGELOG_SIGNALS:
    - Added: [count] items
    - Changed: [count] items
    - Fixed: [count] items
    - Removed: [count] items
    - Breaking: [yes/no]

    COMMIT_SIGNALS:
    - Total commits: [N]
    - feat: [count]
    - fix: [count]
    - docs: [count]
    - other: [count]
    - Breaking markers: [yes/no]

    REASONING:
    [1-2 sentence explanation of why this bump type]

    CHANGELOG_CONTENT:
    [The full [Unreleased] section content for display]
    ```
```

**Parse the agent's response** to extract:
- `RECOMMENDED_BUMP`
- `NEXT_VERSION`
- Signals for display
- Reasoning
- Changelog content

---

## Phase 4: Present and Confirm

Present the release plan to the user:

```markdown
## Release Preview

**Current Version**: v0.5.0
**New Version**: v0.6.0
**Bump Type**: MINOR (auto-detected)

### Reasoning

[Agent's reasoning from Phase 3]

### Analysis Summary

**Changelog signals:**
- ✓ "### Added" section has 3 items
- ✗ No breaking changes detected
- ✓ "### Fixed" section has 2 items

**Commit signals (12 commits):**
- 4 feat: commits
- 6 fix: commits
- 2 docs: commits

### Changes to be Released

[Changelog content from agent]

### Files to be Modified

1. `VERSION` — 0.5.0 → 0.6.0
2. `0-System/changelog.md` — [Unreleased] → [0.6.0] - YYYY-MM-DD

### Git Operations

1. Commit: "Release v0.6.0"
2. Tag: v0.6.0 (annotated)
3. Push: origin main + tag
```

If `--dry-run` flag is present, **STOP** here.

Otherwise, use AskUserQuestion:
```
header: "Confirm Release"
question: "Create release v0.6.0?"
options:
  - label: "Yes, MINOR is correct (Recommended)"
    description: "New features added, backward compatible"
  - label: "No, make it PATCH"
    description: "These are just bug fixes (0.5.0 → 0.5.1)"
  - label: "No, make it MAJOR"
    description: "There are breaking changes (0.5.0 → 1.0.0)"
  - label: "Cancel"
    description: "Abort without making changes"
```

If user overrides the bump type, recalculate version.

---

## Phase 5: Execute Release

### 5.1: Check tag doesn't exist

```bash
git tag -l "v0.6.0"
```

If tag exists, **STOP**:
```
## Cannot Release: Tag Already Exists

Tag v0.6.0 already exists. Choose a different version or delete:
- `git tag -d v0.6.0 && git push origin :refs/tags/v0.6.0`
```

### 5.2: Update VERSION File

```bash
echo "0.6.0" > VERSION
```

### 5.3: Update Changelog

Edit `0-System/changelog.md` using the Edit tool:

1. Replace the `## [Unreleased]` section with a fresh empty one
2. Insert the new version section with today's date
3. Move all previous [Unreleased] content under the new version

**Target structure:**
```markdown
## [Unreleased]

### Added

### Changed

### Fixed

---

## [0.6.0] - 2026-01-31

[Previous [Unreleased] content here]
```

### 5.4: Commit and Tag

```bash
# Stage changes
git add VERSION 0-System/changelog.md

# Commit (use HEREDOC for message)
git commit -m "$(cat <<'EOF'
Release v0.6.0

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Create annotated tag
git tag -a v0.6.0 -m "Version 0.6.0"
```

### 5.5: Push to Origin

```bash
# Push commit and tag
git push origin main && git push origin v0.6.0
```

If push fails, report error and provide recovery commands.

### 5.6: Optional GitHub Release

Ask using AskUserQuestion:
```
header: "GitHub Release"
question: "Create a GitHub Release?"
options:
  - label: "Yes, create GitHub Release (Recommended)"
    description: "Creates a release on GitHub with the changelog as notes"
  - label: "No, skip"
    description: "Tag is pushed, but no GitHub Release created"
```

If yes and `gh` is available:
```bash
gh release create v0.6.0 --title "v0.6.0" --notes "[changelog content]"
```

---

## Phase 6: Report

```markdown
## Release Complete

**Version**: v0.6.0
**Tag**: v0.6.0
**Commit**: [short sha from `git rev-parse --short HEAD`]

### Links

- Tag: https://github.com/[owner]/[repo]/releases/tag/v0.6.0
- Compare: https://github.com/[owner]/[repo]/compare/v0.5.0...v0.6.0

### What's Next

- Users will see update notification on next session start
- They can upgrade with `/system:upgrade`

### Release Notes

[Summary of what was released]
```

---

## Edge Cases

### Push Fails

```
## Push Failed

The commit and tag were created locally but could not be pushed.
Error: [error message]

To retry:
- `git push origin main`
- `git push origin v0.6.0`

To undo local changes:
- `git reset --hard HEAD~1`
- `git tag -d v0.6.0`
```

### No GitHub CLI

```
## GitHub CLI Not Available

Install GitHub CLI to create releases:
- macOS: `brew install gh`
- Then: `gh auth login`

Or create the release manually at:
https://github.com/[owner]/[repo]/releases/new?tag=v0.6.0
```

---

## Related Commands

- `/system:upgrade` - Consumer side: apply updates from upstream
- `/system:inject` - Regenerate templated files
- `/system:configure-hooks` - Regenerate hook configuration

## When to Use

- After completing a set of features (minor release)
- After fixing bugs (patch release)
- Before breaking changes (major release)
- At natural milestones (sprint end, before sharing)

**Do NOT release on every commit** - releases represent meaningful milestones.
