---
description: Review processes for clarity, consistency, and improvements
argument-hint: [area to review (optional)]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, Task, TaskCreate, TaskList, TaskUpdate, TaskOutput
---

# System Review Command (Orchestrator)

Review Claude Code processes (commands, skills, hooks, agents, templates, configuration) for clarity, consistency, and potential improvements.

This command operates as an **orchestrator** that:
- Determines review scope and mode based on file count
- Spawns parallel `system-reviewer` agents for large reviews
- Synthesizes findings from all sources
- Presents unified recommendations

## Arguments

- `$ARGUMENTS` - Optional area to focus on. If empty, review everything.
  - Valid areas: `commands`, `skills`, `hooks`, `agents`, `templates`, `config`, `memory` (CLAUDE.md), `guides` (0-System), `docs` (0-System)
  - Can also specify a specific file or pattern: `daily commands`, `task-system skill`

## Review Areas

| Area | Location | File Pattern |
|------|----------|--------------|
| **Commands** | `.claude/commands/` | `**/*.md` |
| **Skills** | `.claude/skills/` | `**/SKILL.md` |
| **Hooks** | `.claude/hooks/` | `*.py`, `*.sh` |
| **Agents** | `.claude/agents/` | `*.md` |
| **Templates** | `workspace/3-Resources/Templates/` | `*.md` |
| **0-System** | `workspace/0-System/` | `**/*.md` |
| **CLAUDE.md** | Root | `CLAUDE.md`, `.claude/rules/*.md` |

## Execution Modes

| Mode | File Count | Strategy |
|------|------------|----------|
| **Small** | <20 files | Direct analysis in main context |
| **Medium** | 20-100 files | 2-3 parallel agents (synchronous) |
| **Large** | >100 files | Full fan-out with `run_in_background: true` |

---

## Phase 1: Discovery & Inventory

### 1.1 Determine Scope

Parse `$ARGUMENTS` to determine what to review:
- If empty → review ALL areas
- If area specified → focus on that area + cross-references
- If specific file → review just that file

### 1.2 Build Inventory

Count files in each area using Glob:

```
Commands:   Glob(".claude/commands/**/*.md")
Skills:     Glob(".claude/skills/**/SKILL.md")
Hooks:      Glob(".claude/hooks/*.py") + Glob(".claude/hooks/*.sh")
Agents:     Glob(".claude/agents/*.md") (exclude .template.md)
Templates:  Glob("workspace/3-Resources/Templates/*.md")
0-System:   Glob("workspace/0-System/**/*.md")
CLAUDE.md:  CLAUDE.md + .claude/rules/*.md
```

### 1.3 Determine Mode

```
total_files = sum of all area counts
if total_files < 20:     MODE = "SMALL"
elif total_files <= 100: MODE = "MEDIUM"
else:                    MODE = "LARGE"
```

### 1.4 Report to User

```markdown
## System Review: Discovery

**Scope:** [areas being reviewed]
**Mode:** [SMALL/MEDIUM/LARGE]

| Area | Files |
|------|-------|
| Commands | X |
| Skills | Y |
| Hooks | Z |
| ... | ... |
| **Total** | **N** |

[For MEDIUM/LARGE: Creating session directory for tracking]
```

### 1.5 Create Session Directory (Medium/Large Only)

For Medium and Large reviews:

```
session_dir = ".claude/review-sessions/YYYY-MM-DD-[scope]/"

Create:
  {session_dir}/config.json
  {session_dir}/inventory.md
  {session_dir}/findings/
  {session_dir}/cross-references/
  {session_dir}/synthesis/
  {session_dir}/fixes/
```

**config.json:**
```json
{
  "created": "ISO timestamp",
  "scope": "[scope description]",
  "mode": "SMALL|MEDIUM|LARGE",
  "current_phase": "discovery",
  "areas": {
    "commands": {"files": N, "status": "pending"},
    "skills": {"files": N, "status": "pending"},
    ...
  },
  "agents": {}
}
```

