"""Tests for DeveloperCheck diagnostic."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from raise_cli.doctor.checks.developer import DeveloperCheck
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


def _ctx(tmp_path: Path | None = None) -> DoctorContext:
    if tmp_path is not None:
        return DoctorContext(working_dir=tmp_path)
    return DoctorContext()


def _find(results: list[CheckResult], check_id: str) -> CheckResult:
    for r in results:
        if r.check_id == check_id:
            return r
    raise AssertionError(f"No result with check_id={check_id!r}")


class TestProfileCheck:
    def test_pass_when_profile_exists(self, tmp_path: Path) -> None:
        """Profile check passes when developer.yaml exists."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir()
        profile = rai_home / "developer.yaml"
        profile.write_text("name: Emilio\npattern_prefix: E\n")

        with patch(
            "raise_cli.doctor.checks.developer._get_rai_home", return_value=rai_home
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-profile")
        assert result.status == CheckStatus.PASS
        assert "Emilio" in result.message

    def test_warn_when_profile_missing(self, tmp_path: Path) -> None:
        """Profile check warns when no developer.yaml."""
        rai_home = tmp_path / ".rai"

        with patch(
            "raise_cli.doctor.checks.developer._get_rai_home", return_value=rai_home
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-profile")
        assert result.status == CheckStatus.WARN
        assert result.fix_hint != ""


class TestCredentialsCheck:
    def test_pass_when_env_vars_set(self, tmp_path: Path) -> None:
        """Credentials pass when JIRA_API_TOKEN is in environment."""
        env = {"JIRA_API_TOKEN": "secret", "JIRA_URL": "https://x.atlassian.net"}
        with patch.dict("os.environ", env, clear=False):
            check = DeveloperCheck()
            results = check.evaluate(_ctx(tmp_path))

        result = _find(results, "dev-credentials")
        assert result.status == CheckStatus.PASS

    def test_pass_when_dotenv_exists(self, tmp_path: Path) -> None:
        """Credentials pass when .env file exists in working dir."""
        dotenv = tmp_path / ".env"
        dotenv.write_text("JIRA_API_TOKEN=secret\n")
        env: dict[str, str] = {}
        with patch.dict("os.environ", env, clear=True):
            check = DeveloperCheck()
            results = check.evaluate(_ctx(tmp_path))

        result = _find(results, "dev-credentials")
        assert result.status == CheckStatus.PASS

    def test_warn_when_no_credentials(self, tmp_path: Path) -> None:
        """Credentials warn when no env vars and no .env."""
        env: dict[str, str] = {}
        with patch.dict("os.environ", env, clear=True):
            check = DeveloperCheck()
            results = check.evaluate(_ctx(tmp_path))

        result = _find(results, "dev-credentials")
        assert result.status == CheckStatus.WARN
        assert ".env" in result.fix_hint


class TestClaudeCodeCheck:
    def test_pass_when_claude_available(self) -> None:
        """Claude Code check passes when claude is in PATH."""
        with patch("shutil.which", return_value="/usr/bin/claude"):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-claude-code")
        assert result.status == CheckStatus.PASS

    def test_warn_when_claude_missing(self) -> None:
        """Claude Code check warns when claude not in PATH."""
        with patch("shutil.which", return_value=None):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-claude-code")
        assert result.status == CheckStatus.WARN
        assert result.fix_hint != ""


class TestMCPServersCheck:
    def test_pass_when_mcp_configured(self, tmp_path: Path) -> None:
        """MCP check passes when ~/.claude.json has mcpServers."""
        claude_json = tmp_path / ".claude.json"
        claude_json.write_text(json.dumps({"mcpServers": {"jira": {}}}))

        with patch(
            "raise_cli.doctor.checks.developer._get_claude_config_path",
            return_value=claude_json,
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-mcp-servers")
        assert result.status == CheckStatus.PASS
        assert "1" in result.message

    def test_warn_when_no_mcp_config(self, tmp_path: Path) -> None:
        """MCP check warns when ~/.claude.json missing."""
        missing = tmp_path / "nonexistent.json"

        with patch(
            "raise_cli.doctor.checks.developer._get_claude_config_path",
            return_value=missing,
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-mcp-servers")
        assert result.status == CheckStatus.WARN

    def test_warn_when_mcp_empty(self, tmp_path: Path) -> None:
        """MCP check warns when mcpServers is empty."""
        claude_json = tmp_path / ".claude.json"
        claude_json.write_text(json.dumps({"mcpServers": {}}))

        with patch(
            "raise_cli.doctor.checks.developer._get_claude_config_path",
            return_value=claude_json,
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())

        result = _find(results, "dev-mcp-servers")
        assert result.status == CheckStatus.WARN


class TestResultStructure:
    def test_returns_four_results(self) -> None:
        """Profile + credentials + claude + mcp = 4 results."""
        with (
            patch(
                "raise_cli.doctor.checks.developer._get_rai_home",
                return_value=Path("/nonexistent"),
            ),
            patch("shutil.which", return_value=None),
            patch(
                "raise_cli.doctor.checks.developer._get_claude_config_path",
                return_value=Path("/nonexistent"),
            ),
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())
        assert len(results) == 4

    def test_all_in_developer_category(self) -> None:
        """All results should be in developer category."""
        with (
            patch(
                "raise_cli.doctor.checks.developer._get_rai_home",
                return_value=Path("/nonexistent"),
            ),
            patch("shutil.which", return_value=None),
            patch(
                "raise_cli.doctor.checks.developer._get_claude_config_path",
                return_value=Path("/nonexistent"),
            ),
        ):
            check = DeveloperCheck()
            results = check.evaluate(_ctx())
        for r in results:
            assert r.category == "developer"
