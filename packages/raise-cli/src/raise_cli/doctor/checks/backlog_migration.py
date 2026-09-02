"""UnmigratedBacklogCheck — filesystem/SQLite backlog parity (RAISE-16625).

Post-migration (S16533.4), filesystem YAML files stay on disk (deletion is
out of scope for E4) — so counting files alone cannot distinguish "migrated
but files kept" from "never migrated". This check compares filesystem keys
against `work_items.local_key` to catch the latter.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.storage.work_items import WorkItemStore

_FIX_HINT = "run: rai backlog migrate"


def _collect_yaml_paths(backlog_root: Path) -> list[Path]:
    """Return every backlog YAML path: hierarchy (e*/*.yaml) + legacy items/."""
    paths: list[Path] = []
    for epic_dir in sorted(backlog_root.glob("e*/")):
        if epic_dir.is_dir():
            paths.extend(sorted(epic_dir.glob("*.yaml")))
    items_dir = backlog_root / "items"
    if items_dir.is_dir():
        paths.extend(sorted(items_dir.glob("*.yaml")))
    return paths


def _extract_key(path: Path) -> str | None:
    """Parse just enough of a backlog YAML file to read its `key` field.

    Returns None on any parse failure — doctor checks must not crash on
    malformed files (they are diagnosed elsewhere, e.g. `rai backlog migrate`).
    """
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — best-effort scan, not authoritative
        return None
    if not isinstance(raw, dict):
        return None
    key = raw.get("key")
    return key if isinstance(key, str) else None


class UnmigratedBacklogCheck(DoctorCheck):
    """Warn when filesystem backlog items have no matching SQLite row.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "unmigrated-backlog"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = (
        "filesystem backlog items not yet migrated to SQLite (work_items)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Compare filesystem backlog keys against work_items.local_key.

        No `.raise/backlog/` directory, or a directory with no YAML files,
        is a PASS (community projects without a filesystem backlog, or a
        project that never had filesystem items).
        """
        backlog_root = context.working_dir / ".raise" / "backlog"
        if not backlog_root.is_dir():
            return [self._pass_result("no filesystem backlog directory found")]

        yaml_paths = _collect_yaml_paths(backlog_root)
        if not yaml_paths:
            return [self._pass_result("no filesystem backlog YAML files found")]

        fs_keys = {
            key for path in yaml_paths if (key := _extract_key(path)) is not None
        }
        if not fs_keys:
            return [self._pass_result("no filesystem backlog YAML files found")]

        try:
            store = WorkItemStore(context.working_dir)
            db_keys = {item.local_key for item in store.list_all()}
        except Exception as exc:  # noqa: BLE001 — report cleanly, never crash doctor
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.ERROR,
                    message=f"could not read work_items store: {exc}",
                )
            ]

        unmigrated = fs_keys - db_keys
        if not unmigrated:
            return [self._pass_result("all filesystem backlog items are migrated")]

        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    f"{len(unmigrated)} filesystem backlog item(s) not migrated to SQLite"
                ),
                fix_hint=_FIX_HINT,
                details=tuple(sorted(unmigrated)),
            )
        ]

    def _pass_result(self, message: str) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            category=self.category,
            status=CheckStatus.PASS,
            message=message,
        )
