"""Loader for ISO 27001 control mapping configuration.

Reads YAML config and validates it via Pydantic models.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.compliance.models import ControlMapping

_DEFAULT_CONFIG_PATH: Path = Path(__file__).parent / "controls.yaml"


def load_control_mapping(path: Path | None = None) -> ControlMapping:
    """Load and validate an ISO 27001 control mapping from YAML.

    Args:
        path: Path to a YAML config file. If ``None``, loads the default
            bundled ``controls.yaml``.

    Returns:
        Validated ``ControlMapping`` instance.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        pydantic.ValidationError: If the YAML content fails validation.
    """
    config_path = path if path is not None else _DEFAULT_CONFIG_PATH

    if not config_path.exists():
        msg = f"Control mapping config not found: {config_path}"
        raise FileNotFoundError(msg)

    raw = config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    return ControlMapping.model_validate(data)
