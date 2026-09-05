"""Session Doctor — diagnose, classify, and safely clean session issues.

Replaces silent gc() with an informed consent model:
1. diagnose() — detect issues without side effects
2. classify() — separate safe-to-clean from needs-consent
3. execute() — only clean what was explicitly authorized

Principle: Never destroy user data without informed consent.

Architecture: E1248 (Git-First Session State), S1248.5
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from raise_cli.config.paths import get_personal_dir
from raise_cli.session.catalog.source import LocalCatalogSource
from raise_cli.session.index import (
    clear_active_session,
    read_all_active_sessions,
)
from raise_cli.session.runner import (
    LivenessObservation,
    TmuxRunnerHandle,
    list_sessions,
)

logger = logging.getLogger(__name__)


class Finding(BaseModel, frozen=True):
    """A single diagnostic finding from the Session Doctor.

    Attributes:
        category: Issue type — zombie, stale_output, orphan_flat_file.
        severity: info, warning, or error.
        description: Human-readable summary.
        detail: Context — age, size, content preview.
        safe_to_auto_clean: Whether this can be cleaned without asking.
        action: Proposed action description.
    """

    category: str
    severity: str
    description: str
    detail: str
    safe_to_auto_clean: bool
    action: str
    extra: dict[str, str] = {}


class ActionPlan(BaseModel, frozen=True):
    """Categorized findings for execution.

    Attributes:
        auto_clean: Safe to clean without asking.
        needs_consent: Must ask developer before cleaning.
        info_only: No action needed — just report.
    """

    auto_clean: list[Finding]
    needs_consent: list[Finding]
    info_only: list[Finding]


class SessionDoctor:
    """Interactive session diagnostics with consent-based cleanup.

    Args:
        project: Project root path.
        max_zombie_hours: Hours before an active session is considered zombie.
        max_output_hours: Deprecated — session output is now per-session.
    """

    def __init__(
        self,
        project: Path,
        max_zombie_hours: int = 48,
        max_output_hours: int = 24,
    ) -> None:
        self._project = project
        self._max_zombie_hours = max_zombie_hours
        self._max_output_hours = max_output_hours

    def diagnose(self) -> list[Finding]:
        """Scan for session issues — no side effects.

        Checks:
        1. Zombie active-session pointer (>max_zombie_hours)
        2. Orphan flat session-state.yaml
        3. OrphanProjection: exited runtime_sessions rows with live tmux

        Returns:
            List of findings, empty if healthy.
        """
        findings: list[Finding] = []

        personal = self._personal_dir()
        if personal.is_dir():
            findings.extend(self._check_zombie(personal))
            findings.extend(self._check_orphan_flat_file(personal))

        findings.extend(self._check_orphan_tmux())
        findings.extend(self._check_orphan_runtime())
        findings.extend(self._check_abandoned_runs())
        findings.extend(self._check_network())
        findings.extend(self._check_cartridge_instances())

        return findings

    def classify(self, findings: list[Finding]) -> ActionPlan:
        """Separate findings by risk level.

        Args:
            findings: Output from diagnose().

        Returns:
            ActionPlan with auto_clean, needs_consent, info_only lists.
        """
        auto_clean: list[Finding] = []
        needs_consent: list[Finding] = []
        info_only: list[Finding] = []

        for f in findings:
            if f.safe_to_auto_clean:
                auto_clean.append(f)
            else:
                # Not safe to auto-clean → needs explicit consent
                needs_consent.append(f)

        return ActionPlan(
            auto_clean=auto_clean,
            needs_consent=needs_consent,
            info_only=info_only,
        )

    def execute(self, plan: ActionPlan, consent: set[str]) -> list[str]:
        """Execute cleanup — only authorized items.

        Args:
            plan: Output from classify().
            consent: Set of authorized categories or "auto" for auto-clean items.

        Returns:
            List of cleaned item descriptions.
        """
        cleaned: list[str] = []

        # Auto-clean items run when "auto" is in consent
        if "auto" in consent:
            for finding in plan.auto_clean:
                result = self._execute_finding(finding)
                if result:
                    cleaned.append(result)

        # Consented categories
        for finding in plan.auto_clean:
            if finding.category in consent and "auto" not in consent:
                result = self._execute_finding(finding)
                if result:
                    cleaned.append(result)

        for finding in plan.needs_consent:
            if finding.category in consent:
                result = self._execute_finding(finding)
                if result:
                    cleaned.append(result)

        return cleaned

    def _execute_finding(self, finding: Finding) -> str | None:
        """Execute a single finding's cleanup action.

        Returns description of what was cleaned, or None if nothing done.
        """
        if finding.category == "zombie":
            cc_sid = finding.extra.get("cc_session_id", "")
            clear_active_session(project_root=self._project, cc_session_id=cc_sid)
            logger.info("Doctor: cleared zombie session pointer (agent=%s)", cc_sid)
            return f"Cleared zombie pointer: {finding.detail}"

        if finding.category == "orphan_tmux":
            from raise_cli.session.runner import kill_session

            if kill_session(finding.detail):
                logger.info("Doctor: killed orphan tmux session %s", finding.detail)
                return f"Killed orphan tmux session: {finding.detail}"
            return None

        return None

    # --- Detection helpers (no side effects) ---

    def _check_zombie(self, personal: Path) -> list[Finding]:
        """Check for zombie active-session pointers using liveness, not just age.

        Decision tree (RAISE-16740):
        - ALIVE  → skip (not zombie, regardless of age)
        - DEAD   → zombie (confirmed dead, classify by content)
        - UNKNOWN + old → stale_session (advisory, D5 consistency)
        - UNKNOWN + young → skip
        """
        findings: list[Finding] = []
        pointers = read_all_active_sessions(project_root=self._project)
        if not pointers:
            return findings

        for pointer in pointers:
            age_hours = (
                datetime.now(UTC) - pointer.started.replace(tzinfo=UTC)
            ).total_seconds() / 3600

            handle = TmuxRunnerHandle(session_id=pointer.id)
            liveness = handle.check_liveness()

            agent_tag = (
                f" [agent={pointer.cc_session_id}]" if pointer.cc_session_id else ""
            )
            extra = {"cc_session_id": pointer.cc_session_id}

            if liveness == LivenessObservation.ALIVE:
                continue

            if liveness == LivenessObservation.UNKNOWN:
                if age_hours <= self._max_zombie_hours:
                    continue
                findings.append(
                    Finding(
                        category="stale_session",
                        severity="warning",
                        description=(
                            f"Unclosed session: {pointer.id}"
                            f" ({age_hours:.0f}h old){agent_tag}"
                        ),
                        detail=(
                            "Liveness unknown — cannot confirm dead."
                            " Review and close if no longer needed."
                        ),
                        safe_to_auto_clean=False,
                        action="Review session and close if finished",
                        extra=extra,
                    )
                )
                continue

            session_dir = personal / "sessions" / pointer.id
            has_narrative = False
            narrative_preview = ""

            if session_dir.is_dir():
                narrative_file = session_dir / "narrative.md"
                if narrative_file.exists():
                    content = narrative_file.read_text().strip()
                    if content:
                        has_narrative = True
                        narrative_preview = content[:100]

            if has_narrative:
                findings.append(
                    Finding(
                        category="zombie",
                        severity="warning",
                        description=(
                            f"Dead session: {pointer.id}"
                            f" ({age_hours:.0f}h old){agent_tag}"
                        ),
                        detail=f'Has narrative content: "{narrative_preview}..."',
                        safe_to_auto_clean=False,
                        action="Review narrative before cleaning",
                        extra=extra,
                    )
                )
            else:
                findings.append(
                    Finding(
                        category="zombie",
                        severity="warning",
                        description=(
                            f"Dead session: {pointer.id}"
                            f" ({age_hours:.0f}h old){agent_tag}"
                        ),
                        detail=f"{pointer.id} — no content to preserve",
                        safe_to_auto_clean=True,
                        action="Clear stale pointer",
                        extra=extra,
                    )
                )

        return findings

    def _check_orphan_flat_file(self, personal: Path) -> list[Finding]:
        """Check for orphan flat session-state.yaml alongside per-session dirs.

        A flat file is only orphan when per-session directories also exist,
        indicating the project has migrated to per-session layout. A flat
        file alone (no sessions/ dir or empty) is a fresh install, not orphan.
        """
        findings: list[Finding] = []
        flat_file = personal / "session-state.yaml"
        if not flat_file.exists():
            return findings

        sessions_dir = personal / "sessions"
        if not sessions_dir.is_dir():
            return findings

        # Check if there are actual session dirs (not just the directory)
        session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
        if not session_dirs:
            return findings

        findings.append(
            Finding(
                category="orphan_flat_file",
                severity="info",
                description="Orphan flat session-state.yaml found",
                detail=(
                    f"Flat file exists alongside {len(session_dirs)} per-session dirs. "
                    "This file is no longer updated by session close."
                ),
                safe_to_auto_clean=False,
                action="Run session close to migrate, or manually remove the flat file",
            )
        )

        return findings

    def _active_session_ids(self) -> set[str]:
        """Return IDs of all currently active sessions."""
        pointers = read_all_active_sessions(project_root=self._project)
        return {p.id for p in pointers}

    def _check_orphan_tmux(self) -> list[Finding]:
        """Check for tmux sessions with rai- prefix that have no active session pointer."""
        tmux_sessions = list_sessions()
        if not tmux_sessions:
            return []

        active_ids = self._active_session_ids()
        findings: list[Finding] = []

        for ts in tmux_sessions:
            if ts.session_id not in active_ids:
                findings.append(
                    Finding(
                        category="orphan_tmux",
                        severity="warning",
                        description=f"Orphan tmux session: {ts.name}",
                        detail=ts.session_id,
                        safe_to_auto_clean=True,
                        action=f"Kill tmux session: tmux kill-session -t {ts.name}",
                    )
                )

        return findings

    def _check_orphan_runtime(self) -> list[Finding]:
        """Report exited runtime_sessions rows whose tmux session is still alive.

        A row is an orphan when:
        - runtime_sessions.state == 'exited' (governance closed but process lingered)
        - tmux session exists and check_liveness() returns ALIVE

        UNKNOWN liveness never triggers a finding (D5 — avoid false-positive cleanup).
        DEAD liveness means tmux is already gone — not an orphan, skip.
        """
        try:
            from raise_cli.storage.connection import get_project_db_path

            db_path = str(get_project_db_path())
            from raise_cli.session.catalog.models import CatalogFilter, SessionState

            src = LocalCatalogSource(db_path=db_path)
            result = src.query(
                CatalogFilter(
                    states=frozenset({SessionState.EXITED}),
                    limit=None,
                )
            )
        except Exception:  # noqa: BLE001 — fail-open: catalog unavailable is not an error
            logger.debug("_check_orphan_runtime: catalog query failed", exc_info=True)
            return []

        if result.error:
            logger.debug("_check_orphan_runtime: catalog error: %s", result.error)
            return []

        from raise_cli.session.catalog.models import SessionState as _SessionState

        findings: list[Finding] = []
        for rec in result.records:
            if rec.state != _SessionState.EXITED:
                continue
            handle = TmuxRunnerHandle(session_id=rec.session_id)
            liveness = handle.check_liveness()
            if liveness != LivenessObservation.ALIVE:
                continue
            findings.append(
                Finding(
                    category="orphan_runtime",
                    severity="warning",
                    description=f"Session {rec.alias} marked exited but tmux is still alive",
                    detail=rec.session_id,
                    safe_to_auto_clean=False,
                    action=f"Review or kill: rai session close --and-exit {rec.alias}@local",
                )
            )
        return findings

    def _check_abandoned_runs(self) -> list[Finding]:
        """Detect active pipeline runs whose owning session is no longer alive.

        Queries the pipeline_runs SQLite table for runs in active statuses
        (started, running, paused, gate_pending) and cross-references each
        run's agent_session_id against live sessions. Runs with a dead or
        missing session are reported as advisory findings.
        """
        active_statuses = frozenset({"started", "running", "paused", "gate_pending"})

        import json
        import sqlite3

        from raise_cli.storage.connection import get_project_db_path

        try:
            db_path = get_project_db_path()
        except Exception:  # noqa: BLE001
            logger.debug("_check_abandoned_runs: DB not available", exc_info=True)
            return []

        if not db_path.exists():
            return []

        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            placeholders = ",".join(f"'{s}'" for s in active_statuses)
            rows = conn.execute(
                f"SELECT run_id, pipeline_name, status, started_at, metadata"  # noqa: S608 # nosec B608 — placeholders are internal status literals, not user input
                f" FROM pipeline_runs WHERE status IN ({placeholders})"
            ).fetchall()
        except Exception:  # noqa: BLE001
            logger.debug("_check_abandoned_runs: query failed", exc_info=True)
            return []
        finally:
            if conn is not None:
                conn.close()

        if not rows:
            return []

        active_sessions = self._active_session_ids()
        findings: list[Finding] = []

        for row in rows:
            metadata = json.loads(row["metadata"] or "{}")
            session_id: str = metadata.get("agent_session_id", "")
            if session_id and session_id in active_sessions:
                continue

            started_raw: str = row["started_at"] or ""
            age_str = ""
            try:
                started = datetime.fromisoformat(started_raw)
                age_hours = (
                    datetime.now(UTC) - started.replace(tzinfo=UTC)
                ).total_seconds() / 3600
                age_str = f", {age_hours:.0f}h old"
            except (ValueError, TypeError):
                pass

            session_tag = f", session={session_id}" if session_id else ", no session"
            findings.append(
                Finding(
                    category="abandoned_run",
                    severity="warning",
                    description=(
                        f"Abandoned pipeline run: {row['pipeline_name']}"
                        f" [{row['status']}]"
                    ),
                    detail=f"{row['run_id']}{session_tag}{age_str}",
                    safe_to_auto_clean=False,
                    action="Review and cancel or resume: rai pipeline cancel <run_id>",
                )
            )

        return findings

    def _check_network(self) -> list[Finding]:
        """Report network availability for mobile re-entry.

        Checks:
        - Tailscale availability (preferred network for mobile)
        - LAN IP fallback

        Returns findings only when Tailscale is down (warning + LAN fallback).
        Returns an info finding when Tailscale is up.
        """
        from raise_cli.session.connect import discover_lan_ip, discover_tailscale_ip

        tailscale_ip = discover_tailscale_ip()
        lan_ip = discover_lan_ip()

        if tailscale_ip:
            return []  # Healthy state — no finding needed

        # Tailscale down — warn and report LAN fallback
        lan_detail = f"LAN fallback: {lan_ip}" if lan_ip else "No LAN IP detected"
        return [
            Finding(
                category="network",
                severity="warning",
                description="Tailscale not running — mobile QR re-entry limited",
                detail=f"{lan_detail}. Use `rai session connect --lan` for LAN-only QR.",
                safe_to_auto_clean=False,
                action="Install and start Tailscale for cross-network mobile access",
            )
        ]

    def _check_cartridge_instances(self) -> list[Finding]:
        """Check for cartridges with extractors but no built instances/ dir.

        A cartridge with extractors/config.yaml is expected to produce
        instances via `rai cartridge build`. If instances/ is missing,
        the extractors have been defined but never run — advisory only,
        this does not construct or validate the governance cartridge.
        """
        findings: list[Finding] = []
        cartridges_dir = self._project / ".raise" / "cartridges"
        if not os.path.isdir(cartridges_dir):
            return findings

        for name in sorted(os.listdir(cartridges_dir)):
            cartridge_dir = cartridges_dir / name
            if not os.path.isdir(cartridge_dir):
                continue

            extractors_config = cartridge_dir / "extractors" / "config.yaml"
            if not os.path.isfile(extractors_config):
                continue

            instances_dir = cartridge_dir / "instances"
            if os.path.isdir(instances_dir):
                continue

            findings.append(
                Finding(
                    category="cartridge-instances-missing",
                    severity="warning",
                    description=(
                        f"Cartridge '{name}' has extractors but no instances/"
                    ),
                    detail=(
                        f"{name}: extractors/config.yaml exists but "
                        "instances/ directory is missing"
                    ),
                    safe_to_auto_clean=False,
                    action=(
                        "Run `rai cartridge build` or `/rai-kc-build` "
                        f"to generate instances for '{name}'"
                    ),
                )
            )

        return findings

    def _personal_dir(self) -> Path:
        """Resolve the personal dir for this project."""
        return get_personal_dir(self._project)


_SEVERITY_ICON = {"info": "i", "warning": "!", "error": "X"}


_CATEGORY_DETAIL_CAP = 10


def format_findings(findings: list[Finding], cleaned: list[str]) -> str:
    """Format doctor findings for CLI output.

    Groups findings by category. Categories with more than
    ``_CATEGORY_DETAIL_CAP`` entries show the first N in detail and a
    one-line summary for the rest, keeping total output bounded.

    Args:
        findings: All findings from diagnose().
        cleaned: Descriptions of items that were auto-cleaned.

    Returns:
        Human-readable string for CLI display.
    """
    if not findings:
        return "Session health: clean (0 issues)"

    by_category: dict[str, list[Finding]] = {}
    for f in findings:
        by_category.setdefault(f.category, []).append(f)

    lines: list[str] = []
    lines.append(f"Session Doctor — {len(findings)} finding(s):")
    lines.append("")

    for category, group in by_category.items():
        shown = group[:_CATEGORY_DETAIL_CAP]
        for f in shown:
            icon = _SEVERITY_ICON.get(f.severity, "?")
            lines.append(f"  [{icon}] {f.description}")
            lines.append(f"      {f.detail}")
            lines.append(f"      Action: {f.action}")
            lines.append("")

        remaining = len(group) - len(shown)
        if remaining > 0:
            lines.append(
                f"  … and {remaining} more {category} finding(s) (total: {len(group)})"
            )
            action = shown[0].action
            lines.append(f"      Action (all): {action}")
            lines.append("")

    if cleaned:
        lines.append("Auto-cleaned:")
        for c in cleaned:
            lines.append(f"  - {c}")
        lines.append("")

    return "\n".join(lines)
