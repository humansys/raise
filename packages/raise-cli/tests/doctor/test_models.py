"""Tests for doctor models."""

from pathlib import Path

import pytest

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


class TestCheckStatus:
    def test_three_levels(self) -> None:
        assert CheckStatus.PASS.value == "pass"
        assert CheckStatus.WARN.value == "warn"
        assert CheckStatus.ERROR.value == "error"


class TestCheckResult:
    def test_minimal(self) -> None:
        r = CheckResult(
            check_id="test", category="env", status=CheckStatus.PASS, message="ok"
        )
        assert r.check_id == "test"
        assert r.fix_hint == ""
        assert r.details == ()

    def test_with_fix_hint(self) -> None:
        r = CheckResult(
            check_id="test",
            category="env",
            status=CheckStatus.ERROR,
            message="missing",
            fix_hint="run: pip install foo",
        )
        assert r.fix_hint == "run: pip install foo"

    def test_frozen(self) -> None:
        r = CheckResult(
            check_id="test", category="env", status=CheckStatus.PASS, message="ok"
        )
        with pytest.raises(AttributeError):
            r.message = "changed"  # type: ignore[misc]


class TestDoctorContext:
    def test_defaults(self) -> None:
        ctx = DoctorContext()
        assert isinstance(ctx.working_dir, Path)
        assert ctx.online is False
        assert ctx.verbose is False

    def test_custom(self, tmp_path: Path) -> None:
        ctx = DoctorContext(working_dir=tmp_path, online=True, verbose=True)
        assert ctx.working_dir == tmp_path
        assert ctx.online is True
