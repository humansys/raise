"""Neutral git utilities shared across CLI subsystems.

Kept free of imports from ``session/``, ``task/``, ``story/`` so the release
CLI (and any other caller) can depend on it without an awkward coupling
direction into session internals (RAISE-11103 architecture review, H14).
"""

from __future__ import annotations

from raise_cli.git.branch_guard import assert_head_branch

__all__ = ["assert_head_branch"]
