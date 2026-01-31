---
description: Create a new song project with structure for lyrics and AI generation
argument-hint: [song-name]
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
---

# Create Song Command

Create a new song project with proper structure for development and eventual library storage.

## Arguments

- `$ARGUMENTS` - The song name/title (e.g., "Summer Vibes", "Wedding Song")

## Workflow

### 1. Parse Input

Extract the song name from arguments. Convert to appropriate formats:
- **Project folder**: `Song-Name` (title case, hyphenated)
- **Song file**: `Song-Name.md`

### 2. Create Project Structure

Create the following in `1-Projects/Current/`:

```
[Song-Name]/
├── _[Song-Name].md      # Project entry point
├── drafts/
│   └── v1-lyrics.md     # Initial lyrics draft
└── prompts/
    └── suno-prompts.md  # AI generation prompts
```

### 3. Create Project Entry File

Create `_[Song-Name].md` with:

```markdown
---
title: "[Song Name]"
status: "current"
company: "Personal"
created: "[today's date]"
type: "project"
tags: ["project", "music", "song", "creative"]
entry_point: true
---

# [Song Name]

> [!ai-context]
> Music project - song in development. When complete, final version moves to [[_Music-Library]].

## Overview

**Style**: [To be defined]
**Tempo**: [To be defined]
**Theme**: [To be defined]

## Status

- [ ] Concept defined
- [ ] Lyrics drafted
- [ ] Style/prompts finalized
- [ ] Generated in Suno
- [ ] Final version selected
- [ ] Added to Music Library

## Files

- [[drafts/v1-lyrics]] - Current lyrics draft
- [[prompts/suno-prompts]] - AI generation prompts

## Notes

[Working notes, ideas, inspiration]

## Related

- [[_Music-Library]] - Final destination when complete
```

### 4. Create Draft Files

**drafts/v1-lyrics.md:**
```markdown
---
title: "[Song Name] - Lyrics v1"
created: "[today's date]"
version: 1
---

# [Song Name] - Lyrics v1

## Song Structure

[Intro]

[Verse 1]

[Pre-Chorus]

[Chorus]

[Verse 2]

[Pre-Chorus]

[Chorus]

[Bridge]

[Final Chorus]

[Outro]

---

## Notes

[Ideas, rhyme schemes, themes to explore]
```

**prompts/suno-prompts.md:**
```markdown
---
title: "[Song Name] - Suno Prompts"
created: "[today's date]"
tool: "Suno v5"
---

# [Song Name] - Suno Prompts

## Primary Style Prompt

```
[Style description - genre, tempo, instruments, vocal style, production notes]
```

## Negative Prompt

```
[What to avoid - e.g., no autotune, no aggressive vocals]
```

## Alternative Prompts

### Variation 1: [Name]
```
[Alternative style]
```

### Variation 2: [Name]
```
[Alternative style]
```

---

## Suno Tips

- Use structure tags in lyrics: [Verse], [Chorus], [Bridge], [Outro]
- For duets: describe vocal personas (e.g., "male baritone and female alto")
- Avoid artist name references (copyright filtering)
- Iterate one variable at a time
- Use Suno Studio for longer songs or stem separation
```

### 5. Add to Music Library Index

Update `3-Resources/Music/_Music-Library.md`:
- Add song to "In Progress" table
- Link to the project

### 6. Confirm Creation

Output:
```
Created song project: [Song Name]

Project: 1-Projects/Current/[Song-Name]/
- Entry: _[Song-Name].md
- Drafts: drafts/v1-lyrics.md
- Prompts: prompts/suno-prompts.md

Added to Music Library index.

Next steps:
1. Define the song concept and style
2. Write lyrics in drafts/v1-lyrics.md
3. Create Suno prompts in prompts/suno-prompts.md
4. Generate and iterate in Suno v5
5. When complete, manually move final version to 3-Resources/Music/Songs/
```

## Example Usage

```
/create:song Wedding Anthem
/create:song Summer in Austin
/create:song {{partner_name}}'s Birthday Song
```

## Notes

- Projects live in `1-Projects/Current/` during active development
- When finished, final song file moves to `3-Resources/Music/Songs/`
- Audio files go to `3-Resources/Music/Audio/`
- The `_Music-Library.md` index tracks all songs
