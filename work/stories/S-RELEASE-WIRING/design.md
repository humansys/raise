---
story: S-RELEASE-WIRING
type: bugfix
complexity: moderate
modules: mod-session, mod-context, mod-cli, mod-governance
---

# Design: S-RELEASE-WIRING — Wire Release into CLI, Session & Skills

## What & Why

**Problem:** S-RELEASE-ONTOLOGY added release as a first-class graph concept (models, parser, builder, tests) but never propagated it to the workflow surface. The CLI, session context, query engine, and skills have zero release awareness. Classic PAT-194 — infrastructure without wiring.

**Value:** Developers and Rai need release context to understand *why* they're working on an epic, what the deadline pressure is, and how the current epic fits into the larger release picture. Without this, the hierarchy stops at epic level and release deadlines are invisible.

## Architectural Context

**Modules affected:**
- `mod-session` (lyr-integration) — bundle assembly, state schema
- `mod-context` (lyr-integration, bc-ontology) — query engine helpers
- `mod-cli` (lyr-orchestration) — new `release` command group
- `mod-governance` (lyr-domain) — no changes needed (parser already exists)
- Skills (7 SKILL.md files) — add release language

**Dependency flow:** `mod-governance` (parser) → `mod-context` (graph/query) → `mod-session` (bundle) → `mod-cli` (commands) → Skills (SKILL.md)

**Key constraint:** Release nodes already exist in the graph. This story wires them into the *consumption* layer, not the *production* layer.

## Approach

Wire release in 3 layers, bottom-up:

1. **Schema + Query** — Add `release` to `CurrentWork`, add `find_release_for()` to query engine
2. **Session Bundle + CLI** — Surface releases in context output, add `rai release list`
3. **Skills** — Add release language to 7 skill SKILL.md files

No new parsers. No new models. No new graph nodes. Pure wiring.

## Components Affected

| Component | File | Change Type |
|-----------|------|-------------|
| `CurrentWork` schema | `schemas/session_state.py` | Modify — add `release` field |
| `CloseInput` | `session/close.py` | Modify — wire `release` through close |
| Session bundle | `session/bundle.py` | Modify — format release in work section |
| Query engine | `context/query.py` | Modify — add `find_release_for()` |
| CLI: release commands | `cli/commands/release.py` | **Create** — `rai release list` |
| CLI: main | `cli/main.py` | Modify — register release_app |
| CLI: validate | `cli/commands/memory.py` | Modify — add release to expected_types |
| 7 x SKILL.md | `.claude/skills/*/SKILL.md` | Modify — add release context |

## Examples

### 1. CurrentWork with release

```python
class CurrentWork(BaseModel):
    release: str = ""   # e.g., "V3.0" or ""
    epic: str = ""
    story: str = ""
    phase: str = ""
    branch: str = ""
```

Session state YAML:
```yaml
current_work:
  release: V3.0
  epic: E19
  story: S19.3
  phase: pending
  branch: epic/e19/v3-product-design
```

### 2. Session bundle output (new line)

```
Release: REL-V3.0 (V3.0 Commercial Launch) — Target: 2026-03-14
Story: S19.3 [pending]
Epic: E19
Branch: epic/e19/v3-product-design
```

The release line appears only if the current epic is part of a release. Uses graph query to resolve.

### 3. find_release_for() query helper

```python
def find_release_for(self, epic_id: str) -> ConceptNode | None:
    """Find the release an epic belongs to via part_of edge."""
    neighbors = self.graph.get_neighbors(
        epic_id, depth=1, edge_types=["part_of"]
    )
    for node in neighbors:
        if node.type == "release":
            return node
    return None
```

Usage in bundle assembly:
```python
# In _format_work_section(), query graph for release
release_node = engine.find_release_for(f"epic-{state.current_work.epic.lower()}")
if release_node:
    target = release_node.metadata.get("target", "")
    name = release_node.metadata.get("name", "")
    lines.insert(0, f"Release: {release_node.metadata.get('release_id', '')} ({name}) — Target: {target}")
```

