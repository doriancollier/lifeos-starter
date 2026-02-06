---
description: Convene your Personal Board of Advisors for multi-perspective deliberation on important decisions
argument-hint: [question or decision to deliberate]
allowed-tools: Read, Write, Edit, Grep, Glob, Task, AskUserQuestion
---

# Board Advise Command

Convene the Personal Board of Advisors to provide multi-perspective guidance on important decisions through structured deliberation with interactive Q&A.

## Arguments

- `$ARGUMENTS` - The question or decision to deliberate. Examples:
  - "Should I take on this new consulting project?"
  - "How should I handle the conflict with [person]?"
  - "What's the right balance between  and ?"
  - "Should we expand ?"

## The Board

Your Personal Board of Advisors consists of:

| Advisor | Perspective | Optimization Focus |
|---------|-------------|-------------------|
| **Strategic Operator** | Business & leverage | Wealth, growth, efficiency |
| **Relationships Guardian** | People & trust | Family, relationships, integrity |
| **Health Steward** | Sustainability | Energy, well-being, longevity |
| **Execution Coach** | Action & results | Discipline, habits, follow-through |
| **Board Chair** | Synthesis | Balance, integration, recommendation |

## Deliberation Process

### Step 1: Clarify the Question

If `$ARGUMENTS` is vague or missing, ask clarifying questions:

```markdown
I'd like to help the Board deliberate effectively. Let me clarify:

1. What's the specific decision or question?
2. What's the time pressure? (immediate / this week / flexible)
3. Who are the key stakeholders affected?
4. What makes this decision difficult?
```

Use AskUserQuestion if helpful for quick clarification.

### Step 2: Configure the Session

Ask about deliberation depth:

**Quick Deliberation (1 round)**
- Simple questions with likely alignment
- ~5 minutes, 1 round of advisor memos
- 0-1 Q&A phases
- Best for: validation, gut-checks, minor decisions

**Standard Deliberation (2 rounds)**
- Moderate complexity with trade-offs
- ~10 minutes, 2 rounds with refinement
- 0-1 Q&A phases
- Best for: most decisions, balanced exploration

**Deep Deliberation (3 rounds)**
- High stakes with significant implications
- ~15-20 minutes, full 3-round debate
- 0-2 Q&A phases
- Best for: major life/business decisions

Default to **Standard (2 rounds)** unless user specifies otherwise.

### Step 3: Invoke the Board Chair

Once the question is clear and depth is set, invoke the Board Chair agent to orchestrate:

```
Task tool:
- subagent_type: persona-board-chair
- prompt: |
    BOARD DELIBERATION REQUEST

    Question: [the question]
    Rounds: [1/2/3]
    Context: [any relevant context gathered]
    Session Date: [today's date]

    Please orchestrate the full deliberation:
    1. Create session directory
    2. Gather context from vault
    3. Assess information adequacy (ask user questions if needed)
    4. Run [N] rounds with all advisors
    5. Process Q&A phases between rounds (if questions exist)
    6. Synthesize and deliver final recommendation
```

### Step 3.5: Handling Q&A Phase Pauses (CRITICAL)

If the Board Chair returns with questions for the user and an `agentId`:

1. **Extract the Session Directory** from the agent's response (look for "Session Directory: [path]")
2. **Store the Session Directory** — you'll need it when resuming
3. **Present questions to user** and collect answers
4. **Resume the agent** with the session directory explicitly included:

```
Task tool:
- resume: [agentId from previous response]
- subagent_type: persona-board-chair
- description: Resume Board deliberation Round 2
- prompt: |
    User has provided answers to Q&A Phase [N].

    **SESSION DIRECTORY (USE THIS - DO NOT CREATE NEW):**
    [The exact session directory path from the agent's previous response]

    **User Answers:**
    [Include all user answers here]

    Please continue the deliberation from where you left off.
    Write all subsequent files to the session directory above.
```

