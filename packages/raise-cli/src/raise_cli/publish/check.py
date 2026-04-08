"""Quality gate runner for pre-publish checks."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Gate:
    """Definition of a quality gate."""

    name: str
    command: str


@dataclass(frozen=True)
class CheckResult:
    """Result of a single quality gate check."""

    gate: str
    passed: bool
    message: str


def _find_gates_yaml(start: Path) -> Path | None:
    """Walk up from start to find .raise/release-gates.yaml."""
    current = start.resolve()
    for _ in range(10):  # safety limit
        candidate = current / ".raise" / "release-gates.yaml"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _load_gates(project_root: Path) -> list[Gate]:
    """Load command gates from .raise/release-gates.yaml.

    Falls back to empty list if file not found.
    """
    import yaml

    gates_path = _find_gates_yaml(project_root)
    if gates_path is None:
        return []

    data = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    if not data or "gates" not in data:
        return []

    return [Gate(name=g["name"], command=g["run"]) for g in data["gates"]]


def _run_command(command: str, cwd: Path) -> tuple[bool, str]:
    """Run a shell command and return (success, output).

    Args:
        command: Shell command string.
        cwd: Working directory.

    Returns:
        Tuple of (passed, message).
    """
    try:
        import shlex

        # shell=True only for glob patterns (dist/*) — commands are internal constants
        use_shell = "*" in command or "?" in command
        result = subprocess.run(  # noqa: S602
            command if use_shell else shlex.split(command),
            cwd=cwd,
            shell=use_shell,  # nosec B602
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0:
            return (True, output or "OK")
        return (False, output or f"Exit code {result.returncode}")
    except subprocess.TimeoutExpired:
        return (False, "Timed out after 300s")
    except FileNotFoundError:
        return (False, f"Command not found: {command}")


def _extract_version(path: Path, pattern: str) -> str | None:
    """Extract a version string from a file using a regex pattern.

    Args:
        path: File to read.
        pattern: Regex with a capture group for the version.

    Returns:
        Extracted version string or None.
    """
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None


def run_checks(
    *,
    project_root: Path,
    pyproject_path: Path,
    changelog_path: Path,
) -> list[CheckResult]:
    """Run all quality gates and return results.

    Args:
        project_root: Project root directory.
        pyproject_path: Path to pyproject.toml.
        changelog_path: Path to CHANGELOG.md.

    Returns:
        List of CheckResult for each gate.
    """
    from raise_cli.publish.changelog import has_unreleased_entries
    from raise_cli.publish.version import is_pep440

    results: list[CheckResult] = []

    # Command-based gates from .raise/release-gates.yaml
    gates = _load_gates(project_root)
    if not gates:
        results.append(
            CheckResult(
                gate="Gate config",
                passed=False,
                message="No .raise/release-gates.yaml found",
            )
        )
    else:
        for gate in gates:
            passed, message = _run_command(gate.command, project_root)
            results.append(CheckResult(gate=gate.name, passed=passed, message=message))

    # Changelog has unreleased entries
    if changelog_path.exists():
        content = changelog_path.read_text(encoding="utf-8")
        has_entries = has_unreleased_entries(content)
        results.append(
            CheckResult(
                gate="CHANGELOG has unreleased entries",
                passed=has_entries,
                message="Unreleased entries found"
                if has_entries
                else "No unreleased entries",
            )
        )
    else:
        results.append(
            CheckResult(
                gate="CHANGELOG has unreleased entries",
                passed=False,
                message=f"File not found: {changelog_path}",
            )
        )

    # Version is PEP 440 compliant
    pyproject_version = _extract_version(pyproject_path, r'version\s*=\s*"([^"]*)"')
    if pyproject_version and is_pep440(pyproject_version):
        results.append(
            CheckResult(
                gate="Version PEP 440 compliant",
                passed=True,
                message=f"{pyproject_version} is valid PEP 440",
            )
        )
    else:
        results.append(
            CheckResult(
                gate="Version PEP 440 compliant",
                passed=False,
                message=f"'{pyproject_version}' is not valid PEP 440"
                if pyproject_version
                else "Could not read version from pyproject.toml",
            )
        )

    return results