### 4. `rai release list` output

```
$ rai release list

Releases:

  REL-V2.0  V2.0 Open Core            In Progress  2026-02-15  E18
  REL-V3.0  V3.0 Commercial Launch     Planning     2026-03-14  E19, E20, E21, E22
```

Implementation: Query the memory graph for all nodes of type `"release"`. The graph is the SSoT — `governance/roadmap.md` feeds into it at `rai memory build` time, but commands always read from the graph, never re-parse source documents. If graph doesn't exist, error with hint to run `rai memory build` (same pattern as `rai memory query`).

### 5. Session close YAML with release

```yaml
current_work:
  release: V3.0
  epic: E19
  story: S19.3
  phase: implement
  branch: epic/e19/v3-product-design
```

### 6. Skill output examples

**`/rai-session-start` Ri output:**
```
## Session: 2026-02-13

**Context:** REL-V3.0 → E19 → S19.3, pending, 29 days to release
**Focus:** [goal]
**Signals:** None
```

**`/rai-epic-start` summary:**
```
## Epic Started: E19 V3 Product Design

**Release:** REL-V3.0 (V3.0 Commercial Launch, target 2026-03-14)
**Branch:** epic/e19/v3-product-design
```

**`/rai-epic-close` summary:**
```
## Release Impact

**REL-V3.0 progress:** 1/4 epics complete (E19 ✓)
**Remaining:** E20, E21, E22
```

## Acceptance Criteria

**MUST:**
1. `CurrentWork` schema has `release: str = ""` field with validator
2. `rai session start --context` includes release line when epic has a release
3. `find_release_for(epic_id)` returns the correct release node from graph
4. `rai release list` displays all releases from the memory graph
5. `rai memory validate` includes `"release": 1` in expected_types
6. Session close persists `release` field in session-state.yaml
7. All 7 skills reference releases in their SKILL.md

**SHOULD:**
- Release line omitted gracefully when no graph exists or no release found
- Error messages guide user to `rai memory build` when graph missing

**MUST NOT:**
- Break existing session start/close behavior
- Parse source documents directly — graph is SSoT for all queries
- Add release fields to models that don't need them (e.g., EpicProgress — release is not progress tracking)

## Skill Updates (7 skills)

### `/rai-session-start`
- Step 2 Ri output template: add `REL-{id}` before epic in Context line
- Step 2 signal check: add release deadline pressure (<30 days)

### `/rai-session-close`
- Step 1 current_work template: add `release: V3.0` field
- YAML example: add release to current_work block

### `/rai-epic-start`
- Step 3 scope template: add `**Release:** REL-{id} ({name}, target {date})` line
- Summary template: add release line

### `/rai-epic-design`
- Step 0.5: add query for release context (`rai memory query` with release type)
- Step 1: frame objective in release context (which release does this epic serve?)
- Scope template: add `> Release: REL-{id}` in header

### `/rai-epic-plan`
- Step 1: review release timeline alongside epic design
- Step 5 milestones: relate to release milestones
- Step 6 timeline: map to release deadline

### `/rai-epic-close`
- Step 3 retrospective template: add "Release Impact" section
- Step 6: note release progress after epic completion

### `/rai-story-start`
- Summary template: add `**Release:** REL-{id}` when epic has release
- No process changes — just display context

## Testing Approach

- **Schema:** Unit test that `CurrentWork(release="V3.0")` works, validator coerces None
- **Query:** Unit test with mock graph that `find_release_for("epic-e19")` returns `rel-v3.0`
- **Bundle:** Unit test that release line appears in bundle when graph has release nodes
- **CLI:** Integration test that `rai release list` queries graph and displays releases
- **Validate:** Test that expected_types includes release
- **Close:** Test that release field persists through close cycle
