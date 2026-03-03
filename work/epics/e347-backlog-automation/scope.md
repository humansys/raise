---
epic_id: "E347"
title: "Backlog Automation"
jira_key: "RAISE-347"
status: "in_progress"
branch: "epic/e347/backlog-automation"
base: "dev"
created: "2026-03-03"
---

# Epic Scope: Backlog Automation

## Objective
Make `rai backlog` CLI work deterministically with both McpJiraAdapter (Jira) and FileAdapter (local markdown), ensuring adapter protocol parity and lifecycle hook integration.

## Context
The backlog subsystem currently has two adapters but they're not at parity. Jira works via McpBridge → mcp-atlassian, FileAdapter works against local markdown files. Skills and hooks reference backlog operations but wiring is incomplete. This creates manual work and inconsistency.

## In Scope
- Adapter protocol audit and parity enforcement
- FileAdapter feature completion to match what `rai backlog` CLI exposes
- Hook wiring for backlog events in skill lifecycle
- Integration tests covering both adapters
- `rai adapter check` passing for both

## Out of Scope
- New adapter types (GitHub, Linear)
- Real-time sync / webhooks
- Backlog visualization UI

## Done Criteria
- Both adapters pass `rai adapter check`
- All `rai backlog` subcommands work with `-a jira` and `-a file`
- Lifecycle hooks fire backlog operations at story/epic start/close
- Integration test suite covers both adapters

## Stories
_(To be defined in /rai-epic-design)_

## Risks
- MCP bridge reliability for Jira operations (mitigate: timeout/retry handling)
- FileAdapter markdown format drift (mitigate: schema validation)
