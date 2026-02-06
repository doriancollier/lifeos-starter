---
name: document-generator
description: Create modern, minimalist printable documents (schedules, checklists, posters). Activates when user asks to create printable documents, charts, routines, flyers, or wall-mounted content.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
---

# Document Generator

Create beautiful, print-ready HTML documents using the LifeOS Design System. Documents are designed for modern, minimalist aesthetics with clean typography, generous white space, and high contrast for excellent print quality.

## When This Skill Activates

- User asks to create a printable document, chart, checklist, schedule, or poster
- User mentions wall-mounted content, routines, or flyers
- User needs documents for {{child_name}} (schedules, chores, routines)
- User wants to generate something "printable" or "print-ready"

## Design System Overview

All documents use the LifeOS Design System (`workspace/3-Resources/Documents/Templates/design-system.css`):

### Typography

**Font Family**: Inter (clean, modern sans-serif)

**Type Scale** (1.25 ratio - Major Third):
| Token | Size | Use For |
|-------|------|---------|
| `--text-xs` | 10px | Captions, fine print |
| `--text-sm` | 13px | Secondary info, table cells |
| `--text-base` | 16px | Body text |
| `--text-md` | 20px | H5, emphasis |
| `--text-lg` | 25px | H4 |
| `--text-xl` | 31px | H3 |
| `--text-2xl` | 39px | H2 |
| `--text-3xl` | 49px | H1 |
| `--text-4xl` | 61px | Display |
| `--text-5xl` | 76px | Hero |

**Poster Scale** (1.333 ratio - for large format, read from 4-20 feet):
| Token | Size | Use For |
|-------|------|---------|
| `--poster-base` | 28px | Body text (readable 4-6 feet) |
| `--poster-md` | 37px | Secondary headings |
| `--poster-lg` | 50px | Section headings |
| `--poster-xl` | 66px | Subtitles |
| `--poster-2xl` | 88px | Main title |
| `--poster-3xl` | 118px | Hero title (readable 15+ feet) |

**Font Weights**:
- `--weight-light` (300): Subtitles, de-emphasized
- `--weight-regular` (400): Body text
- `--weight-medium` (500): Subheadings
- `--weight-semibold` (600): Section headers
- `--weight-bold` (700): Headings
- `--weight-black` (900): Primary titles

### Spacing System (8px base)

| Token | Size | Use For |
|-------|------|---------|
| `--space-0.5` | 4px | Micro gaps |
| `--space-1` | 8px | Tight spacing |
| `--space-1.5` | 12px | Small gaps |
| `--space-2` | 16px | Standard spacing |
| `--space-3` | 24px | Medium spacing |
| `--space-4` | 32px | Large spacing |
| `--space-6` | 48px | Section gaps |
| `--space-8` | 64px | Major divisions |
| `--space-10` | 80px | Page-level |
| `--space-12` | 96px | Maximum |

### Color Palette

**Neutrals** (use primarily for minimalist aesthetic):
- `--color-black`: #000000
- `--color-gray-900`: #171717 (primary text)
- `--color-gray-600`: #525252 (secondary text)
- `--color-gray-500`: #737373 (tertiary text)
- `--color-gray-400`: #a3a3a3 (borders, icons)
- `--color-gray-200`: #e5e5e5 (light borders)
- `--color-gray-100`: #f5f5f5 (backgrounds)
- `--color-gray-50`: #fafafa (subtle backgrounds)
- `--color-white`: #ffffff

**Accent** (use sparingly for emphasis):
- `--color-accent`: #2563eb (blue)

## Document Templates

### 1. Poster / Wall Art (`poster-wall.html`)
**Best for**: Wall-mounted content read from 4-20 feet
**Characteristics**:
- Very large typography (poster scale)
- High contrast black/white
- Minimal content, maximum impact
- Single-page focus

**Use cases**: Routine reminders, motivational posters, simple schedules

### 2. Checklist / Routine (`checklist-routine.html`)
**Best for**: Daily routines, task lists, step-by-step guides
**Characteristics**:
- Large checkboxes for easy marking
- Clear item separation
- Optional time columns
- Designed for repeated daily use

**Use cases**: Morning routine, bedtime routine, chore lists

