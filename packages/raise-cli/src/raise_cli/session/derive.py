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
_JIRA_STORY_RE = re.compile(r"^story/([A-Z]+-\d+)/", re.IGNORECASE)
_EPIC_PIPELINE_RE = re.compile(r"^epic/[A-Za-z]+-(\d+)/pipeline$")

# Patterns for scope.md parsing
_STATUS_RE = re.compile(r">\s*\*\*Status:\*\*\s*(.+)", re.IGNORECASE)
_FRONTMATTER_STATUS_RE = re.compile(r"^status:\s*(.+)", re.IGNORECASE)
_EPIC_DIR_RE = re.compile(r"^e(\d+)-")

# Patterns for git log parsing
_STORY_ID_RE = re.compile(r"[sS](\d+\.\d+)")
_EPIC_ID_RE = re.compile(r"[eE](\d+)")


def _parse_epic_status(content: str) -> str | None:
    """Extract status from scope.md content — YAML frontmatter or markdown blockquote.

    Detection order:
    1. If content starts with ``---``, parse the frontmatter block and look for ``status:``.
    2. Fallback: scan lines for the legacy markdown blockquote pattern ``> **Status:** …``.

    Returns the status value normalised to lowercase, or ``None`` if not found.
    """
    if content.startswith("---"):
        # Extract frontmatter block between the first pair of --- delimiters
        rest = content[3:]
        end = rest.find("\n---")
        if end != -1:
            frontmatter = rest[:end]
            for line in frontmatter.splitlines():
                m = _FRONTMATTER_STATUS_RE.match(line.strip())
                if m:
                    return m.group(1).strip().lower()
            return None  # Frontmatter present but no status key → don't fall through to body

    # Legacy markdown blockquote: > **Status:** in-progress
    for line in content.splitlines():
        m = _STATUS_RE.match(line)
        if m:
            return m.group(1).strip().lower()

    return None


def _find_epic_from_jira_key(epics_dir: Path, jira_key: str) -> str:
    """Find epic ID by looking up a Jira key in work/epics/*/stories/.

    Searches for ``{jira_key}*.md`` files inside each epic's stories/ subdir.
    Returns the epic ID (e.g. ``E17330``) or ``""`` if not found.
    """
    for epic_dir in sorted(epics_dir.iterdir()):
        if not epic_dir.is_dir():
            continue
        dir_match = _EPIC_DIR_RE.match(epic_dir.name)
        if not dir_match:
            continue
        stories_dir = epic_dir / "stories"
        if not stories_dir.is_dir():
            continue
        for f in stories_dir.iterdir():
            if f.name.startswith(jira_key) and f.suffix == ".md":
                return f"E{dir_match.group(1)}"
    return ""


