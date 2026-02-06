---
title: "Decision-Making Guide"
type: "guide"
created: "2025-12-30"
---

# Decision-Making Guide

Structured approaches for better decisions.

## Decision Types

### Type 1: One-Way Doors
Irreversible or very costly to reverse. Take time, analyze thoroughly.
- Major career moves
- Large financial commitments
- Relationship decisions
- Health decisions with lasting impact

Use: Full pre-mortem, first principles analysis, Board of Advisors

### Type 2: Two-Way Doors
Easily reversible. Bias toward action, iterate.
- Most daily decisions
- Experiments and tests
- Process changes
- Tool choices

Use: Quick filter, then act

## Decision Process

### Quick Filter (< 5 min)
1. Does this pass my focus filter?
2. Is this a one-way or two-way door?
3. What's the worst case? Can I survive it?
4. Does this build or dilute my moat?

### Full Analysis (for one-way doors)
1. First principles: What are the fundamental truths?
2. Inversion: What would guarantee failure?
3. Pre-mortem: Imagine it failed—why?
4. Second-order: What happens next? And after that?
5. Asymmetry: What's the upside-to-downside ratio?

## Pre-Mortem Process

Before major decisions:
1. Imagine it's 6 months later and this failed spectacularly
2. Write down all the reasons it failed
3. For each reason, identify a mitigation
4. Decide if the mitigated risk is acceptable

## Commands

- `/strategic:decide` - Guided strategic decision
- `/premortem:run` - Run pre-mortem on decision
- `/board:advise` - Multi-perspective deliberation

## System Improvement

When decisions reveal process gaps or new capabilities:

- `/system:learn` - Codify working patterns discovered through experimentation
- `/system:update` - Add or improve processes based on identified gaps

Claude will proactively suggest these when:
- A successful approach is discovered that could be reused
- Friction with current processes suggests improvement needed
- See `.claude/rules/coaching.md` → "Proactive Command Suggestions" for full triggers

## Templates

- `first-principles-decision` - Break down to fundamentals
- `decision-inversion` - Think backwards from failure
- `premortem-individual` - Personal decision pre-mortem
- `strategic-decision-one-way` - Irreversible decisions
- `strategic-decision-two-way` - Reversible decisions