**IMPORTANT**: Always pass the session directory explicitly when resuming. Failure to do so may result in the agent creating a duplicate directory with a different name.

### Step 4: Present Results

The Board Chair will:
1. Gather pre-round information if needed
2. Run the multi-round deliberation with Q&A phases
3. Save all memos and Q&A to `workspace/3-Resources/Board-Sessions/[date-topic]/`
4. Produce a synthesized recommendation
5. Present the recommendation with next steps

After the Board Chair returns, offer:
- "Would you like to explore any advisor's perspective in more depth?"
- "Should I add any action items to today's tasks?"
- "Any aspect of the recommendation you'd like to challenge?"

## Deliberation Flow with Q&A and Research

The enhanced deliberation includes interactive Q&A and research phases:

```
Pre-Round Info Gathering (if needed)
    ↓
  Round 1 → [Q&A Phase 1] → [Research Phase 1] → Round 2 → [Q&A Phase 2] → [Research Phase 2] → Round 3
    ↓                                                                                              ↓
                                               Synthesis
```

**Q&A and Research Phases are conditional** — they only run if advisors have questions or research requests.

### What Happens in Q&A Phases

1. **Questions for User**: Advisors can ask for missing information that would materially change their advice
2. **Questions for Other Advisors**: Advisors can ask each other for domain expertise or challenge positions
3. **Conditional Progression**: If no questions exist, the next round begins automatically

### Types of Questions

| Question Type | Example |
|---------------|---------|
| User question (financial) | "What's your monthly discretionary income?" |
| User question (relational) | "How does  feel about this?" |
| User question (health) | "Rate your current burnout level 1-10?" |
| Inter-advisor question | Strategic Operator → Health Steward: "Is this pace sustainable?" |
| Open question | "Has  faced similar decisions before?" |

### What Happens in Research Phases

1. **Research Requests**: Advisors can request external information that would materially improve their advice
2. **Consolidation**: Board Chair consolidates similar requests (max 3 topics per phase)
3. **Research Execution**: Board Chair invokes the research-expert agent for focused investigation
4. **Distribution**: Research findings are shared with all advisors in subsequent rounds

### Types of Research Requests

| Advisor | Example Research Requests |
|---------|--------------------------|
| Strategic Operator | "Current market rates for consulting in this space" |
| Relationships Guardian | "Best practices for communicating difficult decisions to partners" |
| Health Steward | "Recovery time recommendations for burnout" |
| Execution Coach | "Time blocking strategies for multi-project management" |

## Session Storage

All deliberations are stored in:
```
3-Resources/Board-Sessions/YYYY-MM-DD-[topic-slug]/
├── question.md              # Original question
├── config.json              # Session settings
├── context.md               # Relevant vault context
│
├── pre-round/               # Pre-Round 1 info gathering (if needed)
│   └── user-info.md         # User's answers to initial questions
│
├── round-1/                 # Initial advisor memos
│   ├── strategic-operator.md
│   ├── relationships-guardian.md
│   ├── health-steward.md
│   └── execution-coach.md
│
├── qa-1/                    # Post-Round 1 Q&A (if questions existed)
│   ├── questions.md         # Extracted questions
│   ├── user-answers.md      # User's responses
│   ├── summary.md           # Compiled Q&A for next round
│   └── advisor-responses/   # Advisor answers to inter-advisor questions
│       ├── strategic-operator.md
│       ├── relationships-guardian.md
│       ├── health-steward.md
│       └── execution-coach.md
│
├── research-1/              # Post-Round 1 research (if requested)
│   ├── requests.md          # Consolidated research requests
│   ├── research_report.md   # Full research report
│   └── summary.md           # Executive summary for advisors
│
├── round-2/                 # Refined positions (if applicable)
│   └── ...
│
├── qa-2/                    # Post-Round 2 Q&A (if 3-round + questions)
│   └── ...
│
├── research-2/              # Post-Round 2 research (if 3-round + requests)
│   └── ...
│
├── round-3/                 # Final stances (if applicable)
│   └── ...
│
└── synthesis/
    └── recommendation.md    # Board Chair's final synthesis
```

