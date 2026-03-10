---
story_id: "S15.8"
title: "Minimal Agent Config — Graph as Single Source of Truth"
epic_ref: "E15 Ontology Graph Refinement"
story_points: 5
complexity: "moderate"
status: "draft"
version: "3.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Feature: Minimal Agent Config — Graph as Single Source of Truth

> **Epic**: E15 - Ontology Graph Refinement
> **Complexity**: moderate | **SP**: 5

---

## 1. What & Why

**Problem**: Four overlapping sources load before a session starts — CLAUDE.md (~300 lines), CLAUDE.local.md (~77 lines), MEMORY.md (~200 lines), and Rai identity (~200 lines via hook). All are manually-maintained copies of content that already lives in the memory graph. They contradict, drift, and create maintenance tax. The context bundle exists but is too thin to replace them.

**Value**: One channel, one truth. Everything Rai needs flows through the context bundle, sourced from the memory graph. Four files shrink to bootstrap pointers. The quality improvement isn't more information — it's **coherence**. No contradictions, no drift, no staleness. Zero manual file edits between sessions. Platform-agnostic by construction.

---

## 2. Approach

**The graph IS Rai's configuration.** Everything that shapes behavior — governance, patterns, identity — lives as tagged nodes, surfaced as primes through the context bundle.

| Source | Before | After | Mechanism |
|--------|--------|-------|-----------|
| CLAUDE.md | ~300 lines governance | 3 lines bootstrap | Graph → governance primes |
| CLAUDE.local.md | ~77 lines session state | 2 lines bootstrap | CLI → session state in bundle |
| MEMORY.md | ~200 lines pattern copy | **Deleted** | Graph → behavioral primes (already works) |
| Identity hook | ~200 lines loaded by hook | Identity primes in bundle | Graph → identity primes |

**Three prime types in the bundle, one mechanism:**
- **Governance primes** — critical guardrails + principles (`always_on: true`)
- **Behavioral primes** — foundational patterns (`foundational: true`, already works)
- **Identity primes** — Rai's values + boundaries (`always_on: true`)

For operational detail (toolchain, directory structure, full identity), the AI queries on demand — just-in-time context, not upfront dump.

### Components Affected

| Component | Change |
|-----------|--------|
| `CLAUDE.md` | **Rewrite** — ~300 lines → 3 lines bootstrap |
| `CLAUDE.local.md` | **Rewrite** — ~77 lines → 2 lines bootstrap |
| `MEMORY.md` | **Delete** — `rai memory generate` updated to skip creation |
| `src/rai_cli/session/bundle.py` | **Modify** — add governance primes, identity primes, recent sessions, progress |
| `src/rai_cli/schemas/session_state.py` | **Modify** — add EpicProgress model |
| `src/rai_cli/session/close.py` | **Modify** — write progress to state |
| `src/rai_cli/cli/commands/session.py` | **Modify** — accept progress flags |
| `src/rai_cli/context/builder.py` | **Modify** — tag `always_on` on guardrails, principles; add identity node extraction |
| `src/rai_cli/memory/generate.py` | **Modify** — generate minimal MEMORY.md |
| `.claude/skills/session-start/SKILL.md` | **Modify** — document unified bundle |
| `.claude/skills/session-close/SKILL.md` | **Modify** — output progress data |

---

## 3. Design Decisions

### D1: CLAUDE.md — pure bootstrap

```markdown
# RaiSE Project

Run `/session-start` to load context and governance.
```

3 lines. All governance lives in the graph, surfaced through the bundle.

### D2: CLAUDE.local.md — pure bootstrap

```markdown
# RaiSE Project — raise-cli
Run `/session-start` for context.
```

2 lines. Session state comes from the bundle.

### D3: MEMORY.md — eliminated

Delete MEMORY.md entirely. Claude Code works fine without it — no error, just loads nothing from auto-memory. The graph already surfaces patterns as behavioral primes through the bundle.

Update `rai memory generate` to skip MEMORY.md creation. The command can still exist for other purposes but no longer writes to Claude Code's auto-memory path.

