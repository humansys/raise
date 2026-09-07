"""Path helpers for raise-cli.

Includes:
- XDG Base Directory paths (global user config/cache/data)
- Per-project directory structure constants

Directory Structure (per-project):
    .raise/                    # RaiSE framework presence
    ├── manifest.yaml          # Project metadata
    ├── config.yaml            # Project configuration
    ├── graph/                 # Context graph cache
    └── rai/                   # AI partner state
        ├── identity/          # Rai's identity
        ├── memory/            # Patterns, calibration, graph (shared, committed)
        └── personal/          # Sessions, telemetry (per-developer, gitignored)
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from raise_cli.exceptions import ConfigurationError

# =============================================================================
# Git Repo Root Resolution
# =============================================================================


def resolve_repo_root() -> Path | None:
    """Return the main repo root, even when called from a linked worktree.

    Uses RAISE_PROJECT_ROOT env var first (CI / test override), then falls
    back to git resolution. git rev-parse --show-toplevel returns the worktree
    root in linked worktrees — worktree list --porcelain always lists the main
    worktree first with an absolute path.
    """
    root = os.environ.get("RAISE_PROJECT_ROOT")
    if root:
        return Path(root)
    try:
        lines = subprocess.check_output(
            ["git", "worktree", "list", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()
        match = next(
            (line.split(" ", 1)[1] for line in lines if line.startswith("worktree ")),
            None,
        )
        return Path(match) if match else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def resolve_checkout_root(cwd: Path | None = None) -> Path:
    """Return the active git checkout root for the current worktree.

    This intentionally differs from ``resolve_repo_root()`` and
    ``resolve_project_root()``: linked worktrees return the linked worktree
    path, not the main checkout/shared project identity.
    """
    effective_cwd = cwd or Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=effective_cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return effective_cwd

    checkout = result.stdout.strip()
    if result.returncode != 0 or not checkout:
        return effective_cwd
    return Path(checkout).resolve()


def checkout_scope_id(root: Path | str) -> str:
    """Return the canonical ``checkout_id`` used to scope the graph keyspace.

    ``project_id`` is repo-wide — it comes from the git-tracked
    ``.raise/manifest.yaml`` and is identical in every worktree and every clone,
    so it cannot isolate their indices (RAISE-15607). ``checkout_id`` is the
    resolved checkout root path; the empty string means "repo-wide" (cartridge
    rows shared by every checkout).

    Resolving here is load-bearing: writers and readers reach this value from
    different starting points (``resolve_checkout_root()``, an explicit
    ``project_root`` argument, a doctor root). Two spellings of the same
    directory would silently create two partitions.
    """
    text = str(root)
    if not text:
        return ""
    return str(Path(text).resolve())


# =============================================================================
# Per-Project Directory Constants
# =============================================================================

# Root directory for RaiSE in a project
RAISE_PROJECT_DIR = ".raise"

# Subdirectory for Rai (AI partner) state within .raise/
RAI_SUBDIR = "rai"

# Common subdirectories
MEMORY_SUBDIR = "memory"
TELEMETRY_SUBDIR = "telemetry"
IDENTITY_SUBDIR = "identity"
GRAPH_SUBDIR = "graph"
FRAMEWORK_SUBDIR = "framework"
MANIFESTS_SUBDIR = "manifests"
MISSIONS_SUBDIR = "missions"

# File names
SKILLS_MANIFEST_FILE = "skills.json"
MANIFEST_FILE = "manifest.yaml"
CONFIG_FILE = "config.yaml"
PATTERNS_FILE = "patterns.jsonl"  # kept for migration reference only
CALIBRATION_FILE = "calibration.jsonl"
SESSIONS_DIR = "sessions"
SIGNALS_FILE = "signals.jsonl"

# Prefix registry (committed to git under .raise/rai/)
PREFIXES_FILE = "prefixes.yaml"
# Active session pointer (gitignored, under personal/)
ACTIVE_SESSION_FILE = "active-session"

# Fitness-function promotion audit log (committed to git — a governance
# record about the repo's CI configuration, not per-developer state).
# RAISE-14679 (S14263.4). Repo-relative, unlike the SUBDIR constants above:
# the log path is assembled directly as `project_root / FITNESS_FUNCTIONS_DIR
# / PROMOTION_LOG_FILE` (see raise_cli.gates.calibration.log) rather than
# via a get_*_dir() helper, since it has exactly one caller today.
FITNESS_FUNCTIONS_DIR = ".raise/rai/fitness-functions"
PROMOTION_LOG_FILE = "promotion-log.json"


def get_raise_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/ directory for a project.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/ directory.
    """
    root = project_root or Path.cwd()
    return root / RAISE_PROJECT_DIR


