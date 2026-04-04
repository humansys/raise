"""Tests for adapter doctor check — S1130.3."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.doctor.checks.adapters import AdapterDoctorCheck
from raise_cli.doctor.models import CheckStatus, DoctorContext

# ── Helpers ──────────────────────────────────────────────────────────


def _make_context(tmp_path: Path, *, online: bool = False) -> DoctorContext:
    """Build a DoctorContext pointing at tmp_path."""
    return DoctorContext(working_dir=tmp_path, online=online)


# ── T1: Config existence checks ─────────────────────────────────────


class TestConfigExistence:
    """Config file existence produces appropriate diagnostics."""

    def test_missing_jira_config_warns(self, tmp_path: Path) -> None:
        """Missing .raise/jira.yaml produces WARN."""
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        jira_results = [
            r for r in results if "jira" in r.check_id and "config" in r.check_id
        ]
        assert len(jira_results) == 1
        assert jira_results[0].status == CheckStatus.WARN
        assert "jira.yaml" in jira_results[0].message

    def test_missing_confluence_config_warns(self, tmp_path: Path) -> None:
        """Missing .raise/confluence.yaml produces WARN."""
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        conf_results = [
            r for r in results if "confluence" in r.check_id and "config" in r.check_id
        ]
        assert len(conf_results) == 1
        assert conf_results[0].status == CheckStatus.WARN
        assert "confluence" in conf_results[0].message.lower()

    def test_config_present_no_warn(self, tmp_path: Path) -> None:
        """Present config files produce PASS (not WARN)."""
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        (raise_dir / "jira.yaml").write_text("default_instance: test\n")
        (raise_dir / "confluence.yaml").write_text("url: https://test\n")
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        config_results = [r for r in results if "config" in r.check_id]
        for r in config_results:
            assert r.status == CheckStatus.PASS

    def test_fix_hint_mentions_setup(self, tmp_path: Path) -> None:
        """Fix hint suggests /rai-adapter-setup."""
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        warn_results = [r for r in results if r.status == CheckStatus.WARN]
        assert len(warn_results) >= 1
        for r in warn_results:
            assert "rai-adapter-setup" in r.fix_hint


# ── T2: Env var checks ──────────────────────────────────────────────


def _setup_configs(tmp_path: Path) -> None:
    """Create both config files so env var checks run."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir(exist_ok=True)
    (raise_dir / "jira.yaml").write_text("default_instance: test\n")
    (raise_dir / "confluence.yaml").write_text("url: https://test\n")


