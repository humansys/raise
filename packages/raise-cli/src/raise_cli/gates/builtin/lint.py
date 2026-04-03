"""Built-in LintGate — validates linting passes.

Reads ``lint_command`` from ``.raise/manifest.yaml`` and reports pass/fail.

Architecture: ADR-039 §5 (Built-in gates), S248.6, S474.2
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.gates.builtin._runner import run_manifest_command
from raise_cli.gates.models import GateContext, GateResult


class LintGate:
    """Quality gate that runs the configured linter.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-lint"
    description: ClassVar[str] = "Linting passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run lint command from manifest and return pass/fail result."""
        return run_manifest_command(
            self.gate_id, "lint_command", self.description, context
        )
