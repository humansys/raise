"""Local WorkstreamMonitor — session analysis from git heuristics.

Implements the WorkstreamMonitor protocol (ADR-038) using git log
to derive commit velocity, TDD compliance, and revert detection.

Architecture: E1248 (Git-First Session State), S1248.4
"""

from __future__ import annotations

import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

from raise_cli.schemas.session_state import Improvement, SessionInsights

logger = logging.getLogger(__name__)

_TEST_SUBJECT_RE = re.compile(r"^test[\s(:]", re.IGNORECASE)
_REVERT_SUBJECT_RE = re.compile(r"^Revert\s", re.IGNORECASE)


class LocalWorkstreamMonitor:
    """Git-based session analysis — the community (2.4) backend.

    Implements ``WorkstreamMonitor`` protocol. Analyzes git log for
    commit patterns and suggests improvements.

    Args:
        project: Project root path. Used for git commands.
    """

    def __init__(self, project: Path) -> None:
        self._project = project

    def analyze_session(self, session_id: str) -> SessionInsights:
        """Analyze a session by parsing git log entries.

        Returns commit count, test commit ratio, revert count, and
        duration in minutes.
        """
        lines = self._git_log_for_session(session_id)

        if not lines:
            return SessionInsights(
                session_id=session_id,
                commit_count=0,
                test_commit_ratio=0.0,
                revert_count=0,
                duration_minutes=0,
            )

        test_count = 0
        revert_count = 0
        timestamps: list[datetime] = []

        for line in lines:
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue

            subject = parts[1].strip()

            if _TEST_SUBJECT_RE.match(subject):
                test_count += 1
            if _REVERT_SUBJECT_RE.match(subject):
                revert_count += 1

            try:
                timestamps.append(datetime.fromisoformat(parts[3].strip()))
            except ValueError:
                continue

        commit_count = len(lines)
        test_ratio = test_count / commit_count if commit_count > 0 else 0.0

        # Duration: difference between first and last commit
        duration = 0
        if len(timestamps) >= 2:
            sorted_ts = sorted(timestamps)
            duration = int((sorted_ts[-1] - sorted_ts[0]).total_seconds() / 60)

        return SessionInsights(
            session_id=session_id,
            commit_count=commit_count,
            test_commit_ratio=test_ratio,
            revert_count=revert_count,
            duration_minutes=duration,
        )

    def suggest_improvements(self, last_n: int = 5) -> list[Improvement]:
        """Suggest improvements based on recent session analysis.

        Simple heuristics:
        - Low test commit ratio (<30%) → suggest more TDD
        - High revert count (>2) → suggest smaller commits
        """
        lines = self._git_log_for_session("last")
        if not lines:
            return []

        # Analyze the available commits
        test_count = sum(
            1 for line in lines
            if len(line.split("|", 2)) >= 2
            and _TEST_SUBJECT_RE.match(line.split("|", 2)[1].strip())
        )
        revert_count = sum(
            1 for line in lines
            if len(line.split("|", 2)) >= 2
            and _REVERT_SUBJECT_RE.match(line.split("|", 2)[1].strip())
        )

        improvements: list[Improvement] = []
        commit_count = len(lines)

        if commit_count > 0 and (test_count / commit_count) < 0.3:
            improvements.append(
                Improvement(
                    category="tdd",
                    description=f"Test commit ratio is {test_count}/{commit_count} ({test_count/commit_count:.0%})",
                    suggestion="Consider writing test commits before implementation commits (RED-GREEN-REFACTOR)",
                )
            )

        if revert_count > 2:
            improvements.append(
                Improvement(
                    category="commit-size",
                    description=f"{revert_count} reverts detected in recent commits",
                    suggestion="Consider smaller, more focused commits to reduce revert frequency",
                )
            )

        return improvements

    def _git_log_for_session(
        self, session_id: str, limit: int = 50
    ) -> list[str]:
        """Get git log lines for analysis.

        For now, returns recent commits. Future: filter by session
        time range using session registry.
        """
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--format=%H|%s|%an|%aI"],
                cwd=self._project,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        if result.returncode != 0:
            return []

        return [line for line in result.stdout.strip().splitlines() if line.strip()]
