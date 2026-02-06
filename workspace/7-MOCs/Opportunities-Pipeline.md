---
title: "Opportunities Pipeline"
type: "moc"
category: "goals-tracking"
created: "2025-12-01"
last_updated: "2026-01-31"
tags: ["moc", "opportunities", "planning", "goals"]
---

# Opportunities Pipeline

> [!ai-context]
> This Map of Content tracks opportunities as they arise. Significant opportunities trigger `/board:advise` for multi-perspective evaluation. Opportunities that pass evaluation can become Projects or inform Goals. Configure your focus filter after completing `/setup:onboard`.

**Last Updated**: 2026-01-31
**Current Focus Filter**: *Not yet configured* — Run `/annual:plan` to set your focus filter

---

## 🔴 Awaiting Evaluation

New opportunities that need to be evaluated against the focus filter. For significant ones, use `/board:advise`.

| Opportunity | Source | Date Captured | Alignment | Action Needed |
|-------------|--------|---------------|-----------|---------------|
| | | | | |

---

## 🟡 Under Consideration

Opportunities being actively explored or deliberated.

| Opportunity | Board Session | Status | Next Step |
|-------------|---------------|--------|-----------|
| | | | |

---

## ✅ Evaluated & Decided

Opportunities that have been fully evaluated with clear decisions.

| Opportunity | Decision | Date | Outcome |
|-------------|----------|------|---------|
| | | | |

---

## 🚫 Declined / Not Aligned

Opportunities explicitly declined (either not aligned with focus filter or decided against).

| Opportunity | Reason | Date | Future Review? |
|-------------|--------|------|----------------|
| | | | |

---

## 📋 Future Exploration (2027+)

Opportunities that are interesting but explicitly "not this year." These are captured so they aren't lost.

| Opportunity | Why Deferred | Captured Date | Revisit When |
|-------------|--------------|---------------|--------------|
| | | | |

---

## 🎯 Focus Filter Check

Before adding a new opportunity to "Under Consideration," check alignment with your focus filter.

> **Note**: Your focus filter is set during `/annual:plan`. It defines 2-3 key themes or pillars that opportunities should align with.

### Quick Decision Matrix

| Alignment | Category | Action |
|-----------|----------|--------|
| High (2-3 pillars) | Priority | Move forward, may need board deliberation |
| Medium (1 pillar) | Consider | Evaluate carefully, likely needs board |
| Low (0 pillars) | Decline | Move to "Not Aligned" or "Future Exploration" |

---

## How Opportunities Flow

```
Capture → Evaluate (Focus Filter)
             ↓
    ┌────────┼────────┐
    ↓        ↓        ↓
  Aligned  Partially  Not Aligned
    ↓      Aligned      ↓
  Consider   ↓        Decline/Defer
    ↓      Board?
    ↓        ↓
 Simple?  /board:advise
    ↓        ↓
 Decide → Decision
    ↓        ↓
┌───┴───┐  ┌─┴──┐
↓       ↓  ↓    ↓
Accept  Pass  Accept  Decline
↓            ↓       ↓
Project      Project  Future/Decline
```

---

## Capturing New Opportunities

**Via `/update`:**
```
/update I got an interesting opportunity: [description]
```
Claude will add to "Awaiting Evaluation" and suggest next steps.

**Via direct edit:**
Add a row to the "Awaiting Evaluation" table with source and date.

**When to use `/board:advise`:**
- Opportunity requires significant time/resource commitment
- Trade-offs across domains (money vs time, work vs family)
- Decision is not obvious from focus filter alone
- High-stakes with long-term implications

---

## Integration

### With Goals
- Opportunities that become projects should link to which goal they support
- Goals may generate opportunities (e.g., "grow personal brand" → speaking opportunity)

### With Projects
- Accepted opportunities become projects in `/1-Projects/`
- Project frontmatter includes `originated_from: "opportunity"`

### With Daily Planning
- `/daily:plan` can optionally surface opportunities awaiting evaluation
- Weekly review includes opportunity pipeline check

---

## Related

- [[2026]] - Current year goals and theme
- [[Life-Events-Timeline]] - Time-based planning view
- [[3-Resources/Board-Sessions/]] - Board deliberation archives
