# RAISE-483: BacklogHook fails with 'No module named mcp'

WHAT:      `rai session start --context` emits "Backlog query error: No module named 'mcp'" and falls back to cached state
WHEN:      Installation without `pip install raise-cli[mcp]` extra
WHERE:     Entry point chain: `rai.adapters.pm` → `McpJiraAdapter` → `raise_cli.mcp.bridge` → `from mcp import ...`
EXPECTED:  BacklogHook degrades gracefully when `mcp` is not installed — uses filesystem adapter or skips MCP-dependent adapters
Done when: BacklogHook works on installations without the `[mcp]` extra; MCP-dependent adapters are skipped cleanly at discovery time
