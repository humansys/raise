"""Developer diagnostic check — profile, credentials, Claude Code, MCP servers.

Reports developer-level setup status for new machine readiness.
All checks are advisory (WARN, not ERROR) since the CLI works without them.

Architecture: E493/S493.4, extends ADR-045.
"""

from __future__ import annotations

import json
import os
import shutil
import tomllib
from pathlib import Path
from typing import ClassVar, cast

import yaml

from raise_cli.config.paths import get_global_rai_dir
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.mcp.workspace_config import CODEX_ENABLED_TOOLS, WORKSPACE_SERVER_NAME

_CODEX_REQUIRED_PIPELINE_TOOLS = frozenset(CODEX_ENABLED_TOOLS)


class DeveloperCheck(DoctorCheck):
    """Validates developer-level setup: profile, credentials, Claude Code, MCP.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "developer"
    category: ClassVar[str] = "developer"
    description: ClassVar[str] = (
        "Developer profile, credentials, Claude Code, MCP servers"
    )
    requires_online: ClassVar[bool] = False

    def _check_profile(self) -> CheckResult:
        rai_home = get_global_rai_dir()
        profile_path = rai_home / "developer.yaml"
        if not profile_path.is_file():
            return CheckResult(
                check_id="dev-profile",
                category=self.category,
                status=CheckStatus.WARN,
                message="No developer profile found",
                fix_hint="Run /rai-welcome or `rai profile import bundle.yaml`",
            )
        try:
            raw: object = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                profile_data: dict[str, object] = raw  # type: ignore[assignment]
                name: str = str(profile_data.get("name", "unknown"))
                prefix: str = str(profile_data.get("pattern_prefix", "?"))
                return CheckResult(
                    check_id="dev-profile",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message=f"Developer profile found ({name}, prefix {prefix})",
                )
        except Exception:  # noqa: BLE001, S110
            pass  # Profile check is best-effort
        return CheckResult(
            check_id="dev-profile",
            category=self.category,
            status=CheckStatus.PASS,
            message="Developer profile found",
        )

    def _check_credentials(self, working_dir: Path) -> CheckResult:
        has_env_var = bool(os.environ.get("JIRA_API_TOKEN"))
        has_dotenv = (working_dir / ".env").is_file()

        if has_env_var or has_dotenv:
            return CheckResult(
                check_id="dev-credentials",
                category=self.category,
                status=CheckStatus.PASS,
                message="Jira/Confluence credentials available",
            )
        return CheckResult(
            check_id="dev-credentials",
            category=self.category,
            status=CheckStatus.WARN,
            message="No Jira/Confluence credentials found",
            fix_hint="Create .env with JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN",
        )

    def _check_claude_code(self) -> CheckResult:
        if shutil.which("claude") is not None:
            return CheckResult(
                check_id="dev-claude-code",
                category=self.category,
                status=CheckStatus.PASS,
                message="Claude Code available",
            )
        return CheckResult(
            check_id="dev-claude-code",
            category=self.category,
            status=CheckStatus.WARN,
            message="Claude Code not found in PATH",
            fix_hint="Install Claude Code: https://claude.ai/claude-code",
        )

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run all developer-level checks."""
        results: list[CheckResult] = []
        results.append(self._check_profile())
        results.append(self._check_credentials(context.working_dir))
        results.append(self._check_claude_code())
        results.append(self._check_mcp_servers(context.working_dir))
        results.append(self._check_codex_pipeline_mcp(context.working_dir))
        return results

    def _check_mcp_servers(self, working_dir: Path) -> CheckResult:
        mcp_json = working_dir / ".mcp.json"
        if not mcp_json.is_file():
            return CheckResult(
                check_id="dev-mcp-servers",
                category=self.category,
                status=CheckStatus.WARN,
                message=".mcp.json not found — MCP tools not available to Claude Code",
                fix_hint="run: rai upgrade",
            )
        try:
            raw_json: object = json.loads(mcp_json.read_text(encoding="utf-8"))
            if isinstance(raw_json, dict):
                config_data: dict[str, object] = raw_json  # type: ignore[assignment]
                servers_val: object = config_data.get("mcpServers", {})
                if isinstance(servers_val, dict):
                    server_count: int = len(cast("dict[str, object]", servers_val))
                    if server_count > 0:
                        return CheckResult(
                            check_id="dev-mcp-servers",
                            category=self.category,
                            status=CheckStatus.PASS,
                            message=f"{server_count} MCP server(s) in .mcp.json",
                        )
        except (json.JSONDecodeError, OSError):
            pass
        return CheckResult(
            check_id="dev-mcp-servers",
            category=self.category,
            status=CheckStatus.WARN,
            message=".mcp.json has no MCP servers configured",
            fix_hint="run: rai upgrade",
        )

    def _check_codex_pipeline_mcp(self, working_dir: Path) -> CheckResult:
        config_path = working_dir / ".codex" / "config.toml"
        if not config_path.is_file():
            return CheckResult(
                check_id="dev-codex-pipeline-mcp",
                category=self.category,
                status=CheckStatus.WARN,
                message=".codex/config.toml missing — Codex pipeline MCP tools unavailable",
                fix_hint="run: rai init --agent codex",
            )
        try:
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
            mcp_servers = raw.get("mcp_servers", {})
            if not isinstance(mcp_servers, dict):
                raise ValueError("mcp_servers is not a table")
            server = mcp_servers.get(WORKSPACE_SERVER_NAME, {})
            if not isinstance(server, dict):
                raise ValueError(f"{WORKSPACE_SERVER_NAME} is not a table")
            tools_raw = server.get("enabled_tools", [])
            tools = (
                {str(tool) for tool in tools_raw}
                if isinstance(tools_raw, list)
                else set()
            )
            missing = sorted(_CODEX_REQUIRED_PIPELINE_TOOLS - tools)
            if missing:
                return CheckResult(
                    check_id="dev-codex-pipeline-mcp",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=(
                        f"Codex {WORKSPACE_SERVER_NAME} MCP missing required pipeline tools: "
                        + ", ".join(missing)
                    ),
                    fix_hint="run: rai init --agent codex",
                )
            return CheckResult(
                check_id="dev-codex-pipeline-mcp",
                category=self.category,
                status=CheckStatus.PASS,
                message=f"Codex {WORKSPACE_SERVER_NAME} MCP exposes pipeline tools",
            )
        except (OSError, tomllib.TOMLDecodeError, ValueError):
            return CheckResult(
                check_id="dev-codex-pipeline-mcp",
                category=self.category,
                status=CheckStatus.WARN,
                message=".codex/config.toml invalid — Codex pipeline MCP tools unavailable",
                fix_hint="run: rai init --agent codex",
            )
