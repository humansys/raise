"""Quality gate runner for pre-publish checks."""

from __future__ import annotations

import importlib.util
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_COMMAND_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class Gate:
    """Definition of a quality gate."""

    name: str
    command: str
    cwd: Path | None = None


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

    repository_root = gates_path.parent.parent.resolve()
    package_root = project_root.resolve()
    return [
        Gate(
            name=g["name"],
            command=g["run"],
            cwd=repository_root if g.get("cwd") == "repository" else package_root,
        )
        for g in data["gates"]
    ]


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
            timeout=DEFAULT_COMMAND_TIMEOUT_SECONDS,
        )
        output = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0:
            return (True, output or "OK")
        return (False, output or f"Exit code {result.returncode}")
    except subprocess.TimeoutExpired:
        return (False, f"Timed out after {DEFAULT_COMMAND_TIMEOUT_SECONDS}s")
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


_DEFAULT_GENERATOR = Path(__file__).parents[5] / "scripts" / "generate-llms.py"


def _find_llms_root(start: Path) -> Path:
    """Find repository-scoped llms artifacts from a package release root."""
    current = start.resolve()
    for _ in range(10):
        if (current / ".llms-hash").exists() and (
            current / "dev" / "llms-content-spec.md"
        ).exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return start


def _load_generator_module(script: Path) -> Any:
    """Dynamically load generate-llms.py to access parse_frontmatter / compute_hash."""
    spec = importlib.util.spec_from_file_location("generate_llms", script)
    if spec is None or spec.loader is None:
        msg = f"Cannot load {script}"
        raise ImportError(msg)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_llms_freshness(
    project_root: Path,
    *,
    _generator_script: Path = _DEFAULT_GENERATOR,
) -> CheckResult:
    """Check that .llms-hash matches the current source content."""
    gate_name = "llms-full.txt freshness"
    llms_root = _find_llms_root(project_root)
    hash_file = llms_root / ".llms-hash"
    spec_path = llms_root / "dev" / "llms-content-spec.md"

    if not hash_file.exists():
        return CheckResult(gate=gate_name, passed=False, message=".llms-hash not found")

    try:
        mod = _load_generator_module(_generator_script)
    except (ImportError, FileNotFoundError) as exc:
        return CheckResult(gate=gate_name, passed=False, message=str(exc))

    try:
        fm = mod.parse_frontmatter(spec_path)
    except (ValueError, FileNotFoundError) as exc:
        return CheckResult(gate=gate_name, passed=False, message=str(exc))

    all_paths: list[Path] = []
    for section in fm.get("sections", []):
        try:
            all_paths.extend(mod.resolve_sources(section.get("sources", []), llms_root))
        except FileNotFoundError as exc:
            return CheckResult(gate=gate_name, passed=False, message=str(exc))

    current_hash = mod.compute_hash(all_paths, llms_root)
    stored_hash = hash_file.read_text(encoding="utf-8").strip()

    if current_hash == stored_hash:
        return CheckResult(
            gate=gate_name,
            passed=True,
            message="Hash verified — llms-full.txt is fresh",
        )

    return CheckResult(
        gate=gate_name,
        passed=False,
        message="Hash mismatch — llms-full.txt is stale, run generate-llms.py",
    )


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
            passed, message = _run_command(gate.command, gate.cwd or project_root)
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

    # llms-full.txt freshness
    results.append(_check_llms_freshness(project_root))

    return results
