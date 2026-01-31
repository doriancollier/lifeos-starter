---
description: Review processes for clarity, consistency, and improvements
argument-hint: [area to review (optional)]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# System Review Command

Review Claude Code processes (commands, skills, hooks, agents, templates, configuration) for clarity, consistency, and potential improvements.

## Arguments

- `$ARGUMENTS` - Optional area to focus on. If empty, review everything.
  - Valid areas: `commands`, `skills`, `hooks`, `agents`, `templates`, `config`, `memory` (CLAUDE.md), `guides` (0-System), `docs` (0-System)
  - Can also specify a specific file or pattern: `daily commands`, `task-system skill`

## Review Scope

### Files and Directories to Review

| Area | Location | What to Check |
|------|----------|---------------|
| **Product Docs** | `/0-System/` | Accuracy, completeness, sync with CLAUDE.md |
| **Guides** | `/0-System/guides/*.md` | Workflow accuracy, user-friendliness |
| **Components** | `/0-System/components/*.md` | Up-to-date with actual implementation |
| **Memory/Instructions** | `/CLAUDE.md` | Main instructions, accuracy, completeness |
| **Commands** | `/.claude/commands/**/*.md` | Clarity, consistency, functionality |
| **Skills** | `/.claude/skills/**/SKILL.md` | Accuracy, usefulness, overlap |
| **Agents** | `/.claude/agents/*.md` | Purpose clarity, tool access, instructions |
| **Hooks** | `/.claude/hooks/*.py`, `*.sh` | Functionality, error handling, documentation |
| **Templates** | `/3-Resources/Templates/*.md` | Completeness, frontmatter, consistency |
| **Obsidian Config** | `/.obsidian/` | Plugin settings, hotkeys, community plugins |
| **Directory Structure** | `/1-Projects/`, `/2-Areas/`, etc. | Organization, naming conventions |

## Order of Operations

Execute these steps sequentially. This is an **interactive review** - ask questions and wait for responses.

### Phase 1: Discovery & Inventory

- [ ] **1.1** Determine scope from `$ARGUMENTS`
  - If empty → review everything
  - If specified → focus on that area + its connections

- [ ] **1.2** Build inventory of files to review:
  ```bash
  # Product Documentation (0-System)
  find "/0-System" -name "*.md" -type f

  # Commands
  find "/.claude/commands" -name "*.md" -type f

  # Skills
  find "/.claude/skills" -name "SKILL.md" -type f

  # Agents
  find "/.claude/agents" -name "*.md" -type f

  # Hooks
  find "/.claude/hooks" -type f \( -name "*.py" -o -name "*.sh" \)

  # Templates
  find "/3-Resources/Templates" -name "*.md" -type f

  # Memory files
  ls -la "/CLAUDE.md"
  ```

- [ ] **1.3** Report inventory to user:
  ```
  Found X commands, Y skills, Z hooks, W agents, V templates to review.
  ```

### Phase 2: Read & Analyze

