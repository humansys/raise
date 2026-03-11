"""MCP server registry — discovers servers from .raise/mcp/*.yaml.

Scans the MCP config directory for YAML files, parses each as
``McpServerConfig``, and returns a name → config mapping.

Architecture: ADR-042, E338
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from raise_cli.mcp.schema import McpServerConfig

logger = logging.getLogger(__name__)


def discover_mcp_servers(
    mcp_dir: Path | None = None,
) -> dict[str, McpServerConfig]:
    """Discover MCP servers registered in .raise/mcp/*.yaml.

    Scans ``mcp_dir`` (default: ``.raise/mcp/``) for ``*.yaml`` files,
    parses each as ``McpServerConfig``, and returns a name → config mapping.

    Args:
        mcp_dir: Directory to scan. Defaults to ``.raise/mcp/``.

    Returns:
        Mapping of server name to parsed config.
    """
    if mcp_dir is None:
        mcp_dir = Path.cwd() / ".raise" / "mcp"

    if not mcp_dir.is_dir():
        return {}

    result: dict[str, McpServerConfig] = {}

    for yaml_path in sorted(mcp_dir.glob("*.yaml")):
        if yaml_path.name == "catalog.yaml":
            continue

        try:
            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping %s: YAML parse error: %s", yaml_path.name, exc)
            continue

        if not isinstance(raw, dict):
            logger.warning("Skipping %s: YAML content is not a mapping", yaml_path.name)
            continue

        try:
            config = McpServerConfig.model_validate(raw)
        except ValidationError as exc:
            logger.warning(
                "Skipping %s: schema validation error: %s", yaml_path.name, exc
            )
            continue

        name = config.name
        if name in result:
            logger.warning(
                "Skipping %s: server name '%s' already defined by another YAML file",
                yaml_path.name,
                name,
            )
            continue

        result[name] = config

    return result
