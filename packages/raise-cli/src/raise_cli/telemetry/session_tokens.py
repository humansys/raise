"""Parse current session CC JSONL to produce per-phase output_token totals."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from raise_cli.telemetry.cost_report import CostReport
    from raise_cli.work_events.schemas import AgentEventCreate


class SessionTokenTotals(BaseModel):
    """Aggregated token usage for a complete CC session."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read: int = 0
    cache_write: int = 0
    model: str = "unknown"
    phases: list[str] = []
    message_count: int = 0


_SIGNAL_RE = re.compile(
    r"rai signal emit-work\s+\w+\s+\S+\s+--event\s+(start|complete)\s+--phase\s+(\w[\w-]*)"
)


def get_session_token_summary(project_path: Path) -> dict[str, int] | None:
    """Return {phase: output_tokens} for the most recent CC session JSONL.

    Returns None if no JSONL file found or no bracketed phases detected.
    """
    jsonl = find_current_session_jsonl(project_path)
    if jsonl is None:
        return None
    totals = _parse_brackets(jsonl)
    return totals if totals else None


def build_token_usage_daily_event(
    totals: SessionTokenTotals,
    *,
    session_id: str | None = None,
    work_item_ref: str | None = None,
    date: str | None = None,
    repo_slug: str | None = None,
) -> AgentEventCreate:
    """Build an AgentEventCreate for token_usage_daily from session totals."""
    from datetime import datetime

    from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

    if date is None:
        date = datetime.now(UTC).strftime("%Y-%m-%d")

    event_id = make_event_id(
        event_type="token_usage_daily",
        work_item_ref=work_item_ref,
        iso_timestamp=date,
        source_id=session_id or "unknown",
    )

    payload: dict[str, object] = {
        "date": date,
        "input_tokens": totals.input_tokens,
        "output_tokens": totals.output_tokens,
        "cache_read": totals.cache_read,
        "cache_write": totals.cache_write,
        "model": totals.model,
        "phases": totals.phases,
        "session_id": session_id,
    }
    if repo_slug is not None:
        payload["repo_slug"] = repo_slug

    return AgentEventCreate(
        event_type="token_usage_daily",
        payload=payload,
        work_item_ref=work_item_ref,
        event_id=event_id,
        session_id=session_id,
    )


