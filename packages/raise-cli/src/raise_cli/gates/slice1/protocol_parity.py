"""FF-3: Protocol parity gate (RAISE-15093).

Every ``@runtime_checkable Protocol`` in ``raise_agent_spi`` must have at
least one implementor. Uses file-based AST analysis to avoid circular deps
with the SPI package. Fail-closed: any error returns ``passed=False``.
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


def _find_protocols(src_dir: Path) -> dict[str, Path]:
    """Find all classes decorated with ``@runtime_checkable`` in the SPI source.

    Returns a dict of protocol_name -> file_path.
    """
    protocols: dict[str, Path] = {}
    for py_file in sorted(src_dir.rglob("*.py")):
        if any(part in _EXCLUDE_DIRS for part in py_file.relative_to(src_dir).parts):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            # Check if any base is Protocol and any decorator is runtime_checkable
            is_protocol = any(
                (isinstance(base, ast.Name) and base.id == "Protocol")
                or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                for base in node.bases
            )
            has_checkable = any(
                (isinstance(dec, ast.Name) and dec.id == "runtime_checkable")
                or (isinstance(dec, ast.Attribute) and dec.attr == "runtime_checkable")
                for dec in node.decorator_list
            )
            if is_protocol and has_checkable:
                protocols[node.name] = py_file
    return protocols


def _base_name(base: ast.expr) -> str | None:
    """Extract the simple name from a base class AST node."""
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def _find_implementors(
    src_dir: Path, protocol_names: set[str], extra_dirs: list[Path] | None = None
) -> dict[str, list[str]]:
    """Find classes that list a known protocol name as a base class.

    Searches src_dir and any extra_dirs (e.g. downstream packages) for nominal
    implementors.  Returns protocol_name -> [implementor_class_name, ...].
    """
    implementors: dict[str, list[str]] = {name: [] for name in protocol_names}

    for search_root in [src_dir, *(extra_dirs or [])]:
        for py_file in sorted(search_root.rglob("*.py")):
            if any(
                part in _EXCLUDE_DIRS for part in py_file.relative_to(search_root).parts
            ):
                continue
            try:
                tree = ast.parse(
                    py_file.read_text(encoding="utf-8"), filename=str(py_file)
                )
            except (SyntaxError, OSError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for base in node.bases:
                    bname = _base_name(base)
                    if (
                        bname is not None
                        and bname in protocol_names
                        and node.name != bname
                    ):
                        implementors[bname].append(node.name)
    return implementors


class ProtocolParityGate:
    """Every Protocol has at least one runtime_checkable implementor."""

    gate_id: ClassVar[str] = "ff-3-protocol-parity"
    description: ClassVar[str] = (
        "Every Protocol has at least one runtime_checkable implementor"
    )
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Find all Protocols in the SPI and verify each has an implementor."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Protocol parity gate error: {exc}",
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

        try:
            protocols = _find_protocols(spi_src)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Protocol discovery failed: {exc}",
            )

        if not protocols:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No @runtime_checkable Protocols found -- nothing to check",
            )

        # Search the full packages/ tree so downstream implementors are found.
        packages_dir = context.working_dir / "packages"
        extra = [packages_dir] if packages_dir.is_dir() else []
        try:
            implementors = _find_implementors(
                spi_src, set(protocols.keys()), extra_dirs=extra
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Implementor discovery failed: {exc}",
            )

        violations: list[str] = []
        for proto_name in sorted(protocols):
            impls = implementors.get(proto_name, [])
            if not impls:
                violations.append(
                    f"Protocol {proto_name} ({protocols[proto_name].name}) "
                    f"has zero implementors"
                )

        if violations:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{len(violations)} protocol(s) without implementors",
                details=tuple(violations),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"{len(protocols)} protocol(s) verified -- "
                f"all have at least one implementor"
            ),
        )
