"""ReleaseVersionGroupConsistentGate.

Verifies raise-cli and raise-core carry identical versions and that the
raise-core pin in raise-cli's dependencies matches that version.

Spike design: RAISE-16273 §4 / D3.
Story: RAISE-16283.

Gate ID: release-version-group-consistent
Workflow point: before:release:publish
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

_PIN_RE: re.Pattern[str] = re.compile(r"raise-core==([^\s,;\"']+)")

_CLI_PYPROJECT = "packages/raise-cli/pyproject.toml"
_CORE_PYPROJECT = "packages/raise-core/pyproject.toml"


def _read_project_version(pyproject_path: Path) -> str | None:
    """Read [project].version from a pyproject.toml.

    Returns ``None`` when the file does not exist or cannot be parsed.
    """
    if not pyproject_path.exists():
        return None
    try:
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)
        version: str | None = data.get("project", {}).get("version")
        return version
    except Exception:  # noqa: BLE001
        return None


def _read_core_pin(pyproject_path: Path) -> str | None:
    """Extract the version from a ``raise-core==<version>`` pin.

    Reads [project].dependencies from the given pyproject.toml.
    Returns ``None`` when the file cannot be read OR the pin is absent.
    """
    if not pyproject_path.exists():
        return None
    try:
        with pyproject_path.open("rb") as fh:
            data = tomllib.load(fh)
        deps: list[str] = data.get("project", {}).get("dependencies", [])
        for dep in deps:
            match = _PIN_RE.search(dep)
            if match:
                return match.group(1)
        return None
    except Exception:  # noqa: BLE001
        return None


class ReleaseVersionGroupConsistentGate:
    """Verify the fixed raise-cli/raise-core version group is consistent.

    Checks that both packages carry identical versions AND that the
    raise-core pin in raise-cli's dependencies matches the cli version.

    Registered via the ``rai.gates`` entry point.
    Skips gracefully when either pyproject.toml is absent (non-monorepo).
    """

    gate_id: ClassVar[str] = "release-version-group-consistent"
    description: ClassVar[str] = (
        "raise-cli and raise-core versions are identical and raise-core pin is current"
    )
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        """Collect all version-group violations and return a single result."""
        working_dir = context.working_dir
        cli_pyproject = working_dir / _CLI_PYPROJECT
        core_pyproject = working_dir / _CORE_PYPROJECT

        cli_version = _read_project_version(cli_pyproject)
        core_version = _read_project_version(core_pyproject)
        pin_version = _read_core_pin(cli_pyproject)

        # Skip when files are absent — non-monorepo or partial checkout.
        if cli_version is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"skipped: raise-cli pyproject.toml not found at {cli_pyproject}",
                skipped=True,
            )
        if core_version is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"skipped: raise-core pyproject.toml not found at {core_pyproject}",
                skipped=True,
            )

        # Pin absent is a hard failure (unlike missing files).
        if pin_version is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    "raise-core pin not found in raise-cli dependencies — "
                    "add 'raise-core==<version>' to [project.dependencies]"
                ),
            )

        failures: list[str] = []
        if cli_version != core_version:
            failures.append(
                f"version mismatch: raise-cli={cli_version!r}, raise-core={core_version!r}"
            )
        if pin_version != cli_version:
            failures.append(
                f"stale pin: raise-core=={pin_version!r} in raise-cli dependencies, "
                f"but raise-cli version is {cli_version!r}"
            )

        if failures:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="fixed version group inconsistent",
                details=tuple(failures),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"fixed group consistent: raise-cli==raise-core=={cli_version}, pin verified"
            ),
        )
