---
epic_id: "E1040"
title: "Design Decisions"
created: "2026-04-02"
---

# E1040: Design Decisions

## DD-1: Steward + Adapter architecture (2026-04-02)

### Context

The original epic assumed all lifecycle skills write directly to filesystem and proposed a unified LocalPersistenceAdapter to wrap everything. Audit revealed work artifacts already pass through an adapter (`DocumentationTarget` → `FilesystemDocsTarget` + `ConfluenceTarget`). The real gap is session state (RAISE-697) and other process-critical data with no governance layer.

The term "adapter" was misleading — it implies the primary value is backend swappability. The real value is **reliability governance**: validation, atomicity, protection against corruption.

### Decision

Introduce a **Steward + Adapter** two-layer architecture:

- **Steward** — domain-aware component that owns invariants for a category of process-critical data. Validates against schema/ontology, protects integrity, resolves location. Will grow from deterministic validation to inference-based intelligence over time.
- **Adapter** — backend-specific I/O. Atomic primitives (read, write, append, list). Knows nothing about domain. Swappable.

```
Skill → CLI → Steward (domain, validation, ontology, inference)
                 → Adapter (I/O, backend, plumbing)
```

### Steward inventory

| Steward | Manages | Adapter today | Adapter future |
|---------|---------|---------------|----------------|
| SessionSteward | state, index, journal | FilesystemAdapter | — |
| MemorySteward | patterns, learnings | FilesystemAdapter | — |
| DeveloperSteward | profile, coaching, corrections | FilesystemAdapter | — |
| DocsSteward | scope, design, plan, retro | CompositeAdapter (filesystem + confluence) | Already exists as DocumentationTarget |
| BacklogSteward | issues, transitions, comments | JiraAdapter | Already exists as ProjectManagementAdapter |

### Design rule

> If a piece of data affects the reliability of the RaiSE process, it is managed by a Steward. No exceptions.

A skill never touches an Adapter directly. The call chain is always: Skill → CLI → Steward → Adapter.

### Why "Steward"

- Active, not passive (unlike Repository which implies storage/retrieval)
- Encapsulates growing intelligence — deterministic validation today, inference tomorrow
- Established in data governance ("Data Steward") but not a loaded software pattern (no collision with GoF, DDD, Spring, etc.)
- Scales semantically: a steward that validates schemas IS a steward. A steward that detects duplicate patterns via inference is ALSO a steward.

### Alternatives considered

| Option | Rejected because |
|--------|-----------------|
| Unified LocalPersistenceAdapter | Work artifacts already have an adapter. Would create competing pipelines. |
| Surgical fixes (atomic writes only) | Fixes symptoms, doesn't create governance enforcement point. |
| Repository pattern | Too passive. These components will encapsulate domain logic and grow with inference, not just store/retrieve. |

## DD-2: Scope is session + memory + developer, not work artifacts (2026-04-02)

### Context

Work artifacts (scope.md, design.md, plan.md, retro.md) already pass through `DocumentationTarget` → `FilesystemDocsTarget` + `ConfluenceTarget`. That pipeline works. What's missing is frontmatter validation — a fix to the existing adapter, not a new one.

Session state, journal, patterns, and developer profile have NO adapter layer. Direct filesystem writes with varying degrees of validation.

### Decision

This epic (E1040) delivers:
1. **SessionSteward** + **MemorySteward** + **DeveloperSteward** — new stewards for unmanaged data
2. **FilesystemAdapter** — shared atomic backend for all three
3. **Validation hardening** of existing `FilesystemDocsTarget` — frontmatter validation for work artifacts
4. **Migration** of all session/memory CLI code to use stewards

Work artifact persistence is NOT reimplemented — the existing `DocumentationTarget` adapter is the DocsSteward in embryonic form.

### Design rule

> One mental model for maintainability: "you write process-critical data? Use the steward." No exceptions, no per-concern special cases. This matters because the primary maintainer (Rai) resets context every session.

## DD-3: Stewards own domain intelligence, Adapters are dumb I/O (2026-04-02)

### Context

Question arose: who owns business rules? For example, in the backlog domain, who knows that a story can't be closed without a retrospective — the adapter (JiraAdapter) or the steward (BacklogSteward)?

### Decision

**Stewards own all domain intelligence. Adapters know nothing about the domain.**

