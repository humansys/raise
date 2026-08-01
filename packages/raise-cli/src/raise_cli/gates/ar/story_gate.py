"""ArchitectureReviewGate — guards story close with mandatory AR confirmation.

The gate verifies a session-scoped marker file written by /rai-story-review
after the P1/P2/P3 checklist (RAISE-14277 / ADR-130: attestation and
verification must not be the same actor at the same instant — /rai-story-close
only checks the marker, it never writes or removes it). Using
RAISE_AGENT_SESSION_ID (or RAISE_CC_SESSION_ID fallback) for scoping prevents
concurrent sessions sharing state.

Architecture: S2100.2, ADR-039 §1 (WorkflowGate Protocol)
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.git.branch_guard import current_branch

_log = logging.getLogger(__name__)

_SKIP_ENV: str = "RAISE_AR_SKIP_REASON"
_MARKER_NAME: str = "ar-reviewed"
_UNSAFE_RUN: re.Pattern[str] = re.compile(r"[^a-zA-Z0-9\-]+")
_SKIP_LOG_PATH: str = "governance/ar-skip-log.jsonl"


def _safe_segment(raw: str) -> str:
    """Sanitize a path segment: collapse disallowed-char runs to one ``-``.

    Generalizes the former ``_SAFE_SESSION_ID`` (which removed disallowed
    chars entirely) into a single formula shared by both the session-id and
    branch segments (RAISE-14326 Open Question #2 — one sanitizer, no second
    formula to drift from this one). Runs of disallowed characters collapse
    to a single hyphen and leading/trailing hyphens are stripped, so:

    - ``"../../evil"`` -> ``"evil"`` (leading run stripped) — preserves the
      exact session-id sanitization the pre-existing regression tests pin.
    - ``"story/s14262.6/x"`` -> ``"story-s14262-6-x"`` (internal runs become
      single separators) — the branch-segment shape this story adds.
    """
    return _UNSAFE_RUN.sub("-", raw).strip("-")


def _marker_path(working_dir: Path, session_id: str | None = None) -> Path | None:
    """Return branch-and-session-scoped marker path, or None with no session ID.

    ``session_id`` (RAISE-12207) is an explicit override from the gate
    context — used when the gate runs out-of-band from the agent's env (the
    in-process MCP emit), where ambient discovery would resolve the wrong/no
    session. When unset, falls back to ambient discovery (env vars).

    The resolved session ID and branch name are both sanitized (path
    traversal via env var/session-id injection, and to keep the branch
    segment filesystem-safe). When the branch cannot be resolved (no git /
    detached HEAD), falls back to the pre-RAISE-14326 session-only path —
    advisory only (a warning is logged; this does not change the gate's
    pass/fail shape), since isolation is lost only in that edge case
    (RAISE-14326 Open Question #3).
    """
    raw_id = discover_agent_session_id(override=session_id)
    if not raw_id:
        return None
    session_id = _safe_segment(raw_id)
    if not session_id:
        return None

    branch = current_branch(working_dir)
    if not branch:
        _log.warning(
            "AR marker falling back to session-only scope (no git branch "
            "resolved at %s) — cross-story marker isolation is not "
            "guaranteed in this context.",
            working_dir,
        )
        return working_dir / ".raise" / "rai" / "sessions" / session_id / _MARKER_NAME

    branch_segment = _safe_segment(branch)
    if not branch_segment:
        _log.warning(
            "AR marker falling back to session-only scope (branch name %r "
            "sanitized to empty) at %s.",
            branch,
            working_dir,
        )
        return working_dir / ".raise" / "rai" / "sessions" / session_id / _MARKER_NAME

    return (
        working_dir
        / ".raise"
        / "rai"
        / "sessions"
        / session_id
        / branch_segment
        / _MARKER_NAME
    )


def marker_path(working_dir: Path, session_id: str | None = None) -> Path | None:
    """Public accessor for the AR marker path (D1, RAISE-14326).

    Thin wrapper over ``_marker_path`` so cross-module callers (``rai gate
    ar-attest`` in ``cli/commands/gate.py``) do not reach into a private
    symbol (pyright ``reportPrivateUsage``) — the writer and this module's
    own checker still resolve through the exact same formula. ``session_id``
    (RAISE-12207) threads an out-of-band override through to ``_marker_path``.
    """
    return _marker_path(working_dir, session_id)


def _persist_ar_skip(working_dir: Path, gate_id: str, reason: str) -> None:
    """Append an auditable record of AR-skip escape-hatch usage.

    RAISE-14278: the skip must not be a silent, ephemeral env-var bypass. It
    is appended to a governance artifact meant to be committed with the
    story's changes, so bypassing the architecture-review gate leaves a
    trail reviewable in the MR — not just a var set in the agent's shell.
    Fails open (never raises): a write failure must not turn an intentional
    skip into a crash.
    """
    log_path = working_dir / _SKIP_LOG_PATH
    record = {
        "gate_id": gate_id,
        "reason": reason,
        "session_id": discover_agent_session_id() or "unknown",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        _log.warning("Failed to persist AR-skip record to %s", log_path)


def _emit_ar_skip_signal(working_dir: Path, gate_id: str, reason: str) -> None:
    """Emit a queryable WorkLifecycle ``ar-skip`` signal for the escape hatch.

    RAISE-15391: ``_persist_ar_skip`` leaves a committed jsonl trail, but that
    trail is invisible to the observability plane (``rai signal query`` / Lean
    flow analytics) — a gate bypass could not be surfaced without reading the
    file. This sibling emits a first-class ``ar-skip`` event so the bypass is
    queryable like any other lifecycle event.

    Emitting from gate code (not skill text) is deliberate: RAISE-15346 found
    that agent-side enforcement in skill text is auto-neutralizable. This fires
    for BOTH ``gate-ar-story`` and ``gate-ar-bugfix`` (shared ``evaluate``) and
    cannot be removed by editing a skill. Fails open (never raises): a telemetry
    failure must not turn an intentional skip into a crash.
    """
    try:
        from raise_cli.telemetry.emitter import emit
        from raise_cli.telemetry.schemas import WorkLifecycle

        work_type = "bugfix" if gate_id.endswith("bugfix") else "story"
        branch = current_branch(working_dir)
        emit(
            WorkLifecycle(
                timestamp=datetime.now(UTC),
                work_type=work_type,
                work_id=branch or "unknown",
                event="ar-skip",
                phase="close",
                blocker=f"{gate_id}: {reason}",
                branch=branch,
                agent_session_id=discover_agent_session_id(),
            )
        )
    except Exception:  # noqa: BLE001
        _log.warning("Failed to emit AR-skip WorkLifecycle signal for %s", gate_id)


class ArchitectureReviewGate:
    """Quality gate confirming architecture review before story close.

    Registered via ``rai.gates`` entry point. Appears in ``rai gate list``.

    Escape hatch: set ``RAISE_AR_SKIP_REASON=<reason>`` to bypass with a
    logged warning — required for XS/docs/tooling stories with no code changes.
    """

    gate_id: ClassVar[str] = "gate-ar-story"
    description: ClassVar[str] = "Architecture review confirmed before story close"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check AR confirmation via session-scoped marker or escape hatch.

        Enforces only when invoked at this gate's own ``workflow_point`` (a
        direct ``rai gate check {gate_id}`` — as the close skills do — or
        ``rai gate check --point before:*:close``). Under a blanket sweep
        (``rai gate check --all``, ``workflow_point=None``) the gate skips with a
        clear reason instead of failing, so it does not pollute a health check.
        """
        if context.workflow_point != self.workflow_point:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"skipped: AR enforced at {self.workflow_point}, "
                    "not in this context"
                ),
            )

        skip_reason = os.environ.get(_SKIP_ENV)
        if skip_reason:
            _log.warning(
                "AR gate %s SKIPPED via %s: %s",
                self.gate_id,
                _SKIP_ENV,
                skip_reason,
            )
            _persist_ar_skip(context.working_dir, self.gate_id, skip_reason)
            _emit_ar_skip_signal(context.working_dir, self.gate_id, skip_reason)
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"AR SKIPPED: {skip_reason}",
                details=(
                    f"Escape hatch {_SKIP_ENV} used — recorded in "
                    f"{_SKIP_LOG_PATH} for MR review.",
                ),
            )

        marker = _marker_path(context.working_dir, context.session_id)
        if marker is None:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"No session context — set {_SKIP_ENV}=<reason> for CI",
            )

        if marker.exists():
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="Architecture review confirmed",
            )

        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="Architecture review not confirmed — run AR checklist first",
            details=(
                "P1: rai drift check packages/<module>/",
                "P2: Beck-R2 — necessary complexity only?",
                "P3: conventions consistent?",
                "Then: complete the checklist in the review phase that owns "
                "this marker (it writes the attestation) — this gate only "
                f"verifies. Rerun: rai gate check {self.gate_id}",
                f"Escape: {_SKIP_ENV}=<reason> rai gate check {self.gate_id}",
            ),
        )
