"""SZZ introducer attribution — find the commit that introduced a bug.

Given a fix commit, runs git-blame over the lines it modified to identify
the introducing commit(s), resolves each introducer's authoring condition
via Claude-Session: trailer, and returns one IntroducerResult per distinct
introducer. Mirrors the cascade/result shape of attribution.py but uses
Pydantic BaseModel (not dataclass) and float confidence.

Usage:
    from pathlib import Path
    from raise_cli.telemetry.szz import SzzAttributor

    results = SzzAttributor().attribute_introducer(
        fix_commit="abc1234", repo_path=Path(".")
    )
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BASE_CONF: float = 0.5
_REAL_CODE_BONUS: float = 0.3
_CONCENTRATION_BONUS: float = 0.1
_REFACTOR_PENALTY: float = 0.4
_SPREAD_PENALTY: float = 0.1
_TRAILER_BONUS: float = 0.1

_REFACTOR_RE = re.compile(
    r"(?i)\b(refactor|rename|move|format|lint|reformat|whitespace|style)\b"
)
_BUG_KEY_RE = re.compile(r"(?:fix(?:\([^)]*\))?:?\s*)?([A-Z]+-\d+)")
_TRAILER_RE = re.compile(r"^Claude-Session:\s+(.+)$", re.MULTILINE)

_DEFAULT_EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".raise/",
    "*.lock",
    "*-index.json",
    ".env.*",
    "embedding_index.json",
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def confidence_band(confidence: float) -> str:
    """Map a confidence score to a human-readable band.

    Returns:
        "high" if confidence >= 0.8
        "medium" if confidence >= 0.5
        "low" if confidence < 0.5
    """
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class IntroducerResult(BaseModel):
    """Result of SZZ introducer attribution for one fix commit.

    One instance per distinct introducer commit found via git-blame.
    confidence is a float in [0.0, 1.0]; values < 0.5 are low-confidence
    and flagged "low confidence" in evidence.
    """

    bug_key: str
    """Jira/tracker key parsed from fix commit subject, or empty string."""

    fix_commit: str
    """The fix commit SHA that was analysed."""

    introducer_commit: str
    """The introducing commit SHA identified by git-blame."""

    introducer_author: str
    """Author email of the introducer commit."""

    introducer_session_id: str | None
    """Claude-Session URL from introducer commit trailer, or None."""

    authoring_condition: str
    """'ai_session_unresolved' when trailer present; 'human_or_pre_trailer' otherwise."""

    confidence: float = Field(ge=0.0, le=1.0)
    """Confidence score in [0.0, 1.0]."""

    evidence: list[str]
    """Human-readable evidence strings explaining the attribution."""


# ---------------------------------------------------------------------------
# Internal git helper
# ---------------------------------------------------------------------------


def _run_git(args: list[str], repo_path: Path) -> str:
    """Run a git command and return stripped stdout.

    Raises subprocess.CalledProcessError on non-zero exit.
    Raises FileNotFoundError if git is not on PATH.
    """
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=str(repo_path),
        timeout=30,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, ["git", *args], result.stdout, result.stderr
        )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# SzzAttributor
# ---------------------------------------------------------------------------


class SzzAttributor:
    """Attribute a fix commit's introducer commits via git-blame.

    Uses subprocess git exclusively (no GitPython). No external dependencies
    beyond the standard library and pydantic.
    """

    def __init__(self, exclude_patterns: list[str] | None = None) -> None:
        """Initialise attributor with optional file-exclusion patterns.

        Args:
            exclude_patterns: Glob patterns (basename, full path, or dir prefix
                ending with '/') for files to skip before running git blame.
                Pass ``None`` to use ``_DEFAULT_EXCLUDE_PATTERNS``.
                Pass ``[]`` to disable all skipping (raw-blame escape hatch).
        """
        self._exclude_patterns: tuple[str, ...] = (
            tuple(exclude_patterns)
            if exclude_patterns is not None
            else _DEFAULT_EXCLUDE_PATTERNS
        )

    def _should_skip_file(self, path: str) -> bool:
        """Return True if *path* matches any exclusion pattern.

        Matching rules (in order, first match wins):
        1. Directory-prefix check: patterns ending with '/' are tested via
           ``path.startswith(pat)`` so ``.raise/`` matches any path beneath it.
        2. Full-path fnmatch: ``fnmatch.fnmatch(path, pat)``.
        3. Basename fnmatch: ``fnmatch.fnmatch(os.path.basename(path), pat)``.
        """
        for pat in self._exclude_patterns:
            if pat.endswith("/"):
                if path.startswith(pat):
                    return True
            elif fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(
                os.path.basename(path), pat
            ):
                return True
        return False

    def attribute_introducer(
        self, fix_commit: str, repo_path: Path
    ) -> list[IntroducerResult]:
        """Return one IntroducerResult per distinct introducing commit.

        Args:
            fix_commit: SHA of the fix commit to analyse.
            repo_path: Path to the git repository root.

        Returns:
            List of IntroducerResult (one per distinct introducer). Empty list
            if the fix only adds new files (net-new code).

        Raises:
            ValueError: If fix_commit is not found in the repository.
            subprocess.CalledProcessError: On unexpected git failures.
        """
        self._verify_commit(fix_commit, repo_path)

        # R1: compute diff once, reuse for both modified-lines and real-code check
        diff_output = self._get_fix_diff(fix_commit, repo_path)
        modified = _parse_diff_deleted_ranges(diff_output)
        if not modified:
            return []

        introducer_evidence = self._collect_introducer_evidence(
            modified, fix_commit, repo_path
        )
        if not introducer_evidence:
            return []

        bug_key = self._parse_bug_key(fix_commit, repo_path)
        fix_is_real_code = _is_real_code_in_diff(diff_output)
        total_introducers = len(introducer_evidence)

        return [
            self._build_result(
                introducer_hash=h,
                raw_evidence=ev,
                fix_commit=fix_commit,
                bug_key=bug_key,
                fix_is_real_code=fix_is_real_code,
                total_introducers=total_introducers,
                repo_path=repo_path,
            )
            for h, ev in introducer_evidence.items()
        ]

    def _collect_introducer_evidence(
        self,
        modified: dict[str, list[tuple[int, int]]],
        fix_commit: str,
        repo_path: Path,
    ) -> dict[str, list[str]]:
        """Run git blame over all modified ranges and group evidence by introducer hash."""
        introducer_lines: dict[str, list[str]] = {}

        for file_path, line_ranges in modified.items():
            if self._should_skip_file(file_path):
                continue
            for start, end in line_ranges:
                blame_commits = self._blame_lines(
                    file_path, start, end, fix_commit, repo_path
                )
                for commit_hash in blame_commits:
                    if commit_hash not in introducer_lines:
                        introducer_lines[commit_hash] = []
                    evidence_line = (
                        f"git blame -w -M -C {file_path} L{start}-{end}"
                        f" → {commit_hash[:7]}"
                    )
                    if evidence_line not in introducer_lines[commit_hash]:
                        introducer_lines[commit_hash].append(evidence_line)

        return introducer_lines

    def _build_result(
        self,
        *,
        introducer_hash: str,
        raw_evidence: list[str],
        fix_commit: str,
        bug_key: str,
        fix_is_real_code: bool,
        total_introducers: int,
        repo_path: Path,
    ) -> IntroducerResult:
        """Build one IntroducerResult for an introducer commit."""
        author = self._get_author(introducer_hash, repo_path)
        session_id, authoring_condition = self._resolve_trailer(
            introducer_hash, repo_path
        )
        has_trailer = session_id is not None
        blame_count = len(raw_evidence)

        # R2: resolve subject once, pass to both confidence and evidence
        intro_subject = self._get_subject(introducer_hash, repo_path)

        confidence = self._compute_confidence(
            intro_subject=intro_subject,
            fix_is_real_code=fix_is_real_code,
            blame_count=blame_count,
            total_introducers=total_introducers,
            has_trailer=has_trailer,
        )

        full_evidence = list(raw_evidence)
        if intro_subject:
            penalty_note = (
                " (refactor penalty applied)"
                if _REFACTOR_RE.search(intro_subject)
                else " (no refactor penalty)"
            )
            full_evidence.append(f"introducer subject '{intro_subject}'{penalty_note}")
        if has_trailer:
            full_evidence.append("Claude-Session trailer resolved")
        if confidence < _BASE_CONF:
            full_evidence.append("low confidence")
        band = confidence_band(confidence)
        full_evidence.append(f"confidence band: {band} ({confidence:.2f})")

        return IntroducerResult(
            bug_key=bug_key,
            fix_commit=fix_commit,
            introducer_commit=introducer_hash,
            introducer_author=author,
            introducer_session_id=session_id,
            authoring_condition=authoring_condition,
            confidence=confidence,
            evidence=full_evidence,
        )

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _verify_commit(self, commit_hash: str, repo_path: Path) -> None:
        """Raise ValueError if commit_hash is not in the repository."""
        try:
            _run_git(["rev-parse", "--verify", f"{commit_hash}^{{commit}}"], repo_path)
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"fix commit '{commit_hash}' not found in repo") from exc

    def _get_fix_diff(self, fix_commit: str, repo_path: Path) -> str:
        """Return the unified diff (--unified=0) for a fix commit.

        R1: single diff subprocess, reused for both modified-line parsing
        and real-code-change detection.
        """
        try:
            return _run_git(
                ["diff", f"{fix_commit}^..{fix_commit}", "--unified=0"],
                repo_path,
            )
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"fix commit '{fix_commit}' not found in repo") from exc

    def _blame_lines(
        self,
        file_path: str,
        start: int,
        end: int,
        fix_commit: str,
        repo_path: Path,
    ) -> list[str]:
        """Run git blame on a line range at fix_commit^ and return unique commit hashes.

        PAT-E-1298: catches only ValueError/subprocess.SubprocessError on parse,
        lets CalledProcessError propagate.
        """
        parent = f"{fix_commit}^"
        try:
            output = _run_git(
                [
                    "blame",
                    "-w",
                    "-M",
                    "-C",
                    "--porcelain",
                    f"-L{start},{end}",
                    parent,
                    "--",
                    file_path,
                ],
                repo_path,
            )
        except subprocess.CalledProcessError:
            # File may not exist at parent (new file introduced in fix) — not an error
            return []

        hashes: list[str] = []
        seen: set[str] = set()
        for line in output.splitlines():
            # Porcelain format: lines starting with 40-char hex are commit hashes
            if len(line) >= 40 and re.match(r"^[0-9a-f]{40}", line):
                h = line[:40]
                if h not in seen:
                    seen.add(h)
                    hashes.append(h)
        return hashes

    def _compute_confidence(
        self,
        *,
        intro_subject: str,
        fix_is_real_code: bool,
        blame_count: int,
        total_introducers: int,
        has_trailer: bool,
    ) -> float:
        """Compute confidence score for an introducer attribution.

        Heuristic (D3, plan T3):
          base 0.5
          + 0.3 if fix is a real code change (non-whitespace/comment)
          + 0.1 if this introducer has a single hunk (blame concentration)
          - 0.4 if introducer subject matches refactor/rename/move/format regex
          - 0.1 per additional introducer beyond first (spread penalty)
          + 0.1 if Claude-Session trailer present (linkage corroboration)
          clamped to [0.0, 1.0]

        R2: intro_subject is resolved once in _build_result, not here.
        """
        score = _BASE_CONF

        if fix_is_real_code:
            score += _REAL_CODE_BONUS

        is_refactor = bool(intro_subject and _REFACTOR_RE.search(intro_subject))

        # Concentration bonus: single hunk, but not when refactor penalty fires
        # (contradictory signals — refactor penalty dominates)
        if blame_count == 1 and not is_refactor:
            score += _CONCENTRATION_BONUS

        if is_refactor:
            score -= _REFACTOR_PENALTY

        # Spread penalty: -0.1 for each introducer beyond the first
        spread = max(0, total_introducers - 1)
        score -= _SPREAD_PENALTY * spread

        if has_trailer:
            score += _TRAILER_BONUS

        return max(0.0, min(1.0, score))

    def resolve_trailer(
        self, commit_hash: str, repo_path: Path
    ) -> tuple[str | None, str]:
        """Extract Claude-Session: trailer from a commit message.

        Public API — promoted from _resolve_trailer in S11899.2 (T3) to allow
        RegionAttributor (Carril B) to resolve authoring condition per blame SHA.

        Returns:
            (session_url, "ai_session_unresolved") when found.
            (None, "human_or_pre_trailer") when absent.
        """
        try:
            body = _run_git(["log", "-1", "--format=%B", commit_hash], repo_path)
        except subprocess.CalledProcessError:
            return None, "human_or_pre_trailer"

        m = _TRAILER_RE.search(body)
        if m:
            return m.group(1).strip(), "ai_session_unresolved"
        return None, "human_or_pre_trailer"

    # Alias for backward compatibility (internal callers used _resolve_trailer)
    _resolve_trailer = resolve_trailer

    def _parse_bug_key(self, fix_commit: str, repo_path: Path) -> str:
        """Parse Jira-style bug key from fix commit subject (e.g. 'fix(RAISE-1234)')."""
        try:
            subject = _run_git(["log", "-1", "--format=%s", fix_commit], repo_path)
        except subprocess.CalledProcessError:
            return ""
        m = _BUG_KEY_RE.search(subject)
        return m.group(1) if m else ""

    def _get_subject(self, commit_hash: str, repo_path: Path) -> str:
        """Return the one-line subject of a commit."""
        try:
            return _run_git(["log", "-1", "--format=%s", commit_hash], repo_path)
        except subprocess.CalledProcessError:
            return ""

    def _get_author(self, commit_hash: str, repo_path: Path) -> str:
        """Return the author email of a commit."""
        try:
            return _run_git(["log", "-1", "--format=%ae", commit_hash], repo_path)
        except subprocess.CalledProcessError:
            return ""


# ---------------------------------------------------------------------------
# Diff parser
# ---------------------------------------------------------------------------


def _is_real_code_in_diff(diff_output: str) -> bool:
    """Return True if the diff contains non-whitespace, non-comment-only deleted lines.

    R1: operates on already-fetched diff output (no subprocess).
    """
    for line in diff_output.splitlines():
        if not line.startswith("-") or line.startswith("---"):
            continue
        stripped = line[1:].strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        return True
    return False


def _parse_diff_deleted_ranges(diff_output: str) -> dict[str, list[tuple[int, int]]]:
    """Parse unified diff output to extract deleted/changed line ranges per file.

    Returns {file_path: [(start, end), ...]} for the *pre-fix* (left/minus) side.
    Only files with actual deleted lines are included; pure additions are excluded.
    """
    result: dict[str, list[tuple[int, int]]] = {}
    current_file: str | None = None

    # Match hunk headers: @@ -start[,count] +start[,count] @@
    hunk_re = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")
    # Match file headers: --- a/path
    file_re = re.compile(r"^--- a/(.+)$")

    for line in diff_output.splitlines():
        fm = file_re.match(line)
        if fm:
            current_file = fm.group(1)
            continue

        hm = hunk_re.match(line)
        if hm and current_file:
            start = int(hm.group(1))
            count = int(hm.group(2)) if hm.group(2) is not None else 1
            if count == 0:
                # Pure addition hunk (--- side has 0 lines) — skip
                continue
            end = start + count - 1
            if current_file not in result:
                result[current_file] = []
            result[current_file].append((start, end))

    return result
