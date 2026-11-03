"""StorageHealthCheck — raise.db size and dead graph partitions (RAISE-18989).

On 2026-10-17 ``~/.rai/raise.db`` held 193 orphan checkout partitions (3.64M
nodes) and nothing reported it: the growth was found by hand. This check is
the Detect action from the RAISE-18985 PIR — it reads the host-wide DB
(read-only) and warns when it is oversized or when graph partitions point at
checkouts that no longer exist, across every project on the host.

Never writes: remediation is ``rai graph prune``, run deliberately.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.storage.connection import get_project_db_path

SIZE_WARN_BYTES = 2 * 1024**3  # 2 GiB, DB + WAL

_PRUNE_HINT = (
    "cd into a live checkout of each listed project and run "
    "rai graph prune --dry-run, then --yes; projects with no checkout left "
    "need --all-projects (RAISE-18985). Full list: rai doctor --json"
)
_SIZE_HINT = (
    "prune dead partitions (rai graph prune), then reclaim space in a quiet window"
)
_MAX_DETAILS = 10


def _path_is_gone(path: str) -> bool:
    """True only when ``path`` is absolute and provably absent (PAT-E-10194).

    Relative paths and any stat error other than not-found count as present,
    so an unreadable path is never reported as dead. A volume whose mount
    point itself is missing does stat as not-found and is reported.
    """
    candidate = Path(path)
    if not candidate.is_absolute():
        return False
    try:
        candidate.stat()
    except (FileNotFoundError, NotADirectoryError):
        return True
    except (OSError, ValueError):
        return False
    return False


def _db_size(db_path: Path) -> int:
    wal = db_path.with_name(db_path.name + "-wal")
    return db_path.stat().st_size + (wal.stat().st_size if wal.exists() else 0)


def _dead_partitions(db_path: Path) -> list[tuple[str, str]]:
    """(project_id, checkout_id) pairs whose checkout path is provably gone."""
    conn = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT DISTINCT project_id, checkout_id FROM graph_nodes "
            "WHERE checkout_id != ''"
        ).fetchall()
    finally:
        conn.close()
    return [(str(p), str(c)) for p, c in rows if _path_is_gone(str(c))]


class StorageHealthCheck(DoctorCheck):
    """Warn on an oversized raise.db or graph partitions of deleted checkouts.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "storage-health"
    category: ClassVar[str] = "environment"
    description: ClassVar[str] = "raise.db size and dead graph checkout partitions"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Inspect the host-wide DB without writing to it."""
        db_path = get_project_db_path(context.working_dir)
        if not db_path.exists():
            return [
                self._result(CheckStatus.PASS, "no raise.db yet — nothing to check")
            ]
        try:
            size = _db_size(db_path)
            dead = _dead_partitions(db_path)
        except (OSError, sqlite3.Error) as exc:
            return [
                self._result(
                    CheckStatus.WARN,
                    f"could not inspect raise.db ({type(exc).__name__}: {exc})",
                )
            ]
        return [self._size_result(size), self._partition_result(dead)]

    def _result(
        self,
        status: CheckStatus,
        message: str,
        fix_hint: str = "",
        details: tuple[str, ...] = (),
    ) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            category=self.category,
            status=status,
            message=message,
            fix_hint=fix_hint,
            details=details,
        )

    def _size_result(self, size: int) -> CheckResult:
        mib = size / 1024**2
        if size > SIZE_WARN_BYTES:
            limit = SIZE_WARN_BYTES / 1024**2
            return self._result(
                CheckStatus.WARN,
                f"raise.db is {mib:,.0f} MiB (DB + WAL), above the {limit:,.0f} MiB threshold",
                fix_hint=_SIZE_HINT,
            )
        return self._result(CheckStatus.PASS, f"raise.db size {mib:,.1f} MiB")

    def _partition_result(self, dead: list[tuple[str, str]]) -> CheckResult:
        if not dead:
            return self._result(CheckStatus.PASS, "no dead graph checkout partitions")
        tmp_root = str(Path(tempfile.gettempdir()).resolve())
        under_tmp = sum(
            1 for _, c in dead if c == tmp_root or c.startswith(tmp_root + "/")
        )
        details = tuple(f"[{p}] {c}" for p, c in dead[:_MAX_DETAILS])
        if len(dead) > _MAX_DETAILS:
            details += (f"… and {len(dead) - _MAX_DETAILS} more",)
        projects = sorted({p for p, _ in dead})
        shown = ", ".join(projects[:_MAX_DETAILS])
        if len(projects) > _MAX_DETAILS:
            shown += ", …"
        return self._result(
            CheckStatus.WARN,
            f"{len(dead)} dead checkout partition(s) across {len(projects)}"
            f" project(s) ({under_tmp} under {tmp_root}): {shown}",
            fix_hint=_PRUNE_HINT,
            details=details,
        )
