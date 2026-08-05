"""Gate that prevents generated graph outputs from entering the Git index."""

from __future__ import annotations

import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

GENERATED_GRAPH_OUTPUTS: tuple[str, ...] = (
    ".raise/cartridges/repo/instances/repo.json",
    ".raise/cartridges/repo/instances/embedding_index.json",
    ".raise/rai/personal/last-build.json",
    ".raise/rai/personal/last-diff.json",
)


class GeneratedArtifactHygieneGate:
    """Block story close when regenerable graph output is Git-tracked."""

    gate_id: ClassVar[str] = "gate-generated-artifact-hygiene"
    description: ClassVar[str] = "Generated graph outputs are absent from Git"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Report any prohibited artifact currently present in the index."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--", *GENERATED_GRAPH_OUTPUTS],
                cwd=context.working_dir,
                capture_output=True,
                check=False,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"could not inspect Git index: {exc}",
            )

        if result.returncode != 0:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="git ls-files failed while checking generated artifacts",
                details=(result.stderr.strip(),),
            )

        tracked = tuple(line for line in result.stdout.splitlines() if line)
        if not tracked:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="generated graph outputs are untracked",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="generated graph output(s) are tracked: " + ", ".join(tracked),
            details=(
                *tracked,
                f"Fix: git rm --cached -- {' '.join(tracked)}",
            ),
        )
