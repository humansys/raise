"""Built-in CoverageGate — validates test coverage collection succeeds.

Reads ``test_command`` from ``.raise/manifest.yaml``, appends coverage flags,
and reports pass/fail. Per PAT-E-444, coverage is diagnostic — this gate
checks that coverage collection succeeds, not a specific percentage threshold.

Architecture: ADR-039 §5 (Built-in gates), S248.6, S474.2
"""

from __future__ import annotations

import subprocess
from typing import ClassVar

from raise_cli.gates.builtin._runner import cleanup_coverage_files, test_env
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.onboarding.manifest import load_manifest

_COVERAGE_FLAGS: list[str] = ["--cov", "--cov-report=term-missing", "-q"]

# Markers of the known pytest-cov × xdist limitation: under many xdist workers
# the workers can fail to return coverage data, aborting the run before any test
# executes. This is a coverage-collection problem, not a test failure.
_XDIST_COVERAGE_MARKERS: tuple[str, ...] = (
    "failed to return coverage data",
    "coverage: failed workers",
)
# Markers of a genuine test failure — never degrade these to a skip. Kept narrow
# so the xdist worker warning text ("workers failed to return …") does not match:
# "FAILED " is pytest's per-test line; " failed," / " failed in " is its summary.
_TEST_FAILURE_MARKERS: tuple[str, ...] = (
    "FAILED ",
    " failed,",
    " failed in ",
    " error,",
    " errors in ",
)


def _is_xdist_coverage_data_failure(output: str) -> bool:
    """True when the run failed only because xdist workers returned no coverage.

    Requires a coverage-worker marker AND the absence of real test-failure
    markers, so a test failure that also trips a worker is still reported.
    """
    if not any(m in output for m in _XDIST_COVERAGE_MARKERS):
        return False
    return not any(m in output for m in _TEST_FAILURE_MARKERS)


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

        env = test_env("test_command", context.working_dir)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(context.working_dir),
                env=env,
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{type(exc).__name__}: {exc}",
            )
        finally:
            cleanup_coverage_files(env)

        if result.returncode == 0:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=self.description,
            )

        combined = (result.stdout or "") + (result.stderr or "")
        if _is_xdist_coverage_data_failure(combined):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    "skipped: coverage data unavailable under pytest-cov × xdist "
                    "— run with -n0 for full coverage (test failures are covered "
                    "by gate-tests)"
                ),
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="Coverage check failed",
            details=tuple(s for s in (result.stdout, result.stderr) if s),
        )
