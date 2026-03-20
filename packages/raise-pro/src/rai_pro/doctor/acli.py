"""Doctor check for ACLI availability, Jira config, and authentication.

Checks:
  1. ``acli-installed`` — binary in PATH (offline)
  2. ``acli-jira-config`` — ``.raise/jira.yaml`` exists with instances (offline)
  3. ``acli-auth-{site}`` — authenticated per instance (online only)

If ACLI is not installed, stops early — no point checking config or auth.
If one site fails auth but others pass: WARN. If ALL fail: ERROR.

Architecture: S613.1 (E613)
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any, ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

_CATEGORY = "acli"


class AcliCheck:
    """Diagnostic check for ACLI Jira adapter prerequisites."""

    check_id: ClassVar[str] = "acli"
    category: ClassVar[str] = _CATEGORY
    description: ClassVar[str] = "ACLI binary, Jira config, and authentication status"
    requires_online: ClassVar[bool] = False  # offline checks always run; auth checks gate internally

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run ACLI diagnostic checks."""
        results: list[CheckResult] = []

        # 1. Binary availability
        installed = self._check_installed()
        results.append(installed)
        if installed.status != CheckStatus.PASS:
            return results  # stop early

        # 2. Jira config
        config_result, instances = self._check_config(context.working_dir)
        results.append(config_result)

        # 3. Auth per instance (online only)
        if context.online and instances:
            results.extend(self._check_auth(instances))

        return results

    @staticmethod
    def _check_installed() -> CheckResult:
        if shutil.which("acli"):
            return CheckResult(
                check_id="acli-installed",
                category=_CATEGORY,
                status=CheckStatus.PASS,
                message="ACLI binary found in PATH",
            )
        return CheckResult(
            check_id="acli-installed",
            category=_CATEGORY,
            status=CheckStatus.ERROR,
            message="ACLI binary not found in PATH",
            fix_hint="Install from https://developer.atlassian.com/cli",
        )

    @staticmethod
    def _check_config(working_dir: Path) -> tuple[CheckResult, dict[str, Any]]:
        """Check jira.yaml exists and has instances. Returns (result, instances_dict)."""
        config_path = working_dir / ".raise" / "jira.yaml"
        if not config_path.exists():
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.WARN,
                    message="No Jira configuration found",
                    fix_hint="Create .raise/jira.yaml with instances and default_instance",
                ),
                {},
            )

        try:
            data: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
        except Exception:
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.ERROR,
                    message="Failed to parse .raise/jira.yaml",
                    fix_hint="Check YAML syntax in .raise/jira.yaml",
                ),
                {},
            )

        instances: dict[str, Any] = data.get("instances") or {}
        if not instances:
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.WARN,
                    message="jira.yaml missing 'instances' section",
                    fix_hint="Add instances with site and projects to .raise/jira.yaml",
                ),
                {},
            )

        count = len(instances)
        return (
            CheckResult(
                check_id="acli-jira-config",
                category=_CATEGORY,
                status=CheckStatus.PASS,
                message=f"jira.yaml valid — {count} instance{'s' if count != 1 else ''} configured",
            ),
            instances,
        )

    @staticmethod
    def _check_auth(instances: dict[str, Any]) -> list[CheckResult]:
        """Check auth status for each configured instance."""
        results: list[CheckResult] = []

        for name, instance in instances.items():
            site = instance.get("site", "")
            if not site:
                results.append(
                    CheckResult(
                        check_id=f"acli-auth-{name}",
                        category=_CATEGORY,
                        status=CheckStatus.WARN,
                        message=f"Instance '{name}' has no site configured",
                    ),
                )
                continue

            authenticated = asyncio.run(_check_site_auth(site))
            if authenticated:
                results.append(
                    CheckResult(
                        check_id=f"acli-auth-{name}",
                        category=_CATEGORY,
                        status=CheckStatus.PASS,
                        message=f"Authenticated to {site}",
                    ),
                )
            else:
                results.append(
                    CheckResult(
                        check_id=f"acli-auth-{name}",
                        category=_CATEGORY,
                        status=CheckStatus.WARN,
                        message=f"Not authenticated to {site}",
                        fix_hint=f"Run: acli jira auth login --site {site}",
                    ),
                )

        # Escalate to ERROR if ALL sites failed
        auth_results = [r for r in results if r.check_id.startswith("acli-auth-")]
        if auth_results and all(r.status != CheckStatus.PASS for r in auth_results):
            results = [
                CheckResult(
                    check_id=r.check_id,
                    category=r.category,
                    status=CheckStatus.ERROR,
                    message=r.message,
                    fix_hint=r.fix_hint,
                )
                for r in results
            ]

        return results


async def _check_site_auth(site: str) -> bool:
    """Switch to site and check auth status. Returns True if authenticated."""
    try:
        # Switch
        switch = await asyncio.create_subprocess_exec(
            "acli", "jira", "auth", "switch", "--site", site,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await switch.communicate()
        if switch.returncode != 0:
            return False

        # Status
        status = await asyncio.create_subprocess_exec(
            "acli", "jira", "auth", "status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await status.communicate()
        return status.returncode == 0
    except FileNotFoundError:
        return False
