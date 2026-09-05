"""LinterSuppressionGate — CAND-03 drift detector.

Rule: module contains ≥2 distinct files with ``# noqa: C901`` suppressions.
Advisory: returns passed=True with violation details.
"""

from __future__ import annotations

from pathlib import Path

from raise_cli.gates.drift._base import (
    DriftGate,
    has_ignore_marker,
    is_excluded,
    scoped_rglob,
)
from raise_cli.gates.models import GateContext, GateResult

_SUPPRESSION = "# noqa: C901"


def _count_suppression_files(
    root: Path, changed_files: tuple[Path, ...] | None = None
) -> list[Path]:
    """Return paths of .py files containing the C901 suppression marker."""
    result: list[Path] = []
    for p in scoped_rglob(root, "*.py", changed_files):
        if is_excluded(p, root) or has_ignore_marker(p):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _SUPPRESSION in text:
            result.append(p)
    return result


class LinterSuppressionGate(DriftGate):
    """Flags modules with ≥2 files suppressing cyclomatic-complexity warnings.

    Evidence: κ=0.802, precision=0.25 (E2161 CAND-03).
    """

    gate_id = "drift-linter-suppression"
    description = "Linter C901 suppression clustering (CAND-03)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for noqa: C901 clustering in working_dir."""
        flagged = _count_suppression_files(context.working_dir, context.changed_files)
        if len(flagged) < 2:
            return GateResult(
                passed=True, gate_id=self.gate_id, message="No violations"
            )
        violations = [str(p.relative_to(context.working_dir)) for p in flagged]
        return self._advisory(self.gate_id, violations)
