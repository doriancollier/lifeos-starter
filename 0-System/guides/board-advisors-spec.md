# Personal Board of Advisors — System Specification (Build Document for AI Agent)

## 1. System Goal

Create a fully functioning “Personal Board of Advisors” inside **Claude Code** that provides {{user_first_name}} with world-class, multi-perspective guidance across all domains of his life:

- Business & career strategy  
- Personal finance & entrepreneurship  
- Health, energy, and sustainability  
- Relationships, family, and parenting  
- Leadership, negotiation, and boundaries  
- Execution, habits, routines, and productivity  

The system should provide **high-quality, multi-perspective debate and synthesis**, leading to final recommendations optimized for {{user_first_name}}’s long-term success in:
- Wealth & business outcomes  
- Strong relationships  
- Health & personal well-being  
- Effective leadership & decision-making  

This system is implemented using **Claude Code**, with two layers:
1. **Skills** = domain expertise  
2. **Agents** = distinct personas / perspectives  

A structured **multi-round debate protocol** ensures each agent responds independently, then critiques the others before the Board Chair synthesizes final guidance.

---

## 2. Architecture Overview

The system has three core components:

1. **Skills Layer (Domain Expertise Modules)**  
2. **Agents Layer (Distinct Perspective Personas)**  
3. **Deliberation Engine (Debate + Synthesis Process)**  

These work together to simulate a real “board of advisors.”

---

## 3. Skills Layer (Domain Expertise Modules)

### Purpose
Skills embody **knowledge** — not personality.  
They represent reusable, context-neutral expertise across key life domains.

### Characteristics
- Implemented using Claude Code **skills** (each in a folder with SKILL.md).
- Skills contain domain reasoning frameworks, constraints, and structured outputs.
- Skills must be **short and efficient**, avoiding large context windows.
- Skills should be **agnostic** about tone, personality, and preference.

### Required Skills (created as `.claude/skills/advisor-*`)
1. Financial  
2. Business Strategy  
3. Operations & Systems  
4. Health & Energy  
5. Relationships  
6. Parenting & Family  
7. Leadership & Boundaries  
8. Success & Execution  
9. Decision Frameworks  
10. Legal Literacy  
11. Librarian / Context Retrieval  

Skills define:
- What the domain *knows*  
- What it *does*  
- What it must *never* do (guardrails)  

---

## 4. Agents Layer (Persona-Based Perspectives)

### Purpose
Agents embody **perspectives, heuristics, and optimization goals** — not domain knowledge.

Each agent:
- Has a distinct worldview  
- Runs in its own context window  
- Uses its own tone and personality  
- Draws upon all Skills for expertise  

### Required Agents
1. **Board Chair (Main Orchestrator)**  
2. **Strategic Operator**  
3. **Relationships Guardian**  
4. **Health Steward**  
5. **Execution Coach**

### Agent Behavior
Agents must:
- Generate short memos (200–350 words max)
- Maintain distinct worldviews
- Use Skills when needed
- Avoid persona cross-contamination  

---

## 5. Deliberation Engine (Multi-Round Debate System)

### Purpose
Simulate a structured, multi-agent debate to produce deep, well-rounded conclusions.

### Debate Rounds

#### Round 1 — Initial Memos
Each agent independently outputs:
- Initial viewpoint  
- Key insights  
- Initial recommendation  
- Risks and opportunities  

#### Round 2 — Critique / Response
Each agent:
- Reads summaries of other agents’ Round 1 memos  
- Updates its stance  
- Highlights conflicts  
- Refines recommendations  

#### Round 3 — Final Stance
Each agent:
- Provides final clarified position  
- States conditions for changing their view  
- Highlights main disagreements  
- Offers actionable suggestions  

### Synthesis (Final Recommendation)
The **Board Chair**:
- Summarizes all agent perspectives  
- Identifies alignment and contradiction  
- Produces a final recommendation  
- Provides concrete next steps  

### Session File Structure

```
.claude/board-sessions/[timestamp-topic]/
  question.md
  config.json
  round-1/
  round-2/
  round-3/
  synthesis/
```

### Number of Rounds
- Default: 3  
- Configurable via `config.json` or user request  

### Efficiency Rules
- Memos must stay short  
- Librarian provides condensed summaries  
- Avoid context bloat  

---

## 6. File & Naming Conventions

### Skills
```
.claude/skills/
  advisor-financial/
  advisor-business-strategy/
  advisor-ops-systems/
  advisor-health-energy/
  advisor-relationships/
  advisor-parenting-family/
  advisor-leadership-boundaries/
  advisor-success-execution/
  advisor-decision-frameworks/
  advisor-legal-literacy/
  advisor-librarian-context/
```

### Agents
```
.claude/agents/
  persona-board-chair.md
  persona-strategic-operator.md
  persona-relationships-guardian.md
  persona-health-steward.md
  persona-execution-coach.md
```

### Sessions
```
.claude/board-sessions/YYYY-MM-DD-topic/
```

---

## 7. Hooks (Optional)

Hooks are **not required** for debate orchestration.

Optional uses:
- Logging  
- Timestamping  
- Session file creation  

Hooks **should not manage rounds**.

---

## 8. Requirements for the AI Agent Building This System

The AI tasked with building this system must:

1. Create the entire directory structure.  
2. Write SKILL.md files for all Skills.  
3. Write persona files for all Agents.  
4. Encode the Deliberation Protocol into the Board Chair persona.  
5. Implement memo formats for each agent.  
6. Implement the Librarian for summarization and retrieval.  
7. Ensure outputs stay short and context-efficient.  
8. Support configurable debate rounds.  
9. Maintain clear separation of Skills (expertise) and Agents (perspective).  
10. Output clean, readable markdown for all generated files.  

This specification contains all required conceptual details.  
Implementation is left to the AI builder.
