## Design: RAISE-161 — Windows Compatibility Verification

### Problem

rai-cli has never been tested on Windows. Kurigage's .NET tech lead (Sofi) works on Windows. Audit found 1 critical crash, 4 high-severity data corruption risks, and several encoding gaps.

### Value

Unblocks Windows developers from using rai-cli. Required for Kurigage Track 1.

### Approach

**Pattern: `compat.py` anti-corruption layer** — Centralize all platform-specific logic in a single module (`rai_cli/compat.py`). The rest of the codebase imports from `compat` and never checks `sys.platform` directly. Established pattern used by pip, poetry, virtualenv, black.

**No new dependencies** — Platform guard for file locking (`fcntl` on Unix, `msvcrt` on Windows) lives in `compat.py`. No `filelock` dependency.

Steps:
1. Create `rai_cli/compat.py` with platform abstractions
2. Wire all platform-specific code through `compat`
3. Fix encoding gaps (mechanical, no compat needed)
4. Add cross-platform tests for `compat` module

### `compat.py` API

```python
# rai_cli/compat.py

def file_lock(f: IO, exclusive: bool = True) -> None:
    """Acquire file lock. fcntl on Unix, msvcrt on Windows."""

def file_unlock(f: IO) -> None:
    """Release file lock. fcntl on Unix, msvcrt on Windows."""

def portable_path(path: Path, relative_to: Path) -> str:
    """Return forward-slash relative path string for serialization."""
    return path.relative_to(relative_to).as_posix()

def to_file_uri(path: Path) -> str:
    """Return correct file:// URI on any platform."""
    return path.resolve().as_uri()

def secure_permissions(path: Path) -> None:
    """Set restrictive permissions. chmod on Unix, no-op on Windows."""
```

### Findings & Fixes

#### CRITICAL — Hard crash on import

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `telemetry/writer.py` | `import fcntl` — Unix-only | Use `compat.file_lock/file_unlock` |

#### HIGH — Data corruption or silent failure

| # | File(s) | Issue | Fix |
|---|---------|-------|-----|
| 2 | `rai_pro/providers/auth/credentials.py` | `chmod(0o600)` no-op on Windows | Use `compat.secure_permissions` |
| 3 | `publish/check.py` | `shell=True` + glob in cmd.exe | Out of scope — CI-only (Linux) |
| 4 | Multiple parsers, builder, scanner (~15 sites) | `str(path.relative_to(...))` → backslashes | Use `compat.portable_path` |
| 5 | `cli/commands/memory.py` | `file://` URI malformed | Use `compat.to_file_uri` |

#### MEDIUM — Encoding

| # | File(s) | Issue | Fix |
|---|---------|-------|-----|
| 6-8 | ~20 call sites across src/ | `write_text()`/`read_text()` without `encoding="utf-8"` | Add `encoding="utf-8"` (no compat needed) |

#### LOW — Deferred

| # | Issue | Rationale |
|---|-------|-----------|
| 9-10 | Hardcoded `/home/...` in test fixtures | Fix when Windows CI exists |

### Acceptance Criteria

**MUST:**
- `compat.py` exists with platform abstractions
- All platform-specific code routes through `compat`
- All serialized paths use forward slashes
- All file I/O specifies `encoding="utf-8"`
- `import rai_cli` succeeds without `fcntl` (testable via mock)
- Existing tests pass unchanged

**MUST NOT:**
- Scatter `sys.platform` checks across modules
- Add external dependencies
- Touch `publish/check.py` or test fixtures

### Governance

**New guardrail candidate:** "Platform-specific code MUST go through `rai_cli/compat.py`. No direct `sys.platform` checks outside `compat`."