---

## Phase 2: Task Creation

Create tasks to track progress:

```javascript
// Main orchestration tasks
TaskCreate({ subject: "Discovery & Inventory", activeForm: "Building inventory" })
TaskCreate({ subject: "Analyze components", activeForm: "Analyzing" })
TaskCreate({ subject: "Cross-reference validation", activeForm: "Validating cross-references" })
TaskCreate({ subject: "Synthesize findings", activeForm: "Synthesizing" })
TaskCreate({ subject: "Present findings", activeForm: "Presenting" })
TaskCreate({ subject: "Apply approved fixes", activeForm: "Applying fixes" })

// Set dependencies
TaskUpdate({ taskId: "cross-ref", addBlockedBy: ["analyze"] })
TaskUpdate({ taskId: "synthesize", addBlockedBy: ["cross-ref"] })
TaskUpdate({ taskId: "present", addBlockedBy: ["synthesize"] })
TaskUpdate({ taskId: "fixes", addBlockedBy: ["present"] })
```

For MEDIUM/LARGE modes, also create per-area tasks:
```javascript
TaskCreate({ subject: "Review commands (N files)", activeForm: "Reviewing commands" })
TaskCreate({ subject: "Review skills (N files)", activeForm: "Reviewing skills" })
// ... for each area with files
```

---

## Phase 3: Analysis

### SMALL Mode (Direct Analysis)

For <20 files, analyze directly in main context:

1. Read CLAUDE.md first (source of truth)
2. Read each file in scope
3. Apply relevant checklist (see Review Checklists below)
4. Classify issues as Critical/Warning/Suggestion
5. Note cross-reference items for Phase 4

### MEDIUM Mode (Parallel Agents, Synchronous)

For 20-100 files, spawn 2-3 agents synchronously:

Group areas into batches:
- Batch 1: Commands + Skills (code-like)
- Batch 2: Hooks + Agents (implementation)
- Batch 3: Templates + Docs (content)

Spawn agents in a single message (parallel execution):

```
Task #1:
  subagent_type: system-reviewer
  description: "Review commands and skills"
  prompt: |
    ## Assignment: Commands & Skills Review

    **Session Directory:** {session_dir}

    **Commands to review:**
    {list of command files}

    **Skills to review:**
    {list of skill files}

    Apply the Commands checklist to each command file.
    Apply the Skills checklist to each skill file.

    Write findings to:
    - {session_dir}/findings/commands.md
    - {session_dir}/findings/skills.md

    Write cross-references to:
    - {session_dir}/cross-references/commands.json
    - {session_dir}/cross-references/skills.json

Task #2:
  subagent_type: system-reviewer
  description: "Review hooks and agents"
  prompt: [similar structure for hooks + agents]

Task #3:
  subagent_type: system-reviewer
  description: "Review templates and docs"
  prompt: [similar structure for templates + docs]
```

Wait for all agents to complete, then read findings from session directory.

### LARGE Mode (Background Agents, Asynchronous)

For >100 files, spawn all area agents with `run_in_background: true`:

Spawn one agent per area in a single message:

```
Task #1:
  subagent_type: system-reviewer
  run_in_background: true
  description: "Review commands"
  prompt: [commands-specific prompt]

Task #2:
  subagent_type: system-reviewer
  run_in_background: true
  description: "Review skills"
  prompt: [skills-specific prompt]

Task #3:
  subagent_type: system-reviewer
  run_in_background: true
  description: "Review hooks"
  prompt: [hooks-specific prompt]

... (all areas in single message for true parallelism)
```

Update config.json with agent output_file paths.

Poll for completion:
```javascript
// Check periodically until all complete
for each agent_id in config.agents:
  result = TaskOutput({ task_id: agent_id, block: false })
  if result.status == "completed":
    update config.agents[area].status = "completed"
```