### 3. Schedule Grid (`schedule-grid.html`)
**Best for**: Weekly/monthly schedules, calendars
**Characteristics**:
- Grid layout with days/times
- Clean cell borders
- Header row emphasis
- Compact but readable

**Use cases**: Weekly activity schedule, class schedule, meal planning

### 4. Reference Document (`reference-dense.html`)
**Best for**: Information-dense reference materials
**Characteristics**:
- Smaller typography (still readable)
- Multi-column layouts
- Tables and lists
- Maximum information density

**Use cases**: Contact lists, quick reference guides, specifications

## Creating Documents

### Step 1: Determine Document Type

Ask yourself:
1. **Viewing distance**: Will it hang on a wall (use poster scale) or be held (use standard scale)?
2. **Content density**: Minimal content (poster) or detailed (reference)?
3. **Interaction**: Will they write on it (checklist) or just read (poster)?
4. **Repeat use**: Daily use (routine) or one-time reference?

### Step 2: Use Appropriate Template

Templates are located in: `workspace/3-Resources/Documents/Templates/`

**Template Selection**:
| Need | Template | Scale |
|------|----------|-------|
| Wall poster (read from distance) | `poster-wall.html` | Poster |
| Daily routine/checklist | `checklist-routine.html` | Standard |
| Weekly schedule | `schedule-grid.html` | Standard |
| Dense reference | `reference-dense.html` | Compact |

### Step 3: Create the Document

1. Copy the appropriate template
2. Save to `workspace/3-Resources/Documents/Printables/[descriptive-name].html`
3. Customize content while preserving structure
4. Preview in browser
5. Print or Save as PDF from Chrome

### Step 4: Verify Single-Page Fit (REQUIRED for single-page documents)

After creating a document intended to fit on one page, **verify it fits** using Playwright:

```javascript
// 1. Navigate to the document
mcp__playwright__browser_navigate({ url: "file:///path/to/document.html" })

// 2. Measure content height
mcp__playwright__browser_evaluate({
  function: `() => {
    const pageEl = document.body.firstElementChild;
    const styles = window.getComputedStyle(pageEl);
    const totalHeight = pageEl.getBoundingClientRect().height;
    const paddingTop = parseFloat(styles.paddingTop);
    const paddingBottom = parseFloat(styles.paddingBottom);
    const innerHeight = totalHeight - paddingTop - paddingBottom;
    // Letter page inner content max: 10 inches = 960px at 96dpi
    return {
      innerHeightPx: Math.round(innerHeight),
      innerHeightInches: (innerHeight / 96).toFixed(2),
      maxHeightPx: 960,
      fitsOnOnePage: innerHeight <= 960,
      overflowPx: innerHeight > 960 ? Math.round(innerHeight - 960) : 0
    };
  }`
})
```

**If `fitsOnOnePage` is false:**
1. Switch to compact spacing (see "Single-Page Compact Layout" section)
2. Re-verify after changes
3. If still overflowing, consider splitting into multiple pages

### Step 5: Print Workflow

1. Open HTML file in Chrome/Edge
2. Press Cmd+P (Mac) or Ctrl+P (Windows)
3. Select "Save as PDF" or your printer
4. Ensure "Background graphics" is checked (for colors)
5. Set margins to "None" or "Minimum" (CSS handles margins)
6. Print

## Available CSS Classes

### Typography
```html
<h1>Heading 1</h1>                          <!-- text-3xl, black -->
<h2>Heading 2</h2>                          <!-- text-2xl, bold -->
<h3>Heading 3</h3>                          <!-- text-xl, semibold -->
<p class="lead">Lead paragraph</p>          <!-- text-lg, light -->
<p>Regular paragraph</p>                    <!-- text-base -->
<p class="small">Small text</p>             <!-- text-sm -->
<span class="caption">Caption</span>        <!-- text-xs -->

<!-- Weight utilities -->
<span class="text-light">Light</span>
<span class="text-regular">Regular</span>
<span class="text-medium">Medium</span>
<span class="text-semibold">Semibold</span>
<span class="text-bold">Bold</span>
<span class="text-black">Black</span>

<!-- Color utilities -->
<span class="text-primary">Primary</span>
<span class="text-secondary">Secondary</span>
<span class="text-tertiary">Tertiary</span>
<span class="text-accent">Accent</span>

<!-- Alignment -->
<p class="text-center">Centered</p>
<p class="text-left">Left</p>
<p class="text-right">Right</p

<!-- Poster scale (for large format) -->
<h1 class="poster-title">Big Title</h1>
<h2 class="poster-subtitle">Subtitle</h2>
<h3 class="poster-heading">Section</h3>
<p class="poster-body">Body text</p>
```

