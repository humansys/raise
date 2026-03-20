"""Thin subprocess wrapper around Atlassian CLI (acli jira).

Executes ``acli jira <subcommand> <flags> --json``, parses stdout as JSON,
and emits telemetry spans. All adapter methods delegate to ``call()``.

Architecture: E494 design (D1, D3)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

try:
    import logfire_api as logfire
except ModuleNotFoundError:  # pragma: no cover
    logfire = None  # type: ignore[assignment]

from raise_cli.adapters.models import AdapterHealth

logger = logging.getLogger(__name__)


class AcliBridgeError(Exception):
    """Raised when an ACLI subprocess call fails."""


class AcliJiraBridge:
    """Subprocess wrapper around ``acli jira`` commands.

    Args:
        binary: Path or name of the acli binary. Defaults to ``"acli"``.
    """

    def __init__(self, binary: str = "acli") -> None:
        self._binary = binary
        self._current_site: str | None = None

    async def _switch_site(self, site: str) -> None:
        """Run ``acli jira auth switch --site <site>`` if needed.

        Raises:
            AcliBridgeError: If the switch command fails.
        """
        if site == self._current_site:
            return
        cmd = [self._binary, "jira", "auth", "switch", "--site", site]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            raise AcliBridgeError(
                f"ACLI binary '{self._binary}' not found in PATH. "
                "Install it from https://developer.atlassian.com/cli"
            ) from None
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            err_msg = stderr.decode().strip() or f"auth switch to {site} failed"
            raise AcliBridgeError(err_msg)
        self._current_site = site
        logger.debug("acli auth switched to %s", site)

    async def call(
        self,
        subcommand: list[str],
        flags: dict[str, str],
        *,
        site: str | None = None,
        json_output: bool = True,
    ) -> Any:
        """Execute ``acli jira <subcommand> <flags>`` and return parsed output.

        Args:
            subcommand: Command parts, e.g. ``["workitem", "search"]``.
            flags: Flag name → value mapping, e.g. ``{"--jql": "...", "--limit": "5"}``.
            site: Optional site for multi-instance. Triggers auth switch if needed.
            json_output: Append ``--json`` flag and parse stdout as JSON.
                Set to False for commands that don't support ``--json``
                (e.g. ``workitem link create``).

        Returns:
            Parsed JSON from stdout (dict or list), or raw stdout string
            when ``json_output=False``.

        Raises:
            AcliBridgeError: On missing binary, non-zero exit, or JSON parse failure.
        """
        if site:
            await self._switch_site(site)

        cmd = [self._binary, "jira", *subcommand]
        for flag, value in flags.items():
            cmd.extend([flag, value])
        if json_output:
            cmd.append("--json")

        start = time.monotonic()
        success = False

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err_msg = (
                    stderr.decode().strip()
                    or f"acli exited with code {proc.returncode}"
                )
                raise AcliBridgeError(err_msg)

            if not json_output:
                success = True
                return stdout.decode().strip()

            try:
                result: Any = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise AcliBridgeError(
                    f"Failed to parse ACLI JSON output: {exc}"
                ) from exc

            success = True
            return result

        except FileNotFoundError:
            raise AcliBridgeError(
                f"ACLI binary '{self._binary}' not found in PATH. "
                "Install it from https://developer.atlassian.com/cli"
            ) from None

        finally:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            cmd_str = " ".join(subcommand)
            if logfire is not None:
                logfire.info(
                    "acli.call {cmd}",
                    cmd=cmd_str,
                    site=site or "",
                    latency_ms=elapsed_ms,
                    success=success,
                )
            logger.debug(
                "acli.call %s site=%s latency=%dms success=%s",
                cmd_str,
                site,
                elapsed_ms,
                success,
            )

    async def health(self, site: str | None = None) -> AdapterHealth:
        """Check ACLI authentication status.

        Args:
            site: Optional site to switch to before checking.

        Returns:
            AdapterHealth with connectivity status.
        """
        start = time.monotonic()
        try:
            if site:
                await self._switch_site(site)
            cmd = [self._binary, "jira", "auth", "status"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            elapsed_ms = int((time.monotonic() - start) * 1000)

            if proc.returncode == 0:
                return AdapterHealth(
                    name="jira-acli",
                    healthy=True,
                    message=stdout.decode().strip(),
                    latency_ms=elapsed_ms,
                )
            return AdapterHealth(
                name="jira-acli",
                healthy=False,
                message=stderr.decode().strip() or "Not authenticated",
                latency_ms=elapsed_ms,
            )
        except AcliBridgeError as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira-acli",
                healthy=False,
                message=str(exc),
                latency_ms=elapsed_ms,
            )
        except FileNotFoundError:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira-acli",
                healthy=False,
                message=f"ACLI binary '{self._binary}' not found",
                latency_ms=elapsed_ms,
            )
