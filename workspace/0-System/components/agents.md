---
title: "Agents"
created: "2025-12-02"
status: "active"
---

# Agents

Agents are autonomous executors spawned for complex, multi-step tasks.

## How Agents Work

Agents are **tool-invoked** — Claude spawns them via the Task tool when a complex task needs isolated execution.

```
Claude: needs deep vault exploration
       ↓
Spawns vault-explorer agent
       ↓
Agent works in separate context
       ↓
Returns final report to main Claude
```

## Key Characteristics

- **Separate context window** — Agents don't see the full conversation
- **Autonomous execution** — Work independently until done
- **Single report back** — Return one final message
- **Stateless** — Each invocation starts fresh

## Agent Structure

Agents live in `.claude/agents/[agent-name].md`:

```
.claude/agents/
├── context-isolator.md
├── vault-explorer.md
├── task-reviewer.md
├── meeting-processor.md
├── relationship-manager.md
├── research-expert.md
├── product-manager.md
├── email-processor.md
├── system-reviewer.md
├── persona-board-chair.md
├── persona-strategic-operator.md
├── persona-relationships-guardian.md
├── persona-health-steward.md
└── persona-execution-coach.md
```

## Available Agents

### General Purpose

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `context-isolator` | Run data-heavy ops in isolated context | Calendar views, large searches, data aggregation |
| `vault-explorer` | Deep search and navigation | Finding information across vault |
| `task-reviewer` | Task management analysis | Daily/weekly planning |
| `meeting-processor` | Process meeting transcripts with user context | Analyzing downloaded meeting notes |
| `relationship-manager` | People intelligence | Understanding relationships |
| `research-expert` | Parallel research | Focused research tasks |
| `product-manager` | PM document generation | PRDs, roadmaps, user stories |
| `email-processor` | Email triage and processing | Inbox processing, email summarization, finding important emails |
| `system-reviewer` | Parallel system component review | Spawned by /system:review orchestrator for parallel analysis |

### Personal Board of Advisors

| Agent | Role | Perspective |
|-------|------|-------------|
| `persona-board-chair` | Orchestrator | Synthesis and balance |
| `persona-strategic-operator` | Business | Wealth, growth, leverage |
| `persona-relationships-guardian` | Relationships | Family, trust, people |
| `persona-health-steward` | Health | Sustainability, energy |
| `persona-execution-coach` | Execution | Action, discipline |

## Agent Definition Format

```markdown
---
description: "Brief description for agent discovery"
tools: ["Tool1", "Tool2", "Tool3"]
---

# [Agent Name]

## Purpose

What this agent does.

## When to Use

- Scenario 1
- Scenario 2

## Instructions

Detailed instructions for the agent.

## Input Expected

What information the agent needs.

## Output Expected

What the agent should return.
```

## Spawning Agents

Claude uses the Task tool to spawn agents:

```
Task tool with:
- subagent_type: "vault-explorer"
- prompt: "Find all references to [topic] in the vault"
- description: "Search vault for topic"
```

## Creating a New Agent

1. **Identify use case** — Complex task needing isolation
2. **Create file:** `.claude/agents/[agent-name].md`
3. **Define tools** the agent needs access to
4. **Write instructions** for autonomous execution
5. **Specify output format** for the final report
6. **Add to CLAUDE.md** agents table
7. **Start new session** — Agents are discovered at session start

**Important:** Claude Code discovers available agents when a session begins. If you create a new agent file mid-session, it won't be available until you start a new session.

### Template

```markdown
---
description: "One-line description"
tools: ["Read", "Grep", "Glob", "Bash"]
---

# [Agent Name]

## Purpose

What this agent accomplishes.

## When to Use

- Use case 1
- Use case 2
- NOT for: anti-use cases

## Instructions

### Phase 1: [Action]

Details...

### Phase 2: [Action]

Details...

### Phase 3: [Action]

Details...

## Input Format

What information to include in the prompt.

## Output Format

Structure of the final report.

## Example

**Prompt:** "Example task"
**Expected output:** Example response structure
```

## Best Practices

1. **Clear scope** — Define what the agent does and doesn't do
2. **Minimal tools** — Only include necessary tools
3. **Structured output** — Define report format
4. **Error handling** — What if the task can't be completed?
5. **Context in prompt** — Agent can't see conversation history

## Agent Resumption & Session State

Some agents (like `persona-board-chair`) run multi-step workflows that pause to ask the user questions. When resuming these agents, special care is needed to maintain state.

### The Problem

When an agent pauses mid-workflow (e.g., for Q&A), the resume operation starts fresh without knowledge of:
- Session directories created in the first invocation
- Files already written
- Configuration set up earlier

### The Solution: Session State Files

For agents with multi-step workflows:

1. **Create a state file** (e.g., `config.json`) with session context:
```json
{
  "session_directory": "/full/path/to/session/",
  "current_phase": "qa-1",
  "rounds_completed": 1,
  "created": "2025-12-31T10:00:00"
}
```

2. **Return the session path** when pausing:
```
Session Directory: /full/path/to/session/
agentId: abc123 (for resuming)
```

3. **Pass the session path on resume**:
```
Task tool:
- resume: abc123
- prompt: |
    SESSION DIRECTORY (USE THIS - DO NOT CREATE NEW):
    /full/path/to/session/

    [Additional context for resumption]
```

### Resume Prompt Template

When resuming a stateful agent:

```markdown
**CRITICAL: Session Context**
- Session Directory: [exact path - use this, don't create new]
- Previous Phase Completed: [what was done]
- Current Phase: [what to do now]

**New Information:**
[Any user answers or new context]

Continue from where you left off. Write all files to the session directory above.
```

### Agents Requiring Session State

| Agent | Multi-Step? | State File |
|-------|-------------|------------|
| `persona-board-chair` | Yes (Q&A phases) | `config.json` in session directory |
| Others | No | N/A |

### Lesson Learned (2025-12-31)

A Board deliberation created duplicate directories (`2025-12-31-annual-planning/` and `2025-12-31-2026-annual-planning/`) because the resume prompt didn't include the session directory. The resumed agent derived a new name instead of using the existing one.

**Prevention**: Always pass the exact session directory path when resuming multi-step agents.
