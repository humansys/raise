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

    async def call(
        self,
        subcommand: list[str],
        flags: dict[str, str],
        *,
        site: str | None = None,
    ) -> Any:
        """Execute ``acli jira <subcommand> <flags> --json`` and return parsed JSON.

        Args:
            subcommand: Command parts, e.g. ``["workitem", "search"]``.
            flags: Flag name → value mapping, e.g. ``{"--jql": "...", "--limit": "5"}``.
            site: Optional site for multi-instance (reserved for S494.4).

        Returns:
            Parsed JSON from stdout (dict or list).

        Raises:
            AcliBridgeError: On missing binary, non-zero exit, or JSON parse failure.
        """
        cmd = [self._binary, "jira", *subcommand]
        for flag, value in flags.items():
            cmd.extend([flag, value])
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
                err_msg = stderr.decode().strip() or f"acli exited with code {proc.returncode}"
                raise AcliBridgeError(err_msg)

            try:
                result: Any = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise AcliBridgeError(f"Failed to parse ACLI JSON output: {exc}") from exc

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
                cmd_str, site, elapsed_ms, success,
            )

    async def health(self, site: str | None = None) -> AdapterHealth:
        """Check ACLI authentication status.

        Args:
            site: Optional site to check (reserved for S494.4).

        Returns:
            AdapterHealth with connectivity status.
        """
        start = time.monotonic()
        try:
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
        except FileNotFoundError:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="jira-acli",
                healthy=False,
                message=f"ACLI binary '{self._binary}' not found",
                latency_ms=elapsed_ms,
            )
