"""xdist safety scanner for RaiSE test suite (RAISE-14875).

Scans Python test source files using the ``ast`` module to identify test
functions and methods that exhibit patterns unsafe under pytest-xdist parallel
execution and are missing the required declarative safety marker.

## Unsafe patterns detected

``META_PATH_MUTATION``
    The test calls ``sys.meta_path.insert()``, ``sys.meta_path.remove()``,
    ``sys.meta_path.append()``, or performs an item assignment on
    ``sys.meta_path``.  ``sys.meta_path`` is a per-*process* global.  Within a
    single xdist worker the mutation can affect other tests executing in the
    same process.  Requires ``@pytest.mark.serial``.

``DIRECT_CHDIR``
    The test calls ``os.chdir()`` directly (not through ``monkeypatch.chdir``).
    The global conftest ``_restore_cwd`` fixture mitigates this within a single
    process, but the fixture-based guard is not guaranteed across ordering
    under xdist.  Requires ``@pytest.mark.serial``.

## Marker convention

``@pytest.mark.serial``
    Test mutates process-global state.  Must not run concurrently with other
    tests in the **same worker process**.  Under xdist ``--dist=no`` all tests
    run in one process, so the default ``-n auto`` is safe *as long as the
    mutation is bracketed*.  This marker documents the constraint and enables
    future enforcement via ``--dist=loadscope`` grouping.

``@pytest.mark.no_xdist``
    Test is fundamentally incompatible with any form of xdist parallelism (e.g.
    loads a large ML model via import side-effects, requires exclusive ownership
    of a system resource, or has ordering dependencies across test files).
    These tests must run with ``-n 0``.

Usage::

    from raise_cli.testing.xdist_safety import scan_file, scan_source

    # Per-file scan
    violations = scan_file(Path("packages/raise-cli/tests/unit/testing/test_foo.py"))
    for v in violations:
        print(v)

    # Or scan in-memory source
    violations = scan_source(source_text, path=Path("test_foo.py"))

See ``dev/analysis/xdist-safety-audit.md`` for the full audit catalog.
"""

from __future__ import annotations

import ast
import enum
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "UnsafePattern",
    "Violation",
    "scan_directory",
    "scan_file",
    "scan_source",
]

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class UnsafePattern(enum.Enum):
    """Enumeration of detected unsafe patterns."""

    META_PATH_MUTATION = "meta_path_mutation"
    """sys.meta_path mutation (insert, remove, append, item-assignment)."""

    DIRECT_CHDIR = "direct_chdir"
    """Direct os.chdir() call (not via monkeypatch)."""


@dataclass(frozen=True)
class Violation:
    """A single xdist safety violation detected in a test function."""

    file: Path
    """Source file containing the violation."""

    line: int
    """1-based line number of the test function/method definition."""

    test_name: str
    """Name of the test function or method (e.g. ``test_foo``)."""

    pattern: UnsafePattern
    """Which unsafe pattern was detected."""

    marker_needed: str
    """Marker that would resolve this violation (``serial`` or ``no_xdist``)."""

    def __str__(self) -> str:
        """Return a human-readable description of this violation."""
        return (
            f"{self.file}:{self.line}: {self.test_name} — "
            f"{self.pattern.value} detected; add @pytest.mark.{self.marker_needed}"
        )


# ---------------------------------------------------------------------------
# Marker names that suppress violations
# ---------------------------------------------------------------------------

#: Markers that indicate a test has already declared its xdist safety posture.
_SAFETY_MARKERS: frozenset[str] = frozenset({"serial", "no_xdist"})

# ---------------------------------------------------------------------------
# AST helper utilities
# ---------------------------------------------------------------------------


