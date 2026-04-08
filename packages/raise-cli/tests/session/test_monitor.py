"""Tests for LocalWorkstreamMonitor — session analysis from git heuristics."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from raise_cli.schemas.session_state import Improvement
from raise_cli.session.monitor import LocalWorkstreamMonitor
from raise_cli.session.protocols import WorkstreamMonitor


class TestProtocolCompliance:
    def test_satisfies_protocol(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        assert isinstance(monitor, WorkstreamMonitor)


class TestAnalyzeSession:
    """analyze_session returns correct SessionInsights from git log."""

    def test_counts_commits(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "abc1|feat(S1.1): add feature|Emilio|2026-04-03T10:00:00+00:00",
            "abc2|test(S1.1): add tests|Emilio|2026-04-03T10:30:00+00:00",
            "abc3|fix(S1.1): fix bug|Emilio|2026-04-03T11:00:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            insights = monitor.analyze_session("S-E-260403-1000")

        assert insights.commit_count == 3
        assert insights.session_id == "S-E-260403-1000"

    def test_detects_test_commits(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "a|feat: code|Dev|2026-04-03T10:00:00+00:00",
            "b|test: tests|Dev|2026-04-03T10:15:00+00:00",
            "c|test(S1): more tests|Dev|2026-04-03T10:30:00+00:00",
            "d|fix: fix|Dev|2026-04-03T10:45:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            insights = monitor.analyze_session("S-E-260403-1000")

        assert insights.test_commit_ratio == 0.5  # 2 test commits / 4 total

    def test_detects_reverts(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "a|feat: add|Dev|2026-04-03T10:00:00+00:00",
            'b|Revert "feat: add"|Dev|2026-04-03T10:15:00+00:00',
            "c|fix: redo|Dev|2026-04-03T10:30:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            insights = monitor.analyze_session("S-E-260403-1000")

        assert insights.revert_count == 1

    def test_calculates_duration(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "a|feat: first|Dev|2026-04-03T10:00:00+00:00",
            "b|feat: last|Dev|2026-04-03T12:00:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            insights = monitor.analyze_session("S-E-260403-1000")

        assert insights.duration_minutes == 120

    def test_empty_log_returns_zero_insights(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        with patch.object(monitor, "_git_log_for_session", return_value=[]):
            insights = monitor.analyze_session("S-E-260403-1000")

        assert insights.commit_count == 0
        assert insights.test_commit_ratio == 0.0
        assert insights.duration_minutes == 0


class TestSuggestImprovements:
    """suggest_improvements returns heuristics-based suggestions."""

    def test_suggests_more_tests_when_low_ratio(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "a|feat: code|Dev|2026-04-03T10:00:00+00:00",
            "b|feat: more code|Dev|2026-04-03T10:30:00+00:00",
            "c|feat: even more|Dev|2026-04-03T11:00:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            improvements = monitor.suggest_improvements(last_n=1)

        assert any(imp.category == "tdd" for imp in improvements)

    def test_no_suggestions_when_healthy(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        log_lines = [
            "a|test: red|Dev|2026-04-03T10:00:00+00:00",
            "b|feat: green|Dev|2026-04-03T10:15:00+00:00",
            "c|test: more red|Dev|2026-04-03T10:30:00+00:00",
            "d|feat: more green|Dev|2026-04-03T10:45:00+00:00",
        ]
        with patch.object(monitor, "_git_log_for_session", return_value=log_lines):
            improvements = monitor.suggest_improvements(last_n=1)

        # 50% test ratio is healthy — no tdd suggestion
        assert not any(imp.category == "tdd" for imp in improvements)

    def test_returns_list_of_improvement(self, tmp_path: Path) -> None:
        monitor = LocalWorkstreamMonitor(project=tmp_path)
        with patch.object(monitor, "_git_log_for_session", return_value=[]):
            improvements = monitor.suggest_improvements(last_n=1)

        assert isinstance(improvements, list)
        for imp in improvements:
            assert isinstance(imp, Improvement)
