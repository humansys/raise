"""Purge logic for reversing `rai init` — removes RaiSE-owned files/directories.

Implements a static ownership registry (D1) derived from the same constants
and scaffolding functions `rai init`/`rai upgrade` use (see
``MCP_JSON_CONTENT``, ``WORKTREEINCLUDE_CONTENT``, and
``generate_agents_md_content`` below, which ``init.py`` imports from here as
its single source of truth), combined with hash-based modification detection
(D2) for files a human could plausibly have hand-edited.

Directories that are exclusively RaiSE-managed (``.raise/``, ``governance/``)
are removed wholesale. Per-agent skill/workflow entries are matched by name
against ``DISTRIBUTABLE_SKILLS`` so mixed-content directories are handled
precisely instead of being wiped blindly.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from raise_cli.config.agent_registry import AgentRegistry, load_registry
from raise_cli.config.agents import AgentConfig
from raise_cli.onboarding.bootstrap import ENV_EXAMPLE_CONTENT
from raise_cli.onboarding.detection import DetectionResult, detect_project_type
from raise_cli.onboarding.instructions import generate_instructions
from raise_cli.onboarding.manifest import load_manifest
from raise_cli.onboarding.profile import load_developer_profile, save_developer_profile
from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

# ---------------------------------------------------------------------------
# Shared scaffolding constants (D1: init.py imports these too, so purge can
# never drift from what init actually writes).
# ---------------------------------------------------------------------------

MCP_JSON_CONTENT: dict[str, object] = {
    "mcpServers": {
        "rai-workspace": {
            "command": "rai-mcp-pipeline",
        }
    }
}

WORKTREEINCLUDE_CONTENT = (
    ".env\n"
    ".env.local\n"
    ".envrc\n"
    ".claude/settings.local.json\n"
    ".hermes/config.yaml\n"
    ".codex/\n"
    ".codex-plugin/\n"
)


def generate_agents_md_content(project_name: str, agent_types: list[str]) -> str:
    """Build the cross-tool AGENTS.md pointer file content (pure function).

    Shared by ``init._generate_agents_md`` (which writes it) and
    ``compute_dispositions`` (which regenerates it to detect edits).

    Args:
        project_name: Name of the project.
        agent_types: Configured agent types for the project.

    Returns:
        Markdown content for the project-root AGENTS.md pointer file.
    """
    if agent_types == ["claude"]:
        session_instruction = "Run `/rai-session-start` to load full context."
    else:
        session_instruction = (
            "Invoke the `rai-session-start` skill from your IDE to load full context."
        )

    return (
        f"# {project_name}\n\n"
        f"> RaiSE-governed project. {session_instruction}\n\n"
        f"## Active Agents\n\n" + "\n".join(f"- {a}" for a in agent_types) + "\n\n"
        "## Process\n\n"
        "This project follows the RaiSE methodology. "
        "See `.raise/` for governance artifacts and `rai --help` for CLI.\n"
    )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class FileDisposition(BaseModel):
    """What purge would do with a single RaiSE-owned path."""

    path: str
    action: Literal["remove", "preserve"]
    reason: str  # "unmodified", "user-modified", "rai-owned-dir"


class PurgeResult(BaseModel):
    """Outcome of executing a purge."""

    files_removed: list[str]
    files_preserved: list[FileDisposition]
    dirs_removed: list[str]
    global_cleaned: bool


# ---------------------------------------------------------------------------
# Disposition helpers
# ---------------------------------------------------------------------------


def _add_text_disposition(
    dispositions: list[FileDisposition],
    project_path: Path,
    path: Path,
    expected_content: str,
) -> None:
    """Compare a text file against its expected regenerated content."""
    if not path.is_file():
        return
    actual = path.read_text(encoding="utf-8")
    if actual == expected_content:
        action: Literal["remove", "preserve"] = "remove"
        reason = "unmodified"
    else:
        action = "preserve"
        reason = "user-modified"
    dispositions.append(
        FileDisposition(
            path=str(path.relative_to(project_path)), action=action, reason=reason
        )
    )


def _add_json_disposition(
    dispositions: list[FileDisposition],
    project_path: Path,
    path: Path,
    expected: dict[str, object],
) -> None:
    """Compare a JSON file against its expected regenerated content (structural)."""
    if not path.is_file():
        return
    try:
        actual_obj = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        actual_obj = None
    if actual_obj == expected:
        action: Literal["remove", "preserve"] = "remove"
        reason = "unmodified"
    else:
        action = "preserve"
        reason = "user-modified"
    dispositions.append(
        FileDisposition(
            path=str(path.relative_to(project_path)), action=action, reason=reason
        )
    )


def _add_owned_skill_entries(
    dispositions: list[FileDisposition],
    project_path: Path,
    skills_dir_rel: str,
    seen: set[str],
) -> None:
    """Mark rai-owned skill subdirectories for wholesale removal."""
    skills_dir = project_path / skills_dir_rel
    if not skills_dir.is_dir():
        return
    for entry in sorted(skills_dir.iterdir()):
        if entry.name not in DISTRIBUTABLE_SKILLS:
            continue
        rel = str(entry.relative_to(project_path))
        if rel in seen:
            continue
        seen.add(rel)
        dispositions.append(
            FileDisposition(path=rel, action="remove", reason="rai-owned-dir")
        )


def _add_owned_workflow_entries(
    dispositions: list[FileDisposition],
    project_path: Path,
    workflows_dir_rel: str,
    seen: set[str],
) -> None:
    """Mark rai-owned workflow shim files for removal."""
    workflows_dir = project_path / workflows_dir_rel
    if not workflows_dir.is_dir():
        return
    for skill_name in DISTRIBUTABLE_SKILLS:
        candidate = workflows_dir / f"{skill_name}.md"
        if not candidate.is_file():
            continue
        rel = str(candidate.relative_to(project_path))
        if rel in seen:
            continue
        seen.add(rel)
        dispositions.append(
            FileDisposition(path=rel, action="remove", reason="rai-owned-dir")
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _add_instructions_dispositions(
    dispositions: list[FileDisposition],
    project_path: Path,
    registry: AgentRegistry,
    agent_types: list[str],
    project_name: str,
    detection: DetectionResult,
) -> None:
    """Check the primary instructions file and the AGENTS.md pointer file.

    Only the first configured agent's instructions file is generated from
    `.raise/` sources by init/upgrade (see init.py); AGENTS.md is checked
    separately unless it *is* that primary instructions file already.
    """
    first_config: AgentConfig | None = None
    if agent_types:
        try:
            first_config = registry.get_config(agent_types[0])
        except KeyError:
            first_config = None

    if first_config is not None:
        instructions_path = project_path / first_config.instructions_file
        expected_instructions = generate_instructions(
            project_name,
            detection,
            agent_config=first_config,
            project_path=project_path,
        )
        _add_text_disposition(
            dispositions, project_path, instructions_path, expected_instructions
        )

    if first_config is None or first_config.instructions_file != "AGENTS.md":
        _add_text_disposition(
            dispositions,
            project_path,
            project_path / "AGENTS.md",
            generate_agents_md_content(project_name, agent_types),
        )


def _add_skill_and_workflow_dispositions(
    dispositions: list[FileDisposition],
    project_path: Path,
    registry: AgentRegistry,
    agent_types: list[str],
    seen: set[str],
) -> None:
    """Check per-agent skills/workflows — scaffolded for every configured agent."""
    for agent_type in agent_types:
        try:
            config = registry.get_config(agent_type)
        except KeyError:
            continue
        if config.skills_dir:
            _add_owned_skill_entries(
                dispositions, project_path, config.skills_dir, seen
            )
        if config.workflows_dir:
            _add_owned_workflow_entries(
                dispositions, project_path, config.workflows_dir, seen
            )


def compute_dispositions(project_path: Path) -> list[FileDisposition]:
    """Compute what purge would do, without writing anything.

    Walks the static ownership registry (D1) and applies hash-based
    modification detection (D2): RaiSE-owned files whose content still
    matches what `rai init`/`rai upgrade` would generate are safe to
    remove; anything that diverges (human-edited) is preserved.

    Args:
        project_path: Project root directory. Caller is responsible for
            verifying the project is actually RaiSE-initialized (i.e.
            `.raise/` exists) before calling this.

    Returns:
        List of FileDisposition entries describing every RaiSE-owned
        candidate path found and whether it will be removed or preserved.
    """
    dispositions: list[FileDisposition] = []
    seen: set[str] = set()

    manifest = load_manifest(project_path)
    agent_types = manifest.agents.types if manifest is not None else ["claude"]
    project_name = manifest.project.name if manifest is not None else project_path.name

    registry = load_registry(project_root=project_path)
    detection = detect_project_type(project_path)

    _add_instructions_dispositions(
        dispositions, project_path, registry, agent_types, project_name, detection
    )
    _add_skill_and_workflow_dispositions(
        dispositions, project_path, registry, agent_types, seen
    )

    # Top-level scaffolded files
    _add_text_disposition(
        dispositions,
        project_path,
        project_path / ".worktreeinclude",
        WORKTREEINCLUDE_CONTENT,
    )
    _add_json_disposition(
        dispositions, project_path, project_path / ".mcp.json", MCP_JSON_CONTENT
    )
    _add_text_disposition(
        dispositions,
        project_path,
        project_path / ".env.example",
        ENV_EXAMPLE_CONTENT,
    )

    # Fully RaiSE-owned directories
    for owned_dir in (project_path / ".raise", project_path / "governance"):
        if owned_dir.is_dir():
            dispositions.append(
                FileDisposition(
                    path=str(owned_dir.relative_to(project_path)),
                    action="remove",
                    reason="rai-owned-dir",
                )
            )

    return dispositions


def _prune_empty_ancestors(
    removed_paths: list[Path], project_path: Path, dirs_removed: list[str]
) -> None:
    """Remove now-empty directories left behind after removing owned paths.

    Only removes a directory that is already empty — never touches a
    directory containing anything else, RaiSE-owned or not. Walks upward
    from each removed path's parent, stopping at the project root. This
    cleans up containers like `.claude/skills/` once every rai-owned skill
    subdirectory inside it has been removed.
    """
    candidates = {p.parent for p in removed_paths}
    for start in candidates:
        current = start
        while current != project_path:
            if not current.is_dir() or any(current.iterdir()):
                break
            dirs_removed.append(str(current.relative_to(project_path)))
            current.rmdir()
            current = current.parent


def execute_purge(
    project_path: Path, dispositions: list[FileDisposition]
) -> PurgeResult:
    """Apply the given dispositions: remove owned paths, leave preserved ones untouched.

    Idempotent-safe: paths already gone (e.g. nested under a directory
    removed earlier in the list) are silently skipped. Also prunes
    directories left empty by removed files (see `_prune_empty_ancestors`).

    Args:
        project_path: Project root directory.
        dispositions: Dispositions previously computed by `compute_dispositions`.

    Returns:
        PurgeResult summarizing what was removed and preserved.
        `global_cleaned` is always False here — global cleanup is a separate
        concern handled by `clean_global_profile`.
    """
    files_removed: list[str] = []
    dirs_removed: list[str] = []
    files_preserved: list[FileDisposition] = []
    removed_paths: list[Path] = []

    for disposition in dispositions:
        if disposition.action == "preserve":
            files_preserved.append(disposition)
            continue

        target = project_path / disposition.path
        if not target.exists():
            continue

        if target.is_dir():
            shutil.rmtree(target)
            dirs_removed.append(disposition.path)
        else:
            target.unlink()
            files_removed.append(disposition.path)
        removed_paths.append(target)

    _prune_empty_ancestors(removed_paths, project_path, dirs_removed)

    return PurgeResult(
        files_removed=files_removed,
        files_preserved=files_preserved,
        dirs_removed=dirs_removed,
        global_cleaned=False,
    )


def clean_global_profile(project_path: Path) -> bool:
    """Remove this project's entry from the global developer profile.

    Only prunes the matching `projects` entry in `~/.rai/developer.yaml` —
    never deletes the profile itself, since it is shared across every
    RaiSE project the developer works on.

    Args:
        project_path: Project root directory to remove from the profile.

    Returns:
        True if an entry was removed, False if there was no profile or no
        matching entry.
    """
    profile = load_developer_profile()
    if profile is None:
        return False

    resolved = str(project_path.resolve())
    remaining = [p for p in profile.projects if str(Path(p).resolve()) != resolved]
    if len(remaining) == len(profile.projects):
        return False

    updated = profile.model_copy(update={"projects": remaining})
    save_developer_profile(updated)
    return True
