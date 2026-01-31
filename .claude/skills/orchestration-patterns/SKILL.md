---
name: orchestration-patterns
description: Agent delegation and orchestration patterns for efficient context management. Use when designing new commands, tackling complex multi-step tasks, or deciding whether to delegate work to subagents.
---

# Orchestration Patterns

Knowledge for designing efficient workflows that delegate context-heavy work to subagents while keeping the main conversation context clean.

## When to Use This Skill

Claude should automatically apply these patterns when:
- **Designing new commands** that involve analysis, search, or data processing
- **Tackling complex tasks** that might flood context
- **Deciding execution strategy** for multi-step workflows
- **Building orchestrator commands** like `/system:review` or `/board:advise`

## Core Principle: Context Conservation

The main conversation context is precious. Protect it by:
1. **Delegating data-heavy analysis** to subagents
2. **Returning only structured summaries** to main context
3. **Using lightweight models** (Haiku) for simple analysis tasks
4. **Keeping user interaction** in main context

---

## Decision Framework

### When to Delegate to Agents

| Situation | Direct Execution | Delegate to Agent |
|-----------|------------------|-------------------|
| Reading 1-3 files | ✓ | |
| Reading 10+ files | | ✓ |
| Simple git commands | ✓ | |
| Analyzing commit history | | ✓ |
| User confirmation flow | ✓ | |
| Data aggregation/analysis | | ✓ |
| Parallel independent tasks | | ✓ |
| Interactive workflow | ✓ | |

### The 3-Tier Execution Model

Based on scope/complexity, choose execution mode:

```
┌─────────────────────────────────────────────────────────────┐
│ SMALL MODE (<20 items, simple analysis)                     │
│ - Execute directly in main context                          │
│ - No agent spawning needed                                  │
│ - Example: Reading one changelog, few commits               │
├─────────────────────────────────────────────────────────────┤
│ MEDIUM MODE (20-100 items, moderate analysis)               │
│ - Spawn 1-3 agents SYNCHRONOUSLY                            │
│ - Wait for results with block: true                         │
│ - Example: Reviewing a subsystem, moderate file count       │
├─────────────────────────────────────────────────────────────┤
│ LARGE MODE (>100 items, heavy analysis)                     │
│ - Spawn all agents with run_in_background: true             │
│ - Poll for completion, report progress                      │
│ - Example: Full system review, comprehensive search         │
└─────────────────────────────────────────────────────────────┘
```

---

## Orchestrator Architecture

An orchestrator command follows this pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN CONTEXT (Orchestrator)              │
│                                                             │
│  1. Parse arguments                                         │
│  2. Pre-flight checks (quick validation)                    │
│  3. Determine execution mode (SMALL/MEDIUM/LARGE)           │
│  4. Spawn analysis agent(s) if needed                       │
│  5. Receive structured results                              │
│  6. Present to user, get confirmation                       │
│  7. Execute final actions                                   │
│  8. Report results                                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼ (if needed)
┌─────────────────────────────────────────────────────────────┐
│                    SUBAGENT (Analysis)                      │
│                                                             │
│  - Read data (files, commits, calendar, etc.)               │
│  - Analyze patterns                                         │
│  - Return STRUCTURED result (not raw data)                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Rules

1. **Pre-flight in main context** — Quick validation doesn't need delegation
2. **Analysis in subagent** — Heavy reading/parsing goes to agents
3. **User interaction in main** — Confirmations, questions stay in main
4. **Structured return** — Agents return summaries, not raw data
5. **Execution in main** — Final actions (git, file writes) stay in main

---

## Agent Selection Guide

| Agent | Model | Use For |
|-------|-------|---------|
| `context-isolator` | Haiku | Calendar queries, data aggregation, simple analysis |
| `vault-explorer` | Sonnet | Deep codebase search, understanding patterns |
| `system-reviewer` | Sonnet | Component review with checklists |
| `research-expert` | Sonnet | Web research, parallel information gathering |
| `general-purpose` | Sonnet | Complex multi-step tasks |

**Model Selection:**
- **Haiku**: Fast, cheap — use for straightforward analysis with clear rules
- **Sonnet**: Balanced — use for tasks requiring judgment or complex reasoning
- **Opus**: Expensive — reserve for high-stakes decisions or creative work

---

## Structured Result Pattern

When agents return results, use a structured format that main context can parse:

```
FIELD_NAME: value
ANOTHER_FIELD: value

SECTION_NAME:
- item 1
- item 2

REASONING:
Brief explanation

RAW_CONTENT:
[Only if main context needs to display it]
```

**Example from /system:release:**
```
RECOMMENDED_BUMP: MINOR
NEXT_VERSION: 0.6.0

CHANGELOG_SIGNALS:
- Added: 3 items
- Fixed: 2 items
- Breaking: no

COMMIT_SIGNALS:
- Total: 12
- feat: 4
- fix: 6

REASONING:
New features added without breaking changes.
```

