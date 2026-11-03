"""Fleet Director configuration models and loader.

Provides fail-safe YAML loading for .raise/fleet.yaml into typed Pydantic models.
Missing or invalid files return an empty FleetConfig rather than raising.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

log = logging.getLogger(__name__)

VALID_SIZES = {"xs", "s", "m", "l", "xl"}


class AutoApproveRule(BaseModel, frozen=True):
    """A single auto-approve rule.

    Attributes:
        size: Story size that this rule applies to (case-insensitive).
              None means wildcard — matches any size.
        gates: Gate condition required for auto-approve. Currently only
               "all_green" is supported; kept as str for future extension.
        scope_overlap: Reserved for D6 trajectory-overlap gate. Unused now.
    """

    size: str | None = None
    gates: str = "all_green"
    scope_overlap: bool = False  # deferred — D6

    @field_validator("size")
    @classmethod
    def _validate_size(cls, v: str | None) -> str | None:
        if v is not None and v.lower() not in VALID_SIZES:
            raise ValueError(f"Invalid size {v!r}; expected one of {VALID_SIZES}")
        return v.lower() if v else v


class FleetAutoApproveConfig(BaseModel, frozen=True):
    """Container for the list of auto-approve rules.

    An empty rules list means auto-approve is effectively disabled.
    """

    rules: list[AutoApproveRule] = []


class FleetConfig(BaseModel, frozen=True):
    """Top-level Fleet Director configuration.

    Loaded from .raise/fleet.yaml. Fail-safe: returns empty config on
    missing or invalid files.
    """

    auto_approve: FleetAutoApproveConfig = FleetAutoApproveConfig()


def load(cwd: str | Path = ".") -> FleetConfig:
    """Load fleet configuration from .raise/fleet.yaml in cwd.

    Fail-safe: returns empty FleetConfig if the file is missing, empty,
    or cannot be parsed. Parse errors are logged at DEBUG level.

    Args:
        cwd: Directory to search for .raise/fleet.yaml.

    Returns:
        Parsed FleetConfig, or FleetConfig() on any failure.
    """
    path = Path(cwd) / ".raise" / "fleet.yaml"
    try:
        raw = yaml.safe_load(path.read_text())
        return FleetConfig.model_validate(raw or {})
    except FileNotFoundError:
        return FleetConfig()
    except Exception as exc:  # noqa: BLE001
        log.debug("fleet.yaml parse error at %s: %s", path, exc)
        return FleetConfig()
