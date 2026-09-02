"""Session MCP tools — raise_signal_emit, raise_session_context, raise_session_topic, raise_session_bind + helpers."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from raise_cli._agent_session import discover_agent_runtime, discover_agent_session_id
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._compact import compact_response
from raise_cli.pipeline._mcp_decorators import local_only
from raise_cli.pipeline._mcp_instance import mcp
from raise_cli.session.context_env import read_context_env

_logger = logging.getLogger(__name__)

_HANSEI_ENDPOINT = "/api/v1/agent/events"
_DEFAULT_HANSEI_JSONL = Path.home() / ".raise" / "rai" / "hansei" / "events.jsonl"


def _resolve_session_jira_key(cc_session_id: str | None = None) -> str | None:
    """Resolve jira_key with namespaced-session precedence.

    Precedence: $RAISE_SESSION_JIRA_KEY >
    .raise/rai/sessions/<cc_session_id>/context.env > None.

    Mirrors `.claude/hooks/_emit_hansei.py::_resolve_jira_key`. Duplicated
    deliberately: the hook script is stdlib-only and cannot import raise_cli.

    Per-session namespacing (RAISE-1982) prevents cross-attribution between
    concurrent CC sessions in the same worktree. Known latent gap: the MCP
    subprocess env cache at CC spawn time may not contain
    RAISE_AGENT_SESSION_ID — callers that have session_id should pass it
    explicitly via the arg.
    """
    env_val = os.environ.get("RAISE_SESSION_JIRA_KEY")
    if env_val:
        return env_val
    cc_id = cc_session_id or discover_agent_session_id()
    if not cc_id:
        return None
    return read_context_env(Path.cwd(), cc_id, "RAISE_SESSION_JIRA_KEY")


def _build_session_topic_event(
    *, kind: str, topic: str, session_id: str
) -> dict[str, Any]:
    """Build the HanseiEvent-shaped dict for a session_topic emission."""
    return {
        "event_id": uuid4().hex[:16],
        "event_type": "session_topic",
        "timestamp": datetime.now(UTC).isoformat(),
        "session_id": session_id,
        "story_id": None,
        "epic_id": None,
        "jira_key": _resolve_session_jira_key(session_id),
        "actor": "agent",
        "title": topic,
        "summary": f"kind={kind}",
        "source": discover_agent_runtime(),
        "source_ref": "raise_session_topic",
        "tags": [f"kind:{kind}"],
        "confidence": 1.0,
    }


def _append_hansei_jsonl(event: dict[str, Any]) -> Path:
    """Write one JSONL line at $RAISE_HANSEI_EVENTS_JSONL (creating parents)."""
    target = Path(
        os.environ.get("RAISE_HANSEI_EVENTS_JSONL", str(_DEFAULT_HANSEI_JSONL))
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")
    return target


def _emit_session_topic(
    *,
    kind: str,
    topic: str,
    transport: Any | None = None,
    agent_session_id: str | None = None,
) -> str:
    """Core emission with Platform/Community switch. Returns JSON-encoded result.

    The ``transport`` parameter is a test seam — in production the httpx
    client builds its own default transport; tests inject
    ``httpx.MockTransport`` to intercept POSTs without touching the network.
    """
    session_id = discover_agent_session_id(override=agent_session_id)
    if not session_id:
        return json.dumps(
            {
                "status": "error",
                "reason": (
                    "Could not resolve agent session_id — neither "
                    "RAISE_AGENT_SESSION_ID, RAISE_CC_SESSION_ID, nor "
                    "CLAUDE_CODE_SSE_PORT + matching .raise/rai/sessions/*/cc.port "
                    "are available."
                ),
            }
        )

    event = _build_session_topic_event(kind=kind, topic=topic, session_id=session_id)

    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    server_url, api_key = creds if creds is not None else ("", "")

    if server_url and api_key:
        import httpx

        from raise_cli.work_events.schemas import AgentEventCreate, make_event_id

        jira_key = event.get("jira_key")
        iso = event["timestamp"]
        agent_event = AgentEventCreate(
            event_type="session_topic",
            work_item_ref=jira_key if jira_key else None,
            event_id=make_event_id(
                event_type="session_topic",
                work_item_ref=jira_key,
                iso_timestamp=iso,
                source_id=session_id,
            ),
            payload=event,
        )
        payload = agent_event.model_dump(mode="json")
        try:
            client_kwargs: dict[str, Any] = {
                "base_url": server_url,
                "headers": {"Authorization": f"Bearer {api_key}"},
                "timeout": httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=2.0),
            }
            if transport is not None:
                client_kwargs["transport"] = transport
            with httpx.Client(**client_kwargs) as client:
                response = client.post(_HANSEI_ENDPOINT, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            return json.dumps(
                {
                    "status": "error",
                    "mode": "platform",
                    "reason": f"HTTP error: {exc}",
                }
            )
        return compact_response({"status": "ok", "mode": "platform"})

    path = _append_hansei_jsonl(event)
    return compact_response({"status": "ok", "mode": "community", "path": str(path)})


@local_only
async def raise_signal_emit(
    work_type: str,
    work_id: str,
    event: str,
    phase: str = "init",
    task: str = "",
    cwd: str = "",
    agent_session_id: str | None = None,
) -> str:
    """Emit a work lifecycle signal for tracking.

    Args:
        work_type: Type of work ("epic" or "story").
        work_id: Work identifier (e.g., "S1305.6", "E1305").
        event: Lifecycle event ("start", "complete", "blocked").
        phase: Workflow phase — canonical ("init", "design", "plan", "implement",
            "architecture-review", "quality-review", "review", "close") or a
            pipeline phase normalized via PHASE_MAP (e.g. bugfix "triage").
        task: Task identity within a phase (e.g., "Task 1: add schema fields").
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (the stateless MCP server has no checkout of its own, S15457.2).
             Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_signal_emit")
    if isinstance(_root, dict):
        return json.dumps(_root)
    _project = _root

    def _run() -> str:
        from raise_cli.telemetry.emitter import emit as _emit_telemetry
        from raise_cli.telemetry.phase_map import normalize_phase
        from raise_cli.telemetry.schemas import WorkLifecycle

        # RAISE-8347: same normalization as the CLI path — pipeline phases
        # (e.g. bugfix "triage") map to canonical phases instead of failing
        # Pydantic validation. Unknown phases still fail loud.
        normalized_phase = normalize_phase(work_type.lower(), phase or "init")

        branch: str | None = None
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=_project,
            )
            branch = result.stdout.strip() or None
        except Exception:  # noqa: BLE001
            _logger.debug("Failed to resolve branch for signal", exc_info=True)

        mission_id: str | None = None

        try:
            lifecycle = WorkLifecycle(
                timestamp=datetime.now(UTC),
                work_type=work_type,  # type: ignore[arg-type]
                work_id=work_id,
                event=event,  # type: ignore[arg-type]
                phase=normalized_phase,  # type: ignore[arg-type]
                task=task or None,
                branch=branch,
                agent_session_id=discover_agent_session_id(override=agent_session_id),
                source=discover_agent_runtime(),
                mission_id=mission_id,
            )
            emit_result = _emit_telemetry(lifecycle)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"status": "error", "reason": str(exc)})
        if not emit_result.success:
            return json.dumps(
                {"status": "error", "reason": emit_result.error or "Signal emit failed"}
            )
        return json.dumps({"status": "ok"})

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_session_context(
    sections: str = "progress,coaching",
    cwd: str = "",
    agent_session_id: str | None = None,
) -> str:
    """Load RaiSE session context sections for AI consumption.

    Args:
        sections: Comma-separated section names (default "progress,coaching").
                  Available: governance, behavioral, coaching, deadlines, progress,
                  ledger.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery — symmetric with `raise_ledger_add`'s
            override, closing the seam where a write under an explicit
            session_id could surface empty under a divergent env-resolved
            session (RAISE-13146 AR F1). Resolved in-process here (design §3)
            and passed to the backend, not left to per-transport resolution.
    """
    from raise_cli.session.context_backend import get_session_context_backend

    _root = _caller_context.require_caller_cwd(cwd, "raise_session_context")
    if isinstance(_root, dict):
        return json.dumps(_root)

    section_list = [s.strip() for s in sections.split(",") if s.strip()]
    resolved_session_id = discover_agent_session_id(override=agent_session_id)
    try:
        backend = get_session_context_backend(cwd=str(_root) if cwd else "")
        result = await backend.bundle(section_list, session_id=resolved_session_id)
    except RuntimeError as exc:
        return json.dumps({"status": "error", "reason": str(exc)})
    return json.dumps(result)


