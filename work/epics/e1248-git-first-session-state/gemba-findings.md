# E1248 Gemba Findings: Session State Architecture

> Date: 2026-04-03
> Method: Direct observation of `.raise/rai/personal/` state files and session start/close code paths
> Worktree: reliability-2.4 (release/2.4.0)

## 1. Inventory of State Sources

### What exists on disk (observed)

| File | Path | Format | Actual Content | Expected |
|------|------|--------|---------------|----------|
| active-session | `.raise/rai/personal/active-session` | JSON | `S-E-260403-0916` | Current session pointer |
| session-state.yaml | `.raise/rai/personal/session-state.yaml` | YAML | **MISSING** | Last session state |
| session-output.yaml | `.raise/rai/personal/session-output.yaml` | YAML | S-E-260401-CC-SAR-2 (2 days stale) | Pre-close state |
| sessions/ | `.raise/rai/personal/sessions/` | dirs | **53 directories** | Per-session state |
| CLAUDE.local.md | repo root | markdown | **EMPTY/MISSING** | Local AI context |

### Developer profile (observed)

```yaml
# ~/.rai/developer.yaml → active_sessions
active_sessions:
  - session_id: S-E-260329-1354    # 5 DAYS OLD — zombie
    project: /home/emilio/Code/Gameye98
  - session_id: S-E-260403-0916    # today, valid
    project: .
  - session_id: S-E-260403-1111    # today, valid (different project)
    project: /home/emilio/Code/raise-gtm
```

### Session directory formats (observed)

```
# Legacy format (pre-prefix era):
SES-030, SES-267, SES-309, ..., SES-378  (26 dirs)

# Current format:
S-E-260323-1634, S-E-260324-0045, ..., S-E-260403-0916  (17 dirs)

# Anomaly:
S-E-260401-CC-SAR-2  (manual/custom ID, 1 dir)
index.jsonl  (session index file mixed in with dirs)
E/  (prefix dir mixed in with session dirs)
```

## 2. Code Path Analysis

### Session Start (session.py:168-361)

```
1. Load developer profile (~/.rai/developer.yaml)
2. Check for stale sessions (>24h) → WARN only, no cleanup
3. Generate session ID (timestamp-based)
4. Write active-session pointer (atomic)
5. Migrate flat state to per-session dir (if flat exists)
6. Assemble context bundle from:
   a. Developer profile (identity, coaching, preferences)
   b. Session state YAML (current_work, last_session, pending, narrative)
   c. Memory graph (always-on governance, patterns)
   d. Session index (recent sessions)
   e. Live backlog status (non-blocking, 5s timeout)
   f. Git branch (runtime query)
```

**Key finding:** Step 5 migrates flat→per-session, but if flat is already gone AND the previous session ID isn't resolved, there's no state to load. Step 6b returns empty defaults.

### Session Close (session close skill → save_session_state)

```
1. Load session-output.yaml (pre-written by skill)
2. Write state to sessions/{id}/state.yaml
3. Append to session index
4. Update developer profile
5. Clear active-session pointer
```

**Key finding:** session-output.yaml is written by the skill BEFORE close, but never cleaned up AFTER close. Next session's close could read stale output.

### Bundle Assembly (bundle.py:212-284)

The orientation bundle assembles from:
- Developer profile → reliable (atomic writes)
- Session state → **unreliable** (may be missing, stale, or from wrong session)
- Memory graph → reliable (committed to git)
- Session index → reliable (append-only, committed)
- Git branch → reliable (runtime query)
- Backlog status → reliable (live query with timeout)

**Key finding:** 5 of 6 sources are reliable. The one unreliable source (session state YAML) is the one that carries the most critical context (current_work, pending, narrative).

## 3. Failure Mode Details

### FM-1: Session state lost between sessions

**Mechanism:**
1. Session A closes → writes state to `sessions/S-A/state.yaml`
2. Flat `session-state.yaml` deleted by migration
3. Session B starts → migration already done, flat gone
4. Session B looks for Session A's state → needs to know Session A's ID
5. If Session A's ID isn't in the active-session pointer (already cleared by close), state is orphaned

