---
story_id: "S15.7"
title: "Deterministic Session Protocol"
epic_ref: "E15 Ontology Graph Refinement"
story_points: 5
complexity: "moderate-complex"
status: "draft"
version: "1.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Feature: Deterministic Session Protocol

> **Epic**: E15 - Ontology Graph Refinement
> **Complexity**: moderate-complex | **SP**: 5

---

## 1. What & Why

**Problem**: Rai's session continuity is fragmented across platform-coupled files (CLAUDE.local.md), cached inference (session bridges), and scattered CLI calls. Each session starts cold — reconstructing context from ~3300 tokens of mixed-quality sources instead of receiving a structured context bundle. Coaching observations, corrections, and relationship state are lost every session.

**Value**: A deterministic session protocol gives Rai reliable continuity across sessions and platforms. Context loading drops from ~3300 to ~150 tokens. Relationship state accumulates. Behavioral primes prevent repeated mistakes. Any AI client can call the same CLI and get the same context — platform-agnostic by construction.

---

## 2. Approach

**How we'll solve it**: Redesign `raise session start` to assemble a complete, token-optimized context bundle from multiple sources (session-state, developer model, graph). Redesign `raise session close` to accept structured session outcomes and write all state deterministically. Extend the developer model with coaching and deadline fields. Add foundational pattern metadata for behavioral priming.

**Components affected**:
- **`src/raise_cli/onboarding/profile.py`**: Modify — extend `DeveloperProfile` with `CoachingContext` and `deadlines`
- **`src/raise_cli/cli/commands/session.py`**: Modify — redesign `start` (context bundle output) and `close` (structured input)
- **`src/raise_cli/schemas/session_state.py`**: Create — `SessionState` Pydantic model
- **`src/raise_cli/session/`**: Create — session protocol module (state reader/writer, bundle assembler)
- **`.raise/rai/session-state.yaml`**: Create — project-level working state (written by close, read by start)
- **`.raise/rai/memory/patterns.jsonl`**: Modify — add `foundational: true` metadata to ~10 patterns
- **`.claude/skills/session-start/SKILL.md`**: Modify — thin to 2 steps (call CLI, interpret)
- **`.claude/skills/session-close/SKILL.md`**: Modify — thin to 2 steps (reflect, feed CLI)

**Design decisions resolved**:

| # | Decision | Resolution | Rationale |
|---|----------|------------|-----------|
| 1 | How does `raise session close` receive structured input? | CLI flags for simple fields + `--state-file` for full state | Flags for common ops (`--summary`, `--patterns`), file for full session-state overwrite. AI writes YAML, CLI reads it. |
| 2 | Which patterns are foundational? | 10 patterns curated with Emilio (HITL) | PAT-187, 183, 186, 150, 154, 159, 149, 152, 153, 151. Human judgment, not automation. |
| 3 | Corrections buffer size | Last 10 corrections | Older corrections should have become patterns. If not generalized after 10, that's a signal. |
| 4 | Deadline source | `~/.rai/developer.yaml` deadlines section | Deadlines are Rai's operational context — they modulate behavior (urgency, focus, pushback). Not governance artifacts. |
| 5 | Migration path | Build alongside, switch when validated | New protocol works in parallel. Session bridges stop being written. CLAUDE.local.md loses data role gradually. |
| 6 | Telemetry ownership | CLI commands emit telemetry internally | Skills stop calling emit-session/emit-work/add-session separately. `raise session close` handles all writes atomically — one command, all data. |
| 7 | Idempotent close | `raise session close` works with or without active session | Real workflow: close, keep working, close again. Second close overwrites state with more current data. `current_session` check is for orphan detection, not a precondition for writing state. |

---

## 3. Interface / Examples

### CLI Usage — Session Start

