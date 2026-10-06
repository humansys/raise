"""Platform documentation target -- publishes HTML artifacts to raise-server.

Implements DocumentationTarget for the RaiSE platform. Used with
``rai docs publish --target platform`` to POST HTML content to the
server's artifact endpoint (POST /api/v1/artifacts/html).

Credentials are resolved via ``get_server_credentials()`` (env vars or
~/.rai/server.json).

RAISE-16621
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from raise_cli.adapters.models.docs import (
    AttachmentSummary,
    CommentSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.config.server import get_server_credentials

logger = logging.getLogger(__name__)

_ARTIFACT_ENDPOINT = "/api/v1/artifacts/html"
_HEALTH_ENDPOINT = "/api/v1/health"
_TIMEOUT_SECONDS = 30


class _StaleRemoteIdError(Exception):
    """Internal signal: PUT 404'd on a remote_id the server no longer has.

    Caught in publish() to trigger the create fallback (RAISE-16660 D4).
    """


class PlatformDocsTarget:
    """Publishes HTML artifacts to the RaiSE platform server.

    No-arg constructor for entry point discovery. Credentials are resolved
    lazily from env vars or ~/.rai/server.json via ``get_server_credentials()``.
    """

    def __init__(self) -> None:
        creds = get_server_credentials()
        if creds is not None:
            self._server_url: str | None = creds[0]
            self._api_key: str | None = creds[1]
        else:
            self._server_url = None
            self._api_key = None

    # -- DocumentationTarget protocol ----------------------------------------

    def can_publish(
        self,
        doc_type: str | None,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> bool:
        """True if format is html and metadata contains a title (RAISE-16870 D2).

        doc_type is purely semantic here (story-design/adr/etc.) -- it no
        longer gates platform publishing. The old doc_type=="html" sentinel
        (_SUPPORTED_DOC_TYPES) is removed; format is the sole content signal.
        """
        if format != "html":
            return False
        return "title" in metadata

    def publish(
        self,
        doc_type: str | None,
        content: str,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> PublishResult:
        """POST or PUT HTML content to the platform server artifact endpoint.

        When ``metadata['remote_id']`` is present (injected by CompositeDocTarget
        from the docs_sync registry, RAISE-5894), PUT-updates that artifact
        instead of creating a new one (RAISE-16660 D1/D4). A 404 on the PUT
        (stale or deleted remote_id) falls back to create -- the CLI side, not
        the server, owns upsert-on-missing-id recovery.
        """
        if self._server_url is None or self._api_key is None:
            return PublishResult(
                success=False,
                message=(
                    "Platform server not configured. "
                    "Set RAISE_SERVER_URL and RAISE_API_KEY environment variables "
                    "or run 'rai connect'."
                ),
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }
        remote_id = metadata.get("remote_id")
        if remote_id:
            try:
                return self._update(remote_id, content, metadata, headers)
            except _StaleRemoteIdError:
                pass  # fall through to create

        return self._create(doc_type, content, metadata, headers)

    def _update(
        self,
        remote_id: str,
        content: str,
        metadata: dict[str, Any],
        headers: dict[str, str],
    ) -> PublishResult:
        """PUT an update to an existing artifact. Raises _StaleRemoteIdError on 404."""
        url = f"{self._server_url}{_ARTIFACT_ENDPOINT}/{remote_id}"
        payload: dict[str, Any] = {
            "title": metadata.get("title", ""),
            "html_content": content,
            "metadata": {},
        }
        try:
            response = httpx.put(
                url,
                json=payload,
                headers=headers,
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            return PublishResult(
                success=True,
                url=data.get("viewer_url") or url,
                message="Updated on platform",
                remote_id=str(data.get("id", remote_id)),
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise _StaleRemoteIdError from exc
            if exc.response.status_code == 401:
                return PublishResult(
                    success=False,
                    message="Platform server rejected credentials (401). Run 'rai connect' to refresh them.",
                )
            logger.debug("Platform server HTTP error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Platform server returned HTTP {exc.response.status_code}: {exc.response.text}",
            )
        except httpx.ConnectError as exc:
            logger.debug("Platform server connection error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Cannot connect to platform server at {self._server_url}: {exc}",
            )
        except httpx.HTTPError as exc:
            logger.debug("Platform server error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Platform server error: {exc}",
            )

    def _create(
        self,
        doc_type: str | None,
        content: str,
        metadata: dict[str, Any],
        headers: dict[str, str],
    ) -> PublishResult:
        """POST a new artifact to the platform server artifact endpoint."""
        url = f"{self._server_url}{_ARTIFACT_ENDPOINT}"
        payload: dict[str, str] = {
            "title": metadata.get("title", ""),
            "html_content": content,
            "artifact_type": doc_type or "html",
        }
        project_id = metadata.get("project_id")
        if project_id is not None:
            payload["project_id"] = project_id

        try:
            response = httpx.post(
                url,
                json=payload,
                headers=headers,
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            artifact_url: str = data.get("viewer_url") or data.get("url", "")
            return PublishResult(
                success=True,
                url=artifact_url,
                message="Published to platform",
                remote_id=data.get("id", ""),
            )
        except httpx.ConnectError as exc:
            logger.debug("Platform server connection error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Cannot connect to platform server at {self._server_url}: {exc}",
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                return PublishResult(
                    success=False,
                    message="Platform server rejected credentials (401). Run 'rai connect' to refresh them.",
                )
            logger.debug("Platform server HTTP error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Platform server returned HTTP {exc.response.status_code}: {exc.response.text}",
            )
        except httpx.HTTPError as exc:
            logger.debug("Platform server error: %s", exc)
            return PublishResult(
                success=False,
                message=f"Platform server error: {exc}",
            )

    def get_page(self, identifier: str) -> PageContent:
        """Not supported -- platform target is publish-only."""
        raise NotImplementedError("PlatformDocsTarget does not support get_page")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Not supported -- platform target is publish-only."""
        raise NotImplementedError("PlatformDocsTarget does not support search")

    def health(self) -> AdapterHealth:
        """Ping the platform server for connectivity check."""
        if self._server_url is None or self._api_key is None:
            return AdapterHealth(
                name="platform-docs",
                healthy=False,
                message="Server credentials not configured",
            )
        try:
            url = f"{self._server_url}{_HEALTH_ENDPOINT}"
            response = httpx.get(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return AdapterHealth(name="platform-docs", healthy=True)
        except httpx.HTTPError as exc:
            return AdapterHealth(
                name="platform-docs",
                healthy=False,
                message=f"Server unreachable: {exc}",
            )

    def add_label(self, page_id: str, name: str) -> None:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support add_label")

    def get_labels(self, page_id: str) -> list[str]:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support get_labels")

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        """Not supported."""
        raise NotImplementedError(
            "PlatformDocsTarget does not support get_page_children"
        )

    def delete_page(self, page_id: str) -> None:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support delete_page")

    def add_comment(self, page_id: str, body: str) -> None:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support add_comment")

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support get_comments")

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str:
        """Not supported."""
        raise NotImplementedError(
            "PlatformDocsTarget does not support upload_attachment"
        )

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        """Not supported."""
        raise NotImplementedError("PlatformDocsTarget does not support get_attachments")

    def embed_attachment(self, page_id: str, filename: str) -> PageContent:
        """Not supported."""
        raise NotImplementedError(
            "PlatformDocsTarget does not support embed_attachment"
        )
