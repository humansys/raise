"""LegacyWorkItemsCheck — detects pre-V72 `work_items` rows with `project_id=''` (RAISE-17264).

RAISE-16622 (V72) added `project_id` scoping to `work_items`. Reads are
lenient during the compat window (D-S2.2, `WorkItemStore`): a row is visible
whether it belongs to the caller's project or is a legacy `''` row. This is
correct for individual-key lookups (`get_by_local_key`, `get_by_jira_key`,
...) but `list_all()` — used to seed a NEW project's backlog and its local
counters — has no way to tell "my project's legacy rows" from "some OTHER
project's legacy rows": every `project_id=''` row is visible to every
project until claimed. A client who used `rai` before V72, running `rai
init` in a brand-new project, sees items from unrelated projects mixed into
their backlog.

This check flags the underlying condition — any `project_id=''` row still
unclaimed in the shared `~/.rai/raise.db` — and points at the existing fix,
`rai backlog migrate`, which claims legacy rows into their owning project
(`WorkItemStore.claim_legacy_row`).
"""

from __future__ import annotations

import sqlite3
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.storage.connection import get_project_db

_FIX_HINT = (
    "run: rai backlog migrate — in each project that originally created "
    "these items — to claim them into that project's scope"
)


class LegacyWorkItemsCheck(DoctorCheck):
    """Warn when unclaimed pre-V72 `project_id=''` rows exist in `work_items`.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "legacy-work-items"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = (
        "unclaimed pre-V72 work_items rows (project_id='') that can leak "
        "across projects"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Count `project_id=''` rows in the shared `work_items` table.

        A missing `work_items` table (fresh install, schema never applied)
        is a PASS, not an ERROR — there is nothing to migrate yet.
        """
        conn = get_project_db(context.working_dir)
        try:
            count, sample_keys = self._count_legacy_rows(conn)
        finally:
            conn.close()

        if count == 0:
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no unclaimed legacy work_items rows found",
                )
            ]
        details = tuple(f"sample: {k}" for k in sample_keys)
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    f"{count} legacy work_items row(s) with project_id='' — "
                    "these are visible to every project until claimed"
                ),
                fix_hint=_FIX_HINT,
                details=details,
            )
        ]

    def _count_legacy_rows(self, conn: sqlite3.Connection) -> tuple[int, list[str]]:
        try:
            row = conn.execute(
                "SELECT COUNT(*) FROM work_items WHERE project_id = ''"
            ).fetchone()
            samples = conn.execute(
                "SELECT COALESCE(jira_key, local_key) FROM work_items "
                "WHERE project_id = '' LIMIT 5"
            ).fetchall()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc):
                return 0, []
            raise
        count = int(row[0]) if row is not None else 0
        sample_keys = [str(s[0]) for s in samples]
        return count, sample_keys