```bash
# Full context bundle for AI consumption
$ raise session start --project /home/emilio/Code/raise-commons --context

# Output: token-optimized context bundle (see Expected Output below)

# Legacy mode (current behavior, backward compat)
$ raise session start --project /home/emilio/Code/raise-commons
# Output: "Session recorded. (last: 2026-02-08)"
```

### Expected Output — Context Bundle

```
# Session Context

Developer: Emilio (ri)
Epic: E15 Ontology Refinement [65%, 11/17 SP]
Story: S15.7 Deterministic Session Protocol [phase: design]
Branch: story/s15.7/session-protocol
Graph: 849 nodes, 6157 rels
Last: SES-097 (2026-02-08, feature) — session protocol design

# Deadlines
F&F: Feb 9 (1 day)
Public Launch: Feb 15
Rovo Webinar: Mar 14

# Behavioral Primes
- PAT-187: Code as Gemba — observe before designing
- PAT-183: Design always, no size exemptions
- PAT-186: Design not optional, even when mechanism exists
- PAT-150: Drift review before implementation
- PAT-149: Single source of truth

# Coaching
Strengths: architectural vision, naming things, knowing when to stop
Growth edge: speed over process under pressure
Recent corrections:
- SES-096: Offered to skip design → Knowledge != behavior
- SES-097: Defaulted to speed under deadline → Reliability > velocity

# Pending
Decisions:
- Foundational pattern curation (HITL)
Next:
- Implement session-state schema
- Write ADR-024
```

### CLI Usage — Session Close

```bash
# Simple close with summary
$ raise session close --summary "Session protocol design" --type feature

# Close with new patterns
$ raise session close --summary "Session protocol design" \
  --type feature \
  --pattern "PAT-187: Code as Gemba — observe before designing"

# Close with coaching correction
$ raise session close --summary "Session protocol design" \
  --type feature \
  --correction "Defaulted to speed under deadline" \
  --correction-lesson "Reliability > velocity"

# Full close with state file (AI writes YAML, CLI reads)
$ raise session close --state-file /tmp/session-output.yaml

# All of the above atomically:
# 1. Writes session-state.yaml
# 2. Adds patterns to patterns.jsonl
# 3. Updates coaching in developer.yaml
# 4. Records session in sessions/index.jsonl
# 5. Emits telemetry (session_close signal)
# 6. Clears current_session
# One command. All writes. No skill telemetry calls needed.
```

### State File Format (for --state-file)

```yaml
# Written by AI skill, consumed by CLI
summary: "Session protocol design exploration"
type: feature
outcomes:
  - "S15.7 scope committed"
  - "Design decisions resolved"
patterns:
  - description: "Code as Gemba — observe before designing"
    context: [process, design, lean]
    type: process
corrections:
  - what: "Defaulted to speed under deadline"
    lesson: "Reliability > velocity"
current_work:
  epic: E15
  story: S15.7
  phase: design
  branch: story/s15.7/session-protocol
pending:
  decisions: []
  blockers: []
  next_actions:
    - "Implement session-state schema"
notes: "ADR-024 needed before implementation."
```

### Data Structures

```python
# src/raise_cli/schemas/session_state.py

class SessionState(BaseModel):
    """Project-level working state. Overwritten each session-close."""

    current_work: CurrentWork
    last_session: LastSession
    pending: PendingItems
    notes: str = ""


class CurrentWork(BaseModel):
    """What Rai is currently working on."""

    epic: str          # "E15"
    story: str         # "S15.7"
    phase: str         # "design"
    branch: str        # "story/s15.7/session-protocol"


class LastSession(BaseModel):
    """Summary of the most recent session."""

    id: str            # "SES-097"
    date: date
    developer: str     # "Emilio"
    summary: str
    patterns_captured: list[str] = Field(default_factory=list)


class PendingItems(BaseModel):
    """Open items carried between sessions."""

    decisions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
```

