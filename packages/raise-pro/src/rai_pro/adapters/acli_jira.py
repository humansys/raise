"""Jira adapter via ACLI subprocess.

Implements ``AsyncProjectManagementAdapter`` by mapping each protocol method
to ``acli jira`` commands via ``AcliJiraBridge``.

Configuration: reads ``.raise/jira.yaml`` for project config.
Status resolution: by convention (``replace("-", " ").title()``), not config lookup.
``status_mapping`` in jira.yaml is MCP legacy — not used by this adapter.

Architecture: E494 design (D1-D4), S494.3
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.models import AdapterHealth

from .acli_bridge import AcliJiraBridge

# Module-level config path as test seam (PAT-E-589)
_JIRA_YAML_PATH = Path(".raise") / "jira.yaml"


def normalize_status(status: str) -> str:
    """Convert CLI slug to Jira status name by convention.

    Examples: "in-progress" → "In Progress", "done" → "Done".
    """
    return status.replace("-", " ").title()


class AcliJiraAdapter:
    """Jira adapter that delegates to ACLI via AcliJiraBridge.

    Implements ``AsyncProjectManagementAdapter`` protocol (structural typing).

    Args:
        project_root: Project root containing ``.raise/jira.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        config = self._load_config(root)
        self._projects: dict[str, dict[str, Any]] = config.get("projects", {})
        self._bridge = AcliJiraBridge()

    @staticmethod
    def _load_config(root: Path) -> dict[str, Any]:
        """Read and parse .raise/jira.yaml."""
        config_path = root / _JIRA_YAML_PATH
        if not config_path.exists():
            msg = f"Jira config not found: {config_path}"
            raise FileNotFoundError(msg)
        with open(config_path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return data

    def build_url(self, key: str) -> str:
        """Construct web browse URL from project site + issue key.

        Returns empty string if project is unknown (no site configured).
        """
        project_key = key.split("-")[0] if "-" in key else ""
        project = self._projects.get(project_key, {})
        site = project.get("site", "")
        if not site:
            return ""
        return f"https://{site}/browse/{key}"

    # ----- Health -----

    async def health(self) -> AdapterHealth:
        """Delegate health check to AcliJiraBridge."""
        return await self._bridge.health()
