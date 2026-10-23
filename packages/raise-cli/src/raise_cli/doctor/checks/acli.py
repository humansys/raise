"""Doctor check for ACLI availability, Jira config, and authentication.

Checks:
  1. ``acli-installed`` — binary in PATH (offline)
  2. ``acli-jira-config`` — ``.raise/backlog.yaml`` declares Jira organizations (offline)
  3. ``acli-jira-yaml-deprecated`` — only while ``.raise/jira.yaml`` lingers (offline)
  4. ``acli-auth-{site}`` — authenticated per organization (online only)

If ACLI is not installed, stops early — no point checking config or auth.
If one site fails auth but others pass: WARN. If ALL fail: ERROR.

``.raise/backlog.yaml`` is the canonical config surface. ``.raise/jira.yaml``
is deprecated (RAISE-16994): ``migrate_jira_yaml_if_needed`` copies it into
``backlog.yaml[jira]`` on every adapter resolution and deliberately does not
delete it. This check reads the canonical file first, treats the legacy one as
a compat fallback, and never tells anyone to create it.

Architecture: S613.1 (E613) · RAISE-16994
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any, ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_CATEGORY = "acli"

_BACKLOG_YAML = Path(".raise") / "backlog.yaml"
_LEGACY_JIRA_YAML = Path(".raise") / "jira.yaml"
_JIRA_SECTION = "jira"

_SETUP_HINT = (
    "Run /rai-backlog-setup to declare a 'jira' section in .raise/backlog.yaml "
    "with organizations and default_org"
)


def _site_of(organization: dict[str, Any]) -> str:
    """Extract an ACLI ``--site`` host from an organization or legacy instance.

    ``backlog.yaml`` carries ``url`` (a full URL — the migration renames
    ``site`` -> ``url``); pre-migration ``jira.yaml`` carries a bare ``site``
    host. ``acli jira auth switch --site`` wants the host, so the scheme and
    any path are stripped.
    """
    raw = str(organization.get("url") or organization.get("site") or "").strip()
    if not raw:
        return ""
    for scheme in ("https://", "http://"):
        if raw.startswith(scheme):
            raw = raw[len(scheme) :]
            break
    return raw.split("/", 1)[0]


class AcliCheck(DoctorCheck):
    """Diagnostic check for ACLI Jira adapter prerequisites."""

    check_id: ClassVar[str] = "acli"
    category: ClassVar[str] = _CATEGORY
    description: ClassVar[str] = "ACLI binary, Jira config, and authentication status"
    requires_online: ClassVar[bool] = (
        False  # offline checks always run; auth checks gate internally
    )

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run ACLI diagnostic checks."""
        results: list[CheckResult] = []

        # 1. Binary availability
        installed = self._check_installed()
        results.append(installed)
        if installed.status != CheckStatus.PASS:
            return results  # stop early

        # 2. Backlog config
        config_result, organizations = self._check_config(context.working_dir)
        results.append(config_result)

        # 3. Deprecated jira.yaml still on disk (RAISE-16994)
        deprecated = self._check_jira_yaml_deprecated(context.working_dir)
        if deprecated is not None:
            results.append(deprecated)

        # 4. Auth per organization (online only)
        if context.online and organizations:
            results.extend(self._check_auth(organizations))

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
        """Validate the backlog config. Returns (result, organizations_dict).

        ``.raise/backlog.yaml`` is canonical. A pre-migration
        ``.raise/jira.yaml`` is read only as a fallback, so an un-migrated
        project keeps working instead of being reported as unconfigured.
        """
        backlog_path = working_dir / _BACKLOG_YAML
        if backlog_path.exists():
            return AcliCheck._check_backlog_yaml(backlog_path)

        legacy_path = working_dir / _LEGACY_JIRA_YAML
        if legacy_path.exists():
            return AcliCheck._check_legacy_jira_yaml(legacy_path)

        return (
            CheckResult(
                check_id="acli-jira-config",
                category=_CATEGORY,
                status=CheckStatus.WARN,
                message="No backlog configuration found",
                fix_hint=_SETUP_HINT,
            ),
            {},
        )

    @staticmethod
    def _check_backlog_yaml(config_path: Path) -> tuple[CheckResult, dict[str, Any]]:
        """Validate ``.raise/backlog.yaml``'s ``jira`` section."""
        try:
            data: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.ERROR,
                    message="Failed to parse .raise/backlog.yaml",
                    fix_hint="Check YAML syntax in .raise/backlog.yaml",
                ),
                {},
            )

        section: dict[str, Any] = data.get(_JIRA_SECTION) or {}
        if not section:
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.WARN,
                    message="backlog.yaml has no 'jira' section",
                    fix_hint=_SETUP_HINT,
                ),
                {},
            )

        organizations: dict[str, Any] = section.get("organizations") or {}
        if not organizations:
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.WARN,
                    message="backlog.yaml[jira] missing 'organizations' section",
                    fix_hint=(
                        "Add organizations with url and projects under "
                        "jira: in .raise/backlog.yaml"
                    ),
                ),
                {},
            )

        count = len(organizations)
        plural = "s" if count != 1 else ""
        return (
            CheckResult(
                check_id="acli-jira-config",
                category=_CATEGORY,
                status=CheckStatus.PASS,
                message=(
                    f"backlog.yaml valid — {count} organization{plural} configured"
                ),
            ),
            organizations,
        )

    @staticmethod
    def _check_legacy_jira_yaml(
        config_path: Path,
    ) -> tuple[CheckResult, dict[str, Any]]:
        """Validate a pre-migration ``.raise/jira.yaml`` (deprecated fallback)."""
        try:
            data: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            return (
                CheckResult(
                    check_id="acli-jira-config",
                    category=_CATEGORY,
                    status=CheckStatus.ERROR,
                    message="Failed to parse .raise/jira.yaml",
                    fix_hint=_SETUP_HINT,
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
                    message="No backlog configuration found",
                    fix_hint=_SETUP_HINT,
                ),
                {},
            )

        count = len(instances)
        plural = "s" if count != 1 else ""
        return (
            CheckResult(
                check_id="acli-jira-config",
                category=_CATEGORY,
                status=CheckStatus.PASS,
                message=(
                    f"{count} organization{plural} configured "
                    "(read from deprecated .raise/jira.yaml)"
                ),
            ),
            instances,
        )

    @staticmethod
    def _check_jira_yaml_deprecated(working_dir: Path) -> CheckResult | None:
        """WARN while ``.raise/jira.yaml`` is still on disk.

        ``migrate_jira_yaml_if_needed`` preserves it deliberately, so a
        migrated project keeps a stale duplicate that nothing reads. WARN
        only — this epic is additive and nothing starts blocking.
        """
        if not (working_dir / _LEGACY_JIRA_YAML).exists():
            return None
        return CheckResult(
            check_id="acli-jira-yaml-deprecated",
            category=_CATEGORY,
            status=CheckStatus.WARN,
            message=(
                ".raise/jira.yaml is deprecated — .raise/backlog.yaml is the "
                "canonical backlog config"
            ),
            fix_hint=(
                "Confirm .raise/backlog.yaml carries your jira section, then "
                "delete .raise/jira.yaml"
            ),
        )

    @staticmethod
    def _check_auth(organizations: dict[str, Any]) -> list[CheckResult]:
        """Check auth status for each configured organization."""
        results: list[CheckResult] = []

        for name, organization in organizations.items():
            site = _site_of(organization)
            if not site:
                results.append(
                    CheckResult(
                        check_id=f"acli-auth-{name}",
                        category=_CATEGORY,
                        status=CheckStatus.WARN,
                        message=f"Organization '{name}' has no url configured",
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
            "acli",
            "jira",
            "auth",
            "switch",
            "--site",
            site,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await switch.communicate()
        if switch.returncode != 0:
            return False

        # Status
        status = await asyncio.create_subprocess_exec(
            "acli",
            "jira",
            "auth",
            "status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await status.communicate()
        return status.returncode == 0
    except FileNotFoundError:
        return False