```python
# Extension to src/raise_cli/onboarding/profile.py

class Correction(BaseModel):
    """A coaching correction episode."""

    session: str       # "SES-097"
    what: str          # "Defaulted to speed under deadline"
    lesson: str        # "Reliability > velocity"


class Deadline(BaseModel):
    """An operational deadline Rai tracks."""

    name: str          # "F&F"
    date: date         # 2026-02-09
    notes: str = ""    # "Pre-launch for HumanSys team"


class CoachingContext(BaseModel):
    """Rai's coaching observations about a developer."""

    strengths: list[str] = Field(default_factory=list)
    growth_edge: str = ""
    trust_level: str = "new"  # new, growing, established, high
    autonomy: str = ""
    corrections: list[Correction] = Field(default_factory=list, max_length=10)
    communication_notes: list[str] = Field(default_factory=list)
    relationship: RelationshipState = Field(default_factory=RelationshipState)


class RelationshipState(BaseModel):
    """State of the Rai-developer relationship."""

    quality: str = "new"  # new, building, collaborative, deep
    since: date | None = None
    trajectory: str = "starting"  # starting, building, deepening, stable


class DeveloperProfile(BaseModel):
    """Extended with coaching and deadlines."""

    name: str
    experience_level: ExperienceLevel = ExperienceLevel.SHU
    communication: CommunicationPreferences = Field(default_factory=CommunicationPreferences)
    skills_mastered: list[str] = Field(default_factory=list)
    universal_patterns: list[str] = Field(default_factory=list)
    first_session: date | None = None
    last_session: date | None = None
    projects: list[str] = Field(default_factory=list)
    current_session: CurrentSession | None = None
    # NEW — S15.7
    coaching: CoachingContext = Field(default_factory=CoachingContext)
    deadlines: list[Deadline] = Field(default_factory=list)
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `raise session start --project . --context` outputs a complete context bundle to stdout
- [ ] Context bundle is <200 tokens for a typical session
- [ ] Context bundle includes: developer model, current work, behavioral primes, coaching, deadlines, pending items
- [ ] `raise session close` accepts `--summary`, `--type`, `--pattern`, `--correction`, `--correction-lesson`, and `--state-file`
- [ ] `.raise/rai/session-state.yaml` is written by close, read by start
- [ ] `~/.rai/developer.yaml` has `coaching` and `deadlines` sections (backward compatible — defaults to empty)
- [ ] Foundational patterns tagged with `foundational: true` in patterns.jsonl metadata
- [ ] Foundational patterns surfaced in context bundle via graph query
- [ ] Corrections list capped at 10 (FIFO — oldest drops when new added)

### Should Have

- [ ] Session-start skill reduced to 2 steps (call CLI, interpret bundle)
- [ ] Session-close skill reduced to 2 steps (reflect + produce structured output, feed CLI)
- [ ] `--context` flag outputs plain text (default), `--context --format json` outputs JSON

### Must NOT

- [ ] **MUST NOT** depend on CLAUDE.local.md for session continuity
- [ ] **MUST NOT** write session bridges (prose files) — learnings go to graph, state to session-state.yaml
- [ ] **MUST NOT** break existing `raise session start/close` behavior (backward compat via `--context` flag)

---

<details>
<summary><h2>5. Detailed Scenarios</h2></summary>

### Scenario 1: Fresh Session Start (Happy Path)

```gherkin
Given a developer with an existing profile in ~/.rai/developer.yaml
  And a session-state.yaml exists from a previous session close
  And the memory graph has been built with foundational patterns tagged
When `raise session start --project . --context` is executed
Then the CLI outputs a context bundle containing:
  - Developer name and level from profile
  - Current work state from session-state.yaml
  - Foundational patterns from graph query
  - Coaching context from profile
  - Deadlines from profile
  - Pending items from session-state.yaml
And the bundle is <200 tokens
And current_session is set in the profile
```

### Scenario 2: First Session (No State File)

```gherkin
Given a developer with an existing profile in ~/.rai/developer.yaml
  And no session-state.yaml exists
  And the memory graph has been built
