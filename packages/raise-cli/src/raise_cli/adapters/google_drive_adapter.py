"""Google Drive DocumentationTarget adapter (s6140.11, s6716.1, S8331.4).

Auth: OAuth refresh_token from GOOGLE_DRIVE_REFRESH_TOKEN env var,
injected per-user by hermes_raise._build_env from identity_map.db.

Read support (s6716.1):
  - Google Docs    → Docs API → Markdown
  - Google Sheets  → Drive export → CSV
  - Google Slides  → Drive export → plain text
  - PDF            → GoogleDriveNotFoundError (not yet supported)
  - image/video/audio → GoogleDriveNotFoundError (binary type)
  - everything else → Drive alt=media → UTF-8 decode or error
Write operations return safe defaults (read-only adapter).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from raise_cli.adapters.google_drive_exceptions import (
    GoogleDriveApiError,
    GoogleDriveAuthError,
    GoogleDriveNotFoundError,
)
from raise_cli.adapters.models import AdapterHealth
from raise_cli.adapters.models.docs import (
    AttachmentSummary,
    CommentSummary,
    PageContent,
    PageSummary,
    PublishResult,
)

_logger = logging.getLogger(__name__)

_DOCS_API_BASE = "https://docs.googleapis.com/v1/documents"
_DRIVE_API_BASE = "https://www.googleapis.com/drive/v3/files"

# Google Workspace types that can be exported via Drive Files API
_EXPORT_MIME: dict[str, str] = {
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}

# Web URLs per mimeType — fallback to drive.google.com/file/d/{id}/view
_FILE_URL_TEMPLATES: dict[str, str] = {
    "application/vnd.google-apps.document": "https://docs.google.com/document/d/{id}/edit",
    "application/vnd.google-apps.spreadsheet": "https://docs.google.com/spreadsheets/d/{id}/edit",
    "application/vnd.google-apps.presentation": "https://docs.google.com/presentation/d/{id}/edit",
}
_DRIVE_FILE_URL = "https://drive.google.com/file/d/{id}/view"

_HEADING_MAP: dict[str, str] = {
    "HEADING_1": "#",
    "HEADING_2": "##",
    "HEADING_3": "###",
    "HEADING_4": "####",
    "TITLE": "#",
}


def _file_url(identifier: str, mime_type: str) -> str:
    template = _FILE_URL_TEMPLATES.get(mime_type, _DRIVE_FILE_URL)
    return template.format(id=identifier)


def _para_to_md(para: dict[str, Any]) -> str:
    """Convert a Docs API paragraph element to a Markdown line."""
    style = para.get("paragraphStyle", {}).get("namedStyleType", "")
    prefix = _HEADING_MAP.get(style, "")
    text = "".join(
        el.get("textRun", {}).get("content", "") for el in para.get("elements", [])
    ).rstrip("\n")
    if not text.strip():
        return ""
    if "bullet" in para:
        return f"- {text}"
    return f"{prefix} {text}".strip() if prefix else text


def _table_to_md(table: dict[str, Any]) -> str:
    """Convert a Docs API table element to Markdown pipe format."""
    rows = table.get("tableRows", [])
    if not rows:
        return ""
    lines: list[str] = []
    for i, row in enumerate(rows):
        cells = [
            " ".join(
                el.get("textRun", {}).get("content", "").strip()
                for p in cell.get("content", [])
                for el in p.get("paragraph", {}).get("elements", [])
            )
            for cell in row.get("tableCells", [])
        ]
        lines.append("| " + " | ".join(cells) + " |")
        if i == 0:
            lines.append("| " + " | ".join("---" for _ in cells) + " |")
    return "\n".join(lines)


def _to_markdown(content: list[dict[str, Any]]) -> str:
    """Convert Docs API body.content list to Markdown string."""
    parts: list[str] = []
    for element in content:
        if "paragraph" in element:
            md = _para_to_md(element["paragraph"])
            if md:
                parts.append(md)
        elif "table" in element:
            md = _table_to_md(element["table"])
            if md:
                parts.append(md)
    return "\n\n".join(parts)


def _check_auth_and_status(resp: httpx.Response, identifier: str) -> None:
    """Raise typed error for non-2xx responses."""
    if resp.status_code in (401, 403):
        raise GoogleDriveAuthError(
            f"Access denied for {identifier} — token may be expired or revoked"
        )
    if resp.status_code == 404:
        raise GoogleDriveNotFoundError(f"Document not found: {identifier}")
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise GoogleDriveApiError(
            f"Google Drive API error {exc.response.status_code}: {identifier}",
            status_code=exc.response.status_code,
        ) from exc


class GoogleDriveAdapter:
    """Read-only DocumentationTarget for Google Drive files.

    Reads GOOGLE_DRIVE_REFRESH_TOKEN, GOOGLE_OAUTH_CLIENT_ID,
    and GOOGLE_OAUTH_CLIENT_SECRET from the environment.
    Token is injected per-user by hermes_raise._build_env.

    Supported types (s6716.1):
    - Google Docs → Docs API → Markdown
    - Google Sheets → CSV export
    - Google Slides → plain text export
    - text/* and other text-encodable files → read in memory via alt=media
    - PDF → error (not yet supported)
    - image/video/audio → error (binary type)
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        import importlib.util

        try:
            _has_google = importlib.util.find_spec("google.oauth2") is not None
        except (ModuleNotFoundError, ValueError):
            _has_google = False
        if not _has_google:
            raise ImportError(
                "google-auth is required for GoogleDriveAdapter. "
                "Install with: pip install 'raise-cli[gdrive]'"
            )

        self._refresh_token = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN", "")
        self._client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
        self._client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

        if not self._refresh_token:
            raise GoogleDriveAuthError(
                "GOOGLE_DRIVE_REFRESH_TOKEN not set — user has not completed OAuth."
            )

    def _get_access_token(self) -> str:
        """Exchange refresh_token for a fresh access_token."""
        from google.auth.transport.requests import Request  # type: ignore[import-untyped]  # noqa: I001
        from google.oauth2.credentials import Credentials  # type: ignore[import-untyped]

        creds = Credentials(
            token=None,
            refresh_token=self._refresh_token,
            token_uri="https://oauth2.googleapis.com/token",  # noqa: S106
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=["https://www.googleapis.com/auth/drive.file"],
        )
        creds.refresh(Request())
        return str(creds.token)

    def provision_workspace_doc(
        self,
        workspace_id: str,
        workspace_name: str,
        template_doc_id: str | None = None,
    ) -> str | None:
        """Create or retrieve a workspace Doc in Drive. Returns doc_id or None on failure.

        Idempotent: if a doc with appProperties.workspaceId == workspace_id already
        exists, returns its id without creating a duplicate.
        Failure is non-blocking — Drive unavailability returns None rather than raising.
        """
        try:
            existing_id = self.get_workspace_doc_id(workspace_id)
            if existing_id:
                return existing_id

            token = self._get_access_token()

            if template_doc_id:
                resp = httpx.post(
                    f"{_DRIVE_API_BASE}/{template_doc_id}/copy",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "name": workspace_name,
                        "appProperties": {"workspaceId": workspace_id},
                    },
                    timeout=30.0,
                )
            else:
                resp = httpx.post(
                    _DRIVE_API_BASE,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "name": workspace_name,
                        "mimeType": "application/vnd.google-apps.document",
                        "appProperties": {"workspaceId": workspace_id},
                    },
                    timeout=30.0,
                )
            resp.raise_for_status()
            doc_id = str(resp.json()["id"])
            self._init_doc_marker(doc_id)
            return doc_id
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Drive provision failed (non-blocking): %s", exc)
            return None

    def _init_doc_marker(self, doc_id: str) -> None:
        """Insert the memory append sentinel into a freshly created workspace Doc.

        Uses insertText at index 1 (start of body). Non-blocking on failure —
        the doc will simply have no marker and memory writes will be no-ops until
        the marker is seeded by other means.
        """
        marker = "{{MEMORY_APPEND_MARKER}}"
        try:
            token = self._get_access_token()
            httpx.post(
                f"{_DOCS_API_BASE}/{doc_id}:batchUpdate",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "requests": [
                        {"insertText": {"location": {"index": 1}, "text": marker}}
                    ]
                },
                timeout=30.0,
            ).raise_for_status()
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Doc marker init failed (non-blocking): %s", exc)

    def get_workspace_doc_id(self, workspace_id: str) -> str | None:
        """Return existing doc_id for workspace_id from Drive appProperties, or None.

        Searches Drive for a file where appProperties.workspaceId == workspace_id.
        Returns None on any failure — callers should treat this as "not found yet".
        """
        try:
            token = self._get_access_token()
            q = f"appProperties has {{key='workspaceId' and value='{workspace_id}'}}"
            resp = httpx.get(
                _DRIVE_API_BASE,
                params={"q": q, "spaces": "drive", "fields": "files(id, name)"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
            resp.raise_for_status()
            files = resp.json().get("files", [])
            if files:
                return str(files[0]["id"])
            return None
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Drive lookup failed: %s", exc)
            return None

    def _get_file_metadata(self, identifier: str, token: str) -> dict[str, Any]:
        """Fetch mimeType and name for a Drive file."""
        resp = httpx.get(
            f"{_DRIVE_API_BASE}/{identifier}",
            params={"fields": "mimeType,name"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        _check_auth_and_status(resp, identifier)
        return resp.json()  # type: ignore[no-any-return]

    def _get_google_doc(self, identifier: str, name: str, token: str) -> PageContent:
        """Read a Google Doc via Docs API and convert to Markdown."""
        resp = httpx.get(
            f"{_DOCS_API_BASE}/{identifier}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        _check_auth_and_status(resp, identifier)
        doc = resp.json()
        return PageContent(
            id=identifier,
            title=doc["title"],
            content=_to_markdown(doc["body"]["content"]),
            url=_file_url(identifier, "application/vnd.google-apps.document"),
        )

    def _get_export(
        self, identifier: str, name: str, mime_type: str, token: str
    ) -> PageContent:
        """Export a Google Workspace file (Sheets→CSV, Slides→text) via Drive API."""
        export_mime = _EXPORT_MIME[mime_type]
        resp = httpx.get(
            f"{_DRIVE_API_BASE}/{identifier}/export",
            params={"mimeType": export_mime},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        _check_auth_and_status(resp, identifier)
        return PageContent(
            id=identifier,
            title=name,
            content=resp.text,
            url=_file_url(identifier, mime_type),
        )

    def _read_native(
        self, identifier: str, name: str, mime_type: str, token: str
    ) -> PageContent:
        """Read a non-Workspace file via alt=media. Decodes as UTF-8 or raises."""
        resp = httpx.get(
            f"{_DRIVE_API_BASE}/{identifier}",
            params={"alt": "media"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        _check_auth_and_status(resp, identifier)
        try:
            content = resp.content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GoogleDriveNotFoundError(
                f"File '{identifier}' (type: {mime_type}) cannot be decoded as text — "
                "it appears to be a binary file"
            ) from exc
        return PageContent(
            id=identifier,
            title=name,
            content=content,
            url=_file_url(identifier, mime_type),
        )

    def get_page(self, identifier: str) -> PageContent:
        """Fetch a Drive file by ID and return its content as text.

        Dispatches by mimeType:
        - Google Docs → Docs API → Markdown
        - Sheets/Slides → Drive export (CSV / plain text)
        - PDF → GoogleDriveNotFoundError (not yet supported)
        - image/video/audio → GoogleDriveNotFoundError (binary type)
        - everything else → alt=media read; fails if not UTF-8 decodable
        """
        token = self._get_access_token()
        meta = self._get_file_metadata(identifier, token)
        mime = meta["mimeType"]
        name = meta["name"]

        if mime == "application/vnd.google-apps.document":
            return self._get_google_doc(identifier, name, token)
        if mime in _EXPORT_MIME:
            return self._get_export(identifier, name, mime, token)
        if mime == "application/pdf":
            raise GoogleDriveNotFoundError(
                f"PDF files are not yet supported: {identifier}"
            )
        if mime.startswith(("image/", "video/", "audio/")):
            raise GoogleDriveNotFoundError(
                f"Binary file type '{mime}' is not supported: {identifier}"
            )
        return self._read_native(identifier, name, mime, token)

    def append_to_doc(self, doc_id: str, marker: str, replacement: str) -> None:
        """Replace *marker* text in a Google Doc via Docs API batchUpdate.

        Uses replaceAllText to substitute *marker* with *replacement*.
        If the marker is absent (occurrencesChanged=0) the call is a no-op —
        this is expected and not treated as an error.

        Raises GoogleDriveAuthError / GoogleDriveApiError on API failure.
        Callers wrapping this for fire-and-forget use should catch all exceptions.
        """
        token = self._get_access_token()
        resp = httpx.post(
            f"{_DOCS_API_BASE}/{doc_id}:batchUpdate",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {"text": marker, "matchCase": True},
                            "replaceText": replacement,
                        }
                    }
                ]
            },
            timeout=30.0,
        )
        _check_auth_and_status(resp, doc_id)

    def can_publish(
        self,
        doc_type: str | None,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> bool:
        """Always False — adapter is read-only, regardless of format (RAISE-16870 D5)."""
        return False

    def publish(
        self,
        doc_type: str | None,
        content: str,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> PublishResult:
        """Not supported — returns failure result, regardless of format (RAISE-16870 D5)."""
        return PublishResult(success=False, message="Google Drive adapter is read-only")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Not supported — returns empty list."""
        return []

    def health(self) -> AdapterHealth:
        """Return health based on token presence."""
        return AdapterHealth(name="google_drive", healthy=bool(self._refresh_token))

    def add_label(self, page_id: str, name: str) -> None:
        """Not supported."""

    def get_labels(self, page_id: str) -> list[str]:
        """Not supported — returns empty list."""
        return []

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        """Not supported — returns empty list."""
        return []

    def delete_page(self, page_id: str) -> None:
        """Not supported."""

    def add_comment(self, page_id: str, body: str) -> None:
        """Not supported."""

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        """Not supported — returns empty list."""
        return []

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str:
        """Not supported — returns empty string."""
        return ""

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        """Not supported — returns empty list."""
        return []

    def embed_attachment(self, page_id: str, filename: str) -> PageContent:
        """Not supported."""
        raise GoogleDriveNotFoundError(
            f"embed_attachment not supported by GoogleDriveAdapter: {page_id}/{filename}"
        )