Report progress to user while waiting:
```markdown
## Review Progress

| Area | Status | Files |
|------|--------|-------|
| Commands | Complete | 69 |
| Skills | In Progress... | 49 |
| Hooks | Complete | 15 |
| ... | ... | ... |
```

---

## Phase 4: Cross-Reference Validation

After all area analyses complete:

1. Read all cross-reference JSON files from `{session_dir}/cross-references/`
2. Build unified reference map
3. Validate each reference:
   - Commands → Skills: Does referenced skill exist?
   - Commands → Commands: Does referenced command exist?
   - Hooks → Patterns: Does validated pattern exist?
   - CLAUDE.md → All: Are all components listed?
4. Classify validation failures as Critical/Warning

```markdown
## Cross-Reference Validation

### Missing References
- `daily/plan.md` references skill `calendar-awareness` - **FOUND**
- `daily/plan.md` references command `health:sync` - **FOUND**
- `system/update.md` references skill `nonexistent-skill` - **NOT FOUND** (Critical)

### CLAUDE.md Sync
- Commands listed: 85, actual: 87 - **MISMATCH** (Warning)
  - Missing from CLAUDE.md: `/new:command`, `/other:command`
```

---

## Phase 5: Synthesis

Combine all findings into unified report:

1. Read all findings from `{session_dir}/findings/`
2. Merge into single list, deduplicating
3. Sort by severity (Critical → Warning → Suggestion)
4. Group by area or by fix type
5. Identify patterns (same issue across multiple files)

Write synthesis to `{session_dir}/synthesis/report.md`:

```markdown
## Synthesis Report

**Total Issues:** X Critical, Y Warning, Z Suggestions
**Files Affected:** N

### Patterns Detected
- "Missing examples" appears in 12 command files
- "Outdated paths" appears in 5 skill files

### Critical Issues (must fix)
1. [Issue] in `file.md` - [brief description]
2. ...

### Warnings (should fix)
1. ...

### Suggestions (optional)
1. ...
```

---

## Phase 6: User Review

Present findings with AskUserQuestion for decisions:

```markdown
## System Review: Findings

**Scope:** [what was reviewed]
**Files Reviewed:** X
**Issues Found:** Y Critical, Z Warning, W Suggestions

### Critical Issues (must fix)

- [ ] **Missing skill reference** in `.claude/commands/daily/plan.md`
  - References `nonexistent-skill` which doesn't exist
  - **Fix:** Remove reference or create skill

### Warnings (should fix)

- [ ] **CLAUDE.md out of sync**
  - Commands table missing 2 entries
  - **Fix:** Add missing commands

### Suggestions

- [ ] Add examples to 12 command files
```

For issues requiring decisions:
```javascript
AskUserQuestion({
  questions: [{
    header: "Fix approach",
    question: "How should we handle the missing skill reference?",
    options: [
      { label: "Remove reference (Recommended)", description: "Simplest fix" },
      { label: "Create the skill", description: "If the functionality is needed" },
      { label: "Skip", description: "Don't fix this" }
    ]
  }]
})
```

---

## Phase 7: Apply Fixes

After user approves:

1. Group approved changes by file
2. Present batch summary:
   ```markdown
   ## Proposed Changes

   ### File: `.claude/commands/daily/plan.md`
   - Remove reference to nonexistent skill

   ### File: `CLAUDE.md`
   - Add missing commands to table

   **Proceed with these X changes?**
   ```

3. Wait for confirmation
4. Apply changes using Edit tool
5. Log changes to `{session_dir}/fixes/log.md`

---

## Phase 8: Report

Final summary:

```markdown
## System Review Complete

**Session:** {session_dir}
**Duration:** [time elapsed]

### Changes Applied
- [x] Fixed X critical issues
- [x] Fixed Y warnings
- [ ] Z suggestions deferred

### Files Modified
- `.claude/commands/daily/plan.md`: Removed invalid reference
- `CLAUDE.md`: Added 2 missing commands

### Remaining Items
- [ ] [Any deferred items]

### Recommendations
1. [High-value improvement opportunity]
2. [Nice-to-have improvement]
```

