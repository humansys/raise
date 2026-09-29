"""Cross-process test-worker budget — RAISE-10544 (E10436).

When several agents run test gates on one machine at once, each launching
pytest-xdist with ``-n auto``, the box is oversubscribed (N×cores workers on
cores cores). This module is a lock-guarded ledger of granted workers shared
across all worktrees/agents via a single file in the rai home.

Semantics, by design:
- A **lone** run (no other live claim) claims the whole budget and stays
  *unbounded* — it keeps ``-n auto`` for full speed, and existing single-run
  behavior is unchanged.
- A run that starts **while another holds budget** is *bounded* to the cores
  that remain, so concurrent agents stop summing past the core count.
- Crashed runs never leak budget: claims held by dead PIDs are reaped on the
  next ``acquire``.

This closes the gap left by S2 (RAISE-10439), whose ``RAISE_TEST_WORKERS`` lever
was opt-in and per-process with no cross-agent coordination. An explicit
``RAISE_TEST_WORKERS`` still wins at the call site (see ``_runner.worker_lease``);
this module is the default-on governor for the unset case.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any
from uuid import uuid4

_logger = logging.getLogger(__name__)

# Minimum workers a contended run still gets — a throttled run should make
# progress, not crawl at -n 1.
_FLOOR = 2


def _budget_file() -> Path:
    """Path to the shared ledger (overridable via env for tests/tuning)."""
    override = os.environ.get("RAISE_WORKER_BUDGET_FILE", "").strip()
    if override:
        return Path(override)
    from raise_cli.config.paths import get_global_rai_dir

    return get_global_rai_dir() / "test-worker-budget.json"


def total_budget() -> int:
    """Total worker budget for this machine.

    ``RAISE_TEST_WORKER_BUDGET`` overrides; otherwise ``cpu_count - 1`` to leave
    a core for the OS/coordinator.
    """
    override = os.environ.get("RAISE_TEST_WORKER_BUDGET", "").strip()
    if override.isdigit() and int(override) > 0:
        return int(override)
    return max(1, (os.cpu_count() or 2) - 1)


def _pid_alive(pid: int) -> bool:
    """True if a process with *pid* exists (signal 0 probe)."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@dataclass(frozen=True)
class Grant:
    """A budget grant. ``bounded`` is True when the run was throttled below full."""

    workers: int
    token: str
    bounded: bool


def _load(fh: IO[str]) -> dict[str, Any]:
    fh.seek(0)
    raw = fh.read()
    if not raw.strip():
        return {"grants": {}}
    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        return {"grants": {}}
    data.setdefault("grants", {})
    return data


def _save(fh: IO[str], data: dict[str, Any]) -> None:
    fh.seek(0)
    fh.truncate()
    fh.write(json.dumps(data))
    fh.flush()


def _lock_exclusive(fh: IO[str]) -> None:
    """Take an exclusive lock on *fh*, on whichever platform we are.

    ``fcntl`` is Unix-only and ``msvcrt`` is Windows-only, so both imports are
    lazy — importing either at module scope made ``rai gate check`` die on the
    other platform before running a single gate (RAISE-15653).

    Windows has no whole-file advisory lock, so the first byte stands in for
    the file. Every writer here goes through this same function, so locking a
    single agreed byte gives the same mutual exclusion as ``flock``.

    The branch is chosen at runtime rather than by ``sys.platform`` so the
    Windows path stays reachable from tests on Linux.
    """
    try:
        import fcntl
    except ModuleNotFoundError:
        pass
    else:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        return

    try:
        import msvcrt
    except ModuleNotFoundError:
        # Neither backend: no cross-process exclusion available. The ledger is
        # advisory — a lost update costs parallelism, never correctness — so
        # degrade rather than refuse to run gates.
        _logger.debug("worker_budget: no file locking on this platform")
        return

    fh.seek(0)
    # Typeshed guards msvcrt's members behind sys.platform == "win32", so a
    # Linux typecheck cannot see them at all. Widening to Any says that
    # plainly instead of scattering per-line ignores.
    win: Any = msvcrt
    win.locking(fh.fileno(), win.LK_LOCK, 1)


def _unlock(fh: IO[str]) -> None:
    """Release what :func:`_lock_exclusive` took. Never raises."""
    with contextlib.suppress(OSError, ModuleNotFoundError):
        try:
            import fcntl
        except ModuleNotFoundError:
            import msvcrt

            fh.seek(0)
            win: Any = msvcrt
            win.locking(fh.fileno(), win.LK_UNLCK, 1)
        else:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def _locked() -> Iterator[IO[str]]:
    """Open the ledger with an exclusive lock held for the block."""
    path = _budget_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(path, "a+", encoding="utf-8")  # noqa: SIM115 — closed in finally
    try:
        _lock_exclusive(fh)
        yield fh
    finally:
        _unlock(fh)
        fh.close()


def acquire(requested: int) -> Grant:
    """Claim up to *requested* workers from the shared budget.

    Reaps dead PIDs first. A lone claim takes the whole budget unbounded; a
    contended claim is throttled to the remaining cores (at least ``_FLOOR``).
    """
    total = total_budget()
    requested = max(1, requested)
    with _locked() as fh:
        data = _load(fh)
        grants: dict[str, Any] = data["grants"]
        for tok in list(grants):
            if not _pid_alive(int(grants[tok]["pid"])):
                del grants[tok]
        in_use = sum(int(g["n"]) for g in grants.values())
        if in_use <= 0:
            workers = min(requested, total)
            bounded = False
        else:
            remaining = total - in_use
            workers = max(
                _FLOOR, min(requested, remaining if remaining > 0 else _FLOOR)
            )
            bounded = True
        token = uuid4().hex
        grants[token] = {"pid": os.getpid(), "n": workers}
        _save(fh, data)
        grant = Grant(workers=workers, token=token, bounded=bounded)
        if bounded:
            _logger.warning(
                "worker_budget: run bounded to %d workers "
                "(total=%d, in_use=%d); set RAISE_TEST_WORKER_BUDGET to override",
                workers,
                total,
                in_use,
            )
        return grant


def release(token: str) -> None:
    """Release a previously-acquired grant."""
    with _locked() as fh:
        data = _load(fh)
        if data["grants"].pop(token, None) is not None:
            _save(fh, data)


@contextlib.contextmanager
def lease(requested: int) -> Iterator[Grant]:
    """Acquire a grant for the duration of the block, releasing on exit."""
    grant = acquire(requested)
    try:
        yield grant
    finally:
        release(grant.token)
