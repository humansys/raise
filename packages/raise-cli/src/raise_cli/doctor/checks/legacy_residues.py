"""LegacyResiduesCheck — session-open-parity legacy residue check (S17495.5).

Mirrors the ``legacy`` field in ``rai session open``:
- scan_project(cwd) only (not global — parity with session open D3)
- snooze-aware: PASS when the set_hash matches the acknowledged hash

Distinct from LegacyInstallCheck which scans project+global and is not
snooze-aware. fix_hint matches what session open shows.
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

# Imported at module level to allow monkeypatching in tests.
from raise_cli.session.open_service import check_legacy_residues

_FIX_HINT = "rai clean --dry-run"


class LegacyResiduesCheck(DoctorCheck):
    """Project-scoped legacy residue check with snooze awareness.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "legacy-residues"
    category: ClassVar[str] = "legacy"
    description: ClassVar[str] = (
        "Legacy residues in project (snooze-aware; mirrors rai session open)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Delegate to check_legacy_residues() — single source of truth."""
        results: list[CheckResult] = []
        try:
            result = check_legacy_residues(context.working_dir, context.working_dir)
        except Exception:  # noqa: BLE001
            self._append_result(
                results, self.check_id, CheckStatus.PASS, "check skipped (error)"
            )
            return results

        if result.status == "warn":
            n = result.data.get("residues", 0)
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                f"{n} legacy residue(s) detected (unacknowledged)",
                _FIX_HINT,
            )
        else:
            n = result.data.get("residues", 0)
            if result.data.get("acknowledged"):
                msg = f"{n} residue(s) — acknowledged (snoozed)"
            elif n == 0:
                msg = "no legacy residues detected"
            else:
                msg = f"{n} residue(s)"
            self._append_result(results, self.check_id, CheckStatus.PASS, msg)
        return results
