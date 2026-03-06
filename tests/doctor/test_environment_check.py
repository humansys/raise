"""Tests for EnvironmentCheck diagnostic."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any
from unittest.mock import patch

from raise_cli.doctor.checks.environment import EnvironmentCheck
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


def _ctx() -> DoctorContext:
    return DoctorContext()


class TestPythonVersion:
    def test_pass_on_current(self) -> None:
        """Current interpreter is >= 3.11, so check should PASS."""
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        py_result = _find(results, "env-python-version")
        assert py_result.status == CheckStatus.PASS
        version_str = f"{sys.version_info[0]}.{sys.version_info[1]}"
        assert version_str in py_result.message

    def test_error_on_old_python(self) -> None:
        fake_info = (3, 10, 0, "final", 0)
        with patch.object(sys, "version_info", fake_info):
            check = EnvironmentCheck()
            results = check.evaluate(_ctx())
        py_result = _find(results, "env-python-version")
        assert py_result.status == CheckStatus.ERROR
        assert "3.10" in py_result.message
        assert py_result.fix_hint != ""


class TestRaiVersion:
    def test_reports_version(self) -> None:
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        ver_result = _find(results, "env-rai-version")
        assert ver_result.status == CheckStatus.PASS
        assert "raise-cli" in ver_result.message


class TestOSInfo:
    def test_reports_platform(self) -> None:
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        os_result = _find(results, "env-os-info")
        assert os_result.status == CheckStatus.PASS
        assert os_result.message != ""


class TestOptionalExtras:
    def test_pass_when_installed(self) -> None:
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        # httpx is always available in test environment
        httpx_result = _find(results, "env-extra-httpx")
        assert httpx_result.status == CheckStatus.PASS

    def test_warn_when_missing(self) -> None:
        original_import = (
            __builtins__.__import__
            if hasattr(__builtins__, "__import__")
            else __import__
        )  # type: ignore[union-attr]

        def _fake_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:
            if name == "mcp":
                raise ImportError("No module named 'mcp'")
            return original_import(name, *args, **kwargs)  # type: ignore[operator]

        with patch("importlib.import_module", side_effect=_fake_import):
            check = EnvironmentCheck()
            results = check.evaluate(_ctx())

        mcp_result = _find(results, "env-extra-mcp")
        assert mcp_result.status == CheckStatus.WARN
        assert "pip install" in mcp_result.fix_hint


class TestResultStructure:
    def test_returns_five_results(self) -> None:
        """Python + raise-cli + OS + 2 extras = 5 results."""
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        assert len(results) == 5

    def test_all_in_environment_category(self) -> None:
        check = EnvironmentCheck()
        results = check.evaluate(_ctx())
        for r in results:
            assert r.category == "environment"


def _find(results: list[CheckResult], check_id: str) -> CheckResult:
    for r in results:
        if r.check_id == check_id:
            return r
    raise AssertionError(f"No result with check_id={check_id!r}")