class GitStateDeriver:
    """Derive current work context from git — the reliable source.

    Implements ``StateDeriver`` protocol. Git commands are instance methods
    to allow patching in tests.
    """

    def current_work(self, project: Path) -> CurrentWork:
        """Derive current work from branch, scope.md, and git log."""
        root = self._resolve_project_root(project)
        branch = self._git_current_branch(project)

        story_id = self._parse_story(branch)
        epic = (
            self._find_epic_from_story_scope(root, story_id)
            or self._parse_epic(branch)
            or self._parse_epic_pipeline(branch)
            or self._find_active_epic(root, project=project)
        )

        return CurrentWork(
            release=self._parse_release(branch),
            epic=epic,
            story=self._parse_story(branch),
            phase=self._infer_phase(project, branch),
            branch=branch,
        )

    def recent_activity(self, project: Path, limit: int = 10) -> list[ActivityEntry]:
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

    @staticmethod
    def _parse_epic(branch: str) -> str:
        """Extract epic ID from story branch name.

        ``story/s1248.1/foo`` → ``E1248``. Avoids scope.md scan that can
        leak other developers' in-progress epics (RAISE-2263).
        """
        m = _STORY_RE.match(branch)
        if m:
            epic_num = m.group(1).split(".")[0]
            return f"E{epic_num}"
        return ""

    @staticmethod
    def _parse_epic_pipeline(branch: str) -> str:
        """Extract epic ID from epic pipeline branch name.

        ``epic/RAISE-17330/pipeline`` → ``E17330``. Handles the epic pipeline
        branch pattern that ``_parse_epic`` misses (RAISE-17944).
        """
        m = _EPIC_PIPELINE_RE.match(branch)
        return f"E{m.group(1)}" if m else ""

    # ------------------------------------------------------------------
    # Scope.md parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _find_epic_from_story_scope(project_root: Path, story_id: str) -> str:
        """Find epic from story scope.md ``## Epic: E{N}`` header.

        Scans ``work/epics/e*/stories/{story_slug}-scope.md`` for the
        authoritative epic ID. Case-insensitive header match.

        Returns epic ID (e.g., ``E153``) or ``""``.
        """
        if not story_id:
            return ""

        epics_dir = project_root / "work" / "epics"
        if not epics_dir.is_dir():
            return ""

        story_slug = story_id.lower().lstrip("s")  # "S154.1" → "154.1"
        scope_filename = f"s{story_slug}-scope.md"

        for epic_dir in sorted(epics_dir.iterdir()):
            if not epic_dir.is_dir():
                continue
            scope_file = epic_dir / "stories" / scope_filename
            if not scope_file.exists():
                continue

            try:
                content = scope_file.read_text(encoding="utf-8")
            except OSError:
                continue

            for line in content.splitlines():
                stripped = line.strip()
                if stripped.lower().startswith("## epic:"):
                    epic_id = stripped.split(":", 1)[1].strip()
                    if epic_id:
                        return epic_id
            break  # Found the file but no epic header — stop scanning

        return ""

    def _find_active_epic(  # noqa: C901 — three-source chain with fail-open guards (RAISE-18076)
        self, project_root: Path, project: Path | None = None
    ) -> str:
        """Find the in-progress epic using a three-source resolution chain.

        Resolution order (RAISE-18076):
        1. ``RAISE_SESSION_JIRA_KEY`` from context.env — binding wins over alphabetical scan.
        2. Jira key parsed from the current branch name (``story/RAISE-XXXX/``).
        3. Alphabetical scan of ``work/epics/e{N}-*/scope.md`` — legacy fallback.

        Returns epic ID (e.g., ``E1248``) or ``""``.
        """
        import os

        epics_dir = project_root / "work" / "epics"
        if not epics_dir.is_dir():
            return ""

        # Source 1 & 2: require project path for context.env read and git branch
        if project is not None:
            # Source 1 — RAISE_SESSION_JIRA_KEY from context.env (explicit binding)
            session_id = os.environ.get("RAISE_AGENT_SESSION_ID") or os.environ.get(
                "RAISE_CC_SESSION_ID"
            )
            if session_id:
                try:
                    from raise_cli.session.context_env import read_context_env

                    jira_key = read_context_env(
                        project, session_id, "RAISE_SESSION_JIRA_KEY"
                    )
                    if jira_key:
                        epic_id = _find_epic_from_jira_key(epics_dir, jira_key)
                        if epic_id:
                            return epic_id
                except Exception:  # noqa: BLE001,S110 — fail-open (ADR-094)
                    pass

            # Source 2 — Jira key from branch name (story/RAISE-XXXX/slug)
            try:
                branch = self._git_current_branch(project)
                m = _JIRA_STORY_RE.match(branch)
                if m:
                    jira_key = m.group(1).upper()
                    epic_id = _find_epic_from_jira_key(epics_dir, jira_key)
                    if epic_id:
                        return epic_id
            except Exception:  # noqa: BLE001,S110 — fail-open (ADR-094)
                pass

        # Source 3 — alphabetical scan (legacy fallback, always runs)
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

            status = _parse_epic_status(content)
            if status == "in-progress":
                return f"E{dir_match.group(1)}"

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
        """Resolve the active checkout root, handling worktrees.

        Delegates to ``raise_cli.config.paths.resolve_checkout_root`` so that
        worktree-local versioned artifacts (e.g. ``work/epics/*/scope.md``)
        are read from the invoking worktree, not the main checkout. Kept as
        instance method for backward compatibility with tests that patch it
        on the deriver instance.
        """
        from raise_cli.config.paths import resolve_checkout_root

        return resolve_checkout_root(project)

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
