"""Google OAuth InstalledAppFlow for Drive auth (RAISE-15335).

ADR-112 brokered pattern: the refresh_token is stored in identity_map.db and
injected into the environment by hermes_raise._build_env; it is NEVER logged
or sent to the LLM context.

PAT-F-501: Google token exchange uses form-encoded POST (data=), not JSON.
The InstalledAppFlow handles this internally — no manual exchange needed here.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from raise_cli.config.paths import get_global_rai_dir

_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"
_CLIENT_JSON = "google_oauth_client.json"
_IDENTITY_DB_DEFAULT = "identity_map.db"

_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"


class GoogleAccountRecord(BaseModel):
    """Google Drive account stored in identity_map.db."""

    jira_account_id: str
    drive_token: str  # OAuth refresh_token (ADR-112: never log this)
    email: str = ""
    label: str = ""
    is_default: bool = False


class GoogleOAuthClientError(Exception):
    """OAuth client credentials are missing, unreadable, or the flow failed."""


class GoogleDriveConnectivityError(Exception):
    """Post-auth Drive connectivity check failed."""


class GoogleAuthManager:
    """Manages Google OAuth InstalledAppFlow and identity_map.db persistence.

    db_path defaults to IDENTITY_DB_PATH env var → ~/.rai/identity_map.db,
    matching hermes_raise._lookup_drive_token so the two always see the same DB.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = (
            Path(db_path) if db_path is not None else self._default_db_path()
        )

    @staticmethod
    def _default_db_path() -> Path:
        env = os.environ.get("IDENTITY_DB_PATH", "")
        if env:
            return Path(env)
        return get_global_rai_dir() / _IDENTITY_DB_DEFAULT

    def _get_client_config(self) -> dict[str, Any]:
        """Load OAuth client credentials from env vars or JSON file."""
        client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
        client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
        if client_id and client_secret:
            return {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }
        json_path = get_global_rai_dir() / _CLIENT_JSON
        if not json_path.is_file():
            raise GoogleOAuthClientError(
                "No Google OAuth client credentials found. "
                "Set GOOGLE_OAUTH_CLIENT_ID + GOOGLE_OAUTH_CLIENT_SECRET, "
                f"or place a client secrets file at {json_path}"
            )
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
        except (OSError, json.JSONDecodeError) as exc:
            raise GoogleOAuthClientError(f"Cannot read {json_path}: {exc}") from exc

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        """Create identity_map if absent; add new columns idempotently.

        Backward compat: existing rows (hermes_raise drive_token entries)
        are untouched — new columns are nullable/defaulted.
        """
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS identity_map (
                jira_account_id TEXT PRIMARY KEY,
                drive_token TEXT
            )
            """
        )
        new_columns = [
            ("client_id", "TEXT"),
            ("client_secret", "TEXT"),
            ("email", "TEXT"),
            ("label", "TEXT DEFAULT ''"),
            ("is_default", "BOOLEAN DEFAULT 0"),
        ]
        for col, coldef in new_columns:
            with contextlib.suppress(sqlite3.OperationalError):
                conn.execute(f"ALTER TABLE identity_map ADD COLUMN {col} {coldef}")
        conn.commit()

    def _open_db(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self._db_path))

    def _run_flow(self, client_config: dict[str, Any]) -> Any:
        """Run InstalledAppFlow and return credentials.

        Isolated method so tests can patch it without needing the library.
        Raises GoogleOAuthClientError if google-auth-oauthlib is not installed.
        """
        try:
            from google_auth_oauthlib.flow import (
                InstalledAppFlow,  # type: ignore[import-untyped]
            )
        except ImportError as exc:
            raise GoogleOAuthClientError(
                "google-auth-oauthlib is required. "
                "Install raise-cli[gdrive]: pip install raise-cli[gdrive]"
            ) from exc
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=[_DRIVE_SCOPE],
        )
        return flow.run_local_server(port=0, access_type="offline", prompt="consent")

    def _verify_drive(self, credentials: Any) -> str:
        """Create and delete a temp Drive file to verify connectivity.

        Returns the authenticated user's email address (empty string on failure).
        Raises GoogleDriveConnectivityError if the file create call fails.
        """
        import httpx  # already a hard dep of raise-cli

        auth_header = f"Bearer {credentials.token}"

        email = ""
        try:
            info_resp = httpx.get(
                _USERINFO_URL,
                headers={"Authorization": auth_header},
                timeout=10,
            )
            if info_resp.status_code == 200:
                email = info_resp.json().get("email", "")
        except httpx.HTTPError:
            pass  # email is optional; connectivity check still proceeds

        create_resp = httpx.post(
            _DRIVE_FILES_URL,
            headers={"Authorization": auth_header},
            json={
                "name": "_rai_auth_check",
                "mimeType": "application/vnd.google-apps.document",
            },
            timeout=10,
        )
        if create_resp.status_code not in (200, 201):
            raise GoogleDriveConnectivityError(
                f"Drive file create failed: HTTP {create_resp.status_code} — {create_resp.text[:200]}"
            )
        file_id: str = create_resp.json().get("id", "")
        if file_id:
            with contextlib.suppress(httpx.HTTPError):
                httpx.delete(
                    f"{_DRIVE_FILES_URL}/{file_id}",
                    headers={"Authorization": auth_header},
                    timeout=10,
                )

        return email

    def authorize(
        self,
        jira_account_id: str,
        label: str = "",
        *,
        is_default: bool = False,
    ) -> GoogleAccountRecord:
        """Run OAuth flow, verify Drive connectivity, persist token, return record.

        The refresh_token is stored in the drive_token column so that
        hermes_raise._lookup_drive_token() can find it unchanged.
        """
        client_config = self._get_client_config()
        credentials = self._run_flow(client_config)
        email = self._verify_drive(credentials)

        refresh_token: str = credentials.refresh_token or ""
        client_id: str = credentials.client_id or ""
        client_secret: str = credentials.client_secret or ""

        conn = self._open_db()
        try:
            self._ensure_schema(conn)
            conn.execute(
                """
                INSERT INTO identity_map (
                    jira_account_id, drive_token, client_id, client_secret,
                    email, label, is_default
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(jira_account_id) DO UPDATE SET
                    drive_token    = excluded.drive_token,
                    client_id      = excluded.client_id,
                    client_secret  = excluded.client_secret,
                    email          = excluded.email,
                    label          = excluded.label,
                    is_default     = excluded.is_default
                """,
                (
                    jira_account_id,
                    refresh_token,
                    client_id,
                    client_secret,
                    email,
                    label,
                    int(is_default),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return GoogleAccountRecord(
            jira_account_id=jira_account_id,
            drive_token=refresh_token,
            email=email,
            label=label,
            is_default=is_default,
        )

    def get_default_drive_token(self) -> str | None:
        """Return the first stored drive_token, or None if none found."""
        creds = self.get_default_drive_credentials()
        return creds[0] if creds else None

    def get_default_drive_credentials(
        self,
    ) -> tuple[str, str, str] | None:
        """Return (refresh_token, client_id, client_secret) for the default account.

        Schema-agnostic: handles old schemas that lack client_id/client_secret columns
        by falling back to empty strings for those fields.

        Returns:
            Tuple of (refresh_token, client_id, client_secret), or None if absent.
        """
        if not self._db_path.is_file():
            return None
        try:
            conn = sqlite3.connect(str(self._db_path))
            try:
                row = conn.execute(
                    "SELECT drive_token, client_id, client_secret FROM identity_map "
                    "WHERE drive_token IS NOT NULL AND drive_token != '' "
                    "LIMIT 1"
                ).fetchone()
                conn.close()
                if not row:
                    return None
                return (row[0] or "", row[1] or "", row[2] or "")
            except sqlite3.OperationalError:
                row = conn.execute(
                    "SELECT drive_token FROM identity_map "
                    "WHERE drive_token IS NOT NULL AND drive_token != '' "
                    "LIMIT 1"
                ).fetchone()
                conn.close()
                if not row:
                    return None
                return (row[0] or "", "", "")
        except Exception:  # noqa: BLE001
            return None

    def list_accounts(self) -> list[GoogleAccountRecord]:
        """Return all Drive-authorized accounts from identity_map.db."""
        if not self._db_path.is_file():
            return []
        conn = self._open_db()
        try:
            self._ensure_schema(conn)
            rows = conn.execute(
                """
                SELECT jira_account_id, drive_token, email, label, is_default
                FROM identity_map
                WHERE drive_token IS NOT NULL AND drive_token != ''
                """
            ).fetchall()
        except Exception:  # noqa: BLE001
            return []
        finally:
            conn.close()
        return [
            GoogleAccountRecord(
                jira_account_id=row[0],
                drive_token=row[1],
                email=row[2] or "",
                label=row[3] or "",
                is_default=bool(row[4]),
            )
            for row in rows
        ]
