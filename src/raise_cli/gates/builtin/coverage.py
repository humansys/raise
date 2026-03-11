"""Built-in CoverageGate — validates test coverage collection succeeds.

Runs ``pytest --cov --cov-report=term-missing -q`` and reports pass/fail.
Per PAT-E-444, coverage is diagnostic — this gate checks that coverage
collection succeeds, not a specific percentage threshold.

Architecture: ADR-039 §5 (Built-in gates), S248.6
"""

from __future__ import annotations

import shlex
import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.onboarding.manifest import load_manifest

_DEFAULT_TEST_CMD = ["pytest"]
_COV_FLAGS = ["--cov", "--cov-report=term-missing", "-q"]


class CoverageGate:
    """Quality gate that runs pytest with coverage.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-coverage"
    description: ClassVar[str] = "Coverage collection succeeds"
    workflow_point: ClassVar[str] = "before:release:publish"

    def _get_command(self, context: GateContext) -> list[str]:
        manifest = load_manifest(context.working_dir)
        if manifest and manifest.project.test_command:
            base = shlex.split(manifest.project.test_command)
        else:
            base = list(_DEFAULT_TEST_CMD)
        return [*base, *_COV_FLAGS]

    def evaluate(self, context: GateContext) -> GateResult:
        """Run test command with coverage flags and return pass/fail result."""
        try:
            result = subprocess.run(
                self._get_command(context),
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
            message="Coverage collection succeeds"
            if passed
            else "Coverage check failed",
            details=(result.stdout,) if not passed else (),
        )