@local_only
async def raise_session_history(
    limit: int = 10,
    epic: str = "",
    project_path: str = "",
    agent_session_id: str | None = None,
    all_worktrees: bool = False,
) -> str:
    """Query recent session records with narratives and outcomes.

    Returns sessions ordered by closed_at DESC with narrative, next_session_prompt,
    outcomes, and pattern IDs. Supports filtering by epic for context loading.

    Defaults to the caller's scope (E15456): same worktree_id only, main
    checkout ('') sees only main-attributable rows; unattributable rows
    (worktree_id='' AND agent_session_id='') are excluded. Pass
    all_worktrees=True to opt into the legacy project-wide read.

    Args:
        limit: Maximum number of sessions to return (default 10).
        epic: Filter to sessions for a specific epic (e.g., "E2780"). Empty = all epics.
        project_path: Caller's absolute checkout path. Required in community
            stdio mode — omitting it returns a structured ``cwd_required``
            error (S15457.2). Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
        all_worktrees: Explicit widen opt-in — legacy project-wide read,
            ignoring the caller's worktree scope (D3: never the default).
    """
    _root = _caller_context.require_caller_cwd(project_path, "raise_session_history")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from raise_cli.session.scope import resolve_scope
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        root = _root
        scope = resolve_scope(root, agent_session_id)
        conn = get_project_db(root)
        create_all(conn)
        pid = get_project_id(root)

        where = "sr.project_id = ?"
        params: list[object] = [pid]
        if not all_worktrees:
            where += (
                " AND sr.worktree_id = ?"
                " AND NOT (sr.worktree_id = '' AND sr.agent_session_id = '')"
            )
            params.append(scope.worktree_id)
        if epic:
            where += " AND sr.epic = ?"
            params.append(epic)
        params.append(limit)

        # The interpolated WHERE clause contains fixed literals; values use "?".
        sql = f"""SELECT sr.session_id, sr.closed_at, sr.summary, sr.session_type,
                          sr.epic, sr.narrative, sr.next_session_prompt, sr.notes,
                          sr.outcomes_json, sr.completed_epics_json
                   FROM session_records sr
                   WHERE {where}
                   ORDER BY sr.closed_at DESC
                   LIMIT ?"""  # noqa: S608  # nosec B608
        rows = conn.execute(sql, params).fetchall()

        sessions = []
        for row in rows:
            pat_rows = conn.execute(
                "SELECT id FROM session_patterns WHERE project_id = ? AND session_id = ?",
                (pid, row["session_id"]),
            ).fetchall()
            sessions.append(
                {
                    "session_id": row["session_id"],
                    "closed_at": row["closed_at"],
                    "summary": row["summary"],
                    "session_type": row["session_type"],
                    "epic": row["epic"],
                    "narrative": row["narrative"],
                    "next_session_prompt": row["next_session_prompt"],
                    "notes": row["notes"],
                    "outcomes": json.loads(row["outcomes_json"] or "[]"),
                    "completed_epics": json.loads(row["completed_epics_json"] or "[]"),
                    "patterns": [r["id"] for r in pat_rows],
                }
            )

        conn.close()
        return json.dumps({"status": "ok", "sessions": sessions})

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_session_topic(
    kind: str, topic: str, agent_session_id: str | None = None
) -> str:
    """Emit a session_topic event for the HUD timeline.

    Platform mode (RAISE_SERVER_URL + RAISE_API_KEY set): POST to raise-server.
    Community mode (either var missing): append JSONL at
    $RAISE_HANSEI_EVENTS_JSONL (defaults to ~/.raise/rai/hansei/events.jsonl).

    Session ID must be resolvable via the agent session priority chain
    (RAISE_AGENT_SESSION_ID or RAISE_CC_SESSION_ID or CC port discovery).
    Without it, the tool returns an error rather than fabricating an id.

    Args:
        kind: Topic kind (e.g., "implement", "decide", "research", "review").
        topic: Short topic description, shown verbatim on the HUD timeline.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
    """
    return await asyncio.to_thread(
        _emit_session_topic, kind=kind, topic=topic, agent_session_id=agent_session_id
    )


