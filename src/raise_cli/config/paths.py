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
from pathlib import Path

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

# File names
SKILLS_MANIFEST_FILE = "skills.json"
MANIFEST_FILE = "manifest.yaml"
CONFIG_FILE = "config.yaml"
PATTERNS_FILE = "patterns.jsonl"
CALIBRATION_FILE = "calibration.jsonl"
PERSONAL_SESSIONS_DIR = "sessions"
SIGNALS_FILE = "signals.jsonl"

# Shared session index (committed to git, per-developer subdirectories)
SHARED_SESSIONS_DIR = "sessions"
PREFIXES_FILE = "prefixes.yaml"
ACTIVE_SESSION_FILE = "active-session"


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
        ValueError: If the path contains traversal components or is not absolute.
    """
    if ".." in raw.split(os.sep):
        msg = f"${var_name} must not contain '..' path components: {raw}"
        raise ValueError(msg)
    resolved = Path(raw).resolve()
    if not resolved.is_absolute():
        msg = f"${var_name} must resolve to an absolute path: {raw}"
        raise ValueError(msg)
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

    # Create empty JSONL files if they don't exist
    patterns_file = global_dir / PATTERNS_FILE
    if not patterns_file.exists():
        patterns_file.touch()

    calibration_file = global_dir / CALIBRATION_FILE
    if not calibration_file.exists():
        calibration_file.touch()

    return global_dir


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


def get_shared_sessions_dir(project_root: Path | None = None) -> Path:
    """Get the shared sessions directory (committed to git).

    This directory contains per-developer session indexes that travel
    with the repository, enabling cross-environment session continuity.

    Structure:
        .raise/rai/sessions/
        ├── prefixes.yaml
        └── {prefix}/
            └── index.jsonl

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/rai/sessions/ directory.
    """
    return get_rai_dir(project_root) / SHARED_SESSIONS_DIR


def get_developer_sessions_dir(
    prefix: str, project_root: Path | None = None
) -> Path:
    """Get the per-developer session index directory (committed to git).

    Args:
        prefix: Developer prefix (e.g., "E", "EO").
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/rai/sessions/{prefix}/ directory.

    Raises:
        ValueError: If prefix contains path traversal characters.
    """
    if ".." in prefix or "/" in prefix or "\\" in prefix:
        raise ValueError(
            f"Invalid developer prefix — path traversal detected: {prefix!r}"
        )
    return get_shared_sessions_dir(project_root) / prefix


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
    sessions_base = (get_personal_dir(project_root) / PERSONAL_SESSIONS_DIR).resolve()
    session_path = (sessions_base / session_id).resolve()
    if not session_path.is_relative_to(sessions_base):
        raise ValueError(
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


def get_claude_memory_path(project_root: Path) -> Path:
    """Get the Claude Code MEMORY.md path for a project.

    Claude Code stores per-project memory at:
        ~/.claude/projects/{encoded_path}/memory/MEMORY.md

    Where {encoded_path} replaces '/' with '-' and prepends '-'.
    This is the first IDE-specific path helper — future IDEs
    (Cursor, Windsurf, etc.) will have sibling functions.

    Args:
        project_root: Absolute path to the project root.

    Returns:
        Path to the Claude Code MEMORY.md file.

    Example:
        >>> get_claude_memory_path(Path("/home/user/Code/my-project"))
        PosixPath('/home/user/.claude/projects/-home-user-Code-my-project/memory/MEMORY.md')
    """
    # Claude Code convention: replace path separators with -, prepend -
    # Must handle both Unix (/) and Windows (\) separators
    path_str = str(project_root)
    # Normalize Windows backslashes to forward slashes
    path_str = path_str.replace("\\", "/")
    # Remove drive letter colon on Windows (C:/Users -> C/Users)
    path_str = path_str.replace(":", "")
    encoded = path_str.replace("/", "-")
    return Path.home() / ".claude" / "projects" / encoded / "memory" / "MEMORY.md"


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
