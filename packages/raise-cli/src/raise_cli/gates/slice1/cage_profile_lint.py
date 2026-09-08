"""FF-S4-lint: Cage profile lint gate (RAISE-15093).

Validates that no cage profile uses ``allow-all`` egress or wildcard
destinations. Fail-closed: parse errors result in ``passed=False``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_PROFILES_DIR = Path("packages") / "raise-agent-spi" / "cage_profiles"


class CageProfileLintGate:
    """No cage profile uses allow-all egress or wildcard destinations."""

    gate_id: ClassVar[str] = "ff-s4-cage-profile-lint"
    description: ClassVar[str] = (
        "No cage profile uses allow-all egress or wildcard destinations"
    )
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Lint all cage profile YAML files for security invariants."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Cage profile lint gate error: {exc}",
            )

    def _evaluate(self, context: GateContext) -> GateResult:
        profiles_path = context.working_dir / _PROFILES_DIR
        if not profiles_path.is_dir():
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="Cage profiles directory not found",
                details=(f"Expected: {_PROFILES_DIR}",),
            )

        yaml_files = sorted(profiles_path.glob("*.yaml"))
        if not yaml_files:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No cage profiles found -- nothing to lint",
            )

        violations: list[str] = []
        for profile_path in yaml_files:
            file_violations = self._lint_profile(profile_path)
            violations.extend(file_violations)

        if violations:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{len(violations)} cage profile violation(s)",
                details=tuple(violations),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"{len(yaml_files)} cage profile(s) passed lint",
        )

    def _lint_profile(self, path: Path) -> list[str]:
        """Return violations for a single cage profile file."""
        violations: list[str] = []
        name = path.name

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            violations.append(f"{name}: failed to parse YAML: {exc}")
            return violations

        if not isinstance(data, dict):
            violations.append(f"{name}: root is not a mapping")
            return violations

        network = data.get("network", {})
        if not isinstance(network, dict):
            violations.append(f"{name}: 'network' is not a mapping")
            return violations

        # Check egress policy (case-insensitive to prevent bypass)
        egress = network.get("egress", "")
        if isinstance(egress, str) and egress.lower() == "allow-all":
            violations.append(f"{name}: egress is '{egress}' -- must be 'deny-all'")

        # Check destinations for wildcards
        destinations = network.get("allowed_destinations", [])
        if isinstance(destinations, list):
            for i, dest in enumerate(destinations):
                if isinstance(dest, dict):
                    host = dest.get("host", "")
                    if isinstance(host, str) and "*" in host:
                        violations.append(
                            f"{name}: allowed_destinations[{i}].host "
                            f"contains wildcard '*': {host}"
                        )
        return violations