@mcp.tool()
async def raise_session_bind(
    key: str, value: str, cwd: str = "", agent_session_id: str | None = None
) -> str:
    """Write a key=value pair to the per-session context.env file.

    Binds a context variable (e.g., RAISE_SESSION_JIRA_KEY) to the active
    agent session. Uses line-replace semantics — preserves other keys.

    Args:
        key: Context key (e.g., "RAISE_SESSION_JIRA_KEY").
        value: Value to bind.
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_session_bind")
    if isinstance(_root, dict):
        return json.dumps(_root)
    _project = _root

    def _run() -> str:
        from raise_cli.session.context_env import write_context_env

        session_id = discover_agent_session_id(override=agent_session_id)
        if not session_id:
            return json.dumps(
                {
                    "status": "error",
                    "reason": (
                        "Could not resolve agent session_id — neither "
                        "RAISE_AGENT_SESSION_ID, RAISE_CC_SESSION_ID, nor "
                        "CLAUDE_CODE_SSE_PORT + matching .raise/rai/sessions/*/cc.port "
                        "are available."
                    ),
                }
            )
        try:
            write_context_env(_project, session_id, key, value)
        except ValueError as exc:
            return json.dumps({"status": "error", "reason": str(exc)})
        return compact_response({"status": "ok"})

    return await asyncio.to_thread(_run)


@mcp.tool()
async def raise_ledger_add(
    kind: str,
    natural_key: str,
    fields: str = "{}",
    cwd: str = "",
    agent_session_id: str | None = None,
) -> str:
    """Upsert a row in the session ledger — cross-project self-surfacing store.

    Independent of the fragile session-binding (path-equality across
    worktrees, `rai session journal add`): keyed by `discover_agent_session_id()`
    (env-resolved, worktree-proof) and persisted to the global
    `~/.rai/raise.db` (`session_ledger_entries`). A second call with the same
    `natural_key` UPSERTs (rewrites the row) rather than duplicating it.

    Args:
        kind: LedgerKind value (meta, project, cartridge, issue, branch,
              artifact, mission, open_thread, friction).
        natural_key: Upsert key within the session (e.g. "RAISE-13146").
        fields: JSON object of per-kind columns (e.g. '{"status":"In Progress"}').
        cwd: Caller's absolute checkout path. Required in community stdio
             mode — omitting it returns a structured ``cwd_required`` error
             (S15457.2). Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_ledger_add")
    if isinstance(_root, dict):
        return json.dumps(_root)
    _project = _root

    def _run() -> str:
        from pydantic import ValidationError

        from raise_cli.schemas.session_ledger import LedgerEntry, LedgerKind
        from raise_cli.session.ledger import upsert_entry
        from raise_cli.storage.connection import get_project_id

        session_id = discover_agent_session_id(override=agent_session_id)
        if not session_id:
            return json.dumps(
                {
                    "status": "error",
                    "reason": (
                        "Could not resolve agent session_id — neither "
                        "RAISE_AGENT_SESSION_ID, RAISE_CC_SESSION_ID, nor "
                        "CLAUDE_CODE_SSE_PORT + matching .raise/rai/sessions/*/cc.port "
                        "are available."
                    ),
                }
            )
        try:
            kind_enum = LedgerKind(kind)
        except ValueError:
            return json.dumps(
                {
                    "status": "error",
                    "reason": f"Invalid kind: {kind!r}. Valid: "
                    f"{sorted(k.value for k in LedgerKind)}",
                }
            )
        try:
            fields_raw = json.loads(fields) if fields else {}
        except json.JSONDecodeError as exc:
            return json.dumps(
                {"status": "error", "reason": f"Invalid fields JSON: {exc}"}
            )
        if not isinstance(fields_raw, dict):
            return json.dumps(
                {
                    "status": "error",
                    "reason": (
                        "fields must be a JSON object (dict), got "
                        f"{type(fields_raw).__name__}: {fields_raw!r}"
                    ),
                }
            )
        # Boundary coercion for CLI parity — `rai session ledger add -f k=v`
        # always yields str values (see cli/commands/ledger.py:_parse_fields).
        # A JSON number/bool/null in `fields` (e.g. design §4.1's numeric
        # `context_size`) must coerce to str here rather than raise an
        # unhandled ValidationError through asyncio.to_thread (QR-1).
        fields_dict: dict[str, str] = {
            str(key): str(value) for key, value in fields_raw.items()
        }

        try:
            entry = LedgerEntry(
                session_id=session_id,
                kind=kind_enum,
                natural_key=natural_key,
                timestamp=datetime.now(UTC),
                project_id=get_project_id(_project),
                fields=fields_dict,
            )
        except ValidationError as exc:
            return json.dumps({"status": "error", "reason": f"Invalid entry: {exc}"})
        upsert_entry(entry, _project)
        return compact_response(
            {"status": "ok", "session_id": session_id, "upserted": natural_key}
        )

    return await asyncio.to_thread(_run)


