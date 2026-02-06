---
description: Show roadmap status for products across organizations
allowed-tools: Read, Glob, Bash
---

# Roadmap Status Dashboard

Show roadmap status for products across organizations.

## Instructions

### Step 1: Identify Products

Products are defined in `workspace/2-Areas/[Company]/products/` directories. Each product has a `roadmap.md` file.

**Known Products:**

| Company | Product | Location |
|---------|---------|----------|
| {{company_1_name}} | (Configure products) | `workspace/2-Areas/{{company_1_name}}/products/` |
| {{company_2_name}} | (Configure products) | `workspace/2-Areas/{{company_2_name}}/products/` |
| {{company_3_name}} | (Configure products) | `workspace/2-Areas/{{company_3_name}}/products/` |

### Step 2: Scan for Product Roadmaps

```bash
find "{{vault_path}}/2-Areas" -name "roadmap.md" -type f 2>/dev/null
```

### Step 3: Read Each Roadmap

For each roadmap found, extract:
- Product name (from parent directory or frontmatter)
- Company (from path)
- Current quarter/phase focus
- Key milestones with status
- Now/Next/Later items

### Step 4: Present Roadmap Dashboard

**Format:**

```markdown
# 🗺️ Roadmap Status Dashboard

*Generated: [current date/time]*

## Summary by Company

### {{company_1_name}}
| Product | Current Focus | Next Milestone | Status |
|---------|---------------|----------------|--------|
| [Product 1] | [Focus] | [Milestone] | 🟢 |
| [Product 2] | [Focus] | [Milestone] | 🟡 |

### {{company_2_name}}
| Product | Current Focus | Next Milestone | Status |
|---------|---------------|----------------|--------|
| [Product 1] | [Focus] | [Milestone] | 🟢 |

## Detailed View

### {{company_1_name}} Platform

**Current Quarter Focus:** [Current focus from roadmap files]

**Now (In Progress):**
- [ ] [Initiatives in progress]

**Next (Up Next):**
- [Planned initiatives]

**Later (Future):**
- [Future initiatives]

**Milestones:**
| Milestone | Target | Status |
|-----------|--------|--------|
| [Milestone 1] | [Date] | [Status] |
| [Milestone 2] | [Date] | [Status] |
```

### Step 5: Offer Actions

After presenting the dashboard, offer:
1. "Would you like to drill into a specific product's roadmap?"
2. "Should I create tasks for any upcoming milestones?"
3. "Any roadmap items that should become projects?"

## Roadmap Status Indicators

| Icon | Meaning |
|------|---------|
| 🟢 | On track |
| 🟡 | Needs attention |
| 🔴 | Blocked/at risk |
| ⏳ | Upcoming |
| ✅ | Complete |

## Integration with Projects

Roadmap items can link to projects:
- `[[AB-New-Wallet-Reports]]` in roadmap → links to project file
- Projects can have `roadmap_item:` in frontmatter to link back

## Creating Product Roadmaps

If a product doesn't have a roadmap yet:

```markdown
---
product: "Product Name"
company: "Company Name"
updated: "YYYY-MM-DD"
quarter: "Q4 2025"
---

# [Product Name] Roadmap

## Current Quarter Focus
[Theme or key objective for this quarter]

## Now (In Progress)
- [ ] Item 1
- [ ] Item 2

## Next (Up Next)
- Item 3
- Item 4

## Later (Future)
- Item 5
- Item 6

## Milestones
| Milestone | Target | Status |
|-----------|--------|--------|
| [Name] | [Date] | [Status] |

## Links
- [[Project 1]]
- [[Project 2]]
```
