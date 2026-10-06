"""Pipeline execution context — single source of truth for skill/engine coordination.

Answers "what is the pipeline context for this issue right now?" using the
local run store. Fail-open to ``standalone`` per RAISE-10966.

RAISE-16987: Consolidates the two duplicate ``_pipeline_run_active``
implementations that previously lived in ``backlog/hooks.py`` and
``story/open_service.py``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from raise_cli.pipeline.run_store import get_run_store
from raise_core.workflow.status_sets import ACTIVE_RUN_STATUSES

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable snapshot of the pipeline context at call time.

    mode == "pipeline"  → engine is running; skill should defer backlog ops.
    mode == "standalone" → no active run; skill owns its transitions.

    Deliberate exception to the Pydantic default (D1): ``ExecutionContext``
    is a pure value object — no serialization boundary, no HTTP crossing.
    A frozen dataclass gives immutability and equality semantics at zero cost.
    """

    mode: Literal["pipeline", "standalone"]
    run_id: str | None
    phase_id: str | None
    issue_key: str | None


_STANDALONE = ExecutionContext(
    mode="standalone", run_id=None, phase_id=None, issue_key=None
)


def get_execution_context(issue_key: str) -> ExecutionContext:
    """Return ExecutionContext for *issue_key*. Fail-open to standalone (RAISE-10966).

    Uses ``run_sync`` (RAISE-15201) — safe from both sync (CLI) and async
    (MCP server) callers without raising ``RuntimeError`` under an active loop.
    Uses ``ACTIVE_RUN_STATUSES`` as the sole source of what constitutes an
    active run.
    """
    try:
        from raise_cli.adapters.sync import run_sync  # noqa: PLC0415

        store = get_run_store()
        runs: list[dict[str, object]] = run_sync(store.list_runs())
        for r in runs:
            if (
                str(r.get("issue_id", "")) == issue_key
                and str(r.get("status", "")) in ACTIVE_RUN_STATUSES
            ):
                return ExecutionContext(
                    mode="pipeline",
                    run_id=str(r["run_id"]),
                    phase_id=_extract_phase_id(r),
                    issue_key=issue_key,
                )
        return _STANDALONE
    except Exception:  # noqa: BLE001 — fail-open per RAISE-10966
        _log.debug(
            "get_execution_context: store unavailable — fail-open", exc_info=True
        )
        return _STANDALONE


def any_pipeline_run_active() -> bool:
    """Return True if any run with an active status exists (global check).

    Used by the batch-transition guard via ``hooks.pipeline_run_active``.
    Fail-open per RAISE-10966: returns False when the store is unavailable
    or raises any exception.
    """
    try:
        from raise_cli.adapters.sync import run_sync  # noqa: PLC0415

        store = get_run_store()
        runs: list[dict[str, object]] = run_sync(store.list_runs())
        return any(str(r.get("status", "")) in ACTIVE_RUN_STATUSES for r in runs)
    except Exception:  # noqa: BLE001 — fail-open per RAISE-10966
        _log.debug(
            "any_pipeline_run_active: store unavailable — fail-open", exc_info=True
        )
        return False


def _extract_phase_id(run: dict[str, object]) -> str | None:
    """Best-effort current phase ID from a raw run dict. Returns None on any failure.

    For active runs, ``paused_at_phase`` is always None.
    The current phase comes from ``phases`` (dict or list) indexed by
    ``current_phase_index`` (int).
    """
    try:
        phases = run.get("phases", {})
        idx = int(run.get("current_phase_index", 0))  # type: ignore[arg-type]
        if isinstance(phases, dict):
            keys = list(phases.keys())
            if 0 <= idx < len(keys):
                return str(keys[idx])
        elif isinstance(phases, list) and 0 <= idx < len(phases):
            entry = phases[idx]
            if isinstance(entry, dict):
                return str(entry.get("phase_id") or entry.get("id") or "")
    except Exception:  # noqa: BLE001, S110
        pass
    return None
