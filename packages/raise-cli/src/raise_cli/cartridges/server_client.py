"""HTTP client for the cartridge server API (S5877.4).

Wraps /api/v2/cartridges endpoints. Pattern follows ApiGraphBackend.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from raise_cli.cartridges.server_models import (
    CartridgeDetail,
    CartridgeInfo,
    CartridgeInstallResult,
    ExtractionJobStatus,
    ExtractionRequest,
    OrgInstallResponse,
    ProjectCartridgeInfo,
    PublicCartridgeItem,
    PublishRequest,
)

logger = logging.getLogger(__name__)

__all__ = ["CartridgeServerClient", "CartridgeServerError"]


class CartridgeServerError(Exception):
    """Error communicating with the cartridge server."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class CartridgeServerClient:
    """Sync HTTP client for the cartridge registry API.

    Args:
        server_url: Base URL of raise-server (e.g. "http://localhost:8000").
        api_key: API key for authentication (rsk_ prefix).
    """

    def __init__(self, server_url: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=120.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def list_remote(self) -> list[CartridgeInfo]:
        """List all cartridges available on the server."""
        data = self._get("/api/v2/cartridges")
        return [CartridgeInfo.model_validate(item) for item in data]

    def list_installed(self) -> list[CartridgeInfo]:
        """List the org's INSTALLED cartridges — the source of truth (RAISE-9781).

        Distinct from ``list_remote`` (whole registry): this hits
        ``/api/v2/cartridges/installed``, which is authoritative for what is
        actually installed for the org (names and node counts).
        """
        data = self._get("/api/v2/cartridges/installed")
        return [CartridgeInfo.model_validate(item) for item in data]

    def list_public(
        self, limit: int = 100, offset: int = 0
    ) -> list[PublicCartridgeItem]:
        """List all public cartridges across all orgs (S-KC4.6)."""
        data = self._get(f"/api/v2/cartridges/public?limit={limit}&offset={offset}")
        return [
            PublicCartridgeItem.model_validate(item) for item in data.get("items", [])
        ]

    def list_project_assignments(self, project_id: str) -> list[ProjectCartridgeInfo]:
        """List cartridges assigned to a project with policies (S-KC4.8)."""
        data = self._get(f"/api/v2/projects/{project_id}/cartridges")
        return [ProjectCartridgeInfo.model_validate(item) for item in data]

    def fetch_cartridge(self, name: str) -> CartridgeDetail:
        """Fetch a cartridge by name with all its nodes."""
        data = self._get(f"/api/v2/cartridges/{name}")
        return CartridgeDetail.model_validate(data)

    def publish_cartridge(self, request: PublishRequest) -> CartridgeInstallResult:
        """Publish a cartridge to the server registry."""
        data = self._post("/api/v2/cartridges", json=request.model_dump())
        return CartridgeInstallResult.model_validate(data)

    def org_install(self, name: str) -> OrgInstallResponse:
        """Register an org-level install on the server (S-KC4.7).

        Idempotent: returns 201 on first install, 200 on re-install.
        """
        data = self._post(f"/api/v2/cartridges/{name}/install", json={})
        return OrgInstallResponse.model_validate(data)

    def org_uninstall(self, name: str) -> None:
        """Remove the org's install from the server (S-KC4.7).

        Raises CartridgeServerError with status_code=409 and detail
        containing blocking_projects if project assignments exist.
        """
        self._delete(f"/api/v2/cartridges/{name}/install")

    def delete_remote(self, name: str) -> None:
        """Delete a cartridge from the server registry."""
        self._delete(f"/api/v2/cartridges/{name}")

    def submit_extraction(
        self, name: str, request: ExtractionRequest
    ) -> ExtractionJobStatus:
        """Submit an async LLM extraction job for a cartridge."""
        data = self._post(
            f"/api/v2/cartridges/{name}/extract", json=request.model_dump()
        )
        return ExtractionJobStatus.model_validate(data)

    def poll_extraction_job(self, job_id: str) -> ExtractionJobStatus:
        """Poll an extraction job's status."""
        data = self._get(f"/api/v2/cartridges/jobs/{job_id}")
        return ExtractionJobStatus.model_validate(data)

    def _get(self, url: str) -> Any:
        try:
            response = self._client.get(url=url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise self._wrap_status_error(e, url) from e
        except httpx.HTTPError as e:
            raise CartridgeServerError(f"Server unreachable or timeout: {e}") from e
        return response.json()

    def _post(self, url: str, json: Any) -> Any:
        try:
            response = self._client.post(url=url, json=json)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise self._wrap_status_error(e, url) from e
        except httpx.HTTPError as e:
            raise CartridgeServerError(f"Server unreachable or timeout: {e}") from e
        return response.json()

    def _delete(self, url: str) -> None:
        try:
            response = self._client.delete(url=url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise self._wrap_status_error(e, url) from e
        except httpx.HTTPError as e:
            raise CartridgeServerError(f"Server unreachable or timeout: {e}") from e

    def _wrap_status_error(
        self, error: httpx.HTTPStatusError, url: str
    ) -> CartridgeServerError:
        status = error.response.status_code
        if status == 401:
            return CartridgeServerError(
                "Authentication failed — check RAISE_API_KEY",
                status_code=401,
            )
        if status == 403:
            return CartridgeServerError(
                "Pro plan required for this operation",
                status_code=403,
            )
        if status == 404:
            return CartridgeServerError(
                f"Cartridge not found at {url}",
                status_code=404,
            )
        if status == 409:
            detail = self._safe_json(error.response)
            return CartridgeServerError(
                detail.get("detail", {}).get("message", f"Conflict at {url}")
                if isinstance(detail.get("detail"), dict)
                else f"Conflict at {url}",
                status_code=409,
                detail=detail.get("detail")
                if isinstance(detail.get("detail"), dict)
                else None,
            )
        if status == 429:
            return CartridgeServerError(
                "Delete rate limit exceeded — too many deletions in the last hour. "
                "Try again later.",
                status_code=429,
            )
        return CartridgeServerError(
            f"Server error {status}: {error}",
            status_code=status,
        )

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict[str, Any]:
        try:
            return response.json()  # type: ignore[no-any-return]
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return {}
