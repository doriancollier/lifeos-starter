---
name: product-management
description: Product management expertise for requirements, roadmaps, and feature definition. Activates when working on product strategy, writing PRDs, prioritizing features, or creating roadmaps.
---

# Product Management Skill

Domain expertise for product management work across projects like AssetOps and {{company_1_name}} initiatives.

## When This Skill Activates

- Working on product roadmaps or feature planning
- Writing or reviewing product requirements
- Prioritizing features or backlog items
- Defining user stories or acceptance criteria
- Discussing product strategy or competitive positioning
- Creating project plans with milestones

## Core PM Frameworks

### PRD Structure (Product Requirements Document)

A good PRD answers these questions:

```markdown
## Problem Statement
What problem are we solving? Who has this problem? How painful is it?

## Solution Overview
High-level description of what we're building.

## Goals & Success Metrics
- Primary goal: [measurable outcome]
- Key metrics: [how we'll measure success]
- Target: [specific numbers/percentages]

## User Stories
As a [user type], I want to [action] so that [benefit].

## Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | [Specific functionality] | Must Have | |
| FR-2 | [Specific functionality] | Should Have | |

## Non-Functional Requirements
- Performance: [response times, load capacity]
- Security: [authentication, data protection]
- Scalability: [growth expectations]

## Out of Scope
Explicitly list what we're NOT building.

## Dependencies
- [System/team/external dependencies]

## Open Questions
- [Unresolved decisions that need input]

## Timeline & Milestones
| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| Alpha | [date] | [what's delivered] |
| Beta | [date] | [what's delivered] |
| Launch | [date] | [what's delivered] |
```

### User Story Format

**Standard format**:
```
As a [user type],
I want to [action/capability],
So that [benefit/value].

Acceptance Criteria:
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
```

**Example (AssetOps)**:
```
As a vendor,
I want to claim available jobs from a list,
So that I can add work to my schedule.

Acceptance Criteria:
- [ ] Given I'm logged in, when I view available jobs, then I see jobs in my service area
- [ ] Given I select a job, when I click "Claim", then the job is assigned to me
- [ ] Given I claim a job, when another vendor views it, then it shows as unavailable
```

### Prioritization Frameworks

#### MoSCoW Method
| Priority | Meaning | Guidance |
|----------|---------|----------|
| **Must Have** | Critical for launch | Without these, product doesn't work |
| **Should Have** | Important but not critical | Significant value, but can work around |
| **Could Have** | Nice to have | Include if time/resources allow |
| **Won't Have** | Out of scope (this time) | Explicitly excluded |

#### RICE Scoring
```
RICE Score = (Reach × Impact × Confidence) / Effort

- Reach: How many users affected per quarter? (number)
- Impact: How much value per user? (0.25=minimal, 0.5=low, 1=medium, 2=high, 3=massive)
- Confidence: How sure are we? (100%=high, 80%=medium, 50%=low)
- Effort: Person-months to build (1=small, 3=medium, 6=large)
```

#### Impact/Effort Matrix
```
        High Impact
             │
    Quick    │    Big Bets
    Wins     │    (plan carefully)
─────────────┼─────────────
    Fill-ins │    Money Pit
    (if time)│    (avoid)
             │
        Low Impact

← Low Effort ─────── High Effort →
```

### Roadmap Structure

**Time-based roadmap**:
```markdown
## Q1 2026 Roadmap: [Project Name]

### Theme: [Overall focus for the quarter]

### Now (Current Sprint)
| Feature | Owner | Status | Target |
|---------|-------|--------|--------|
| [Feature] | [Name] | In Progress | [Date] |

### Next (1-2 Sprints Out)
| Feature | Priority | Dependencies |
|---------|----------|--------------|
| [Feature] | Must Have | [Deps] |

### Later (This Quarter)
| Feature | Priority | Notes |
|---------|----------|-------|
| [Feature] | Should Have | [Context] |

### Future (Beyond This Quarter)
- [Feature]: [Brief description]
- [Feature]: [Brief description]
```

**Now/Next/Later roadmap** (simpler):
```markdown
## Now (In Progress)
- Feature A - [owner]
- Feature B - [owner]

## Next (Up Next)
- Feature C
- Feature D

## Later (Future)
- Feature E
- Feature F
```

