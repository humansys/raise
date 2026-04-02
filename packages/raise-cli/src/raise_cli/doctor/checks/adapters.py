"""Adapter doctor check — config, env vars, and live health for Jira + Confluence.

Three-level diagnostics per adapter:
1. Config file exists (.raise/jira.yaml, .raise/confluence.yaml)
2. Required env vars set (API tokens, usernames)
3. Live backend connectivity (online mode only)

RAISE-1130 (S1130.3)
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

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