### Layout
```html
<!-- Containers -->
<div class="container">Standard width (8.5in)</div>
<div class="container container-narrow">Narrow (6in)</div>
<div class="container container-wide">Wide (11in)</div>

<!-- Flexbox -->
<div class="flex items-center justify-between gap-2">
  <div>Left</div>
  <div>Right</div>
</div>

<div class="flex flex-col gap-3">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Grid -->
<div class="grid grid-cols-7 gap-1">
  <!-- 7 columns (for weekly schedule) -->
</div>

<div class="grid grid-cols-2 gap-4">
  <!-- 2 columns -->
</div>
```

### Spacing
```html
<!-- Margin -->
<div class="mt-4">Margin top 32px</div>
<div class="mb-2">Margin bottom 16px</div>
<div class="m-3">All margins 24px</div>

<!-- Padding -->
<div class="p-4">Padding 32px</div>
<div class="py-2">Vertical padding 16px</div>
<div class="px-3">Horizontal padding 24px</div>
```

### Components
```html
<!-- Divider -->
<hr class="divider">
<hr class="divider divider-strong">

<!-- Card -->
<div class="card">Card with border</div>
<div class="card-flat">Card with background</div>

<!-- Table -->
<table class="table">
  <thead>
    <tr><th>Header</th></tr>
  </thead>
  <tbody>
    <tr><td>Cell</td></tr>
  </tbody>
</table>

<table class="table table-bordered table-striped">
  <!-- Bordered + striped variant -->
</table>

<!-- Checkbox (printable) -->
<div class="checkbox">
  <span class="checkbox-box"></span>
  <span>Unchecked item</span>
</div>

<div class="checkbox">
  <span class="checkbox-box checked"></span>
  <span>Checked item</span>
</div>

<!-- List -->
<ul class="list">
  <li class="list-item">
    <span class="list-bullet"></span>
    <span>Item content</span>
  </li>
</ul>

<!-- Badge -->
<span class="badge">Default</span>
<span class="badge badge-accent">Accent</span>
```

### Page Sizes
```html
<!-- Letter portrait (default) -->
<div class="page-letter">...</div>

<!-- Letter landscape -->
<div class="page-letter-landscape">...</div>

<!-- A4 -->
<div class="page-a4">...</div>

<!-- Half letter (5.5 x 8.5) -->
<div class="page-half-letter">...</div>
```

### Print Control
```html
<!-- Hide when printing -->
<div class="no-print">Only shows on screen</div>

<!-- Show only when printing -->
<div class="print-only">Only shows in print</div>

<!-- Keep together (avoid page break inside) -->
<div class="keep-together">...</div>
```

### Page Breaks (Multi-Page Documents)
```html
<!-- Method 1: Multiple page divs (recommended) -->
<div class="page">
  <!-- Page 1 content -->
</div>
<div class="page page-break-before">
  <!-- Page 2 content -->
</div>
<div class="page page-break-before">
  <!-- Page 3 content -->
</div>

<!-- Method 2: Insert break between sections -->
<div class="page">
  <section>Week 1 Schedule</section>
  <div class="page-break"></div>
  <section>Week 2 Schedule</section>
  <div class="page-break"></div>
  <section>Week 3 Schedule</section>
</div>

<!-- Method 3: Break after specific element -->
<div class="checklist-section page-break-after">
  <!-- This section will have a page break after it -->
</div>
```

**Page Break Classes:**
| Class | Effect |
|-------|--------|
| `.page-break` | Insert page break (use as empty div) |
| `.page-break-before` | Force break before this element |
| `.page-break-after` | Force break after this element |
| `.keep-together` | Prevent break inside this element |

## Design Principles

### 1. Hierarchy Through Weight & Size
- Use font weight and size to create hierarchy
- Avoid colors for hierarchy (save accent for emphasis only)
- Bigger + bolder = more important