# --- S7884.2: composite session bookends (ADR-093 / ADR-024) ---------------


async def _session_open_impl(cwd: str = "", include_bundle: bool = True) -> str:
    def _run() -> str:
        from raise_cli.session.open_service import (
            build_open_report,
            run_or_log_bundle_skip,
            surface_ledger_if_bundle_skipped,
        )

        project = Path(cwd)
        report = build_open_report(project_path=project, cwd=project)
        report = run_or_log_bundle_skip(report, project, include_bundle)
        report = surface_ledger_if_bundle_skipped(project, report, include_bundle)
        # K3: telemetry is a handler side-effect, never an LLM turn.
        with suppress(Exception):
            _emit_session_topic(kind="lifecycle", topic="session-open")
        payload = report.model_dump()
        if not payload.get("bundle"):
            payload.pop("bundle", None)
        if not payload.get("orientation_ledger"):
            payload.pop("orientation_ledger", None)
        # Workspace readiness gate (S14927.4 / RAISE-14931).
        # Deferred imports break the import cycle:
        #   workspace_readiness → worktree.provision → workspace.readiness
        # Mirrors the pattern in doctor/checks/workspace_readiness.py.
        # Gate flag RAISE_SESSION_READINESS_GATE=0 disables eval cleanly.
        # Exception guard: eval failure must never prevent session open.
        # Only evaluate readiness for leased worktrees (.git is a file, not a dir).
        # Main-checkout sessions are legitimate for config reads/edits (CLAUDE.md) —
        # running the full worktree policy there produces false-positive warnings.
        _is_worktree = (project / ".git").is_file()
        if _is_worktree and os.environ.get("RAISE_SESSION_READINESS_GATE", "1") not in (
            "0",
            "false",
            "False",
        ):
            with suppress(Exception):
                from raise_cli.workspace.readiness import evaluate_workspace_readiness
                from raise_cli.worktree.provision import git_worktree_readiness_policy

                wt_report = evaluate_workspace_readiness(
                    project, git_worktree_readiness_policy()
                )
                payload["readiness"] = {
                    "is_ready": wt_report.is_ready,
                    "findings": [
                        {
                            "code": f.code,
                            "message": f.message,
                            "severity": f.severity,
                        }
                        for f in wt_report.findings
                    ],
                }
                if not wt_report.is_ready:
                    payload["readiness_warning"] = {
                        "message": (
                            "Workspace has readiness issues — run "
                            "'rai worktree register' to re-provision."
                        ),
                        "required_findings": [
                            f.code for f in wt_report.required_findings
                        ],
                    }
        # Session lease acquisition (RAISE-15087 S3).
        # Acquire a worktree lease so the cockpit TUI shows this session as active.
        # Best-effort: failure must never prevent session open.
        if _is_worktree:
            with suppress(Exception):
                from raise_cli._agent_session import discover_agent_session_id
                from raise_cli.cockpit.session_lease import (
                    acquire_session_lease,
                    resolve_worktree_for_session,
                )
                from raise_cli.storage.leases import SqliteLeaseStore

                sid = discover_agent_session_id()
                if sid:
                    wt_id = resolve_worktree_for_session(project, project)
                    if wt_id:
                        lease_store = SqliteLeaseStore(project)
                        acquired = acquire_session_lease(lease_store, wt_id, sid)
                        payload["session_lease"] = {
                            "worktree_id": wt_id,
                            "acquired": acquired,
                        }

        from raise_cli._agent_session import discover_agent_session_id
        from raise_cli.storage.connection import get_project_id

        _sid = discover_agent_session_id()
        _pid = get_project_id(project)
        payload["rai_meta"] = {
            "session_id": _sid,
            "project_id": _pid,
        }

        return compact_response(payload)

    return await asyncio.to_thread(_run)


