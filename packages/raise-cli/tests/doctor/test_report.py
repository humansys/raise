"""Tests for diagnostic report generation and email submission."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.doctor.models import CheckResult, CheckStatus
from raise_cli.doctor.report import (
    DiagnosticReport,
    generate_report,
    open_mailto,
    report_to_markdown,
    save_report,
)

runner = CliRunner()


def _sample_results() -> list[CheckResult]:
    """Create sample check results for testing."""
    return [
        CheckResult(
            check_id="env-python",
            category="python",
            status=CheckStatus.PASS,
            message="Python 3.12 detected",
        ),
        CheckResult(
            check_id="proj-config",
            category="config",
            status=CheckStatus.WARN,
            message=".raise/config.yaml missing",
            fix_hint="Run rai init",
        ),
        CheckResult(
            check_id="proj-graph",
            category="graph",
            status=CheckStatus.ERROR,
            message="Graph stale (30 days)",
        ),
    ]


class TestGenerateReport:
    """Tests for generate_report."""

    def test_collects_version_info(self, tmp_path: Path) -> None:
        """Report contains Python version and OS info."""
        report = generate_report([], tmp_path)
        assert report.python_version  # non-empty
        assert report.os_info  # non-empty

    def test_collects_rai_version(self, tmp_path: Path) -> None:
        """Report contains raise-cli version."""
        report = generate_report([], tmp_path)
        assert report.rai_version  # either version string or "unknown"

    def test_collects_raise_structure_names_only(self, tmp_path: Path) -> None:
        """Report contains file names from .raise/ but not contents."""
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        secret_file = raise_dir / "config.yaml"
        secret_file.write_text("api_key: super-secret-value")

        report = generate_report([], tmp_path)

        # Structure has the file name
        assert any("config.yaml" in s for s in report.raise_structure)
        # But the report object has no file contents
        md = report_to_markdown(report)
        assert "super-secret-value" not in md

    def test_caps_structure_at_50(self, tmp_path: Path) -> None:
        """Structure list is capped at 50 entries."""
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        for i in range(60):
            (raise_dir / f"file-{i:03d}.txt").write_text("x")

        report = generate_report([], tmp_path)
        assert len(report.raise_structure) == 50

    def test_includes_check_results(self, tmp_path: Path) -> None:
        """Report preserves check results passed in."""
        results = _sample_results()
        report = generate_report(results, tmp_path)
        assert len(report.check_results) == 3

    def test_has_utc_timestamp(self, tmp_path: Path) -> None:
        """Timestamp is in UTC ISO format."""
        report = generate_report([], tmp_path)
        assert "+00:00" in report.timestamp or "Z" in report.timestamp


class TestReportToMarkdown:
    """Tests for report_to_markdown."""

    def test_valid_markdown_header(self) -> None:
        """Output starts with markdown header."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
        )
        md = report_to_markdown(report)
        assert md.startswith("# rai doctor report")

    def test_contains_version_fields(self) -> None:
        """Markdown includes version, python, os fields."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
        )
        md = report_to_markdown(report)
        assert "**raise-cli:** 2.1.0" in md
        assert "**Python:** 3.12.0" in md
        assert "**OS:** Linux" in md

    def test_check_result_icons(self) -> None:
        """Check results show correct status icons."""
        results = _sample_results()
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=results,
        )
        md = report_to_markdown(report)
        assert "[OK] python:" in md
        assert "[!!] config:" in md
        assert "[XX] graph:" in md

    def test_fix_hints_rendered(self) -> None:
        """Fix hints appear in markdown output."""
        results = _sample_results()
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=results,
        )
        md = report_to_markdown(report)
        assert "hint: Run rai init" in md

    def test_extras_none_shown(self) -> None:
        """When no extras, show 'none'."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
            installed_extras=[],
        )
        md = report_to_markdown(report)
        assert "**Extras:** none" in md

    def test_structure_section(self) -> None:
        """Structure section appears when files exist."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
            raise_structure=[".raise/config.yaml", ".raise/mcp/server.yaml"],
        )
        md = report_to_markdown(report)
        assert "## .raise/ structure" in md
        assert "- .raise/config.yaml" in md


class TestSaveReport:
    """Tests for save_report."""

    def test_saves_to_personal_dir(self, tmp_path: Path) -> None:
        """Report is saved to .raise/rai/personal/ directory."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
        )
        path = save_report(report, tmp_path)
        assert path.exists()
        assert ".raise/rai/personal" in str(path)
        assert path.name.startswith("report-")
        assert path.name.endswith(".md")

    def test_file_contains_markdown(self, tmp_path: Path) -> None:
        """Saved file contains the markdown report."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
        )
        path = save_report(report, tmp_path)
        content = path.read_text()
        assert "# rai doctor report" in content


class TestOpenMailto:
    """Tests for open_mailto."""

    def test_builds_correct_mailto_uri(self) -> None:
        """Mailto URI contains subject and body."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=_sample_results(),
        )
        with patch("raise_cli.doctor.report.webbrowser.open") as mock_open:
            mock_open.return_value = True
            result = open_mailto(report)

        assert result is True
        call_url = mock_open.call_args[0][0]
        assert call_url.startswith("mailto:support@raise.humansys.ai")
        assert "subject=" in call_url
        assert "body=" in call_url
        assert "rai-doctor" in call_url

    def test_subject_includes_error_count(self) -> None:
        """Subject line mentions error and warning counts."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=_sample_results(),
        )
        with patch("raise_cli.doctor.report.webbrowser.open") as mock_open:
            mock_open.return_value = True
            open_mailto(report)

        call_url = mock_open.call_args[0][0]
        # 1 error, 1 warning from sample results
        assert "1%20error" in call_url or "1 error" in call_url

    def test_body_truncated_at_1800(self) -> None:
        """Body is truncated for long reports."""
        # Create many check results to make a long report
        results = [
            CheckResult(
                check_id=f"chk-{i}",
                category=f"check-{i}",
                status=CheckStatus.WARN,
                message="x" * 100,
                fix_hint="y" * 50,
            )
            for i in range(30)
        ]
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=results,
        )
        with patch("raise_cli.doctor.report.webbrowser.open") as mock_open:
            mock_open.return_value = True
            open_mailto(report)

        call_url = mock_open.call_args[0][0]
        # URL-decoded body should contain truncation notice
        assert "truncated" in call_url

    def test_returns_false_on_failure(self) -> None:
        """Returns False when webbrowser.open fails."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[],
        )
        with patch(
            "raise_cli.doctor.report.webbrowser.open", side_effect=OSError("no browser")
        ):
            result = open_mailto(report)
        assert result is False

    def test_all_clear_subject(self) -> None:
        """Subject says 'all clear' when no issues."""
        report = DiagnosticReport(
            timestamp="2026-03-05T00:00:00+00:00",
            rai_version="2.1.0",
            python_version="3.12.0",
            os_info="Linux 6.17.0 (x86_64)",
            check_results=[
                CheckResult(
                    check_id="test-ok",
                    category="test",
                    status=CheckStatus.PASS,
                    message="OK",
                ),
            ],
        )
        with patch("raise_cli.doctor.report.webbrowser.open") as mock_open:
            mock_open.return_value = True
            open_mailto(report)

        call_url = mock_open.call_args[0][0]
        assert "all%20clear" in call_url or "all clear" in call_url


class TestDoctorReportCLI:
    """CLI integration tests for rai doctor report."""

    def test_report_command_runs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Rai doctor report runs without error."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["doctor", "report"])
        assert result.exit_code == 0
        assert "Report saved to" in result.output

    def test_report_help(self) -> None:
        """Rai doctor report --help works."""
        result = runner.invoke(app, ["doctor", "report", "--help"])
        assert result.exit_code == 0
        assert "diagnostic report" in result.output.lower()

    def test_doctor_help(self) -> None:
        """Rai doctor --help shows report subcommand."""
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "report" in result.output