### 2. White Space (Context-Dependent)
- **Multi-page documents**: Use generous spacing (space-3, space-4)
- **Single-page documents**: Use compact spacing (see below)
- Related items close together, unrelated items far apart

### 3. Single-Page Compact Layout (IMPORTANT)

When creating documents intended to fit on one page, use **compact spacing**:

| Element | Standard | Compact (single-page) |
|---------|----------|----------------------|
| Section margins | `space-3` (24px) | `space-2` (16px) |
| Section title margin | `space-1.5` (12px) | `space-1` (8px) |
| List item padding | `space-1` (8px) | `space-0.5` (4px) |
| List line-height | 1.4 | 1.35 |
| Header margin | `space-3` (24px) | `space-2` (16px) |
| Footer margin | `space-4` (32px) | `space-2` (16px) |
| Column gap | `space-4` (32px) | `space-3` (24px) |
| Box padding/margins | `space-2` (16px) | `space-1.5` (12px) |

**Rule of thumb**: For single-page documents with 20+ list items or 5+ sections, default to compact spacing. Standard spacing is reserved for documents with minimal content or multi-page layouts.

**Warning signs that spacing is too generous**:
- Document has more than ~10 inches of content on letter paper (11" - 0.5" margins × 2 = 10" usable)
- Content wraps to second page when printing
- Large blank areas at bottom while content overflows

### 3. Alignment & Grid
- Stick to the grid (8px increments)
- Left-align text for readability
- Center only short elements (titles, badges)

### 4. Restraint
- Limit to 3-5 font sizes per document
- One accent color maximum
- Avoid decorative elements

### 5. Print Optimization
- Test actual print output
- Ensure "Background graphics" enabled for colors
- High contrast (black on white) for legibility

## File Storage

**Templates**: `workspace/3-Resources/Documents/Templates/`
- `design-system.css` - Core design system
- `poster-wall.html` - Large format poster template
- `checklist-routine.html` - Routine/checklist template
- `schedule-grid.html` - Weekly schedule template
- `reference-dense.html` - Dense reference template

**Created Documents**: `workspace/3-Resources/Documents/Printables/`
- Store finalized documents here
- Use descriptive names: `{{child_name}}-Morning-Routine.html`, `Weekly-Chore-Chart.html`

## Example Usage Patterns

### Creating a Morning Routine for {{child_name}}
```
User: "Create a morning routine checklist for {{child_name}}"

1. Use checklist-routine.html template
2. Add time-based items (7:00 - Wake up, 7:15 - Breakfast, etc.)
3. Include checkbox for each item
4. Save as: 3-Resources/Documents/Printables/{{child_name}}-Morning-Routine.html
5. User opens in Chrome, prints
```

### Creating a Weekly Chore Chart
```
User: "Create a weekly chore chart"

1. Use schedule-grid.html template
2. 7-column grid for days
3. Rows for each chore
4. Checkboxes in cells
5. Save as: 3-Resources/Documents/Printables/Weekly-Chore-Chart.html
```

### Creating a Wall Poster
```
User: "Make a poster with {{child_name}}'s after-school routine"

1. Use poster-wall.html template
2. Large poster-title for header
3. Numbered steps with poster-body text
4. Simple, minimal content (5-7 items max)
5. Save as: 3-Resources/Documents/Printables/{{child_name}}-After-School-Poster.html
```

### Creating Multi-Page Documents
```
User: "Create a 4-week schedule for December"

1. Use schedule-grid.html as base
2. Create 4 page divs, each with class="page page-break-before"
3. Each page contains one week's schedule
4. Header on each page shows "Week of: [date]"
5. Save as: 3-Resources/Documents/Printables/December-2025-Schedule.html

Structure:
<div class="page">Week 1</div>
<div class="page page-break-before">Week 2</div>
<div class="page page-break-before">Week 3</div>
<div class="page page-break-before">Week 4</div>
```

### Creating a Document Bundle (Multiple Documents)
```
User: "Create morning routine, bedtime routine, and chore chart in one file"

1. Create separate page divs for each document
2. Use page-break-before on 2nd and 3rd documents
3. Each can use different styling (poster vs checklist)
4. Print all at once, or select specific pages in print dialog
5. Save as: 3-Resources/Documents/Printables/{{child_name}}-Routines-Bundle.html
```
