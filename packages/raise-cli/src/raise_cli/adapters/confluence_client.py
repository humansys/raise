"""Confluence client wrapper over atlassian-python-api.

Concrete class (NOT Protocol) providing 10 methods for publishing,
labels, discovery, search, and health. Consumed by adapter, discovery,
and doctor — not directly by skills or CLI.

Optional dependency: ``pip install raise-cli[confluence]``

RAISE-1054 (S1051.1)
"""

from __future__ import annotations

import os

from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig
from raise_cli.adapters.confluence_exceptions import (
    ConfluenceAuthError,
)


class ConfluenceClient:
    """Wraps atlassian.Confluence with auth resolution and error normalization."""

    def __init__(self, config: ConfluenceInstanceConfig) -> None:
        try:
            from atlassian import Confluence
        except ImportError as exc:
            raise ImportError(
                "atlassian-python-api required for Confluence adapter. "
                "Install with: pip install raise-cli[confluence]"
            ) from exc

        token = self._resolve_token(config.instance_name)
        self._config = config
        self._client = Confluence(
            url=config.url,
            username=config.username,
            password=token,
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )

    @staticmethod
    def _resolve_token(instance_name: str) -> str:
        """Resolve API token from environment.

        Order: CONFLUENCE_API_TOKEN_{INSTANCE} → CONFLUENCE_API_TOKEN → error.
        Instance name is uppercased with hyphens replaced by underscores.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"CONFLUENCE_API_TOKEN_{env_suffix}"

        token = os.environ.get(instance_var) or os.environ.get("CONFLUENCE_API_TOKEN")
        if not token:
            raise ConfluenceAuthError(
                f"No Confluence API token found. Set {instance_var} or "
                "CONFLUENCE_API_TOKEN environment variable."
            )
        return token
