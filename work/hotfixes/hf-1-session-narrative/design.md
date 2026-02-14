---
story_id: HF-1
name: session-narrative
size: S
sp: 3
status: design
module: mod-session
---

# HF-1: Session Narrative

## What & Why

**Problem:** Session handoff loses reasoning between conversations. The context bundle preserves mechanical state ("what to do next") but drops decision rationale, research conclusions, and artifact context ("why we decided this"). PAT-E-279.

**Value:** Next session is "immediately resumable" — Rai can start working with full context of WHY, not just WHAT. Validated by research RES-SESSION-MEM-001 (Cline, OpenAI SDK, Claude Code all converge on structured summaries).

## Architectural Context

- **Module:** mod-session (session lifecycle — state persistence, context bundle assembly, close orchestration)
- **Dependencies touched:** mod-schemas (SessionState model)
- **No new modules, no new files** — changes to existing flow only
- **Consistent with PAT-E-188:** Deterministic data (CLI stores/loads) with inference interpretation (skill generates/reads)

## Approach

Add a single `narrative: str = ""` field to `SessionState`. The session-close skill generates structured markdown as the narrative content; the CLI persists it in session-state.yaml; the bundle loads it verbatim into the context output.

**Why one string, not a Pydantic sub-model with 5 fields:**
- The bundle renders it as text — no parsing benefit from structured fields
- Structure lives in the skill template guidance, not the schema
- Simpler schema = simpler migration = simpler tests
- YAGNI — if we need parsable fields later, we migrate then

**Why not reuse `notes`:**
- `notes` has different semantic intent (ad-hoc remarks)
- Already populated with unrelated content in production
- Overloading changes meaning silently

## Components Affected

| Component | Change | File |
|-----------|--------|------|
| SessionState schema | Add `narrative: str = ""` | `src/rai_cli/schemas/session_state.py` |
| CloseInput dataclass | Add `narrative: str = ""` | `src/rai_cli/session/close.py` |
| load_state_file | Extract `narrative` from YAML | `src/rai_cli/session/close.py` |
| process_session_close | Pass narrative to SessionState | `src/rai_cli/session/close.py` |
| bundle.py | Add `_format_narrative()`, include in bundle | `src/rai_cli/session/bundle.py` |
| session-close skill | Add `narrative` field with guidance | `.claude/skills/rai-session-close/SKILL.md` |
| session-start skill | Mention narrative in bundle description | `.claude/skills/rai-session-start/SKILL.md` |

## Examples

### Session Close YAML (skill produces)

```yaml
summary: "E21 Platform Integration — epic start, design, plan"
type: feature
narrative: |
  ## Decisions
  - Architecture = sync model (NOT real-time adapters). Local files primary, JIRA/Confluence are sync targets. YAGNI on BacklogProvider ABC until GitLab needed.
  - Push first, then pull — JIRA has no v2 data, populate from local first.
  - atlassian-python-api chosen over httpx/MCP for speed to market.

  ## Research
  - OpenClaw (dev/research/openclaw-extension-patterns.md) — adapter patterns at scale. Deferred for v1.
  - Rovo AI (dev/research/rovo-ai-platform-analysis.md) — CLI IS the integration layer. Skill→subagent conversion is mechanical.

  ## Artifacts
  - work/epics/e21-platform-integration/scope.md — sync model, 3-story sprint
  - dev/decisions/adr-026-platform-integration-architecture.md — sync model ADR

  ## Branch State
  - On epic/e21/platform-integration (8 commits ahead of v2)
  - No story branch created yet
outcomes:
  - "ADR-026 rewritten for sync model"
  - "E19 V3 scope preserved"
# ... rest of state file
```

### Context Bundle Output (session start)

```
# Session Context
Developer: Emilio (ri)
...

Last: SES-159 (2026-02-14, Emilio) — E21 Platform Integration — epic start...

# Session Narrative
## Decisions
- Architecture = sync model (NOT real-time adapters)...

## Research
- OpenClaw — adapter patterns at scale. Deferred for v1...

# Governance Primes
...
```

### Backward Compatibility

```python
# Old session-state.yaml without narrative field
data = {
    "current_work": {"epic": "E15", ...},
    "last_session": {"id": "SES-097", ...},
}
state = SessionState.model_validate(data)
assert state.narrative == ""  # Pydantic default, no error
```

## Acceptance Criteria

**MUST:**
- [ ] `SessionState.narrative` field exists with default `""`
- [ ] Session close persists narrative from state file to session-state.yaml
- [ ] Session start includes narrative in context bundle (not truncated)
- [ ] Bundle omits narrative section when empty
- [ ] Backward compatible with existing session-state.yaml files (no narrative field)
- [ ] All existing tests pass unchanged
- [ ] New tests cover: schema, close wiring, bundle formatting, roundtrip

**MUST NOT:**
- [ ] Break existing session-state.yaml files
- [ ] Truncate narrative content (unlike primes/patterns)
- [ ] Add new files or infrastructure — changes to existing flow only

**SHOULD:**
- [ ] Skill template provides structure guidance (~300-500 tokens, 4 sections)
- [ ] Narrative section appears after "Last:" and before primes in bundle
