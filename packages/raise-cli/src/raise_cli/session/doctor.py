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
import subprocess
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
        findings.extend(self._check_network())

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
        """Check for zombie active-session pointers across all agents."""
        findings: list[Finding] = []
        pointers = read_all_active_sessions(project_root=self._project)
        if not pointers:
            return findings

        for pointer in pointers:
            age_hours = (
                datetime.now(UTC) - pointer.started.replace(tzinfo=UTC)
            ).total_seconds() / 3600

            if age_hours <= self._max_zombie_hours:
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

            agent_tag = (
                f" [agent={pointer.cc_session_id}]" if pointer.cc_session_id else ""
            )
            extra = {"cc_session_id": pointer.cc_session_id}

            if has_narrative:
                findings.append(
                    Finding(
                        category="zombie",
                        severity="warning",
                        description=f"Zombie session: {pointer.id} ({age_hours:.0f}h old){agent_tag}",
                        detail=f'Has narrative content: "{narrative_preview}..."',
                        safe_to_auto_clean=False,
                        action="Review narrative before cleaning",
                        extra=extra,
                    )
                )
            elif commit := self._latest_commit_since(pointer.started):
                findings.append(
                    Finding(
                        category="zombie",
                        severity="warning",
                        description=f"Zombie session: {pointer.id} ({age_hours:.0f}h old){agent_tag}",
                        detail=f"Has git commit since session start: {commit}",
                        safe_to_auto_clean=False,
                        action="Review commit activity before cleaning",
                        extra=extra,
                    )
                )
            else:
                findings.append(
                    Finding(
                        category="zombie",
                        severity="warning",
                        description=f"Zombie session: {pointer.id} ({age_hours:.0f}h old){agent_tag}",
                        detail=f"{pointer.id} — no content to preserve",
                        safe_to_auto_clean=True,
                        action="Clear stale pointer",
                        extra=extra,
                    )
                )

        return findings

    def _latest_commit_since(self, started: datetime) -> str | None:
        """Return one commit made after a session started, if git is available."""
        cutoff = started.replace(tzinfo=UTC).isoformat()
        try:
            result = subprocess.run(
                ["git", "log", "--format=%h", "--max-count=1", f"--after={cutoff}"],
                cwd=self._project,
                capture_output=True,
                check=False,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None

        commit = result.stdout.strip()
        return commit if result.returncode == 0 and commit else None

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

    def _personal_dir(self) -> Path:
        """Resolve the personal dir for this project."""
        return get_personal_dir(self._project)


_SEVERITY_ICON = {"info": "i", "warning": "!", "error": "X"}


def format_findings(findings: list[Finding], cleaned: list[str]) -> str:
    """Format doctor findings for CLI output.

    Args:
        findings: All findings from diagnose().
        cleaned: Descriptions of items that were auto-cleaned.

    Returns:
        Human-readable string for CLI display.
    """
    if not findings:
        return "Session health: clean (0 issues)"

    lines: list[str] = []
    lines.append(f"Session Doctor — {len(findings)} finding(s):")
    lines.append("")

    for f in findings:
        icon = _SEVERITY_ICON.get(f.severity, "?")
        lines.append(f"  [{icon}] {f.description}")
        lines.append(f"      {f.detail}")
        lines.append(f"      Action: {f.action}")
        lines.append("")

    if cleaned:
        lines.append("Auto-cleaned:")
        for c in cleaned:
            lines.append(f"  - {c}")
        lines.append("")

    return "\n".join(lines)
