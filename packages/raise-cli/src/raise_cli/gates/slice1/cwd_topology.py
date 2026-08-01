"""FF-2: CWD topology gate (RAISE-15093).

Static check ensuring runner implementations do not assume a fixed working
directory. Greps for ``os.chdir`` and ``Path.cwd()`` usage in runner code,
and verifies ``SessionSpec`` does not expose a ``cwd`` field.
Fail-closed: any error returns ``passed=False``.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_SPI_SRC = Path("packages") / "raise-agent-spi" / "src" / "raise_agent_spi"

_EXCLUDE_DIRS = frozenset(
    {
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".git",
    }
)

# Patterns indicating fixed-CWD assumptions in runner code
_CWD_ANTIPATTERNS: tuple[tuple[str, str], ...] = (
    ("os.chdir", "os.chdir() mutates global CWD -- runners must use ephemeral dirs"),
    ("Path.cwd()", "Path.cwd() reads global CWD -- runners must use explicit paths"),
    ("os.getcwd()", "os.getcwd() reads global CWD -- runners must use explicit paths"),
)

_IGNORE_MARKER = "# cwd-topology: ignore"


class CWDTopologyGate:
    """Runner processes use ephemeral working directories."""

    gate_id: ClassVar[str] = "ff-2-cwd-topology"
    description: ClassVar[str] = "Runner processes use ephemeral working directories"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Static check for CWD assumptions in runner code and SessionSpec."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"CWD topology gate error: {exc}",
            )

    def _evaluate(self, context: GateContext) -> GateResult:
        spi_src = context.working_dir / _SPI_SRC
        if not spi_src.is_dir():
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="raise-agent-spi source directory not found",
                details=(f"Expected: {_SPI_SRC}",),
            )

        violations: list[str] = []

        # 1. Check SessionSpec does not have a cwd field
        try:
            spec_violations = self._check_session_spec(spi_src)
            violations.extend(spec_violations)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"SessionSpec check failed: {exc}",
            )

        # 2. Grep runner code for CWD anti-patterns
        try:
            grep_violations = self._grep_cwd_patterns(spi_src)
            violations.extend(grep_violations)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"CWD pattern scan failed: {exc}",
            )

        if violations:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{len(violations)} CWD topology violation(s)",
                details=tuple(violations),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="CWD topology invariant holds -- no fixed-CWD assumptions",
        )

    def _check_session_spec(self, spi_src: Path) -> list[str]:
        """Verify SessionSpec does not have a 'cwd' field."""
        violations: list[str] = []
        models_path = spi_src / "models.py"
        if not models_path.is_file():
            return violations

        try:
            tree = ast.parse(
                models_path.read_text(encoding="utf-8"), filename=str(models_path)
            )
        except (SyntaxError, OSError):
            violations.append("models.py: failed to parse -- cannot verify SessionSpec")
            return violations

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or node.name != "SessionSpec":
                continue
            for item in node.body:
                if (
                    isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                    and item.target.id == "cwd"
                ):
                    violations.append(
                        "SessionSpec has a 'cwd' field -- runners must "
                        "use ephemeral directories, not a configured CWD"
                    )
        return violations

    def _grep_cwd_patterns(self, spi_src: Path) -> list[str]:
        """Grep for CWD anti-patterns in Python files."""
        violations: list[str] = []
        for py_file in sorted(spi_src.rglob("*.py")):
            if any(
                part in _EXCLUDE_DIRS for part in py_file.relative_to(spi_src).parts
            ):
                continue

            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            if _IGNORE_MARKER in text:
                continue

            rel = py_file.relative_to(spi_src)
            for lineno, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for pattern, reason in _CWD_ANTIPATTERNS:
                    if pattern in line:
                        violations.append(f"{rel}:{lineno}: {reason}: {stripped[:80]}")
        return violations
