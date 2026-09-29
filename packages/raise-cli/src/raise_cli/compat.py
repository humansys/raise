"""Cross-platform compatibility layer.

Centralizes all platform-specific code so the rest of the codebase
never checks sys.platform directly. Pattern used by pip, poetry, virtualenv.

All platform guards live here. Import from compat, not from fcntl/msvcrt.
"""

from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404 - subprocess required for detached process spawning
import sys
import webbrowser
from pathlib import Path
from typing import IO

IS_WINDOWS = sys.platform == "win32"
IS_FROZEN: bool = getattr(sys, "frozen", False)


def open_browser(url: str) -> bool:
    """Open `url` in the default browser, safe under a frozen binary.

    PyInstaller's onedir bootloader sets LD_LIBRARY_PATH to its bundled
    _internal/ dir for the process lifetime, so its own bundled libs
    resolve first. webbrowser.open() spawns `xdg-open` (a `#!/bin/sh`
    script), and that subprocess inherits the contaminated env — if the
    bundled libreadline's ABI diverges from the system's, /bin/sh crashes
    with "undefined symbol: rl_print_keybinding" before it can run
    (RAISE-16007). Restore the pre-frozen value (or clear it, if there was
    none) around the call, then put the frozen value back.
    """
    if not IS_FROZEN:
        return webbrowser.open(url)

    frozen_value = os.environ.get("LD_LIBRARY_PATH")
    orig_value = os.environ.get("LD_LIBRARY_PATH_ORIG")
    try:
        if orig_value is not None:
            os.environ["LD_LIBRARY_PATH"] = orig_value
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
        return webbrowser.open(url)
    finally:
        if frozen_value is not None:
            os.environ["LD_LIBRARY_PATH"] = frozen_value
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)


def get_rai_executable() -> list[str]:
    """Return the rai invocation prefix for the current environment.

    Note: uses `uv run rai` when uv is available, which resolves from the
    target repository's cwd. For identity-critical paths (e.g. onboarding)
    use ``get_self_invocation()`` instead.
    """
    if IS_FROZEN:
        return [sys.executable]
    if shutil.which("uv"):
        return ["uv", "run", "rai"]
    return [sys.executable, "-m", "raise_cli"]


def get_self_invocation() -> list[str]:
    """Strict self-invocation prefix for child rai processes.

    Unlike get_rai_executable(), never returns a cwd- or PATH-sensitive
    launcher: `uv run rai` can resolve a different raise-cli from the
    target repository (RAISE-16346).

    Returns:
        ``[sys.executable]`` when frozen (PyInstaller binary);
        ``[sys.executable, "-m", "raise_cli"]`` otherwise.
    """
    if IS_FROZEN:
        return [sys.executable]
    return [sys.executable, "-m", "raise_cli"]


def file_lock(f: IO[str], *, exclusive: bool = True) -> None:
    """Acquire a file lock. Uses fcntl on Unix, msvcrt on Windows."""
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(f.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)


def spawn_detached(args: list[str]) -> None:
    """Spawn a background process that outlives the caller.

    Used by `rai self-update` (RAISE-15632) to launch the Windows swap
    script after this process exits — Windows can't overwrite a running
    executable's own file, so the swap runs in a separate process that
    waits for this one to end.
    """
    if IS_WINDOWS:
        creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
        subprocess.Popen(args, creationflags=creationflags, close_fds=True)
    else:
        subprocess.Popen(args, start_new_session=True, close_fds=True)


def file_unlock(f: IO[str]) -> None:
    """Release a file lock. Uses fcntl on Unix, msvcrt on Windows."""
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def portable_path(path: Path, relative_to: Path) -> str:
    """Return forward-slash relative path string for serialization.

    Always uses forward slashes regardless of OS, ensuring consistent
    path strings in JSON, graph data, and other serialized formats.
    """
    return path.relative_to(relative_to).as_posix()


def to_file_uri(path: Path) -> str:
    """Return correct file:// URI on any platform.

    Uses pathlib's as_uri() which handles Windows drive letters correctly.
    """
    return path.resolve().as_uri()


def secure_permissions(path: Path) -> None:
    """Set restrictive file permissions (0o600). No-op on Windows.

    On Windows, POSIX chmod has no effect. For true Windows ACL
    restriction, icacls would be needed — deferred until required.
    """
    if not IS_WINDOWS:
        path.chmod(0o600)


# check_legacy_packages() removed in S2 (RAISE-16229).  Detection is now
# structural via raise_cli.legacy.scanner.scan_venvs (venv-prerename-pkg).
