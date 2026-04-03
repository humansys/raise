"""Pre-commit hook that runs lint, format, and type-check from manifest.

Loads ``.raise/manifest.yaml`` and runs the configured lint, format,
and type-check commands. Deliberately skips test_command (too slow
for commit-time).

Usage as git hook shim target::

    uv run python -m raise_cli.gates.hook

Architecture: S474.4 -- Pre-commit Hook
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

from raise_cli.onboarding.manifest import load_manifest

# Commands to run from manifest, in order.
# test_command is deliberately excluded (too slow for commit-time).
_HOOK_COMMANDS: tuple[tuple[str, str], ...] = (
    ("lint_command", "lint"),
    ("format_command", "format"),
    ("type_check_command", "type-check"),
)


def run_hook(working_dir: Path) -> int:
    """Run pre-commit checks from manifest.

    Args:
        working_dir: Project root directory.

    Returns:
        0 if all checks pass, 1 if any fail or manifest not found.
    """
    manifest = load_manifest(working_dir)
    if manifest is None:
        print("[FAIL] No .raise/manifest.yaml found")
        return 1

    any_failed = False

    for manifest_key, label in _HOOK_COMMANDS:
        command: str | None = getattr(manifest.project, manifest_key, None)
        if command is None:
            continue

        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                cwd=str(working_dir),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {label}: {type(exc).__name__}: {exc}")
            any_failed = True
            continue

        if result.returncode == 0:
            print(f"[PASS] {label}")
        else:
            print(f"[FAIL] {label}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            any_failed = True

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(run_hook(Path.cwd()))