The adapter executes: "transition this issue to Done." The steward decides whether that transition is allowed based on RaiSE process rules.

```python
# Adapter — executes, no questions asked
class JiraAdapter:
    def transition(self, key, status): ...  # API call, done

# Steward — knows the rules
class BacklogSteward:
    def transition(self, key, target_status):
        issue = self.adapter.get(key)
        if issue.type == "Story" and target_status == "Done":
            if not self.has_retro(key):
                raise GateFailed("retrospective required before close")
        self.adapter.transition(key, target_status)
```

### Applied to E1040 stewards

| Steward | Domain rules (steward) | Plumbing (adapter) |
|---------|----------------------|-------------------|
| SessionSteward | "don't overwrite state with older timestamps", "closed sessions reject new journal entries" | read/write YAML, append JSONL |
| MemorySteward | "this pattern already exists as PAT-312", "context keywords must exist in graph" | append JSONL |
| DeveloperSteward | "don't erase existing corrections on merge", "coaching level only goes up" | read/write YAML |

### Growth path

Today: deterministic rules (timestamp comparison, existence checks, enum validation).
Tomorrow: inference-based intelligence ("this pattern is redundant with PAT-312, should I merge?", "this coaching observation contradicts an earlier one").

The boundary stays the same: steward decides, adapter executes. The steward's intelligence grows without changing the adapter contract.

## DD-4: Single concrete FilesystemAdapter, no protocol yet (2026-04-02)

### Context

Considered three options for the adapter layer: one adapter per steward (DRY violation), a shared concrete class, or a protocol with a concrete implementation.

### Decision

One concrete `FilesystemAdapter` class shared by all stewards. No protocol abstraction until a second backend exists (3.0 scope).

```python
adapter = FilesystemAdapter(root=project_root)
session = SessionSteward(adapter)
memory = MemorySteward(adapter)
developer = DeveloperSteward(FilesystemAdapter(root=Path.home() / ".rai"))
```

Primitives: `write(path, content)`, `append(path, line)`, `read(path)`, `list(glob)`. All atomic (write-to-temp + rename).

### Why no protocol

- No second backend exists today
- Protocol adds indirection that doesn't help readability
- Extract-to-protocol is a safe, mechanical refactor when needed (3.0)
- "Simple First" — complexity must earn its place

## DD-5: CLI orchestrates, stewards persist (2026-04-02)

### Context

Three integration options: (A) replace direct calls with steward calls in existing CLI functions, (B) steward as orchestrator (CLI delegates entirely), (C) hybrid — CLI orchestrates flow, stewards handle persistence.

### Decision

Option C: CLI keeps orchestration, stewards handle persistence only.

```python
def process_session_close(state_file):
    data = load_state_file(state_file)
    
    session_steward.save_state(data.session)
    session_steward.append_journal(data.journal_entries)
    
    for pattern in data.patterns:
        memory_steward.add_pattern(pattern)
    
    developer_steward.update_coaching(data.coaching)
```

### Why

- The flow (what to persist and when) is process logic — belongs in CLI
- Each line is readable: I know what's persisted and who manages it
- In 50 sessions, when something fails in `process_session_close()`, the flow is right there — not hidden inside a steward's `close()` method
- Stewards stay cohesive: validate + persist their concern, nothing else

## DD-6: Stewards absorb existing validation, add missing protections (2026-04-02)

### Context

Pydantic validation already exists for most data types (SessionState, SessionIndexEntry, JournalEntry, PatternSubType, DeveloperProfile). But it's scattered across direct-write functions with no structural protection (atomicity, timestamp guards, dedup).

### Decision

Stewards absorb existing Pydantic validation and add the protections that are missing:

| Steward | Existing validation (absorbed) | New protections |
|---------|-------------------------------|-----------------|
| SessionSteward | SessionState, SessionIndexEntry, JournalEntry models | Timestamp comparison before overwrite (RAISE-697), session_id existence check before journal append |
| MemorySteward | PatternSubType enum | ID generation (PAT-{N}) inside steward, optional dedup check |
| DeveloperSteward | DeveloperProfile model | Defensive merge (don't overwrite fields not in update), coaching level monotonic |

This is primarily a refactoring epic, not a greenfield effort. The bulk of the work is moving existing code into stewards and adding targeted protections where gaps exist.