When `raise session start --project . --context` is executed
Then the CLI outputs a context bundle with:
  - Developer name and level
  - "(no previous session state)" for current work
  - Foundational patterns from graph
  - Empty coaching and pending sections
And the bundle gracefully handles missing state
```

### Scenario 3: Session Close with Structured Input

```gherkin
Given an active session with current_session set
When `raise session close --state-file output.yaml` is executed
  And output.yaml contains summary, patterns, corrections, and current_work
Then session-state.yaml is overwritten with current_work, last_session, pending
And new patterns are appended to patterns.jsonl
And corrections are appended to developer.yaml coaching (FIFO cap 10)
And session record is added to sessions/index.jsonl
And current_session is cleared
And telemetry signal emitted (session_close with duration, outcomes)
And the skill did NOT call any separate telemetry/memory commands
```

### Scenario 4: Idempotent Close (Double Close)

```gherkin
Given a session was already closed (current_session is None)
  And the developer continued working after close
When `raise session close --state-file output2.yaml` is executed
Then session-state.yaml is overwritten with the updated state
And new patterns (if any) are appended to patterns.jsonl
And coaching corrections (if any) are added to developer.yaml
And a new session record is added to sessions/index.jsonl
And the command succeeds without error
And current_session remains None (already cleared)
```

### Scenario 5: Backward Compatibility

```gherkin
Given the current CLI behavior (no --context flag)
When `raise session start --project .` is executed without --context
Then behavior is identical to current: "Session recorded. (last: ...)"
And no context bundle is output
```

### Scenario 6: Profile Without Coaching (Migration)

```gherkin
Given an existing developer.yaml without coaching or deadlines sections
When the profile is loaded by the CLI
Then coaching defaults to empty CoachingContext
And deadlines defaults to empty list
And the profile loads without error (backward compat)
```

</details>

---

<details>
<summary><h2>6. Algorithm — Context Bundle Assembly</h2></summary>

```python
def assemble_context_bundle(project_path: Path) -> str:
    """Assemble token-optimized context bundle from multiple sources.

    Sources (read in parallel where possible):
    1. ~/.rai/developer.yaml → developer model + coaching + deadlines
    2. .raise/rai/session-state.yaml → current work state
    3. Memory graph → foundational patterns (metadata query)
    4. Session index → last session info (if no session-state)

    Output: Plain text, ~150 tokens, section-based format.
    """
    # 1. Load developer profile
    profile = load_developer_profile()

    # 2. Load session state (may not exist)
    state = load_session_state(project_path)

    # 3. Query graph for foundational patterns
    graph = load_graph(project_path)
    primes = [n for n in graph.iter_concepts()
              if n.node_type == "pattern"
              and n.metadata.get("foundational") is True]

    # 4. Format compact output
    return format_context_bundle(profile, state, primes)
```

**Format rules:**
- Inline metadata in brackets: `E15 Ontology Refinement [65%, 11/17 SP]`
- One-liner patterns: `- PAT-183: Design always, no size exemptions`
- Section headers as semantic anchors: `# Coaching`, `# Deadlines`
- No prose — facts only
- Deadline includes days remaining: `F&F: Feb 9 (1 day)`

</details>

---

## References

**Related ADRs:**
- ADR-023: Ontology graph extension (parent epic)
- ADR-024: Deterministic session protocol (to be created)

**Related Patterns:**
- PAT-187: Code as Gemba — observe before designing
- PAT-183: Design always, no size exemptions
- PAT-186: Design not optional
- PAT-146: Three-tier data architecture
- PAT-149: Single source of truth
- PAT-129: Session as first-class workflow state
- PAT-130: One concept, one location
- PAT-158: Progressive directory structure

**Dependencies:**
- S15.4 (Edge-type filtering) — complete, needed for foundational pattern graph query
- Memory graph with pattern nodes — exists (186 patterns)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-08
**Based on**: SES-097 design exploration — deterministic data + inference interpretation