## Example Usage

```
/board:advise Should I accept the  co-founder role?

/board:advise How do I balance time between  work and building ?

/board:advise  wants to drop out of his activity - how should I handle this?

/board:advise I'm feeling burned out but have commitments. What should I do?

/board:advise Should I buy a new car?
```

## When to Use the Board

**Good fit:**
- Major life or career decisions
- Decisions with trade-offs across domains (money vs time, work vs family)
- When you feel stuck between valid options
- High-stakes choices with long-term implications
- Questions where you're missing important information

**Not ideal for:**
- Simple factual questions
- Tasks that need execution, not deliberation
- Emergencies requiring immediate action
- Questions with obvious answers

## Domain Skills Available to Advisors

All advisors can draw on:
- `advisor-financial` — Money, investment, tax
- `advisor-business-strategy` — Business, markets, growth
- `advisor-ops-systems` — Operations, efficiency, automation
- `advisor-health-energy` — Health, energy, sustainability
- `advisor-relationships` — Communication, trust, conflict
- `advisor-parenting-family` — Family, parenting, co-parenting
- `advisor-leadership-boundaries` — Leadership, delegation, boundaries
- `advisor-success-execution` — Goals, habits, productivity
- `advisor-decision-frameworks` — Decision theory, risk, trade-offs
- `advisor-legal-literacy` — Contracts, IP, regulatory awareness
- `advisor-librarian-context` — Vault search and context retrieval

## Framework Integrations

The Board deliberation process now includes these additional frameworks:

### Pre-Mortem Integration

**Before final recommendation**, the Board Chair runs a pre-mortem:

1. **Time Travel**: "It is 12 months from now. This decision has failed spectacularly."
2. **Failure Reasons**: Each advisor identifies 2-3 ways this could fail from their domain
3. **Categorize**: Tigers (real threats), Paper Tigers (apparent threats), Elephants (avoided topics)
4. **Mitigate**: For each Tiger, identify preventive action

Ask: "What would cause this to fail? What are we not discussing?"

### Second-Order Thinking

All advisors must include in their perspective:
- **First order**: What happens immediately?
- **Second order**: What chain reactions follow?
- **Third order**: What compounds over time?

The 10-10-10 rule is applied: How will this feel in 10 minutes, 10 months, 10 years?

### Leverage Analysis

For action-oriented decisions, advisors assess:
- "Is this high-leverage or busy work?"
- "Does this require 's specific knowledge and judgment, or could it be delegated?"
- "Is this building leverage (systems, code, content, relationships) or just trading time for output?"

### Values Alignment Check

Before synthesis, the Board Chair verifies:
- "Does this align with courage?" (Acting despite fear, not avoiding discomfort)
- "Does this align with love?" (Serving those who matter, not just ego)
- "Does this protect what matters?" (Family, health, integrity)

If the recommendation conflicts with core values, the conflict is surfaced explicitly.

## Tips for Better Deliberations

1. **Be specific**: "Should I take this project?" is better than "What should I do about work?"
2. **Include stakes**: "This would mean 20 extra hours/week" helps advisors weigh trade-offs
3. **Name the tension**: "I want growth but I'm exhausted" focuses the discussion
4. **Allow dissent**: The best insights often come from advisor disagreement
5. **Answer questions honestly**: The Q&A phases help advisors give better advice — incomplete information leads to generic recommendations
6. **Expect questions**: If you're asking about a purchase, expect financial questions; if about relationships, expect questions about stakeholders
7. **Research takes time**: If advisors request external research, deliberation may take longer but advice will be better-informed
8. **Research is optional**: Not all deliberations need research — it only happens when advisors identify genuine information gaps
9. **Expect pre-mortem**: Major decisions will include failure analysis before recommendation
10. **Second-order required**: Advisors will consider consequences beyond the immediate