async def _session_close_full_impl(
    state_json: str, cwd: str = "", agent_session_id: str | None = None
) -> str:
    _root = _caller_context.require_caller_cwd(cwd, "raise_session_close_full")
    if isinstance(_root, dict):
        return json.dumps(_root)

    def _run() -> str:
        from pydantic import ValidationError

        from raise_cli.onboarding.profile import (
            DeveloperProfile,
            load_developer_profile,
        )
        from raise_cli.session.close import CloseInput, process_session_close

        project = _root
        try:
            close_input = CloseInput.model_validate_json(state_json)
        except ValidationError as exc:
            return json.dumps({"status": "error", "reason": str(exc)})

        profile = load_developer_profile() or DeveloperProfile(name="unknown")
        session_id = discover_agent_session_id(override=agent_session_id)
        if not session_id:
            return json.dumps(
                {
                    "status": "error",
                    "reason": "No active session — run rai session start first",
                }
            )
        result = process_session_close(close_input, profile, project, session_id)
        with suppress(Exception):
            _emit_session_topic(kind="lifecycle", topic="session-close")
        with suppress(Exception):
            from raise_cli.session.close import (
                _maybe_emit_session_cost_kpi,  # pyright: ignore[reportPrivateUsage]
            )

            _maybe_emit_session_cost_kpi(project)

        # Release session lease on close (RAISE-15087 S3).
        with suppress(Exception):
            from raise_cli.cockpit.session_lease import (
                release_session_lease,
                resolve_worktree_for_session,
            )
            from raise_cli.storage.leases import SqliteLeaseStore

            wt_id = resolve_worktree_for_session(project, project)
            if wt_id:
                lease_store = SqliteLeaseStore(project)
                release_session_lease(lease_store, wt_id, session_id)

        if not result.success:
            return json.dumps({"status": "error", "reason": "; ".join(result.messages)})

        # Match the CLI close path: remove only the active pointer that belongs
        # to this agent and the session just closed.  Passing both identities
        # preserves a newer session for this agent and every other agent's
        # pointer.
        from raise_cli.session.index import clear_active_session

        clear_active_session(
            session_id=result.session_id,
            project_root=project,
            cc_session_id=session_id,
        )

        # Register the closed session in the shared index, matching the CLI
        # close path.  ``process_session_close`` persists the state and rich
        # record, but session-open resolves its continuity donor via the
        # prefix-scoped ``sessions`` index.
        from raise_cli.session.index import SessionIndexEntry, write_session_entry

        close_time = datetime.now()
        branch = (
            close_input.current_work.branch
            if close_input.current_work is not None
            else ""
        )
        write_session_entry(
            profile.get_pattern_prefix(),
            SessionIndexEntry(
                id=result.session_id,
                name=close_input.summary or result.session_id,
                started=close_time,
                closed=close_time,
                type=close_input.session_type,
                summary=close_input.summary,
                outcomes=close_input.outcomes,
                branch=branch,
            ),
            project_root=project,
        )

        # Worktree donor bookkeeping — parity with CLI close
        # (cli/commands/session.py): the next session opened in this worktree
        # finds its continuity donor via worktrees.last_session_id (S15456.1).
        # Narrow catches only: close must never fail because bookkeeping did.
        from raise_cli.storage.worktrees import (
            SqliteWorktreeStore,
            WorktreeNotFoundError,
        )

        try:
            wt_store = SqliteWorktreeStore(project=project)
            wt = wt_store.get_by_path(str(project))
            wt_store.set_last_session(wt.worktree_id, result.session_id)
        except WorktreeNotFoundError:
            _logger.debug("MCP close outside a registered worktree — no donor to mark")
        except Exception:  # noqa: BLE001
            _logger.warning("MCP close: failed to mark worktree donor", exc_info=True)

        return compact_response(
            {
                "status": "ok",
                "session_id": result.session_id,
                "recorded": {
                    "patterns": result.patterns_added,
                    "corrections": result.corrections_added,
                },
            }
        )

    return await asyncio.to_thread(_run)


