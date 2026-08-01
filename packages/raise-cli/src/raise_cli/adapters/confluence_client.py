"""Confluence client wrapper over atlassian-python-api.

Concrete class (NOT Protocol) providing 10 methods for publishing,
labels, discovery, search, and health. Consumed by adapter, discovery,
and doctor — not directly by skills or CLI.

Optional dependency: ``pip install raise-cli[confluence]``

RAISE-1054 (S1051.1)
"""

from __future__ import annotations

import logging
import os
from typing import Any

from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig
from raise_cli.adapters.confluence_exceptions import (
    ConfluenceApiError,
    ConfluenceAuthError,
    ConfluenceError,
    ConfluenceNotFoundError,
)
from raise_cli.adapters.confluence_markdown import markdown_to_storage
from raise_cli.adapters.models.docs import (
    AttachmentSummary,
    CommentSummary,
    PageContent,
    PageSummary,
    SpaceInfo,
)
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

        self._config = config
        self._is_oauth = False
        self._oauth_token = ""
        self._oauth_cloud_id = ""

        # OAuth-priority: Bearer token auth when both vars are set (S6574.7)
        oauth_token = self._resolve_oauth_token(config.instance_name)
        cloud_id = self._resolve_cloud_id(config.instance_name)
        if oauth_token and cloud_id:
            self._is_oauth = True
            self._oauth_token = oauth_token
            self._oauth_cloud_id = cloud_id
            self._client = Confluence(
                url=f"https://api.atlassian.com/ex/confluence/{cloud_id}",
                token=oauth_token,
                cloud=True,
            )
            return

        # Fallback: Basic Auth
        token = self._resolve_token(config.instance_name)
        username = config.username or self._resolve_username(config.instance_name)
        self._client = Confluence(
            url=config.url,
            username=username,
            password=token,
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )

    @classmethod
    def _from_oauth(cls, cloud_id: str, access_token: str) -> ConfluenceClient:
        """Create ConfluenceClient using OAuth 2.0 Bearer token.

        Uses api.atlassian.com/ex/confluence/{cloudId} as base URL (required for OAuth).
        """
        from atlassian import Confluence

        obj = object.__new__(cls)
        obj._config = None
        obj._is_oauth = True
        obj._oauth_token = access_token
        obj._oauth_cloud_id = cloud_id
        obj._client = Confluence(
            url=f"https://api.atlassian.com/ex/confluence/{cloud_id}",
            token=access_token,
            cloud=True,
        )
        return obj

    # ── Publishing ────────────────────────────────────────────────────

    def create_page(
        self,
        title: str,
        body: str,
        parent_id: str | None = None,
        space: str | None = None,
    ) -> PageContent:
        """Create a page. Uses config.space_key unless space is overridden.

        ``body`` is markdown, converted to Confluence storage format
        (RAISE-1679) before upload.
        """
        target_space = space or (self._config.space_key if self._config else "")
        storage_body = markdown_to_storage(body)
        try:
            if self._is_oauth:
                space_id = self._get_space_id(target_space)
                payload: dict[str, Any] = {
                    "spaceId": space_id,
                    "status": "current",
                    "title": title,
                    "body": {"representation": "storage", "value": storage_body},
                }
                if parent_id:
                    payload["parentId"] = parent_id
                return self._parse_page_v2(self._v2("POST", "/pages", json=payload))
            raw: dict[str, Any] = self._client.create_page(  # type: ignore[no-untyped-call]
                space=target_space,
                title=title,
                body=storage_body,
                parent_id=parent_id,
                type="page",
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"create_page({title!r})") from e

    def update_page(
        self,
        page_id: str,
        title: str,
        body: str,
    ) -> PageContent:
        """Update an existing page by ID.

        ``body`` is markdown, converted to Confluence storage format
        (RAISE-1679) before upload.
        """
        storage_body = markdown_to_storage(body)
        try:
            if self._is_oauth:
                current = self._v2("GET", f"/pages/{page_id}")
                version = int((current.get("version") or {}).get("number", 0)) + 1
                return self._parse_page_v2(
                    self._v2(
                        "PUT",
                        f"/pages/{page_id}",
                        json={
                            "id": page_id,
                            "version": {"number": version},
                            "status": "current",
                            "title": title,
                            "body": {
                                "representation": "storage",
                                "value": storage_body,
                            },
                        },
                    )
                )
            raw: dict[str, Any] = self._client.update_page(  # type: ignore[no-untyped-call]
                page_id=page_id,
                title=title,
                body=storage_body,
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"update_page({page_id})") from e

    def get_page_by_id(self, page_id: str) -> PageContent:
        """Get full page content by ID."""
        try:
            if self._is_oauth:
                return self._parse_page_v2(
                    self._v2(
                        "GET", f"/pages/{page_id}", params={"body-format": "storage"}
                    )
                )
            raw: dict[str, Any] = self._client.get_page_by_id(  # type: ignore[no-untyped-call]
                page_id=page_id,
                expand="body.storage,version,space,ancestors",
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
        target_space = space or (self._config.space_key if self._config else "")
        try:
            if self._is_oauth:
                space_id = self._get_space_id(target_space)
                data = self._v2(
                    "GET",
                    "/pages",
                    params={
                        "title": title,
                        "space-id": space_id,
                        "body-format": "storage",
                        "limit": 1,
                    },
                )
                results: list[dict[str, Any]] = data.get("results", [])
                return self._parse_page_v2(results[0]) if results else None
            # Suppress atlassian-python-api's log.error("Can't find '...' page")
            # emitted on not-found — returning None is valid and handled by callers.
            atl_log = logging.getLogger("atlassian.confluence")
            prev_level = atl_log.level
            atl_log.setLevel(logging.CRITICAL)
            try:
                result = self._client.get_page_by_title(  # type: ignore[no-untyped-call]
                    space=target_space,
                    title=title,
                    expand="body.storage,version,space,ancestors",
                )
            finally:
                atl_log.setLevel(prev_level)
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
            if self._is_oauth:
                data = self._v2(
                    "GET", "/spaces", params={"keys": space_key, "limit": 1}
                )
                results = data.get("results", [])
                if not results:
                    return None
                homepage_id = results[0].get("homepageId")
                return str(homepage_id) if homepage_id else None
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

    def delete_page(self, page_id: str) -> None:
        """Delete a page by ID."""
        try:
            self._client.remove_page(page_id)  # type: ignore[no-untyped-call]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"delete_page({page_id})") from e

    def add_comment(self, page_id: str, body: str) -> None:
        """Add a page-level comment."""
        try:
            self._client.add_comment(page_id, body)  # type: ignore[no-untyped-call]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"add_comment({page_id})") from e

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        """Return page-level comments."""
        try:
            raw: dict[str, Any] = self._client.get_page_comments(
                page_id, expand="body.storage"
            )  # type: ignore[no-untyped-call]
            results: list[dict[str, Any]] = raw.get("results", [])
            return [
                CommentSummary(
                    id=str(r["id"]),
                    body=r.get("body", {}).get("storage", {}).get("value", ""),
                )
                for r in results
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_comments({page_id})") from e

    def upload_attachment(
        self,
        page_id: str,
        file_path: str,
        content_type: str,
        comment: str | None,
    ) -> str:
        """Upload a file attachment to a page and return the download URL."""
        try:
            raw: dict[str, Any] = self._client.attach_file(  # type: ignore[no-untyped-call]
                filename=file_path,
                content_type=content_type,
                page_id=page_id,
                comment=comment,
            )
            results = raw.get("results")
            if not results:
                raise ConfluenceApiError(
                    f"upload_attachment({page_id}): empty results from attach_file"
                )
            base = raw.get("_links", {}).get("base", "")
            return base + results[0]["_links"]["download"]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"upload_attachment({page_id})") from e

    def append_attachment_macro(self, page_id: str, filename: str) -> PageContent:
        """Append a view-file structured macro for filename to the end of page body.

        Calls self._client.update_page() (atlassian lib) directly to avoid
        markdown_to_storage() corrupting the existing storage XHTML (D2).
        """
        page = self.get_page_by_id(page_id)
        macro = (
            '<ac:structured-macro ac:name="view-file" ac:schema-version="1">'
            f'<ac:parameter ac:name="name">'
            f'<ri:attachment ri:filename="{filename}"/>'
            "</ac:parameter>"
            "</ac:structured-macro>"
        )
        try:
            raw: dict[str, Any] = self._client.update_page(  # type: ignore[no-untyped-call]
                page_id=page_id,
                title=page.title,
                body=page.content + macro,
            )
            return self._parse_page(raw)
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"append_attachment_macro({page_id})") from e

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        """Return attachments on a page."""
        try:
            raw: dict[str, Any] = self._client.get_attachments_from_content(  # type: ignore[no-untyped-call]
                page_id
            )
            base = raw.get("_links", {}).get("base", "")
            results: list[dict[str, Any]] = raw.get("results", [])
            return [
                AttachmentSummary(
                    id=r["id"],
                    filename=r["title"],
                    size=r.get("extensions", {}).get("fileSize", 0),
                    media_type=r.get("extensions", {}).get("mediaType", ""),
                    url=base + r["_links"]["download"],
                )
                for r in results
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_attachments({page_id})") from e

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
            if self._is_oauth:
                # CQL search via REST API v1 tunnel (still supported with OAuth)
                raw = self._v2_rest(
                    "GET",
                    "/rest/api/search",
                    params={"cql": effective_cql, "limit": limit},
                )
                return [
                    PageSummary(
                        id=str(r["content"]["id"]),
                        title=r["content"].get("title", ""),
                        url=r.get("url", ""),
                        space_key=r["content"].get("space", {}).get("key", ""),
                    )
                    for r in raw.get("results", [])
                    if "content" in r
                ]
            raw: dict[str, Any] = self._client.cql(effective_cql, limit=limit)  # type: ignore[no-untyped-call]
            return [
                PageSummary(
                    id=str(r["content"]["id"]),
                    title=r["content"].get("title", ""),
                    url=r.get("url", ""),
                    space_key=r["content"].get("space", {}).get("key", ""),
                )
                for r in raw.get("results", [])
                if "content" in r
            ]
        except ConfluenceError:
            raise
        except Exception as e:
            raise self._map_error(e, f"search({effective_cql!r})") from e

    def health(self) -> AdapterHealth:
        """Check connectivity by listing 1 space."""
        try:
            if self._is_oauth:
                self._v2("GET", "/spaces", params={"limit": 1})
                return AdapterHealth(name="confluence", healthy=True)
            self._client.get_all_spaces(limit=1)  # type: ignore[no-untyped-call]
            return AdapterHealth(name="confluence", healthy=True)
        except Exception as e:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return AdapterHealth(name="confluence", healthy=False, message=str(e))

    # ── OAuth v2 helpers ──────────────────────────────────────────────

    def _v2(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """HTTP request to Confluence REST API v2 via OAuth Bearer."""
        import requests

        url = f"https://api.atlassian.com/ex/confluence/{self._oauth_cloud_id}/wiki/api/v2{path}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._oauth_token}",
            "Accept": "application/json",
        }
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
        r = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        r.raise_for_status()
        result: dict[str, Any] = r.json() if r.content else {}
        return result

    def _v2_rest(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """HTTP request to Confluence REST API v1 tunnel via OAuth Bearer."""
        import requests

        url = f"https://api.atlassian.com/ex/confluence/{self._oauth_cloud_id}{path}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._oauth_token}",
            "Accept": "application/json",
        }
        r = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        r.raise_for_status()
        result: dict[str, Any] = r.json() if r.content else {}
        return result

    def _get_space_id(self, space_key: str) -> str:
        """Resolve space key → v2 space ID (cached per instance)."""
        if not hasattr(self, "_space_id_cache"):
            self._space_id_cache: dict[str, str] = {}
        if space_key not in self._space_id_cache:
            data = self._v2("GET", "/spaces", params={"keys": space_key, "limit": 1})
            results = data.get("results", [])
            if not results:
                raise ConfluenceApiError(f"Space {space_key!r} not found via OAuth")
            self._space_id_cache[space_key] = str(results[0]["id"])
        return self._space_id_cache[space_key]

    @staticmethod
    def _parse_page_v2(raw: dict[str, Any]) -> PageContent:
        """Convert Confluence REST API v2 response to PageContent."""
        links = raw.get("_links", {})
        base_url = links.get("base", "")
        webui = links.get("webui", "")
        url = f"{base_url}{webui}" if base_url and webui else webui

        body = raw.get("body", {})
        content = body.get("storage", {}).get("value", "") if body else ""
        version_num: int = int((raw.get("version") or {}).get("number", 1))

        return PageContent(
            id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            content=content,
            url=url,
            space_key="",  # v2 uses spaceId — not mapped back to key
            version=version_num,
        )

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
    def _resolve_oauth_token(instance_name: str) -> str:
        """OAuth 2.0 Bearer token. Returns '' if absent — silent fallback to Basic Auth.

        Order: CONFLUENCE_OAUTH_ACCESS_TOKEN_{INSTANCE} → CONFLUENCE_OAUTH_ACCESS_TOKEN → ''.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        return os.environ.get(
            f"CONFLUENCE_OAUTH_ACCESS_TOKEN_{env_suffix}"
        ) or os.environ.get("CONFLUENCE_OAUTH_ACCESS_TOKEN", "")

    @staticmethod
    def _resolve_cloud_id(instance_name: str) -> str:
        """Atlassian cloud ID for OAuth. Returns '' if absent.

        Order: CONFLUENCE_CLOUD_ID_{INSTANCE} → CONFLUENCE_CLOUD_ID → ''.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        return os.environ.get(f"CONFLUENCE_CLOUD_ID_{env_suffix}") or os.environ.get(
            "CONFLUENCE_CLOUD_ID", ""
        )

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

        ancestors: list[dict[str, Any]] = raw.get("ancestors") or []
        parent: dict[str, Any] = ancestors[-1] if ancestors else {}
        parent_id: str | None = str(parent["id"]) if parent.get("id") else None
        parent_title: str | None = str(parent["title"]) if parent.get("title") else None

        return PageContent(
            id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            content=content,
            url=url,
            space_key=space_key,
            version=version_num,
            parent_id=parent_id,
            parent_title=parent_title,
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
