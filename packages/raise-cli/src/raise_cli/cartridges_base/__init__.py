"""Base cartridges package for distribution.

This package contains the base knowledge cartridges that ship with raise-cli.
On `rai init`, these cartridges are copied to the project's `.raise/cartridges/`
directory for local use and customization.

Contents:
    raise-methodology/      Universal RaiSE methodology (identity, values, workflows, coaching)
    management-ontology/    Default work management ontology (work types, phases, transitions)
    raise-dev-workflow/     Development workflow definitions (patterns, lifecycle stages)

Usage:
    from importlib.resources import files

    cartridges_pkg = files("raise_cli.cartridges_base")
    methodology_dir = cartridges_pkg / "raise-methodology"
    cartridge_yaml = (methodology_dir / "CARTRIDGE.yaml").read_text(encoding="utf-8")
    instances = list((methodology_dir / "instances").iterdir())
"""

from __future__ import annotations

__version__ = "1.0.0"
