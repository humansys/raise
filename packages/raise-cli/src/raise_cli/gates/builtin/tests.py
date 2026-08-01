"""Built-in TestGate — validates all tests pass.

Reads ``test_command`` from ``.raise/manifest.yaml`` and reports pass/fail.

Architecture: ADR-039 §5 (Built-in gates), S248.6, S474.2
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.gates.builtin._runner import run_manifest_command
from raise_cli.gates.models import GateContext, GateResult


class TestGate:
    """Quality gate that runs the configured test command.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-tests"
    description: ClassVar[str] = "All tests pass"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run test command from manifest and return pass/fail result."""
        return run_manifest_command(
            self.gate_id, "test_command", self.description, context
        )
