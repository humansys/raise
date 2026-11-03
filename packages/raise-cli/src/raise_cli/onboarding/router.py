"""Deterministic routing core for rai onboard.

Pure decision layer: observe_repository → decide_route.
No subprocess, no console output. All evidence sourced from existing
onboarding/ modules — this module only composes them.

Architecture: RAISE-16346 design §Components.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel

from raise_cli import __version__
from raise_cli.developer_profile.profile import DEVELOPER_PROFILE_FILE, get_rai_home
from raise_cli.legacy.scanner import scan_project
from raise_cli.onboarding.detection import ProjectType, detect_project_type
from raise_cli.onboarding.governance import (
    _GOVERNANCE_TEMPLATES,  # pyright: ignore[reportPrivateUsage]
)
from raise_cli.onboarding.manifest import load_manifest
from raise_cli.onboarding.skill_manifest import load_skill_manifest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Six blocking legacy kinds — subset of ResidueKind.
# Ownership (orphan-project-db etc.) NEVER blocks. This is a fixed taxonomy:
# membership must not be derived from OWNERSHIP_BY_KIND (SD4).
BLOCKING_LEGACY_KINDS: frozenset[str] = frozenset(
    {
        "path-shadowing",
        "dangling-rai-symlink",
        "global-console-script",
        "venv-prerename-pkg",
        "venv-console-script",
        "venv-renamed",
    }
)

# Scaffold markers that indicate grounding is incomplete (case-insensitive match).
_SCAFFOLD_MARKERS: tuple[str, ...] = (
    "fill with /rai-project-create",
    "fill with /rai-project-onboard",
)

# Architecture docs whose front-matter must NOT carry status: draft (SD5).
# Derived from _GOVERNANCE_TEMPLATES — never a re-typed copy.
_ARCH_DEST_PATHS: frozenset[str] = frozenset(
    dest for _, dest in _GOVERNANCE_TEMPLATES if dest.startswith("architecture/")
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class RouteKind(StrEnum):
    """Enumeration of onboarding routes (priority order)."""

    NEW_USER = "new_user"
    LEGACY_CONFLICT = "legacy_conflict"
    INVALID_PROJECT = "invalid_project"
    BROWNFIELD = "brownfield"
    GREENFIELD = "greenfield"
    UPGRADE = "upgrade"
    GROUNDING_REQUIRED = "grounding_required"
    READY = "ready"


class RepositorySignals(BaseModel):
    """Observed repository state used as input to decide_route.

    Attributes:
        raise_dir_exists: Whether .raise/ directory is present.
        manifest_valid: Whether load_manifest returned a valid manifest.
        project_type: From manifest when valid, else from detect_project_type.
        blocking_legacy_kinds: Subset of BLOCKING_LEGACY_KINDS found by scan.
        skill_manifest_current: False when upgrade is needed.
        grounding_complete: Whether all governance files are in final form.
        developer_profile_exists: Whether ~/.rai/developer.yaml is present.
            Defaults to True for backward compatibility with callers that do
            not yet supply this field. Set to False when the file is absent
            so decide_route can emit the NEW_USER route (RAISE-17236).
    """

    raise_dir_exists: bool
    manifest_valid: bool
    project_type: ProjectType | None
    blocking_legacy_kinds: tuple[str, ...]
    skill_manifest_current: bool
    grounding_complete: bool
    developer_profile_exists: bool = True


class OnboardDecision(BaseModel):
    """Routing decision output from decide_route.

    Attributes:
        route: Classification of the current state.
        detected: Rendered "Detected:" label for the transcript.
        operation: Child argv AFTER the self-invocation prefix, or None.
        action: Rendered "Action:" label (happy path; executor updates on failure).
        next_step: Single command or skill name for the "Next:" label.
        exit_code: Intended process exit code.
    """

    route: RouteKind
    detected: str
    operation: tuple[str, ...] | None
    action: str
    next_step: str
    exit_code: int


# ---------------------------------------------------------------------------
# Predicates
# ---------------------------------------------------------------------------


def is_skill_manifest_current(root: Path) -> bool:
    """Return True when skills.json exists, is schema-valid, and version matches.

    Collapses missing + invalid-JSON + schema-invalid → False,
    matching the same observable as _maybe_auto_upgrade (session.py:744).
    """
    sm = load_skill_manifest(root)
    if sm is None:
        return False
    return sm.raise_cli_version == __version__


def _has_draft_status(path: Path) -> bool:
    """Return True if the file's YAML front-matter contains status: draft."""
    if not path.exists():
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    if not content.startswith("---"):
        return False
    end = content.find("---", 3)
    if end == -1:
        return False
    front_matter_text = content[3:end]
    try:
        data = yaml.safe_load(front_matter_text)
        if isinstance(data, dict):
            return str(data.get("status", "")).lower() == "draft"
    except yaml.YAMLError:
        pass
    return False


