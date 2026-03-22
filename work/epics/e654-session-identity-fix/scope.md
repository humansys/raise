# Epic Scope: Session Identity Fix

> **Epic:** E654
> **Jira:** RAISE-654
> **Objective:** Move session data to git, isolate by dev+repo, eliminate cross-environment leakage

---

## Objective

Fix session identity so that sessions are scoped to developer+repository (not environment/channel), enabling coherent multi-session work regardless of where the developer opens Claude Code.

## Design Decisions (from gemba + research)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key | Timestamp-based: `SES-{prefix}-{YYYYMMDD}T{HHMM}` | No coordination needed, no counter collisions across worktrees/branches/machines |
| Display key | `name` (required on start, refinable on close) | Human-readable, searchable, like Jira summary |
| Storage split | Index in git (committed), working state gitignored | Shared definition + local cache (direnv pattern) |
| Developer isolation | Per-prefix subdirectories: `.raise/rai/sessions/{prefix}/index.jsonl` | Zero merge conflicts between developers |
| When to commit | On session close | Complete metadata, instant start |
| Journal | Local only — destilled into index on close | Signal > noise |
| Git pull on start | Best-effort `--ff-only`, non-blocking | Sync without friction, graceful offline |
| Prefix registry | Auto-register on first use, collision detection | Zero config for new developers |
| Migration | One-time auto-migration of existing `SES-NNN` → new format | Existing users must not lose session history |

## In Scope

- Session identity model: timestamp-based ID + human-readable name
- Per-developer session index in git (`.raise/rai/sessions/{prefix}/index.jsonl`)
- Developer prefix registry with auto-registration (`.raise/rai/sessions/prefixes.yaml`)
- Active session pointer (local, gitignored): `.raise/rai/personal/active-session`
- Working state stays local: `.raise/rai/personal/sessions/{id}/`
- Migration from old format (`SES-NNN` in `.raise/rai/personal/`) to new format
- CLI compatibility: `rai session start/close/journal/list/context` work with new storage
- Cross-environment continuity: session index travels with git
- Named sessions: `--name` on start (required), refinable on close

## Out of Scope

- Workstream abstraction (separate epic, depends on this one)
- Session data encryption or access control
- Changes to session context bundle format
- Cross-session memory or learning (beyond what patterns.jsonl already does)

## Stories

| ID | Name | Size | Dependencies |
|----|------|------|-------------|
| S654.1 | Session ID Model & Prefix Registry | S | None |
| S654.2 | Shared Session Index | M | S654.1 |
| S654.3 | CLI Adaptation | M | S654.1, S654.2 |
| S654.4 | Context Bundle & Orientation | S | S654.2, S654.3 |
| S654.5 | Migration | S | S654.1, S654.2 |

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Build the new identity model and storage layer first (S654.1 → S654.2), proving the architecture with tests before integrating into CLI. Migration goes last — it's the highest-risk story and needs the full new stack ready.

### Sequence

| # | Story | Rationale | Enables |
|---|-------|-----------|---------|
| 1 | **S654.1** — ID Model & Prefix Registry | Foundation — everything depends on the new ID format and prefix system | S654.2, S654.3, S654.5 |
| 2 | **S654.2** — Shared Session Index | Walking skeleton — proves the shared-in-git storage model E2E | S654.3, S654.4, S654.5 |
| 3 | **S654.3** — CLI Adaptation | Integration — connects new model to user-facing commands | S654.4, S654.5 |
| 4a | **S654.4** — Context Bundle & Orientation | Leaf — reads shared index for session history | (none) |
| 4b | **S654.5** — Migration | Leaf — converts existing sessions. Parallel with S654.4 | (none) |

S654.4 and S654.5 are independent — can run in parallel after S654.3.

### Critical Path

```
S654.1 → S654.2 → S654.3 → S654.4
                           → S654.5  (parallel)
```

### Milestones

**M1: Walking Skeleton** (after S654.1 + S654.2)
- New ID format generates correctly (`SES-E-20260322T1430`)
- Prefix registry creates/reads `prefixes.yaml`
- Shared index writes/reads from `.raise/rai/sessions/{prefix}/index.jsonl`
- All verified by tests — not yet wired to CLI
- **Verifiable:** `pytest` passes for new modules

**M2: CLI Integration** (after S654.3)
- `rai session start --name "..."` creates session with new ID format
- `rai session close` writes to shared index
- `rai session list` shows names
- Resolver handles both old and new ID formats
- **Verifiable:** manual `rai session start/close/list` roundtrip works

**M3: Epic Complete** (after S654.4 + S654.5)
- Context bundle reads shared index for session history
- Existing `SES-NNN` sessions migrated automatically on first start
- All done criteria met
- **Verifiable:** full `rai session start --context` shows cross-environment history, old sessions visible in new format

### Progress Tracking

| Story | Status | Notes |
|-------|--------|-------|
| S654.1 | pending | |
| S654.2 | pending | |
| S654.3 | pending | |
| S654.4 | pending | |
| S654.5 | pending | |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| S654.3 (CLI) is large — touches many commands | TDD per command, commit after each. Break into sub-tasks in story plan |
| S654.5 (migration) discovers edge cases in old data | Defensive parsing, log warnings for unrecoverable entries, never crash |
| Resolver backward compat breaks old session references | Keep `SES-NNN` normalization as fallback path in resolver |

## Done Criteria

- [ ] Sessions use timestamp-based IDs (`SES-{prefix}-{YYYYMMDD}T{HHMM}`)
- [ ] Sessions have human-readable names (required)
- [ ] Session index lives in git under `.raise/rai/sessions/{prefix}/`
- [ ] Per-developer prefix isolation (zero merge conflicts)
- [ ] Working state stays gitignored
- [ ] Existing `SES-NNN` sessions migrated to new format (one-time, automatic)
- [ ] Cross-environment continuity: same index visible from any terminal/machine
- [ ] All `rai session` CLI commands work with new model
- [ ] Zero cross-repo leakage
