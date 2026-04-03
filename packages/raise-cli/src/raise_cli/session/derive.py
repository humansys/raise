"""Git-only StateDeriver — derives current work from git and scope.md.

Implements the StateDeriver protocol (ADR-038) using only git commands
and filesystem reads. Works in both normal repos and worktrees.

Architecture: E1248 (Git-First Session State)
"""

from __future__ import annotations

import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

from raise_cli.schemas.session_state import ActivityEntry, CurrentWork

logger = logging.getLogger(__name__)

# Patterns for branch parsing
_RELEASE_RE = re.compile(r"^release/(.+)$")
_STORY_RE = re.compile(r"^story/[sS](\d+\.\d+)/", re.IGNORECASE)

# Patterns for scope.md parsing
_STATUS_RE = re.compile(r">\s*\*\*Status:\*\*\s*(.+)", re.IGNORECASE)
_EPIC_DIR_RE = re.compile(r"^e(\d+)-")

# Patterns for git log parsing
_STORY_ID_RE = re.compile(r"[sS](\d+\.\d+)")
_EPIC_ID_RE = re.compile(r"[eE](\d+)")


class GitStateDeriver:
    """Derive current work context from git — the reliable source.

    Implements ``StateDeriver`` protocol. Git commands are instance methods
    to allow patching in tests.
    """

    def current_work(self, project: Path) -> CurrentWork:
        """Derive current work from branch, scope.md, and git log."""
        root = self._resolve_project_root(project)
        branch = self._git_current_branch(project)

        return CurrentWork(
            release=self._parse_release(branch),
            epic=self._find_active_epic(root),
            story=self._parse_story(branch),
            phase=self._infer_phase(project, branch),
            branch=branch,
        )

    def recent_activity(
        self, project: Path, limit: int = 10
    ) -> list[ActivityEntry]:
        """Parse recent git log into structured activity entries."""
        lines = self._git_log_lines(project, limit)
        entries: list[ActivityEntry] = []
        for line in lines:
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            commit_hash, subject, author, ts_str = parts
            try:
                timestamp = datetime.fromisoformat(ts_str.strip())
            except ValueError:
                continue

            story_match = _STORY_ID_RE.search(subject)
            epic_match = _EPIC_ID_RE.search(subject)

            entries.append(
                ActivityEntry(
                    commit_hash=commit_hash.strip(),
                    subject=subject.strip(),
                    author=author.strip(),
                    timestamp=timestamp,
                    story_id=f"S{story_match.group(1)}" if story_match else "",
                    epic_id=f"E{epic_match.group(1)}" if epic_match else "",
                )
            )
        return entries

    # ------------------------------------------------------------------
    # Branch parsing (static — no git calls needed)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_release(branch: str) -> str:
        """Extract release version from branch name.

        ``release/2.4.0`` → ``v2.4.0``, anything else → ``""``.
        """
        m = _RELEASE_RE.match(branch)
        return f"v{m.group(1)}" if m else ""

    @staticmethod
    def _parse_story(branch: str) -> str:
        """Extract story ID from branch name.

        ``story/s1248.1/foo`` → ``S1248.1``, anything else → ``""``.
        """
        m = _STORY_RE.match(branch)
        return f"S{m.group(1)}" if m else ""

    # ------------------------------------------------------------------
    # Scope.md parsing
    # ------------------------------------------------------------------

    def _find_active_epic(self, project_root: Path) -> str:
        """Find the first in-progress epic from scope.md frontmatter.

        Scans ``work/epics/e{N}-*/scope.md`` for ``Status: in-progress``.
        Returns epic ID (e.g., ``E1248``) or ``""``.
        """
        epics_dir = project_root / "work" / "epics"
        if not epics_dir.is_dir():
            return ""

        for epic_dir in sorted(epics_dir.iterdir()):
            if not epic_dir.is_dir():
                continue
            dir_match = _EPIC_DIR_RE.match(epic_dir.name)
            if not dir_match:
                continue

            scope_file = epic_dir / "scope.md"
            if not scope_file.exists():
                continue

            try:
                content = scope_file.read_text(encoding="utf-8")
            except OSError:
                continue

            for line in content.splitlines():
                status_match = _STATUS_RE.match(line)
                if status_match:
                    status = status_match.group(1).strip().lower()
                    if status == "in-progress":
                        return f"E{dir_match.group(1)}"
                    break  # Found status line but not in-progress

        return ""

    # ------------------------------------------------------------------
    # Phase inference
    # ------------------------------------------------------------------

    def _infer_phase(self, project: Path, branch: str) -> str:
        """Infer current work phase from recent git activity.

        Heuristics:
        - No recent commits on branch → ``planning``
        - Recent merge commit → ``reviewing``
        - Recent regular commits → ``implementing``
        """
        lines = self._git_log_lines(project, limit=5)

        if not lines:
            return "planning"

        # Check first (most recent) commit
        first = lines[0]
        subject = first.split("|", 2)[1] if "|" in first else first
        if subject.strip().startswith("Merge"):
            return "reviewing"

        return "implementing"

    # ------------------------------------------------------------------
    # Git commands (instance methods for testability)
    # ------------------------------------------------------------------

    def _git_current_branch(self, project: Path) -> str:
        """Run ``git branch --show-current``."""
        return self._run_git(project, ["branch", "--show-current"])

    def _git_common_dir(self, project: Path) -> str:
        """Run ``git rev-parse --git-common-dir``."""
        return self._run_git(project, ["rev-parse", "--git-common-dir"])

    def _git_log_lines(self, project: Path, limit: int = 5) -> list[str]:
        """Run ``git log`` and return formatted lines."""
        output = self._run_git(
            project,
            ["log", f"--max-count={limit}", "--format=%H|%s|%an|%aI"],
        )
        return [line for line in output.splitlines() if line.strip()]

    def _resolve_project_root(self, project: Path) -> Path:
        """Resolve the main project root, handling worktrees.

        In a worktree, ``git rev-parse --git-common-dir`` points to the
        main repo's ``.git/`` directory. We derive the project root from that.
        """
        try:
            common_dir = self._git_common_dir(project)
        except RuntimeError:
            return project

        common_path = Path(common_dir)
        if not common_path.is_absolute():
            common_path = (project / common_path).resolve()

        # .git/ → parent is project root
        # .git/worktrees/X → .git is 2 levels up, parent of .git is root
        if common_path.name == ".git":
            return common_path.parent
        return project

    @staticmethod
    def _run_git(project: Path, args: list[str]) -> str:
        """Run a git command and return stripped stdout.

        Raises RuntimeError on non-zero exit.
        """
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            raise RuntimeError(f"git {args[0]} failed: {exc}") from exc

        if result.returncode != 0:
            raise RuntimeError(
                f"git {args[0]} failed (exit {result.returncode}): {result.stderr.strip()}"
            )
        return result.stdout.strip()
