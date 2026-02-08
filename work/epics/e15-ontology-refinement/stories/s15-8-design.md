---
story_id: "S15.8"
title: "Minimal Agent Config — Graph as Agent Configuration"
epic_ref: "E15 Ontology Graph Refinement"
story_points: 3
complexity: "moderate"
status: "draft"
version: "2.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Feature: Minimal Agent Config — Graph as Agent Configuration

> **Epic**: E15 - Ontology Graph Refinement
> **Complexity**: moderate | **SP**: 3

---

## 1. What & Why

**Problem**: CLAUDE.md (~300 lines) and CLAUDE.local.md (~77 lines) are manually-maintained copies of governance content that already lives in the memory graph (guardrails, principles, architecture, terms). CLAUDE.local.md requires manual edits after every session — the #1 source of maintenance friction. The context bundle works but is too thin (~150 tokens) — deadlines, recent sessions, progress, and governance primes are missing.

**Value**: The memory graph becomes Rai's agent configuration. No duplicate files. CLAUDE.md and CLAUDE.local.md shrink to bootstrap pointers. The context bundle carries everything a session needs — session state AND governance primes — all from the graph. Zero manual file edits between sessions. Platform-agnostic by construction.

---

## 2. Approach

**The graph IS the agent config.** No new files — extend what exists.

The graph already has 22 guardrail nodes, principle nodes, architecture nodes, and term nodes. Tag critical ones with `always_on: true` metadata. The bundle queries them alongside foundational patterns and surfaces them as **governance primes**.

For operational detail (pre-commit config, toolchain commands), the AI queries on demand — just-in-time context, not upfront dump.

**CLAUDE.md** and **CLAUDE.local.md** shrink to bootstrap pointers.

### Components Affected

| Component | Change |
|-----------|--------|
| `CLAUDE.md` | **Rewrite** — ~300 lines → 3 lines (bootstrap pointer) |
| `CLAUDE.local.md` | **Rewrite** — ~77 lines → 2 lines (bootstrap pointer) |
| `src/raise_cli/session/bundle.py` | **Modify** — add governance primes, recent sessions, progress |
| `src/raise_cli/schemas/session_state.py` | **Modify** — add progress model |
| `src/raise_cli/session/close.py` | **Modify** — write progress to state |
| `src/raise_cli/cli/commands/session.py` | **Modify** — accept progress flags |
| `src/raise_cli/context/builder.py` | **Modify** — tag critical nodes with `always_on: true` |
| `.claude/skills/session-start/SKILL.md` | **Modify** — remove agent.md step, document governance primes |
| `.claude/skills/session-close/SKILL.md` | **Modify** — output progress data |

---

## 3. Design Decisions

### D1: What stays in CLAUDE.md?

Pure platform adapter — bootstrap pointer only:

```markdown
# RaiSE Project

Run `/session-start` to load context and governance.
```

3 lines. ALL governance lives in the memory graph, surfaced through the context bundle. Nothing should happen before `/session-start` runs.

**Rationale**: CLAUDE.md is a platform adapter, not a governance carrier. RaiSE owns all governance in its own artifacts, accessible through the graph.

### D2: Graph as agent configuration — governance primes

Same mechanism as behavioral primes (foundational patterns), extended to governance:

```python
def get_governance_primes(project_path: Path) -> list[ConceptNode]:
    """Query graph for nodes with always_on=true metadata."""
    return [
        node for node in graph.iter_concepts()
        if node.metadata.get("always_on") is True
    ]
```

**What gets tagged `always_on: true`:**
- Critical guardrails: MUST-SEC-* (security), MUST-CODE-* (type safety), MUST-DEV-* (workflow)
- Core principles: §1 (Humans Define), §3 (Platform Agnosticism), §7 (Jidoka)
- Git practices: from governance nodes or ADR references

**Bundle output:**
```
# Governance Primes
- MUST-SEC-001: No secrets in code
- MUST-CODE-001: Type annotations on all functions
- §3: Platform Agnosticism — works where Git works
- §7: Lean + Jidoka — stop on defects
```

**On-demand**: For full code standards, toolchain details, directory structure — AI queries `raise memory query "code standards" --types guardrail` or reads files directly when needed.

