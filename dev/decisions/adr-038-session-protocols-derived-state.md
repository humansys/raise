# ADR-038: Session Protocols with Derived State

## Status

Proposed — 2026-04-03

## Context

Gemba analysis (E1248) identified 7 failure modes in session state management. The root cause: mutable YAML files serve as source of truth when git is the only reliable state source.

Simultaneously, the strategic vision (RAISE-1229) calls for server-backed state in 3.0 — a centralized session registry, real-time workstream monitoring, and cross-repo visibility.

Building 2.4 fixes as ad-hoc patches to YAML files creates throwaway work. Instead, we need interfaces that the server can implement in 3.0 while community gets a functional git-only backend now.

## Decision

Introduce three session protocols following the established adapter pattern (ADR-033):

### 1. StateDeriver

Derives current work context from available sources. Replaces the unreliable `session-state.yaml` read for `current_work`.

```python
@runtime_checkable
class StateDeriver(Protocol):
    def current_work(self, project: Path) -> CurrentWork: ...
    def recent_activity(self, project: Path, limit: int = 10) -> list[ActivityEntry]: ...
```

- **Git backend (2.4):** Parses branch name, greps scope.md frontmatter, reads git log
- **Server backend (3.0):** Real-time tracking with heartbeats, cross-worktree visibility

### 2. SessionRegistry

Tracks active sessions across a developer's workstreams.

```python
@runtime_checkable
class SessionRegistry(Protocol):
    def register(self, session: SessionInfo) -> None: ...
    def active(self, project: Path | None = None) -> list[SessionInfo]: ...
    def close(self, session_id: str, outcome: SessionOutcome) -> None: ...
    def gc(self, max_age_hours: int = 48) -> list[str]: ...
```

- **Git backend (2.4):** Local files (active-session, index.jsonl) with zombie reaping
- **Server backend (3.0):** Centralized DB, cross-repo, cross-machine, blast radius

### 3. WorkstreamMonitor

Observes session patterns and suggests improvements. The kaizen agent.

```python
@runtime_checkable
class WorkstreamMonitor(Protocol):
    def analyze_session(self, session_id: str) -> SessionInsights: ...
    def suggest_improvements(self, last_n: int = 5) -> list[Improvement]: ...
```

- **Git backend (2.4):** Heuristics from journal + git log (commit velocity, TDD compliance, revert ratio)
- **Server backend (3.0):** Async agent with pattern recognition across team

### Registration

Follow established entry point pattern:

```toml
[project.entry-points."rai.session.state_deriver"]
git = "raise_cli.session.derive:GitStateDeriver"

[project.entry-points."rai.session.registry"]
local = "raise_cli.session.registry:LocalSessionRegistry"

[project.entry-points."rai.session.monitor"]
local = "raise_cli.session.monitor:LocalWorkstreamMonitor"
```

`raise-pro` and `raise-server` register their implementations under the same groups. Resolution: server > local, with fallback.

## Consequences

### Positive

- 2.4 community work is NOT throwaway — it becomes the fallback backend
- Server implementation in 3.0 is additive (new entry point, not code rewrite)
- Bundle assembly consumes protocols, not file paths — testable, swappable
- Worktree awareness becomes a property of the git backend, not a separate concern

### Negative

- More upfront abstraction than "just parse git" — must earn its complexity
- Three new protocols is a significant API surface to stabilize
- Git backend has inherent limitations (local-only, no real-time) that protocols can't hide

### Risks

- Over-engineering: protocols must stay minimal. If a method only has one implementation path, it doesn't need a protocol.
- PAT-E-628 tension: adapter-aware isinstance dispatch is simpler than polymorphism for 1-2 adapters. If only git+server exist, maybe direct dispatch is enough.

## Mitigation

Start with StateDeriver only (Story 1). Validate the protocol pattern works. Then extend to SessionRegistry and WorkstreamMonitor. If the pattern proves too heavy, collapse to direct dispatch per PAT-E-628.
