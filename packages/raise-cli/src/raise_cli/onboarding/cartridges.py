"""Scaffold bundled cartridges into a project during initialization.

Copies RaiSE cartridges from the raise_cli.cartridges_base package to the
project's .raise/cartridges directory during `rai init`. Uses a safe copy
policy: skips existing cartridges by default; force=True overwrites the two
things the bundle owns (CARTRIDGE.yaml and instances/) and leaves everything
else in the cartridge untouched.

Uses importlib.resources to read bundled cartridge files (Python 3.9+).

Example:
    from raise_cli.onboarding.cartridges import scaffold_cartridges

    result = scaffold_cartridges(project_path)
    if result.cartridges_distributed:
        print(f"Distributed {result.cartridges_distributed} cartridges")
"""

from __future__ import annotations

import logging
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# List of bundled cartridges to distribute
BUNDLED_CARTRIDGES = [
    "raise-methodology",
    "management-ontology",
    "raise-dev-workflow",
]


class CartridgeScaffoldResult(BaseModel):
    """Result of cartridge scaffolding operation."""

    cartridges_distributed: int = 0
    cartridges_skipped: int = 0
    names_distributed: list[str] = Field(default_factory=list)
    names_skipped: list[str] = Field(default_factory=list)


def scaffold_cartridges(
    project_root: Path,
    *,
    force: bool = False,
) -> CartridgeScaffoldResult:
    """Copy bundled cartridges to project's .raise/cartridges directory.

    Args:
        project_root: Root path of the project being initialized.
        force: If True, overwrite the bundle-owned files (CARTRIDGE.yaml and
            instances/) of cartridges that already exist, leaving any other
            content in place. If False (default), skip existing cartridges
            entirely.

    Returns:
        CartridgeScaffoldResult with counts and names of distributed/skipped
        cartridges.
    """
    cartridges_target_dir = project_root / ".raise" / "cartridges"
    cartridges_target_dir.mkdir(parents=True, exist_ok=True)

    distributed: list[str] = []
    skipped: list[str] = []

    try:
        # Use importlib.resources to access bundled cartridges_base package
        cartridges_base = files("raise_cli.cartridges_base")
    except ModuleNotFoundError as e:
        logger.error(
            f"Bundled cartridges package 'raise_cli.cartridges_base' not found. "
            f"This indicates the cartridges_base data was not included in the distribution. "
            f"Ensure pyproject.toml includes cartridges_base in package-data. {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Failed to access bundled cartridges: {e}")
        raise

    for cartridge_name in BUNDLED_CARTRIDGES:
        target_cartridge_dir = cartridges_target_dir / cartridge_name

        # Check if cartridge already exists
        if target_cartridge_dir.exists() and not force:
            logger.debug(f"Skipping cartridge {cartridge_name} (already exists)")
            skipped.append(cartridge_name)
            continue

        try:
            # force overwrites what the bundle owns — CARTRIDGE.yaml and
            # instances/ — and nothing else. It must never clear the directory
            # first: corpus/, eval/ and extractors/ exist only in the project
            # and the bundle cannot reconstruct them, so wiping to "overwrite"
            # destroys curated content permanently (RAISE-15655).
            source_cartridge = cartridges_base / cartridge_name

            # Create target directory
            target_cartridge_dir.mkdir(parents=True, exist_ok=True)

            # Copy CARTRIDGE.yaml
            source_cartridge_file = source_cartridge / "CARTRIDGE.yaml"
            target_cartridge_file = target_cartridge_dir / "CARTRIDGE.yaml"

            if source_cartridge_file.is_file():
                content = source_cartridge_file.read_text(encoding="utf-8")
                target_cartridge_file.write_text(content, encoding="utf-8")
                logger.debug(f"Copied {cartridge_name}/CARTRIDGE.yaml")

            # Copy instances/ directory
            source_instances = source_cartridge / "instances"
            target_instances = target_cartridge_dir / "instances"

            if source_instances.is_dir():
                target_instances.mkdir(parents=True, exist_ok=True)
                for instance_file in source_instances.iterdir():
                    if instance_file.is_file():
                        content = instance_file.read_text(encoding="utf-8")
                        (target_instances / instance_file.name).write_text(
                            content, encoding="utf-8"
                        )
                        logger.debug(
                            f"Copied {cartridge_name}/instances/{instance_file.name}"
                        )

            logger.debug(f"Distributed cartridge {cartridge_name}")
            distributed.append(cartridge_name)

        except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.error(f"Failed to scaffold cartridge {cartridge_name}: {e}")
            continue

    return CartridgeScaffoldResult(
        cartridges_distributed=len(distributed),
        cartridges_skipped=len(skipped),
        names_distributed=distributed,
        names_skipped=skipped,
    )
