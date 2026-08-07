"""Deterministic pattern evaluator for session-close auto-reinforcement.

Compares patterns returned during a session (logged in session_pattern_queries)
against the git diff of the session, using keyword and file overlap heuristics.
"""

from __future__ import annotations

import contextlib
import json
import logging
import re
import sqlite3
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "can",
        "could",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "and",
        "but",
        "or",
        "nor",
        "not",
        "so",
        "yet",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "only",
        "own",
        "same",
        "than",
        "too",
        "very",
        "just",
        "if",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "all",
        "any",
        "every",
        "when",
        "how",
        "what",
        "which",
        "who",
        "whom",
        "where",
        "why",
        "use",
        "using",
    }
)

OVERLAP_THRESHOLD = 0.1
FILE_OVERLAP_BONUS = 0.1


class EvalResult(BaseModel):
    """Result of evaluating a single pattern against the session diff."""

    pattern_id: str
    vote: int = Field(..., ge=-1, le=1)
    score: float = Field(..., ge=0.0)
    reason: str = ""


def _tokenize(text: str) -> set[str]:
    """Split text into lowercase tokens, filtering stop words and short tokens."""
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 2}


def _get_session_diff(project_path: Path) -> str:
    """Get the git diff for the current session (uncommitted + recent commits)."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~5..HEAD", "--no-binary", "--unified=0"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Failed to get git diff", exc_info=True)
        return ""


def _get_changed_files(diff_text: str) -> set[str]:
    """Extract changed file paths from a unified diff."""
    files: set[str] = set()
    for line in diff_text.splitlines():
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            path = line[6:]
            if path and path != "/dev/null":
                files.add(path)
                parts = path.split("/")
                files.update(parts)
    return files


def evaluate_session(
    conn: sqlite3.Connection,
    session_id: str,
    project_path: Path,
    *,
    project_id: str = "",
) -> list[EvalResult]:
    """Evaluate patterns returned during a session against its git diff.

    Returns a list of EvalResult with vote +1 (influenced) or -1 (not used).
    """
    rows = conn.execute(
        "SELECT spq.pattern_id, p.content, p.context_json "
        "FROM session_pattern_queries spq "
        "JOIN patterns p ON spq.pattern_id = p.pattern_id AND spq.project_id = p.project_id "
        "WHERE spq.session_id = ? AND spq.project_id = ?",
        (session_id, project_id),
    ).fetchall()

    if not rows:
        return []

    diff_text = _get_session_diff(project_path)
    diff_tokens = _tokenize(diff_text)
    changed_files = _get_changed_files(diff_text)

    results: list[EvalResult] = []
    for pattern_id, content, context_json in rows:
        pattern_tokens = _tokenize(content)
        if not pattern_tokens:
            results.append(
                EvalResult(
                    pattern_id=pattern_id,
                    vote=-1,
                    score=0.0,
                    reason="empty pattern tokens",
                )
            )
            continue

        overlap = pattern_tokens & diff_tokens
        keyword_score = len(overlap) / len(pattern_tokens)

        context_tags: list[str] = []
        with contextlib.suppress(json.JSONDecodeError, TypeError):
            context_tags = json.loads(context_json) if context_json else []

        file_bonus = sum(
            FILE_OVERLAP_BONUS
            for tag in context_tags
            if tag.lower() in {f.lower() for f in changed_files}
        )

        total_score = keyword_score + file_bonus
        vote = 1 if total_score >= OVERLAP_THRESHOLD else -1

        overlap_desc = ", ".join(sorted(overlap)[:5]) if overlap else "none"
        reason = f"keyword overlap: {overlap_desc}" if overlap else "no overlap"
        if file_bonus > 0:
            reason += " + file match"

        results.append(
            EvalResult(
                pattern_id=pattern_id,
                vote=vote,
                score=round(total_score, 3),
                reason=reason,
            )
        )

    return results
