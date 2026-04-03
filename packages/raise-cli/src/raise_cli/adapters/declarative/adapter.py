"""Generic declarative MCP adapter driven by YAML config.

Implements ``AsyncProjectManagementAdapter`` and ``AsyncDocumentationTarget``
by dispatching each protocol method to the MCP tool specified in the YAML
config. Expression templates in args are evaluated against a context dict
built from method parameters. One class serves both protocols (AR-Q1).

Architecture: ADR-041, E337, AR-C1/C2/R1/Q1
"""

from __future__ import annotations

import logging
import os
from typing import Any, cast

from raise_cli.adapters.declarative.expressions import ExpressionEvaluator
from raise_cli.adapters.declarative.schema import (
    DeclarativeAdapterConfig,
    MethodMapping,
)
from raise_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    FailureDetail,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.mcp.bridge import McpBridge, McpBridgeError, McpToolResult
from raise_cli.mcp.registry import discover_mcp_servers
from raise_cli.mcp.schema import ServerConnection

logger = logging.getLogger(__name__)


class DeclarativeMcpAdapter:
    """Async adapter driven by YAML config — serves PM or Docs protocol.

    Implements ``AsyncProjectManagementAdapter`` and ``AsyncDocumentationTarget``
    via structural typing. Each protocol method dispatches to the MCP tool
    declared in config.methods. One class, both protocols (AR-Q1).

    Args:
        config: Parsed YAML adapter configuration.
    """

    def __init__(self, config: DeclarativeAdapterConfig) -> None:
        self._config = config
        self._evaluator = ExpressionEvaluator()
        self._bridge = self._create_bridge()

    def _create_bridge(self) -> McpBridge:
        """Create McpBridge from server config.

        Resolves ``server.ref`` via MCP registry if set, otherwise
        uses inline connection fields. (S338.5, AR-C2)
        """
        server = self._config.server
        if server.ref is not None:
            registry = discover_mcp_servers()
            if server.ref not in registry:
                msg = f"Server ref '{server.ref}' not found in MCP registry"
                raise McpBridgeError(msg)
            conn = registry[server.ref].server
        else:
            assert server.command is not None  # noqa: S101 -- guaranteed by ServerRef validator
            conn = ServerConnection(
                command=server.command,
                args=server.args,
                env=server.env,
            )
        env: dict[str, str] | None = None
        if conn.env:
            env = {
                **os.environ,
                **{k: os.environ.get(k, "") for k in conn.env},
            }
        return McpBridge(
            server_command=conn.command,
            server_args=conn.args,
            env=env,
        )

    def _get_method(self, name: str) -> MethodMapping:
        """Get method mapping, raising NotImplementedError if null or missing."""
        mapping = self._config.methods.get(name)
        if mapping is None:
            msg = f"Method '{name}' not supported by adapter '{self._config.adapter.name}'"
            raise NotImplementedError(msg)
        return mapping

    async def _dispatch(
        self, method_name: str, context: dict[str, Any]
    ) -> McpToolResult:
        """Dispatch a protocol method call to the configured MCP tool."""
        mapping = self._get_method(method_name)
        args = self._evaluator.evaluate_args(mapping.args, context)
        result = await self._bridge.call(mapping.tool, args)
        if result.is_error:
            raise McpBridgeError(result.error_message)
        return result

    def _parse_single(
        self, method_name: str, result: McpToolResult, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Parse a single-item response using the method's response mapping."""
        mapping = self._get_method(method_name)
        if mapping.response is None:
            return result.data

        parse_ctx = {**context, "data": result.data}
        return {
            field: self._evaluator.evaluate(tmpl, parse_ctx)
            for field, tmpl in mapping.response.fields.items()
        }

    def _parse_list(
        self, method_name: str, result: McpToolResult
    ) -> list[dict[str, Any]]:
        """Parse a list response using items_path and field mappings."""
        mapping = self._get_method(method_name)
        if mapping.response is None:
            return result.data.get("items", [])

        # Navigate to list via items_path
        items: Any = result.data
        if mapping.response.items_path:
            for part in mapping.response.items_path.split("."):
                if isinstance(items, dict):
                    items = cast("Any", items.get(part, []))

        if not isinstance(items, list):
            items = []

        parsed: list[dict[str, Any]] = []
        for raw_item in cast("list[Any]", items):
            item_ctx: dict[str, Any] = {"item": raw_item}
            row = {
                field: self._evaluator.evaluate(tmpl, item_ctx)
                for field, tmpl in mapping.response.fields.items()
            }
            parsed.append(row)
        return parsed

    # ----- CRUD -----

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        ctx = {"project_key": project_key, "issue": issue.model_dump()}
        result = await self._dispatch("create_issue", ctx)
        fields = self._parse_single("create_issue", result, ctx)
        return IssueRef(**fields)

    async def get_issue(self, key: str) -> IssueDetail:
        ctx = {"key": key}
        result = await self._dispatch("get_issue", ctx)
        fields = self._parse_single("get_issue", result, ctx)
        return IssueDetail(**fields)

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        ctx = {"key": key, "fields": fields}
        result = await self._dispatch("update_issue", ctx)
        parsed = self._parse_single("update_issue", result, ctx)
        return IssueRef(**parsed)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        ctx = {"key": key, "status": status}
        result = await self._dispatch("transition_issue", ctx)
        parsed = self._parse_single("transition_issue", result, ctx)
        return IssueRef(**parsed)

    # ----- Batch -----

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Auto-loops over transition_issue (AR design D6)."""
        succeeded: list[IssueRef] = []
        failed: list[FailureDetail] = []

        for key in keys:
            try:
                ref = await self.transition_issue(key, status)
                succeeded.append(ref)
            except Exception as exc:
                failed.append(FailureDetail(key=key, error=str(exc)))

        return BatchResult(succeeded=succeeded, failed=failed)

    # ----- Relationships -----

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        ctx = {"child_key": child_key, "parent_key": parent_key}
        await self._dispatch("link_to_parent", ctx)

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        ctx = {"source": source, "target": target, "link_type": link_type}
        await self._dispatch("link_issues", ctx)

    # ----- Comments -----

    async def add_comment(self, key: str, body: str) -> CommentRef:
        ctx = {"key": key, "body": body}
        result = await self._dispatch("add_comment", ctx)
        fields = self._parse_single("add_comment", result, ctx)
        return CommentRef(**fields)

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        ctx = {"key": key, "limit": limit}
        result = await self._dispatch("get_comments", ctx)
        items = self._parse_list("get_comments", result)
        return [Comment(**item) for item in items]

    # ----- Query -----

    async def search(
        self, query: str, limit: int = 50
    ) -> list[IssueSummary] | list[PageSummary]:
        """Protocol-aware search: returns IssueSummary (PM) or PageSummary (docs).

        SyncDocsAdapter calls .search() — must return the right type based on
        the adapter's configured protocol (QR-C1 fix).
        """
        ctx = {"query": query, "limit": limit}
        result = await self._dispatch("search", ctx)
        items = self._parse_list("search", result)
        if self._config.adapter.protocol == "docs":
            return [PageSummary(**item) for item in items]
        return [IssueSummary(**item) for item in items]

    # ----- Docs: Documentation Target (AR-Q1) -----

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        ctx = {"doc_type": doc_type, "metadata": metadata}
        result = await self._dispatch("can_publish", ctx)
        fields = self._parse_single("can_publish", result, ctx)
        return bool(fields.get("result", False))

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        ctx = {"doc_type": doc_type, "content": content, "metadata": metadata}
        result = await self._dispatch("publish", ctx)
        fields = self._parse_single("publish", result, ctx)
        return PublishResult(**fields)

    async def get_page(self, identifier: str) -> PageContent:
        ctx = {"identifier": identifier}
        result = await self._dispatch("get_page", ctx)
        fields = self._parse_single("get_page", result, ctx)
        return PageContent(**fields)

    # ----- Lifecycle -----

    async def health(self) -> AdapterHealth:
        bridge_health = await self._bridge.health()
        return AdapterHealth(
            name=self._config.adapter.name,
            healthy=bridge_health.healthy,
            message=bridge_health.message,
            latency_ms=bridge_health.latency_ms,
        )

    async def aclose(self) -> None:
        """Close the underlying MCP bridge."""
        await self._bridge.aclose()
