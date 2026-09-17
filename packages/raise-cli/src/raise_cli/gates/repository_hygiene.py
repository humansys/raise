"""Gate that prevents regenerable build artifacts from entering the Git index."""

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

# Cartridge instance embedding caches (RAISE-15996) — regenerable via
# `rai cartridge embed`, never committed. A glob pathspec (rather than a
# per-cartridge path list) so newly added cartridges are covered without
# an edit here.
GENERATED_EMBEDDING_CACHES: tuple[str, ...] = ("*.npy",)

# Full pathspec checked against the Git index. Kept as two named tuples
# above so each list documents what it covers; combined only at use.
_TRACKED_ARTIFACT_PATHSPECS: tuple[str, ...] = (
    *GENERATED_GRAPH_OUTPUTS,
    *GENERATED_EMBEDDING_CACHES,
)


class GeneratedArtifactHygieneGate:
    """Block story close when a regenerable build artifact is Git-tracked."""

    gate_id: ClassVar[str] = "gate-generated-artifact-hygiene"
    description: ClassVar[str] = "Regenerable build artifacts are absent from Git"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Report any prohibited artifact currently present in the index."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--", *_TRACKED_ARTIFACT_PATHSPECS],
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
                message="regenerable build artifacts are untracked",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="regenerable build artifact(s) are tracked: " + ", ".join(tracked),
            details=(
                *tracked,
                f"Fix: git rm --cached -- {' '.join(tracked)}",
            ),
        )
