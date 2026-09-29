"""Doctor checks for graph_node_annotations health (RAISE-17923).

RAISE-17909 found two symptoms nothing detected automatically until a human
tripped over them: an always-NULL nullable column (ddd_tactical_type, dead
since V79/RAISE-16915 — fixed by dropping it in V81, RAISE-17923 S1) and
namespaces writing under an undocumented checkout_id scope (ADR-148 D2 makes
"ddd"/"ddd_tactical" REPO_WIDE on purpose; any other namespace claiming
REPO_WIDE has no ADR decision behind it, and any of those two namespaces
found per-checkout means D2 was silently violated).

These two checks generalize past the specific ddd_tactical_type incident so
the *next* orphaned column or scoping violation surfaces here instead of
requiring another gemba walk.
"""

from __future__ import annotations

import sqlite3
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.storage.connection import get_project_db_path

# Structural columns every row always has a value for by construction (PK
# parts, JSON default, or NOT NULL with a DEFAULT). Excluded from the
# always-NULL scan — flagging them would be noise, not signal.
_STRUCTURAL_COLUMNS = frozenset(
    {
        "project_id",
        "checkout_id",
        "node_id",
        "namespace",
        "payload_json",
        "created_at",
        "updated_at",
    }
)

# ADR-148 D2: these namespaces are REPO_WIDE (checkout_id == '') on purpose —
# DDD classification is a property of a symbol's content, not its worktree.
# Any namespace NOT in this set that has REPO_WIDE rows has no ADR decision
# behind that choice (RAISE-17923 S3).
_DOCUMENTED_REPO_WIDE_NAMESPACES = frozenset({"ddd", "ddd_tactical"})

_REPO_WIDE = ""


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


class GraphAnnotationAlwaysNullColumnCheck(DoctorCheck):
    """Warn when a nullable column in graph_node_annotations is NULL on every row.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "graph-annotation-always-null-column"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = (
        "graph_node_annotations columns that are NULL on every row (orphaned schema)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan graph_node_annotations for columns that are NULL on every row."""
        db_path = get_project_db_path(context.working_dir)
        if not db_path.exists():
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no local graph DB yet — nothing to check",
                )
            ]
        conn = sqlite3.connect(str(db_path))
        try:
            if not _table_exists(conn, "graph_node_annotations"):
                return [
                    CheckResult(
                        check_id=self.check_id,
                        category=self.category,
                        status=CheckStatus.PASS,
                        message="graph_node_annotations table not present yet",
                    )
                ]
            total = conn.execute(
                "SELECT COUNT(*) FROM graph_node_annotations"
            ).fetchone()[0]
            if total == 0:
                return [
                    CheckResult(
                        check_id=self.check_id,
                        category=self.category,
                        status=CheckStatus.PASS,
                        message="graph_node_annotations is empty — nothing to check",
                    )
                ]
            columns = [
                row[1]
                for row in conn.execute("PRAGMA table_info(graph_node_annotations)")
                if row[1] not in _STRUCTURAL_COLUMNS
            ]
            always_null: list[str] = []
            for col in columns:
                non_null = conn.execute(
                    f"SELECT COUNT(*) FROM graph_node_annotations WHERE {col} IS NOT NULL"  # noqa: S608  # nosec B608 — col is from a hardcoded schema list
                ).fetchone()[0]
                if non_null == 0:
                    always_null.append(col)
        finally:
            conn.close()

        if not always_null:
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no always-NULL columns in graph_node_annotations",
                )
            ]
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    f"{len(always_null)} always-NULL column(s) in "
                    f"graph_node_annotations: {', '.join(sorted(always_null))} "
                    f"(out of {total} rows)"
                ),
                fix_hint=(
                    "verify no reader/writer uses this column (grep the codebase) "
                    "and drop it in a schema migration if genuinely orphaned"
                ),
            )
        ]


class GraphAnnotationScopingDriftCheck(DoctorCheck):
    """Warn when a graph_node_annotations namespace violates its documented checkout_id scope.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "graph-annotation-scoping-drift"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = (
        "graph_node_annotations namespaces writing outside their documented "
        "checkout_id scope (ADR-148 D2)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Flag graph_node_annotations namespaces outside their documented checkout_id scope."""
        db_path = get_project_db_path(context.working_dir)
        if not db_path.exists():
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no local graph DB yet — nothing to check",
                )
            ]
        conn = sqlite3.connect(str(db_path))
        try:
            if not _table_exists(conn, "graph_node_annotations"):
                return [
                    CheckResult(
                        check_id=self.check_id,
                        category=self.category,
                        status=CheckStatus.PASS,
                        message="graph_node_annotations table not present yet",
                    )
                ]
            rows = conn.execute(
                """
                SELECT namespace,
                       SUM(CASE WHEN checkout_id = ? THEN 1 ELSE 0 END) AS repo_wide,
                       SUM(CASE WHEN checkout_id != ? THEN 1 ELSE 0 END) AS per_checkout
                FROM graph_node_annotations
                GROUP BY namespace
                """,
                (_REPO_WIDE, _REPO_WIDE),
            ).fetchall()
        finally:
            conn.close()

        violations: list[str] = []
        for namespace, repo_wide, per_checkout in rows:
            documented_repo_wide = namespace in _DOCUMENTED_REPO_WIDE_NAMESPACES
            if documented_repo_wide and per_checkout:
                violations.append(
                    f"{namespace!r} is documented REPO_WIDE (ADR-148 D2) but has "
                    f"{per_checkout} per-checkout row(s)"
                )
            elif not documented_repo_wide and repo_wide:
                violations.append(
                    f"{namespace!r} has {repo_wide} REPO_WIDE row(s) but is not in "
                    "the documented REPO_WIDE namespace list — no ADR decision "
                    "backs this scope choice"
                )

        if not violations:
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="all namespaces respect their documented checkout_id scope",
                )
            ]
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=f"{len(violations)} namespace scoping violation(s)",
                details=tuple(violations),
                fix_hint=(
                    "either fix the write path's checkout_id argument, or update "
                    "_DOCUMENTED_REPO_WIDE_NAMESPACES with a new ADR decision"
                ),
            )
        ]
