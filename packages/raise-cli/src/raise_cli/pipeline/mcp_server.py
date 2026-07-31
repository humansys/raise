"""RaiSE Workspace MCP Server — stateless (S15457.2).

Tools are registered at import time via @mcp.tool() in each domain module.
Add new tools by creating/editing the appropriate mcp_tools_*.py file.

Usage:
    rai-mcp-pipeline                       # console script (preferred)
    rai-mcp-pipeline --project /checkout   # identity assertion only (D4)
    python -m raise_cli.pipeline.mcp_server  # equivalent

Statelessness contract (E15457): no boot-time ``os.chdir``; the process CWD
is never used to resolve project state. Checkout-scoped tools resolve from
the caller's explicit ``cwd`` (see ``pipeline/_caller_context.py``).
``--project`` is an identity ASSERTION consumed only by
``_check_mcp_worktree_identity`` — never a resolution source.
"""

from __future__ import annotations

import logging
import sys

import raise_cli.pipeline.mcp_tools_artifact  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_backlog  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_docs  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_fleet  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_gate  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_graph  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_pattern  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_pipeline  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_session  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_story  # noqa: F401  # pyright: ignore[reportUnusedImport]
import raise_cli.pipeline.mcp_tools_task  # noqa: F401  # pyright: ignore[reportUnusedImport]
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._mcp_instance import mcp
from raise_cli.pipeline._startup_checks import check_server_version, check_staleness
from raise_cli.pipeline.loader import create_loader

logger = logging.getLogger(__name__)


def _validate_pipelines() -> list[str]:
    """Fail-loud at startup if pipeline registry is empty.

    Package tier only (pipelines_base/ ships with raise-cli); the project
    tier resolves per-call from the caller's ``cwd`` — the server has no
    checkout of its own to pin here (S15457.2).
    """
    pipelines = sorted(create_loader().list_available())
    if not pipelines:
        sys.stderr.write(
            "FATAL: rai-workspace MCP server found 0 pipelines.\n"
            "  Expected at least: story, bugfix, epic\n"
            "  Check that raise-cli is installed and pipelines_base/ ships with it.\n"
        )
        sys.exit(1)
    return pipelines


def main() -> None:
    """Console entry point — `rai-mcp-pipeline`."""
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    project = _caller_context.parse_boot_argv(sys.argv[1:])
    if project:
        _caller_context.set_asserted_root(
            _caller_context.validate_asserted_root(project)
        )

    from raise_cli.cli.commands.connect import load_cli_env, load_server_credentials

    load_cli_env()
    load_server_credentials()
    check_server_version()
    check_staleness()
    pipelines = _validate_pipelines()
    logger.info("rai-workspace ready — %d pipelines: %s", len(pipelines), pipelines)
    mcp.run()


if __name__ == "__main__":
    main()
