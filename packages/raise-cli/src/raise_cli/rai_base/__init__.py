"""Base Rai package for distribution.

This package contains the base identity, patterns, and methodology
that ship with raise-cli. On `rai init`, these files are copied
to the project's `.raise/rai/` directory.

Contents:
    identity/       Base identity files (core.yaml, core.md, perspective.md)
    memory/         Base patterns (patterns-base.jsonl) [F14.2]
    framework/      Methodology definition (methodology.yaml) [F14.3]

Usage:
    from importlib.resources import files

    base_files = files("raise_cli.rai_base")
    identity_dir = base_files / "identity"
    core_yaml = (identity_dir / "core.yaml").read_text(encoding="utf-8")
"""

from __future__ import annotations

__version__ = "1.0.0"
