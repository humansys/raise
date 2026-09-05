"""tmux session runner — persistent sessions for CLI harnesses.

Creates tmux sessions so harness processes survive terminal close.
`rai session resume` reattaches via tmux attach.
"""

from __future__ import annotations

import enum
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

RAI_TMUX_PREFIX = "rai-"

CLI_HARNESSES = frozenset({"claude_code", "codex"})


class TmuxSession(BaseModel, frozen=True):
    """A tmux session managed by rai."""

    name: str
    session_id: str


class TmuxStartResult(enum.Enum):
    """Outcome of maybe_start_tmux."""

    CREATED = "created"
    SKIPPED_FLAG = "skipped_flag"
    SKIPPED_ALREADY_IN_TMUX = "skipped_already_in_tmux"
    SKIPPED_NO_TMUX = "skipped_no_tmux"
    SKIPPED_HARNESS = "skipped_harness"


class LivenessObservation(str, enum.Enum):
    """Tri-state liveness result — UNKNOWN never triggers state transitions."""

    ALIVE = "alive"
    DEAD = "dead"
    UNKNOWN = "unknown"


class TmuxRunnerHandle:
    """Handle for a tmux-backed runtime session; provides liveness checks."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    def check_liveness(self) -> LivenessObservation:
        """Return liveness of the tmux session; UNKNOWN on any subprocess error."""
        if not tmux_available():
            return LivenessObservation.UNKNOWN
        try:
            return (
                LivenessObservation.ALIVE
                if session_exists(self.session_id)
                else LivenessObservation.DEAD
            )
        except OSError:
            return LivenessObservation.UNKNOWN


_TMUX_SEARCH_PATHS = ("/usr/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin"))


def _find_tmux() -> str | None:
    """Find tmux binary, checking common paths when PATH is incomplete (e.g. SSH)."""
    found = shutil.which("tmux")
    if found:
        return found
    for d in _TMUX_SEARCH_PATHS:
        candidate = os.path.join(d, "tmux")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def tmux_available() -> bool:
    """Check if tmux is installed."""
    return _find_tmux() is not None


_TMUX_VERSION_RE = re.compile(r"tmux (\d+)\.(\d+)")

_FEATURE_REQUIREMENTS: dict[str, tuple[int, int]] = {
    "window-size-latest": (3, 1),
    "attach-readonly": (3, 2),
}


def get_tmux_version() -> tuple[int, int] | None:
    """Return (major, minor) from `tmux -V`, or None if unavailable/unparseable."""
    tmux = _find_tmux()
    if tmux is None:
        return None
    try:
        result = subprocess.run([tmux, "-V"], capture_output=True, text=True)
        m = _TMUX_VERSION_RE.search(result.stdout or "")
        return (int(m.group(1)), int(m.group(2))) if m else None
    except OSError:
        return None


def probe_feature(feature: str) -> bool:
    """Return True if the installed tmux supports *feature*.

    Known features: ``window-size-latest`` (>= 3.1), ``attach-readonly`` (>= 3.2).
    Unknown features always return False.
    """
    required = _FEATURE_REQUIREMENTS.get(feature)
    if required is None:
        return False
    ver = get_tmux_version()
    return ver is not None and ver >= required


def in_tmux() -> bool:
    """Check if we're already inside a tmux session."""
    return bool(os.environ.get("TMUX"))


def _tmux_bin() -> str:
    """Return the full path to tmux, or 'tmux' as fallback."""
    return _find_tmux() or "tmux"


def _tmux_name(session_id: str) -> str:
    return f"{RAI_TMUX_PREFIX}{session_id}"


def create_session(
    session_id: str,
    command: list[str] | None = None,
    *,
    cols: int | None = None,
    rows: int | None = None,
) -> None:
    """Create a detached tmux session.

    Args:
        session_id: The rai session ID.
        command: Command to run inside the session. Defaults to user's shell.
        cols: Terminal width to set via ``-x`` (requires tmux >= 3.1).
        rows: Terminal height to set via ``-y`` (requires tmux >= 3.1).
    """
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    cmd: list[str] = [tmux, "new-session", "-d", "-s", name]
    if cols is not None and rows is not None and probe_feature("window-size-latest"):
        cmd.extend(["-x", str(cols), "-y", str(rows)])
    if command:
        cmd.extend(command)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        msg = f"tmux session creation failed: {result.stderr}"
        raise RuntimeError(msg)

    logger.info("tmux session created: %s", name)


def attach_session(session_id: str) -> None:
    """Attach to a tmux session. Replaces the current process."""
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    os.execvp(tmux, [tmux, "attach-session", "-t", name])  # noqa: S606


def attach_session_readonly(session_id: str) -> None:
    """Attach read-only to a tmux session. Requires tmux >= 3.2.

    Replaces the current process via os.execvp.
    Raises RuntimeError if the installed tmux does not support ``-r ignore-size``.
    """
    if not probe_feature("attach-readonly"):
        ver = get_tmux_version()
        ver_str = f"{ver[0]}.{ver[1]}" if ver else "unknown"
        msg = f"tmux >= 3.2 required for --view (found {ver_str})"
        raise RuntimeError(msg)
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    os.execvp(tmux, [tmux, "attach-session", "-r", "-t", name, "-x", "ignore-size"])  # noqa: S606