def build_story_cost_summary_event(
    report: CostReport,
    *,
    story_id: str,
    jira_key: str,
    session_id: str,
    date: str | None = None,
    repo_slug: str | None = None,
    agent_id: str | None = None,
    runtime: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> AgentEventCreate:
    """Build an AgentEventCreate for the story_cost_summary event type.

    Args:
        report: CostReport from scan_single_session() scoped to the story window.
        story_id: Story identifier (e.g. "S6456.2").
        jira_key: Jira issue key (e.g. "RAISE-8762") — used as work_item_ref.
        session_id: CC session ID (JSONL stem).
        date: ISO date string (YYYY-MM-DD). Defaults to today UTC.
        repo_slug: Project identifier (e.g. "raise-commons").
        agent_id: Cross-runtime agent session identity for fleet correlation.
        runtime: Runtime identifier (e.g. "claude_code").
        since: Window start used to scope the scan (None = session_fallback).
        until: Window end used to scope the scan (None = session_fallback).
    """
    from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

    if date is None:
        date = datetime.now(UTC).strftime("%Y-%m-%d")

    boundary_source = (
        "lifecycle_signals"
        if (since is not None and until is not None)
        else "session_fallback"
    )

    event_id = make_event_id(
        event_type="story_cost_summary",
        work_item_ref=jira_key,
        iso_timestamp=date,
        source_id=f"{session_id}:{story_id}",
    )

    by_skill = [
        {"skill": s.skill, "category": s.category, "cost_usd": s.cost_usd}
        for s in report.skills
    ]
    by_phase = [{"phase": p.phase, "cost_usd": p.cost_usd} for p in report.phases]
    by_model = [{"model": m.model, "cost_usd": m.cost_usd} for m in report.models]

    payload: dict[str, object] = {
        "story_id": story_id,
        "jira_key": jira_key,
        "date": date,
        "boundary_source": boundary_source,
        "cost_usd": report.total_cost_usd,
        "cost_breakdown": {
            "by_skill": by_skill,
            "by_phase": by_phase,
            "by_model": by_model,
        },
        "session_id": session_id,
    }
    if since is not None:
        payload["since"] = since.isoformat()
    if until is not None:
        payload["until"] = until.isoformat()
    if repo_slug is not None:
        payload["repo_slug"] = repo_slug
    if agent_id is not None:
        payload["agent_id"] = agent_id
    if runtime is not None:
        payload["runtime"] = runtime

    return AgentEventCreate(
        event_type="story_cost_summary",
        payload=payload,
        work_item_ref=jira_key,
        event_id=event_id,
        session_id=session_id,
    )


def build_replay_events(
    report: CostReport,
    *,
    session_id: str,
    date: str,
    repo_slug: str,
    work_item_ref: str | None = None,
    agent_id: str | None = None,
    runtime: str | None = None,
) -> list[AgentEventCreate]:
    """Build one token_usage_daily event per skill from a CostReport.

    Token counts are distributed proportionally by each skill's cost share.

    Args:
        report: CostReport from scan_single_session().
        session_id: CC log stem (JSONL filename stem).
        date: ISO date string (YYYY-MM-DD).
        repo_slug: Project identifier.
        work_item_ref: Story/epic Jira key for work attribution (AC2).
            Fed into make_event_id for idempotency — two sessions on
            different stories with identical splits get different event_ids.
        agent_id: Cross-runtime agent session identity for fleet correlation (AC3).
            Omitted from payload when None.
        runtime: Runtime identifier (e.g. "claude_code") (AC3).
            Omitted from payload when None.
    """
    from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

    if not report.skills:
        return []

    total_input = sum(m.input_tokens for m in report.models)
    total_output = sum(m.output_tokens for m in report.models)
    total_cw = sum(m.cache_write for m in report.models)
    total_cr = sum(m.cache_read for m in report.models)
    total_cost = report.total_cost_usd

    events: list[AgentEventCreate] = []
    for skill in report.skills:
        fraction = skill.cost_usd / total_cost if total_cost > 0 else 0.0

        event_id = make_event_id(
            event_type="token_usage_daily",
            work_item_ref=work_item_ref,
            iso_timestamp=date,
            source_id=f"{session_id}:{skill.skill}",
        )

        payload: dict[str, object] = {
            "date": date,
            "skill": skill.skill,
            "category": skill.category,
            "input_tokens": round(total_input * fraction),
            "output_tokens": round(total_output * fraction),
            "cache_write": round(total_cw * fraction),
            "cache_read": round(total_cr * fraction),
            "cost_usd": skill.cost_usd,
            "session_id": session_id,
            "repo_slug": repo_slug,
        }
        if agent_id is not None:
            payload["agent_id"] = agent_id
        if runtime is not None:
            payload["runtime"] = runtime

        events.append(
            AgentEventCreate(
                event_type="token_usage_daily",
                payload=payload,
                work_item_ref=work_item_ref,
                event_id=event_id,
                session_id=session_id,
            )
        )

    return events


def get_session_token_totals(project_path: Path) -> SessionTokenTotals | None:
    """Return aggregated token totals for the most recent CC session JSONL.

    Returns None if no JSONL file found or no assistant messages detected.
    """
    jsonl = find_current_session_jsonl(project_path)
    if jsonl is None:
        return None
    return parse_totals(jsonl)


def parse_totals(jsonl_path: Path) -> SessionTokenTotals | None:
    """Sum all token fields across assistant messages in a JSONL file."""
    input_tokens = 0
    output_tokens = 0
    cache_read = 0
    cache_write = 0
    message_count = 0
    model_counts: Counter[str] = Counter()
    phases: list[str] = []

    for raw in jsonl_path.open(encoding="utf-8", errors="replace"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj: Any = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or obj.get("type") != "assistant":
            continue

        message = obj.get("message")
        if not isinstance(message, dict):
            continue

        usage: Any = message.get("usage")
        if isinstance(usage, dict):
            message_count += 1
            input_tokens += _safe_int(usage.get("input_tokens"))
            output_tokens += _safe_int(usage.get("output_tokens"))
            cache_read += _safe_int(usage.get("cache_read_input_tokens"))
            cache_write += _safe_int(usage.get("cache_creation_input_tokens"))

        model_val: Any = message.get("model")
        if isinstance(model_val, str) and model_val:
            model_counts[model_val] += 1

        signal = _extract_signal(obj)
        if signal is not None and signal[0] == "complete" and signal[1] not in phases:
            phases.append(signal[1])

    if message_count == 0:
        return None

    model = model_counts.most_common(1)[0][0] if model_counts else "unknown"

    return SessionTokenTotals(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read=cache_read,
        cache_write=cache_write,
        model=model,
        phases=phases,
        message_count=message_count,
    )


def _safe_int(val: Any) -> int:
    return val if isinstance(val, int) else 0


def find_current_session_jsonl(project_path: Path) -> Path | None:
    """Return the most recently modified JSONL for this project in ~/.claude/projects/.

    CC encodes the project path by replacing both '/' and '.' with '-'.
    Promoted from private to public in S9115.1 (ADR-062 Agent Telemetry Adapter).

    RAISE-10219: when the project_path-specific CC dir has no JSONL,
    fall back to the git toplevel directory. Worktrees often run CC
    sessions whose JSONL lands under the main repo's CC project dir.
    """
    result = _find_jsonl_in_cc_dir(project_path)
    if result is not None:
        return result

    # Fallback: resolve git toplevel and retry (RAISE-10219)
    toplevel = _resolve_git_toplevel(project_path)
    if toplevel is not None and toplevel != project_path.resolve():
        return _find_jsonl_in_cc_dir(toplevel)

    return None


def _find_jsonl_in_cc_dir(project_path: Path) -> Path | None:
    """Look up the CC project dir for project_path and return newest JSONL."""
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return None
    resolved = str(project_path.resolve())
    proj_name = resolved.replace("/", "-").replace(".", "-")
    proj_dir = base / proj_name
    if not proj_dir.exists():
        return None
    jsonl_files = list(proj_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


def _resolve_git_toplevel(project_path: Path) -> Path | None:
    """Resolve git toplevel from a worktree path without subprocess.

    Walks up from project_path looking for .git. If .git is a file
    (worktree marker), reads the gitdir pointer and resolves to the
    main repo. If .git is a directory, returns that parent directly.
    """
    current = project_path.resolve()
    for _ in range(50):  # safety bound
        git_path = current / ".git"
        if git_path.is_file():
            # Worktree: .git file contains "gitdir: /path/to/.git/worktrees/name"
            try:
                content = git_path.read_text(encoding="utf-8").strip()
            except OSError:
                return None
            if content.startswith("gitdir:"):
                gitdir = content[len("gitdir:") :].strip()
                # gitdir points to .git/worktrees/<name> — main repo is two levels up
                main_git = Path(gitdir).resolve()
                if main_git.name != "worktrees":
                    main_git = main_git.parent  # .git/worktrees/<name> → .git/worktrees
                if main_git.name == "worktrees":
                    return main_git.parent.parent  # .git/worktrees → .git → repo root
            return None
        if git_path.is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


_find_current_session_jsonl = find_current_session_jsonl


def find_cc_jsonl_by_session_id(session_id: str) -> Path | None:
    """Find the Claude Code session JSONL for a given session_id.

    Searches ``~/.claude/projects/*/{session_id}.jsonl``. Returns the path with
    the largest file size (main checkout; worktree stubs are 0-byte). Returns
    None if not found or if session_id is empty.

    This bridges the MCP telemetry gap (RAISE-15783): the MCP server process
    cannot discover CLAUDE_CODE_SESSION_ID at phase advance time, but
    ``run["metadata"]["agent_session_id"]`` is stored at pipeline_start time
    when CC environment variables ARE available via the Bash tool.
    """
    if not session_id:
        return None

    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return None

    candidates: list[Path] = []
    for proj_dir in base.iterdir():
        if not proj_dir.is_dir():
            continue
        candidate = proj_dir / f"{session_id}.jsonl"
        if candidate.exists():
            candidates.append(candidate)

    if not candidates:
        return None

    return max(candidates, key=lambda f: f.stat().st_size)


def _extract_output_tokens(obj: Any) -> int:
    """Return output_tokens from an assistant message, or 0."""
    message = obj.get("message")
    if not isinstance(message, dict):
        return 0
    usage: Any = message.get("usage")
    if not isinstance(usage, dict):
        return 0
    tokens: Any = usage.get("output_tokens")
    return tokens if isinstance(tokens, int) else 0


def _extract_signal(obj: Any) -> tuple[str, str] | None:
    """Return (event, phase) if obj contains a lifecycle signal bash call, else None."""
    message = obj.get("message")
    if not isinstance(message, dict):
        return None
    for block in message.get("content", []):  # type: ignore[union-attr]
        block_any: Any = block
        if not isinstance(block_any, dict):
            continue
        if block_any.get("type") != "tool_use" or block_any.get("name") != "Bash":
            continue
        inp: Any = block_any.get("input")
        if not isinstance(inp, dict):
            continue
        cmd: Any = inp.get("command", "")
        if not isinstance(cmd, str):
            continue
        m = _SIGNAL_RE.search(cmd)
        if m:
            return m.group(1), m.group(2)
    return None


def _parse_iso_utc(ts_raw: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string and return a UTC-aware datetime or None."""
    try:
        return datetime.fromisoformat(ts_raw).astimezone(UTC)
    except ValueError:
        return None


def story_window(
    project_path: Path,
    story_id: str,
) -> tuple[datetime, datetime] | None:
    """Return (start_ts, end_ts) for the lifecycle bracket of story_id, or None.

    Queries the SQLite ``signals`` table for ``work_lifecycle`` events with
    ``work_id = story_id`` and ``event in ('start', 'complete')``. Returns None
    when either boundary is missing — the caller should fall back to the
    full-session window (D2, D4).

    Args:
        project_path: Project root used to locate the global DB.
        story_id: Story identifier in story_id format (e.g. "S6456.2").
            Must NOT be a Jira key — signals store the story_id, not the key.
    """
    import sqlite3

    from raise_cli.storage.connection import get_project_db_path

    db_path = get_project_db_path(project_path)
    if not db_path.exists():
        return None

    try:
        conn = sqlite3.connect(str(db_path))
        try:
            rows = conn.execute(
                """
                SELECT
                    json_extract(payload, '$.event') AS event,
                    timestamp
                FROM signals
                WHERE type = 'work_lifecycle'
                  AND json_extract(payload, '$.work_id') = ?
                  AND json_extract(payload, '$.event') IN ('start', 'complete')
                ORDER BY timestamp ASC
                """,
                (story_id,),
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return None

    start_ts: datetime | None = None
    end_ts: datetime | None = None

    for event, ts_raw in rows:
        ts_utc = _parse_iso_utc(ts_raw)
        if ts_utc is None:
            continue
        if event == "start" and start_ts is None:
            start_ts = ts_utc
        elif event == "complete" and end_ts is None:
            end_ts = ts_utc

    if start_ts is not None and end_ts is not None:
        return start_ts, end_ts
    return None


def _parse_brackets(jsonl_path: Path) -> dict[str, int]:
    """Sum output_tokens between start/complete signal pairs per phase."""
    totals: dict[str, int] = {}
    open_phase: str | None = None
    running: int = 0

    for raw in jsonl_path.open(encoding="utf-8", errors="replace"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj: Any = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or obj.get("type") != "assistant":
            continue

        running += _extract_output_tokens(obj)

        signal = _extract_signal(obj)
        if signal is None:
            continue
        event, phase = signal
        if event == "start":
            open_phase = phase
            running = 0
        elif event == "complete" and open_phase == phase:
            totals[phase] = totals.get(phase, 0) + running
            open_phase = None
            running = 0

    return totals
