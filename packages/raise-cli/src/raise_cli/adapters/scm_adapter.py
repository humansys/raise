"""RaiSE Server SCM adapter — PR/MR + repo operations via server endpoints (S10724.4, S10873.4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from raise_cli.adapters.protocols import ScmPrResult, ScmRepoInfo
from raise_cli.config.server import get_server_credentials


class RaiseServerScmAdapter:
    """SCM adapter that proxies PR/MR and repo operations through raise-server."""

    def __init__(self, project_root: Path | None = None) -> None:
        creds = get_server_credentials()
        if creds is None:
            msg = "Not connected to a RaiSE server. Run `rai connect` first."
            raise ConnectionError(msg)
        self._server_url, self._api_key = creds

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    async def create_pr(
        self,
        *,
        provider: str,
        repo_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str = "",
    ) -> ScmPrResult:
        """Create a PR/MR via server proxy."""
        async with httpx.AsyncClient(base_url=self._server_url, timeout=30) as client:
            resp = await client.post(
                f"/api/v2/git-auth/pr/{provider}",
                headers=self._headers(),
                json={
                    "repo_id": repo_id,
                    "title": title,
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "description": description,
                },
            )
            resp.raise_for_status()
            return self._parse_pr_response(resp.json())

    async def get_pr(
        self,
        *,
        provider: str,
        repo_id: str,
        pr_number: int,
    ) -> ScmPrResult:
        """Get PR/MR details via server proxy."""
        async with httpx.AsyncClient(base_url=self._server_url, timeout=30) as client:
            resp = await client.get(
                f"/api/v2/git-auth/pr/{provider}/{repo_id}/{pr_number}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return self._parse_pr_response(resp.json())

    async def list_repos(
        self,
        *,
        provider: str,
        search: str = "",
        limit: int = 50,
    ) -> list[ScmRepoInfo]:
        """List repositories from connected provider."""
        params: dict[str, str | int] = {"limit": limit}
        if search:
            params["search"] = search
        async with httpx.AsyncClient(base_url=self._server_url, timeout=30) as client:
            resp = await client.get(
                f"/api/v2/git-auth/{provider}/repos",
                headers=self._headers(),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            ScmRepoInfo(
                provider_repo_id=r["provider_repo_id"],
                name=r["name"],
                full_name=r["full_name"],
                visibility=r.get("visibility", "private"),
                default_branch=r.get("default_branch", "main"),
            )
            for r in data.get("repos", [])
        ]

    async def list_branches(
        self,
        *,
        provider: str,
        repo_id: str,
    ) -> list[str]:
        """List branches for a repository."""
        async with httpx.AsyncClient(base_url=self._server_url, timeout=30) as client:
            resp = await client.get(
                f"/api/v2/git-auth/{provider}/branches/{repo_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return data.get("branches", [])

    async def disconnect(
        self,
        *,
        provider: str,
    ) -> bool:
        """Disconnect a git provider."""
        async with httpx.AsyncClient(base_url=self._server_url, timeout=30) as client:
            resp = await client.delete(
                f"/api/v2/git-auth/{provider}/disconnect",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        return data.get("disconnected", False)

    @staticmethod
    def _parse_pr_response(data: dict[str, Any]) -> ScmPrResult:
        return ScmPrResult(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            url=data["url"],
            source_branch=data["source_branch"],
            target_branch=data["target_branch"],
            author=data["author"],
        )
