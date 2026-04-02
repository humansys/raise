"""Tests for adapter doctor check — S1130.3."""

from __future__ import annotations

from pathlib import Path

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
        jira_results = [r for r in results if "jira" in r.check_id and "config" in r.check_id]
        assert len(jira_results) == 1
        assert jira_results[0].status == CheckStatus.WARN
        assert "jira.yaml" in jira_results[0].message

    def test_missing_confluence_config_warns(self, tmp_path: Path) -> None:
        """Missing .raise/confluence.yaml produces WARN."""
        ctx = _make_context(tmp_path)
        check = AdapterDoctorCheck()
        results = check.evaluate(ctx)
        conf_results = [r for r in results if "confluence" in r.check_id and "config" in r.check_id]
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
