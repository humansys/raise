"""LegacyInstallCheck — detects legacy install residues (S16227.1).

Presents ``scan_project()`` + ``scan_global()`` results as doctor
``CheckResult`` objects grouped by residue family.  Status is always
WARN (never ERROR) -- legacy residues are advisory, not blocking.

No ``fix_id`` is registered -- ``rai doctor --fix`` never cleans legacy
residues.  The ``fix_hint`` points to ``rai clean --dry-run`` (D1).

Architecture: Epic RAISE-16227 design §S1, I3.
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.legacy.models import FAMILY_BY_KIND, Residue

_FIX_HINT = "run: rai clean --dry-run"


class LegacyInstallCheck(DoctorCheck):
    """Detect legacy install residues: old venvs, stale configs, orphan DBs.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "legacy-install"
    category: ClassVar[str] = "legacy"
    description: ClassVar[str] = (
        "Legacy install residues (old venvs, stale configs, orphan DBs)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan project + global and present one CheckResult per family."""
        from raise_cli.legacy.scanner import scan_global, scan_project

        report = scan_project(context.working_dir)

        # Also include global residues (pipx, user-site, etc.)
        try:
            global_residues = scan_global()
            all_residues = report.residues + global_residues
        except Exception:  # noqa: BLE001
            all_residues = report.residues

        if not all_residues:
            return [
                CheckResult(
                    check_id="legacy-clean",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no legacy install residues detected",
                )
            ]

        # Group by family
        families: dict[str, list[Residue]] = {}
        for r in all_residues:
            family = FAMILY_BY_KIND[r.kind]
            families.setdefault(family, []).append(r)

        results: list[CheckResult] = []
        for family, residues in sorted(families.items()):
            details = tuple(
                f"{r.kind}: {r.path} -- {r.action_hint}"
                if r.action_hint
                else f"{r.kind}: {r.path}"
                for r in residues
            )
            results.append(
                CheckResult(
                    check_id=f"legacy-{family}",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=f"{len(residues)} legacy residue(s) in {family}",
                    fix_hint=_FIX_HINT,
                    details=details,
                )
            )

        return results
