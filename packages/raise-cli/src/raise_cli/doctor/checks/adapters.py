"""Adapter doctor check — config, env vars, and live health for Jira + Confluence.

Three-level diagnostics per adapter:
1. Config file exists (.raise/jira.yaml, .raise/confluence.yaml)
2. Required env vars set (API tokens, usernames)
3. Live backend connectivity (online mode only)

RAISE-1130 (S1130.3)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

logger = logging.getLogger(__name__)

_JIRA_CONFIG = Path(".raise") / "jira.yaml"
_CONFLUENCE_CONFIG = Path(".raise") / "confluence.yaml"


class AdapterDoctorCheck:
    """Validates Jira and Confluence adapter configuration and connectivity."""

    check_id: ClassVar[str] = "adapters"
    category: ClassVar[str] = "adapters"
    description: ClassVar[str] = (
        "Jira and Confluence adapter config, credentials, and connectivity"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run adapter checks: config → env vars → live health."""
        results: list[CheckResult] = []

        # Jira checks
        jira_exists = self._check_config(
            context.working_dir, _JIRA_CONFIG, "jira", results
        )
        if jira_exists:
            self._check_jira_env(results)

        # Confluence checks
        conf_exists = self._check_config(
            context.working_dir, _CONFLUENCE_CONFIG, "confluence", results
        )
        if conf_exists:
            self._check_confluence_env(results)

        # Live health checks (online mode only)
        if context.online:
            if jira_exists:
                self._check_jira_health(results, context.working_dir)
            if conf_exists:
                self._check_confluence_health(results, context.working_dir)

        return results

    @staticmethod
    def _check_config(
        working_dir: Path,
        config_path: Path,
        adapter_name: str,
        results: list[CheckResult],
    ) -> bool:
        """Check if config file exists. Returns True if present."""
        full_path = working_dir / config_path
        if full_path.exists():
            results.append(
                CheckResult(
                    check_id=f"adapter-{adapter_name}-config",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message=f"{adapter_name.title()} config found: {config_path}",
                )
            )
            return True
        results.append(
            CheckResult(
                check_id=f"adapter-{adapter_name}-config",
                category="adapters",
                status=CheckStatus.WARN,
                message=f"{adapter_name.title()} config not found: {config_path}",
                fix_hint=f"Run /rai-adapter-setup to generate {config_path}",
            )
        )
        return False

    @staticmethod
    def _check_jira_env(results: list[CheckResult]) -> None:
        """Check Jira env vars — token and email."""
        import os

        token = os.environ.get("JIRA_API_TOKEN", "")
        email = os.environ.get("JIRA_EMAIL", "")

        if token:
            results.append(
                CheckResult(
                    check_id="adapter-jira-token",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message="JIRA_API_TOKEN is set",
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="adapter-jira-token",
                    category="adapters",
                    status=CheckStatus.ERROR,
                    message="JIRA_API_TOKEN is not set",
                    fix_hint="Set JIRA_API_TOKEN environment variable with your Jira API token",
                )
            )

        if email:
            results.append(
                CheckResult(
                    check_id="adapter-jira-email",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message="JIRA_EMAIL is set",
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="adapter-jira-email",
                    category="adapters",
                    status=CheckStatus.WARN,
                    message="JIRA_EMAIL is not set (will fall back to instance-specific var)",
                    fix_hint="Set JIRA_EMAIL environment variable with your Atlassian email",
                )
            )

    @staticmethod
    def _check_confluence_env(results: list[CheckResult]) -> None:
        """Check Confluence env vars — token and username."""
        import os

        token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        username = os.environ.get("CONFLUENCE_USERNAME", "")

        if token:
            results.append(
                CheckResult(
                    check_id="adapter-confluence-token",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message="CONFLUENCE_API_TOKEN is set",
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="adapter-confluence-token",
                    category="adapters",
                    status=CheckStatus.ERROR,
                    message="CONFLUENCE_API_TOKEN is not set",
                    fix_hint="Set CONFLUENCE_API_TOKEN environment variable with your Confluence API token",
                )
            )

        if username:
            results.append(
                CheckResult(
                    check_id="adapter-confluence-username",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message="CONFLUENCE_USERNAME is set",
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="adapter-confluence-username",
                    category="adapters",
                    status=CheckStatus.WARN,
                    message="CONFLUENCE_USERNAME is not set (will fall back to instance-specific var)",
                    fix_hint="Set CONFLUENCE_USERNAME environment variable with your Atlassian email",
                )
            )

    def _check_jira_health(self, results: list[CheckResult], working_dir: Path) -> None:
        """Check Jira backend connectivity via list_projects()."""
        try:
            from raise_cli.adapters.jira_client import JiraClient
            from raise_cli.adapters.jira_config import load_jira_config

            config = load_jira_config(working_dir)
            client = JiraClient.from_config(config, config.default_instance)
            projects = client.list_projects()
            site = config.instances[config.default_instance].site
            results.append(
                CheckResult(
                    check_id="adapter-jira-health",
                    category="adapters",
                    status=CheckStatus.PASS,
                    message=f"Jira backend reachable ({site}, {len(projects)} projects)",
                )
            )
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Jira health check failed", exc_info=True)
            results.append(
                CheckResult(
                    check_id="adapter-jira-health",
                    category="adapters",
                    status=CheckStatus.ERROR,
                    message=f"Jira backend unreachable: {exc}",
                    fix_hint="Check JIRA_API_TOKEN and network connectivity",
                )
            )

    def _check_confluence_health(
        self, results: list[CheckResult], working_dir: Path
    ) -> None:
        """Check Confluence backend connectivity via health()."""
        try:
            from raise_cli.adapters.confluence_client import ConfluenceClient
            from raise_cli.adapters.confluence_config import load_confluence_config

            config = load_confluence_config(working_dir)
            inst = config.instances[config.default_instance]
            client = ConfluenceClient(inst)
            health = client.health()
            if health.healthy:
                results.append(
                    CheckResult(
                        check_id="adapter-confluence-health",
                        category="adapters",
                        status=CheckStatus.PASS,
                        message=f"Confluence backend reachable ({inst.url})",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="adapter-confluence-health",
                        category="adapters",
                        status=CheckStatus.ERROR,
                        message=f"Confluence backend unreachable: {health.message}",
                        fix_hint="Check CONFLUENCE_API_TOKEN and network connectivity",
                    )
                )
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Confluence health check failed", exc_info=True)
            results.append(
                CheckResult(
                    check_id="adapter-confluence-health",
                    category="adapters",
                    status=CheckStatus.ERROR,
                    message=f"Confluence health check failed: {exc}",
                    fix_hint="Check Confluence config and credentials",
                )
            )
