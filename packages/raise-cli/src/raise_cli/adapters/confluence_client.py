"""Confluence client wrapper over atlassian-python-api.

Concrete class (NOT Protocol) providing 10 methods for publishing,
labels, discovery, search, and health. Consumed by adapter, discovery,
and doctor — not directly by skills or CLI.

Optional dependency: ``pip install raise-cli[confluence]``

RAISE-1054 (S1051.1)
"""

from __future__ import annotations

import os
from typing import Any

from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig
from raise_cli.adapters.confluence_exceptions import (
    ConfluenceApiError,
    ConfluenceAuthError,
    ConfluenceError,
    ConfluenceNotFoundError,
)
from raise_cli.adapters.models.docs import PageContent, PageSummary, SpaceInfo
from raise_cli.adapters.models.health import AdapterHealth


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
        username = config.username or self._resolve_username(config.instance_name)
        self._config = config
        self._client = Confluence(
            url=config.url,
            username=username,
            password=token,
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )

    # ── Publishing ────────────────────────────────────────────────────

    def create_page(
        self,
        title: str,
        body: str,
        parent_id: str | None = None,
        space: str | None = None,
    ) -> PageContent:
        """Create a page. Uses config.space_key unless space is overridden."""
        target_space = space or self._config.space_key
        try:
            raw: dict[str, Any] = self._client.create_page(  # type: ignore[no-untyped-call]
                space=target_space,
                title=title,
                body=body,
                parent_id=parent_id,
                type="page",
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"create_page({title!r})") from e

    def update_page(self, page_id: str, title: str, body: str) -> PageContent:
        """Update an existing page by ID."""
        try:
            raw: dict[str, Any] = self._client.update_page(  # type: ignore[no-untyped-call]
                page_id=page_id,
                title=title,
                body=body,
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"update_page({page_id})") from e

    def get_page_by_id(self, page_id: str) -> PageContent:
        """Get full page content by ID."""
        try:
            raw: dict[str, Any] = self._client.get_page_by_id(  # type: ignore[no-untyped-call]
                page_id=page_id,
                expand="body.storage,version,space",
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_page_by_id({page_id})") from e

    def get_page_by_title(
        self, title: str, space: str | None = None
    ) -> PageContent | None:
        """Get page by title. Returns None if not found."""
        target_space = space or self._config.space_key
        try:
            result = self._client.get_page_by_title(  # type: ignore[no-untyped-call]
                space=target_space,
                title=title,
                expand="body.storage,version,space",
            )
            if not result:  # None or empty dict
                return None
            return self._parse_page(result)  # type: ignore[arg-type]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_page_by_title({title!r})") from e

    # ── Labels ────────────────────────────────────────────────────────

    def set_labels(self, page_id: str, labels: list[str]) -> None:
        """Set labels on a page (replace semantics — removes unlisted labels)."""
        try:
            existing = set(self.get_labels(page_id))
            desired = set(labels)

            # Remove labels not in desired set
            for label in existing - desired:
                self._client.remove_page_label(page_id, label)  # type: ignore[no-untyped-call]

            # Add labels not yet present
            for label in desired - existing:
                self._client.set_page_label(page_id, label)  # type: ignore[no-untyped-call]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"set_labels({page_id})") from e

    def add_labels(self, page_id: str, labels: list[str]) -> None:
        """Add labels to a page (additive — does not remove existing)."""
        try:
            for label in labels:
                self._client.set_page_label(page_id, label)  # type: ignore[no-untyped-call]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"add_labels({page_id})") from e

    def get_labels(self, page_id: str) -> list[str]:
        """Get labels for a page."""
        try:
            raw: dict[str, Any] = self._client.get_page_labels(page_id)  # type: ignore[no-untyped-call]
            return [label["name"] for label in raw.get("results", [])]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_labels({page_id})") from e

    # ── Discovery ─────────────────────────────────────────────────────

    def get_space_homepage_id(self, space_key: str) -> str | None:
        """Get the homepage page ID for a space. Returns None if not found."""
        try:
            raw: Any = self._client.get_home_page_of_space(space_key)  # type: ignore[no-untyped-call]
            if isinstance(raw, dict) and "id" in raw:
                return str(raw["id"])  # type: ignore[no-untyped-call]
            return None
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_space_homepage_id({space_key})") from e

    def get_spaces(self) -> list[SpaceInfo]:
        """List all accessible spaces.

        Paginates through all results — ``get_all_spaces()`` returns only
        one page (default limit=50), which misses spaces beyond that page.
        RAISE-1187: discovered during S1130.4 dogfood.
        """
        try:
            all_results: list[dict[str, Any]] = []
            start = 0
            limit = 100
            while True:
                raw: dict[str, Any] = self._client.get_all_spaces(  # type: ignore[no-untyped-call]
                    start=start, limit=limit
                )
                results: list[dict[str, Any]] = raw.get("results", [])
                all_results.extend(results)
                if len(results) < limit:
                    break
                start += limit
            return [
                SpaceInfo(
                    key=s["key"],
                    name=s.get("name", ""),
                    url=s.get("_links", {}).get("webui", ""),
                    type=s.get("type", "global"),
                )
                for s in all_results
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, "get_spaces") from e

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        """Get child pages of a page."""
        try:
            raw: list[dict[str, Any]] = self._client.get_child_pages(page_id)  # type: ignore[no-untyped-call]
            return [
                PageSummary(
                    id=str(p["id"]),
                    title=p.get("title", ""),
                    url=p.get("_links", {}).get("webui", ""),
                    space_key=p.get("space", {}).get("key", ""),
                )
                for p in raw
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_page_children({page_id})") from e

    # ── Search & Health ───────────────────────────────────────────────

    @staticmethod
    def _ensure_cql(query: str) -> str:
        """Wrap plain text in CQL siteSearch if not already CQL.

        CQL queries contain operators like ~, =, AND, OR, or known
        predicates like type=, space=, text~. Plain text does not.
        """
        cql_indicators = ("~", "=", " AND ", " OR ", " ORDER BY ")
        if any(op in query for op in cql_indicators):
            return query
        # Escape double quotes in user query
        escaped = query.replace('"', '\\"')
        return f'siteSearch ~ "{escaped}"'

    def search(self, cql: str, limit: int = 10) -> list[PageSummary]:
        """Search using CQL. Plain text queries are auto-wrapped."""
        effective_cql = self._ensure_cql(cql)
        try:
            raw: dict[str, Any] = self._client.cql(effective_cql, limit=limit)  # type: ignore[no-untyped-call]
            return [
                PageSummary(
                    id=str(r["content"]["id"]),
                    title=r["content"].get("title", ""),
                    url=r.get("url", ""),
                    space_key=r["content"].get("space", {}).get("key", ""),
                )
                for r in raw.get("results", [])
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"search({effective_cql!r})") from e

    def health(self) -> AdapterHealth:
        """Check connectivity by listing 1 space."""
        try:
            self._client.get_all_spaces(limit=1)  # type: ignore[no-untyped-call]
            return AdapterHealth(name="confluence", healthy=True)
        except Exception as e:
            return AdapterHealth(name="confluence", healthy=False, message=str(e))

    # ── Internal ──────────────────────────────────────────────────────

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

    @staticmethod
    def _resolve_username(instance_name: str) -> str:
        """Resolve username (email) from environment.

        Order: CONFLUENCE_USERNAME_{INSTANCE} → CONFLUENCE_USERNAME → error.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"CONFLUENCE_USERNAME_{env_suffix}"

        username = os.environ.get(instance_var) or os.environ.get("CONFLUENCE_USERNAME")
        if not username:
            raise ConfluenceAuthError(
                f"No Confluence username found. Set {instance_var} or "
                "CONFLUENCE_USERNAME environment variable, or set username in config."
            )
        return username

    @staticmethod
    def _parse_page(raw: dict[str, Any]) -> PageContent:
        """Convert raw API response to PageContent."""
        links = raw.get("_links", {})
        base_url = links.get("base", "")
        webui = links.get("webui", "")
        url = f"{base_url}{webui}" if base_url and webui else webui

        body = raw.get("body", {})
        content = body.get("storage", {}).get("value", "") if body else ""

        space_raw: dict[str, Any] = raw.get("space") or {}
        space_key: str = str(space_raw.get("key", ""))

        version_raw: dict[str, Any] = raw.get("version") or {}
        version_num: int = int(version_raw.get("number", 1))

        return PageContent(
            id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            content=content,
            url=url,
            space_key=space_key,
            version=version_num,
        )

    @staticmethod
    def _map_error(error: Exception, context: str) -> ConfluenceError:
        """Map atlassian exceptions to our hierarchy using isinstance."""
        from atlassian.errors import ApiError, ApiNotFoundError, ApiPermissionError

        if isinstance(error, ApiPermissionError):
            return ConfluenceAuthError(f"{context}: {error}")
        if isinstance(error, ApiNotFoundError):
            return ConfluenceNotFoundError(f"{context}: {error}")
        if isinstance(error, ApiError):
            return ConfluenceApiError(f"{context}: {error}")
        return ConfluenceApiError(f"{context}: unexpected error: {error}")
