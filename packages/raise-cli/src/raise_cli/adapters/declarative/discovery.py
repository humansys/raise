"""YAML adapter discovery for declarative MCP adapters.

Scans ``.raise/adapters/*.yaml`` for adapter configs, parses them with
``DeclarativeAdapterConfig``, filters by protocol, and returns factory
closures compatible with ``resolve_entrypoint``.

Architecture: ADR-041, E337, S337.3, AR-C1 (factory closure)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from raise_cli.adapters.declarative.schema import DeclarativeAdapterConfig

logger = logging.getLogger(__name__)


def _make_factory(cfg: DeclarativeAdapterConfig) -> Callable[[], Any]:
    """AR-C1: factory closure captures config for no-arg instantiation."""

    def factory() -> Any:
        from raise_cli.adapters.declarative.adapter import DeclarativeMcpAdapter

        return DeclarativeMcpAdapter(cfg)

    return factory


def discover_yaml_adapters(
    protocol: str,
    *,
    adapters_dir: Path | None = None,
) -> dict[str, Callable[[], Any]]:
    """Discover YAML-defined adapters for a given protocol.

    Scans ``adapters_dir`` (default: ``.raise/adapters/``) for ``*.yaml``
    files, parses each as a ``DeclarativeAdapterConfig``, filters by
    ``adapter.protocol``, and returns factory closures.

    Each factory closure captures its parsed config and returns a new
    ``DeclarativeMcpAdapter`` when called with no arguments (AR-C1).

    Args:
        protocol: Protocol to filter by (``"pm"`` or ``"docs"``).
        adapters_dir: Directory to scan. Defaults to ``.raise/adapters/``.

    Returns:
        Mapping of adapter name to no-arg factory callable.
    """
    if adapters_dir is None:
        adapters_dir = Path.cwd() / ".raise" / "adapters"

    if not adapters_dir.is_dir():
        return {}

    result: dict[str, Callable[[], Any]] = {}

    for yaml_path in sorted(adapters_dir.glob("*.yaml")):
        try:
            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping %s: YAML parse error: %s", yaml_path.name, exc)
            continue

        try:
            config = DeclarativeAdapterConfig.model_validate(raw)
        except ValidationError as exc:
            logger.warning(
                "Skipping %s: schema validation error: %s", yaml_path.name, exc
            )
            continue

        if config.adapter.protocol != protocol:
            continue

        name = config.adapter.name
        if name in result:
            logger.warning(
                "Skipping %s: adapter name '%s' already defined by another YAML file",
                yaml_path.name,
                name,
            )
            continue

        result[name] = _make_factory(config)

    return result
