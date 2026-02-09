# Epic E16: Incremental Coherence - Scope

> **Status:** IN PROGRESS
> Branch: `epic/e16/incremental-coherence`
> Created: 2026-02-08
> Target: Post-F&F

---

## Objective

Prevent architecture documentation and graph drift through small-batch updates integrated into the story lifecycle, with full discovery as a validation safety net.

**Value proposition:** Every story leaves the architecture map accurate. Drift never accumulates. Future sessions always work from truth, not stale snapshots.

---

## Architectural Context

**Modules affected:**

| Module | Domain | Layer | Role in Epic |
|--------|--------|-------|--------------|
| `mod-context` | bc-ontology | Integration | Graph diffing, change set generation |
| `mod-discovery` | bc-discovery | Domain | Validation via full discovery rerun |
| `mod-memory` | bc-ontology | Integration | Build command enhancement |
| `mod-cli` | bc-tooling | Orchestration | New commands, story-close integration |

**Cross-domain:** Epic spans bc-ontology and bc-discovery — justified because coherence requires comparing graph (ontology) against code reality (discovery).

**Key constraints from graph:**
- MUST: Type hints, Pydantic models, >90% coverage (all standard guardrails)
- Architecture: Engine/content separation, deterministic CLI + inference skill (PAT-200)

---

## Stories (4 planned)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S16.1 | Graph Diff Engine | M | Pending | Compare old vs new unified graph, emit structured change set (added/removed/modified nodes and edges) |
| S16.2 | Deterministic Doc Updater | S | Pending | Auto-update factual frontmatter in module docs from code analysis (imports, public API, components) |
| S16.3 | AI Doc Regeneration | M | Pending | Subagent regenerates narrative sections in affected docs when structural changes detected |
| S16.4 | Lifecycle Integration | S | Pending | Wire coherence check into story-close (Step 1.75), add discovery-as-validation command |

**Total:** 4 stories, ~2S + 2M

---

## In Scope

**MUST:**
- Graph diffing: compare two graph snapshots, produce structured change set
- Deterministic frontmatter update for module docs (depends_on, depended_by, entry_points, public_api, components)
- Story-close integration point (Step 1.75, after existing structural drift check)
- HITL gate: human reviews all doc changes before commit
- Full discovery as validation audit (verify incremental state)

**SHOULD:**
- AI subagent for narrative section regeneration (high-level docs, module purpose updates)
- Change set includes categorized impact (frontmatter-only vs structural vs architectural)
- `raise coherence check` CLI command for ad-hoc use outside lifecycle

---

## Out of Scope (defer to parking lot)

- **Drift detector calibration** (SES-118) → Separate item, complements but doesn't block
- **Real-time/watch-mode detection** → Post-V3, no current need
- **Cross-project coherence** → V3 scope (multi-project Rai)
- **Auto-commit without human review** → Violates HITL principle
- **High-level doc restructuring** (bounded context boundaries, layer redesign) → Human-only decisions

---

## Architecture

### Two-Layer Design (ADR-025)

```
Story work changes code
         │
         ▼
┌─────────────────────────┐
│   Layer 1: CLI          │  Deterministic
│   (raise memory build   │
│    --diff)              │
│                         │
│   Input: old graph +    │
│          new sources    │
│   Output: GraphDiff     │
│     - added nodes/edges │
│     - removed           │
│     - modified          │
│     - impact category   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Frontmatter-only?     │──yes──▶ Auto-update module docs
│                         │         (deterministic, no review)
└────────┬────────────────┘
         │ no (structural changes)
         ▼
┌─────────────────────────┐
│   Layer 2: Skill        │  Inference
│   (subagent)            │
│                         │
│   Input: GraphDiff +    │
│          affected docs  │
│   Output: Updated docs  │
│          (human reviews) │
└────────┬────────────────┘
         │
         ▼
    HITL review
         │
         ▼
    Commit with story
```

### Graph Diff Data Model

```python
class NodeChange(BaseModel):
    node_id: str
    change_type: Literal["added", "removed", "modified"]
    old_value: ConceptNode | None
    new_value: ConceptNode | None
    changed_fields: list[str]  # For modified: which fields changed

class EdgeChange(BaseModel):
    source: str
    target: str
    edge_type: str
    change_type: Literal["added", "removed", "modified"]

class GraphDiff(BaseModel):
    node_changes: list[NodeChange]
    edge_changes: list[EdgeChange]
    impact: Literal["none", "frontmatter", "structural", "architectural"]
    affected_modules: list[str]
    summary: str  # Human-readable one-liner
```

### Lifecycle Integration

```
story-close (existing):
  Step 1:   Verify feature ready
  Step 1.5: Check structural drift (existing)
  Step 1.75: COHERENCE CHECK (NEW)           ◄━━━━
             │
             ├─ rebuild graph
             ├─ diff against previous
             ├─ if frontmatter changes: auto-update docs
             ├─ if structural changes: flag for subagent
             ├─ human reviews changes
             └─ commit doc updates with story
  Step 2:   Identify parent branch
  ...
```

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Pydantic models for all data structures
- [ ] Unit tests passing (>90% coverage)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] Graph diff produces accurate change sets on real raise-commons data
- [ ] Module doc frontmatter auto-updates correctly from code changes
- [ ] Story-close coherence step triggers on structural changes
- [ ] Full discovery validates incremental state (no regression)
- [ ] Architecture docs updated for new modules/capabilities
- [ ] Epic retrospective done
- [ ] Merged to v2

---

## Dependencies

```
S16.1 Graph Diff Engine (foundation)
  │
  ├──▶ S16.2 Deterministic Doc Updater
  │
  └──▶ S16.3 AI Doc Regeneration
              │
              ▼
        S16.4 Lifecycle Integration (needs S16.1 + S16.2, optionally S16.3)
```

S16.2 and S16.3 can be parallel after S16.1 completes.
S16.4 requires S16.1 + S16.2 at minimum. S16.3 can be wired in later.

**External blockers:** None.

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Graph diffing + AI doc regen | ADR-025 | Two-layer: deterministic CLI + inference skill |
| Unified context graph | ADR-019 | Single graph, NetworkX, node_link_data format |
| Ontology graph extension | ADR-023 | Structural nodes (BCs, layers) in graph |

---

## Notes

### Why This Epic

- PAT-196 keeps recurring: stale docs → wrong paths in new sessions
- PAT-152: schema changes invalidate graph silently
- Current drift detection (383 false positives) is unusable
- Prevention > detection: small batches at story-close vs periodic big-bang audit
- Graph diff is foundational infrastructure — enables future tooling beyond docs

### Key Risks

- **Graph diff accuracy** (Medium likelihood, High impact): False positives in diff could trigger unnecessary doc rewrites. Mitigation: conservative change detection, HITL gate.
- **Subagent quality** (Medium likelihood, Medium impact): AI-generated doc sections may need significant editing. Mitigation: start with frontmatter-only (S16.2), add AI layer (S16.3) incrementally.
- **Story-close latency** (Low likelihood, Low impact): Extra step adds time. Mitigation: skip when no structural changes detected.

### Key Patterns Informing Design

- **PAT-196:** Architecture docs are the map — stale docs cause wrong paths
- **PAT-200:** Deterministic (CLI) for structure, inference (skill) for content
- **PAT-202/203:** Templates-as-contract — doc structure IS the contract
- **PAT-174:** Architecture docs are intentional governance — deviating is drift
- **PAT-191:** Simplest architecture is discovered, not designed upfront

---

*Epic tracking — update per story completion*
*Created: 2026-02-08*