---

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
- [ ] Listed in CLAUDE.md or components.md

### For Skills

- [ ] Has valid YAML frontmatter (name, description)
- [ ] Description indicates when Claude should invoke autonomously
- [ ] Includes `allowed-tools` if tool access should be restricted
- [ ] Tools in `allowed-tools` are appropriate for purpose
- [ ] Clear trigger conditions
- [ ] Practical examples
- [ ] Integration documented
- [ ] Listed in CLAUDE.md or components.md

### For Hooks

- [ ] Has docstring explaining purpose
- [ ] Matches appropriate lifecycle event
- [ ] Event choice justified
- [ ] Input/output format documented
- [ ] Error handling present
- [ ] File paths correct
- [ ] Registered in settings.json
- [ ] For PreToolUse: Uses correct permission decision format
- [ ] Listed in CLAUDE.md or components.md

### For Agents

- [ ] Valid YAML frontmatter (name, description, tools, model)
- [ ] Clear role definition
- [ ] Appropriate tool access
- [ ] Output guidelines defined
- [ ] Justification for agent vs skill
- [ ] Documentation explains Task tool invocation
- [ ] Listed in CLAUDE.md or components.md

### For Templates

- [ ] Valid YAML frontmatter with required fields
- [ ] Placeholder instructions clear
- [ ] Consistent with documented patterns

### For 0-System Documentation

- [ ] Content accuracy (matches actual implementation)
- [ ] Completeness (covers all relevant components)
- [ ] Sync with CLAUDE.md (no conflicts)
- [ ] Examples work correctly
- [ ] Links/references valid

---

## Cross-Reference Validation

Check these relationships:

```
0-System/guides ←→ CLAUDE.md (workflows consistent?)
0-System/components ←→ .claude/ (docs match implementation?)
CLAUDE.md ←→ Commands (all listed?)
CLAUDE.md ←→ Skills (all listed?)
CLAUDE.md ←→ Hooks (all listed?)
CLAUDE.md ←→ Agents (all listed?)
Commands ←→ Skills (referenced skills exist?)
Commands ←→ Agents (Task tool invocations valid?)
Hooks ←→ Patterns (validated patterns exist?)
```

---

## Resumption Support

If review is interrupted, it can be resumed:

1. Check for existing session: `Glob(".claude/review-sessions/YYYY-MM-DD-*")`
2. If found, read `config.json` for state
3. Resume from `current_phase`
4. For background agents, check `TaskOutput` for any completed

Ask user:
```javascript
AskUserQuestion({
  questions: [{
    header: "Resume",
    question: "Found existing session from today. Resume or start fresh?",
    options: [
      { label: "Resume (Recommended)", description: "Continue where you left off" },
      { label: "Start fresh", description: "Archive old session and start new" }
    ]
  }]
})
```

---

## Interaction Guidelines

- **Be thorough but efficient** - Don't overwhelm with minor issues
- **Prioritize clarity** - Always explain why something is an issue
- **Infer when possible** - If the right answer is obvious, just fix it
- **Ask when uncertain** - Use AskUserQuestion for genuine ambiguity
- **Batch changes** - Group related fixes and confirm before applying
- **Preserve intent** - Fix bugs, don't redesign unless asked
- **Track progress** - Update tasks as phases complete

---

## Agent Availability Note

This command uses the `system-reviewer` agent for parallel analysis. If the agent isn't available (error: "Agent type 'system-reviewer' not found"), fall back to:

1. **For SMALL/MEDIUM reviews**: Use `general-purpose` agent instead
2. **For LARGE reviews**: Consider splitting into multiple sessions

The `system-reviewer` agent is defined in `.claude/agents/system-reviewer.md` and should be auto-discovered at session start. If it's not available, ensure:
- The file exists with valid YAML frontmatter
- You've started a new Claude Code session after the agent file was created
