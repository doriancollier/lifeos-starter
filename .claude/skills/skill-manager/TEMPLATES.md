# Skill Templates

Ready-to-use templates for creating new Claude Code skills.

## Template 1: Simple Skill

For focused, single-purpose skills (< 300 lines).

```markdown
---
name: my-skill
description: [What it does]. Use when [trigger context 1], [trigger context 2], or when the user mentions [keywords].
---

# My Skill Name

Brief description of what this skill does and why.

## Vault Location

- **Primary directory**: `/path/to/relevant/files/`

## When to Use

This skill activates when:
- User asks about [topic]
- Working with [file type/domain]
- User mentions [keywords]

## Instructions

### Main Operation

1. First step
2. Second step
3. Third step

### Common Patterns

**Pattern 1:**
```
Example code or format
```

**Pattern 2:**
```
Another example
```

## Examples

### Example 1
**User says**: "Help me with [scenario]"
**Claude does**: [Expected behavior]

### Example 2
**User says**: "[Another scenario]"
**Claude does**: [Expected behavior]

## Integration

- Use **other-skill** for related functionality
```

---

## Template 2: Multi-File Skill

For complex skills with extensive documentation (> 300 lines).

### SKILL.md (Main File)

```markdown
---
name: complex-skill
description: [Comprehensive description with multiple capabilities and keywords].
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Complex Skill Name

Overview paragraph explaining the skill's purpose and scope.

> **Note**: For detailed reference, see [REFERENCE.md](REFERENCE.md). For examples, see [EXAMPLES.md](EXAMPLES.md).

## Quick Start

### Most Common Use Case

Minimal instructions to get started quickly.

```bash
# Quick command example
```

### Second Common Use Case

Brief instructions for alternative use.

## Core Concepts

### Concept 1

Brief explanation (details in REFERENCE.md).

### Concept 2

Brief explanation (details in REFERENCE.md).

## When to Use

- Scenario 1
- Scenario 2
- User mentions [keywords]

## Utility Scripts

Run validation:
```bash
python scripts/validate.py input
```

Run processing:
```bash
python scripts/process.py --input file.txt
```

## Additional Resources

- **Full Reference**: [REFERENCE.md](REFERENCE.md)
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **Patterns**: [PATTERNS.md](PATTERNS.md)

## Integration

- Relates to **skill-a** for [purpose]
- Relates to **skill-b** for [purpose]
```

### REFERENCE.md (Detailed Documentation)

```markdown
# [Skill Name] Reference

Complete reference documentation for [skill name].

## API Reference

### Function/Format 1

**Purpose**: What this does

**Syntax**:
```
format or syntax
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param1 | string | Yes | What it does |
| param2 | number | No | Optional feature |

**Example**:
```
concrete example
```

### Function/Format 2

[Same structure]

## Configuration

### Option 1

**Default**: value
**Description**: What this controls

### Option 2

[Same structure]

## Troubleshooting

### Issue 1

**Symptom**: What user sees
**Cause**: Why it happens
**Solution**: How to fix

### Issue 2

[Same structure]
```

### EXAMPLES.md (Usage Patterns)

```markdown
# [Skill Name] Examples

Real-world usage examples for [skill name].

## Basic Examples

### Example 1: [Scenario Name]

**Context**: When this applies

**Input**:
```
user input or file content
```

**Process**:
1. What Claude does first
2. What Claude does second
3. Result

**Output**:
```
expected output
```

### Example 2: [Another Scenario]

[Same structure]

## Advanced Examples

### Example 3: [Complex Scenario]

**Context**: Advanced use case

**Input**:
```
complex input
```

**Process**:
Step-by-step breakdown

**Output**:
```
complex output
```

## Edge Cases

### Edge Case 1: [Description]

What happens in unusual situations.
```

---

## Template 3: Workflow Skill

For skills that guide multi-step processes.

```markdown
---
name: workflow-skill
description: Guide [workflow type] from start to finish. Use when [starting condition], during [process], or when user asks about [workflow name].
---

# Workflow Skill Name

Guides the complete [workflow] process.

## Workflow Overview

```
Start → Phase 1 → Phase 2 → Phase 3 → Complete
         ↓          ↓          ↓
    [Output 1]  [Output 2]  [Output 3]
```

## Phase 1: [Name]

### Prerequisites

