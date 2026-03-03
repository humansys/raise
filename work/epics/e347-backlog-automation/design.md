---
epic_id: "E347"
title: "Backlog Automation — Design"
created: "2026-03-03"
---

# Epic Design: Backlog Automation

## Gemba (Current State)

### Affected Surface

| File | Role | Change Needed |
|------|------|---------------|
| `src/rai_cli/adapters/filesystem.py` | FileAdapter — epics only | Add stories, links, comments |
| `src/rai_cli/adapters/protocols.py` | PM adapter protocol | No change (protocol is complete) |
| `src/rai_cli/cli/commands/_resolve.py` | Adapter resolution | Read default from manifest |
| `src/rai_cli/hooks/builtin/backlog.py` | BacklogHook — hardcoded jira | Use adapter default, exact key match |
| `src/rai_cli/session/bundle.py` | Session context assembly | Add live backlog query |
| `src/rai_cli/cli/commands/backlog.py` | CLI commands | Add `sync` command |
| `.raise/manifest.yaml` | Project config | Add `backlog.adapter_default` |
| `src/rai_cli/skills_base/rai-epic-start/` | Skill prompt | Replace manual edit with `rai backlog` |
| `src/rai_cli/skills_base/rai-epic-close/` | Skill prompt | Replace manual edit with `rai backlog` |
| `src/rai_cli/skills_base/rai-story-start/` | Skill prompt | Add `rai backlog` transition |
| `src/rai_cli/skills_base/rai-story-close/` | Skill prompt | Add `rai backlog` transition |

### Data Flow (Target)

```
                    ┌─────────────────────┐
                    │   Consumer Layer    │
                    │ (skills, hooks,     │
                    │  session, human)    │
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │   rai backlog CLI   │
                    │ (single entry point)│
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │  Adapter Resolver   │
                    │ manifest default /  │
                    │ auto-detect / -a    │
                    └───┬────────────┬────┘
                        │            │
              ┌─────────▼──┐   ┌────▼──────────┐
              │ McpJira    │   │ Filesystem    │
              │ Adapter    │   │ PMAdapter     │
              │ (Jira =    │   │ (backlog.md = │
              │  truth)    │   │  truth)       │
              └────────────┘   └───────────────┘
```

### Adapter Resolution (Target)

```python
# Priority order:
1. Explicit -a/--adapter flag  →  use that adapter
2. manifest.yaml backlog.adapter_default  →  use default
3. Exactly 1 adapter registered  →  auto-detect
4. 0 or 2+ without default  →  error with guidance
```

### manifest.yaml Extension

```yaml
# Existing fields unchanged
backlog:
  adapter_default: jira    # or "filesystem"
```

### FileAdapter Stories Model

Current backlog.md has one table (Epics Overview). For stories, two options:

**Option A: Nested in epic scope docs** — stories live in `work/epics/e{N}-{name}/scope.md`, FileAdapter reads those.

**Option B: Stories section in backlog.md** — add a `## Stories` section per epic in backlog.md.

Decision deferred to S347.2 story design.

### Session-Start Integration

```
assemble_context_bundle()
  └── current_work from session-state.yaml (existing)
  └── NEW: if current_work.epic or current_work.story:
        run: rai backlog get {key} --format agent
        merge live status into bundle
        on failure: add warning "backlog unavailable, showing cached state"
```

### BacklogHook Key Resolution (Target)

Current: `summary ~ "S1.2"` (fuzzy JQL) → fragile.

Target: Issues carry work_id in a label or custom field. Resolution by exact match:
- Jira: `labels = "rai:S347.1"` or key stored in scope doc metadata
- File: direct key lookup

Decision deferred to S347.4 story design.

## Work Item Ontology (ADR-043, revised after research + arch review)

**Research:** `work/research/workflow-adapter-patterns/` (9 sources, Azure DevOps, Jira Align, Nango, DDD/ACL)

**Principle:** RaiSE defines STRUCTURE (grammar), teams define CONTENT (vocabulary). The adapter is an Anti-Corruption Layer.

### Fixed (Structure)
- Issues have types → types have workflows → workflows have states
- States have a terminal flag (is work done?)
- Adapter translates between team vocabulary and backend operations

### Configurable (Content)
- Which states exist per issue type
- How states map to backend (Jira transition IDs, file emojis)
- Which states are terminal

### Configuration

```yaml
# .raise/workflows.yaml — ships default, teams override
workflows:
  defaults:
    states: [backlog, in_progress, done]
    terminal: [done]
  story:
    states: [backlog, in_progress, in_review, done]
    terminal: [done]
```

```yaml
# .raise/jira.yaml — adapter mapping (extends existing)
workflow:
  state_mapping:
    backlog: 11
    in_progress: 31
    in_review: 31
    done: 41
```

### Interaction Flow

```
Skill: "rai backlog transition S347.1 in_progress"
        ↓
CLI: validates state exists in workflows.yaml
        ↓
Adapter: translates "in_progress" → Jira transition ID 31
        ↓
Backend: executes

Read (reverse):
Backend: Jira status "In Progress"
        ↓
Adapter: reverse maps → "in_progress" (from jira.yaml)
        ↓
Consumer: sees team vocabulary, not Jira's
```

See `dev/decisions/adr-043-workflow-as-abstraction.md` for full decision and research evidence.

## Key Contracts

### No Protocol Changes
The `ProjectManagementAdapter` protocol is already complete. All 7 stories work within the existing contract. No new methods needed.

### Adapter Default Contract
```python
def resolve_adapter(name: str | None = None) -> ProjectManagementAdapter:
    """
    Resolve order:
    1. name explicitly provided → use it
    2. manifest backlog.adapter_default → use it
    3. exactly 1 registered → auto-detect
    4. else → error
    """
```

### Fail-Fast Contract
When the active adapter cannot respond (MCP timeout, file missing):
- Raise clear error with adapter name and failure reason
- Never cache or queue operations locally
- Never silently fall back to another adapter

## Parking Lot

Items deferred from this epic:
- GitHub Issues adapter — separate epic (RAISE-141)
- Bidirectional sync (Jira ↔ files) — explicitly rejected, one source of truth
- `rai backlog` TUI/dashboard — out of scope
- Automatic backlog.md sync on every write — just `rai backlog sync` command for now
