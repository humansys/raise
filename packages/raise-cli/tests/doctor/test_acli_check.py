"""Tests for AcliCheck — ACLI availability, config, and auth diagnostics."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


def _ctx(tmp_path: Path | None = None, *, online: bool = False) -> DoctorContext:
    return DoctorContext(
        working_dir=tmp_path or Path.cwd(),
        online=online,
    )


def _find(results: list[CheckResult], check_id: str) -> CheckResult:
    for r in results:
        if r.check_id == check_id:
            return r
    raise AssertionError(f"No result with check_id={check_id!r}")


def _find_prefix(results: list[CheckResult], prefix: str) -> list[CheckResult]:
    return [r for r in results if r.check_id.startswith(prefix)]


def _write_jira_yaml(tmp_path: Path) -> None:
    """Write a minimal jira.yaml for testing."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir(exist_ok=True)
    config = {
        "default_instance": "primary",
        "instances": {
            "primary": {
                "site": "primary.atlassian.net",
                "projects": ["PROJ"],
            },
            "secondary": {
                "site": "secondary.atlassian.net",
                "projects": ["EXT"],
            },
        },
    }
    (raise_dir / "jira.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


# ---------------------------------------------------------------------------
# acli-installed
# ---------------------------------------------------------------------------


class TestAcliInstalled:
    def test_pass_when_in_path(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        result = _find(results, "acli-installed")
        assert result.status == CheckStatus.PASS

    def test_error_when_missing(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        with patch("shutil.which", return_value=None):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        result = _find(results, "acli-installed")
        assert result.status == CheckStatus.ERROR
        assert "developer.atlassian.com" in result.fix_hint


# ---------------------------------------------------------------------------
# acli-jira-config
# ---------------------------------------------------------------------------


class TestJiraConfig:
    def test_pass_when_config_exists(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)
        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        result = _find(results, "acli-jira-config")
        assert result.status == CheckStatus.PASS
        assert "2 instance" in result.message

    def test_warn_when_missing(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        result = _find(results, "acli-jira-config")
        assert result.status == CheckStatus.WARN
        assert "jira.yaml" in result.fix_hint

    def test_warn_when_no_instances(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir(exist_ok=True)
        (raise_dir / "jira.yaml").write_text("default_instance: x\n", encoding="utf-8")
        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        result = _find(results, "acli-jira-config")
        assert result.status == CheckStatus.WARN


# ---------------------------------------------------------------------------
# acli-auth-{site} (online only)
# ---------------------------------------------------------------------------


class TestAcliAuth:
    def test_skipped_when_offline(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)
        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path, online=False))
        auth_results = _find_prefix(results, "acli-auth-")
        assert len(auth_results) == 0

    def test_pass_all_sites_authenticated(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)

        async def _mock_exec(*args: object, **kwargs: object) -> AsyncMock:
            proc = AsyncMock()
            proc.returncode = 0
            proc.communicate.return_value = (b"Authenticated", b"")
            return proc

        with (
            patch("shutil.which", return_value="/usr/local/bin/acli"),
            patch("asyncio.create_subprocess_exec", side_effect=_mock_exec),
        ):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path, online=True))

        auth_results = _find_prefix(results, "acli-auth-")
        assert len(auth_results) == 2
        assert all(r.status == CheckStatus.PASS for r in auth_results)

    def test_warn_one_site_fails(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)
        call_count = 0

        async def _mock_exec(*args: object, **kwargs: object) -> AsyncMock:
            nonlocal call_count
            call_count += 1
            proc = AsyncMock()
            # First site passes (switch + status), second fails
            if call_count <= 2:
                proc.returncode = 0
                proc.communicate.return_value = (b"Authenticated", b"")
            else:
                proc.returncode = 1
                proc.communicate.return_value = (b"", b"Not authenticated")
            return proc

        with (
            patch("shutil.which", return_value="/usr/local/bin/acli"),
            patch("asyncio.create_subprocess_exec", side_effect=_mock_exec),
        ):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path, online=True))

        auth_results = _find_prefix(results, "acli-auth-")
        assert len(auth_results) == 2
        statuses = {r.status for r in auth_results}
        assert CheckStatus.PASS in statuses
        assert CheckStatus.WARN in statuses

    def test_error_when_no_site_authenticates(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)

        async def _mock_exec(*args: object, **kwargs: object) -> AsyncMock:
            proc = AsyncMock()
            proc.returncode = 1
            proc.communicate.return_value = (b"", b"Not authenticated")
            return proc

        with (
            patch("shutil.which", return_value="/usr/local/bin/acli"),
            patch("asyncio.create_subprocess_exec", side_effect=_mock_exec),
        ):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path, online=True))

        auth_results = _find_prefix(results, "acli-auth-")
        assert len(auth_results) == 2
        assert all(r.status == CheckStatus.ERROR for r in auth_results)


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


class TestStructure:
    def test_all_in_acli_category(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        for r in results:
            assert r.category == "acli"

    def test_offline_returns_two_results(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        _write_jira_yaml(tmp_path)
        with patch("shutil.which", return_value="/usr/local/bin/acli"):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        assert len(results) == 2  # installed + config

    def test_stops_early_when_acli_missing(self, tmp_path: Path) -> None:
        from rai_pro.doctor.acli import AcliCheck

        with patch("shutil.which", return_value=None):
            check = AcliCheck()
            results = check.evaluate(_ctx(tmp_path))
        # Only the installed check — no point checking config/auth
        assert len(results) == 1