## Quality Criteria

### Good PRD Characteristics
- [ ] Problem is clearly articulated with evidence
- [ ] Success metrics are specific and measurable
- [ ] User stories have acceptance criteria
- [ ] Requirements are prioritized (MoSCoW or similar)
- [ ] Out of scope is explicitly stated
- [ ] Dependencies are identified
- [ ] Open questions are documented

### Good Roadmap Characteristics
- [ ] Tied to business goals/strategy
- [ ] Realistic given team capacity
- [ ] Dependencies are visible
- [ ] Flexibility for changes (not over-specified)
- [ ] Stakeholders can understand it

### Good User Story Characteristics
- [ ] Independent (can be built alone)
- [ ] Negotiable (not a contract)
- [ ] Valuable (delivers user value)
- [ ] Estimable (team can size it)
- [ ] Small (fits in a sprint)
- [ ] Testable (clear acceptance criteria)

## PM Heuristics

### Prioritization
- "If everything is priority 1, nothing is priority 1"
- Ship the smallest thing that delivers value
- Sequence dependencies correctly (blocking items first)
- Protect engineering time from scope creep

### Requirements
- Requirements should be testable, not vague
- "Fast" is not a requirement; "< 200ms response time" is
- Ask "what problem does this solve?" before "what feature do we need?"
- Write acceptance criteria as if you're testing it yourself

### Roadmaps
- Roadmaps are communication tools, not commitments
- Further out = less detailed (don't over-specify the future)
- Update when reality changes (roadmaps are living documents)
- Include "why" not just "what"

### Stakeholder Management
- Engineers need clarity, not flexibility
- Executives need outcomes, not features
- Users need value, not technology

## Integration with Projects

### Products vs Projects

**Products** are ongoing entities (platforms, apps, businesses) that persist over time.
**Projects** are time-bound efforts that advance products.

| Entity | Location | Lifecycle |
|--------|----------|-----------|
| Product | `2-Areas/[Company]/products/[product]/` | Ongoing |
| Project | `1-Projects/Current/[project].md` | Time-bound |

### Product Structure

Each product has its own directory with:
```
2-Areas/[Company]/products/[product]/
├── roadmap.md          # Now/Next/Later roadmap
├── overview.md         # Product vision and context
├── architecture.md     # Technical architecture (if applicable)
└── decisions/          # ADRs and key decisions
```

### Where PM Artifacts Live
- **Product Roadmaps**: `2-Areas/[Company]/products/[product]/roadmap.md`
- **Project PRDs**: `1-Projects/Current/[Project]/prd-[feature].md`
- **User Stories**: In PRD or project file under "User Stories" section
- **Competitive Analysis**: `1-Projects/Current/[Project]/competitive-analysis.md`

### Linking Products to Projects

Projects should reference which product they advance:
```yaml
---
title: "AB-New-Wallet-Reports"
product: "platform"           # Links to {{company_1_name}} Platform product
company: "{{company_1_name}}"
---
```

Use `/roadmap:status` to see all products and their roadmaps across companies.

### Linking to Daily Work
- Reference PM artifacts in daily notes when working on features
- Update project status when milestones are reached
- Link to meeting notes where decisions were made

## When to Use Product-Manager Agent

For heavy document generation, invoke the `product-manager` agent:

- Creating a complete PRD from scratch
- Drafting a multi-quarter roadmap
- Writing comprehensive user stories for a feature
- Conducting competitive analysis with research
- Generating a feature prioritization analysis

The agent handles deep work; this skill provides ongoing guidance.

## Context for {{user_first_name}}'s Projects

### AssetOps
- Property management platform with collaborators
- Key features: Vendor claiming, scheduling, Alfred automation, payments
- Competitor: ServiceTitan (lacks agent support)
- Roadmap priority: Claiming → Scheduling → Lead Uploads → Payments

### {{company_1_name}}
- Generative art platform
- {{user_first_name}} is part-time product consultant
- Focus areas: Collector engagement, analytics
- Key stakeholders: Load from contacts-config.json

### {{company_2_name}}
- Project initiative
- Partnership venture
- Experimental, ship-fast mentality
