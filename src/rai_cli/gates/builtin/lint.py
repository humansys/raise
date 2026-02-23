"""Built-in LintGate — validates linting passes.

Runs ``ruff check .`` and reports pass/fail.

Architecture: ADR-039 §5 (Built-in gates), S248.6
"""

from __future__ import annotations

import logging
import subprocess
from typing import ClassVar

from rai_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)


class LintGate:
    """Quality gate that runs ruff.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-lint"
    description: ClassVar[str] = "Linting passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run ruff check and return pass/fail result."""
        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                capture_output=True,
                text=True,
                cwd=str(context.working_dir),
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{type(exc).__name__}: {exc}",
            )

        passed = result.returncode == 0
        return GateResult(
            passed=passed,
            gate_id=self.gate_id,
            message="Linting passes" if passed else "Lint errors found",
            details=(result.stdout,) if not passed else (),
        )
