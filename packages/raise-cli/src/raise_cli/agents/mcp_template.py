"""MCP configuration template for RaiSE-initialized projects.

Canonical source of truth for the .mcp.json content written by ``rai init``
and verified by ``rai purge``. Moved from ``onboarding/purge.py`` (RAISE-16419 S4 T3)
so agents/ (unclassified) can import it without a layer-contract dependency on onboarding/.
"""

from __future__ import annotations

MCP_JSON_CONTENT: dict[str, object] = {
    "mcpServers": {
        "rai-workspace": {
            "command": "rai-mcp-pipeline",
        }
    }
}
