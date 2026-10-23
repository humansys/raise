"""Bob IBM integration doctor check — validates .bob/ config beyond binary presence.

Binary presence on PATH is ``RuntimesCheck``'s job (manifest-driven, generic
across agent types). This check validates the structural config Bob needs to
work with rai: ``custom_modes.yaml`` (the ``rai-developer`` mode),
``mcp.json`` (the ``rai-workspace`` MCP server), and ``.bobrules`` at the
project root. All findings are advisory (WARN, never ERROR) — a broken Bob
config degrades one optional agent integration, it does not break rai.

D3 (design.md): does not import ``raise_cli.agents.bob_plugin`` — RAISE-16351
is unmerged on this branch. ``_RAI_MODE_SLUG`` mirrors
``BOB_CUSTOM_MODES_RAI_MODE["slug"]`` from that module; consolidate once both
stories land on release/3.1.0.

Architecture: extends ADR-045 (DoctorCheck protocol).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.mcp.workspace_config import WORKSPACE_SERVER_NAME

# Mirrors BOB_CUSTOM_MODES_RAI_MODE["slug"] in raise_cli.agents.bob_plugin
# (RAISE-16351, unmerged on this branch). Consolidate once both stories land
# on release/3.1.0.
_RAI_MODE_SLUG = "rai-developer"

_FIX_HINT_INIT_BOB = "run: rai init --agent bob"
_FIX_HINT_MCP_JSON = f'add "{WORKSPACE_SERVER_NAME}" under mcpServers in .bob/mcp.json'


class BobIntegrationCheck(DoctorCheck):
    """Validates Bob IBM integration config: custom_modes.yaml, mcp.json, .bobrules.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "bob"
    category: ClassVar[str] = "bob"
    description: ClassVar[str] = "Bob IBM integration config (.bob/, .bobrules)"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run Bob config checks, gated on Bob being configured at all."""
        working_dir = context.working_dir
        bob_dir = working_dir / ".bob"
        manifest_declares_bob = "bob" in self._read_agent_types(working_dir)

        if not bob_dir.is_dir() and not manifest_declares_bob:
            return [
                CheckResult(
                    check_id="bob-config",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="Bob not configured — checks skipped",
                )
            ]

        if not bob_dir.is_dir():
            return [
                CheckResult(
                    check_id="bob-config",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=(
                        "manifest declares bob agent but .bob/ directory is missing"
                    ),
                    fix_hint=_FIX_HINT_INIT_BOB,
                )
            ]

        return [
            self._check_custom_modes(bob_dir),
            self._check_mcp_json(bob_dir),
            self._check_bobrules(working_dir),
        ]

    @staticmethod
    def _read_agent_types(root: Path) -> list[str]:
        """Read agents.types from .raise/manifest.yaml.

        Duplicated from ``RuntimesCheck._read_agent_types`` — private, not
        shared across checks.
        """
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

    def _check_custom_modes(self, bob_dir: Path) -> CheckResult:
        path = bob_dir / "custom_modes.yaml"
        if not path.is_file():
            return CheckResult(
                check_id="bob-custom-modes",
                category=self.category,
                status=CheckStatus.WARN,
                message=".bob/custom_modes.yaml missing",
                fix_hint=_FIX_HINT_INIT_BOB,
            )
        try:
            raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            return CheckResult(
                check_id="bob-custom-modes",
                category=self.category,
                status=CheckStatus.WARN,
                message=f".bob/custom_modes.yaml invalid YAML: {exc}",
                fix_hint=_FIX_HINT_INIT_BOB,
            )
        except OSError as exc:
            return CheckResult(
                check_id="bob-custom-modes",
                category=self.category,
                status=CheckStatus.WARN,
                message=f".bob/custom_modes.yaml unreadable: {exc}",
                fix_hint=_FIX_HINT_INIT_BOB,
            )

        modes: object = raw.get("customModes", []) if isinstance(raw, dict) else []
        slugs: set[object] = (
            {m.get("slug") for m in modes if isinstance(m, dict)}
            if isinstance(modes, list)
            else set()
        )
        if _RAI_MODE_SLUG in slugs:
            return CheckResult(
                check_id="bob-custom-modes",
                category=self.category,
                status=CheckStatus.PASS,
                message=f'.bob/custom_modes.yaml has mode "{_RAI_MODE_SLUG}"',
            )
        return CheckResult(
            check_id="bob-custom-modes",
            category=self.category,
            status=CheckStatus.WARN,
            message=(
                ".bob/custom_modes.yaml customModes has no mode with slug "
                f'"{_RAI_MODE_SLUG}"'
            ),
            fix_hint=_FIX_HINT_INIT_BOB,
        )

    def _check_mcp_json(self, bob_dir: Path) -> CheckResult:
        path = bob_dir / "mcp.json"
        if not path.is_file():
            return CheckResult(
                check_id="bob-mcp-json",
                category=self.category,
                status=CheckStatus.WARN,
                message=".bob/mcp.json missing",
                fix_hint=_FIX_HINT_MCP_JSON,
            )
        try:
            raw: object = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return CheckResult(
                check_id="bob-mcp-json",
                category=self.category,
                status=CheckStatus.WARN,
                message=f".bob/mcp.json invalid JSON: {exc}",
                fix_hint=_FIX_HINT_MCP_JSON,
            )
        except OSError as exc:
            return CheckResult(
                check_id="bob-mcp-json",
                category=self.category,
                status=CheckStatus.WARN,
                message=f".bob/mcp.json unreadable: {exc}",
                fix_hint=_FIX_HINT_MCP_JSON,
            )

        servers: object = raw.get("mcpServers", {}) if isinstance(raw, dict) else {}
        if isinstance(servers, dict) and WORKSPACE_SERVER_NAME in servers:
            return CheckResult(
                check_id="bob-mcp-json",
                category=self.category,
                status=CheckStatus.PASS,
                message=f'.bob/mcp.json has "{WORKSPACE_SERVER_NAME}" server',
            )
        return CheckResult(
            check_id="bob-mcp-json",
            category=self.category,
            status=CheckStatus.WARN,
            message=(
                f'.bob/mcp.json mcpServers has no "{WORKSPACE_SERVER_NAME}" entry'
            ),
            fix_hint=_FIX_HINT_MCP_JSON,
        )

    def _check_bobrules(self, working_dir: Path) -> CheckResult:
        path = working_dir / ".bobrules"
        if not path.is_file():
            return CheckResult(
                check_id="bob-bobrules",
                category=self.category,
                status=CheckStatus.WARN,
                message=".bobrules missing",
                fix_hint=_FIX_HINT_INIT_BOB,
            )
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            return CheckResult(
                check_id="bob-bobrules",
                category=self.category,
                status=CheckStatus.WARN,
                message=f".bobrules unreadable: {exc}",
                fix_hint=_FIX_HINT_INIT_BOB,
            )
        if not content.strip():
            return CheckResult(
                check_id="bob-bobrules",
                category=self.category,
                status=CheckStatus.WARN,
                message=".bobrules is empty",
                fix_hint=_FIX_HINT_INIT_BOB,
            )
        return CheckResult(
            check_id="bob-bobrules",
            category=self.category,
            status=CheckStatus.PASS,
            message=".bobrules present and non-empty",
        )
