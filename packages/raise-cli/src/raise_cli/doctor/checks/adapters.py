"""Adapter doctor check — config, env vars, and live health for Jira + Confluence.

Three-level diagnostics per adapter:
1. Config file exists (.raise/backlog.yaml, .raise/docs.yaml)
2. Required env vars set (API tokens, usernames)
3. Live backend connectivity (online mode only)

RAISE-1130 (S1130.3)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

if TYPE_CHECKING:
    from raise_cli.adapters.confluence_client import ConfluenceClient
    from raise_cli.adapters.confluence_config import ConfluenceTargetConfig

logger = logging.getLogger(__name__)

_JIRA_CONFIG = Path(".raise") / "backlog.yaml"
_CONFLUENCE_CONFIG = Path(".raise") / "docs.yaml"


class AdapterDoctorCheck(DoctorCheck):
    """Validates Jira and Confluence adapter configuration and connectivity."""

    check_id: ClassVar[str] = "adapters"
    category: ClassVar[str] = "adapters"
    description: ClassVar[str] = (
        "Jira and Confluence adapter config, credentials, and connectivity"
    )
    requires_online: ClassVar[bool] = False

    def _check_env_var_result(
        self,
        results: list[CheckResult],
        value: str,
        check_id: str,
        pass_msg: str,
        fail_msg: str,
        fix_hint: str,
        status_on_fail: CheckStatus = CheckStatus.ERROR,
    ) -> None:
        if value:
            self._append_result(results, check_id, CheckStatus.PASS, pass_msg)
        else:
            self._append_result(results, check_id, status_on_fail, fail_msg, fix_hint)

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run adapter checks: config → env vars → live health."""
        results: list[CheckResult] = []

        uses_jira, uses_confluence = self._manifest_adapters(context.working_dir)

        # Jira checks (skip if manifest doesn't declare jira adapter)
        jira_exists = False
        if uses_jira:
            jira_exists = self._check_config(
                context.working_dir, _JIRA_CONFIG, "jira", results
            )
            if jira_exists:
                self._check_jira_env(results)

        # Confluence checks (skip if manifest doesn't declare confluence)
        conf_exists = False
        if uses_confluence:
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
                space_ok = self._check_confluence_space_exists(
                    results, context.working_dir
                )
                if space_ok:
                    self._check_confluence_routing_parents(results, context.working_dir)

        return results

    @staticmethod
    def _manifest_adapters(root: Path) -> tuple[bool, bool]:
        """Return (uses_jira, uses_confluence) from manifest config."""
        manifest_path = root / ".raise" / "manifest.yaml"
        if not manifest_path.is_file():
            return False, False
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return False, False
            backlog = data.get("backlog", {}) or {}
            uses_jira = backlog.get("adapter") == "jira"
            docs = data.get("docs", {}) or {}
            uses_confluence = docs.get("target") == "confluence"
            return uses_jira, uses_confluence
        except (yaml.YAMLError, OSError):
            return False, False

    def _check_config(
        self,
        working_dir: Path,
        config_path: Path,
        adapter_name: str,
        results: list[CheckResult],
    ) -> bool:
        """Check if config file exists. Returns True if present."""
        full_path = working_dir / config_path
        if full_path.exists():
            self._append_result(
                results,
                f"adapter-{adapter_name}-config",
                CheckStatus.PASS,
                f"{adapter_name.title()} config found: {config_path}",
            )
            return True
        self._append_result(
            results,
            f"adapter-{adapter_name}-config",
            CheckStatus.WARN,
            f"{adapter_name.title()} config not found: {config_path}",
            f"Run /rai-backlog-setup to generate {config_path}"
            if adapter_name == "jira"
            else f"Run /rai-docs-setup to generate {config_path}",
        )
        return False

    def _check_jira_env(self, results: list[CheckResult]) -> None:
        """Check Jira env vars — token and username."""
        import os

        token = os.environ.get("JIRA_API_TOKEN", "")
        # Accept both JIRA_USERNAME (canonical) and JIRA_EMAIL (legacy)
        username = os.environ.get("JIRA_USERNAME", "") or os.environ.get(
            "JIRA_EMAIL", ""
        )

        self._check_env_var_result(
            results,
            token,
            "adapter-jira-token",
            "JIRA_API_TOKEN is set",
            "JIRA_API_TOKEN is not set",
            "Set JIRA_API_TOKEN environment variable with your Jira API token",
        )
        self._check_env_var_result(
            results,
            username,
            "adapter-jira-username",
            "JIRA_USERNAME is set",
            "JIRA_USERNAME is not set",
            "Set JIRA_USERNAME environment variable with your Atlassian email",
            status_on_fail=CheckStatus.WARN,
        )

    def _check_confluence_env(self, results: list[CheckResult]) -> None:
        """Check Confluence env vars — token and username."""
        import os

        token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        username = os.environ.get("CONFLUENCE_USERNAME", "")

        self._check_env_var_result(
            results,
            token,
            "adapter-confluence-token",
            "CONFLUENCE_API_TOKEN is set",
            "CONFLUENCE_API_TOKEN is not set",
            "Set CONFLUENCE_API_TOKEN environment variable with your Confluence API token",
        )
        self._check_env_var_result(
            results,
            username,
            "adapter-confluence-username",
            "CONFLUENCE_USERNAME is set",
            "CONFLUENCE_USERNAME is not set (will fall back to instance-specific var)",
            "Set CONFLUENCE_USERNAME environment variable with your Atlassian email",
            status_on_fail=CheckStatus.WARN,
        )

    def _load_confluence_client(
        self,
        results: list[CheckResult],
        working_dir: Path,
        check_id: str,
    ) -> tuple[ConfluenceTargetConfig, ConfluenceClient] | None:
        from raise_cli.adapters.confluence_client import ConfluenceClient
        from raise_cli.adapters.confluence_config import load_confluence_target_config

        try:
            inst = load_confluence_target_config(working_dir)
            client = ConfluenceClient(inst)
            return inst, client
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Confluence config/client load failed", exc_info=True)
            self._append_result(
                results,
                check_id,
                CheckStatus.ERROR,
                f"Confluence validation failed: {exc}",
                "Check Confluence connectivity and credentials",
            )
            return None

    def _check_jira_health(self, results: list[CheckResult], working_dir: Path) -> None:
        """Check Jira backend connectivity via list_projects()."""
        try:
            from raise_cli.adapters.backlog_config import load_backlog_config
            from raise_cli.adapters.jira_adapter import PythonApiJiraAdapter

            config = load_backlog_config(working_dir, "jira")
            adapter = PythonApiJiraAdapter(project_root=working_dir)
            # default_org is an org name, not a project key — use the org path
            # (client_for would raise UnknownProjectKeyError under fail-strong resolve).
            projects = adapter.client_for_org(config.default_org).list_projects()
            url = config.organizations[config.default_org].url
            self._append_result(
                results,
                "adapter-jira-health",
                CheckStatus.PASS,
                f"Jira backend reachable ({url}, {len(projects)} projects)",
            )
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Jira health check failed", exc_info=True)
            self._append_result(
                results,
                "adapter-jira-health",
                CheckStatus.ERROR,
                f"Jira backend unreachable: {exc}",
                "Check JIRA_API_TOKEN and network connectivity",
            )

    def _check_confluence_space_exists(
        self, results: list[CheckResult], working_dir: Path
    ) -> bool:
        """Check configured space_key exists on instance. Returns True if found."""
        from raise_cli.adapters.confluence_discovery import ConfluenceDiscovery
        from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError

        loaded = self._load_confluence_client(
            results, working_dir, "adapter-confluence-space-exists"
        )
        if loaded is None:
            return False
        inst, client = loaded

        space_key = inst.space_key
        try:
            discovery = ConfluenceDiscovery(client)
            discovery.discover(space_key=space_key)
            self._append_result(
                results,
                "adapter-confluence-space-exists",
                CheckStatus.PASS,
                f"Confluence space '{space_key}' exists",
            )
            return True
        except ConfluenceNotFoundError as exc:
            logger.debug("Confluence space check failed", exc_info=True)
            self._append_result(
                results,
                "adapter-confluence-space-exists",
                CheckStatus.ERROR,
                f"Confluence space '{space_key}' not found on instance",
                f"Check space_key in .raise/docs.yaml — {exc.message}",
            )
            return False
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Confluence space validation failed", exc_info=True)
            self._append_result(
                results,
                "adapter-confluence-space-exists",
                CheckStatus.ERROR,
                f"Confluence space validation failed: {exc}",
                "Check Confluence connectivity and credentials",
            )
            return False

    def _check_confluence_routing_parents(
        self, results: list[CheckResult], working_dir: Path
    ) -> None:
        """Check each routing parent page exists in the configured space."""
        loaded = self._load_confluence_client(
            results, working_dir, "adapter-confluence-routing-parent"
        )
        if loaded is None:
            return
        inst, client = loaded

        for artifact_type, routing in inst.routing.items():
            check_id = f"adapter-confluence-routing-parent-{artifact_type}"
            if routing.parent_title is None:
                continue
            try:
                page = client.get_page_by_title(
                    routing.parent_title, space=inst.space_key
                )
                if page:
                    self._append_result(
                        results,
                        check_id,
                        CheckStatus.PASS,
                        f"Routing parent page '{routing.parent_title}' "
                        f"exists (artifact type: {artifact_type})",
                    )
                else:
                    self._append_result(
                        results,
                        check_id,
                        CheckStatus.ERROR,
                        f"Routing parent page '{routing.parent_title}' "
                        f"not found in space '{inst.space_key}'",
                        f"Create page '{routing.parent_title}' in space "
                        f"{inst.space_key}, or update routing in docs.yaml",
                    )
            except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
                logger.debug(
                    "Routing parent check failed for %s", artifact_type, exc_info=True
                )
                self._append_result(
                    results,
                    check_id,
                    CheckStatus.ERROR,
                    f"Routing parent check failed for '{artifact_type}': {exc}",
                    "Check Confluence connectivity and credentials",
                )

    def _check_confluence_health(
        self, results: list[CheckResult], working_dir: Path
    ) -> None:
        """Check Confluence backend connectivity via health()."""
        try:
            from raise_cli.adapters.confluence_client import ConfluenceClient
            from raise_cli.adapters.confluence_config import (
                load_confluence_target_config,
            )

            inst = load_confluence_target_config(working_dir)
            client = ConfluenceClient(inst)
            health = client.health()
            if health.healthy:
                self._append_result(
                    results,
                    "adapter-confluence-health",
                    CheckStatus.PASS,
                    f"Confluence backend reachable ({inst.url})",
                )
            else:
                self._append_result(
                    results,
                    "adapter-confluence-health",
                    CheckStatus.ERROR,
                    f"Confluence backend unreachable: {health.message}",
                    "Check CONFLUENCE_API_TOKEN and network connectivity",
                )
        except Exception as exc:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Confluence health check failed", exc_info=True)
            self._append_result(
                results,
                "adapter-confluence-health",
                CheckStatus.ERROR,
                f"Confluence health check failed: {exc}",
                "Check Confluence config and credentials",
            )