**Rationale**: A bootstrap pointer to say "run /session-start" is still muda — the user already knows to run it. No file > empty file.

### D4: Identity as graph primes

Extract Rai's core values and boundaries from `.raise/rai/identity/core.md` during graph build. Create nodes tagged `always_on: true`:

**Values** (from identity/core.md § Values):
- `RAI-VAL-1`: Honesty over agreement — push back on bad ideas
- `RAI-VAL-2`: Simplicity over cleverness — simple solution that works > elegant complex
- `RAI-VAL-3`: Observability over trust — show work, explain reasoning
- `RAI-VAL-4`: Learning over perfection — every session teaches something
- `RAI-VAL-5`: Partnership over service — collaborator, not tool

**Boundaries** (from identity/core.md § Boundaries):
- `RAI-BND-1`: Stop on incoherence, ambiguity, or drift
- `RAI-BND-2`: Ask before expensive operations
- `RAI-BND-3`: Admit uncertainty rather than pretend confidence
- `RAI-BND-4`: Redirect gently when dispersing

Node type: `principle` (identity values are principles for Rai's behavior).

**Implementation**: New `_load_identity()` method in builder. Reads identity/core.md, extracts structured sections (Values, Boundaries), creates nodes with `always_on: true` metadata.

**Bundle output:**
```
# Identity Primes
- RAI-VAL-1: Honesty over agreement
- RAI-VAL-2: Simplicity over cleverness
- RAI-BND-1: Stop on incoherence, ambiguity, or drift
- RAI-BND-2: Ask before expensive operations
```

### D5: Governance primes from graph

Same mechanism as D4. Tag critical guardrails and principles with `always_on: true`:

- All `MUST-*` guardrails (mandatory rules)
- Core principles: §1 (Humans Define), §3 (Platform Agnosticism), §7 (Lean + Jidoka)
- Git practices: tag relevant governance content

```python
def get_always_on_primes(project_path: Path) -> list[ConceptNode]:
    """Query graph for all always_on nodes (governance + identity)."""
    return [
        node for node in graph.iter_concepts()
        if node.metadata.get("always_on") is True
    ]
```

**Bundle output:**
```
# Governance Primes
- MUST-SEC-001: No secrets in code
- MUST-CODE-001: Type annotations on all functions
- §3: Platform Agnosticism
- §7: Lean + Jidoka — stop on defects
- Git: GitLab (glab), v2 branch, conventional commits, Co-Authored-By: Rai
```

**On-demand**: Full code standards, toolchain config, directory structure — query `rai memory query` or read files when needed.

### D6: Unified bundle — one CLI call, everything needed

After S15.8, the bundle has these sections:

```
# Session Context          ← session state (existing)
# Progress                 ← NEW: epic SP, completed epics
# Recent Sessions          ← NEW: last 3 from index.jsonl
# Deadlines                ← existing (needs data in developer.yaml)
# Governance Primes        ← NEW: always_on guardrails + principles
# Identity Primes          ← NEW: always_on values + boundaries
# Behavioral Primes        ← existing (foundational patterns)
# Coaching                 ← existing (when populated)
# Pending                  ← existing
```

One CLI call: `rai session start --project "$(pwd)" --context`
One output: everything the AI needs to start working.

### D7: Session state expansion

```python
class EpicProgress(BaseModel):
    epic: str           # "E15"
    stories_done: int   # 5
    stories_total: int  # 8
    sp_done: int        # 16
    sp_total: int       # 25

class SessionState(BaseModel):
    current_work: CurrentWork
    last_session: LastSession
    pending: PendingItems
    notes: str = ""
    # NEW
    progress: EpicProgress | None = None
    completed_epics: list[str] = []
```

### D8: Session-close captures progress

The session-close skill outputs progress in its state file:

```yaml
progress:
  epic: E15
  stories_done: 6
  stories_total: 8
  sp_done: 19
  sp_total: 25
completed_epics: [E1, E2, E3, E4, E7, E8, E9, E11, E12, E13, E14]
```

Skill computes from epic scope. CLI writes to session-state.yaml.

### D9: Recent sessions from index.jsonl

```python
def _format_recent_sessions(project_path: Path, limit: int = 3) -> str:
    """Read last N sessions from sessions/index.jsonl."""
```

Read last 3 entries, format as one-liners.

### D10: Clear hook — becomes redundant, no changes needed

The hook currently loads Rai identity. After S15.8, identity primes come through the bundle. The hook becomes redundant but stays as-is — removing it is a separate cleanup, not blocking.

---

## 4. Examples

### Context Bundle Output (After S15.8)

```
# Session Context

Developer: Emilio (ri)

Story: S15.8 [implement]
Epic: E15
Branch: epic/e15/ontology-refinement

Progress: E15 — 6/8 stories, 19/25 SP (76%)
Completed: E1, E2, E3, E4, E7, E8, E9, E11, E12, E13, E14

Last: SES-099 (2026-02-08, Emilio) — S15.8 design complete
Recent:
- SES-098: S15.7 implement → review → close (4.1x, PAT-189)
- SES-097: S15.7 design — deterministic session protocol

# Deadlines
F&F: Feb 09 (1 day) — Friends & Family Pre-launch (FLEXIBLE)
Open Core: Feb 15 (7 days) — Public launch

# Governance Primes
- MUST-SEC-001: No secrets in code
- MUST-CODE-001: Type annotations on all functions
- MUST-CODE-002: Ruff linting + formatting
- MUST-TEST-001: >90% coverage, all tests pass
- §1: Humans Define, Machines Execute
- §3: Platform Agnosticism
- §7: Lean + Jidoka — stop on defects
- Git: GitLab (glab), v2 branch, conventional commits, Co-Authored-By: Rai

# Identity Primes
- RAI-VAL-1: Honesty over agreement
- RAI-VAL-2: Simplicity over cleverness
- RAI-BND-1: Stop on incoherence, ambiguity, or drift
- RAI-BND-2: Ask before expensive operations

# Behavioral Primes
- PAT-149: Single source of truth
- PAT-186: Design is not optional
- PAT-187: Code as Gemba
- PAT-188: Deterministic data + inference interpretation

# Coaching
Strengths: rapid prototyping, architectural vision
Growth edge: delegation

# Pending
Next:
- S15.5 query helpers
- S15.6 skill integration
- PyPI publish
```

### Minimal CLAUDE.md (3 lines)

```markdown
# RaiSE Project

Run `/session-start` to load context and governance.
```

### Minimal CLAUDE.local.md (2 lines)

```markdown
# RaiSE Project — raise-cli
Run `/session-start` for context.
```

### MEMORY.md — Deleted

No file. Claude Code loads nothing from auto-memory. Bundle carries everything.

---

## 5. Acceptance Criteria

### MUST

- [ ] Context bundle includes governance primes (from graph, `always_on=true`)
- [ ] Context bundle includes identity primes (values + boundaries from graph)
- [ ] Context bundle includes recent sessions (last 3) and epic progress
- [ ] Critical guardrails, principles, and identity values tagged `always_on: true` in builder
- [ ] CLAUDE.md ≤ 5 lines (bootstrap pointer)
- [ ] CLAUDE.local.md ≤ 3 lines (bootstrap pointer)
- [ ] MEMORY.md deleted (no auto-memory file; `rai memory generate` updated)
- [ ] `SessionState` model has `progress` and `completed_epics` fields
- [ ] Session-close writes progress to session-state.yaml
- [ ] Full lifecycle (start → work → close → start) with zero manual file edits
- [ ] Tests pass, >90% coverage on new code
- [ ] Graph rebuild produces nodes with `always_on` metadata

### SHOULD

- [ ] Bundle stays under ~600 tokens total
- [ ] Deadlines populated in developer.yaml
- [ ] Clear hook noted as redundant (cleanup in follow-up)

### MUST NOT

- Create duplicate governance or identity files
- Break existing session-start/close CLI interface
- Modify the clear hook (redundancy is noted, not acted on)