def is_grounding_complete(root: Path) -> bool:
    """Return True when the governance scaffold is syntactically complete.

    Three conditions must all hold:
    1. All seven _GOVERNANCE_TEMPLATES dest paths exist under governance/.
    2. None of them contains a scaffold marker (case-insensitive).
    3. None of the three architecture/*.md docs has front-matter status: draft.
    """
    gov_dir = root / "governance"
    for _, dest_rel in _GOVERNANCE_TEMPLATES:
        dest = gov_dir / dest_rel
        if not dest.exists():
            return False
        try:
            content = dest.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False
        for marker in _SCAFFOLD_MARKERS:
            if marker.lower() in content.lower():
                return False

    # Architecture docs: check for draft front-matter
    for _, dest_rel in _GOVERNANCE_TEMPLATES:
        if dest_rel in _ARCH_DEST_PATHS:
            dest = gov_dir / dest_rel
            if _has_draft_status(dest):
                return False

    return True


# ---------------------------------------------------------------------------
# Core observe/decide functions
# ---------------------------------------------------------------------------


def observe_repository(root: Path) -> RepositorySignals:
    """Observe current repository state — all IO in one place.

    Composes five existing evidence sources without reimplementing them.
    """
    # Blocking legacy residues
    report = scan_project(root)
    blocking = tuple(r.kind for r in report.residues if r.kind in BLOCKING_LEGACY_KINDS)

    # .raise/ directory
    raise_dir_exists = (root / ".raise").is_dir()

    # Manifest
    manifest = load_manifest(root)
    manifest_valid = manifest is not None

    # Project type: manifest-recorded when valid, detected otherwise
    project_type: ProjectType | None
    if manifest is not None:
        project_type = manifest.project.project_type
    else:
        project_type = detect_project_type(root).project_type

    # Upgrade predicate
    skill_manifest_current = is_skill_manifest_current(root)

    # Grounding predicate
    grounding = is_grounding_complete(root)

    developer_profile_exists = (get_rai_home() / DEVELOPER_PROFILE_FILE).exists()

    return RepositorySignals(
        raise_dir_exists=raise_dir_exists,
        manifest_valid=manifest_valid,
        project_type=project_type,
        blocking_legacy_kinds=blocking,
        skill_manifest_current=skill_manifest_current,
        grounding_complete=grounding,
        developer_profile_exists=developer_profile_exists,
    )


def decide_route(signals: RepositorySignals) -> OnboardDecision:
    """Pure decision function — first-match-wins on the seven-row route table.

    No IO. Callers supply pre-observed RepositorySignals.
    """
    # P0: New user — no developer profile
    if not signals.developer_profile_exists:
        return OnboardDecision(
            route=RouteKind.NEW_USER,
            detected="no developer profile found (first run)",
            operation=None,
            action="no-op",
            next_step="/rai-welcome",
            exit_code=0,
        )

    # P1: Blocking legacy conflict
    if signals.blocking_legacy_kinds:
        kind = signals.blocking_legacy_kinds[0]
        return OnboardDecision(
            route=RouteKind.LEGACY_CONFLICT,
            detected=f"conflicting legacy installation ({kind})",
            operation=None,
            action="blocked — no changes made",
            next_step="rai clean --dry-run",
            exit_code=1,
        )

    # P2: .raise/ exists but manifest is invalid or missing
    if signals.raise_dir_exists and not signals.manifest_valid:
        return OnboardDecision(
            route=RouteKind.INVALID_PROJECT,
            detected=(
                "RaiSE project directory exists but manifest is invalid or missing"
            ),
            operation=None,
            action="blocked — no changes made",
            next_step="rai manifest validate",
            exit_code=1,
        )

    # P3/P4: No .raise/ directory — init required
    if not signals.raise_dir_exists:
        if signals.project_type == ProjectType.BROWNFIELD:
            return OnboardDecision(
                route=RouteKind.BROWNFIELD,
                detected="no RaiSE project; source code detected (brownfield)",
                operation=("init", "--detect", "--yes", "--apply"),
                action="ran rai init --detect --yes --apply",
                next_step="/rai-project-onboard",
                exit_code=0,
            )
        return OnboardDecision(
            route=RouteKind.GREENFIELD,
            detected="no RaiSE project; no source code (greenfield)",
            operation=("init", "--yes", "--apply"),
            action="ran rai init --yes --apply",
            next_step="/rai-project-create",
            exit_code=0,
        )

    # P5: Valid manifest, upgrade required
    if not signals.skill_manifest_current:
        return OnboardDecision(
            route=RouteKind.UPGRADE,
            detected="RaiSE project found; upgrade required",
            operation=("upgrade",),
            action="ran rai upgrade",
            next_step="/rai-session-start",
            exit_code=0,
        )

    # P6: Grounding incomplete
    if not signals.grounding_complete:
        next_step = (
            "/rai-project-onboard"
            if signals.project_type == ProjectType.BROWNFIELD
            else "/rai-project-create"
        )
        return OnboardDecision(
            route=RouteKind.GROUNDING_REQUIRED,
            detected="RaiSE project found; grounding incomplete",
            operation=None,
            action="no-op",
            next_step=next_step,
            exit_code=0,
        )

    # P7: Ready
    return OnboardDecision(
        route=RouteKind.READY,
        detected="RaiSE project found; ready to work",
        operation=None,
        action="no-op",
        next_step="/rai-session-start",
        exit_code=0,
    )
