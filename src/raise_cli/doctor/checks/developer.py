"""Developer diagnostic check — profile, credentials, Claude Code, MCP servers.

Reports developer-level setup status for new machine readiness.
All checks are advisory (WARN, not ERROR) since the CLI works without them.

Architecture: E493/S493.4, extends ADR-045.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import ClassVar, cast

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


def _get_rai_home() -> Path:
    """Return ~/.rai directory path."""
    return Path.home() / ".rai"


def _get_claude_config_path() -> Path:
    """Return ~/.claude.json path."""
    return Path.home() / ".claude.json"


class DeveloperCheck:
    """Validates developer-level setup: profile, credentials, Claude Code, MCP.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "developer"
    category: ClassVar[str] = "developer"
    description: ClassVar[str] = (
        "Developer profile, credentials, Claude Code, MCP servers"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run all developer-level checks."""
        results: list[CheckResult] = []
        results.append(self._check_profile())
        results.append(self._check_credentials(context.working_dir))
        results.append(self._check_claude_code())
        results.append(self._check_mcp_servers())
        return results

    @staticmethod
    def _check_profile() -> CheckResult:
        rai_home = _get_rai_home()
        profile_path = rai_home / "developer.yaml"
        if not profile_path.is_file():
            return CheckResult(
                check_id="dev-profile",
                category="developer",
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
                    category="developer",
                    status=CheckStatus.PASS,
                    message=f"Developer profile found ({name}, prefix {prefix})",
                )
        except Exception:  # noqa: BLE001, S110
            pass  # Profile check is best-effort
        return CheckResult(
            check_id="dev-profile",
            category="developer",
            status=CheckStatus.PASS,
            message="Developer profile found",
        )

    @staticmethod
    def _check_credentials(working_dir: Path) -> CheckResult:
        has_env_var = bool(os.environ.get("JIRA_API_TOKEN"))
        has_dotenv = (working_dir / ".env").is_file()

        if has_env_var or has_dotenv:
            return CheckResult(
                check_id="dev-credentials",
                category="developer",
                status=CheckStatus.PASS,
                message="Jira/Confluence credentials available",
            )
        return CheckResult(
            check_id="dev-credentials",
            category="developer",
            status=CheckStatus.WARN,
            message="No Jira/Confluence credentials found",
            fix_hint="Create .env with JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN",
        )

    @staticmethod
    def _check_claude_code() -> CheckResult:
        if shutil.which("claude") is not None:
            return CheckResult(
                check_id="dev-claude-code",
                category="developer",
                status=CheckStatus.PASS,
                message="Claude Code available",
            )
        return CheckResult(
            check_id="dev-claude-code",
            category="developer",
            status=CheckStatus.WARN,
            message="Claude Code not found in PATH",
            fix_hint="Install Claude Code: https://claude.ai/claude-code",
        )

    @staticmethod
    def _check_mcp_servers() -> CheckResult:
        config_path = _get_claude_config_path()
        if not config_path.is_file():
            return CheckResult(
                check_id="dev-mcp-servers",
                category="developer",
                status=CheckStatus.WARN,
                message="No Claude config found (~/.claude.json)",
                fix_hint="Run /rai-mcp-add to configure MCP servers",
            )
        try:
            raw_json: object = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(raw_json, dict):
                config_data: dict[str, object] = raw_json  # type: ignore[assignment]
                servers_val: object = config_data.get("mcpServers", {})
                if isinstance(servers_val, dict):
                    server_count: int = len(cast("dict[str, object]", servers_val))
                    if server_count > 0:
                        return CheckResult(
                            check_id="dev-mcp-servers",
                            category="developer",
                            status=CheckStatus.PASS,
                            message=f"{server_count} MCP server(s) configured",
                        )
        except (json.JSONDecodeError, OSError):
            pass  # noqa: S110
        return CheckResult(
            check_id="dev-mcp-servers",
            category="developer",
            status=CheckStatus.WARN,
            message="No MCP servers configured",
            fix_hint="Run /rai-mcp-add to configure MCP servers",
        )
