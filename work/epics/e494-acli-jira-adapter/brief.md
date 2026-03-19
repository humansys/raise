# E494: ACLI Jira Adapter — Brief

## Hypothesis

Replacing the MCP bridge-based Jira adapter with a thin wrapper around Atlassian CLI
(ACLI) will unlock multi-instance Jira support, simplify the codebase, and align the
developer experience with the tool users already have installed and authenticated.

## Problem

The current `McpJiraAdapter` depends on `mcp-atlassian` as a subprocess MCP server,
which:
- Only supports a single Jira instance per process (env vars: JIRA_URL, JIRA_USERNAME,
  JIRA_API_TOKEN)
- Requires complex async infrastructure (McpBridge, stdio_client, lazy session management)
- Has fragile response parsing (dual flat/nested format detection)
- Adds `mcp` as a heavyweight dependency for basic Jira CRUD
- Does not match how users actually interact with Jira (they use ACLI directly)

## Appetite

Small — 3-5 stories. The protocol and data models already exist; this is a backend swap.

## Success Metrics

1. All 11 `AsyncProjectManagementAdapter` methods work via ACLI
2. Multi-instance support (e.g., rai-agent.atlassian.net + humansys.atlassian.net)
3. Zero MCP infrastructure required for Jira operations
4. Telemetry/observability preserved (logfire spans)
5. Existing CLI commands (`rai backlog`) work unchanged

## Rabbit Holes

- Do NOT redesign the adapter protocol — swap the backend only
- Do NOT add new CLI commands — keep `rai backlog` interface stable
- ACLI JSON output parsing should be straightforward — validate with spike first
- Multi-instance config schema change needs backward compatibility consideration
