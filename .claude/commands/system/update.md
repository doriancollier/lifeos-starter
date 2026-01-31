---
description: Add, update, or improve processes based on user input
argument-hint: [description of what to add/change]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite, SlashCommand
---

# System Update Command

Add new processes, update existing ones, or improve the Claude Code workflow based on user instructions.

## Arguments

- `$ARGUMENTS` - Description of what to add, update, or improve. Examples:
  - "add a command to quickly log time spent on tasks"
  - "update the task system to support a 'delegated' status"
  - "improve the meeting prep process to include calendar integration"
  - "create a new skill for handling code reviews"

## Process Files Reference

| Type | Location | When to Create/Modify |
|------|----------|----------------------|
| **Commands** | `/.claude/commands/[namespace]/[name].md` | New quick actions |
| **Skills** | `/.claude/skills/[name]/SKILL.md` | Reusable knowledge/instructions |
| **Agents** | `/.claude/agents/[name].md` | Complex multi-step workflows |
| **Hooks** | `/.claude/hooks/[name].py` or `.sh` | Automated validation/actions |
| **Templates** | `/3-Resources/Templates/[name].md` | New note types |
| **Memory** | `/CLAUDE.md` | Core instructions, technical reference |
| **Guides** | `/0-System/guides/[name].md` | User-facing workflow documentation |
| **Components** | `/0-System/components/[name].md` | Documentation of system components |

### Documentation Layers

LifeOS has two documentation layers that should stay in sync:

1. **0-System/** - Product documentation (user-friendly guides, architecture, patterns)
2. **CLAUDE.md** - Technical reference (implementation details, tables, examples)

When adding significant new features, update both layers.

## Order of Operations

Execute these steps sequentially. This is an **interactive, research-first** process.

### Phase 1: Understand the Request

- [ ] **1.1** Parse `$ARGUMENTS` to understand:
  - What is the user trying to accomplish?
  - Is this a new process or modification of existing?
  - What type(s) of files will be involved?

- [ ] **1.2** Ask clarifying questions if the request is ambiguous:
  - Use AskUserQuestion with specific options when possible
  - Don't proceed until the goal is clear

### Phase 2: Research Current State

- [ ] **2.1** Read documentation sources:

  **0-System/ (product documentation)**:
  - `0-System/README.md` - System overview
  - `0-System/architecture.md` - How components interact
  - `0-System/patterns.md` - Naming conventions, standards
  - `0-System/guides/*.md` - Workflow documentation
  - `0-System/components/*.md` - Component documentation

  **CLAUDE.md (technical reference)**:
  - Current process architecture
  - Existing patterns and conventions
  - What's already documented

- [ ] **2.2** Search for related existing processes:
  ```bash
  # Find related documentation in 0-System
  grep -r "[relevant keywords]" "/0-System" --include="*.md" -l

  # Find related commands
  grep -r "[relevant keywords]" "/.claude/commands" --include="*.md" -l

  # Find related skills
  grep -r "[relevant keywords]" "/.claude/skills" --include="*.md" -l

  # Find related hooks
  grep -r "[relevant keywords]" "/.claude/hooks" -l

  # Check templates
  grep -r "[relevant keywords]" "/3-Resources/Templates" --include="*.md" -l
  ```

- [ ] **2.3** Read related files to understand:
  - How similar things are currently done
  - What patterns to follow
  - What might need to be updated alongside

- [ ] **2.4** Identify connections:
  - What existing processes will this interact with?
  - What needs to reference the new/updated process?
  - Are there hooks that will validate this?

### Phase 3: Create the Plan

- [ ] **3.1** Determine what files need to be:
  - **Created**: New files that don't exist
  - **Modified**: Existing files that need updates
  - **Referenced**: Files that should link to new content

- [ ] **3.2** Create a detailed action plan using TodoWrite:
  ```
  1. [First action] - [file affected]
  2. [Second action] - [file affected]
  3. Update CLAUDE.md documentation
  4. Verify cross-references
  ```

- [ ] **3.3** Present the plan to user:
  ```markdown
  ## Implementation Plan: [Brief Title]

  ### Understanding
  You want to: [summary of goal]

  ### Research Findings
  - Related existing process: [what exists]
  - Pattern to follow: [which existing file is a good model]
  - Connections: [what will interact with this]

  ### Proposed Actions

  #### New Files to Create
  1. `[path/to/new/file.md]` - [purpose]

  #### Files to Modify
  1. `[path/to/existing.md]` - [what changes]
  2. `/CLAUDE.md` - Add documentation for new process

  #### Validation
  - [ ] Follows existing patterns
  - [ ] CLAUDE.md will be updated
  - [ ] No conflicts with existing processes

  ### Questions Before Proceeding
  - [Any decisions needed]

  **Does this plan look correct?**
  ```

- [ ] **3.4** Wait for user approval or adjustments

### Phase 4: Execute the Plan

- [ ] **4.1** Work through the todo list methodically:
  - Complete one item at a time
  - Mark items complete as you go
  - If you encounter issues, pause and ask

- [ ] **4.2** For each new file, follow the appropriate template:

**Command Template:**
```markdown
---
description: [clear description]
argument-hint: [argument format]
allowed-tools: [appropriate tools]
---

# [Command Name]

[Purpose and context]

## Arguments

- `$ARGUMENTS` - [description]

## Task

### Step 1: [First Step]
[Instructions]

### Step 2: [Next Step]
[Instructions]

## Output Format

[Expected output structure]

## Edge Cases

[How to handle unusual situations]
```

**Skill Template:**
```markdown
---
name: [skill-name]
description: [when to use this skill - be specific about triggers for autonomous invocation]
allowed-tools: [Read, Grep, Glob]  # OPTIONAL - restricts Claude's tool access when using this Skill
---

# [Skill Name]

[Detailed knowledge and instructions that Claude will autonomously read when context matches]

## When to Use

[Describe the contexts/scenarios where Claude should automatically use this Skill]
[Remember: You don't invoke Skills - Claude reads them when relevant to the task]

## Key Information

[Core knowledge this Skill provides - Claude will have this available when Skill is active]

## Integration

[How this works with other processes - which Commands might reference this, which other Skills complement it]

## Tool Access (if using allowed-tools)

[Explain why these specific tools are restricted to this Skill's use cases]
```

**Agent Template:**
```markdown
---
name: [agent-name]
description: [purpose - what specialized task does this agent handle?]
tools: [tool list - what tools does this isolated agent need?]
model: [sonnet/haiku/opus - which model is appropriate for this task?]
---

# [Agent Name]

[Role and capabilities - remember this agent runs in a separate context window]

## Your Task

[What the agent should accomplish in its isolated execution]
[Note: This agent is invoked via the Task tool, not directly]
[Note: This agent cannot spawn other agents (no infinite nesting)]

## Guidelines

[How to approach the work within this agent's specialized context]

## Why This is an Agent

[Explain why this needs context isolation / separate execution]
[Example reasons: complex multi-step workflow, specialized expertise, security isolation]

## Output Format

[What should this agent return to the main conversation?]
[Remember: The main conversation doesn't see the agent's internal work, only the final output]
```

- [ ] **4.3** After creating/modifying process files, update documentation:

  **CLAUDE.md** (always update):
  - Add to appropriate table (commands, skills, hooks, agents)
  - Add to usage examples if helpful
  - Ensure accuracy

  **0-System/** (update when significant):
  - Update relevant guide if workflow changes (`0-System/guides/`)
  - Update component doc if adding new command/skill/agent (`0-System/components/`)
  - Update changelog (`0-System/changelog.md`) for notable changes

### Phase 5: Batch Confirmation

- [ ] **5.1** Before writing any files, present the batch:
  ```markdown
  ## Ready to Apply Changes

  ### Files to Create
  1. `[path]` - [X lines]

  ### Files to Modify
  1. `[path]` - [summary of changes]

  ### Preview of Key Changes

  **[filename]:**
  ```
  [Key content snippet]
  ```

  **Proceed with these changes?**
  ```

- [ ] **5.2** Wait for explicit confirmation

- [ ] **5.3** Apply all changes

### Phase 6: Verification

- [ ] **6.1** Verify the implementation:
  - Read back created/modified files
  - Check CLAUDE.md is accurate
  - Verify no broken references

- [ ] **6.2** Report completion:
  ```markdown
  ## Implementation Complete

  ### Created
  - `[path]` - [description]

  ### Modified
  - `[path]` - [what changed]

  ### How to Use
  [Quick instructions for the new/updated process]

  ### Testing Suggestion
  Try: `[example usage]`
  ```

- [ ] **6.3** Offer follow-up:
  - "Would you like me to test this?"
  - "Any adjustments needed?"

### Phase 7: Automatic Review

- [ ] **7.1** After implementation is complete, automatically run `/system:review` to validate:
  - The new/updated processes are consistent with existing ones
  - CLAUDE.md documentation is accurate
  - No conflicts were introduced
  - Cross-references are valid

- [ ] **7.2** Report the review findings and address any issues discovered

**Note**: This automatic review ensures quality and catches any inconsistencies introduced by the update.

## Claude Code Architecture Primer

Understanding HOW each component is invoked is critical for choosing the right file type.

### Invocation Models

| Component | Invocation | When to Use | Example |
|-----------|------------|-------------|---------|
| **Slash Command** | **User-invoked** - User types `/command` | User wants explicit control over when this runs | `/daily:capture`, `/update` |
| **Skill** | **Model-invoked** - Claude autonomously reads when relevant | Claude should automatically have this knowledge available | `daily-note`, `work-logging` |
| **Agent** | **Tool-invoked** - Invoked via Task tool for isolated tasks | Complex multi-step workflows needing separate context | `vault-explorer`, `task-reviewer` |
| **Hook** | **Event-triggered** - Runs at specific lifecycle events | Deterministic behavior that MUST happen at specific points | `directory-guard`, `frontmatter-validator` |

### Key Architecture Concepts

**Slash Commands:**
- User explicitly types `/command` to trigger them
- They are expanded prompts - Markdown files containing instructions
- User controls when they execute
- Can reference Skills in their instructions (but don't "invoke" them)

**Skills:**
- Claude **autonomously** decides when to use them based on context
- They provide knowledge Claude draws from automatically
- Can restrict tool access with `allowed-tools` frontmatter
- When task context matches the Skill's description, Claude reads it
- You never explicitly invoke a Skill - Claude does it for you

**Agents:**
- Invoked via the **Task tool** for complex isolated workflows
- Have **separate context windows** (prevents context pollution)
- Cannot spawn other agents (prevents infinite nesting)
- Use when task needs isolation or specialized expertise
- Custom system prompts and tool permissions

**Hooks:**
- Automatically run at specific **lifecycle events**
- Provide deterministic control (always happen at certain points)
- Don't rely on LLM decisions - they execute based on events
- Available events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`

### Key Questions for Choosing Type

**Ask yourself:**

1. **Who decides when this runs?**
   - User explicitly triggers → **Command**
   - Claude decides based on context → **Skill**
   - Spawned for complex isolated task → **Agent**
   - System automatically at lifecycle event → **Hook**

2. **Does it need tool restrictions?**
   - Yes, limit what Claude can do → Use **Skill** with `allowed-tools`
   - Yes, isolate for security → Use **Agent** with custom tool list

3. **Does it need separate context?**
   - Yes, prevent context pollution → **Agent** (separate context window)
   - No, share context → **Command** or **Skill**

### Lifecycle Events (for Hooks)

| Event | When It Fires | Common Uses |
|-------|---------------|-------------|
| `SessionStart` | New/resumed session starts | Load context, set env vars, install dependencies |
| `UserPromptSubmit` | User submits a prompt | Add contextual information, check time/calendar |
| `PreToolUse` | Before tool executes | Permission gating, validation, blocking |
| `PostToolUse` | After tool completes | Validation, formatting checks, logging |
| `Notification` | System notification shown | Custom alerts, external integrations |
| `Stop` | Session ends | Cleanup, auto-commit, final actions |

## Decision Framework

When making implementation choices:

### Choosing File Type

See **Claude Code Architecture Primer** above for detailed explanation of invocation models.

| If the need is... | Create a... | Why |
|-------------------|-------------|-----|
| User wants explicit control over execution | Command | User-invoked via `/command` |
| Claude needs automatic access to knowledge | Skill | Model-invoked autonomously |
| Complex task needs isolation/separate context | Agent | Tool-invoked via Task tool |
| Deterministic behavior at lifecycle events | Hook | Event-triggered automatically |
| New note structure/template | Template | File creation pattern |

### Choosing Location

| Command type | Namespace |
|--------------|-----------|
| Daily workflow | `daily/` |
| Meeting related | `meeting/` |
| Context switching | `context/` |
| Creating things | `create/` |
| System/meta | `system/` |
| Other | Create new namespace or use root |

### Naming Conventions

- **Commands**: `verb` or `noun` (e.g., `capture`, `tasks`, `note`)
- **Skills**: `domain-action` (e.g., `task-system`, `meeting-prep`)
- **Agents**: `role-based` (e.g., `vault-explorer`, `task-reviewer`)
- **Hooks**: `action-target` (e.g., `directory-guard`, `frontmatter-validator`)

## Interaction Guidelines

- **Research first** - Never modify without understanding current state
- **Confirm assumptions** - If unsure about user intent, ask
- **Follow patterns** - Match existing file structure and style
- **Update documentation** - CLAUDE.md must reflect changes
- **Batch changes** - Group related modifications
- **Explain reasoning** - Help user understand implementation choices
- **Offer alternatives** - If there are multiple good approaches, present options

## Quality Checklist

Before presenting changes for approval:

- [ ] Follows existing naming conventions
- [ ] Uses appropriate file type for the need
- [ ] Has complete YAML frontmatter
- [ ] Includes clear instructions/documentation
- [ ] Handles edge cases
- [ ] Will be documented in CLAUDE.md
- [ ] Doesn't conflict with existing processes
- [ ] File paths are correct and consistent

## Edge Cases

- **Request is vague**: Ask clarifying questions before planning
- **Request conflicts with existing**: Present the conflict, ask how to resolve
- **Request requires multiple file types**: Plan all together, implement sequentially
- **Request affects hooks**: Extra caution - hooks can block operations
- **Request is very large**: Break into phases, confirm each phase
