---
name: advisor-librarian-context
description: Context retrieval expertise for board deliberations. Use when gathering relevant context from the vault, summarizing prior discussions, or retrieving historical information for board sessions.
allowed-tools: Read, Grep, Glob
---

# Librarian & Context Retrieval Skill

Domain expertise for finding, summarizing, and presenting relevant context from the Obsidian vault.

## Purpose

The Librarian skill enables efficient context retrieval for board deliberations:
- Find relevant prior decisions and discussions
- Surface related projects, people, and context
- Summarize lengthy content into digestible briefs
- Connect current questions to historical patterns

## Vault Navigation

### Key Locations
- **Daily Notes**: `4-Daily/YYYY-MM-DD.md` - Tasks, reflections, captures
- **Meetings**: `5-Meetings/YYYY/MM-Month/` - Meeting notes and decisions
- **People**: `6-People/Professional/` and `6-People/Personal/` - Relationship context
- **Projects**: `1-Projects/Current/` - Active work
- **Areas**: `2-Areas/` - Ongoing responsibilities by company
- **Prior Sessions**: `3-Resources/Board-Sessions/` - Past board deliberations

### Search Strategies

**Find mentions of a topic:**
```bash
grep -r "topic" --include="*.md" -l
```

**Find recent discussions:**
```bash
# Recent daily notes
ls -t 4-Daily/*.md | head -14
```

**Find related people:**
```bash
grep -r "\[\[Person Name\]\]" --include="*.md" -l
```

**Find prior board sessions:**
```bash
ls -la "3-Resources/Board-Sessions/"
```

## Summarization Guidelines

When summarizing content for board deliberations:

### Compression Targets
- Full documents → 100-200 word summaries
- Meeting notes → Key decisions + action items
- Prior board sessions → Core recommendation + reasoning
- Daily notes → Relevant tasks and reflections only

### Summary Structure
```markdown
## Context: [Topic]

**Source**: [file path or type]
**Relevance**: [Why this matters to current question]

**Key Points**:
- [Point 1]
- [Point 2]
- [Point 3]

**Notable Quote**: "[Direct quote if impactful]"
```

### What to Include
- Decisions already made on this topic
- Relevant stakeholders mentioned
- Prior commitments or constraints
- Related projects or initiatives
- Emotional or relational context

### What to Exclude
- Routine task lists
- Unrelated captures
- Duplicate information
- Outdated context

## Integration with Board Sessions

### Pre-Deliberation Context Gathering
1. Search for prior discussions on the topic
2. Identify relevant people and relationships
3. Find related projects and commitments
4. Surface prior board session decisions
5. Compile into concise brief

### Context Brief Format
```markdown
## Context Brief: [Question/Topic]

### Prior Decisions
- [Date]: [Decision made]

### Related People
- [[Person]]: [Their relevance]

### Active Projects
- [[Project]]: [Connection to question]

### Historical Pattern
[Any recurring theme or pattern observed]

### Key Constraints
- [Constraint 1]
- [Constraint 2]
```

## Guardrails

This skill must NEVER:
- Include irrelevant context that bloats deliberation
- Miss critical prior decisions on the topic
- Editorialize or interpret beyond summarization
- Expose private information inappropriately
- Create summaries longer than source material

## Output Format

When used in board deliberations, provide:
- Concise context brief (under 300 words)
- Source references for key points
- Explicit "no relevant context found" when applicable
