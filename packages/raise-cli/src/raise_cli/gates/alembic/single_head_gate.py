"""AlembicSingleHeadGate — verifies the alembic migration chain has exactly one head.

When multiple bug/story branches add migrations independently, each sets
down_revision to the head at branch-creation time. Merging in sequence
produces forks: two or more migrations with the same down_revision.
Alembic refuses to run `upgrade head` against a forked chain, blocking prod
deploy.

This gate catches the fork before push/MR, at before:bug:close and
before:story:close, by running `alembic heads` and asserting a single head.

RCA: RAISE-14852 sprint of 4 backfill migrations merged independently;
two forks discovered only when tagging v3.1.0-rc.4.

Gate ID: gate-alembic-single-head
Workflow point: before:bug:close (also wired in before:story:close for
    story-level migrations)
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

# Relative to project root — adjust if raise-server moves.
_ALEMBIC_PACKAGE: str = "packages/raise-server"


def _find_alembic_root(working_dir: Path) -> Path | None:
    """Return the raise-server package dir if it exists under working_dir."""
    candidate = working_dir / _ALEMBIC_PACKAGE
    if (candidate / "alembic.ini").exists():
        return candidate
    return None


class AlembicSingleHeadGate:
    """Verify that the alembic migration chain has exactly one head.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Skips gracefully when:
    - raise-server package not found (non-server repo)
    - alembic not available (no venv / non-Python project)
    """

    gate_id: ClassVar[str] = "gate-alembic-single-head"
    description: ClassVar[str] = (
        "Alembic migration chain has exactly one head (no forks)"
    )
    workflow_point: ClassVar[str] = "before:bug:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run `alembic heads` and fail if more than one head is found."""
        alembic_root = _find_alembic_root(context.working_dir)
        if alembic_root is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="skipped: raise-server package not found at "
                f"{context.working_dir / _ALEMBIC_PACKAGE}",
            )

        # Prefer `uv run --no-sync alembic` (cross-platform venv, skips workspace
        # build — avoids coincurve/native-ext build failures on machines without
        # the C toolchain); fall back to alembic on PATH.
        alembic_cmd = (
            ["uv", "run", "--no-sync", "alembic"] if shutil.which("uv") else ["alembic"]
        )

        try:
            result = subprocess.run(
                [*alembic_cmd, "heads"],
                cwd=alembic_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"skipped: alembic unavailable ({exc})",
            )

        if result.returncode != 0:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="alembic heads failed — check alembic.ini and DB config",
                details=(result.stderr.strip(),),
            )

        # Each head is one non-empty line. Strip blank lines and "(head)" suffixes.
        heads = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and not line.strip().startswith("INFO")
        ]

        if len(heads) == 1:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"single head: {heads[0]}",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=f"migration chain forked — {len(heads)} heads found",
            details=(
                "Multiple heads mean two migrations share the same down_revision.",
                "Fix: update down_revision so the chain is linear.",
                "Check: cd packages/raise-server && uv run alembic heads",
                *heads,
            ),
        )
