---
title: "Personal Board of Advisors Guide"
created: "2025-12-02"
status: "active"
---

# Personal Board of Advisors Guide

Multi-perspective deliberation on important decisions.

## What is the Personal Board?

The Personal Board of Advisors is a system for getting diverse perspectives on important decisions. It simulates having a personal advisory board with different areas of expertise, each optimizing for different outcomes.

## Quick Start

```
/board:advise [your question or decision]
```

**Examples:**
```
/board:advise Should I accept the consulting opportunity?
/board:advise How do I balance {{company_1_name}} and {{company_2_name}}?
/board:advise {{child_name}} wants to quit his activity - how should I handle this?
/board:advise I'm feeling burned out but have commitments. What should I do?
```

## The Advisors

| Advisor | Perspective | Optimizes For |
|---------|-------------|---------------|
| **Strategic Operator** | Business & wealth | Growth, efficiency, leverage |
| **Relationships Guardian** | People & trust | Family, integrity, connection |
| **Health Steward** | Sustainability | Energy, well-being, longevity |
| **Execution Coach** | Action & results | Discipline, habits, follow-through |
| **Board Chair** | Synthesis | Balance, integration, recommendation |

### Advisor Roles in Detail

**Strategic Operator** asks:
- What's the financial upside?
- What's the opportunity cost?
- How does this build long-term wealth?
- What leverage can we create?

**Relationships Guardian** asks:
- How does this affect family?
- What are the relationship costs?
- Are we maintaining trust?
- Who else is impacted?

**Health Steward** asks:
- Is this sustainable?
- What's the energy cost?
- Are we avoiding burnout?
- What's the physical/mental toll?

**Execution Coach** asks:
- Can you actually do this?
- What needs to change?
- Is this aligned with your strengths?
- What's the action plan?

**Board Chair**:
- Orchestrates the deliberation
- Synthesizes perspectives
- Identifies tensions
- Delivers final recommendation

## Deliberation Depth

| Depth | Rounds | Duration | Best For |
|-------|--------|----------|----------|
| **Quick** | 1 | ~5 min | Validation, gut-checks |
| **Standard** | 2 | ~10 min | Most decisions |
| **Deep** | 3 | ~15-20 min | Major life/business decisions |

### Choosing Depth

- **Quick**: "Should I buy this $200 item?"
- **Standard**: "Should I take on this 20-hour/week project?"
- **Deep**: "Should I change careers?"

Default is **Standard (2 rounds)**.

## The Deliberation Process

### Complete Flow

```
Clarify Question
      ↓
Configure Session (depth)
      ↓
Pre-Round Info Gathering (if needed)
      ↓
Round 1 (all advisors)
      ↓
[Q&A Phase 1] ← Questions for you and each other
      ↓
[Research Phase 1] ← External research if requested
      ↓
Round 2 (refined positions)
      ↓
[Q&A Phase 2] ← If 3-round deliberation
      ↓
[Research Phase 2] ← If 3-round deliberation
      ↓
Round 3 (final stances)
      ↓
Synthesis & Recommendation
```

### Interactive Q&A Phases

Advisors can ask questions during deliberation:

**Questions for You:**
```
Strategic Operator: "What's your monthly discretionary income?"
Relationships Guardian: "How does {{partner_name}} feel about this?"
Health Steward: "Rate your current burnout level 1-10?"
```

**Questions for Each Other:**
```
Strategic Operator → Health Steward: "Is this pace sustainable long-term?"
Relationships Guardian → Execution Coach: "How would you handle the conversation with {{partner_name}}?"
```

Q&A phases only run if advisors have questions. Simple deliberations skip them.

### Research Phases

Advisors can request external research:

```
Strategic Operator: "Current market rates for consulting in this space"
Health Steward: "Recovery time recommendations for burnout"
Execution Coach: "Time blocking strategies for multi-project management"
```

Research is consolidated (max 3 topics per phase) and findings are shared with all advisors.

## Personalization

The Board uses your personal profile to customize advice:

