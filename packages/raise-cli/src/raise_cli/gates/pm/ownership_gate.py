"""PMOwnershipGate — guards epic design with a PM ownership requirement.

Checks that the active epic's scope.md contains a non-empty ``## PM Ownership``
section before epic design begins.

Opt-in: skips silently if ``project.pm_gates.enabled`` is not True in
``.raise/manifest.yaml``.

Architecture: RAISE-11404, S11404.3
"""

from __future__ import annotations

import os
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.pm._config import pm_gates_enabled
from raise_cli.gates.pm._utils import extract_section_content, find_active_scope

_SKIP_ENV: str = "RAISE_PM_OWNERSHIP_SKIP_REASON"
_OWNERSHIP_MIN_CHARS: int = 3


class PMOwnershipGate:
    """Quality gate requiring a named PM owner before epic design.

    Fail-open: no scope.md found → passes silently.
    Escape hatch: ``RAISE_PM_OWNERSHIP_SKIP_REASON=<reason>`` → passes with warning.
    """

    gate_id: ClassVar[str] = "gate-pm-ownership"
    description: ClassVar[str] = "PM ownership required before epic design"
    workflow_point: ClassVar[str] = "before:epic:design"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check for a PM Ownership section in the active epic's scope.md."""
        if not pm_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="pm_gates not configured — skipping",
            )

        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        scope_path = find_active_scope(context.working_dir)
        if scope_path is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no scope.md found — skipping",
            )

        content = scope_path.read_text(encoding="utf-8")
        ownership_content = extract_section_content(content, "PM Ownership")

        if len(ownership_content) < _OWNERSHIP_MIN_CHARS:
            rel = scope_path.relative_to(context.working_dir)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"PM Ownership required. Add content to '## PM Ownership' in {rel} "
                    f"(format: '[Name] ([Role])')"
                ),
            )

        return GateResult(passed=True, gate_id=self.gate_id)
