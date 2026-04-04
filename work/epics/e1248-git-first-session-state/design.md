# E1248 Design: Git-First Session State

## Gemba Summary

7 failure modes in session state (see `gemba-findings.md`). Root cause: YAML files as source of truth instead of git. 5 of 6 bundle data sources are reliable — the one unreliable source (session-state.yaml) carries the most critical context.

## Target Architecture

### Design Principle: Server-First, Community Retrofit

Design protocols as if the server existed. Implement with git-only backend for community (2.4). Server (3.0/RAISE-1229) provides richer implementations of the same contracts.

### Three Protocols (ADR-038)

```
┌─────────────────────────────────────────────────────────┐
│                   Bundle Assembly                        │
│              (consumes protocols, not files)             │
├──────────────┬──────────────────┬───────────────────────┤
│ StateDeriver │ SessionRegistry  │ WorkstreamMonitor     │
│  .current_   │  .register()     │  .analyze_session()   │
│   work()     │  .active()       │  .suggest_             │
│  .recent_    │  .close()        │   improvements()      │
│   activity() │  .gc()           │                       │
├──────────────┼──────────────────┼───────────────────────┤
│ GitState     │ LocalSession     │ LocalWorkstream       │
│ Deriver      │ Registry         │ Monitor               │
│ (2.4)        │ (2.4)            │ (2.4)                 │
├──────────────┼──────────────────┼───────────────────────┤
│ ServerState  │ ServerSession    │ ServerWorkstream      │
│ Deriver      │ Registry         │ Monitor               │
│ (3.0)        │ (3.0)            │ (3.0)                 │
└──────────────┴──────────────────┴───────────────────────┘
```

### Key Components (New/Modified)

| Component | Location | Action |
|-----------|----------|--------|
| Session protocols | `session/protocols.py` (NEW) | Define StateDeriver, SessionRegistry, WorkstreamMonitor |
| Session models | `schemas/session_state.py` (MODIFY) | Add ActivityEntry, SessionInfo, SessionOutcome, SessionInsights, Improvement |
| Git state deriver | `session/derive.py` (NEW) | Implement StateDeriver from git + scope.md |
| Local registry | `session/registry.py` (NEW) | Implement SessionRegistry with zombie gc |
| Local monitor | `session/monitor.py` (NEW) | Implement WorkstreamMonitor from journal + git log |
| Bundle assembly | `session/bundle.py` (MODIFY) | Consume StateDeriver instead of reading YAML directly |
| Session start command | `cli/commands/session.py` (MODIFY) | Use SessionRegistry for lifecycle, StateDeriver for bundle |
| Session close command | `session/close.py` (MODIFY) | Use SessionRegistry.close(), clean stale files |
| Entry points | `pyproject.toml` (MODIFY) | Register git backends under rai.session.* groups |
| Registry discovery | `adapters/registry.py` (MODIFY) | Add get_state_deriver(), get_session_registry(), get_workstream_monitor() |

### Git State Derivation Logic

```python
class GitStateDeriver:
    """Derive current work from git — the reliable source."""

    def current_work(self, project: Path) -> CurrentWork:
        branch = _git_current_branch()

        # Parse branch for release/story context
        release = _parse_release(branch)      # release/2.4.0 → v2.4.0
        story = _parse_story(branch)          # story/s1248.1/name → S1248.1

        # Find in-progress epics from scope.md frontmatter
        epic = _find_active_epic(project)     # grep Status.*in.progress

        # Infer phase from recent git activity
        phase = _infer_phase(project, branch) # commits → implementing, merge → reviewing

        return CurrentWork(
            release=release,
            epic=epic,
            story=story,
            phase=phase,
            branch=branch,
        )

    def recent_activity(self, project: Path, limit: int = 10) -> list[ActivityEntry]:
        # git log --oneline with story/epic ID extraction
        ...
```

### SessionRegistry Lifecycle

```
Session Start:
  registry.gc(max_age_hours=48)     # Clean zombies first
  registry.register(session_info)   # Then register new session

Session Close:
  registry.close(session_id, outcome)  # Atomic: write index + clear pointer + cleanup

Crash Recovery:
  Next session start calls gc() → removes entries older than 48h
  No manual intervention needed
```

### Worktree Awareness

Git derivation naturally handles worktrees because git commands work identically:
- `git branch --show-current` works in worktree
- `git log` works in worktree
- `scope.md` is in the working tree (shared via git)

For state files that AREN'T in git (active-session, session index), the `LocalSessionRegistry` resolves to the **main repo's** `.raise/rai/personal/` using:

```python
def _resolve_personal_dir(project: Path) -> Path:
    """Resolve personal state dir, handling worktrees."""
    git_common = subprocess.check_output(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=project, text=True
    ).strip()
    # git-common-dir points to the main repo's .git/
    # Derive .raise/rai/personal/ relative to that
    main_repo = Path(git_common).parent
    return main_repo / ".raise" / "rai" / "personal"
```

### CLAUDE.local.md Decision

**Kill it.** Rationale:
- Never implemented (FM-5)
- Bundle assembly via `--context` flag already provides richer context
- StateDeriver makes it redundant — state is derived, not cached in a file
- Removes a whole class of drift bugs (RAISE-821)

Action: remove references, close RAISE-821 as "won't fix — superseded by derived state".

### Session Directory Retention

```python
def gc(self, max_age_hours: int = 48) -> list[str]:
    """Garbage collect stale sessions and old directories."""
    cleaned = []

    # 1. Reap zombie active_sessions from profile
    for session in profile.active_sessions:
        if age(session) > max_age_hours:
            profile.remove_session(session.id)
            cleaned.append(session.id)

    # 2. Clean old session directories (keep last 20 or 30 days)
    dirs = sorted(session_dirs, key=mtime)
    keep = max(20, dirs_within_30_days)
    for d in dirs[:-keep]:
        shutil.rmtree(d)
        cleaned.append(d.name)

    # 3. Delete stale session-output.yaml
    output = personal_dir / "session-output.yaml"
    if output.exists() and age(output) > 24:
        output.unlink()

    return cleaned
```

### Migration Path

1. **session-state.yaml** → Still written by close (backward compat), but bundle reads from StateDeriver first, falls back to YAML
2. **active-session** → Managed by SessionRegistry, same file format
3. **session index** → Managed by SessionRegistry, same JSONL format
4. **CLAUDE.local.md** → References removed, file ignored

No breaking changes. Old state files continue to work. New sessions use protocols.

## Failure Mode Coverage

| FM | Resolution | Story |
|----|-----------|-------|
| FM-1 (state lost) | StateDeriver derives from git — YAML is optional fallback | S1248.1 |
| FM-2 (stale output) | gc() cleans output.yaml older than 24h | S1248.2 |
| FM-3 (zombies) | gc() reaps sessions older than 48h | S1248.2 |
| FM-4 (no cleanup) | gc() with retention policy (20 dirs / 30 days) | S1248.2 |
| FM-5 (CLAUDE.local dead) | Kill it — derived state supersedes | S1248.3 |
| FM-6 (worktree blind) | _resolve_personal_dir() + git derivation | S1248.1 |
| FM-7 (git not primary) | StateDeriver IS git-first | S1248.1 |
