"""Agent runtime doctor check — reports agent runtimes from manifest.

Reads agents.types from .raise/manifest.yaml to determine which runtimes
to check. Falls back to checking common agent binaries on PATH.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_AGENT_BINARIES: dict[str, str] = {
    "claude": "claude",
    "hermes": "hermes",
    "cursor": "cursor",
    "codex": "codex",
    "copilot": "github-copilot-cli",
    "kimi": "kimi",
    "devin": "devin",
}


class RuntimesCheck(DoctorCheck):
    """Reports which agent runtimes are available based on manifest config."""

    check_id: ClassVar[str] = "runtimes"
    category: ClassVar[str] = "runtimes"
    description: ClassVar[str] = "Agent runtime availability from manifest"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check agent binaries declared in manifest."""
        agent_types = self._read_agent_types(context.working_dir)
        if not agent_types:
            return [
                CheckResult(
                    check_id="runtime-agents",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no agents configured in manifest",
                )
            ]
        results: list[CheckResult] = []
        for agent_type in agent_types:
            results.append(self._check_agent_binary(agent_type))
        return results

    @staticmethod
    def _read_agent_types(root: Path) -> list[str]:
        manifest_path = root / ".raise" / "manifest.yaml"
        if not manifest_path.is_file():
            return []
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            agents = (data or {}).get("agents", {}) or {}
            types = agents.get("types", [])
            return types if isinstance(types, list) else []
        except (yaml.YAMLError, OSError):
            return []

    def _check_agent_binary(self, agent_type: str) -> CheckResult:
        binary = _AGENT_BINARIES.get(agent_type, agent_type)
        path = shutil.which(binary)
        if path is not None:
            return CheckResult(
                check_id=f"runtime-{agent_type}",
                category=self.category,
                status=CheckStatus.PASS,
                message=f"{agent_type} binary at {path}",
            )
        return CheckResult(
            check_id=f"runtime-{agent_type}",
            category=self.category,
            status=CheckStatus.WARN,
            message=f"{agent_type} binary not found on PATH",
            fix_hint=f"Install {agent_type} or add it to PATH",
        )