def get_rai_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/ directory for AI partner state.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/rai/ directory.
    """
    return get_raise_dir(project_root) / RAI_SUBDIR


def get_missions_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/missions/ directory.

    Missions are project-shared artifacts (one YAML file per mission + an
    ``_active`` pointer). Not personal — missions are collaboration
    containers, committed to git alongside epics.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to missions directory.
    """
    return get_rai_dir(project_root) / MISSIONS_SUBDIR


def get_memory_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/memory/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to memory directory.
    """
    return get_rai_dir(project_root) / MEMORY_SUBDIR


def get_telemetry_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/personal/telemetry/ directory.

    Telemetry is personal data (developer-specific, gitignored).

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to telemetry directory.
    """
    return get_personal_dir(project_root) / TELEMETRY_SUBDIR


def get_identity_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/identity/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to identity directory.
    """
    return get_rai_dir(project_root) / IDENTITY_SUBDIR


def get_framework_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/framework/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to framework directory.
    """
    return get_rai_dir(project_root) / FRAMEWORK_SUBDIR


def get_graph_dir(project_root: Path | None = None) -> Path:
    """Get the memory index directory (.raise/rai/memory/).

    The "graph" is an implementation detail — it's really memory indexing.
    This function returns the memory directory where index.json lives.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to memory directory (contains index.json).
    """
    return get_memory_dir(project_root)


# =============================================================================
# Global User Directory (XDG)
# =============================================================================

# Global Rai directory in user home (for developer profile)
GLOBAL_RAI_DIR = ".rai"

# Personal subdirectory (gitignored, per-developer within project)
PERSONAL_SUBDIR = "personal"


def _sanitize_env_path(raw: str, var_name: str) -> Path:
    """Sanitize a path read from an environment variable (CWE-23).

    Validates that the raw value does not contain ``..`` path components
    (before resolution) and that the resolved result is absolute.

    Args:
        raw: Raw environment variable value.
        var_name: Variable name (for error messages).

    Returns:
        Resolved, absolute ``Path``.

    Raises:
        ConfigurationError: If the path contains traversal components or is not absolute.
    """
    if ".." in raw.split(os.sep):
        msg = f"${var_name} must not contain '..' path components: {raw}"
        raise ConfigurationError(msg)
    resolved = Path(raw).resolve()
    if not resolved.is_absolute():
        msg = f"${var_name} must resolve to an absolute path: {raw}"
        raise ConfigurationError(msg)
    return resolved


def get_global_rai_dir() -> Path:
    """Get the global ~/.rai directory for cross-repo Rai state.

    This directory stores:
    - developer.yaml (identity, already exists)
    - patterns.jsonl (universal patterns, NEW)
    - calibration.jsonl (global calibration, NEW)

    Can be overridden with RAI_HOME environment variable.

    Returns:
        Path to global Rai directory (e.g., ~/.rai or $RAI_HOME)

    Raises:
        ValueError: If RAI_HOME contains path-traversal components.

    Example:
        >>> global_dir = get_global_rai_dir()
        >>> patterns_file = global_dir / "patterns.jsonl"
    """
    rai_home = os.environ.get("RAI_HOME")
    if rai_home:
        return _sanitize_env_path(rai_home, "RAI_HOME")
    return Path.home() / GLOBAL_RAI_DIR


def ensure_global_rai_dir() -> Path:
    """Ensure the global ~/.rai directory exists with required files.

    Creates:
    - ~/.rai/ directory (if not exists)
    - ~/.rai/patterns.jsonl (empty, if not exists)
    - ~/.rai/calibration.jsonl (empty, if not exists)

    Does NOT overwrite existing files.

    Returns:
        Path to global Rai directory.

    Example:
        >>> global_dir = ensure_global_rai_dir()
        >>> # Now safe to write patterns to global_dir / "patterns.jsonl"
    """
    global_dir = get_global_rai_dir()
    global_dir.mkdir(parents=True, exist_ok=True)

    calibration_file = global_dir / CALIBRATION_FILE
    if not calibration_file.exists():
        calibration_file.touch()

    return global_dir


