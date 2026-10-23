"""Cockpit worktree operations — extracted from app.py monolith (RAISE-16704).

Interactive worktree lifecycle operations (register, close orphan).
These run after the TUI loop stops — they use print/input for interaction.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from raise_cli.cockpit.data import main_repo_root
from raise_cli.storage.worktrees import Worktree


def register_existing_worktree(wt: Worktree) -> None:
    """Register a git worktree that exists on disk but is not in the DB."""
    rai_cmd = str(Path(sys.executable).parent / "rai")
    repo_root = main_repo_root()

    print()
    print(f"  Registering {wt.worktree_id}…")
    result = subprocess.run(
        [
            rai_cmd,
            "worktree",
            "register",
            "--name",
            wt.worktree_id,
            "--path",
            str(Path(wt.path).resolve()),
            "--branch",
            wt.branch,
            "--merge-target",
            wt.merge_target,
        ],
        cwd=repo_root,
    )
    if result.returncode == 0:
        print(f"  ✓ {wt.worktree_id} registered")
    else:
        print(f"  ✗ registration failed (exit {result.returncode})", file=sys.stderr)
    input("\n  Press Enter to return to cockpit...")


def close_orphan_worktree(wt: Worktree) -> None:
    """Mark an orphan DB entry as closed."""
    rai_cmd = str(Path(sys.executable).parent / "rai")
    repo_root = main_repo_root()

    print()
    print(f"  Removing orphan {wt.worktree_id} from DB…")

    result = subprocess.run(
        [rai_cmd, "worktree", "complete", "--name", wt.worktree_id],
        cwd=repo_root,
        capture_output=True,
    )
    if result.returncode == 0:
        print(f"  ✓ {wt.worktree_id} removed")
    else:
        try:
            from raise_cli.storage.worktrees import SqliteWorktreeStore

            store = SqliteWorktreeStore(repo_root)
            store.complete(wt.worktree_id)
            print(f"  ✓ {wt.worktree_id} closed in DB")
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ failed: {exc}", file=sys.stderr)
    input("\n  Press Enter to return to cockpit...")


def slugify(text: str) -> str:
    """Convert free text to a valid kebab-case worktree slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:50]
