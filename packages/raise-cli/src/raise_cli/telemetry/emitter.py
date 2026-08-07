"""UnifiedEmitter — single emission path for all telemetry signals (S3672.1).

Replaces writer.py (SQLite path) and ServerEmitHook (server POST path).
Every signal is always written to SQLite; server POST is attempted when
RAISE_SERVER_URL + RAISE_API_KEY are configured.

server_sync_status, trace_id, span_id, and source are stored as dedicated
indexed columns (V18/V19). The payload JSON carries all Signal fields unchanged.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal

import httpx
from pydantic import ValidationError

from raise_cli.hooks.events import (
    HookEvent,
    HookResult,
    PipelinePhaseEvent,
    WorkCloseEvent,
    WorkLifecycleEvent,
    WorkStartEvent,
)
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all
from raise_cli.work_events.schemas import AgentEventCreate, AgentEventResponse

if TYPE_CHECKING:
    from raise_cli.telemetry.schemas import Signal

logger = logging.getLogger(__name__)

_ENDPOINT = "/api/v1/agent/events"
_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=2.0)

SkillEventType = Literal["start", "complete", "abandon"]


@dataclass
class EmitResult:
    """Result of emitting a signal."""

    success: bool
    path: Path | None = None
    error: str | None = None


class UnifiedEmitter:
    """Single emitter replacing writer.py + ServerEmitHook.

    emit(signal) always writes SQLite; optionally POSTs to server when configured.
    handle(event) provides the hook interface replacing both TelemetryHook and
    ServerEmitHook.
    """

    events: ClassVar[list[str]] = [
        "session:start",
        "session:close",
        "graph:build",
        "pattern:added",
        "discover:scan",
        "init:complete",
        "adapter:loaded",
        "adapter:failed",
        "release:publish",
        "work:start",
        "work:close",
        "work:lifecycle",
        "pipeline:phase_entered",
    ]
    priority: ClassVar[int] = 0

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        client: httpx.Client | None = None,
        db_path: Path | None = None,
    ) -> None:
        self._project_root = project_root
        self._client = client
        self._db_path = db_path
        self._built_client: httpx.Client | None = None
        self._retry_queue = None
        self._stats: dict[str, int] = {
            "emitted": 0,
            "errors": 0,
            "dropped_no_ref": 0,
            "response_schema_errors": 0,
        }
        if project_root is not None:
            from raise_cli.work_events.retry_queue import WorkEventRetryQueue

            self._retry_queue = WorkEventRetryQueue(project_root)

    @property
    def stats(self) -> dict[str, int]:
        """Expose counters for observability (mirrors ServerEmitHook.stats)."""
        merged = dict(self._stats)
        if self._retry_queue is not None:
            merged.update(self._retry_queue.stats)
        else:
            merged.setdefault("queued", 0)
            merged.setdefault("drained", 0)
            merged.setdefault("dead_lettered", 0)
        return merged

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def emit(
        self,
        signal: Signal,
        *,
        base_path: Path | None = None,
        session_id: str | None = None,
        db_path: Path | None = None,
    ) -> EmitResult:
        """Emit signal to SQLite (always) and server (when configured)."""
        from raise_cli.work_events.translator import translate_signal

        client = self._get_client()
        server_event = (
            translate_signal(signal, session_id=session_id) if client else None
        )

        sync_status = "local_only"
        if client and server_event:
            if self._retry_queue is not None:
                self._retry_queue.drain(lambda p: self._post_once(client, p))
            post_ok = self._post_once(client, server_event.model_dump(mode="json"))
            if post_ok:
                sync_status = "synced"
                self._stats["emitted"] += 1
            else:
                sync_status = "pending"
                self._stats["errors"] += 1
                if self._retry_queue is not None:
                    self._retry_queue.enqueue(
                        server_event.model_dump(mode="json"),
                        server_event.work_item_ref,
                    )

        result = self._write_sqlite(
            signal,
            sync_status=sync_status,
            session_id=session_id,
            base_path=base_path,
            db_path=db_path,
        )
        _post_otlp(signal)
        return result

    def handle(self, event: HookEvent) -> HookResult:
        """Hook interface — replaces TelemetryHook + ServerEmitHook.

        Work/pipeline events: server POST via translate() (no SQLite write —
        SQLite write happens via emit() from CLI commands directly).
        Telemetry events: CommandUsage Signal → self.emit() (SQLite + server).
        Never raises.
        """
        try:
            if isinstance(event, (WorkStartEvent, WorkCloseEvent, WorkLifecycleEvent)):
                return self._handle_work_hook_event(event)
            if isinstance(event, PipelinePhaseEvent):
                return self._handle_pipeline_phase(event)
            return self._handle_command_event(event)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "UnifiedEmitter.handle failed for %s: %s",
                getattr(event, "event_name", "?"),
                exc,
            )
            return HookResult(status="error", message=str(exc))

    def _handle_work_hook_event(self, event: HookEvent) -> HookResult:
        """Server POST for work hook events — mirrors old ServerEmitHook behavior."""
        from raise_cli.work_events.translator import translate

        client = self._get_client()
        if client is None:
            return HookResult(status="ok")

        if self._retry_queue is not None:
            self._retry_queue.drain(lambda p: self._post_once(client, p))

        server_event = translate(event, db_path=self._db_path)
        if server_event is None:
            self._stats["dropped_no_ref"] += 1
            return HookResult(status="ok")

        payload = server_event.model_dump(mode="json")
        outcome = self._post_with_validation(client, payload, event.event_name)
        if outcome == "ok":
            self._stats["emitted"] += 1
            return HookResult(status="ok")
        if outcome == "schema_error":
            self._stats["response_schema_errors"] += 1
            return HookResult(status="error", message="response schema drift")
        # transport error — queue if available (CLI must not see hard error)
        self._stats["errors"] += 1
        if self._retry_queue is not None:
            self._retry_queue.enqueue(payload, server_event.work_item_ref)
            return HookResult(status="ok", message="queued for retry")
        return HookResult(status="error", message="transport: POST failed")

    def _post_with_validation(
        self, client: httpx.Client, payload: dict[str, Any], event_name: str
    ) -> Literal["ok", "transport_error", "schema_error"]:
        """POST + validate response. Returns tagged outcome."""
        try:
            response = client.post(_ENDPOINT, json=payload)
            response.raise_for_status()
        except (httpx.HTTPError, httpx.RequestError) as exc:
            logger.debug("work hook POST failed for %s — %s", event_name, exc)
            return "transport_error"
        try:
            AgentEventResponse.model_validate_json(response.content)
        except ValidationError as exc:
            logger.debug("work hook response drift for %s — %s", event_name, exc)
            return "schema_error"
        return "ok"

    def _handle_pipeline_phase(self, event: HookEvent) -> HookResult:
        from raise_cli.work_events.translator import translate

        client = self._get_client()
        if client is None:
            return HookResult(status="ok")

        if self._retry_queue is not None:
            self._retry_queue.drain(lambda p: self._post_once(client, p))

        server_event = translate(event)
        if server_event is None:
            return HookResult(status="ok")

        payload = server_event.model_dump(mode="json")
        ok = self._post_once(client, payload)
        if not ok and self._retry_queue is not None:
            self._retry_queue.enqueue(payload, server_event.work_item_ref)
        return HookResult(status="ok")

    def _handle_command_event(self, event: HookEvent) -> HookResult:
        """R1 fix: call self.emit() directly — avoids module-level re-entry."""
        from raise_cli.telemetry.schemas import CommandUsage

        command, subcommand = event.event_name.split(":", 1)
        signal = CommandUsage(
            timestamp=datetime.now(UTC), command=command, subcommand=subcommand
        )
        result = self.emit(signal)
        if not result.success:
            return HookResult(status="error", message=result.error or "emit failed")
        return HookResult(status="ok")

    def post_direct(
        self, event: AgentEventCreate
    ) -> Literal["emitted", "already_present", "queued", "dropped"]:
        """Emit a pre-built AgentEventCreate (backfill path). Mirrors ServerEmitHook."""
        client = self._get_client()
        if client is None:
            return "dropped"

        if self._retry_queue is not None:
            self._retry_queue.drain(lambda p: self._post_once(client, p))

        payload = event.model_dump(mode="json")
        try:
            response = client.post(_ENDPOINT, json=payload)
            response.raise_for_status()
        except (httpx.HTTPError, httpx.RequestError) as exc:
            logger.debug("post_direct failed — %s", exc)
            if self._retry_queue is not None:
                self._retry_queue.enqueue(payload, event.work_item_ref)
                return "queued"
            return "dropped"

        try:
            parsed = AgentEventResponse.model_validate_json(response.content)
        except ValidationError as exc:
            logger.debug("post_direct response drift — %s", exc)
            return "dropped"

        if parsed.status == "duplicate":
            return "already_present"
        self._stats["emitted"] += 1
        return "emitted"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.Client | None:
        if self._client is not None:
            return self._client
        if self._built_client is not None:
            from raise_cli.config.server import get_server_credentials

            if get_server_credentials() is None:
                self._built_client.close()
                self._built_client = None
                return None
            return self._built_client
        built = _build_client()
        if built is not None:
            self._built_client = built
        return built

    def _post_once(self, client: httpx.Client, payload: dict[str, Any]) -> bool:
        try:
            response = client.post(_ENDPOINT, json=payload)
            response.raise_for_status()
            AgentEventResponse.model_validate_json(response.content)
            return True
        except (httpx.HTTPError, httpx.RequestError, ValidationError) as exc:
            logger.debug("server POST failed — %s", exc)
            return False

    def _write_sqlite(
        self,
        signal: Signal,
        *,
        sync_status: str,
        session_id: str | None,
        base_path: Path | None,
        db_path: Path | None,
    ) -> EmitResult:
        root = (base_path or Path.cwd()).resolve()
        pid = get_project_id(root)
        try:
            if db_path is not None:
                db_path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(db_path))
                _configure_connection(conn)
            else:
                conn = get_project_db(root)
            create_all(conn)

            if session_id is None:
                try:
                    from raise_cli._agent_session import discover_agent_session_id

                    cc_sid = discover_agent_session_id() or ""
                    row = conn.execute(
                        "SELECT session_id FROM active_sessions"
                        " WHERE project_id = ? AND cc_session_id = ? LIMIT 1",
                        (pid, cc_sid),
                    ).fetchone()
                    if row is not None:
                        session_id = row[0]
                except Exception:  # noqa: BLE001, S110
                    pass

            signal_type = signal.type if hasattr(signal, "type") else "unknown"
            timestamp = (
                signal.timestamp.isoformat()
                if hasattr(signal, "timestamp")
                else datetime.now(UTC).isoformat()
            )

            conn.execute(
                "INSERT INTO signals"
                " (project_id, timestamp, type, payload, session_id, server_sync_status,"
                "  trace_id, span_id, source, otel_resource_json,"
                "  output_tokens, input_tokens, cache_read_tokens, cache_write_tokens)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pid,
                    timestamp,
                    signal_type,
                    signal.model_dump_json(),
                    session_id,
                    sync_status,
                    getattr(signal, "trace_id", None),
                    getattr(signal, "span_id", None),
                    getattr(signal, "source", None),
                    _build_otel_resource(),
                    getattr(signal, "output_tokens", None),
                    getattr(signal, "input_tokens", None),
                    getattr(signal, "cache_read_tokens", None),
                    getattr(signal, "cache_write_tokens", None),
                ),
            )
            conn.commit()

            resolved_path = Path(conn.execute("PRAGMA database_list").fetchone()[2])
            conn.close()
            return EmitResult(success=True, path=resolved_path)

        except PermissionError as exc:
            return EmitResult(success=False, error=f"Permission denied: {exc}")
        except OSError as exc:
            return EmitResult(success=False, error=f"OS error: {exc}")
        except sqlite3.Error as exc:
            return EmitResult(success=False, error=f"SQLite error: {exc}")


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _post_otlp(signal: Signal) -> None:
    """Fire-and-forget OTLP HTTP POST. Silently drops on any error."""
    import json

    endpoint = os.environ.get("RAISE_OTLP_ENDPOINT")
    if not endpoint:
        return

    signal_type = signal.type if hasattr(signal, "type") else "unknown"
    ts = signal.timestamp if hasattr(signal, "timestamp") else datetime.now(UTC)
    ts_ns = int(ts.timestamp() * 1_000_000_000)
    trace_id = getattr(signal, "trace_id", None) or ""
    span_id = getattr(signal, "span_id", None) or ""

    resource_attrs = json.loads(_build_otel_resource())
    otel_attrs = [
        {"key": k, "value": {"stringValue": v}} for k, v in resource_attrs.items()
    ]

    payload = {
        "resourceSpans": [
            {
                "resource": {"attributes": otel_attrs},
                "scopeSpans": [
                    {
                        "scope": {"name": "raise.signals"},
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": span_id,
                                "name": signal_type,
                                "startTimeUnixNano": ts_ns,
                                "endTimeUnixNano": ts_ns,
                                "attributes": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    try:
        httpx.post(
            f"{endpoint.rstrip('/')}/v1/traces",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=2.0,
        )
    except Exception:  # noqa: BLE001
        logger.debug("OTLP POST failed — continuing", exc_info=True)


def _build_otel_resource() -> str:
    """Build OTel resource attributes JSON for signal writes."""
    import importlib.metadata
    import json

    try:
        version = importlib.metadata.version("raise-cli")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"

    attrs = {
        "gen_ai.system": "raise-cli",
        "gen_ai.environment": os.environ.get("RAISE_ENVIRONMENT", "local"),
        "service.name": "raise-cli",
        "service.version": version,
    }
    return json.dumps(attrs)


def _configure_connection(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row


def _build_client() -> httpx.Client | None:
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is None:
        return None
    server_url, api_key = creds
    return httpx.Client(
        base_url=server_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=_TIMEOUT,
    )


def load_raise_env_from_bashrc() -> None:
    """Load RAISE_SERVER_URL/RAISE_API_KEY from ~/.bashrc (moved from ServerEmitHook)."""
    bashrc = Path.home() / ".bashrc"
    if not bashrc.is_file():
        return
    try:
        for line in bashrc.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("export RAISE_SERVER_URL=") or stripped.startswith(
                "export RAISE_API_KEY="
            ):
                _, _, assignment = stripped.partition(" ")
                key, _, val = assignment.partition("=")
                val = val.strip('"').strip("'")
                if key and val and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Module-level compat functions (same API as writer.py — backward compat)
# ---------------------------------------------------------------------------

default_emitter = UnifiedEmitter()


def emit(
    signal: Signal,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
    db_path: Path | None = None,
) -> EmitResult:
    """Emit a telemetry signal. SQLite always, server when configured."""
    return default_emitter.emit(
        signal, base_path=base_path, session_id=session_id, db_path=db_path
    )


def emit_skill_event(
    skill: str,
    event: SkillEventType,
    duration_sec: int | None = None,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
    db_path: Path | None = None,
) -> EmitResult:
    """Convenience wrapper for SkillEvent emission."""
    from raise_cli.telemetry.schemas import SkillEvent

    signal = SkillEvent(
        timestamp=datetime.now(UTC),
        skill=skill,
        event=event,
        duration_sec=duration_sec,
    )
    return emit(signal, base_path=base_path, session_id=session_id, db_path=db_path)


def emit_command_usage(
    command: str,
    subcommand: str | None = None,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
    db_path: Path | None = None,
) -> EmitResult:
    """Convenience wrapper for CommandUsage emission."""
    from raise_cli.telemetry.schemas import CommandUsage

    signal = CommandUsage(
        timestamp=datetime.now(UTC),
        command=command,
        subcommand=subcommand,
    )
    return emit(signal, base_path=base_path, session_id=session_id, db_path=db_path)


def emit_error_event(
    tool: str,
    error_type: str,
    context: str,
    recoverable: bool,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,
    db_path: Path | None = None,
) -> EmitResult:
    """Convenience wrapper for ErrorEvent emission."""
    from raise_cli.telemetry.schemas import ErrorEvent

    signal = ErrorEvent(
        timestamp=datetime.now(UTC),
        tool=tool,
        error_type=error_type,
        context=context,
        recoverable=recoverable,
    )
    return emit(signal, base_path=base_path, session_id=session_id, db_path=db_path)
