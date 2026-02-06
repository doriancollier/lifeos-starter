---
description: Ask how to do something in this vault/repository
argument-hint: [question]
allowed-tools: Read, Grep, Glob, Bash, Skill, SlashCommand, AskUserQuestion
---

# System Help Command

Answer questions about how to accomplish tasks in this Obsidian vault using Claude Code or manual methods.

## Arguments

- `$ARGUMENTS` - The question about how to do something (e.g., "how do I add a task?")

## Task

### 1. Research the Answer

Search these sources to find the relevant process:

**LifeOS Product Documentation (start here)**:
```bash
# Read the main README and find relevant guides
cat "{{vault_path}}/0-System/README.md"

# List all available guides
find "{{vault_path}}/0-System/guides" -name "*.md" -type f

# List component documentation
find "{{vault_path}}/0-System/components" -name "*.md" -type f
```

**CLAUDE.md (technical reference)**:
```bash
# Read the main project instructions
cat "{{vault_path}}/CLAUDE.md"
```

**Available slash commands**:
```bash
# List all available commands
find "{{vault_path}}/.claude/commands" -name "*.md" -type f
```

**Available skills**:
```bash
# List all skills
find "{{vault_path}}/.claude/skills" -name "SKILL.md" -type f
```

**Available agents**:
```bash
# List all agents
find "{{vault_path}}/.claude/agents" -name "*.md" -type f
```

**Hooks (automated behaviors)**:
```bash
# List all hooks
find "{{vault_path}}/.claude/hooks" -type f \( -name "*.py" -o -name "*.sh" \)
```

**Templates (for manual creation)**:
```bash
# List available templates
find "{{vault_path}}/3-Resources/Templates" -name "*.md" -type f
```

### 2. Read Relevant Files

Based on the question, read the relevant documentation files to understand:
- What slash commands are available
- What skills can help
- What the manual process involves
- What templates exist
- What automated hooks are in place

### 3. Identify the Best Approaches

Determine:
1. **Claude Code Method**: Is there a slash command, skill, or prompt that can do this?
2. **Manual Method**: What's the step-by-step process to do it by hand?
3. **Process Exists?**: Is there a clearly defined process, or is this undocumented?

### 4. Handle Missing Processes

If NO clear process exists for the user's question:

1. **Acknowledge the gap**: Clearly state that there's no defined process for this yet
2. **Provide best-effort guidance**: Offer what you can based on similar patterns
3. **Offer to create a process**: Ask if they'd like to create one

Use AskUserQuestion:
```
"I couldn't find a defined process for [topic]. Would you like me to create one?"
- Yes, create a new process
- No, the guidance you provided is enough
```

If user says **yes**, run `/system:update create a process for [topic based on user's question]`

### 5. Provide the Answer

## Output Format

```markdown
## How to: [Task Description]

### Via Claude Code

**Option 1: Slash Command** (if applicable)
Use the command: `/command:name [arguments]`

Example:
```
/daily:capture Add a new task for tomorrow
```

**Option 2: Direct Prompt** (if no slash command)
Send this to Claude Code:
```
[Example prompt that accomplishes the task]
```

**Option 3: Skill** (if a skill helps)
The `[skill-name]` skill can help with this. **Note:** Skills are model-invoked - Claude will automatically use this skill when the context matches. You don't explicitly invoke skills; Claude reads them autonomously when relevant to your task.

---

### Manual Method

1. **Open the file**: `[path/to/file.md]`
   - In Obsidian: [how to navigate]
   - Or I can open it for you

2. **Make the change**:
   [Step-by-step instructions]

3. **Save**:
   [Any additional steps]

---

### Would you like me to:
- [ ] Open the relevant file in Obsidian?
- [ ] Execute the Claude Code method now?
- [ ] Show you more details about [specific aspect]?
```

### Output Format (No Process Found)

```markdown
## How to: [Task Description]

### Process Status: Not Defined

There's no clearly defined process for this in the vault yet.

### Best-Effort Guidance

Based on similar patterns, here's how you might approach this:

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Create a Process?

Would you like me to create a defined process for this? This would:
- Add documentation to CLAUDE.md
- Create a slash command (if appropriate)
- Establish a consistent workflow

**Options:**
- Yes, create a new process → I'll run `/system:update`
- No, the guidance above is enough
```

## Common Question Mappings

Reference these when answering:

| Question Pattern | Claude Code | Manual |
|-----------------|-------------|--------|
| "add a task" | `/daily:capture` or prompt | Edit daily note, add `- [ ]` line |
| "create meeting note" | `/meeting:ab`, `/meeting:144`, `/meeting:emh` | Create in `workspace/5-Meetings/YYYY/MM-Month/` |
| "look up a person" | `/create:person [name]` | Search `workspace/6-People/` |
| "create a project" | `/create:project [name]` | Create in `workspace/1-Projects/Backlog/` |
| "today's tasks" | `/daily:tasks` | Open today's note in `workspace/4-Daily/` |
| "prepare for meeting" | `/meeting:prep [topic]` | Use `meeting-prep` skill |
| "switch context" | `/context:ab`, `/context:144`, etc. | Load relevant area |
| "end of day review" | `/daily:eod` | Review daily note tasks |
| "weekly review" | Use `weekly-review` skill | Review past 7 daily notes |

## Claude Code Architecture Notes

When explaining processes, clarify the invocation model:

**Slash Commands (User-Invoked):**
- User explicitly types `/command` to trigger them
- Example: `/daily:capture`, `/update`, `/meeting:prep`
- Use when: User wants explicit control over execution

**Skills (Model-Invoked):**
- Claude autonomously uses based on context matching
- User never directly invokes - Claude reads them when relevant
- Example: `daily-note`, `work-logging`, `task-system`
- Use when: Claude should automatically have knowledge available

**Agents (Tool-Invoked):**
- Invoked via Task tool for complex isolated workflows
- Have separate context windows
- Example: `vault-explorer`, `task-reviewer`
- Use when: Complex multi-step task needs isolation

**Hooks (Event-Triggered):**
- Automatically run at lifecycle events (SessionStart, PreToolUse, PostToolUse, etc.)
- Provide deterministic control
- Example: `directory-guard`, `frontmatter-validator`
- Use when: Behavior must happen at specific points

### When Explaining Processes

- **For Commands**: Explain they're user-triggered with `/cmd`
- **For Skills**: Emphasize they activate automatically when context matches
- **For Agents**: Mention they're spawned via Task tool for isolated execution
- **For Hooks**: Explain which lifecycle event triggers them

## Important Notes

- **Start with 0-System/ guides** - they provide user-friendly workflow documentation
- CLAUDE.md is the technical reference - use for implementation details
- If a slash command exists, prefer that over a raw prompt
- If manual, offer to open the relevant file using the `obsidian-open` skill
- Mention any relevant hooks that automate part of the process
- Clarify invocation model (user-invoked vs model-invoked vs tool-invoked vs event-triggered)

## LifeOS Guides Reference

| Guide | Topics Covered |
|-------|----------------|
| `workspace/0-System/guides/daily-workflow.md` | Daily planning, task management, EOD review |
| `workspace/0-System/guides/task-management.md` | A/B/C priority system, blocked tasks, scheduling |
| `workspace/0-System/guides/meeting-workflow.md` | Meeting prep, notes, follow-up |
| `workspace/0-System/guides/board-advisors.md` | Personal Board of Advisors deliberation |
| `workspace/0-System/guides/calendar-integration.md` | Timeboxing, context windows, calendar awareness |