This allows main context to:
1. Parse the recommendation
2. Display reasoning to user
3. Act on structured data

---

## Session State for Multi-Step Workflows

When an orchestrator needs to pause (e.g., for user Q&A), maintain state:

### Session Directory Pattern

```
.claude/sessions/YYYY-MM-DD-[topic]/
├── config.json       # Current phase, agent status, paths
├── context.md        # Shared context for all agents
├── round-1/          # Results from first round
│   └── [agent outputs]
├── qa-1/             # Q&A phase results (if needed)
└── synthesis/        # Final synthesis
```

### Config.json Structure

```json
{
  "session_directory": "/full/path/to/session/",
  "created": "ISO timestamp",
  "current_phase": "round-1",
  "mode": "MEDIUM",
  "agents": {
    "analyzer": {"status": "completed", "output": "findings.md"},
    "validator": {"status": "pending"}
  }
}
```

### Resume Protocol

When resuming a paused orchestrator:

```
Task tool:
  resume: [agent_id]
  prompt: |
    SESSION DIRECTORY (USE THIS - DO NOT CREATE NEW):
    /full/path/to/session/

    [User's answer or new context]

    Continue from current phase.
```

**Critical**: Always pass the exact session directory path. Failure causes duplicate directories.

---

## Parallel Agent Spawning

For maximum efficiency, spawn independent agents in a **single message**:

```
// GOOD: All agents spawn in parallel
Task #1: { subagent_type: "system-reviewer", prompt: "Review commands..." }
Task #2: { subagent_type: "system-reviewer", prompt: "Review skills..." }
Task #3: { subagent_type: "system-reviewer", prompt: "Review hooks..." }

// BAD: Sequential spawning
Task #1 → wait → Task #2 → wait → Task #3
```

For background agents, use `run_in_background: true` and poll with `TaskOutput`.

---

## Examples in This Vault

| Command | Pattern | Agents Used |
|---------|---------|-------------|
| `/system:release` | Lightweight orchestrator | 1 context-isolator (Haiku) |
| `/system:review` | Full orchestrator | N system-reviewers (parallel) |
| `/board:advise` | Multi-round orchestrator | 4 advisors + board-chair |

### Lightweight Orchestrator (release)

```
Main Context:
  1. Pre-flight checks (git status, branch, VERSION)
  2. If auto-detect needed → spawn analysis agent
  3. Parse structured result
  4. Present to user, confirm
  5. Execute release

Agent (context-isolator, Haiku):
  - Read changelog [Unreleased]
  - Get commits since tag
  - Count feat:/fix:/BREAKING
  - Return: RECOMMENDED_BUMP, REASONING, etc.
```

### Full Orchestrator (review)

```
Main Context:
  1. Discovery: Count files per area
  2. Determine mode (SMALL/MEDIUM/LARGE)
  3. Create session directory
  4. Spawn agents (parallel or background)
  5. Collect all findings
  6. Cross-reference validation
  7. Synthesize report
  8. Present to user
  9. Apply approved fixes
```

---

## Anti-Patterns

### Don't Delegate These

- **User confirmations** — Keep in main for responsiveness
- **Simple file reads** — 1-3 files isn't worth agent overhead
- **Git operations** — Execute directly, they're fast
- **Error recovery** — Main context should handle failures

### Don't Return These from Agents

- **Raw file contents** — Return summaries/analysis
- **Full search results** — Return filtered/ranked items
- **Unstructured text** — Use structured format for parsing

### Avoid

- **Over-orchestrating** — Simple tasks don't need agents
- **Sequential when parallel works** — Batch independent agents
- **Forgetting session state** — Multi-step workflows need persistence

---

## Integration with Command Design

When creating new commands via `/system:update`:

1. **Estimate data volume** — Will this read many files? Analyze much data?
2. **Identify analysis vs action** — What's heavy analysis vs simple execution?
3. **Choose pattern**:
   - Simple command → Direct execution
   - Data-heavy analysis → Single agent delegation
   - Multi-area analysis → Orchestrator with parallel agents
4. **Design structured return** — What does main context need from agent?
5. **Plan user interaction** — Where do confirmations happen?

---

## Quick Reference: Task Tool Parameters

```
Task tool:
  subagent_type: "context-isolator"  # or vault-explorer, etc.
  description: "Brief description"    # 3-5 words
  prompt: "Detailed instructions"
  model: "haiku"                      # or sonnet, opus
  run_in_background: true             # for async execution
  resume: "agent_id"                  # for resuming paused agent
```

---

## Related Components

- `context-isolator` agent — Lightweight data isolation
- `system-reviewer` agent — Parallel component review
- `/system:review` command — Full orchestrator example
- `/system:release` command — Lightweight orchestrator example
- `/board:advise` command — Multi-round orchestrator example