### From `2-Areas/Personal/context.md`:
- Your known strengths and weaknesses
- Decision-making patterns to watch for
- Historical patterns (what worked, what didn't)
- Current goals and focus filter

### Example Personalization:

```
Based on your profile, I notice:
- You tend to "wait" on difficult decisions (pattern to watch)
- You sometimes optimize for "nice" over "shrewd"
- Your 2026 focus filter is NFT + Physical + AI

This opportunity scores LOW on focus alignment (0/3 pillars).
```

## Session Storage

All deliberations are saved for reference:

```
3-Resources/Board-Sessions/YYYY-MM-DD-[topic]/
├── question.md              # Original question
├── context.md               # Vault context gathered
├── round-1/                 # Initial advisor memos
│   ├── strategic-operator.md
│   ├── relationships-guardian.md
│   ├── health-steward.md
│   └── execution-coach.md
├── qa-1/                    # Q&A exchange (if occurred)
│   ├── questions.md
│   └── user-answers.md
├── research-1/              # Research (if requested)
│   └── research_report.md
├── round-2/                 # Refined positions
└── synthesis/
    └── recommendation.md    # Final recommendation
```

## Domain Expertise

All advisors can draw on specialized knowledge:

| Domain Skill | Expertise |
|--------------|-----------|
| `advisor-financial` | Money, investing, tax optimization |
| `advisor-business-strategy` | Markets, growth, partnerships |
| `advisor-ops-systems` | Efficiency, automation, scaling |
| `advisor-health-energy` | Health, energy, sustainability |
| `advisor-relationships` | Communication, trust, conflict |
| `advisor-parenting-family` | Parenting, co-parenting, family |
| `advisor-leadership-boundaries` | Leadership, delegation, boundaries |
| `advisor-success-execution` | Goals, habits, productivity |
| `advisor-decision-frameworks` | Decision theory, risk, trade-offs |
| `advisor-legal-literacy` | Contracts, IP, regulatory awareness |
| `advisor-librarian-context` | Vault search, historical context |

## When to Use the Board

### Good Fit

- Major life or career decisions
- Trade-offs across domains (money vs time, work vs family)
- When stuck between valid options
- High-stakes choices with long-term implications
- Questions where you need multiple perspectives

### Not Ideal For

- Simple factual questions
- Tasks needing execution, not deliberation
- Emergencies requiring immediate action
- Questions with obvious answers

## Tips for Better Deliberations

### Frame the Question Well

| Weak | Strong |
|------|--------|
| "What should I do about work?" | "Should I take this 20-hour/week project for $X?" |
| "Help with {{partner_name}}" | "How do I discuss the car purchase with {{partner_name}}?" |
| "I'm stressed" | "I'm working 60 hours/week and feeling burned out. What should change?" |

### Include Context

- Stakes: "This would mean 20 extra hours/week"
- Constraints: "But I'm already committed to X"
- Tension: "I want growth but I'm exhausted"

### Answer Questions Honestly

Q&A phases exist to get better advice. Incomplete information leads to generic recommendations.

### Allow Dissent

The best insights often come from advisor disagreement. Don't dismiss perspectives that feel uncomfortable.

## Example Session

```
User: /board:advise Should I accept a consulting project that pays $5k/month
      but requires 20 hours/week for 6 months?

Board Chair: I'll convene the Board for a Standard (2-round) deliberation.

[Pre-Round Gathering]
- Checks your personal profile
- Notes current commitments
- Loads focus filter (NFT + Physical + AI)

[Round 1]
Strategic Operator: High ROI, but check opportunity cost...
Relationships Guardian: 20 hours = significant family impact...
Health Steward: Currently at 6/10 burnout, adding this risks...
Execution Coach: Can you realistically do this? Let's check calendar...

[Q&A Phase 1]
Strategic Operator → User: "What's your current monthly consulting income?"
Health Steward → User: "How many hours are you working now?"
Relationships Guardian → Execution Coach: "Is there precedent for time-boxing consulting?"

[User Answers]
...

[Round 2 - Refined]
Advisors update positions based on new information...

[Synthesis]
Board Chair: Given your 8/10 burnout level, existing 45-hour weeks, and the
project's LOW alignment with your focus filter, the consensus is to DECLINE
or NEGOTIATE significantly reduced scope (10 hours/week).

Recommended next steps:
1. Counter-offer: $3k/month for 10 hours/week
2. If declined, pass without regret
3. Use this as a filter template for future opportunities
```

## After a Deliberation

The system will ask:
- "Would you like to explore any advisor's perspective in more depth?"
- "Should I add any action items to today's tasks?"
- "Any aspect of the recommendation you'd like to challenge?"

All sessions are saved for future reference in `3-Resources/Board-Sessions/`.

## Troubleshooting

### Duplicate Session Directories

**Problem**: Two session directories are created (e.g., `2025-12-31-topic/` and `2025-12-31-other-topic/`).

**Cause**: When the Board Chair pauses for Q&A and is resumed, the session directory wasn't passed in the resume prompt.

**Prevention**: The system now automatically tracks the session directory. If you manually resume the agent, always include:

```
SESSION DIRECTORY (USE THIS - DO NOT CREATE NEW):
/full/path/to/3-Resources/Board-Sessions/YYYY-MM-DD-topic/
```

**Fix**: Consolidate files manually:
```bash
# Move files from duplicate to original
mv duplicate-dir/* original-dir/
rmdir duplicate-dir
```

### Session State Reference

All session state is stored in `config.json` within the session directory:

```json
{
  "rounds": 3,
  "topic": "topic-name",
  "session_directory": "/full/path/to/session/",
  "created": "timestamp"
}
```

## Related Guides

- [[../components/agents|Agents]] — How persona agents work (including session resumption)
- [[../components/skills|Skills]] — Domain expertise skills
