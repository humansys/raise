"""Built-in TypeGateTestsAdvisory — advisory-only pyright coverage for tests/.

RAISE-11850 (S2) root-caused ``tests/`` type-check exclusion to three
independent layers (manifest ``type_check_command``, ``pyproject.toml``
``[tool.pyright].include``, and ``gates/execution.py::types_scope_for()``),
all deliberately src-only (S8370.3) to avoid false blocks from pre-existing
test-code debt. Turning tests/ coverage on for real surfaced 311 genuine
pyright errors (basic mode) — decomposed into a burn-down
(RAISE-14344..14350, ``work/epics/e14112-gates-pipeline/tests-typedebt-burndown.md``).

This gate makes that debt VISIBLE without making CI red: it runs pyright
directly against the basic-mode config in
``pyrightconfig.tests-advisory.json`` (repo root, deliberately outside the
strict ``[tool.pyright].include`` used by the blocking ``gate-types``
command) and always returns ``passed=True`` — the same convention the drift
gates use (``gates/drift/_base.py::advisory()``). RAISE-12207 flips this gate
to a real pass/fail once the burn-down count reaches zero.
"""

from __future__ import annotations

import json
import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

_CONFIG_REL_PATH = "pyrightconfig.tests-advisory.json"
_BURNDOWN_REF = "burn-down RAISE-14344..14350"
_FLIP_REF = "RAISE-12207"


class TypeGateTestsAdvisory:
    """Advisory (non-blocking) pyright coverage for ``tests/``.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-types-tests-advisory"
    description: ClassVar[str] = (
        "Advisory: tests/ type-check coverage (non-blocking, RAISE-11850)"
    )
    workflow_point: ClassVar[str] = "before:release:publish"
    is_blocker: ClassVar[bool] = False

    def evaluate(self, context: GateContext) -> GateResult:
        """Run the basic-mode pyright scan over tests/ and report, never fail."""
        config_path = context.working_dir / _CONFIG_REL_PATH
        if not config_path.exists():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Skipped — {_CONFIG_REL_PATH} not found",
            )

        try:
            result = subprocess.run(
                ["uv", "run", "pyright", "--project", str(config_path), "--outputjson"],
                capture_output=True,
                text=True,
                cwd=str(context.working_dir),
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"Advisory scan errored (non-blocking): {type(exc).__name__}: {exc}",
            )

        error_count = _parse_error_count(result.stdout)
        if error_count is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="Advisory scan produced no parseable pyright output (non-blocking)",
                details=tuple(s for s in (result.stdout, result.stderr) if s),
            )

        if error_count == 0:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"tests/ type-check: 0 errors — ready for {_FLIP_REF} blocking flip",
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"⚠ ADVISORY: {error_count} pyright error(s) in tests/ "
                f"(non-blocking, {_BURNDOWN_REF})"
            ),
            details=(f"{error_count} errors — see {_BURNDOWN_REF}",),
        )


def _parse_error_count(stdout: str) -> int | None:
    """Extract ``summary.errorCount`` from pyright's ``--outputjson`` payload."""
    try:
        data = json.loads(stdout)
        return int(data["summary"]["errorCount"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
