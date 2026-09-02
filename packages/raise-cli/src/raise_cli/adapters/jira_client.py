"""Jira client wrapper over atlassian-python-api.

Concrete class (NOT Protocol) providing methods for issue CRUD,
search, transitions, relationships, comments, and health.
Consumed by PythonApiJiraAdapter — not directly by skills or CLI.

Optional dependency: ``pip install raise-cli[jira]``

RAISE-1052 (S1052.1)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote

if TYPE_CHECKING:
    from raise_cli.adapters.models.pm import IssueTypeInfo, ProjectInfo, WorkflowState

from raise_cli.adapters.jira_exceptions import (
    JiraAdapterError,
    JiraApiError,
    JiraAuthError,
    JiraNotFoundError,
)


class JiraClient:
    """Wraps atlassian.Jira with auth resolution and error normalization."""

    def __init__(self, url: str, username: str, token: str) -> None:
        try:
            from atlassian import Jira
        except ImportError as exc:
            raise ImportError(
                "atlassian-python-api required for Jira adapter. "
                "Install with: pip install raise-cli[jira]"
            ) from exc

        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        self._url = url
        self._client = Jira(
            url=url,
            username=username,
            password=token,
            cloud=True,
            api_version=3,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )
        # RAISE-3800: backoff_and_retry=True mounts a Retry with connect=None, which
        # causes urllib3 to retry DNS/connection failures with exponential backoff (31s+).
        # Override the adapter so connection errors fail immediately while HTTP rate-limit
        # retry (413/429/503) is preserved.
        _retry = Retry(
            total=None,
            connect=False,
            status=5,
            status_forcelist=[413, 429, 503],
            backoff_factor=1.0,
            backoff_max=1800,
        )
        self._client._session.mount(url, HTTPAdapter(max_retries=_retry))  # pyright: ignore[reportPrivateUsage]

    # ── Auth Resolution ──────────────────────────────────────────────

    @staticmethod
    def _resolve_token(instance_name: str) -> str:
        """Resolve API token from environment.

        Order: JIRA_API_TOKEN_{INSTANCE} -> JIRA_API_TOKEN -> error.
        Instance name is uppercased with hyphens replaced by underscores.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"JIRA_API_TOKEN_{env_suffix}"

        token = os.environ.get(instance_var) or os.environ.get("JIRA_API_TOKEN")
        if not token:
            raise JiraAuthError(
                f"No Jira API token found. Set {instance_var} or "
                "JIRA_API_TOKEN environment variable."
            )
        return token

    @staticmethod
    def _resolve_username(instance_name: str) -> str:
        """Resolve username (email) from environment.

        Order: JIRA_USERNAME_{INSTANCE} -> JIRA_USERNAME -> error.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"JIRA_USERNAME_{env_suffix}"

        username = os.environ.get(instance_var) or os.environ.get("JIRA_USERNAME")
        if not username:
            raise JiraAuthError(
                f"No Jira username found. Set {instance_var} or "
                "JIRA_USERNAME environment variable, or set email in config."
            )
        return username

    # ── OAuth Resolution ─────────────────────────────────────────────

    @staticmethod
    def _resolve_oauth_token(org_name: str) -> str:
        """Resolve OAuth 2.0 Bearer token from environment. Returns empty string if absent.

        Order: JIRA_OAUTH_ACCESS_TOKEN_{ORG} -> JIRA_OAUTH_ACCESS_TOKEN -> "".
        """
        env_suffix = org_name.upper().replace("-", "_")
        return os.environ.get(
            f"JIRA_OAUTH_ACCESS_TOKEN_{env_suffix}"
        ) or os.environ.get("JIRA_OAUTH_ACCESS_TOKEN", "")

    @staticmethod
    def _resolve_cloud_id(org_name: str) -> str:
        """Resolve Atlassian cloud ID from environment. Returns empty string if absent.

        Order: JIRA_CLOUD_ID_{ORG} -> JIRA_CLOUD_ID -> "".
        """
        env_suffix = org_name.upper().replace("-", "_")
        return os.environ.get(f"JIRA_CLOUD_ID_{env_suffix}") or os.environ.get(
            "JIRA_CLOUD_ID", ""
        )

    @classmethod
    def from_oauth(cls, cloud_id: str, access_token: str) -> JiraClient:
        """Create a JiraClient using OAuth 2.0 Bearer token auth.

        Uses api.atlassian.com/ex/jira/{cloudId} as base URL (required for OAuth).
        """
        try:
            from atlassian import Jira
        except ImportError as exc:
            raise ImportError(
                "atlassian-python-api required for Jira adapter. "
                "Install with: pip install raise-cli[jira]"
            ) from exc

        obj = object.__new__(cls)
        obj._url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        obj._client = Jira(
            url=obj._url,
            token=access_token,
            cloud=True,
            api_version=3,
        )
        return obj  # type: ignore[return-value]

    # ── OAuth Refresh ────────────────────────────────────────────────

    @staticmethod
    def _jira_token_expired(token: str) -> bool:
        """Return True if the JWT access token is expired or expires within 60s."""
        import base64 as _b64
        import json as _json
        import time as _time

        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            data = _json.loads(_b64.urlsafe_b64decode(payload))
            return float(_time.time()) > float(data.get("exp", 0)) - 60.0
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return False

    @staticmethod
    def _refresh_jira_oauth_token(
        refresh_token: str, client_id: str, client_secret: str
    ) -> str:
        """Exchange a Jira refresh_token for a new access_token via Atlassian token endpoint.

        Persists the new token to RAISE_USER_ENV_FILE if set, so subsequent
        rai invocations don't refresh again unnecessarily.
        """
        import json as _json
        import urllib.request as _req

        body = _json.dumps(
            {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            }
        ).encode()
        request = _req.Request(
            "https://auth.atlassian.com/oauth/token",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with _req.urlopen(request, timeout=10) as resp:  # noqa: S310  # nosec B310
            data = _json.loads(resp.read())
        new_token = str(data["access_token"])

        # Write back to env file so the next rai invocation skips the refresh call.
        env_file = os.environ.get("RAISE_USER_ENV_FILE", "")
        if env_file:
            import contextlib as _ctx
            from pathlib import Path as _Path

            with _ctx.suppress(Exception):
                path = _Path(env_file)
                if path.exists():
                    lines = path.read_text().splitlines(keepends=True)
                    new_lines = []
                    found = False
                    for line in lines:
                        if line.startswith("JIRA_OAUTH_ACCESS_TOKEN="):
                            new_lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={new_token}\n")
                            found = True
                        else:
                            new_lines.append(line)
                    if not found:
                        new_lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={new_token}\n")
                    path.write_text("".join(new_lines))

        return new_token

    # ── Issue CRUD ───────────────────────────────────────────────────

    def get_issue(self, key: str) -> dict[str, Any]:
        """Get issue by key. Returns full raw dict."""
        try:
            result: dict[str, Any] = self._client.issue(key)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_issue({key})") from e

    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]:
        """Create an issue. Returns raw dict with at least key and id."""
        try:
            result: dict[str, Any] = self._client.create_issue(fields)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "create_issue") from e

    def update_issue(self, key: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update an issue by key. Returns raw response dict."""
        try:
            result: dict[str, Any] = self._client.update_issue(key, {"fields": fields})  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"update_issue({key})") from e

    # ── Project versions / fixVersions ──────────────────────────────

    def get_project_versions(self, project_key: str) -> list[dict[str, Any]]:
        """Return Jira project versions for *project_key*."""
        try:
            result: list[dict[str, Any]] = self._client.get_project_versions(
                project_key
            )  # type: ignore[no-untyped-call]
            return list(result or [])
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_project_versions({project_key})") from e

    def create_project_version(
        self, project_key: str, version_name: str
    ) -> dict[str, Any]:
        """Create a Jira project version by name."""
        try:
            project: dict[str, Any] = self._client.get_project(project_key)  # type: ignore[no-untyped-call]
            project_id = str(project.get("id", ""))
            if not project_id:
                raise JiraApiError(f"Project {project_key} has no id")
            result: dict[str, Any] = self._client.add_version(
                project_key, project_id, version_name
            )  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(
                e, f"create_project_version({project_key}, {version_name!r})"
            ) from e

    # ── Search ───────────────────────────────────────────────────────

    @property
    def _is_cloud(self) -> bool:
        return bool(getattr(self._client, "cloud", False))

    def jql(self, query: str, limit: int = 50, start: int = 0) -> list[dict[str, Any]]:
        """Run a JQL query. Returns list of issue dicts.

        On Jira Cloud, uses enhanced_jql (cursor-based). start > 0 on Cloud
        cursor-walks to skip the first `start` items before returning `limit`.
        On Server/DC, delegates to the offset-based jql endpoint directly.
        """
        try:
            if self._is_cloud:
                return self._jql_cloud(query, limit=limit, start=start)
            raw: dict[str, Any] = self._client.jql(query, limit=limit, start=start)  # type: ignore[no-untyped-call]
            return list(raw.get("issues", []))
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"jql({query!r})") from e

    def _jql_cloud(
        self, query: str, limit: int = 50, start: int = 0
    ) -> list[dict[str, Any]]:
        """Cloud jql via enhanced_jql. Cursor-walks to skip `start` items."""
        next_token: str | None = None
        skipped = 0
        # Walk past the first `start` issues using cursor pagination
        while skipped < start:
            batch = min(50, start - skipped)
            raw: dict[str, Any] = self._client.enhanced_jql(  # type: ignore[no-untyped-call]
                query, limit=batch, nextPageToken=next_token
            )
            page = list(raw.get("issues", []))
            skipped += len(page)
            next_token = raw.get("nextPageToken")
            if raw.get("isLast", True) or not page:
                return []
        raw = self._client.enhanced_jql(query, limit=limit, nextPageToken=next_token)  # type: ignore[no-untyped-call]
        return list(raw.get("issues", []))

    def jql_all(
        self, query: str, page_size: int = 50, cap: int | None = None
    ) -> list[dict[str, Any]]:
        """Fetch ALL matching issues via page-walk (Cloud cursor or Server offset).

        When ``cap`` is set, the walk stops as soon as at least ``cap`` issues
        have been collected (the final page may overshoot — callers truncate).
        This bounds the fetch when only the first N are needed instead of pulling
        the entire result set (RAISE-10763).
        """
        try:
            if self._is_cloud:
                return self._jql_all_cloud(query, page_size, cap)
            return self._jql_all_server(query, page_size, cap)
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"jql_all({query!r})") from e

    def _jql_all_cloud(
        self, query: str, page_size: int = 50, cap: int | None = None
    ) -> list[dict[str, Any]]:
        all_issues: list[dict[str, Any]] = []
        next_token: str | None = None
        while True:
            raw: dict[str, Any] = self._client.enhanced_jql(  # type: ignore[no-untyped-call]
                query, limit=page_size, nextPageToken=next_token
            )
            all_issues.extend(raw.get("issues", []))
            if cap is not None and len(all_issues) >= cap:
                break
            if raw.get("isLast", True):
                break
            next_token = raw.get("nextPageToken")
            if not next_token:
                break
        return all_issues

    def _jql_all_server(
        self, query: str, page_size: int = 50, cap: int | None = None
    ) -> list[dict[str, Any]]:
        all_issues: list[dict[str, Any]] = []
        start = 0
        while True:
            raw: dict[str, Any] = self._client.jql(query, limit=page_size, start=start)  # type: ignore[no-untyped-call]
            page = list(raw.get("issues", []))
            all_issues.extend(page)
            if cap is not None and len(all_issues) >= cap:
                break
            if len(page) < page_size:
                break
            start += page_size
        return all_issues

    # ── Transitions ──────────────────────────────────────────────────

    def get_transitions(self, key: str) -> list[dict[str, Any]]:
        """Get available transitions for an issue, including to_id for locale-independent matching.

        Uses get_issue_transitions_full to access to.id from the raw Jira API
        response — the simplified get_issue_transitions only exposes to.name,
        which fails when status display names differ from transition names (RAISE-4140).
        """
        try:
            raw: dict[str, Any] = self._client.get_issue_transitions_full(key) or {}  # type: ignore[no-untyped-call]
            return [
                {
                    "name": t["name"],
                    "id": str(t["id"]),
                    "to": t["to"]["name"],
                    "to_id": str(t["to"]["id"]),
                }
                for t in raw.get("transitions", [])
            ]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_transitions({key})") from e

    def transition_issue(self, key: str, transition_id: str) -> None:
        """Execute a transition by numeric ID.

        Posts directly to ``/issue/{key}/transitions`` because the
        library's ``set_issue_status`` and ``issue_transition`` both
        route through ``get_transition_id_to_status_name`` which calls
        ``.lower()`` on the status param — breaks when given a numeric ID.
        """
        try:
            url = f"{self._client.resource_url('issue')}/{key}/transitions"
            self._client.post(url, data={"transition": {"id": transition_id}})  # type: ignore[no-untyped-call]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"transition_issue({key}, {transition_id})") from e

    # ── Relationships ────────────────────────────────────────────────

    def create_link(
        self,
        source: str,
        target: str,
        link_type: str,
        *,
        inward: bool = False,
    ) -> None:
        """Create an issue link between two issues.

        Jira REST API semantics (empirically verified on Jira Cloud):
        ``inwardIssue`` is the side that performs the **outward** verb,
        ``outwardIssue`` is the side that performs the **inward** verb.
        This is counterintuitive but consistent: for type "Blocks",
        ``inwardIssue=A, outwardIssue=B`` creates "A blocks B".

        When ``inward=False`` (default): ``source <outward-verb> target``
        e.g. source=A, target=B, type=Blocks → "A blocks B".

        When ``inward=True``: ``source <inward-verb> target``
        e.g. source=A, target=B, type=Blocks, inward → "A is blocked by B"
        which means B blocks A.
        """
        if inward:
            jira_inward, jira_outward = target, source
        else:
            jira_inward, jira_outward = source, target
        try:
            self._client.create_issue_link(
                {  # type: ignore[no-untyped-call]
                    "type": {"name": link_type},
                    "inwardIssue": {"key": jira_inward},
                    "outwardIssue": {"key": jira_outward},
                }
            )
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"create_link({source}, {target})") from e

    def delete_issue_link(self, link_id: str) -> None:
        """Delete an issue link by ID."""
        try:
            self._client.remove_issue_link(link_id)  # type: ignore[no-untyped-call]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"delete_issue_link({link_id})") from e

    def set_parent(self, child: str, parent: str) -> None:
        """Set the parent of an issue."""
        self.update_issue(child, {"parent": {"key": parent}})

    # ── Users ───────────────────────────────────────────────────────

    def search_users(self, query: str) -> list[dict[str, Any]]:
        """Search Jira users by email or display name."""
        try:
            result: list[dict[str, Any]] = self._client.user_find_by_user_string(  # type: ignore[no-untyped-call]
                query=query
            )
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"search_users({query!r})") from e

    # ── Comments ─────────────────────────────────────────────────────

    def add_comment(self, key: str, body: str | dict[str, Any]) -> dict[str, Any]:
        """Add a comment to an issue."""
        try:
            result: dict[str, Any] = self._client.issue_add_comment(key, body)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"add_comment({key})") from e

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[dict[str, Any]]:
        """Get comments on an issue."""
        try:
            raw: dict[str, Any] = self._client.issue_get_comments(key)  # type: ignore[no-untyped-call]
            comments: list[dict[str, Any]] = raw.get("comments", [])
            if fetch_all:
                return comments[offset:]
            return comments[offset : offset + limit]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_comments({key})") from e

    # ── Discovery (S1130.2) ───────────────────────────────────────────

    def list_projects(self) -> list[ProjectInfo]:
        """List all accessible projects."""
        from raise_cli.adapters.models.pm import ProjectInfo

        try:
            raw: list[dict[str, Any]] = self._client.projects()  # type: ignore[no-untyped-call]
            return [
                ProjectInfo(
                    key=p["key"],
                    name=p["name"],
                    project_type_key=p.get("projectTypeKey", "unknown"),
                )
                for p in raw
            ]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "list_projects") from e

    def get_project_workflows(
        self, project_key: str, issue_type: str | None = None
    ) -> list[WorkflowState]:
        """Get workflow states for a project, optionally filtered by issue type name.

        Calls ``/project/{key}/statuses`` which returns statuses grouped by
        issue type. When issue_type is set, returns only statuses for that group.
        Matches by display name OR untranslatedName (case-insensitive) to support
        localized Jira instances (e.g. "Historia" for "Story" in Spanish Jira).
        """
        from raise_cli.adapters.models.pm import WorkflowState

        try:
            raw: Any = self._client.get_status_for_project(project_key)  # type: ignore[no-untyped-call]
            groups: list[dict[str, Any]] = (
                cast("list[dict[str, Any]]", raw) if isinstance(raw, list) else []
            )
            if issue_type is not None:
                it_lower = issue_type.lower()
                groups = [
                    g
                    for g in groups
                    if str(g.get("name", "")).lower() == it_lower
                    or str(g.get("untranslatedName", "")).lower() == it_lower
                ]
            seen: dict[tuple[str, str], WorkflowState] = {}
            for itg in groups:
                statuses: list[dict[str, Any]] = list(itg.get("statuses", []))
                for status in statuses:
                    name: str = str(status.get("name", ""))
                    if not name:
                        continue
                    cat_raw: Any = status.get("statusCategory", {})
                    cat_dict: dict[str, str] = (
                        cast("dict[str, str]", cat_raw)
                        if isinstance(cat_raw, dict)
                        else {}
                    )
                    category: str = str(cat_dict.get("key", "unknown"))
                    key = (name, category)
                    if key not in seen:
                        seen[key] = WorkflowState(
                            id=str(status.get("id", "")),
                            name=name,
                            status_category=category,
                            transitions=[],
                        )
            return list(seen.values())
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_project_workflows({project_key})") from e

    def find_issue_type_display_name(
        self, project_key: str, canonical_name: str
    ) -> str | None:
        """Return the localized display name for a canonical issue type name, or None.

        Returns non-None only when the display name differs from canonical_name
        (i.e. a localization mismatch exists). E.g. canonical="Story", display="Historia"
        → returns "Historia". Returns None if no mismatch or type not found.

        Strategy (two passes, first match wins):
        1. untranslatedName field in get_status_for_project — present on some Jira plans.
        2. Cross-reference by id: get_status_for_project returns canonical names with
           type ids; get_issue_types returns display names with the same ids. When
           untranslatedName is absent (pass 1 misses), match on id to find the display
           name (pass 2).
        """
        try:
            raw: Any = self._client.get_status_for_project(project_key)  # type: ignore[no-untyped-call]
            groups: list[dict[str, Any]] = (
                cast("list[dict[str, Any]]", raw) if isinstance(raw, list) else []
            )
            canonical_lower = canonical_name.lower()

            # Pass 1: untranslatedName field (present on some Jira Cloud plans).
            for g in groups:
                name = str(g.get("name", ""))
                untranslated = g.get("untranslatedName")
                if (
                    untranslated is not None
                    and str(untranslated).lower() == canonical_lower
                ):
                    return name if name.lower() != canonical_lower else None

            # Pass 2: cross-reference by id using get_issue_types (display names).
            # get_status_for_project returns canonical name in `name`; match on id to
            # find the corresponding display name from the createmeta endpoint.
            canonical_id: str | None = next(
                (
                    str(g.get("id", ""))
                    for g in groups
                    if str(g.get("name", "")).lower() == canonical_lower
                ),
                None,
            )
            if canonical_id:
                display_types = self.get_issue_types(project_key)
                for it in display_types:
                    if it.id == canonical_id and it.name.lower() != canonical_lower:
                        return it.name
        except Exception:  # noqa: BLE001,S110 — best-effort display name lookup, non-critical
            pass
        return None

    def resolve_canonical_from_display(
        self, project_key: str, display_name: str
    ) -> str | None:
        """Return the canonical Jira type name for a localized display name, or None.

        Inverse of find_issue_type_display_name. Given 'Historia' returns 'Story'
        by cross-referencing get_issue_types (display names + ids) with
        get_status_for_project (canonical names + ids) by type id.
        """
        try:
            display_types = self.get_issue_types(project_key)
            display_lower = display_name.lower()
            matched = next(
                (it for it in display_types if it.name.lower() == display_lower), None
            )
            if not matched:
                return None
            raw: Any = self._client.get_status_for_project(project_key)  # type: ignore[no-untyped-call]
            groups: list[dict[str, Any]] = (
                cast("list[dict[str, Any]]", raw) if isinstance(raw, list) else []
            )
            canonical_group = next(
                (g for g in groups if str(g.get("id", "")) == matched.id), None
            )
            return str(canonical_group["name"]) if canonical_group else None
        except Exception:  # noqa: BLE001 -- best-effort, non-critical
            return None

    def get_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Get issue types available for a project."""
        from raise_cli.adapters.models.pm import IssueTypeInfo

        try:
            raw: Any = self._client.issue_createmeta_issuetypes(project_key)  # type: ignore[no-untyped-call]
            raw_dict: dict[str, Any] = (
                cast("dict[str, Any]", raw) if isinstance(raw, dict) else {}
            )
            # API v2 returns "issueTypes", v3 returns "values"
            values: list[dict[str, Any]] = list(
                raw_dict.get("issueTypes", raw_dict.get("values", []))
            )
            return [
                IssueTypeInfo(
                    id=str(it["id"]),
                    name=str(it["name"]),
                    subtask=bool(it.get("subtask", False)),
                )
                for it in values
            ]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_issue_types({project_key})") from e

    # ── Field Metadata ───────────────────────────────────────────────

    def get_fields(self) -> list[dict[str, Any]]:
        """Get all fields (system + custom). Returns list with id, name, schema."""
        try:
            result: list[dict[str, Any]] = self._client.get_all_fields()  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "get_fields") from e

    def get_fields_for_issue_type(
        self, project_key: str, issue_type_name: str
    ) -> list[dict[str, Any]]:
        """Get fields for a specific issue type with allowedValues and schema.type.

        Uses createmeta?expand=projects.issuetypes.fields — returns a flat list
        of field dicts, each with 'id', 'name', 'schema', 'allowedValues'.
        Returns [] when the project or issue type is not found (best-effort).

        S9939.1
        """
        try:
            url = (
                f"rest/api/3/issue/createmeta"
                f"?projectKeys={project_key}"
                f"&issuetypeNames={quote(issue_type_name)}"
                f"&expand=projects.issuetypes.fields"
            )
            raw: dict[str, Any] = self._client.get(url)  # type: ignore[no-untyped-call]
            projects: list[dict[str, Any]] = raw.get("projects", [])
            if not projects:
                return []
            issue_types: list[dict[str, Any]] = projects[0].get("issuetypes", [])
            if not issue_types:
                return []
            fields_dict: dict[str, Any] = issue_types[0].get("fields", {})
            return [
                {
                    "id": field_id,
                    "name": field_data.get("name", ""),
                    "schema": field_data.get("schema", {}),
                    "required": field_data.get("required", False),
                    "allowedValues": field_data.get("allowedValues", []),
                }
                for field_id, field_data in fields_dict.items()
            ]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(
                e, f"get_fields_for_issue_type({project_key}, {issue_type_name})"
            ) from e

    def get_link_types(self) -> list[dict[str, Any]]:
        """GET /rest/api/3/issueLinkType → raw list of link type dicts."""
        try:
            raw: Any = self._client.get_issue_link_types()  # type: ignore[no-untyped-call]
            if isinstance(raw, list):
                return list(raw)
            raw_dict: dict[str, Any] = (
                cast("dict[str, Any]", raw) if isinstance(raw, dict) else {}
            )
            return list(raw_dict.get("issueLinkTypes", []))
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "get_link_types") from e

    def get_field_contexts(self, field_id: str) -> list[dict[str, Any]]:
        """Get all contexts for a custom field.

        GET /rest/api/3/field/{fieldId}/context
        Returns list of context dicts with id, name, isGlobalContext.
        """
        try:
            url = f"rest/api/3/field/{field_id}/context"
            raw: dict[str, Any] = self._client.get(url)  # type: ignore[no-untyped-call]
            values: list[dict[str, Any]] = raw.get("values", [])
            return values
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_field_contexts({field_id})") from e

    def get_field_context_options(self, field_id: str, context_id: str) -> list[str]:
        """Get valid option values for a custom field context.

        GET /rest/api/3/field/{fieldId}/context/{contextId}/option
        Paginates until isLast=True. Returns flat list of option value strings.
        """
        try:
            base_url = f"rest/api/3/field/{field_id}/context/{context_id}/option"
            values: list[str] = []
            start_at = 0
            while True:
                url = f"{base_url}?startAt={start_at}&maxResults=100"
                raw: dict[str, Any] = self._client.get(url)  # type: ignore[no-untyped-call]
                page: list[dict[str, Any]] = raw.get("values", [])
                values.extend(item["value"] for item in page if "value" in item)
                if raw.get("isLast", True) or not page:
                    break
                start_at += len(page)
            return values
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(
                e, f"get_field_context_options({field_id}, {context_id})"
            ) from e

    # ── Attachments (S2503.7) ────────────────────────────────────────

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> dict[str, Any]:
        """Upload a file to an issue. Returns the attachment metadata dict.

        The atlassian lib returns a list even for single uploads — we extract
        the first element. If the lib ever returns a bare dict, we handle that
        too.
        """
        try:
            with open(path, "rb") as f:
                raw = self._client.add_attachment_object(key, f)
            result: list[dict[str, Any]] | dict[str, Any] = cast(
                "list[dict[str, Any]] | dict[str, Any]", raw
            )
            if isinstance(result, list):
                return result[0]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"attach({key}, {path.name})") from e

    def get_attachments(self, key: str) -> list[dict[str, Any]]:
        """Return the attachment list from an issue's fields.attachment[]."""
        try:
            issue: dict[str, Any] = cast("dict[str, Any]", self._client.issue(key))
            attachments: list[dict[str, Any]] = issue.get("fields", {}).get(
                "attachment", []
            )
            return attachments
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_attachments({key})") from e

    def download_attachment(self, attachment_id: str) -> bytes:
        """Download attachment binary content by ID."""
        try:
            content: bytes = self._client.get_attachment_content(attachment_id)
            return content
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"download_attachment({attachment_id})") from e

    # ── Sprint (Jira Agile API) ──────────────────────────────────────

    def get_board_for_project(self, project_key: str) -> int:
        """Return the first scrum board ID associated with project_key."""
        try:
            result: dict[str, Any] = self._client.get_all_agile_boards(
                project_key=project_key, board_type="scrum"
            )  # type: ignore[no-untyped-call]
            values: list[dict[str, Any]] = result.get("values", [])
            if not values:
                raise JiraAdapterError(
                    f"No scrum board found for project '{project_key}'. "
                    "Sprints require a Scrum board."
                )
            board_id: int = values[0]["id"]
            return board_id
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_board_for_project({project_key})") from e

    def get_sprints(self, board_id: int, state: str | None = None) -> list[Any]:
        """Return sprints for board_id, optionally filtered by state."""
        from raise_cli.adapters.models.pm import SprintRef

        try:
            result: dict[str, Any] = self._client.get_all_sprints_from_board(
                board_id, state=state
            )  # type: ignore[no-untyped-call]
            sprints = []
            for s in result.get("values", []):
                sprints.append(
                    SprintRef(
                        id=s["id"],
                        name=s["name"],
                        state=s["state"],
                        start_date=s.get("startDate", ""),
                        end_date=s.get("endDate", ""),
                    )
                )
            return sprints
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_sprints({board_id})") from e

    def assign_to_sprint(self, sprint_id: int, issue_key: str) -> None:
        """Assign a single issue to a sprint."""
        try:
            self._client.add_issues_to_sprint(sprint_id, [issue_key])  # type: ignore[no-untyped-call]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(
                e, f"assign_to_sprint({sprint_id}, {issue_key})"
            ) from e

    # ── Health ───────────────────────────────────────────────────────

    def server_info(self) -> dict[str, Any]:
        """Get Jira server info for health checks."""
        try:
            result: dict[str, Any] = self._client.get_server_info()  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "server_info") from e

    # ── Factory ──────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Any, instance: str | None = None) -> JiraClient:
        """Create a JiraClient from config and environment.

        Args:
            config: JiraConfig or any object with .default_instance and
                    .instances dict. Each instance has .site and optional .email.
            instance: Instance name. Uses config.default_instance if None.
        """
        instance_name = instance or config.default_instance
        instances: dict[str, Any] = config.instances
        if instance_name not in instances:
            raise JiraApiError(
                f"Instance {instance_name!r} not found in config. "
                f"Available: {list(instances.keys())}"
            )

        inst = instances[instance_name]
        url = f"https://{inst.site}"
        token = cls._resolve_token(instance_name)
        email: str | None = getattr(inst, "email", None)
        username = email or cls._resolve_username(instance_name)

        return cls(url=url, username=username, token=token)

    @classmethod
    def from_org(cls, org_name: str, url: str, email: str) -> JiraClient:
        """Create a JiraClient from BacklogAdapterConfig org fields.

        OAuth Bearer takes priority over Basic Auth when JIRA_OAUTH_ACCESS_TOKEN
        and JIRA_CLOUD_ID are both set. Falls back to Basic Auth otherwise.
        Proactively refreshes the access_token if expired and refresh credentials
        are available in the environment.

        Args:
            org_name: Logical org name used for token/username env-var resolution.
            url: Org endpoint (e.g. "humansys.atlassian.net") — used for Basic Auth only.
            email: Auth email — falls back to env if empty.
        """
        env_suffix = org_name.upper().replace("-", "_")
        oauth_token = cls._resolve_oauth_token(org_name)
        cloud_id = cls._resolve_cloud_id(org_name)

        if oauth_token and cloud_id:
            refresh_token = os.environ.get(
                f"JIRA_OAUTH_REFRESH_TOKEN_{env_suffix}"
            ) or os.environ.get("JIRA_OAUTH_REFRESH_TOKEN", "")
            client_id = os.environ.get(
                f"JIRA_OAUTH_CLIENT_ID_{env_suffix}"
            ) or os.environ.get("JIRA_OAUTH_CLIENT_ID", "")
            client_secret = os.environ.get(
                f"JIRA_OAUTH_CLIENT_SECRET_{env_suffix}"
            ) or os.environ.get("JIRA_OAUTH_CLIENT_SECRET", "")
            if (
                refresh_token
                and client_id
                and client_secret
                and cls._jira_token_expired(oauth_token)
            ):
                import contextlib as _ctx

                with _ctx.suppress(Exception):
                    oauth_token = cls._refresh_jira_oauth_token(
                        refresh_token, client_id, client_secret
                    )
            return cls.from_oauth(cloud_id, oauth_token)

        token = cls._resolve_token(org_name)
        username = email or cls._resolve_username(org_name)
        return cls(url=f"https://{url}", username=username, token=token)

    @classmethod
    def from_bearer_token(cls, url: str, access_token: str) -> JiraClient:
        """Create a JiraClient using an OAuth Bearer token (Carril B, ADR-112).

        Uses ``personal_access_token`` which sends ``Authorization: Bearer <token>``.
        No username required — the token identifies the user on Jira Cloud.
        """
        try:
            from atlassian import Jira
        except ImportError as exc:
            raise ImportError(
                "atlassian-python-api required. Install with: pip install raise-cli[jira]"
            ) from exc

        instance = cls.__new__(cls)
        instance._url = url
        instance._client = Jira(
            url=url,
            token=access_token,
            cloud=True,
            api_version=3,
        )
        return instance

    # ── Internal ─────────────────────────────────────────────────────

    @staticmethod
    def _map_error(error: Exception, context: str) -> JiraAdapterError:
        """Map atlassian exceptions to our hierarchy using isinstance."""
        from atlassian.errors import ApiError, ApiNotFoundError, ApiPermissionError

        if isinstance(error, ApiPermissionError):
            return JiraAuthError(f"{context}: {error}")
        if isinstance(error, ApiNotFoundError):
            return JiraNotFoundError(f"{context}: {error}")
        if isinstance(error, ApiError):
            return JiraApiError(f"{context}: {error}")
        return JiraApiError(f"{context}: unexpected error: {error}")