- Requirement 1
- Requirement 2

### Steps

1. **First step**: Details
2. **Second step**: Details
3. **Validation**: How to know it worked

### Outputs

- [ ] Output 1 created
- [ ] Output 2 ready

## Phase 2: [Name]

### Prerequisites

- Phase 1 complete
- Additional requirements

### Steps

1. Step details
2. Step details

### Outputs

- [ ] Outputs from this phase

## Phase 3: [Name]

[Same structure]

## Complete Checklist

At the end of the workflow:

- [ ] All phases complete
- [ ] Final outputs generated
- [ ] Quality verified

## Common Issues

### Issue 1

**When**: During Phase X
**Solution**: How to resolve

### Issue 2

[Same structure]

## Related Workflows

- **workflow-a**: Use before this workflow
- **workflow-b**: Use after this workflow
```

---

## Template 4: Domain Knowledge Skill

For skills that teach Claude about a specific domain.

```markdown
---
name: domain-skill
description: Expert knowledge for [domain]. Use when working with [domain], analyzing [domain content], or when user asks about [domain topics].
---

# Domain Skill Name

Expert knowledge for [domain area].

## Domain Overview

Brief introduction to the domain.

### Key Concepts

| Concept | Definition |
|---------|------------|
| Term 1 | What it means |
| Term 2 | What it means |
| Term 3 | What it means |

### Domain Structure

```
High-level component
├── Sub-component 1
│   ├── Detail A
│   └── Detail B
└── Sub-component 2
    ├── Detail C
    └── Detail D
```

## Core Knowledge

### Topic 1

Detailed explanation of topic 1.

**Key points**:
- Point A
- Point B
- Point C

### Topic 2

Detailed explanation of topic 2.

### Topic 3

[Same structure]

## Best Practices

### Practice 1

Why and how to do this.

### Practice 2

Why and how to do this.

## Common Mistakes

### Mistake 1

What to avoid and why.

### Mistake 2

What to avoid and why.

## Applying Knowledge

### Scenario 1

How to apply domain knowledge in specific situation.

### Scenario 2

[Same structure]

## Resources

- External reference 1
- External reference 2
```

---

## Template 5: Integration Skill

For skills that connect with external systems (calendars, APIs, etc.).

```markdown
---
name: integration-skill
description: Integrate with [system]. Use when accessing [system], syncing [data type], or when user mentions [system] operations.
allowed-tools: mcp__system-name__*, Read, Write
---

# Integration Skill Name

Manages integration with [external system].

## Connection Details

- **System**: [System name]
- **MCP Tools**: `mcp__system-name__*`
- **Authentication**: [How auth works]

## Available Operations

### Operation 1: [Name]

**Tool**: `mcp__system-name__operation-name`

**Purpose**: What this does

**Parameters**:
```json
{
  "param1": "value",
  "param2": "value"
}
```

**Example**:
```json
// Input
{ "query": "example" }

// Output
{ "result": "example result" }
```

### Operation 2: [Name]

[Same structure]

## Common Workflows

### Workflow 1: [Name]

1. Call operation A
2. Process result
3. Call operation B

### Workflow 2: [Name]

[Same structure]

## Error Handling

### Error 1: [Type]

**Cause**: Why this happens
**Solution**: How to handle

### Error 2: [Type]

[Same structure]

## Rate Limits & Constraints

- Constraint 1
- Constraint 2

## Data Format

### Input Format

```json
{
  "structure": "example"
}
```

### Output Format

```json
{
  "response": "example"
}
```
```

---

## Description Formula

Use this formula for effective descriptions:

```
[Capability verbs]: Create, review, analyze, extract, manage, guide, etc.
[Domain nouns]: tasks, calendar, PDFs, code, meetings, etc.
[Trigger phrases]: Use when..., Activates when..., For questions about...
[Keywords]: Words users would naturally say
```

**Example construction:**

```yaml
# Components
Capabilities: Create, review, maintain
Domain: Claude Code skills
Triggers: creating new skills, auditing existing skills
Keywords: skill development, SKILL.md, skill best practices

