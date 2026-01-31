# Skill Manager Reference

Detailed documentation for creating and maintaining Claude Code skills.

---

## Skills vs Commands vs Agents

| Component | Invocation | Complexity | Context | Best For |
|-----------|------------|------------|---------|----------|
| **Skills** | Automatic (semantic match) | Multi-file OK | Main conversation | Domain knowledge, workflows, guidelines |
| **Commands** | Manual (`/command`) | Single file | Main conversation | Quick actions, frequent tasks |
| **Agents** | Task tool delegation | Full subprocess | Isolated context | Heavy data ops, parallel work |

**When to create each:**

| Create a... | When... |
|-------------|---------|
| **Skill** | Claude needs specialized knowledge repeatedly; auto-activation preferred |
| **Command** | User explicitly invokes; single-file prompt; explicit control preferred |
| **Agent** | Needs isolated context; heavy data processing; parallel execution |

---

## Writing Effective Descriptions

### Description Formula

```
[What it does]: Extract, analyze, generate, write, review, etc.
[File types/domains]: PDFs, code, tasks, calendar, etc.
[When to use]: Keywords users would mention
```

### Examples

**Bad (won't trigger):**
```yaml
description: Helps with tasks
```

**Good (will trigger):**
```yaml
description: Understand and work with the task priority system used in daily notes. Use when managing tasks, setting priorities, finding blocked items, or moving tasks between days.
```

### Claude Search Optimization (CSO)

**Critical**: Descriptions should contain ONLY triggering conditions — never workflow summaries.

When descriptions summarize the process, Claude may follow the description instead of reading the full skill content.

**Bad (summarizes process):**
```yaml
description: Helps create skills by asking questions, generating templates, and validating output.
```

**Good (triggers only):**
```yaml
description: Create new Claude Code skills. Use when creating skills, discussing SKILL.md files, or asking about skill best practices.
```

---

## Token Efficiency Targets

| Skill Type | Target Words | Reasoning |
|------------|--------------|-----------|
| Getting-started | < 150 | Minimal friction |
| Frequently-loaded | < 200 | Context preservation |
| Standard | < 500 | Balance detail/efficiency |
| Complex (multi-file) | < 500 | Use progressive disclosure |

**Rule**: If SKILL.md exceeds 500 lines, split into reference files.

---

## Degrees of Freedom

Match specificity to task fragility:

| Freedom Level | When to Use | Example |
|---------------|-------------|---------|
| **High** | Flexible decisions, creative work | "Choose an appropriate approach..." |
| **Medium** | Preferred patterns, conventions | "Prefer X, but Y is acceptable if..." |
| **Low** | Fragile operations, strict requirements | "MUST always...", "NEVER..." |

**Discipline skills** need low freedom with explicit loophole-closing.
**Creative skills** need high freedom.

---

## Test-Driven Skill Development (TDD)

**Iron Law**: "No skill without failing test first."

If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

### TDD Mapping

| TDD Phase | Skill Equivalent |
|-----------|------------------|
| **RED** | Run pressure scenarios WITHOUT the skill; document baseline failures |
| **GREEN** | Write minimal skill addressing those specific violations |
| **REFACTOR** | Identify new rationalizations; add explicit counters; re-test |

### Testing by Skill Type

| Skill Type | Testing Approach |
|------------|------------------|
| **Discipline** | Pressure scenarios under combined stress |
| **Technique** | Application and variation scenarios |
| **Pattern** | Recognition and counter-examples |
| **Reference** | Retrieval and gap testing |

### Bulletproofing Discipline Skills

For skills that enforce rules:

1. **State rule clearly** — No ambiguity
2. **Forbid specific workarounds** — List known evasions
3. **Add rationalization table** — Capture excuses from baseline tests
4. **Create red flags checklist** — Warning signs of violation
5. **Include foundational principle** — "Violating letter = violating spirit"

**Example rationalization table:**

| Excuse | Counter |
|--------|---------|
| "Just this once" | No exceptions — consistency is the value |
| "It's faster" | Short-term speed, long-term debt |
| "Nobody will notice" | YOU will notice; integrity matters |

---

## SKILL.md Template (Full)

```markdown
---
name: skill-name
description: Clear, keyword-rich description. Include trigger contexts and keywords users would naturally mention.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill Name

Brief overview of what this skill does and why it exists.

## Vault Location

- **Primary directory**: `/path/to/relevant/files/`
- **Related files**: List important files

## When to Use

This skill activates when:
- Context 1
- Context 2
- User mentions [keywords]

## Core Instructions

### Main Operation
Step-by-step guidance for the primary use case.

### Secondary Operation
Additional capabilities.

## Examples

### Example 1: [Scenario]
**Input**: What user might say
**Output**: What Claude should do

### Example 2: [Scenario]
**Input**: Another scenario
**Output**: Expected behavior

## Integration with Other Skills

- **skill-name**: How this skill relates
- **other-skill**: Integration points

## Common Operations

### Useful Commands
```bash
# Example commands for this skill's domain
```
```

---

## Required Frontmatter

| Field | Max Length | Notes |
|-------|------------|-------|
| `name` | 64 chars | Lowercase, hyphens, must match directory name |
| `description` | 1024 chars | **Critical** — determines when skill activates |
| `allowed-tools` | — | Optional: restricts tool access |
| `model` | — | Optional: override conversation model |

---

## Skill Categories in This Vault

**Core Workflow:** `daily-note`, `task-system`, `task-sync`, `work-logging`

**Calendar:** `calendar-awareness`, `calendar-management`, `birthday-awareness`, `daily-timebox`

**Planning:** `planning-cadence`, `strategic-thinking`, `pre-mortem`, `energy-management`

**People:** `person-context`, `person-file-management`, `meeting-prep`

**Content:** `writing-voice`, `document-generator`, `product-management`

**System:** `inbox-processor`, `project-status`, `goals-tracking`, `skill-manager`

**Advisors:** 11 `advisor-*` skills for Personal Board of Advisors

---

## Maintenance & Troubleshooting

### Skill Review Checklist

- [ ] Description is specific and keyword-rich
- [ ] Name matches directory name
- [ ] SKILL.md under 500 lines (use progressive disclosure)
- [ ] Examples are concrete and helpful
- [ ] Integration with other skills documented
- [ ] No duplicate functionality with other skills
- [ ] Vault paths are current

### Common Issues

**Skill doesn't activate:**
- Description too vague — add more keywords
- Competing skill with better match — make descriptions distinct
- Claude needs restart — exit and restart Claude Code

**Skill has wrong behavior:**
- Instructions unclear — add concrete examples
- Missing context — add vault paths, integration notes
- Too broad — split into focused skills

**Skill is too large:**
- Use progressive disclosure — split into SKILL.md + reference files
- Extract scripts — move to scripts/ directory
- Remove redundancy — link instead of duplicate

### Description Optimization

If a skill isn't activating reliably:

1. **Add domain keywords**: "tasks", "calendar", "PDF", etc.
2. **Add action verbs**: "create", "review", "extract", "manage"
3. **Add trigger phrases**: "Use when...", "Activates when..."
4. **Make it distinct**: Differentiate from similar skills

---

## Slash Command Integration

Skills can have associated slash commands for explicit invocation.

**Location:** `.claude/commands/[namespace]/[name].md`

**Format:**
```markdown
---
description: Brief description
---

Use the skill-name skill to [do something].

[Additional context or parameters]

$ARGUMENTS
```

---

## Advanced Patterns

### Tool Restrictions

```yaml
# Read-only skill
allowed-tools: Read, Grep, Glob

# Data analysis skill
allowed-tools: Bash(python:*), Read, Write

# Calendar skill
allowed-tools: mcp__google-calendar__*
```

### Model Override

```yaml
model: claude-opus-4
```

### Scripts Directory

Bundle utility scripts that Claude can execute:

```
my-skill/
├── SKILL.md
└── scripts/
    ├── validate.py
    └── process.sh
```

Scripts are executed, not read — only output consumes tokens.

---

## Progressive Disclosure Pattern

For complex skills, split content:

1. **SKILL.md** (< 500 words): Overview, quick start, links
2. **REFERENCE.md**: Detailed documentation
3. **EXAMPLES.md**: Comprehensive examples
4. **TEMPLATES.md**: Ready-to-use templates
5. **scripts/**: Utility scripts (executed, not read)

**Link, don't duplicate:**
```markdown
For detailed patterns, see [REFERENCE.md](REFERENCE.md).
```
