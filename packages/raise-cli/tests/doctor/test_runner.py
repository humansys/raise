"""Tests for doctor check runner."""

from pathlib import Path

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.registry import CheckRegistry
from raise_cli.doctor.runner import run_checks, summarize


class _PassCheck:
    check_id = "env-ok"
    category = "environment"
    description = "Pass check"
    requires_online = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="Python 3.12",
            )
        ]


class _WarnCheck:
    check_id = "project-warn"
    category = "project"
    description = "Warn check"
    requires_online = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message="Graph stale",
                fix_hint="run: rai graph build",
            )
        ]


class _ErrorCheck:
    check_id = "env-error"
    category = "environment"
    description = "Error check"
    requires_online = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.ERROR,
                message="Python 3.8 unsupported",
            )
        ]


class _OnlineCheck:
    check_id = "mcp-health"
    category = "mcp"
    description = "MCP check"
    requires_online = True

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="MCP healthy",
            )
        ]


class _CrashCheck:
    check_id = "crash"
    category = "project"
    description = "Crashes"
    requires_online = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        msg = "boom"
        raise RuntimeError(msg)


def _context(tmp_path: Path, online: bool = False) -> DoctorContext:
    return DoctorContext(working_dir=tmp_path, online=online)


class TestRunChecks:
    def test_empty_registry(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        results = run_checks(registry, _context(tmp_path))
        assert results == []

    def test_pass_and_warn(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_PassCheck())
        registry.register(_WarnCheck())
        results = run_checks(registry, _context(tmp_path))
        assert len(results) == 2
        statuses = {r.status for r in results}
        assert statuses == {CheckStatus.PASS, CheckStatus.WARN}

    def test_online_check_skipped_by_default(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_OnlineCheck())
        results = run_checks(registry, _context(tmp_path, online=False))
        assert len(results) == 0

    def test_online_check_runs_with_flag(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_OnlineCheck())
        results = run_checks(registry, _context(tmp_path, online=True))
        assert len(results) == 1
        assert results[0].check_id == "mcp-health"

    def test_crash_handled_gracefully(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_CrashCheck())
        results = run_checks(registry, _context(tmp_path))
        assert len(results) == 1
        assert results[0].status == CheckStatus.ERROR
        assert "boom" in results[0].message

    def test_environment_error_skips_downstream(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_ErrorCheck())
        registry.register(_WarnCheck())
        results = run_checks(registry, _context(tmp_path))
        # Environment error + project skipped
        project_results = [r for r in results if r.category == "project"]
        assert len(project_results) == 1
        assert project_results[0].status == CheckStatus.WARN
        assert "Skipped" in project_results[0].message

    def test_category_filter(self, tmp_path: Path) -> None:
        registry = CheckRegistry()
        registry.register(_PassCheck())
        registry.register(_WarnCheck())
        results = run_checks(registry, _context(tmp_path), categories=["project"])
        assert all(r.category == "project" for r in results)


class TestSummarize:
    def test_all_pass(self) -> None:
        results = [
            CheckResult(
                check_id="a", category="env", status=CheckStatus.PASS, message="ok"
            ),
        ]
        assert summarize(results) == (1, 0, 0)

    def test_mixed(self) -> None:
        results = [
            CheckResult(
                check_id="a", category="env", status=CheckStatus.PASS, message="ok"
            ),
            CheckResult(
                check_id="b", category="env", status=CheckStatus.WARN, message="warn"
            ),
            CheckResult(
                check_id="c", category="proj", status=CheckStatus.ERROR, message="err"
            ),
        ]
        assert summarize(results) == (1, 1, 1)
