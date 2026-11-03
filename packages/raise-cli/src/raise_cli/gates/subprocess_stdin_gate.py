"""Gate: subprocess calls in MCP-reachable raise_cli code must pass ``stdin=``.

On Windows a child process that inherits the MCP server's stdio pipe
deadlocks the handler (RAISE-18871). ``input=`` is accepted too:
``run(input=...)`` creates its own stdin pipe, and passing ``stdin=`` together
with ``input=`` raises ``ValueError``.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal

from raise_cli.gates.models import GateContext, GateResult

_SPAWNERS: frozenset[str] = frozenset(
    {"run", "Popen", "check_output", "check_call", "call"}
)

_SOURCE_ROOT = Path("packages/raise-cli/src/raise_cli")

# Interactive or non-MCP-reachable code left out on purpose by RAISE-18871:
# adding stdin=DEVNULL there would change POSIX behavior (git editor,
# prompts, tmux attach). Prefix match on the path relative to raise_cli/.
_EXCLUDED: tuple[str, ...] = (
    "cockpit/",
    "cli/commands/",
    "dev/processes.py",
    "dev/runtime_image.py",
    "dev/status.py",
    "distillation/",
    "harness_review/",
    "eval/memory_recall.py",
)


@dataclass(frozen=True)
class StdinViolation:
    """A subprocess call that does not pass ``stdin=``."""

    path: str
    line: int
    kind: Literal["missing", "kwargs"]


def _subprocess_names(tree: ast.AST) -> tuple[set[str], set[str]]:
    """Return (names bound to the subprocess module, bare spawner names)."""
    modules: set[str] = set()
    funcs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    modules.add(alias.asname or "subprocess")
        elif isinstance(node, ast.ImportFrom) and node.module == "subprocess":
            for alias in node.names:
                if alias.name in _SPAWNERS:
                    funcs.add(alias.asname or alias.name)
    return modules, funcs


def _is_spawn(func: ast.expr, modules: set[str], funcs: set[str]) -> bool:
    if isinstance(func, ast.Attribute):
        return (
            func.attr in _SPAWNERS
            and isinstance(func.value, ast.Name)
            and func.value.id in modules
        )
    return isinstance(func, ast.Name) and func.id in funcs


def find_violations(source: str, path: str) -> list[StdinViolation]:
    """Find subprocess calls in ``source`` that do not pass ``stdin=``."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    modules, funcs = _subprocess_names(tree)
    found: list[StdinViolation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_spawn(node.func, modules, funcs):
            continue
        names = {kw.arg for kw in node.keywords}
        if "stdin" in names or "input" in names:
            continue
        kind: Literal["missing", "kwargs"] = "kwargs" if None in names else "missing"
        found.append(StdinViolation(path=path, line=node.lineno, kind=kind))
    return sorted(found, key=lambda v: v.line)


class SubprocessStdinGate:
    """Block story close when a subprocess call lacks an explicit ``stdin=``."""

    gate_id: ClassVar[str] = "subprocess-stdin"
    description: ClassVar[str] = (
        "subprocess calls in raise_cli pass stdin= explicitly (RAISE-18871)"
    )
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Scan raise_cli sources and report unguarded subprocess calls."""
        root = context.working_dir / _SOURCE_ROOT
        if not root.is_dir():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="raise_cli sources not found — gate not applicable",
                skipped=True,
            )

        missing: list[str] = []
        warnings: list[str] = []
        for path in sorted(root.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            if rel.startswith(_EXCLUDED):
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for violation in find_violations(source, rel):
                where = f"raise_cli/{violation.path}:{violation.line}"
                if violation.kind == "missing":
                    missing.append(f"{where} subprocess call without stdin=")
                else:
                    warnings.append(
                        f"warning: {where} subprocess call uses **kwargs — "
                        "stdin= cannot be verified statically"
                    )

        if missing:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"{len(missing)} subprocess call(s) without explicit stdin= — "
                    "deadlocks the MCP server on Windows (RAISE-18871)"
                ),
                details=(
                    *missing,
                    *warnings,
                    "Fix: add stdin=subprocess.DEVNULL to the call",
                ),
            )

        suffix = f" ({len(warnings)} warning(s))" if warnings else ""
        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="all subprocess calls pass stdin= explicitly" + suffix,
            details=tuple(warnings),
        )
