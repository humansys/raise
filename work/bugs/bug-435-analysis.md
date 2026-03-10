# RAISE-435 Analysis

## Root Cause

Claude Code Bash tool escapes `!` to `\!` in command arguments. The JQL query
`status != Done` arrives at the adapter as `status \!= Done`, which is invalid
JQL. Jira returns empty results (no error), causing silent failure.

## Evidence

- Raw MCP bridge call with `!=` returns correct results
- `resolve_adapter('jira').search('status != Done ...')` from Python returns results
- Same query via `rai backlog search` in real terminal works
- Same query via Claude Code Bash tool returns "No results"
- `echo 'status != Done'` in Claude Code Bash outputs `status \!= Done`

## Fix Approach

Sanitize `\!` → `!` in `McpJiraAdapter.search()` before passing JQL to bridge.
This is defensive input normalization at the system boundary (CLI → adapter).
