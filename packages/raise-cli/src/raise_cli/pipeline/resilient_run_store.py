"""ResilientRunStore — circuit-breaker decorator over a primary run store.

Implements PipelineRunStore Protocol. ADR-103. S8371.1: breaker + runtime
fallback to SqliteRunStore. Buffering of fallback writes and recovery
replay (pending_sync) are S8371.2 — see _buffer_write / _on_recovery.

State machine:
    CLOSED → (N consecutive transport failures) → OPEN
    OPEN   → (cooldown elapsed, next call)       → HALF_OPEN (probe)
    HALF_OPEN probe ok  → CLOSED  + _on_recovery()
    HALF_OPEN probe fail → OPEN   (cooldown restarts)
"""

from __future__ import annotations

import asyncio
import enum
import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from raise_cli.pipeline.run_store import PipelineRunStore

__all__ = ["CircuitState", "ResilientRunStore"]

_logger = logging.getLogger(__name__)


class CircuitState(enum.Enum):
    """State of the circuit breaker controlling primary vs. fallback routing."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ResilientRunStore:
    """Circuit-breaker decorator over a primary run store with SQLite fallback.

    Args:
        primary:           Primary store (ApiRunStore in production).
        fallback:          Fallback store (SqliteRunStore — global ~/.rai/raise.db).
        failure_threshold: Consecutive transport failures before opening the breaker.
        cooldown_seconds:  Time to wait in OPEN before attempting a HALF_OPEN probe.
        clock:             Monotonic clock for cooldown measurement (injectable for tests).
    """

    def __init__(
        self,
        primary: PipelineRunStore,
        fallback: PipelineRunStore,
        *,
        failure_threshold: int = 3,
        cooldown_seconds: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._threshold = failure_threshold
        self._cooldown = cooldown_seconds
        self._clock = clock
        self._state = CircuitState.CLOSED
        self._consecutive_failures: int = 0
        self._opened_at: float | None = None
        # M1 probe guard: exactly one coroutine may probe the primary in HALF_OPEN.
        # Set synchronously (before any await) so no second coroutine can also enter
        # the probe path on the same event-loop tick.
        self._probe_in_flight: bool = False
        # S8371.2: handle to the flush task — prevents overlapping flushes.
        self._flush_task: asyncio.Task[None] | None = None

    # ------------------------------------------------------------------
    # PipelineRunStore Protocol implementation
    # ------------------------------------------------------------------

    async def save(self, run: dict[str, Any]) -> None:
        """Upsert a run — primary in CLOSED/HALF_OPEN; fallback when OPEN."""
        if self._should_attempt_primary():
            try:
                await self._primary.save(run)
                await self._mirror_primary_save(run)
                self._record_success()
                return
            except (RuntimeError, httpx.TransportError, httpx.HTTPStatusError) as exc:
                self._record_transport_failure(exc)
            finally:
                # B1 fix: guarantee _probe_in_flight is always cleared once a
                # probe completes, regardless of which exception escapes.
                # HTTPStatusError propagates past the except above — without this
                # finally the flag stays True forever and the primary is never
                # re-probed (permanent stuck-HALF_OPEN deadlock).
                if self._state is CircuitState.HALF_OPEN:
                    # HTTPStatusError reached here: server responded → transport
                    # is healthy → treat as recovery (HALF_OPEN → CLOSED).
                    _logger.info(
                        "circuit breaker: HALF_OPEN probe got HTTPStatusError "
                        "(server responded) — closing (HALF_OPEN → CLOSED)"
                    )
                    self._on_recovery()
                    self._consecutive_failures = 0
                    self._probe_in_flight = False
                    self._state = CircuitState.CLOSED
        # OPEN, or primary just failed this call → degrade to SQLite.
        # F1 fix (AR): write run AND sync_state='pending' in a single transaction
        # when the fallback supports the sync_state kwarg (SqliteRunStore V42+).
        # Falls back to the legacy two-step path for pure-Protocol fakes.
        await self._fallback_save_pending(run)

    async def load(self, run_id: str) -> dict[str, Any] | None:
        """Return the run — fallback when OPEN, on primary exception, or on primary None.

        RAISE-11102: a 404-derived None from the primary is not authoritative — the
        run may be local-only (sync_state='pending' after a degraded save). Only a
        fallback None (genuinely unknown everywhere) is returned as None.
        """
        if self._should_attempt_primary():
            try:
                result = await self._primary.load(run_id)
                self._record_success()
                if result is not None:
                    pending = self._find_pending_run(run_id)
                    if pending is not None:
                        return await self._reconcile_pending_run(result, pending)
                    return result
                local = await self._fallback.load(run_id)
                if local is not None and local.get("sync_state") == "pending":
                    return await self._reconcile_pending_run(None, local)
                return local
            except (RuntimeError, httpx.TransportError) as exc:
                self._record_transport_failure(exc)
            finally:
                if self._state is CircuitState.HALF_OPEN:
                    _logger.info(
                        "circuit breaker: HALF_OPEN probe got HTTPStatusError "
                        "(server responded) — closing (HALF_OPEN → CLOSED)"
                    )
                    self._on_recovery()
                    self._consecutive_failures = 0
                    self._probe_in_flight = False
                    self._state = CircuitState.CLOSED
        return await self._fallback.load(run_id)

    async def list_runs(self) -> list[dict[str, Any]]:
        """Return all runs — union of primary + local-only rows (D5: fallback-only when OPEN).

        RAISE-11102: a successful primary list is not necessarily complete — a run
        that degraded to local-only (sync_state='pending') may not be in the
        primary's list. Merge those in by run_id so they stay visible.
        """
        if self._should_attempt_primary():
            try:
                result = await self._primary.list_runs()
                self._record_success()
                return await self._merge_local_only_runs(result)
            except (RuntimeError, httpx.TransportError) as exc:
                self._record_transport_failure(exc)
            finally:
                if self._state is CircuitState.HALF_OPEN:
                    _logger.info(
                        "circuit breaker: HALF_OPEN probe got HTTPStatusError "
                        "(server responded) — closing (HALF_OPEN → CLOSED)"
                    )
                    self._on_recovery()
                    self._consecutive_failures = 0
                    self._probe_in_flight = False
                    self._state = CircuitState.CLOSED
        return await self._fallback.list_runs()

    async def delete(self, run_id: str) -> None:
        """Remove a run — fallback when OPEN."""
        if self._should_attempt_primary():
            try:
                await self._primary.delete(run_id)
                await self._delete_local_mirror(run_id)
                self._record_success()
                return
            except (RuntimeError, httpx.TransportError) as exc:
                self._record_transport_failure(exc)
            finally:
                if self._state is CircuitState.HALF_OPEN:
                    _logger.info(
                        "circuit breaker: HALF_OPEN probe got HTTPStatusError "
                        "(server responded) — closing (HALF_OPEN → CLOSED)"
                    )
                    self._on_recovery()
                    self._consecutive_failures = 0
                    self._probe_in_flight = False
                    self._state = CircuitState.CLOSED
        # OPEN: tombstone if run exists locally; warn if server-only.
        mark_pending_delete = getattr(self._fallback, "mark_pending_delete", None)
        if mark_pending_delete is not None:
            # Check if the run has a local row to tombstone
            local_run = await self._fallback.load(run_id)
            if local_run is not None:
                mark_pending_delete(run_id)
            else:
                _logger.warning(
                    "delete(%s) while OPEN: no local row found (server-only run) — "
                    "cannot tombstone; delete will be re-deferred (m3 narrow sub-case)",
                    run_id,
                )
        else:
            await self._fallback.delete(run_id)

    async def aclose(self) -> None:
        """Close underlying connections on both primary and fallback.

        Primary (ApiRunStore) exposes ``aclose`` (async HTTP client cleanup).
        Fallback (SqliteRunStore) exposes a synchronous ``close`` on its
        underlying ``sqlite3.Connection``. Both are closed here to avoid
        ResourceWarning: unclosed database spam (m2).
        """
        if hasattr(self._primary, "aclose"):
            await self._primary.aclose()  # type: ignore[attr-defined]
        if hasattr(self._fallback, "aclose"):
            await self._fallback.aclose()  # type: ignore[attr-defined]
        elif hasattr(self._fallback, "close"):
            self._fallback.close()  # type: ignore[attr-defined]

    async def _mirror_primary_save(self, run: dict[str, Any]) -> None:
        """Best-effort local mirror of a successful primary save.

        The local mirror lets OPEN-state reads recover the current run after a
        transient transport outage instead of silently falling back to stale
        project history.
        """
        try:
            await self._fallback.save(run)
            mark_synced = getattr(self._fallback, "mark_synced", None)
            if mark_synced is not None:
                mark_synced(run["run_id"])
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "local mirror save failed for run %s after primary success: %s",
                run["run_id"],
                exc,
            )

    async def _merge_local_only_runs(
        self, primary_runs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Union a successful primary list_runs() with local-only rows (RAISE-11102).

        Prefers ``fallback.list_pending()`` (targeted to unsynced rows) when the
        fallback supports it; falls back to a full ``fallback.list_runs()`` diff
        for pure-Protocol fakes without ``list_pending`` (guarded with getattr).

        Best-effort: a local-read failure must not break an otherwise-successful
        primary list_runs() (mirrors _mirror_primary_save/_delete_local_mirror).
        """
        merged = list(primary_runs)
        indexes = {run["run_id"]: index for index, run in enumerate(merged)}
        try:
            list_pending = getattr(self._fallback, "list_pending", None)
            extra_runs = (
                list_pending()
                if list_pending is not None
                else await self._fallback.list_runs()
            )
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "local fallback read failed while merging list_runs(): %s", exc
            )
            return primary_runs
        for local in extra_runs:
            run_id = local["run_id"]
            index = indexes.get(run_id)
            if local.get("sync_state") == "pending":
                primary = (
                    await self._primary.load(run_id) if index is not None else None
                )
                chosen = await self._reconcile_pending_run(primary, local)
                if index is None:
                    indexes[run_id] = len(merged)
                    merged.append(chosen)
                else:
                    merged[index] = chosen
            elif index is None:
                indexes[run_id] = len(merged)
                merged.append(local)
        return merged

    def _find_pending_run(self, run_id: str) -> dict[str, Any] | None:
        """Return a pending local copy for ``run_id`` when the fallback supports it."""
        list_pending = getattr(self._fallback, "list_pending", None)
        if list_pending is None:
            return None
        try:
            return next(
                (
                    run
                    for run in list_pending()
                    if run["run_id"] == run_id and run.get("sync_state") == "pending"
                ),
                None,
            )
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "local fallback read failed while reconciling run %s: %s",
                run_id,
                exc,
            )
            return None

    async def _reconcile_pending_run(
        self,
        primary: dict[str, Any] | None,
        local: dict[str, Any],
    ) -> dict[str, Any]:
        """Expose and replay a pending copy when it is ahead of the primary."""
        clean_local = {
            key: value for key, value in local.items() if key != "sync_state"
        }
        local_phase = local.get("current_phase_index", 0)
        primary_phase = primary.get("current_phase_index", 0) if primary else -1
        if not isinstance(local_phase, int) or not isinstance(primary_phase, int):
            return primary or clean_local
        if local_phase < primary_phase:
            if primary is not None:
                await self._mirror_primary_save(primary)
            return primary or clean_local
        try:
            await self._primary.save(clean_local)
        except (RuntimeError, httpx.TransportError) as exc:
            _logger.warning(
                "pending run %s could not be reconciled after a healthy read: %s",
                local["run_id"],
                exc,
            )
        except httpx.HTTPStatusError as exc:
            self._handle_flush_http_error(local, exc)
        else:
            mark_synced = getattr(self._fallback, "mark_synced", None)
            if mark_synced is not None:
                mark_synced(local["run_id"])
        return clean_local

    async def _delete_local_mirror(self, run_id: str) -> None:
        """Best-effort cleanup of the local mirror after a primary delete."""
        try:
            await self._fallback.delete(run_id)
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "local mirror delete failed for run %s after primary delete: %s",
                run_id,
                exc,
            )

    # ------------------------------------------------------------------
    # State-machine internals
    # ------------------------------------------------------------------

    def _should_attempt_primary(self) -> bool:
        """Return True when the call should be directed at the primary store.

        M1 probe guard: at most one coroutine may probe the primary during the
        HALF_OPEN window. When a probe is already in-flight (_probe_in_flight is
        True), concurrent callers return False and are served by the fallback.
        This flag is set synchronously (before any ``await``) so no second
        coroutine can slip through on the same event-loop tick.
        """
        if self._state is CircuitState.CLOSED:
            return True
        if self._state is CircuitState.OPEN:
            if self._opened_at is None:  # pragma: no cover — set atomically with OPEN
                return False
            if self._clock() - self._opened_at >= self._cooldown:
                if self._probe_in_flight:
                    # Another coroutine is already probing — route to fallback.
                    return False
                self._state = CircuitState.HALF_OPEN  # this call is the probe
                self._probe_in_flight = True
                return True
            return False
        # HALF_OPEN: _probe_in_flight is always True here — set atomically with the
        # OPEN→HALF_OPEN transition above, and cleared only when the probe resolves
        # (success, transport failure, or unexpected exception via finally).
        # Concurrent callers arriving while the probe is in-flight are routed to
        # the fallback.
        return False

    def _record_success(self) -> None:
        """A primary call succeeded — reset failure counter; close half-open probe."""
        if self._state is CircuitState.HALF_OPEN:
            _logger.info(
                "circuit breaker: probe succeeded — closing (HALF_OPEN → CLOSED)"
            )
            self._on_recovery()
        self._consecutive_failures = 0
        self._probe_in_flight = False
        self._state = CircuitState.CLOSED

    def _record_transport_failure(self, exc: BaseException) -> None:
        """A transport failure was detected — update counter and maybe open the breaker."""
        if self._state is CircuitState.HALF_OPEN:
            _logger.warning(
                "circuit breaker: half-open probe failed — re-opening (cooldown restarts): %s",
                exc,
            )
            self._probe_in_flight = False
            self._opened_at = self._clock()
            self._state = CircuitState.OPEN
            return
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._threshold:
            _logger.warning(
                "circuit breaker: %d consecutive transport failures — opening (CLOSED → OPEN): %s",
                self._consecutive_failures,
                exc,
            )
            self._opened_at = self._clock()
            self._state = CircuitState.OPEN

    # ------------------------------------------------------------------
    # S8371.2 seam hooks
    # ------------------------------------------------------------------

    async def _fallback_save_pending(self, run: dict[str, Any]) -> None:
        """Save run to fallback with sync_state='pending' in a single transaction (F1 fix).

        When the fallback supports the ``sync_state`` kwarg (SqliteRunStore V42+),
        delegates to ``fallback.save(run, sync_state='pending')`` so that the run
        row and its pending marker are written atomically in one commit.

        Falls back to the legacy two-step path (save then mark_pending) for
        pure-Protocol fakes or V41 DBs without the sync_state column.
        """
        import inspect

        save_fn = getattr(self._fallback, "save", None)
        if save_fn is not None:
            try:
                sig = inspect.signature(save_fn)
                if "sync_state" in sig.parameters:
                    await self._fallback.save(run, sync_state="pending")  # type: ignore[call-arg]
                    return
            except (ValueError, TypeError):
                pass
        # Legacy two-step path: separate save + mark_pending (non-atomic).
        await self._fallback.save(run)
        self._buffer_write(run)

    def _buffer_write(self, run: dict[str, Any]) -> None:
        """Legacy: mark a fallback write for re-sync via separate mark_pending call (S8371.2).

        Used only when the fallback does not support the sync_state kwarg (pure-Protocol
        fakes without SqliteRunStore).  The primary hot path is _fallback_save_pending().
        """
        mark = getattr(self._fallback, "mark_pending", None)
        if mark is not None:
            mark(run["run_id"])

    def _on_recovery(self) -> None:
        """Schedule a background flush of buffered runs on recovery (S8371.2).

        Schedules via ``asyncio.create_task`` (non-blocking) so the recovering
        call returns at primary latency. A task guard prevents overlapping
        flushes from the two S8371.1 B1 call sites.
        """
        _logger.info(
            "circuit breaker: recovery detected — scheduling buffered-run flush"
        )
        if self._flush_task is not None and not self._flush_task.done():
            return  # a flush is already running — don't pile up
        self._flush_task = asyncio.create_task(self._flush_buffered_runs())

    async def _flush_buffered_runs(self) -> None:
        """Replay pending rows to the primary in FIFO order (S8371.2).

        Ordering: started_at ASC, rowid ASC (deterministic FIFO).
        Error handling:
        - RuntimeError / httpx.TransportError → STOP (server flapped; resume next recovery).
        - httpx.HTTPStatusError → dispatch to _handle_flush_http_error + continue.
        """
        list_pending = getattr(self._fallback, "list_pending", None)
        if list_pending is None:
            return
        for run in list_pending():
            try:
                await self._flush_one(run)
            except (RuntimeError, httpx.TransportError):
                _logger.warning(
                    "re-sync interrupted (transport failure) — will resume on next recovery"
                )
                return
            except httpx.HTTPStatusError as exc:
                self._handle_flush_http_error(run, exc)

    async def _flush_one(self, run: dict[str, Any]) -> None:
        """Attempt to push a single pending row to the primary."""
        sync_state = run.get("sync_state")
        if sync_state == "pending_delete":
            await self._primary.delete(run["run_id"])
            purge = getattr(self._fallback, "purge_local", None)
            if purge is not None:
                purge(run["run_id"])
        else:
            await self._maybe_warn_conflict(run)
            await self._primary.save(run)
            mark_synced = getattr(self._fallback, "mark_synced", None)
            if mark_synced is not None:
                mark_synced(run["run_id"])

    def _handle_flush_http_error(
        self, run: dict[str, Any], exc: httpx.HTTPStatusError
    ) -> None:
        """Handle HTTPStatusError during flush (F2 fix).

        For pending_delete: server rejected the delete (e.g. 404) — run is already
        gone on the server.  Call purge_local to remove the local tombstone and
        avoid leaving a phantom row.

        For pending (non-delete): server rejected the payload — mark_synced so
        we don't retry forever (poison pill).
        """
        sync_state = run.get("sync_state")
        if sync_state == "pending_delete":
            _logger.error(
                "server rejected delete for run %s: %s — purging local tombstone",
                run["run_id"],
                exc,
            )
            purge = getattr(self._fallback, "purge_local", None)
            if purge is not None:
                purge(run["run_id"])
        else:
            _logger.error(
                "server rejected buffered run %s: %s — marking synced to avoid infinite retry",
                run["run_id"],
                exc,
            )
            mark_synced = getattr(self._fallback, "mark_synced", None)
            if mark_synced is not None:
                mark_synced(run["run_id"])

    async def _maybe_warn_conflict(self, run: dict[str, Any]) -> None:
        """Best-effort conflict check: warn if server copy is ahead of buffered copy (S8371.2 AC7).

        On any exception from primary.load: log at DEBUG and skip (server may be
        partially down — a failed load during re-sync is expected).
        Proceed with primary.save regardless (last-writer-wins per server contract).
        """
        try:
            server_copy = await self._primary.load(run["run_id"])
        except Exception as exc:  # noqa: BLE001
            _logger.debug(
                "conflict check skipped for %s — primary.load failed: %s",
                run["run_id"],
                exc,
            )
            return
        if server_copy is None:
            return  # run not on server yet — no conflict
        local_phase = run.get("current_phase_index", 0)
        server_phase = server_copy.get("current_phase_index", 0)
        local_status = run.get("status", "")
        server_status = server_copy.get("status", "")
        if server_phase > local_phase or (
            server_phase == local_phase and server_status != local_status
        ):
            _logger.warning(
                "conflict detected for run %s: local phase=%s status=%s, "
                "server phase=%s status=%s — applying last-writer-wins (local copy wins)",
                run["run_id"],
                local_phase,
                local_status,
                server_phase,
                server_status,
            )
