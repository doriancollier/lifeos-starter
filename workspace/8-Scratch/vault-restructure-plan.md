# Vault Restructure Migration Plan

**Goal**: Move Obsidian vault content to `workspace/` subdirectory to enable a web app at root level while keeping everything in one git repository.

## Target Structure

```
life-os-starter/
├── package.json              # Web app
├── tsconfig.json
├── src/                      # Web app source
├── dist/                     # Build output (gitignored)
├── node_modules/             # Dependencies (gitignored)
│
├── CLAUDE.md                 # Claude Code config (stays at root)
├── CLAUDE.template.md
├── README.md
├── .gitignore
│
├── .claude/                  # Claude Code extensions (stays at root)
│   ├── settings.json
│   ├── skills/
│   ├── commands/
│   ├── hooks/
│   ├── agents/
│   └── rules/
│
├── .user/                    # User config (stays at root)
│   ├── identity.yaml
│   ├── companies.yaml
│   └── ...
│
└── workspace/                # Obsidian vault (NEW LOCATION)
    ├── .obsidian/            # Obsidian config
    ├── 0-Inbox/
    ├── 0-System/
    ├── 1-Projects/
    ├── 2-Areas/
    ├── 3-Resources/
    ├── 4-Daily/
    ├── 5-Meetings/
    ├── 6-People/
    ├── 7-MOCs/
    └── 8-Scratch/
```

## Migration Steps

### Phase 1: Preparation

- [ ] Create full backup (git commit + zip archive)
- [ ] Document current Obsidian settings
- [ ] Close Obsidian

### Phase 2: Directory Structure

- [ ] Create `workspace/` directory
- [ ] Move all vault content directories:
  - `0-Inbox/` → `workspace/0-Inbox/`
  - `0-System/` → `workspace/0-System/`
  - `1-Projects/` → `workspace/1-Projects/`
  - `2-Areas/` → `workspace/2-Areas/`
  - `3-Resources/` → `workspace/3-Resources/`
  - `4-Daily/` → `workspace/4-Daily/`
  - `5-Meetings/` → `workspace/5-Meetings/`
  - `6-People/` → `workspace/6-People/`
  - `7-MOCs/` → `workspace/7-MOCs/`
  - `8-Scratch/` → `workspace/8-Scratch/`
  - `.obsidian/` → `workspace/.obsidian/`

### Phase 3: Hook Updates (13 files)

All hooks use this pattern:
```python
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)
```

**New pattern** (add `workspace/` subdirectory):
```python
PROJECT_ROOT = os.environ.get("PROJECT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or os.path.join(PROJECT_ROOT, "workspace")
```

**Files to update:**

| File | Type |
|------|------|
| `.claude/hooks/directory-guard.py` | Python |
| `.claude/hooks/task-sync-detector.py` | Python |
| `.claude/hooks/table-format-validator.py` | Python |
| `.claude/hooks/reminders-session-sync.py` | Python |
| `.claude/hooks/task-format-validator.py` | Python |
| `.claude/hooks/session-context-loader.py` | Python |
| `.claude/hooks/health-session-sync.py` | Python |
| `.claude/hooks/reminders-task-detector.py` | Python |
| `.claude/hooks/frontmatter-validator.py` | Python |
| `.claude/hooks/git-task-sync-detector.sh` | Bash |
| `.claude/hooks/auto-git-backup.sh` | Bash |
| `.claude/hooks/changelog-populator.py` | Python |
| `.claude/scripts/health_sync.py` | Python |

### Phase 4: CLAUDE.md Updates

Update directory structure documentation:

**Before:**
```
/
├── 0-Inbox/
├── 0-System/
...
```

**After:**
```
/
├── workspace/            # Obsidian vault
│   ├── 0-Inbox/
│   ├── 0-System/
│   ...
├── src/                  # Web app
├── .claude/              # Claude Code config
...
```

Update all path references like:
- `4-Daily/*.md` → `workspace/4-Daily/*.md`
- `2-Areas/Personal/context.md` → `workspace/2-Areas/Personal/context.md`
- `0-System/README.md` → `workspace/0-System/README.md`

**Files:**
- `CLAUDE.md`
- `CLAUDE.template.md`

### Phase 5: Skills & Commands (122 files)

Most references are documentation/examples, not code paths. Categories:

**A. Path references in prose** (documentation, examples)
- Update for accuracy but not functionally critical
- Example: "See `0-System/guides/...`" → "See `workspace/0-System/guides/...`"

**B. Actual code paths** (grep patterns, glob patterns)
- Functionally critical, must update
- Example: `Grep pattern in 4-Daily/` → `workspace/4-Daily/`

**Key files with code paths:**
- `.claude/skills/daily-note/SKILL.md`
- `.claude/skills/vault-task-system/SKILL.md`
- `.claude/skills/vault-task-sync/SKILL.md`
- `.claude/skills/meeting-prep/SKILL.md`
- `.claude/skills/person-context/SKILL.md`
- `.claude/skills/work-logging/SKILL.md`
- `.claude/commands/daily/plan.md`
- `.claude/commands/vault-tasks/due.md`
- `.claude/agents/vault-explorer.md`
- `.claude/agents/task-reviewer.md`

### Phase 6: .gitignore Updates

Add:
```gitignore
# Node.js
node_modules/
dist/
.next/
.turbo/

# Build artifacts
*.tsbuildinfo
.cache/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
```

### Phase 7: Obsidian Configuration

1. Open Obsidian
2. "Open folder as vault" → select `workspace/`
3. Verify plugins, themes, settings preserved
4. Test that daily notes, search, graph work

### Phase 8: Web App Scaffold

```bash
cd /Users/doriancollier/Keep/life-os-starter
npm init -y
npm install @anthropic-ai/claude-agent-sdk typescript
npx tsc --init
```

Create `src/index.ts`:
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const WORKSPACE_PATH = "./workspace";

// Example: Query the vault
async function main() {
  const result = await query({
    prompt: "What are today's A-priority tasks?",
    options: {
      cwd: WORKSPACE_PATH,
      allowedTools: ["Read", "Grep", "Glob"],
    }
  });

  for await (const message of result) {
    console.log(message);
  }
}

main();
```

### Phase 9: Verification

- [ ] All hooks run without error
- [ ] `/daily:plan` works
- [ ] Task validation works
- [ ] Obsidian opens correctly from `workspace/`
- [ ] Web app can read vault files
- [ ] Git status clean (no untracked node_modules)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Lost files during move | Full backup before starting |
| Broken Obsidian links | Links are relative, should still work |
| Hook failures | Test each hook individually after update |
| Missed path references | Grep for old paths, fix incrementally |

## Rollback Plan

If issues arise:
1. `git checkout .` to restore all files
2. Move `workspace/*` back to root
3. Delete `workspace/` directory

## Time Estimate

| Phase | Effort |
|-------|--------|
| Phase 1-2 (Structure) | Low |
| Phase 3 (Hooks) | Medium |
| Phase 4 (CLAUDE.md) | Low |
| Phase 5 (Skills/Commands) | High (many files) |
| Phase 6-9 (Finalize) | Low |

## Decision Points

1. **VAULT_ROOT strategy**: Environment variable vs hardcoded `workspace/`?
   - Recommend: Support both (env var with `workspace/` default)

2. **Web framework**: What to use for the web interface?
   - Options: Next.js, Express + React, Fastify + Vue, etc.
   - Defer until structure is in place

3. **Obsidian vault location**: Some users may want flexibility
   - Consider: Config file option for vault subdirectory name?
