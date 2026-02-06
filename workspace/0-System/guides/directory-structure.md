---
title: "Directory Structure Philosophy"
created: "2026-02-06"
status: "active"
---

# Directory Structure Philosophy

This guide explains the design principles behind LifeOS's directory structure and how different types of data are organized.

## Design Principles

### 1. Separation of Concerns

Each top-level directory has a single responsibility:

| Directory | Responsibility | Who Uses It |
|-----------|---------------|-------------|
| `workspace/` | User content (Obsidian vault) | Human + Claude |
| `.claude/` | Claude Code extensions | Claude Code |
| `.user/` | User configuration | Both |
| `gateway/` | API server + channels | Node.js server (future) |
| `tasks/` | Background processes | launchd, cron |
| `integrations/` | Data source connectors | Import scripts |
| `extensions/` | User plugins | User customizations |
| `data/` | Imported external data | Read by skills |
| `state/` | Ephemeral runtime | Temporary storage |

### 2. Core vs Extensions Pattern

The system distinguishes between:
- **Core**: Built-in functionality (`.claude/`, `integrations/`, `tasks/`)
- **Extensions**: User-added functionality (`extensions/`)

Extensions mirror core structure:
- `extensions/skills/` mirrors `.claude/skills/`
- `extensions/channels/` mirrors `gateway/src/channels/`
- `extensions/integrations/` mirrors `integrations/`

### 3. Data Lifecycle

Three categories of data with different persistence:

| Category | Location | Git? | Backup? | Ephemeral? |
|----------|----------|------|---------|------------|
| Content | `workspace/` | Yes | Yes | No |
| Imported | `data/` | No | Yes | No |
| Runtime | `state/` | No | No | Yes |

**Why separate data/ and state/?**
- `data/` contains valuable imports (HealthKit, transcripts) that take effort to regenerate
- `state/` contains caches, logs, sessions that can be deleted without loss

### 4. Integration Architecture

Data flows from external sources through importers to storage:

```
External Source → integrations/[name]/importer → data/[name]/
                                    ↓
                         .claude/skills/ reads data
```

Example for HealthKit:
```
integrations/health/
├── SKILL.md              # How Claude uses health data
├── importer.py           # Script to import from Health Auto Export
├── schema.sql            # Database schema
└── config.yaml           # Import settings

data/health/
├── healthkit.db          # Imported data (SQLite)
└── raw/                  # Raw JSON files from Health Auto Export
```

The integration *code* lives in `integrations/`, but the *data* lives in `data/`.

## Full Directory Structure

```
/
├── CLAUDE.md                    # AI instructions (entry point)
├── package.json                 # Node.js project root
│
├── workspace/                   # Obsidian vault (user content)
│   ├── .obsidian/
│   ├── 0-System/                # LifeOS documentation
│   ├── 1-Projects/              # Active work
│   ├── 2-Areas/                 # Ongoing responsibilities
│   ├── 3-Resources/             # Reference materials
│   ├── 4-Daily/                 # Daily notes
│   ├── 5-Meetings/              # Meeting notes
│   ├── 6-People/                # Person files
│   ├── 7-MOCs/                  # Maps of Content
│   └── 8-Scratch/               # Temporary workspace
│
├── .user/                       # User configuration (preserved on upgrade)
│   ├── identity.yaml
│   ├── companies.yaml
│   ├── coaching.yaml
│   ├── integrations.yaml
│   └── ...
│
├── .claude/                     # Claude Code extensions
│   ├── skills/                  # Model-invoked knowledge
│   ├── commands/                # User-invoked actions
│   ├── agents/                  # Spawned subprocesses
│   ├── hooks/                   # Lifecycle automation
│   ├── scripts/                 # Configuration scripts
│   ├── rules/                   # Persistent context (coaching, components)
│   └── upgrade-notes/           # AI guidance for version upgrades
│
├── gateway/                     # Node.js API server (future)
│   └── src/
│       ├── server/              # REST API + WebSocket
│       └── channels/            # Channel adapters (web, telegram, slack)
│
├── tasks/                       # Background tasks
│   └── heartbeat/               # Periodic vault health checks
│       ├── config.yaml
│       ├── HEARTBEAT.md
│       ├── runner.sh
│       └── plist/               # launchd integration
│
├── integrations/                # Data source connectors
│   ├── health/                  # HealthKit integration
│   ├── supernormal/             # Meeting transcripts
│   └── email/                   # Mail.app integration
│
├── extensions/                  # User-added plugins
│   ├── skills/
│   ├── commands/
│   ├── channels/
│   ├── tasks/
│   └── integrations/
│
├── data/                        # Imported external data (gitignored, backed up)
│   ├── health/                  # HealthKit imports
│   ├── meetings/                # Meeting transcripts
│   ├── email/                   # Email cache
│   └── calendar/                # Calendar cache
│
├── state/                       # Runtime state (gitignored, ephemeral)
│   ├── heartbeat/               # Heartbeat state and logs
│   ├── sessions/                # Chat sessions
│   ├── cache/                   # Temporary caches
│   └── logs/                    # Rotating logs
│
└── scripts/                     # Build, install, dev scripts
```

## What Goes Where?

### User Content → workspace/

All Obsidian notes and user content:
- Daily notes, projects, areas, resources
- Meeting notes, person files
- Templates, MOCs

### Claude Extensions → .claude/

Anything that extends Claude Code:
- Skills (knowledge modules)
- Commands (slash commands)
- Agents (autonomous workers)
- Hooks (lifecycle automation)

### Background Processes → tasks/

Scheduled or continuous processes:
- Heartbeat (periodic health checks)
- Cron jobs (scheduled tasks)
- One-shot deferred tasks

### Data Connectors → integrations/

Code that imports from external sources:
- HealthKit importer
- SuperNormal sync
- Email reader

### Imported Data → data/

The actual data pulled from external sources:
- Health databases
- Meeting transcripts
- Cached content

### Ephemeral State → state/

Temporary runtime data:
- Session files
- Caches
- Logs
- Heartbeat run history

### User Plugins → extensions/

User-created additions:
- Custom skills
- Custom commands
- Custom channel adapters

**Extension Loading**: Extensions are synced to `.claude/` via symlinks, making them discoverable by Claude Code while surviving system upgrades.

See `extensions/README.md` for full documentation on creating and managing extensions.

#### Extension Loading Mechanism

```
extensions/skills/my-skill/SKILL.md
        ↓ (symlink via /extensions:sync)
.claude/skills/ext--my-skill/ → extensions/skills/my-skill/
        ↓
Claude Code discovers the skill
```

Key points:
- Extensions live in `extensions/` and are preserved during upgrades
- Symlinks in `.claude/` (prefixed with `ext--`) point to extensions
- `extensions/manifest.json` tracks registered extensions
- Run `/extensions:sync` after adding new extensions or upgrading

## Inspiration

This architecture draws from [OpenClaw](https://github.com/openclaw):
- Gateway pattern for multi-channel support
- Workspace separation from system configuration
- Extension/plugin architecture
- Heartbeat background task pattern

## Related

- [Architecture](../architecture.md) — System layers and information flow
- [Patterns](../patterns.md) — Content placement conventions
- [Versioning](versioning.md) — How upgrades preserve user data
