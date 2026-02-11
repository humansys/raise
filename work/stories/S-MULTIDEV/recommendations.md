# S-MULTIDEV: Multi-Developer Collaboration Safety

## Recommendations

> Spike deliverable. Research + decisions, no implementation.
> Decisions made: 2026-02-11 (Emilio + Rai, SES-141)

---

## Context

Fer is pulling `v2` and starting work with Rai on raise-commons. Several `.raise/` files are tracked in git and will cause merge conflicts or data corruption when two developers work on separate branches.

## Decisions

### D1: `index.json` — Gitignore

**File:** `.raise/rai/memory/index.json` (152K lines, 3.4MB)
**Decision:** Add to `.gitignore`. Each developer rebuilds with `rai memory build`.

**Rationale:** It's a derived artifact — fully regenerated from JSONL sources + governance docs. Tracking it guarantees merge conflicts on every pull. Rebuilding takes <2 seconds.

**Implementation:**
- Add `.raise/rai/memory/index.json` to `.gitignore`
- Remove from git tracking (`git rm --cached`)
- Consider: auto-rebuild in `rai session start` if index.json is missing

---

### D2: `session-state.yaml` — Move to personal/

**File:** `.raise/rai/session-state.yaml`
**Decision:** Move to `.raise/rai/personal/session-state.yaml` (already gitignored).

**Rationale:** Session state is per-developer by definition — current story, phase, last session. One developer's session close would overwrite the other's working context.

**Implementation:**
- Update `session/state.py` to read/write from personal/ path
- Migration: move existing file on first access
- Delete old file from git tracking

---

### D3: Pattern IDs — Developer-prefixed

**File:** `.raise/rai/memory/patterns.jsonl`
**Decision:** Switch from sequential `PAT-NNN` to developer-prefixed `PAT-{X}-NNN` where X is the developer's initial (stored in `~/.rai/developer.yaml`).

**Rationale:** When two developers branch from the same last pattern number and independently add patterns, they produce different patterns with the same ID. This is semantic corruption, not just a merge conflict — debugging which PAT-260 is which is muda.

**ID format:** `PAT-{prefix}-{number}`
- Emilio: PAT-E-001 through PAT-E-259 (migrated), then PAT-E-260+
- Fer: PAT-F-001+

**Prefix source:** `~/.rai/developer.yaml` field (e.g., `pattern_prefix: E`).
Convention: first letter of name. No shared registry — trust-based for small teams.

**Migration:**
- Rename existing PAT-001..PAT-259 → PAT-E-001..PAT-E-259 in patterns.jsonl
- Update references in MEMORY.md (auto-generated, will rebuild)
- Update any scope docs or skill files referencing specific PAT-NNN IDs

---

### D4: `calibration.jsonl` — Move to personal/

**File:** `.raise/rai/memory/calibration.jsonl` (64 entries)
**Decision:** Move to `.raise/rai/personal/calibration.jsonl`.

**Rationale:** Coaching corrections, trust levels, and growth edges are per-developer. Mixing two developers' calibration data in one file makes the coaching system unable to distinguish whose profile is whose.

**Implementation:**
- Move file to personal/
- Update `context/builder.py` to load calibration from personal/
- Migration: move on first access

---

### D5: Empty `sessions/index.jsonl` — Delete

**File:** `.raise/rai/memory/sessions/index.jsonl` (0 bytes)
**Decision:** Delete. Sessions already write to `.raise/rai/personal/sessions/index.jsonl`.

**Implementation:** `git rm` the empty file and parent directory if empty.

---

## File Classification (Final)

| File | Scope | Location | Tracked? |
|------|-------|----------|----------|
| `index.json` | Derived | `.raise/rai/memory/` | **No** (gitignore) |
| `session-state.yaml` | Personal | `.raise/rai/personal/` | No (already gitignored) |
| `patterns.jsonl` | Shared | `.raise/rai/memory/` | Yes |
| `calibration.jsonl` | Personal | `.raise/rai/personal/` | No (already gitignored) |
| `sessions/index.jsonl` | Personal | `.raise/rai/personal/sessions/` | No (already gitignored) |
| `MEMORY.md` | Shared | `.raise/rai/memory/` | Yes (generated, but useful) |
| `methodology.yaml` | Shared | `.raise/rai/framework/` | Yes |
| `governance/` | Shared | `governance/` | Yes |
| `work/stories/` | Shared | `work/stories/` | Yes |
| `developer.yaml` | Personal | `~/.rai/` | Per-machine |
| `CLAUDE.local.md` | Personal | Project root | No (gitignored) |

---

## Implementation Scope

| Change | Files Affected | Effort |
|--------|---------------|--------|
| Gitignore index.json | `.gitignore`, git rm | Trivial |
| Move session-state to personal/ | `session/state.py`, migration | Small |
| Developer-prefixed pattern IDs | `memory/writer.py`, `onboarding/profile.py`, patterns.jsonl | Medium |
| Move calibration to personal/ | `context/builder.py`, `memory/loader.py`, migration | Small |
| Delete empty sessions file | git rm | Trivial |
| Auto-rebuild index on session start | `cli/commands/session.py` | Small |

**Total estimate:** ~150 lines changed across 6-8 files. One story (S/M size).