class TestEnvVarChecks:
    """Env var validation when config files exist."""

    def test_missing_jira_token_errors(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing JIRA_API_TOKEN produces ERROR."""
        _setup_configs(tmp_path)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        token_results = [r for r in results if r.check_id == "adapter-jira-token"]
        assert len(token_results) == 1
        assert token_results[0].status == CheckStatus.ERROR
        assert "JIRA_API_TOKEN" in token_results[0].message

    def test_present_jira_token_passes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Set JIRA_API_TOKEN produces PASS."""
        _setup_configs(tmp_path)
        monkeypatch.setenv("JIRA_API_TOKEN", "test-token")
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        token_results = [r for r in results if r.check_id == "adapter-jira-token"]
        assert len(token_results) == 1
        assert token_results[0].status == CheckStatus.PASS

    def test_missing_confluence_token_errors(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing CONFLUENCE_API_TOKEN produces ERROR."""
        _setup_configs(tmp_path)
        monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        token_results = [r for r in results if r.check_id == "adapter-confluence-token"]
        assert len(token_results) == 1
        assert token_results[0].status == CheckStatus.ERROR
        assert "CONFLUENCE_API_TOKEN" in token_results[0].message

    def test_no_env_checks_when_config_missing(self, tmp_path: Path) -> None:
        """Env var checks are skipped when config file is absent."""
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        env_results = [
            r
            for r in results
            if "token" in r.check_id
            or "email" in r.check_id
            or "username" in r.check_id
        ]
        assert len(env_results) == 0


# ── T3: Live health checks ──────────────────────────────────────────


class TestLiveHealthChecks:
    """Online mode health checks for adapter backends."""

    def test_offline_skips_health(self, tmp_path: Path) -> None:
        """Offline mode does not produce health check results."""
        _setup_configs(tmp_path)
        ctx = _make_context(tmp_path, online=False)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        health_results = [r for r in results if "health" in r.check_id]
        assert len(health_results) == 0

    def test_online_calls_health_checks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Online mode invokes health check methods."""
        from unittest.mock import MagicMock, patch

        _setup_configs(tmp_path)
        monkeypatch.setenv("JIRA_API_TOKEN", "test")
        monkeypatch.setenv("JIRA_EMAIL", "test@test.com")
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "test")
        monkeypatch.setenv("CONFLUENCE_USERNAME", "test@test.com")
        ctx = _make_context(tmp_path, online=True)
        check = AdapterDoctorCheck()

        mock_jira = MagicMock()
        mock_conf = MagicMock()
        with (
            patch.object(check, "_check_jira_health", mock_jira),
            patch.object(check, "_check_confluence_health", mock_conf),
        ):
            check.evaluate(ctx)

        mock_jira.assert_called_once()
        mock_conf.assert_called_once()

    def test_health_error_on_exception(self, tmp_path: Path) -> None:
        """Health check exception produces ERROR result (never crashes)."""
        _setup_configs(tmp_path)
        ctx = _make_context(tmp_path, online=True)
        check = AdapterDoctorCheck()

        # Health checks will fail because no real config/credentials
        # but should produce ERROR results, not raise
        results = check.evaluate(ctx)
        health_results = [r for r in results if "health" in r.check_id]
        for r in health_results:
            assert r.status == CheckStatus.ERROR


# ── T4: Confluence space existence checks (S1051.5/T1) ────────────


def _setup_confluence_config(
    tmp_path: Path, *, routing: dict[str, dict[str, object]] | None = None
) -> None:
    """Create a valid multi-instance confluence.yaml for online tests."""
    import yaml

    routing_block = routing or {}
    data = {
        "default_instance": "default",
        "instances": {
            "default": {
                "url": "https://test.atlassian.net/wiki",
                "space_key": "TEST",
                "instance_name": "default",
                "routing": routing_block,
            }
        },
    }
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir(exist_ok=True)
    (raise_dir / "confluence.yaml").write_text(yaml.dump(data))
    # Also create jira.yaml to avoid early exit
    (raise_dir / "jira.yaml").write_text("default_instance: test\n")


class TestConfluenceSpaceCheck:
    """Online space existence checks — S1051.5/T1."""

    def test_space_exists_passes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Space found on instance produces PASS."""
        from unittest.mock import MagicMock, patch

        _setup_confluence_config(tmp_path)
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "tok")
        monkeypatch.setenv("CONFLUENCE_USERNAME", "user@test.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "tok")
        ctx = _make_context(tmp_path, online=True)
        check = AdapterDoctorCheck()

        mock_discovery_inst = MagicMock()
        mock_discovery_inst.discover.return_value = MagicMock()

        with (
            patch.object(check, "_check_jira_health", MagicMock()),
            patch.object(check, "_check_confluence_health", MagicMock()),
            patch(
                "raise_cli.adapters.confluence_discovery.ConfluenceDiscovery",
                return_value=mock_discovery_inst,
            ),
            patch(
                "raise_cli.adapters.confluence_client.ConfluenceClient",
                return_value=MagicMock(),
            ),
        ):
            results = check.evaluate(ctx)

        space_results = [
            r for r in results if r.check_id == "adapter-confluence-space-exists"
        ]
        assert len(space_results) == 1
        assert space_results[0].status == CheckStatus.PASS
        assert "TEST" in space_results[0].message

    def test_space_missing_errors_with_available(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing space produces ERROR with available spaces in message."""
        from unittest.mock import MagicMock, patch

        from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError

        _setup_confluence_config(tmp_path)
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "tok")
        monkeypatch.setenv("CONFLUENCE_USERNAME", "user@test.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "tok")
        ctx = _make_context(tmp_path, online=True)
        check = AdapterDoctorCheck()

        mock_discovery_inst = MagicMock()
        mock_discovery_inst.discover.side_effect = ConfluenceNotFoundError(
            "Space 'TEST' not found. Available: RaiSE1, DEMO"
        )

        with (
            patch.object(check, "_check_jira_health", MagicMock()),
            patch.object(check, "_check_confluence_health", MagicMock()),
            patch(
                "raise_cli.adapters.confluence_discovery.ConfluenceDiscovery",
                return_value=mock_discovery_inst,
            ),
            patch(
                "raise_cli.adapters.confluence_client.ConfluenceClient",
                return_value=MagicMock(),
            ),
        ):
            results = check.evaluate(ctx)

        space_results = [
            r for r in results if r.check_id == "adapter-confluence-space-exists"
        ]
        assert len(space_results) == 1
        assert space_results[0].status == CheckStatus.ERROR
        assert "TEST" in space_results[0].message
        assert space_results[0].fix_hint is not None
        assert "Available" in space_results[0].fix_hint

    def test_discovery_exception_errors_with_hint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Generic discovery exception produces ERROR with connectivity hint."""
        from unittest.mock import MagicMock, patch

        _setup_confluence_config(tmp_path)
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "tok")
        monkeypatch.setenv("CONFLUENCE_USERNAME", "user@test.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "tok")
        ctx = _make_context(tmp_path, online=True)
        check = AdapterDoctorCheck()

        mock_discovery_inst = MagicMock()
        mock_discovery_inst.discover.side_effect = ConnectionError("timeout")

        with (
            patch.object(check, "_check_jira_health", MagicMock()),
            patch.object(check, "_check_confluence_health", MagicMock()),
            patch(
                "raise_cli.adapters.confluence_discovery.ConfluenceDiscovery",
                return_value=mock_discovery_inst,
            ),
            patch(
                "raise_cli.adapters.confluence_client.ConfluenceClient",
                return_value=MagicMock(),
            ),
        ):
            results = check.evaluate(ctx)

        space_results = [
            r for r in results if r.check_id == "adapter-confluence-space-exists"
        ]
        assert len(space_results) == 1
        assert space_results[0].status == CheckStatus.ERROR
        assert "connectivity" in (space_results[0].fix_hint or "").lower()

    def test_offline_skips_space_check(self, tmp_path: Path) -> None:
        """Offline mode does not produce space check results."""
        _setup_confluence_config(tmp_path)
        ctx = _make_context(tmp_path, online=False)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        space_results = [r for r in results if "space" in r.check_id]
        assert len(space_results) == 0
