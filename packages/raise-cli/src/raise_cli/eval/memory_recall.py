"""MemoryRecallGate — AC-3 bilingual memory recall regression gate.

Wraps the S14055.2 harness (``tests/eval/test_memory_recall_gate.py``) as a
release-blocking ``WorkflowGate``. Shells out to the harness via subprocess
pytest — the harness stays filesystem-pure under ``tests/`` by design (DD-2,
s14055.3-design.md); this gate does not reimplement or import its logic.

Fail-loud, NOT the skip-on-missing-scorer of ``EvalGate`` (DD-3): a missing
``sentence-transformers`` dependency does NOT downgrade to ``passed=True``.
The harness's own AC4 assert (``backend._scorer is not None``) already
produces a non-zero exit in that case, which this gate maps straight to
``passed=False`` with the raw pytest output attached. The only legitimate
skip is the harness file itself being absent (partial checkout) — distinct
from, and never conflated with, a scorer failure.

Registered via ``rai.gates`` entry point in pyproject.toml.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

_HARNESS_RELATIVE_PATH = Path(
    "packages/raise-cli/tests/eval/test_memory_recall_gate.py"
)
_TEST_NODE_ID = "test_memory_recall_gate_bilingual_end_to_end"
_RECALL_RESULT_RE = re.compile(r"RECALL_RESULT en=(\d+) es=(\d+) neg=(\d+)")


class MemoryRecallGate:
    """Release gate: AC-3 memory recall >=80% per language (EN & ES)."""

    gate_id: ClassVar[str] = "gate-memory-recall"
    description: ClassVar[str] = "Memory recall AC-3 >=80% per language (EN & ES)"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Run the S2 harness by subprocess and map exit-code -> passed."""
        harness_path = context.working_dir / _HARNESS_RELATIVE_PATH
        if not harness_path.exists():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"skipped: harness not found at {harness_path} "
                    "(partial checkout) — the only legitimate skip for this gate"
                ),
            )

        try:
            proc = subprocess.run(  # noqa: S603
                [
                    "uv",
                    "run",
                    "pytest",
                    f"{harness_path}::{_TEST_NODE_ID}",
                    "-m",
                    "ml",
                    "-p",
                    "no:cacheprovider",
                    "-s",  # disable pytest's per-test capture so RECALL_RESULT
                    # (a plain print(), otherwise swallowed on a PASS and only
                    # ever shown on a FAIL) reaches this subprocess's stdout.
                    "-n",
                    "0",  # root pyproject.toml addopts default to -n auto
                    # (xdist); a worker's stdout is relayed via xdist's own IPC
                    # reporting, not forwarded live, so -s alone is not enough —
                    # xdist itself must be disabled for RECALL_RESULT to survive.
                ],
                cwd=context.working_dir,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            # `uv` (or the runner) absent from PATH — map to fail-closed rather
            # than crashing the whole release flow with an uncaught error
            # (arch-review Q1). Loud, but a uniform GateResult, not a traceback.
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"AC-3 recall gate could not launch pytest: {exc} (is `uv` on PATH?)",
            )
        output = proc.stdout + proc.stderr

        if proc.returncode != 0:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"AC-3 recall FAILED (exit {proc.returncode}): {output.strip()}",
                details=(output,),
            )

        # Fail-closed on a green-but-vacuous run (arch-review R1): exit 0 with
        # no RECALL_RESULT line means the harness was SKIPPED (a runtime
        # pytest.skip/importorskip yields exit 0) or otherwise never reached
        # D3.5's measurement. A passing exit code alone is NOT proof the recall
        # was measured — require the summary so the parse is load-bearing, not
        # cosmetic, and a future `importorskip` cannot silently pass the gate.
        if _RECALL_RESULT_RE.search(output) is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    "AC-3 recall NOT MEASURED: pytest exited 0 but emitted no "
                    "RECALL_RESULT line — the harness was skipped or did not run "
                    "the measurement. A vacuous pass is not a pass."
                ),
                details=(output,),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"AC-3 recall PASS ({self._summarize(output)})",
            details=(output,),
        )

    @staticmethod
    def _summarize(output: str) -> str:
        """Parse the ``RECALL_RESULT en=.. es=.. neg=..`` summary line.

        Falls back to an explicit "unavailable" note (never a silent blank)
        when the line is absent — e.g. the harness failed before D3.5's loop
        printed it, in which case the raw pytest output (attached in
        ``details``) already carries the actionable assertion text.
        """
        match = _RECALL_RESULT_RE.search(output)
        if match is None:
            return "recall counts unavailable — RECALL_RESULT line not found"
        en, es, neg = match.groups()
        return f"EN {en}/5, ES {es}/5, neg {neg}"
