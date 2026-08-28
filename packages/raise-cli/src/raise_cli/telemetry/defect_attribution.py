"""Defect attribution — join introducer commit to authoring condition + persist.

Given an IntroducerResult from szz.py, resolves the final authoring_condition
by looking up the Claude-Session UUID in CC JSONL logs (~/.claude/projects/).
Persists AttributionRecords to the introducer_attributions SQLite table.

Design decisions in effect:
- D1: New module (SRP) — consumes IntroducerResult, does not extend szz.py
- D2: Persist to canonical raise.db via storage/connection.py (S11899.6)
- D3: 4-value taxonomy: interactive | batch_agent | human | unknown
- D4: Historical session lookup via CC JSONL log archives
- D5: Pydantic BaseModel for AttributionRecord
- D6: batch_agent detection heuristic via --dangerously-skip-permissions etc.

Usage:
    from pathlib import Path
    from raise_cli.telemetry.szz import SzzAttributor
    from raise_cli.telemetry.defect_attribution import (
        resolve_authoring_condition,
        persist_attribution,
        get_attribution_dataset,
    )

    results = SzzAttributor().attribute_introducer('abc1234', Path('.'))
    records = [resolve_authoring_condition(r, repo_path=Path('.')) for r in results]
    persist_attribution(records, project_root=Path('.'))
    dataset = get_attribution_dataset(project_root=Path('.'))
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from raise_cli.storage.connection import get_project_db, get_project_id

if TYPE_CHECKING:
    from raise_cli.telemetry.szz import IntroducerResult

# ---------------------------------------------------------------------------
# Batch-agent detection markers (D6)
# ---------------------------------------------------------------------------

_BATCH_MARKERS = (
    "--dangerously-skip-permissions",
    "--print",
    "RAISE_AGENT_RUNTIME",  # historical logs (pre-RAISE-15790)
    "RAISE_AGENT_COMMAND",  # post-RAISE-15790: cockpit launch command var
)


# ---------------------------------------------------------------------------
# Data model (D5)
# ---------------------------------------------------------------------------


class AttributionRecord(BaseModel):
    """Final defect attribution record.

    Represents the resolved authoring_condition for one bug introducer commit.
    """

    bug_key: str
    """Jira/tracker key parsed from the fix commit, or empty string."""

    fix_commit: str
    """SHA of the fix commit that was analysed by SZZ."""

    introducer_commit: str
    """SHA of the introducer commit identified by SZZ git-blame."""

    introducer_author: str
    """Author email of the introducer commit."""

    introducer_session_id: str | None
    """Claude-Session UUID from introducer commit trailer, or None."""

    authoring_condition: Literal[
        "interactive", "batch_agent", "human", "ai_unknown", "unknown"
    ]
    """Resolved authoring condition.

    'ai_unknown': código IA con condición irrecuperable (sin trailer =
    pre-instrumentación en repo 100%-IA). 'human' se conserva pero NUNCA se
    enruta sin evidencia POSITIVA de autoría humana (RAISE-11898 — antes se
    colapsaba 'human_or_pre_trailer' → 'human', un error de categoría que
    inventaba una población humana inexistente en raise-commons)."""

    resolution_reason: str
    """Human-readable explanation of how authoring_condition was resolved."""

    confidence: float = Field(ge=0.0, le=1.0)
    """Confidence score in [0.0, 1.0] — carried over from SZZ IntroducerResult."""

    resolved_at: datetime
    """When this attribution was resolved."""


# ---------------------------------------------------------------------------
# Session lookup (D4)
# ---------------------------------------------------------------------------


def _default_claude_projects_dir() -> Path:
    """Return the default CC projects directory (~/.claude/projects)."""
    return Path.home() / ".claude" / "projects"


def _find_session_jsonl(
    session_id: str,
    claude_projects_dir: Path,
) -> Path | None:
    """Search for a JSONL file containing the given session_id.

    Strategy:
    1. Look for a file whose name (stem) matches the session_id exactly.
    2. Scan file content for '"sessionId": "<session_id>"' substring.

    Returns the first matching Path, or None if not found.
    Edge cases: session archive purged (>30d) → returns None.
    """
    if not claude_projects_dir.exists():
        return None

    # Fast path: filename match (CC names files after session UUID)
    for jsonl in claude_projects_dir.rglob("*.jsonl"):
        if jsonl.stem == session_id:
            return jsonl

    # Slow path: content search
    needle = f'"sessionId": "{session_id}"'
    for jsonl in claude_projects_dir.rglob("*.jsonl"):
        try:
            text = jsonl.read_text(encoding="utf-8", errors="replace")
            if needle in text:
                return jsonl
        except OSError:
            continue

    return None


def _is_batch_agent_session(jsonl_path: Path) -> bool:
    """Return True if the JSONL session contains batch/agent execution markers.

    Heuristic (D6): checks for --dangerously-skip-permissions, --print, or
    RAISE_AGENT_RUNTIME in any line of the conversation log. Proportional
    precision for S-sized story; refine in follow-up if too coarse.

    Edge cases: multi-author commits, merge commits → not addressed here
    (those surface at SZZ layer, not here). Cherry-picks: same session_id
    resolution applies.
    """
    try:
        text = jsonl_path.read_text(encoding="utf-8", errors="replace")
        for marker in _BATCH_MARKERS:
            if marker in text:
                return True
    except OSError:
        pass
    return False


# ---------------------------------------------------------------------------
# Core resolution function
# ---------------------------------------------------------------------------


def resolve_authoring_condition(
    introducer_result: IntroducerResult,
    *,
    repo_path: Path,  # noqa: ARG001 — reserved for future commit-date lookup
    claude_projects_dir: Path | None = None,
) -> AttributionRecord:
    """Resolve the final authoring_condition for an IntroducerResult.

    Resolution paths:
    - (a) No trailer (human_or_pre_trailer) → 'ai_unknown',
      reason='no_trailer_pre_instrumentation' (repo 100%-IA: sin trailer =
      código IA pre-instrumentación, NO humano — RAISE-11898)
    - (b) Trailer present + JSONL found + no batch markers → 'interactive'
    - (c) Trailer present + JSONL found + batch markers → 'batch_agent'
    - (d) Trailer present + JSONL not found → 'unknown', reason contains 'irrecoverable'

    Args:
        introducer_result: Output from SzzAttributor.attribute_introducer().
        repo_path: Path to the git repository root (reserved for future use).
        claude_projects_dir: Override the CC projects directory (default: ~/.claude/projects).
            Used in tests to inject a fake directory.

    Returns:
        AttributionRecord with resolved authoring_condition.
    """
    projects_dir = claude_projects_dir or _default_claude_projects_dir()
    now = datetime.now(tz=UTC)

    # Path (a): No Claude-Session trailer → ai_unknown (IA pre-instrumentación).
    # RAISE-11898: raise-commons es 100%-IA; la ausencia de trailer NO implica
    # autoría humana. Antes se colapsaba a 'human' (error de categoría que
    # produjo el falso "82% human" del estudio).
    if (
        introducer_result.authoring_condition == "human_or_pre_trailer"
        or introducer_result.introducer_session_id is None
    ):
        return AttributionRecord(
            bug_key=introducer_result.bug_key,
            fix_commit=introducer_result.fix_commit,
            introducer_commit=introducer_result.introducer_commit,
            introducer_author=introducer_result.introducer_author,
            introducer_session_id=None,
            authoring_condition="ai_unknown",
            resolution_reason="no_trailer_pre_instrumentation",
            confidence=introducer_result.confidence,
            resolved_at=now,
        )

    session_id = introducer_result.introducer_session_id

    # Path (b)/(c)/(d): Trailer present — look up JSONL
    jsonl_path = _find_session_jsonl(session_id, projects_dir)

    if jsonl_path is None:
        # Path (d): Session log missing (archived or purged)
        return AttributionRecord(
            bug_key=introducer_result.bug_key,
            fix_commit=introducer_result.fix_commit,
            introducer_commit=introducer_result.introducer_commit,
            introducer_author=introducer_result.introducer_author,
            introducer_session_id=session_id,
            authoring_condition="unknown",
            resolution_reason="session_archived_irrecoverable",
            confidence=introducer_result.confidence,
            resolved_at=now,
        )

    # JSONL found — determine interactive vs batch_agent
    if _is_batch_agent_session(jsonl_path):
        condition: Literal["interactive", "batch_agent"] = "batch_agent"
        reason = "session_log_resolved_batch_markers"
    else:
        condition = "interactive"
        reason = "session_log_resolved"

    return AttributionRecord(
        bug_key=introducer_result.bug_key,
        fix_commit=introducer_result.fix_commit,
        introducer_commit=introducer_result.introducer_commit,
        introducer_author=introducer_result.introducer_author,
        introducer_session_id=session_id,
        authoring_condition=condition,
        resolution_reason=reason,
        confidence=introducer_result.confidence,
        resolved_at=now,
    )


# ---------------------------------------------------------------------------
# Persistence (D2)
# ---------------------------------------------------------------------------


def persist_attribution(
    records: list[AttributionRecord],
    project_root: Path,
) -> int:
    """Persist AttributionRecords to the introducer_attributions SQLite table.

    Uses INSERT OR REPLACE to deduplicate by UNIQUE(project_id, fix_commit,
    introducer_commit, carril). Idempotent: re-running with the same records
    produces no duplicate rows.

    Conecta vía capa canónica (get_project_db) — S11899.6 / E8204.

    Args:
        records: List of AttributionRecord instances to persist.
        project_root: Project root path — resolved via get_project_db/get_project_id.

    Returns:
        Number of rows inserted/replaced.
    """
    from raise_cli.storage.schema import create_all

    pid = get_project_id(project_root)
    conn = get_project_db(project_root)
    create_all(conn)  # idempotente — garantiza tabla en DB canónica
    count = 0
    for record in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO introducer_attributions (
                project_id,
                bug_key,
                fix_commit,
                carril,
                tier,
                introducer_commit,
                introducer_author,
                introducer_session_id,
                authoring_condition,
                resolution_reason,
                confidence,
                resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pid,
                record.bug_key,
                record.fix_commit,
                "commission",  # V47: carril Carril A — legacy SZZ
                "high",  # AC5: alinea con multitrack (S11899.1)
                record.introducer_commit,
                record.introducer_author,
                record.introducer_session_id,
                record.authoring_condition,
                record.resolution_reason,
                record.confidence,
                record.resolved_at.isoformat(),
            ),
        )
        count += 1
    conn.commit()
    return count
    # Sin conn.close() — patrón multitrack (GC gestiona ciclo de vida)


def get_attribution_dataset(
    *,
    project_root: Path,
) -> list[AttributionRecord]:
    """Return all persisted AttributionRecords for the given project.

    Conecta vía capa canónica (get_project_db) — S11899.6 / E8204.
    create_all() es idempotente — garantiza tabla-existe; SELECT vacío retorna [].

    Args:
        project_root: Project root path — resolved via get_project_db/get_project_id.

    Returns:
        List of AttributionRecord instances (empty if no rows for project_id).
    """
    from raise_cli.storage.schema import create_all

    pid = get_project_id(project_root)
    conn = get_project_db(project_root)
    create_all(conn)  # idempotente — contrato tabla-existe
    rows = conn.execute(
        "SELECT * FROM introducer_attributions WHERE project_id = ? ORDER BY id",
        (pid,),
    ).fetchall()
    result: list[AttributionRecord] = []
    for row in rows:
        resolved_at_raw = row["resolved_at"]
        try:
            resolved_at = datetime.fromisoformat(resolved_at_raw)
        except (ValueError, TypeError):
            resolved_at = datetime.now(tz=UTC)

        result.append(
            AttributionRecord(
                bug_key=row["bug_key"] or "",
                fix_commit=row["fix_commit"],
                introducer_commit=row["introducer_commit"],
                introducer_author=row["introducer_author"] or "",
                introducer_session_id=row["introducer_session_id"],
                authoring_condition=row["authoring_condition"],
                resolution_reason=row["resolution_reason"] or "",
                confidence=float(row["confidence"]),
                resolved_at=resolved_at,
            )
        )
    return result
    # Sin conn.close() — patrón multitrack (GC gestiona ciclo de vida)
