"""LocalDbCheck — detects orphaned per-project SQLite DBs (S8204.3).

The global DB (``~/.rai/raise.db``) is the single source of truth since
E3937/E8204. Any live per-project DB means a legacy writer is still active
or data is stranded — both recoverable via ``rai db consolidate``.

Reuses ``discover_sources()`` so "what counts as an orphan DB" has exactly
one definition (markers, backups, and 0-byte files are excluded there).
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.storage.consolidate import discover_sources

_FIX_HINT = "run: rai db consolidate (merge verificado a ~/.rai/raise.db)"


class LocalDbCheck(DoctorCheck):
    """Warn when orphaned per-project SQLite DBs exist.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "local-db"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = "orphaned per-project SQLite DBs (global DB is SoT)"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan the project tree for orphaned per-project DBs.

        Scoped to project-local and worktree sources — ``~/.rai/projects``
        partitions are historical and already reported by
        ``rai db consolidate --dry-run``.
        """
        sources = [
            s
            for s in discover_sources(context.working_dir)
            if s.kind in ("project-local", "worktree")
        ]
        if not sources:
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no per-project SQLite DBs — global DB is the only store",
                )
            ]
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    f"{len(sources)} per-project SQLite DB(s) found — "
                    "data may be stranded outside the global DB"
                ),
                fix_hint=_FIX_HINT,
                details=tuple(f"[{s.kind}] {s.path}" for s in sources),
            )
        ]