**Impact:** Session starts with empty `current_work`, `pending`, `narrative`. Developer must re-explain context.

### FM-2: Stale session-output.yaml

**Mechanism:**
1. Session A: skill writes session-output.yaml, then close reads it
2. Session A close completes → output.yaml NOT cleaned up
3. Session B: if close runs without a fresh skill write, reads Session A's output
4. Session B's close persists Session A's narrative as its own

**Impact:** Cross-contamination of session narratives and work context.

### FM-3: Zombie sessions in developer profile

**Mechanism:**
1. Session starts → adds to `profile.active_sessions`
2. Session crashes/user kills terminal → close never runs
3. Zombie entry persists forever
4. Next session start warns "you have N active sessions" (noise)

**Impact:** Warning fatigue, inaccurate concurrent session count.

### FM-4: No session directory cleanup

**Mechanism:** Each session creates `sessions/{id}/` with state.yaml, signals.jsonl, journal.jsonl. No TTL, no cleanup command, no retention policy.

**Observed:** 53 directories spanning 3 months, two naming formats. At current rate: ~365 dirs/year.

**Impact:** Disk usage, slower glob operations, cognitive load when debugging.

### FM-5: CLAUDE.local.md dead

**Mechanism:** RAISE-821 identified that epic/story close skills should update CLAUDE.local.md. But the file was never generated in the first place — there's no write path.

**Impact:** A whole state synchronization channel (Claude Code → project context) is unused.

### FM-6: Worktree invisibility

**Mechanism:**
1. `.raise/rai/personal/` is gitignored → not shared across worktrees
2. Worktree has its own working tree but shares `.git/`
3. Session in worktree writes to worktree's `.raise/rai/personal/`
4. Main repo's session state is invisible, and vice versa

**Observed:** This session (reliability-2.4 worktree) has NO `.raise/rai/personal/` directory at all. State files don't exist here.

**Impact:** Every worktree session starts blind. No continuity, no context.

### FM-7: Git not used as primary state source

**Reliable git-derived state available but unused:**

```bash
# Current branch → tells you release target + story context
git branch --show-current
# → release/2.4.0 or story/s1248.1/git-state-derivation

# Active epic → from scope.md with in-progress status
grep -rl 'Status.*in.progress' work/epics/*/scope.md
# → work/epics/e1248-git-first-session-state/scope.md

# Last merge → tells you what was completed
git log --oneline --merges -3
# → recent story merges with IDs

# Recent work → what was actually done
git log --oneline -10
# → commit history with story/epic references
```

**Impact:** The bundle could derive 80% of `current_work` from git, but instead depends on a YAML file that may be missing or stale.

## 4. Remediation Classification

| FM | Fix Approach | Complexity | Dependencies |
|----|-------------|-----------|--------------|
| FM-7 | Git state derivation in bundle assembly | M | None — can start here |
| FM-1 | Chain session state via last-session-id pointer | S | FM-7 (derived state reduces importance) |
| FM-2 | Clean session-output.yaml after close | XS | None |
| FM-3 | Zombie reaper on session start (>48h TTL) | S | None |
| FM-4 | Retention policy (keep last N or last 30 days) | S | None |
| FM-5 | Kill CLAUDE.local.md or generate from derived state | S | FM-7 (need derived state first) |
| FM-6 | Worktree-aware path resolution (shared state via .git/) | M | FM-7 (shared git is the bridge) |

## 5. Recommended Story Sequence

1. **Git state derivation** (FM-7) — foundation, everything else depends on this
2. **Zombie reaper + stale cleanup** (FM-3, FM-2, FM-4) — quick wins, independent
3. **Worktree awareness** (FM-6) — needs git derivation in place
4. **CLAUDE.local.md decision** (FM-5) — kill or generate, depends on approach
5. **Session state chaining** (FM-1) — may become unnecessary after FM-7

*Detailed stories to be designed via `/rai-epic-design`*