@local_only
async def raise_session_open(cwd: str = "", include_bundle: bool = True) -> str:
    """Composite session open: hygiene, drift, DB, mission, bundle, MCP.

    One call replaces the deterministic sequence of the session-start
    skill. Statuses are ok|warn|blocked — blocked requires a human
    decision (the tool never auto-resolves).

    Args:
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
        include_bundle: Also run the start flow and embed the orientation
            bundle (set False to re-check without starting a session).
    """
    _root = _caller_context.require_caller_cwd(cwd, "raise_session_open")
    if isinstance(_root, dict):
        return json.dumps(_root)
    return await _session_open_impl(cwd=str(_root), include_bundle=include_bundle)


@local_only
async def raise_session_close_full(
    state_json: str, cwd: str = "", agent_session_id: str | None = None
) -> str:
    """Composite session close: atomic structured close via CloseInput JSON.

    Parity with `rai session close --state-file` — patterns, corrections,
    journal and state are written by the CLI service in one operation.

    Args:
        state_json: JSON object matching CloseInput (summary, session_type,
            patterns, corrections, next_session_prompt, ...).
            ``patterns`` entries: {"content": str (required),
            "context": str = "", "type": str = "process"} — uses the same
            ``content`` field name as ``raise_pattern_add``, NOT
            "description". ``corrections`` entries:
            {"what": str (required), "lesson": str (required)}. Malformed
            entries raise a validation error (status: "error") instead of
            being silently dropped (RAISE-16243).
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
        agent_session_id: Explicit session ID from pipeline context (RAISE-9886).
            Overrides env discovery when the MCP server env is frozen (subagent).
    """
    return await _session_close_full_impl(
        state_json=state_json, cwd=cwd, agent_session_id=agent_session_id
    )
