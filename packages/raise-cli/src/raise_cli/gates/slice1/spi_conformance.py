"""FF-S1: SPI conformance gate (RAISE-15093).

Runs the raise-agent-spi conformance suite via subprocess and fails if any
test fails. Fail-closed: any error (missing package, subprocess crash)
returns ``passed=False``.
"""

from __future__ import annotations

import logging
import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_CONFORMANCE_DIR = "packages/raise-agent-spi/tests/conformance/"


class SPIConformanceGate:
    """SPI conformance suite passes for all runner implementations."""

    gate_id: ClassVar[str] = "ff-s1-spi-conformance"
    description: ClassVar[str] = (
        "SPI conformance suite passes for all runner implementations"
    )
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run ``pytest packages/raise-agent-spi/tests/conformance/ -v``."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"SPI conformance gate error: {exc}",
            )

    def _evaluate(self, context: GateContext) -> GateResult:
        conformance_path = context.working_dir / _CONFORMANCE_DIR
        if not conformance_path.is_dir():
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="Conformance directory not found",
                details=(f"Expected: {conformance_path}",),
            )

        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--project",
                    str(context.working_dir / "packages" / "raise-agent-spi"),
                    "python",
                    "-m",
                    "pytest",
                    str(conformance_path),
                    "-v",
                    "--tb=short",
                    "--no-header",
                ],
                capture_output=True,
                text=True,
                cwd=str(context.working_dir),
                timeout=120,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("SPI conformance gate error: %s", exc)
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"SPI conformance suite failed to execute: {exc}",
            )

        if result.returncode != 0:
            # Collect last N lines of output for actionable detail
            output_lines = (result.stdout + result.stderr).strip().splitlines()
            tail = output_lines[-20:] if len(output_lines) > 20 else output_lines
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="SPI conformance suite failed",
                details=tuple(tail),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="SPI conformance suite passed",
        )
