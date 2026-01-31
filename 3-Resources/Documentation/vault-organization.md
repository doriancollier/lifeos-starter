---
title: "Vault Organization Guide"
type: "documentation"
tags: ["system", "organization", "reference"]
created: "2025-11-24"
modified: "2025-11-24"
---

# Vault Organization Guide

This document explains the organizational principles behind this Obsidian vault and provides guidance on where to place different types of content.

## Organizational Philosophy

This vault uses a hybrid approach combining:

1. **PARA Method** (Projects, Areas, Resources, Archives) - for content type classification
2. **Johnny Decimal** - for numbered directory prefixes ensuring consistent navigation
3. **Time-based Organization** - for daily notes and meetings

The numbered prefixes (1-, 2-, 3-, etc.) ensure directories always appear in a predictable order and prevent folder sprawl.

## Directory Purpose Guide

### 1-Projects/
**Active work with defined end dates and deliverables.**

| Subfolder | Purpose |
|-----------|---------|
| Current/ | Work actively in progress |
| Backlog/ | Planned future initiatives |
| Completed/ | Finished projects (archived for reference) |
| Cancelled/ | Abandoned projects (kept for context) |

**Examples**: {{company_1_name}} Analytics Dashboard, Website Redesign, Q2 Strategy Document

### 2-Areas/
**Ongoing responsibilities with no end date.**

| Subfolder | Purpose |
|-----------|---------|
| {{company_1_name}}/ | {{company_1_name}} company context, processes, team info |
| {{company_2_name}}/ | {{company_2_name}} initiative documentation |
| {{company_3_name}}/ | {{company_3_name}} business operations |
| Personal/ | Family, health, personal development |

**Examples**: Team contacts, company processes, role documentation, family info

### 3-Resources/
**Reference material and supporting content.**

| Subfolder | Purpose |
|-----------|---------|
| Documentation/ | System guides, how-to docs, AI configuration |
| Templates/ | All note templates (daily, meeting, person, project) |
| Archives/ | Inactive content, legacy systems, old companies |
| Data/ | Data files (CSV, JSON, etc.) |
| Files/ | Attachments (PDFs, images, etc.) |

**Examples**: This guide, daily note template, archived Obsidian content

### 4-Daily/
**Time-based capture and daily planning.**

- Files named `YYYY-MM-DD.md`
- Primary capture point for tasks, reflections, ideas
- Links to projects, people, and meetings

### 5-Meetings/
**Meeting notes organized chronologically.**

- Structure: `YYYY/MM-Month/YYYY-MM-DD-meeting-title.md`
- Links to attendees, projects, and action items

### 6-People/
**Relationship management and contact information.**

| Subfolder | Purpose |
|-----------|---------|
| Professional/ | Work relationships (organized by company) |
| Personal/ | Family and personal relationships |

### 7-MOCs/
**Maps of Content for navigation and discovery.**

- Topic-based navigation hubs
- Link collections for major themes
- Entry points into different areas of the vault

## Decision Tree: "Where Does This Go?"

```
Is this a time-bound goal with deliverables?
├── YES → 1-Projects/Current/ (or Backlog/)
└── NO → Is this an ongoing responsibility?
    ├── YES → 2-Areas/[Company or Personal]/
    └── NO → Is this reference material?
        ├── YES → 3-Resources/[appropriate subfolder]
        └── NO → Is this a daily capture?
            ├── YES → 4-Daily/YYYY-MM-DD.md
            └── NO → Is this a meeting note?
                ├── YES → 5-Meetings/YYYY/MM-Month/
                └── NO → Is this about a person?
                    ├── YES → 6-People/[Professional or Personal]/
                    └── NO → 7-MOCs/ (for navigation content)
```

## Key Principles

### 1. One Source of Truth
Never duplicate content. Link to it instead. If information exists in one place, reference it from others using wiki-links.

### 2. Link Liberally
Every note should link to 3-5 related notes minimum. Rich linking enables discovery and maintains context.

### 3. Capture Fast, Organize Later
Daily notes are the primary capture point. Worry about perfect organization during weekly reviews, not during capture.

### 4. Company Context Matters
Always identify the company context ({{company_1_name}}, {{company_2_name}}, EMC, Personal) in work-related notes.

### 5. Flat Over Deep
Avoid deep folder nesting. Use metadata (YAML frontmatter) and links instead of complex folder hierarchies.

## Maintenance Schedule

### Daily
- Create/update daily note
- Capture tasks, ideas, and quick notes

### Weekly
- Process daily notes
- Update active project files
- Review and update MOCs if needed

### Monthly
- Archive completed projects
- Review Areas for outdated content
- Clean up Resources

### Quarterly
- Deep audit of structure
- Archive or delete unused content
- Review and update documentation

## Migration Notes (November 2025)

This vault was reorganized from a legacy structure. Key changes:

1. **Numbered directories** introduced for consistent navigation
2. **Legacy content** archived to `3-Resources/Archives/Legacy-2024-Obsidian/`
3. **Templates consolidated** to single location `3-Resources/Templates/`
4. **Company content** merged into `2-Areas/`
5. **Capture system** archived (daily notes serve as primary capture)

> [!ai-context]
> This vault serves as both a personal knowledge management system and AI agent memory. The organizational structure is designed for both human navigation and AI comprehension. When helping with this vault, always respect the numbered directory structure and content organization rules defined here.
