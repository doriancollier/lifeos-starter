---
name: proactive-suggestions
description: Proactively suggest high-value commands when context matches. Use when user discusses decisions, opportunities, process improvements, working patterns, or system gaps. Activates during planning, reviews, experimentation, and when conversation involves trade-offs, strategy, or repeated friction.
---

# Proactive Suggestions Skill

Claude should actively suggest these commands when context matches. Don't wait for the user to ask.

## Core Principle

High-value commands like `/board:advise`, `/system:learn`, and `/system:update` are underutilized because users don't always know when they're applicable. This skill enables Claude to recognize patterns and proactively offer these tools.

## When to Suggest `/board:advise`

**Trigger conditions:**
- User faces a **one-way door decision** (irreversible or costly to reverse)
- Trade-offs span multiple life domains (money vs time, work vs family, health vs career)
- User expresses uncertainty: "should I", "torn between", "weighing options", "not sure whether"
- Major opportunity evaluation needed (new job, big purchase, relationship decision)
- User seems stuck between valid options after initial discussion
- Decision involves significant stakes and hasn't considered multiple perspectives

**Suggestion phrasing:**
> "This sounds like a multi-dimensional decision with real trade-offs. Would `/board:advise` help you think through it with different perspectives?"

**Don't suggest when:**
- Simple factual questions or two-way door decisions
- User has already decided and needs execution help
- Emergency requiring immediate action
- User explicitly declined board consultation recently

## When to Suggest `/system:learn`

**Trigger conditions:**
- Conversation discovers a **working approach through experimentation**
- Success phrases: "figured out how to", "this worked", "turns out you can", "we got it working"
- Successful interaction with a new tool, API, or system
- User asks "how do I do X" and Claude experiments to find a working answer
- A manual process works well and could be codified
- Pattern emerges that will likely recur

**Suggestion phrasing:**
> "We discovered a working approach for [X]. Should we codify this with `/system:learn` so the system remembers it?"

**Don't suggest when:**
- The approach is already documented in a skill or command
- It was a one-off task unlikely to recur
- The solution is trivial or widely known
- User is in a hurry and learning codification would interrupt flow

## When to Suggest `/system:update`

**Trigger conditions:**
- User identifies a **gap in current processes**
- Gap phrases: "it would be nice if", "we should add", "this process is missing", "I wish Claude could"
- User asks for a new command or capability that doesn't exist
- Feedback on existing workflow that suggests improvement
- Repeated friction with current processes (same issue comes up multiple times)
- User describes a workaround that should be the default behavior

**Suggestion phrasing:**
> "This seems like a process improvement worth formalizing. Should we add it with `/system:update`?"

**Don't suggest when:**
- The capability already exists (point to it instead)
- It's a one-time need
- The user is just venting, not requesting change
- The improvement is trivial (just do it inline)

## Integration with Session Context

The `session-context-loader.py` hook provides deterministic triggers at session start:

| Hook Detection | Suggestion |
|----------------|------------|
| Learning log stale (30+ days) | Suggest `/system:learn` for any discovered patterns |
| Opportunities awaiting evaluation | Suggest `/board:advise` for significant ones |
| Decision language in daily note | Suggest `/board:advise` for deliberation |

This skill provides heuristic triggers during conversation.

## Integration with Coaching

Fire these suggestions **alongside** coaching questions from `.claude/rules/coaching.md`:

| Coaching Question | If Still Unclear | Suggest |
|-------------------|------------------|---------|
| "Is this strategic adjustment or avoidance?" | User remains uncertain | `/board:advise` |
| "What pattern does this belong to?" | New pattern found | `/system:learn` |
| "Does this pass your focus filter?" | Major opportunity | `/board:advise` |
| Process friction identified | Gap confirmed | `/system:update` |

## Timing and Frequency

- **Don't spam**: One suggestion per conversation topic is enough
- **Wait for natural pause**: Suggest after initial discussion, not immediately
- **Respect rejection**: If user declines, don't re-suggest same command in same session
- **Batch when appropriate**: "Given the decision complexity, `/board:advise` might help. Also, we discovered a working pattern for X that `/system:learn` could codify."

## Examples

### Decision Recognition
```
User: "I'm not sure whether to take this consulting gig. It pays well but would eat into family time."

Claude: "This sounds like a trade-off between financial gain and family presence - a classic multi-domain decision.

A few questions first:
- Is this reversible? (Can you exit if it's not working?)
- What's the time commitment?
- How does {{partner_name}} feel about it?

If you'd like a structured multi-perspective view, `/board:advise` can bring in the Strategic Operator (wealth/efficiency), Relationships Guardian (family impact), and other advisors."
```

### Learning Recognition
```
User: "That AppleScript approach worked great for reading contacts."

Claude: "We discovered a working pattern for AppleScript contact integration. Should we codify this with `/system:learn` so the system remembers how to do this in the future? It would create a skill that Claude can automatically use when contact-related tasks come up."
```

### Gap Recognition
```
User: "I keep having to manually check which tasks have due dates coming up."

Claude: "That's a process gap - there should be an easier way to surface upcoming deadlines. Would you like to formalize this with `/system:update`? We could create a command like `/tasks:due` that shows overdue and upcoming tasks."
```

## Related Components

- `.claude/rules/coaching.md` - Coaching questions that integrate with these suggestions
- `.claude/hooks/session-context-loader.py` - Deterministic triggers at session start
- `.claude/commands/board/advise.md` - Board of Advisors deliberation
- `.claude/commands/system/learn.md` - Learning and codification
- `.claude/commands/system/update.md` - Process improvement