# Combined
description: Create, review, and maintain Claude Code skills. Use when creating new skills, auditing existing skills, understanding skill vs command vs agent patterns, or when the user mentions skill development, SKILL.md files, or skill best practices.
```

---

## Template 6: Discipline Skill (TDD-Based)

For skills that enforce rules, standards, or processes. Uses bulletproofing pattern from superpowers.

```markdown
---
name: discipline-skill
description: Enforce [standard/rule]. Use when [working on X], [reviewing Y], or when consistency with [standard] is required.
---

# Discipline Skill Name

Enforces [standard/rule] across all relevant work.

> **Iron Rule**: [Core principle in one sentence]

## When to Use

This skill activates when:
- Working on [relevant domain]
- Reviewing [relevant artifacts]
- User mentions [standard keywords]

## The Rule

**[Rule Name]**: [Clear, unambiguous statement of the rule]

## Forbidden Workarounds

Do NOT:
- [Specific evasion 1]
- [Specific evasion 2]
- [Specific evasion 3]

## Rationalization Table

| Excuse | Counter |
|--------|---------|
| "Just this once" | No exceptions — consistency is the value |
| "It's faster" | Short-term speed creates long-term debt |
| "Nobody will notice" | YOU will notice; integrity matters |
| "It's not that important" | Small violations enable large ones |

## Red Flags Checklist

Warning signs that the rule is being violated:
- [ ] [Red flag 1]
- [ ] [Red flag 2]
- [ ] [Red flag 3]

## Correct Approach

### Step 1: [First compliance step]

[Clear instructions]

### Step 2: [Second compliance step]

[Clear instructions]

## Examples

### Correct Example
```
[Example of compliant behavior]
```

### Incorrect Example (DO NOT DO THIS)
```
[Example of non-compliant behavior]
```

## Foundational Principle

**Violating the letter = violating the spirit.**

The rule exists for [reason]. Any attempt to technically comply while undermining the purpose is still a violation.
```

---

## TDD Methodology for Skill Development

Based on superpowers/writing-skills: "No skill without failing test first."

### Phase 1: RED (Document Baseline Failures)

Before writing the skill:

1. **Run pressure scenarios WITHOUT the skill**
2. **Document what Claude does wrong**
3. **Capture rationalizations Claude uses**

```markdown
## Baseline Test Results

**Scenario**: [Description of test case]

**Without skill, Claude**:
- [Failure 1]
- [Failure 2]

**Rationalizations observed**:
- "[Excuse 1]"
- "[Excuse 2]"
```

### Phase 2: GREEN (Write Minimal Skill)

1. **Address ONLY the specific failures** from baseline tests
2. **Keep it minimal** — don't over-engineer
3. **Verify compliance WITH skill present**

```markdown
## Post-Skill Test Results

**Same scenario**, now with skill:
- [x] Failure 1 now handled correctly
- [x] Failure 2 now handled correctly
```

### Phase 3: REFACTOR (Bulletproof)

1. **Identify new rationalizations** that emerge
2. **Add explicit counters** to the skill
3. **Re-test until bulletproof**

```markdown
## Iteration 2

**New rationalization observed**: "[New excuse]"
**Counter added**: "[Explicit prohibition]"
**Re-test result**: Pass
```

### Testing by Skill Type

| Skill Type | Testing Approach |
|------------|------------------|
| **Discipline** | Pressure scenarios under combined stress |
| **Technique** | Application and variation scenarios |
| **Pattern** | Recognition and counter-examples |
| **Reference** | Retrieval and gap testing |

---

## Checklist for New Skills

Before finalizing a skill:

**Structure:**
- [ ] Name is lowercase with hyphens
- [ ] Name matches directory name
- [ ] SKILL.md is < 500 lines (or use progressive disclosure)

**Description (Critical):**
- [ ] Description is < 1024 characters
- [ ] Description includes keywords users would say
- [ ] Description includes "Use when..." triggers
- [ ] Description does NOT summarize workflow (CSO)

**Content:**
- [ ] Examples are concrete and realistic
- [ ] Integration with other skills documented
- [ ] Vault paths are absolute (for this vault)
- [ ] Token efficiency: < 500 words for standard skills

**TDD (for discipline skills):**
- [ ] Baseline test performed WITHOUT skill
- [ ] Failures documented
- [ ] Minimal skill written to address failures
- [ ] Post-skill test confirms fix
- [ ] Rationalizations have explicit counters

**Distribution:**
- [ ] Added to CLAUDE.md skills table
- [ ] Validated with `python scripts/validate_skill.py`
