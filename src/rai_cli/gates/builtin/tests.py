"""Built-in TestGate — validates all tests pass.

Runs ``pytest -x --tb=short`` and reports pass/fail.

Architecture: ADR-039 §5 (Built-in gates), S248.6
"""

from __future__ import annotations

import subprocess
from typing import ClassVar

from rai_cli.gates.models import GateContext, GateResult


class TestGate:
    """Quality gate that runs pytest.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-tests"
    description: ClassVar[str] = "All tests pass"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run pytest and return pass/fail result."""
        try:
            result = subprocess.run(
                ["pytest", "-x", "--tb=short"],
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
            message="Tests pass" if passed else "Tests failing",
            details=(result.stdout,) if not passed else (),
        )
