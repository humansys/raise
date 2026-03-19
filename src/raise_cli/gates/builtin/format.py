"""Built-in FormatGate — validates code formatting.

Reads ``format_command`` from ``.raise/manifest.yaml`` and reports pass/fail.

Architecture: ADR-039 §5 (Built-in gates), S474.2
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.gates.builtin._runner import run_manifest_command
from raise_cli.gates.models import GateContext, GateResult


class FormatGate:
    """Quality gate that runs the configured formatter check.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-format"
    description: ClassVar[str] = "Code formatting passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run format check command from manifest and return pass/fail result."""
        return run_manifest_command(
            self.gate_id, "format_command", self.description, context
        )
