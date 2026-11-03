"""ImportFanInGate — CAND-17 drift detector.

Rule: module __init__.py imports ≥7 distinct top-level packages synchronously
(no TYPE_CHECKING guard, no deferred import).
Advisory: returns passed=True with violation details.
"""

from __future__ import annotations

import ast

from raise_cli.gates.drift._base import DriftGate, is_excluded, scoped_rglob
from raise_cli.gates.models import GateContext, GateResult

_THRESHOLD = 7


def _is_type_checking_block(node: ast.stmt) -> bool:
    """Return True if node is ``if TYPE_CHECKING:``."""
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _top_level_imports(source: str) -> set[str]:
    """Return distinct top-level package names imported at module level.

    Counts only module-level import statements. Excludes imports inside
    ``if TYPE_CHECKING:`` blocks and imports nested in functions or classes.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    packages: set[str] = set()
    for node in tree.body:
        if _is_type_checking_block(node):
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                packages.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            packages.add(node.module.split(".")[0])
    return packages


class ImportFanInGate(DriftGate):
    """Flags modules importing ≥7 top-level packages at init time.

    Evidence: κ=0.802, precision=0.20 (E2161 CAND-17).
    """

    gate_id = "drift-import-fan-in"
    description = "Cross-boundary import fan-in at module init (CAND-17)"

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan __init__.py files for import fan-in."""
        violations: list[str] = []
        for init_file in scoped_rglob(
            context.working_dir, "__init__.py", context.changed_files
        ):
            if is_excluded(init_file, context.working_dir) or self._has_ignore_marker(
                init_file
            ):
                continue
            source = init_file.read_text(encoding="utf-8", errors="replace")
            packages = _top_level_imports(source)
            if len(packages) >= _THRESHOLD:
                rel = init_file.relative_to(context.working_dir)
                violations.append(f"{rel}: {len(packages)} top-level imports")
        return self._advisory(self.gate_id, violations)