def _get_marker_names(decorator_list: list[ast.expr]) -> set[str]:
    """Extract pytest marker names from a decorator list.

    Recognises both::

        @pytest.mark.serial          # Attribute access
        @pytest.mark.serial()        # Call form

    Returns a set of marker name strings (e.g. ``{"serial", "ml"}``).
    """
    names: set[str] = set()
    for dec in decorator_list:
        node = dec
        # Unwrap Call: @pytest.mark.serial()
        if isinstance(node, ast.Call):
            node = node.func
        # Expect Attribute chain: pytest.mark.<name>
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "pytest"
            and node.value.attr == "mark"
        ):
            names.add(node.attr)
    return names


def _is_test_function(name: str) -> bool:
    """Return True if the name matches pytest's default test function pattern."""
    return name.startswith("test_") or name == "test"


# ---------------------------------------------------------------------------
# Pattern checkers
# ---------------------------------------------------------------------------


def _has_meta_path_mutation(body: list[ast.stmt]) -> bool:
    """Return True if any statement in *body* calls or assigns sys.meta_path.

    Detected patterns::

        sys.meta_path.insert(...)
        sys.meta_path.remove(...)
        sys.meta_path.append(...)
        sys.meta_path[...] = ...

    The body is walked with ``ast.walk`` — nested function/class *definition*
    nodes are skipped, but calls *inside* nested helpers are still visited
    because ``ast.walk`` queues children before the caller's loop can prune them.
    A ``sys.meta_path`` call inside an inline helper defined inside the test
    body WILL produce a violation on the outer test.
    """
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        # sys.meta_path.method(...)  →  Call with Attribute whose value
        # is an Attribute "sys.meta_path".
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Attribute)
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "sys"
                and func.value.attr == "meta_path"
                and func.attr in {"insert", "remove", "append"}
            ):
                return True

        # sys.meta_path[...] = ...
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "sys"
                    and target.value.attr == "meta_path"
                ):
                    return True

    return False


def _has_direct_chdir(body: list[ast.stmt]) -> bool:
    """Return True if any statement calls ``os.chdir()`` directly.

    ``monkeypatch.chdir(...)`` is NOT flagged because monkeypatch
    automatically restores the original directory after the test.
    """
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        if isinstance(node, ast.Call):
            func = node.func
            # os.chdir(...)
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "os"
                and func.attr == "chdir"
            ):
                return True
            # chdir(...) when imported as `from os import chdir`
            if isinstance(func, ast.Name) and func.id == "chdir":
                return True

    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_PATTERN_CHECKERS: list[
    tuple[
        UnsafePattern,
        str,
        Callable[[list[ast.stmt]], bool],
    ]
] = [
    (UnsafePattern.META_PATH_MUTATION, "serial", _has_meta_path_mutation),
    (UnsafePattern.DIRECT_CHDIR, "serial", _has_direct_chdir),
]


def _check_func_node(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
    path: Path,
    extra_markers: set[str] | None = None,
) -> list[Violation]:
    """Check a single test function/method node for safety violations.

    Args:
        func: The AST function node to inspect.
        path: Source file path (used in ``Violation.file``).
        extra_markers: Markers already declared on a containing class, if any.

    Returns:
        Violations found on this function, in pattern order.
    """
    inherited = extra_markers or set()
    func_markers = _get_marker_names(func.decorator_list)
    all_markers = func_markers | inherited
    if all_markers & _SAFETY_MARKERS:
        return []

    found: list[Violation] = []
    for pattern, marker, checker in _PATTERN_CHECKERS:
        if checker(func.body):
            found.append(
                Violation(
                    file=path,
                    line=func.lineno,
                    test_name=func.name,
                    pattern=pattern,
                    marker_needed=marker,
                )
            )
    return found


def _scan_tree(tree: ast.Module, path: Path) -> list[Violation]:
    """Walk a parsed AST and collect xdist safety violations.

    Args:
        tree: Parsed AST module node.
        path: Source file path (forwarded to each ``Violation``).

    Returns:
        All violations found, in source order.
    """
    violations: list[Violation] = []

    # -- Class methods --
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_markers = _get_marker_names(node.decorator_list)
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not _is_test_function(item.name):
                continue
            violations.extend(_check_func_node(item, path, extra_markers=class_markers))

    # -- Top-level test functions --
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _is_test_function(node.name):
            continue
        violations.extend(_check_func_node(node, path))

    return violations