def capture_pane(session_id: str, lines: int = 50) -> str:
    """Capture the last *lines* lines of terminal output from a tmux session.

    Returns the raw output string (may contain ANSI sequences).
    Raises RuntimeError if tmux returns a non-zero exit code.
    """
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    result = subprocess.run(
        [tmux, "capture-pane", "-p", "-t", name, "-S", f"-{lines}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        msg = f"capture-pane failed: {result.stderr}"
        raise RuntimeError(msg)
    return result.stdout


def count_attached_clients(session_id: str) -> int:
    """Return the number of clients currently attached to a tmux session.

    Returns 0 on any error or parse failure.
    """
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    result = subprocess.run(
        [tmux, "display-message", "-p", "#{session_attached}", "-t", name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def kill_session(session_id: str) -> bool:
    """Kill a tmux session. Returns True if killed, False if not found."""
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    result = subprocess.run(
        [tmux, "kill-session", "-t", name],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        logger.info("tmux session killed: %s", name)
        return True
    return False


def session_exists(session_id: str) -> bool:
    """Check if a tmux session exists."""
    tmux = _tmux_bin()
    name = _tmux_name(session_id)
    result = subprocess.run(
        [tmux, "has-session", "-t", name],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def list_sessions() -> list[TmuxSession]:
    """List all rai-managed tmux sessions."""
    tmux = _tmux_bin()
    try:
        result = subprocess.run(
            [tmux, "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []

    if result.returncode != 0:
        return []

    sessions: list[TmuxSession] = []
    for line in result.stdout.strip().splitlines():
        if line.startswith(RAI_TMUX_PREFIX):
            sid = line.removeprefix(RAI_TMUX_PREFIX)
            sessions.append(TmuxSession(name=line, session_id=sid))
    return sessions


def maybe_start_tmux(
    *,
    session_id: str,
    harness: str,
    no_tmux: bool,
) -> TmuxStartResult:
    """Decide whether to create a tmux session and create it if appropriate."""
    if no_tmux:
        return TmuxStartResult.SKIPPED_FLAG

    if harness not in CLI_HARNESSES:
        return TmuxStartResult.SKIPPED_HARNESS

    if not tmux_available():
        logger.warning("tmux not installed — session won't survive terminal close")
        return TmuxStartResult.SKIPPED_NO_TMUX

    if in_tmux():
        logger.info("already in tmux — skipping tmux session creation")
        return TmuxStartResult.SKIPPED_ALREADY_IN_TMUX

    create_session(session_id)
    return TmuxStartResult.CREATED


# --- Harness registry ---

_BUILTIN_HARNESSES: dict[str, dict[str, Any]] = {
    "claude": {
        "command": ["claude"],
        "runtime_name": "claude_code",
        "model_flag": "--model",
    },
    "codex": {"command": ["codex"], "runtime_name": "codex", "model_flag": "--model"},
    "cursor": {"command": ["cursor"], "runtime_name": "cursor", "model_flag": None},
    "aider": {"command": ["aider"], "runtime_name": "aider", "model_flag": "--model"},
}


class HarnessConfig(BaseModel, frozen=True):
    """Configuration for a harness that rai can launch."""

    command: list[str]
    runtime_name: str = ""
    model_flag: str | None = Field(default="--model")


class HarnessRegistry:
    """Registry of known harnesses with their launch commands."""

    def __init__(self, harnesses: dict[str, HarnessConfig] | None = None) -> None:
        self.harnesses: dict[str, HarnessConfig] = {}
        for name, raw in _BUILTIN_HARNESSES.items():
            self.harnesses[name] = HarnessConfig(**raw)
        if harnesses:
            self.harnesses.update(harnesses)

    @classmethod
    def from_yaml(cls, path: Path) -> HarnessRegistry:
        """Load harness config from YAML, merged over builtins."""
        custom: dict[str, HarnessConfig] = {}
        if path.is_file():
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for name, cfg in raw.items():
                if isinstance(cfg, dict):
                    custom[name] = HarnessConfig(**cfg)
        registry = cls()
        registry.harnesses.update(custom)
        return registry

    def get(self, name: str) -> HarnessConfig | None:
        """Look up a harness by name."""
        return self.harnesses.get(name)

    def list_names(self) -> list[str]:
        """Return sorted list of all registered harness names."""
        return sorted(self.harnesses.keys())


def resolve_harness_command(
    config: HarnessConfig,
    *,
    model: str | None,
    extra_args: list[str],
) -> list[str]:
    """Build the full command for launching a harness."""
    cmd = list(config.command)
    if model and config.model_flag:
        cmd.extend([config.model_flag, model])
    cmd.extend(extra_args)
    return cmd
