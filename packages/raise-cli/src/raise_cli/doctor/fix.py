"""Auto-fix actions for rai doctor --fix.

Each fix is a function registered via @register_fix(fix_id).
Fix IDs correspond to CheckResult.fix_id values set by checks.

Before any mutation, backups are created (.bak suffix).

Architecture: S352.4
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from raise_cli.doctor.models import CheckResult

FIX_REGISTRY: dict[str, Callable[[Path], bool]] = {}


def register_fix(
    fix_id: str,
) -> Callable[[Callable[[Path], bool]], Callable[[Path], bool]]:
    """Decorator to register a fix function by ID."""

    def decorator(fn: Callable[[Path], bool]) -> Callable[[Path], bool]:
        FIX_REGISTRY[fix_id] = fn
        return fn

    return decorator


@register_fix("rebuild-graph")
def rebuild_graph(working_dir: Path) -> bool:
    """Rebuild the knowledge graph by invoking ``rai graph build``."""
    result = subprocess.run(
        [sys.executable, "-m", "raise_cli", "graph", "build"],
        cwd=working_dir,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


@register_fix("add-gitignore-personal")
def add_gitignore_personal(working_dir: Path) -> bool:
    """Add .raise/rai/personal/ to .gitignore with backup."""
    gitignore = working_dir / ".gitignore"
    entry = ".raise/rai/personal/"

    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if entry in content:
            return True  # already present, no-op
        # Backup before mutation
        shutil.copy2(gitignore, working_dir / ".gitignore.bak")
    else:
        content = ""

    try:
        with open(gitignore, "a", encoding="utf-8") as f:
            f.write(f"\n# RaiSE personal data (sessions, telemetry)\n{entry}\n")
    except OSError:
        return False
    return True


def run_fixes(
    results: list[CheckResult],
    working_dir: Path,
) -> list[tuple[str, bool]]:
    """Run fixes for all results that have a fix_id.

    Returns:
        List of (fix_id, success) pairs for each attempted fix.
    """
    outcomes: list[tuple[str, bool]] = []
    for r in results:
        if r.fix_id and r.fix_id in FIX_REGISTRY:
            success = FIX_REGISTRY[r.fix_id](working_dir)
            outcomes.append((r.fix_id, success))
    return outcomes