**Rationale**: Single source of truth (PAT-149). The graph already has the governance. Tagging critical nodes extends an existing mechanism (foundational patterns). No new files.

### D3: How does session-start load governance?

Single-step context loading — the bundle carries everything:

```
Step 1: Load Context Bundle (session state + governance primes)
  uv run raise session start --project "$(pwd)" --context

Step 2: Interpret & Present
```

No Step 1.5. No file reads. The bundle is self-contained.

**Rationale**: Simpler than the previous agent.md approach. One CLI call, one output, one source of truth.

### D4: What expands in the context bundle?

Add to `bundle.py`:

| New section | Source | Tokens |
|-------------|--------|--------|
| Governance primes | Graph (`always_on=true`) | ~80 |
| Recent sessions (last 3) | `sessions/index.jsonl` | ~100 |
| Epic progress (SP, %) | `session-state.yaml` | ~20 |
| Completed epics | `session-state.yaml` | ~20 |

New `SessionState` fields:
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
    completed_epics: list[str] = []  # ["E1", "E2", ...]
```

### D5: How does session-close capture progress?

The session-close skill outputs progress in its state file:

```yaml
# Existing fields...
summary: "..."
current_work: {epic: E15, story: S15.8, ...}
# NEW fields
progress:
  epic: E15
  stories_done: 6
  stories_total: 8
  sp_done: 19
  sp_total: 25
completed_epics: [E1, E2, E3, E4, E7, E8, E9, E11, E12, E13, E14]
```

The skill computes this from epic scope during retrospective. CLI writes it to session-state.yaml.

### D6: Recent sessions — where to read from?

`sessions/index.jsonl` — already exists, append-only. Read last 3-5 entries in `bundle.py`.

```python
def _format_recent_sessions(project_path: Path, limit: int = 3) -> str:
    """Read last N sessions from index.jsonl."""
```

### D7: CLAUDE.local.md — what stays?

```markdown
# RaiSE Project — raise-cli
Run `/session-start` for context.
```

Two lines. Platform adapter tells Claude Code this is a RaiSE project.

### D8: How to tag graph nodes as `always_on`?

In `builder.py`, when building guardrail and principle nodes, set `metadata["always_on"] = True` for critical nodes:

- Guardrails: all `MUST-*` prefixed (mandatory rules)
- Principles: §1, §3, §7 (core safety/quality principles)
- Git: create a `governance` node type entry or tag relevant ADR

**IMPORTANT:** This requires a graph rebuild (`raise memory build`) — same pattern as S15.3 constraint edges.

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
- SES-097: S15.7 design — deterministic session protocol (PAT-187, PAT-188)

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

# Behavioral Primes
- PAT-149: Single source of truth
- PAT-186: Design is not optional
- PAT-187: Code as Gemba
- PAT-188: Deterministic data + inference interpretation

# Coaching
Strengths: rapid prototyping, architectural vision
Growth edge: delegation
Recent corrections:
- SES-096: Over-scoping → explicit design gate

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

---

## 5. Acceptance Criteria

### MUST

- [ ] Context bundle includes governance primes (from graph, `always_on=true`)
- [ ] Context bundle includes recent sessions (last 3), epic progress, completed epics
- [ ] Critical guardrails and principles tagged `always_on: true` in graph builder
- [ ] CLAUDE.md is ≤ 5 lines (bootstrap pointer only)
- [ ] CLAUDE.local.md is ≤ 3 lines (bootstrap pointer)
- [ ] `SessionState` model has `progress` and `completed_epics` fields
- [ ] Session-close writes progress to session-state.yaml
- [ ] Full lifecycle (start → work → close → start) with zero manual file edits
- [ ] Tests pass, >90% coverage on new code
- [ ] Graph rebuild produces nodes with `always_on` metadata

### SHOULD

- [ ] Bundle stays under ~500 tokens total
- [ ] Deadlines populated in developer.yaml (via session-close or manual seed)

### MUST NOT

- Create duplicate governance files (no agent.md — graph is the source)
- Break existing session-start/close CLI interface
- Require hook changes
