"""Built-in CoverageGate — validates test coverage collection succeeds.

Reads ``test_command`` from ``.raise/manifest.yaml``, appends coverage flags,
and reports pass/fail. Per PAT-E-444, coverage is diagnostic — this gate
checks that coverage collection succeeds, not a specific percentage threshold.

Architecture: ADR-039 §5 (Built-in gates), S248.6, S474.2
"""

from __future__ import annotations

import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.onboarding.manifest import load_manifest

_COVERAGE_FLAGS: list[str] = ["--cov", "--cov-report=term-missing", "-q"]


class CoverageGate:
    """Quality gate that runs the test command with coverage flags.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-coverage"
    description: ClassVar[str] = "Coverage collection succeeds"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run test command + coverage flags and return pass/fail result."""
        manifest = load_manifest(context.working_dir)
        if manifest is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="No .raise/manifest.yaml found",
            )

        test_command = manifest.project.test_command
        if test_command is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="Skipped — test_command not configured",
            )

        cmd = test_command.split() + _COVERAGE_FLAGS

        try:
            result = subprocess.run(
                cmd,
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
            message=self.description if passed else "Coverage check failed",
            details=tuple(s for s in (result.stdout, result.stderr) if s)
            if not passed
            else (),
        )
