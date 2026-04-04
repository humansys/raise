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
import time
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from raise_cli.config.paths import get_personal_dir
from raise_cli.session.index import clear_active_session, read_active_session

logger = logging.getLogger(__name__)


class Finding(BaseModel, frozen=True):
    """A single diagnostic finding from the Session Doctor.

    Attributes:
        category: Issue type — zombie, stale_output, retention, derivation.
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
        max_dirs: Maximum session directories to retain.
        max_output_hours: Hours before session-output.yaml is stale.
    """

    def __init__(
        self,
        project: Path,
        max_zombie_hours: int = 48,
        max_dirs: int = 20,
        max_output_hours: int = 24,
    ) -> None:
        self._project = project
        self._max_zombie_hours = max_zombie_hours
        self._max_dirs = max_dirs
        self._max_output_hours = max_output_hours

    def diagnose(self) -> list[Finding]:
        """Scan for session issues — no side effects.

        Checks:
        1. Zombie active-session pointer (>max_zombie_hours)
        2. Stale session-output.yaml (>max_output_hours)
        3. Session dirs beyond retention limit (>max_dirs)

        Returns:
            List of findings, empty if healthy.
        """
        findings: list[Finding] = []

        personal = self._personal_dir()
        if not personal.is_dir():
            return findings

        findings.extend(self._check_zombie(personal))
        findings.extend(self._check_stale_output(personal))
        findings.extend(self._check_retention(personal))

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
            elif f.severity == "info":
                info_only.append(f)
            else:
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
            clear_active_session(project_root=self._project)
            logger.info("Doctor: cleared zombie session pointer")
            return f"Cleared zombie pointer: {finding.detail}"

        if finding.category == "stale_output":
            output = self._personal_dir() / "session-output.yaml"
            if output.exists():
                output.unlink()
                logger.info("Doctor: removed stale session-output.yaml")
                return "Removed stale session-output.yaml"

        if finding.category == "retention":
            cleaned = self._execute_retention()
            if cleaned:
                return f"Removed {len(cleaned)} old session dirs"

        return None

    def _execute_retention(self) -> list[str]:
        """Remove oldest session dirs beyond retention limit."""
        import shutil

        cleaned: list[str] = []
        sessions_dir = self._personal_dir() / "sessions"
        if not sessions_dir.is_dir():
            return cleaned

        dirs = sorted(
            (d for d in sessions_dir.iterdir() if d.is_dir()),
            key=lambda d: d.stat().st_mtime,
        )

        if len(dirs) <= self._max_dirs:
            return cleaned

        to_remove = dirs[: len(dirs) - self._max_dirs]
        for d in to_remove:
            try:
                shutil.rmtree(d)
                cleaned.append(d.name)
                logger.info("Doctor: removed session dir %s", d.name)
            except OSError as exc:
                logger.warning("Doctor: failed to remove %s: %s", d.name, exc)

        return cleaned

    # --- Detection helpers (no side effects) ---

    def _check_zombie(self, personal: Path) -> list[Finding]:
        """Check for zombie active-session pointer."""
        findings: list[Finding] = []
        pointer = read_active_session(project_root=self._project)
        if pointer is None:
            return findings

        age_hours = (
            datetime.now(UTC) - pointer.started.replace(tzinfo=UTC)
        ).total_seconds() / 3600

        if age_hours <= self._max_zombie_hours:
            return findings

        # Check if session dir has content worth preserving
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
                    description=f"Zombie session: {pointer.id} ({age_hours:.0f}h old)",
                    detail=f"Has narrative content: \"{narrative_preview}...\"",
                    safe_to_auto_clean=False,
                    action="Review narrative before cleaning",
                )
            )
        else:
            findings.append(
                Finding(
                    category="zombie",
                    severity="warning",
                    description=f"Zombie session: {pointer.id} ({age_hours:.0f}h old)",
                    detail=f"{pointer.id} — no content to preserve",
                    safe_to_auto_clean=True,
                    action="Clear stale pointer",
                )
            )

        return findings

    def _check_stale_output(self, personal: Path) -> list[Finding]:
        """Check for stale session-output.yaml."""
        findings: list[Finding] = []
        output = personal / "session-output.yaml"
        if not output.exists():
            return findings

        age_hours = (time.time() - output.stat().st_mtime) / 3600
        if age_hours <= self._max_output_hours:
            return findings

        size_kb = output.stat().st_size / 1024

        findings.append(
            Finding(
                category="stale_output",
                severity="info",
                description=f"Stale session-output.yaml ({age_hours:.0f}h old)",
                detail=f"{size_kb:.1f} KB — safe to remove",
                safe_to_auto_clean=True,
                action="Remove stale output file",
            )
        )

        return findings

    def _check_retention(self, personal: Path) -> list[Finding]:
        """Check session directory count against retention limit."""
        findings: list[Finding] = []
        sessions_dir = personal / "sessions"
        if not sessions_dir.is_dir():
            return findings

        dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
        count = len(dirs)

        if count <= self._max_dirs:
            return findings

        excess = count - self._max_dirs
        findings.append(
            Finding(
                category="retention",
                severity="info",
                description=f"Session dirs exceed limit: {count}/{self._max_dirs}",
                detail=f"{count} dirs — {excess} would be removed to reach limit",
                safe_to_auto_clean=False,
                action=f"Remove {excess} oldest session dirs",
            )
        )

        return findings

    def _personal_dir(self) -> Path:
        """Resolve the personal dir for this project."""
        return get_personal_dir(self._project)
