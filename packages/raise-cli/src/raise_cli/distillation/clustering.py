"""Cross-session pattern emergence clustering for proposed_patterns.

Reads journal_md from distillation_runs, extracts Insight bullet points,
and groups them by keyword overlap across sessions. When a keyword cluster
appears in ≥min_sessions distinct sessions, it is written to proposed_patterns.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass

# Stop words excluded from keyword matching
_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "was",
        "are",
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
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "it",
        "its",
        "we",
        "i",
        "you",
        "he",
        "she",
        "they",
        "them",
        "their",
        "our",
        "not",
        "no",
        "so",
        "if",
        "then",
        "when",
        "use",
        "used",
        "using",
        "make",
        "run",
        "all",
        "any",
    }
)

_INSIGHT_SECTION_RE = re.compile(r"## Insights\n+(.*?)(?=\n## |\Z)", re.DOTALL)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[turn \d+\]\s+)?(.+)$", re.MULTILINE)
_MIN_KEYWORD_LEN = 4


@dataclass
class ProposedPattern:
    """A cross-session pattern cluster ready for proposed_patterns insertion."""

    cluster_theme: str
    keywords: frozenset[str]
    session_ids: list[str]
    sample_keys: list[str]  # session_id list as sample evidence


def _tokenize(text: str) -> frozenset[str]:
    """Return meaningful keywords from text."""
    words = re.findall(r"[a-z_][a-z_0-9]*", text.lower())
    return frozenset(w for w in words if len(w) >= _MIN_KEYWORD_LEN and w not in _STOP)


def _extract_insights(journal_md: str) -> list[str]:
    """Return insight bullet texts from a journal's '## Insights' section."""
    m = _INSIGHT_SECTION_RE.search(journal_md)
    if not m:
        return []
    section = m.group(1)
    bullets = _BULLET_RE.findall(section)
    return [b.strip() for b in bullets if b.strip() and b.strip() != "_None detected._"]


def _cluster_insights(
    session_insights: dict[str, list[str]],
    min_sessions: int,
) -> list[ProposedPattern]:
    """Group insights by shared keywords; return clusters meeting min_sessions."""
    # keyword → {session_id: [insight texts]}
    keyword_sessions: dict[str, dict[str, list[str]]] = {}
    for session_id, insights in session_insights.items():
        for text in insights:
            for kw in _tokenize(text):
                keyword_sessions.setdefault(kw, {}).setdefault(session_id, []).append(
                    text
                )

    # Build clusters: keywords meeting min_sessions → pick representative text
    seen_themes: set[str] = set()
    clusters: list[ProposedPattern] = []
    for kw, by_session in keyword_sessions.items():
        if len(by_session) < min_sessions:
            continue
        # Representative theme = first text containing this keyword (shortest)
        all_texts = [t for texts in by_session.values() for t in texts]
        rep = min((t for t in all_texts if kw in _tokenize(t)), key=len, default=kw)
        if rep in seen_themes:
            continue
        seen_themes.add(rep)
        session_ids = sorted(by_session.keys())
        clusters.append(
            ProposedPattern(
                cluster_theme=rep,
                keywords=frozenset({kw}),
                session_ids=session_ids,
                sample_keys=session_ids[:5],
            )
        )
    return clusters


def propose_from_journals(
    conn: sqlite3.Connection,
    *,
    min_sessions: int = 2,
    lookback: int = 50,
) -> list[ProposedPattern]:
    """Read recent journals, cluster insights, write proposed_patterns.

    Idempotent: existing rows with status='pending' for the same cluster_theme
    are updated (correction_count + sample_keys); accepted/rejected rows are
    never overwritten.

    Returns the full list of clusters found (regardless of whether they were
    new or already existed).
    """
    rows = conn.execute(
        "SELECT session_id, journal_md FROM distillation_runs "
        "WHERE journal_md != '' ORDER BY date DESC, created_at DESC LIMIT ?",
        (lookback,),
    ).fetchall()

    session_insights: dict[str, list[str]] = {}
    for session_id, journal_md in rows:
        insights = _extract_insights(journal_md)
        if insights:
            session_insights[session_id] = insights

    clusters = _cluster_insights(session_insights, min_sessions)

    for cluster in clusters:
        existing = conn.execute(
            "SELECT id, status FROM proposed_patterns WHERE cluster_theme = ?",
            (cluster.cluster_theme,),
        ).fetchone()
        if existing is None:
            conn.execute(
                """
                INSERT INTO proposed_patterns
                    (cluster_theme, correction_count, sample_keys, status)
                VALUES (?, ?, ?, 'pending')
                """,
                (
                    cluster.cluster_theme,
                    len(cluster.session_ids),
                    json.dumps(cluster.sample_keys),
                ),
            )
        elif existing["status"] == "pending":
            conn.execute(
                """
                UPDATE proposed_patterns
                SET correction_count = ?, sample_keys = ?
                WHERE id = ?
                """,
                (
                    len(cluster.session_ids),
                    json.dumps(cluster.sample_keys),
                    existing["id"],
                ),
            )
        # accepted/rejected rows are left untouched

    conn.commit()
    return clusters