def get_external_cartridge_roots(project_root: Path) -> list[Path]:
    """Get the ordered list of cartridge scan roots — repo-local + external.

    RAISE-13911 (DD-2 (b)): the memory cartridge lives OUTSIDE the repo at
    ``$RAI_HOME/cartridges/`` (default ``~/.rai/cartridges/``) so a derived
    index over personal memory is structurally impossible to commit. Callers
    that scan ``.raise/cartridges/*`` (``_find_all_embeddings_dirs``,
    ``GraphBuilder.load_cartridges``) must scan this second root too — this
    is the single shared helper for both call-sites (no divergent parches,
    per "Canonical Resolver Callers", CLAUDE.md).

    Neither path is checked for existence — callers decide how to handle an
    absent root (skip silently, same as they already do for a missing
    ``.raise/cartridges/``).

    Args:
        project_root: Project root path.

    Returns:
        ``[project_root/.raise/cartridges, $RAI_HOME/cartridges]``, in that
        order (repo-local first).
    """
    return [
        get_raise_dir(project_root) / "cartridges",
        get_global_rai_dir() / "cartridges",
    ]


def get_credentials_path() -> Path:
    """Get path to encrypted credentials file for external providers.

    Returns path to ~/.rai/credentials.json which stores OAuth tokens
    for external providers (JIRA, GitLab, etc.) with Fernet encryption.

    The file is created with user-only permissions (0600) when first written.

    Returns:
        Path to credentials file (e.g., ~/.rai/credentials.json).

    Example:
        >>> creds_path = get_credentials_path()
        >>> # Use with rai_pro.providers.auth.credentials.store_token()
    """
    return get_global_rai_dir() / "credentials.json"


def get_prefixes_path(project_root: Path | None = None) -> Path:
    """Get path to the developer prefix registry (committed to git).

    This is the only session-related file in git by default.
    Lives at .raise/rai/prefixes.yaml.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to prefixes.yaml.
    """
    return get_rai_dir(project_root) / PREFIXES_FILE


def get_developer_sessions_dir(prefix: str, project_root: Path | None = None) -> Path:
    """Get the per-developer session index directory.

    Lives under personal/sessions/{prefix}/ (gitignored by default).
    Teams can opt-in to sharing by modifying .gitignore.

    Args:
        prefix: Developer prefix (e.g., "E", "EO").
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/rai/personal/sessions/{prefix}/ directory.

    Raises:
        ConfigurationError: If prefix contains path traversal characters.
    """
    if ".." in prefix or "/" in prefix or "\\" in prefix:
        raise ConfigurationError(
            f"Invalid developer prefix — path traversal detected: {prefix!r}"
        )
    return get_personal_dir(project_root) / SESSIONS_DIR / prefix


def get_session_dir(session_id: str, project_root: Path | None = None) -> Path:
    """Get the per-session directory for isolated session state.

    Each session instance gets its own directory containing:
    - state.yaml (session working state)
    - signals.jsonl (session telemetry)

    Args:
        session_id: Session identifier (e.g., "SES-177").
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to per-session directory (e.g., .raise/rai/personal/sessions/SES-177/)
    """
    sessions_base = (get_personal_dir(project_root) / SESSIONS_DIR).resolve()
    session_path = (sessions_base / session_id).resolve()
    if not session_path.is_relative_to(sessions_base):
        raise ConfigurationError(
            f"Invalid session_id — path traversal detected: {session_id!r}"
        )
    return session_path


def get_personal_dir(project_root: Path | None = None) -> Path:
    """Get the personal directory for developer-specific project data.

    This directory is gitignored and stores:
    - sessions/index.jsonl (my sessions)
    - telemetry/signals.jsonl (my telemetry)
    - calibration.jsonl (project-specific calibration)
    - patterns.jsonl (project-specific learnings)

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to personal directory (e.g., .raise/rai/personal/)

    Example:
        >>> personal_dir = get_personal_dir()
        >>> my_sessions = personal_dir / "sessions" / "index.jsonl"
    """
    return get_rai_dir(project_root) / PERSONAL_SUBDIR


