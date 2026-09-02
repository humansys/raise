#!/usr/bin/env bash
# scripts/build-binary-local.sh — RAISE-15629
#
# Repeatable local build + smoke test for the two PyInstaller onedir
# binaries (rai, rai-mcp-pipeline). Real build (~1-2 min, ~130MB per
# binary) — deliberately NOT wired into per-commit CI (that automation is
# S6/RAISE-15630 scope). Run this manually as the mandatory gate before S6.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CLI_DIR="$REPO_ROOT/packages/raise-cli"

echo "==> Building rai (raise-cli.spec)"
(cd "$CLI_DIR" && uv run pyinstaller --noconfirm raise-cli.spec)

echo "==> Building rai-mcp-pipeline (raise-mcp-pipeline.spec)"
(cd "$CLI_DIR" && uv run pyinstaller --noconfirm raise-mcp-pipeline.spec)

RAI_BIN="$CLI_DIR/dist/rai/rai"
MCP_BIN="$CLI_DIR/dist/rai-mcp-pipeline/rai-mcp-pipeline"

echo "==> Smoke test: rai gate list (expect 48)"
GATE_COUNT=$("$RAI_BIN" gate list --format json | python3 -c "import json,sys; print(len(json.load(sys.stdin)['gates']))")
echo "    gates found: $GATE_COUNT"
if [ "$GATE_COUNT" -ne 48 ]; then
  echo "FAIL: expected 48 gates, got $GATE_COUNT — .spec is missing metadata/submodules for an entry-point group" >&2
  exit 1
fi

echo "==> Smoke test: rai adapter list"
"$RAI_BIN" adapter list

echo "==> Smoke test: rai-mcp-pipeline exposes MCP tools over stdio"
# A bare `binary &` + `kill -0` liveness check is unreliable here: with no
# real MCP client attached, the stdio transport sees EOF on stdin and exits
# by design — that looked like a crash in earlier iterations but was a test
# harness bug, not a packaging defect. McpBridge (raise_cli.mcp.bridge,
# already used in production to talk to any stdio MCP server) does a real
# handshake and gives an actual tool count instead of inferring from logs.
TOOL_COUNT=$(uv run python3 - "$MCP_BIN" <<'PYEOF'
import asyncio
import sys

from raise_cli.mcp.bridge import McpBridge


async def main() -> int:
    bridge = McpBridge(server_command=sys.argv[1])
    tools = await bridge.list_tools()
    await bridge.aclose()
    print(len(tools))
    return 0


sys.exit(asyncio.run(main()))
PYEOF
)
echo "    tools found: $TOOL_COUNT"
if [ "$TOOL_COUNT" -lt 30 ]; then
  echo "FAIL: expected ~36 MCP tools, got $TOOL_COUNT" >&2
  exit 1
fi

echo "==> All smoke tests passed"