- [ ] **2.1** Read CLAUDE.md first (it's the source of truth)
  - Note all documented processes
  - Note all referenced commands/skills/hooks
  - Build a mental model of how things should work

- [ ] **2.2** Read each file in scope, checking for:

**Clarity Issues:**
- Ambiguous instructions
- Missing context
- Unclear when to use
- Missing examples

**Consistency Issues:**
- Conflicting instructions between files
- Different terminology for same concepts
- Inconsistent formatting
- Mismatched YAML frontmatter

**Functionality Issues:**
- Broken file paths
- Outdated references
- Missing dependencies
- Logic errors in hooks

**Completeness Issues:**
- Missing documentation
- Incomplete instructions
- Missing edge case handling

- [ ] **2.3** Check cross-references:
  - Does CLAUDE.md accurately list all commands/skills/hooks?
  - Do commands reference skills that exist?
  - Do hooks validate things that are documented?

### Phase 3: Identify Issues

- [ ] **3.1** Categorize findings:

| Severity | Meaning | Action |
|----------|---------|--------|
| **Critical** | Broken functionality, blocking errors | Must fix |
| **Warning** | Inconsistency, confusion risk | Should fix |
| **Suggestion** | Improvement opportunity | Optional |

- [ ] **3.2** For each issue, determine:
  - Can it be fixed automatically?
  - Is there an obvious correct answer?
  - Does it require user input?

### Phase 4: Present Findings

- [ ] **4.1** Present summary to user:
  ```markdown
  ## Process Review Summary

  **Scope**: [what was reviewed]
  **Files Reviewed**: X

  ### Critical Issues (must fix)
  - [ ] [Issue description] in `file.md`

  ### Warnings (should fix)
  - [ ] [Issue description] in `file.md`

  ### Suggestions (optional improvements)
  - [ ] [Improvement idea]
  ```

- [ ] **4.2** For issues requiring decisions, use AskUserQuestion:
  - Present the conflict/ambiguity
  - Offer clear options
  - Include a recommendation when possible

### Phase 5: Apply Fixes

- [ ] **5.1** Group proposed changes by file

- [ ] **5.2** Present batch of changes:
  ```markdown
  ## Proposed Changes

  ### File: `.claude/commands/daily/note.md`
  - Change 1: [description]
  - Change 2: [description]

  ### File: `CLAUDE.md`
  - Change 1: [description]

  **Proceed with these X changes?**
  ```

- [ ] **5.3** Wait for user confirmation before making changes

- [ ] **5.4** Apply approved changes using Edit tool

- [ ] **5.5** Report completion:
  ```markdown
  ## Changes Applied

  - [x] Updated `file1.md`: [what changed]
  - [x] Updated `file2.md`: [what changed]

  ## Remaining Items
  - [ ] [Any deferred items]
  ```

### Phase 6: Recommendations

- [ ] **6.1** Present improvement opportunities:
  ```markdown
  ## Improvement Recommendations

  ### High Value
  1. **[Recommendation]**: [Why and how]

  ### Nice to Have
  1. **[Recommendation]**: [Why and how]
  ```

- [ ] **6.2** Ask user which (if any) to implement now

## Review Checklists

### For Commands
- [ ] Has valid YAML frontmatter (description, argument-hint, allowed-tools)
- [ ] Clear purpose statement
- [ ] Arguments documented
- [ ] Step-by-step instructions
- [ ] Example outputs
- [ ] Edge cases handled
- [ ] File paths are correct
- [ ] Referenced skills/commands exist

### For Skills
- [ ] Has valid YAML frontmatter (name, description)
- [ ] Description clearly indicates when Claude should autonomously invoke this Skill
- [ ] Includes `allowed-tools` if tool access should be restricted
- [ ] Tools in `allowed-tools` are appropriate for Skill's purpose (if present)
- [ ] Clear explanation of contexts/triggers for automatic invocation
- [ ] Practical examples showing what Claude can do with this knowledge
- [ ] Integration with other processes documented (which Commands reference this, etc.)
- [ ] Explains what knowledge/capabilities this provides to Claude

### For Hooks
- [ ] Has docstring explaining purpose
- [ ] Matches appropriate lifecycle event (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Notification, Stop)
- [ ] Event choice justified (why this event vs others?)
- [ ] Input/output format documented for the specific event type
- [ ] Error handling present (hooks should fail gracefully)
- [ ] File paths correct
- [ ] Registered in settings.json (if applicable)
- [ ] For PreToolUse: Uses correct permission decision format (permissionDecision: "allow"/"deny")
- [ ] For SessionStart: Properly handles environment variable persistence if needed

### For Agents
- [ ] Has valid YAML frontmatter (name, description, tools, model)
- [ ] Clear role definition (what specialized task does this handle?)
- [ ] Appropriate tool access for agent's isolated purpose
- [ ] Output guidelines (what should agent return to main conversation?)
- [ ] Justification for why this needs to be an Agent (context isolation, complexity, etc.)
- [ ] Documentation explains agent is invoked via Task tool
- [ ] Notes that agent cannot spawn other agents (no infinite nesting)
- [ ] Explains benefits of separate context window for this task

### For Templates
- [ ] Valid YAML frontmatter with required fields
- [ ] Placeholder instructions clear
- [ ] Consistent with documented patterns

### For CLAUDE.md
- [ ] All commands listed and accurate
- [ ] All skills listed and accurate
- [ ] All hooks listed and accurate
- [ ] All agents listed and accurate
- [ ] Directory structure accurate
- [ ] Examples work correctly

### For 0-System/ (Product Documentation)
- [ ] README.md provides accurate overview
- [ ] architecture.md reflects current system design
- [ ] patterns.md conventions match actual usage
- [ ] Guides in 0-System/guides/ match actual workflows
- [ ] Components in 0-System/components/ match .claude/ implementations
- [ ] roadmap.md reflects current development priorities
- [ ] changelog.md is up to date with recent changes
- [ ] No conflicts between 0-System/ and CLAUDE.md

## Cross-Reference Validation

Check these relationships:

```
0-System/guides ←→ CLAUDE.md (workflows documented in both? consistent?)
0-System/components ←→ .claude/ (component docs match actual implementation?)
0-System/architecture ←→ CLAUDE.md (structure descriptions aligned?)
CLAUDE.md ←→ Commands (all listed? user-invoked via /cmd?)
CLAUDE.md ←→ Skills (all listed? model-invoked autonomously?)
CLAUDE.md ←→ Hooks (all listed? event-triggered at correct lifecycle points?)
CLAUDE.md ←→ Agents (all listed? tool-invoked via Task?)
Commands ←→ Skills (do Commands reference Skills that exist?)
Commands ←→ Agents (do Commands use Task tool to invoke Agents?)
Skills ←→ allowed-tools (are tool restrictions appropriate for Skill's purpose?)
Agents ←→ Task tool invocation (are Agents documented as being invoked via Task?)
Agents ←→ tools frontmatter (does tool access match agent's specialized purpose?)
Hooks ←→ Lifecycle events (does hook use appropriate event for its purpose?)
Hooks ←→ Templates (does validation match template format?)
Hooks ←→ Event-specific behavior (PreToolUse = permission decisions, SessionStart = env vars, etc.)
Directory rules in hooks ←→ CLAUDE.md directory docs
```

### Architecture-Specific Validations

**For Skills:**
- If Skill modifies files, does it have Write/Edit in `allowed-tools`?
- If Skill only reads, is it restricted to Read/Grep/Glob?
- Does description explain WHEN Claude should autonomously use it?

**For Agents:**
- Is there a clear reason why this needs context isolation?
- Could this be a Skill instead (if it's just knowledge, not execution)?
- Are agents used via Task tool (not directly invoked)?

**For Hooks:**
- Is the lifecycle event correct for the hook's purpose?
  - Validation/blocking → PreToolUse
  - Checking/logging → PostToolUse
  - Context loading → SessionStart or UserPromptSubmit
  - Cleanup → Stop
- Does hook fail gracefully with proper error messages?

## Interaction Guidelines

- **Be thorough but efficient** - don't overwhelm with minor issues
- **Prioritize clarity** - always explain why something is an issue
- **Infer when possible** - if the right answer is obvious from CLAUDE.md, just fix it
- **Ask when uncertain** - use AskUserQuestion for genuine ambiguity
- **Batch changes** - group related fixes and confirm before applying
- **Preserve intent** - fix bugs, don't redesign unless asked

## Edge Cases

- **No issues found**: Report clean bill of health, suggest any improvements
- **Many issues**: Prioritize critical first, offer to fix in batches
- **Conflicting sources**: CLAUDE.md is authoritative, but ask if conflict seems intentional
- **Scope unclear**: Ask user to clarify what they want reviewed