def _encode_claude_project_path(project_root: Path) -> str:
    """Encode a project path to match Claude Code's project directory naming.

    CC encodes '/', '.', AND '_' as '-' (verified empirically via ~/.claude/projects/).
    Example: /home/developer/.worktree/proj → -home-user--worktree-proj
    """
    path_str = str(project_root.resolve())
    path_str = path_str.replace("\\", "/")  # normalize Windows separators
    path_str = path_str.replace(":", "")  # strip Windows drive letter colon
    return path_str.replace("/", "-").replace(".", "-").replace("_", "-")


def get_claude_memory_path(project_root: Path) -> Path:
    """Get the Claude Code MEMORY.md path for a project.

    Claude Code stores per-project memory at:
        ~/.claude/projects/{encoded_path}/memory/MEMORY.md

    Where {encoded_path} encodes '/' and '.' as '-'. See _encode_claude_project_path.
    This is the first IDE-specific path helper — future IDEs
    (Cursor, Windsurf, etc.) will have sibling functions.

    Args:
        project_root: Absolute path to the project root.

    Returns:
        Path to the Claude Code MEMORY.md file.

    Example:
        >>> get_claude_memory_path(Path("/home/developer/Code/my-project"))
        PosixPath('/home/developer/.claude/projects/-home-user-Code-my-project/memory/MEMORY.md')
    """
    encoded = _encode_claude_project_path(project_root)
    return Path.home() / ".claude" / "projects" / encoded / "memory" / "MEMORY.md"


def get_claude_memory_dir(project_root: Path) -> Path:
    """Get the Claude Code memory directory for a project.

    Returns:
        Parent directory of the MEMORY.md file.
    """
    return get_claude_memory_path(project_root).parent


def get_global_memory_dir(project_root: Path) -> Path:
    """Get the ``_global/`` subdirectory inside Claude Code memory."""
    return get_claude_memory_dir(project_root) / "_global"


def get_mission_memory_dir(project_root: Path, mission_id: str) -> Path:
    """Get ``missions/{mission_id}/`` subdirectory inside Claude Code memory."""
    return get_claude_memory_dir(project_root) / "missions" / mission_id


def get_unassigned_memory_dir(project_root: Path) -> Path:
    """Get the ``_unassigned/`` subdirectory inside Claude Code memory."""
    return get_claude_memory_dir(project_root) / "_unassigned"


def get_agent_memory_dir(agent_type: str, project_root: Path) -> Path:
    """Get the memory directory for a given agent runtime.

    Claude Code uses ~/.claude/projects/{encoded}/memory/.
    All other runtimes use project-local .raise/rai/memory/.
    """
    if agent_type == "claude":
        return get_claude_memory_dir(project_root)
    return project_root / ".raise" / "rai" / "memory"


def _get_xdg_dir(env_var: str, fallback: str) -> Path:
    """Get an XDG directory for raise-cli.

    Args:
        env_var: XDG environment variable name (e.g., "XDG_CONFIG_HOME").
        fallback: Fallback path relative to home (e.g., ".config").

    Returns:
        Path to the rai subdirectory within the XDG directory.
    """
    xdg_value = os.environ.get(env_var)
    base = (
        _sanitize_env_path(xdg_value, env_var) if xdg_value else Path.home() / fallback
    )
    return base / "rai"


def get_config_dir() -> Path:
    """Get the XDG config directory for raise-cli.

    Returns:
        Path to config directory (e.g., ~/.config/rai/ or $XDG_CONFIG_HOME/rai/)

    Example:
        >>> config_dir = get_config_dir()
        >>> config_file = config_dir / "config.toml"
    """
    return _get_xdg_dir("XDG_CONFIG_HOME", ".config")


def get_cache_dir() -> Path:
    """Get the XDG cache directory for raise-cli.

    Returns:
        Path to cache directory (e.g., ~/.cache/rai/ or $XDG_CACHE_HOME/rai/)

    Example:
        >>> cache_dir = get_cache_dir()
        >>> cache_file = cache_dir / "downloaded_katas.json"
    """
    return _get_xdg_dir("XDG_CACHE_HOME", ".cache")


def get_data_dir() -> Path:
    """Get the XDG data directory for raise-cli.

    Returns:
        Path to data directory (e.g., ~/.local/share/rai/ or $XDG_DATA_HOME/rai/)

    Example:
        >>> data_dir = get_data_dir()
        >>> state_file = data_dir / "session_state.json"
    """
    return _get_xdg_dir("XDG_DATA_HOME", ".local/share")