def scan_source(source: str, path: Path) -> list[Violation]:
    """Scan *source* (Python text) for xdist safety violations.

    Parameters
    ----------
    source:
        Python source code to scan (typically the contents of a test file).
    path:
        The filesystem path to report in violations.  Used only for the
        ``Violation.file`` field — the file is **not** read by this function.

    Returns:
    -------
    list[Violation]
        Violations found, in source order.
    """
    if not source.strip():
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    return _scan_tree(tree, path)


def scan_file(path: Path) -> list[Violation]:
    """Read *path* and return xdist safety violations.

    Parameters
    ----------
    path:
        Filesystem path to a Python test file.

    Returns:
    -------
    list[Violation]
        Violations found, in source order.

    Raises:
    ------
    FileNotFoundError
        If *path* does not exist.
    """
    source = path.read_text(encoding="utf-8")
    return scan_source(source, path)


def scan_directory(path: Path) -> list[Violation]:
    """Walk *path* recursively and scan every ``*.py`` file for violations.

    Parameters
    ----------
    path:
        Root directory to scan.  All ``*.py`` files found under this directory
        (including subdirectories) are scanned.

    Returns:
    -------
    list[Violation]
        All violations found across every Python file under *path*, in
        filesystem traversal order.
    """
    violations: list[Violation] = []
    for py_file in sorted(path.rglob("*.py")):
        violations.extend(scan_file(py_file))
    return violations


# ---------------------------------------------------------------------------
# CLI entrypoint — __main__ block
# ---------------------------------------------------------------------------


def _parse_targets(argv: list[str] | None) -> list[Path]:
    """Parse CLI arguments and return the list of target paths to scan."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m raise_cli.testing.xdist_safety",
        description="Scan Python test files for xdist safety violations.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="Python test files or directories to scan.",
    )
    parser.add_argument(
        "--paths",
        dest="paths_file",
        metavar="FILE",
        help=(
            "Path to a text file containing one filesystem path per line "
            "(for delta mode: pipe git diff --name-only output here)."
        ),
    )
    args = parser.parse_args(argv)

    targets: list[Path] = []

    if args.paths_file:
        lines = Path(args.paths_file).read_text(encoding="utf-8").splitlines()
        targets.extend(Path(line.strip()) for line in lines if line.strip())

    targets.extend(Path(raw) for raw in args.paths)
    return targets


def _scan_targets(targets: list[Path]) -> list[Violation]:
    """Scan a list of file/directory paths and return all violations."""
    import sys as _sys

    all_violations: list[Violation] = []
    for target in targets:
        if not target.exists():
            _sys.stderr.write(f"warning: {target} does not exist, skipping\n")
            continue
        if target.is_dir():
            all_violations.extend(scan_directory(target))
        elif target.suffix == ".py":
            all_violations.extend(scan_file(target))
    return all_violations


def _main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the xdist safety scanner.

    Accepts either positional path arguments or ``--paths FILE`` (a text file
    with one filesystem path per line).  Exits non-zero if any violation is
    found; exits 0 if the input is clean.

    This is the interface used by the ``test:xdist-safety-delta`` CI job, which
    pipes ``git diff --name-only`` output through this entrypoint to enforce
    the xdist safety invariant on every new or modified Python file in an MR.
    """
    targets = _parse_targets(argv)
    if not targets:
        return 0

    all_violations = _scan_targets(targets)
    for v in all_violations:
        print(str(v))

    return 1 if all_violations else 0


if __name__ == "__main__":  # pragma: no cover
    import sys as _sys

    _sys.exit(_main())
