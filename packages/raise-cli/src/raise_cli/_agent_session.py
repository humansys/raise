"""Discover agent session_id via runtime-agnostic priority chain.

Resolution order:
1. RAISE_AGENT_SESSION_ID (explicit, set by any runtime adapter)
2. RAISE_CC_SESSION_ID (Claude Code backward compat)
2.5. CLAUDE_CODE_SESSION_ID (CC-native; always injected into Bash tool env)
3. CC port discovery (CLAUDE_CODE_SSE_PORT → cc.port, unambiguous match only)
4. Terminal bindings (PPID ancestry → _terminal_bindings.json)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_SESSIONS_DIR = Path(".raise") / "rai" / "sessions"
_CLAUDE_WORKTREES_DIR = Path(".claude") / "worktrees"


def discover_agent_session_id(override: str | None = None) -> str | None:
    """Resolve session ID from any supported runtime.

    Priority chain ensures backward compatibility while enabling
    new runtimes (Hermes, Codex) to participate in session correlation.

    Args:
        override: Explicit session ID (e.g. from pipeline context). When set,
            bypasses env discovery entirely — use when the caller receives the
            parent session ID via an out-of-band channel (RAISE-9886).
    """
    if override:
        return override

    agent_sid = os.environ.get("RAISE_AGENT_SESSION_ID", "").strip()
    if agent_sid:
        return agent_sid

    cc_sid = os.environ.get("RAISE_CC_SESSION_ID", "").strip()
    if cc_sid:
        return cc_sid

    native_sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if native_sid:
        return native_sid

    port_sid = _discover_via_cc_port()
    if port_sid:
        return port_sid

    return _discover_via_terminal_bindings()


def discover_agent_runtime() -> str:
    """Resolve the active agent runtime identifier.

    Resolution: $RAISE_AGENT_RUNTIME > CC-specific env detection > "unknown".
    """
    explicit = os.environ.get("RAISE_AGENT_RUNTIME", "").strip()
    if explicit:
        return explicit

    if os.environ.get("RAISE_CC_SESSION_ID", "").strip():
        return "claude_code"

    if os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip():
        return "claude_code"

    if _discover_via_cc_port():
        return "claude_code"

    if _discover_via_terminal_bindings():
        return "claude_code"

    return "unknown"


def _discover_via_cc_port() -> str | None:
    """CC-specific: match CLAUDE_CODE_SSE_PORT to session dir's cc.port file.

    Returns the matching session ID only when exactly one session matches the
    port. Returns None when the match is ambiguous (multiple sessions share the
    same port, which happens during multi-agent runs where each subagent session
    also writes cc.port). Ambiguous cases are resolved by the terminal-bindings
    fallback instead.
    """
    port = os.environ.get("CLAUDE_CODE_SSE_PORT", "").strip()
    if not port:
        return None
    matches: list[str] = []
    for sessions_dir in _candidate_session_dirs(Path.cwd()):
        for sess_dir in sessions_dir.iterdir():
            if not sess_dir.is_dir():
                continue
            port_file = sess_dir / "cc.port"
            if port_file.exists() and port_file.read_text().strip() == port:
                matches.append(sess_dir.name)
    return matches[0] if len(matches) == 1 else None


def _candidate_session_dirs(root: Path) -> list[Path]:
    """Return session directories relevant from an MCP server CWD."""
    candidates: list[Path] = []
    local_sessions = root / _SESSIONS_DIR
    if local_sessions.exists():
        candidates.append(local_sessions)

    worktrees_root = root / _CLAUDE_WORKTREES_DIR
    if worktrees_root.exists():
        for worktree in sorted(worktrees_root.iterdir()):
            sessions_dir = worktree / _SESSIONS_DIR
            if sessions_dir.exists():
                candidates.append(sessions_dir)

    return candidates


def _get_parent_pid(pid: int) -> int | None:
    """Return the parent PID of *pid* via /proc (Linux only)."""
    try:
        status = Path(f"/proc/{pid}/status").read_text()
        for line in status.splitlines():
            if line.startswith("PPid:"):
                return int(line.split()[1])
        return None
    except (FileNotFoundError, ValueError, PermissionError, OSError):
        return None


def _discover_via_terminal_bindings() -> str | None:
    """Resolve session ID by walking the PID ancestry to the CC process.

    The SessionStart hook writes ``{cc_pid: {session_id: ...}}`` to
    ``_terminal_bindings.json``. From within a Bash tool call the CC process is
    the grandparent: ``rai`` → ``bash`` → ``CC``. Reading the grandparent PID
    and looking it up in the bindings gives the correct session even when
    multiple sessions share the same SSE port.
    """
    try:
        bash_pid = os.getppid()
        cc_pid = _get_parent_pid(bash_pid)
        if cc_pid is None:
            return None
        bindings_file = Path.cwd() / _SESSIONS_DIR / "_terminal_bindings.json"
        if not bindings_file.exists():
            return None
        bindings: dict[str, dict[str, object]] = json.loads(bindings_file.read_text())
        entry = bindings.get(str(cc_pid))
        if entry:
            sid = entry.get("session_id")
            if sid:
                return str(sid)
        return None
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None
