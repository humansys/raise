# Epic E301: Agent Tool Abstraction — Retrospective

> **Started:** 2026-02-26 | **Closed:** 2026-03-01 | **Duration:** 4 days
> **Stories:** 9 (2M + 7S) | **Commits:** 35 | **Branch:** `epic/e301/agent-tool-abstraction`

## Delivered

- `rai backlog` CLI — 9 commands (create, transition, update, link, comment, search, batch-transition, get, get-comments)
- `rai docs` CLI — 3 commands (publish, get, search)
- **McpBridge** — generic async Python bridge over MCP SDK with telemetry
- **McpJiraAdapter** — 11 async PM methods via mcp-atlassian
- **McpConfluenceAdapter** — 5 async docs methods via mcp-atlassian
- **FilesystemPMAdapter** — open-core read+write adapter over governance/backlog.md
- **JiraSyncHook** — lifecycle skills auto-transition Jira issues
- **Generic resolver** — auto-detect + async→sync wrapping for adapters/targets
- Entry points: `rai.adapters.pm` (filesystem, jira), `rai.docs.targets` (confluence)
- Token reduction: ~27x vs raw MCP for equivalent CRUD operations

## Story Metrics

| Story | Size | Velocity | Tests | Bugs | QR Fixes |
|-------|:----:|:--------:|:-----:|:----:|:--------:|
| S301.1 Protocols + Models | M | 1.5x | 103 | 1 (semantic) | 1 |
| S301.2 rai backlog CLI | M | 1.25x | 16 | 0 | 4 |
| S301.3 McpBridge + JiraAdapter | M | 0.8x | 44 | 0 | 0 |
| S301.4 rai docs CLI | S | 2.2x | 23 | 0 | 0 |
| S301.5 McpConfluenceAdapter | S | 2.0x | 21 | 0 | 3 |
| S301.6 Skill auto-sync hooks | S | 1.67x | 22 | 0 | 0 |
| S301.7 E2E dogfood | S | 0.78x | 0 | 1 (CQL) | 2 |
| S301.8 Complete backlog CLI | S | 1.25x | 10 | 0 | 0 |
| S301.9 FilesystemPMAdapter | S | 1.5x | 26 | 0 | 2 |
| **Total** | | **1.44x avg** | **265** | **2** | **12** |

## What Went Well

1. **McpBridge as generic layer** — the bet on wrapping MCP SDK paid off. Adding
   McpConfluenceAdapter after McpJiraAdapter took 25 min (2.0x velocity) because
   the bridge pattern was established.
2. **Extract→refine→mechanical pattern** (PAT-E-442/443) — velocity compounded
   across stories as patterns solidified.
3. **QR consistently found real issues** — 12 fixes across 9 stories that automated
   gates missed (semantic bugs, dead code, DRY violations).
4. **Token reduction exceeded target** — 27x measured vs 10x goal.

## What Could Be Better

1. **S301.3 was the slowest story (0.8x)** — first McpBridge implementation had
   discovery overhead (stdio transport, async wrapping). Expected for foundational work.
2. **S301.7 E2E was also slow (0.78x)** — integration testing against real Jira/Confluence
   exposed a CQL bug that unit tests with mocks would never catch. The slowness was
   productive — PAT-E-539 (integration gate) captured the lesson.
3. **MCP dependency fragility** — `mcp` package not available in all worktrees,
   causing import errors. Need to handle optional dependency gracefully.

## Patterns Captured

| ID | Type | Summary |
|----|------|---------|
| PAT-E-555 | process | Lint all files (src + tests) before commit |
| PAT-E-556 | technical | McpBridge: call_tool returns content[0].text, not raw result |
| PAT-E-572 | architecture | Value preservation gate — domain intelligence vs pass-through |
| PAT-E-573 | process | KISS review before implementation catches over-engineering |
| PAT-E-574 | codebase | Artifact type → path convention for rai docs |
| PAT-E-596 | technical | Markdown table round-trip validation |

## Process Insights

- **Full skill cycle for every story** worked — even XS/S stories benefited from
  design→plan→implement→review→close. The overhead was minimal (~5 min) and
  the discipline prevented drift.
- **QR as external auditor** is the highest-value gate after TDD. 12 fixes in 9
  stories = ~1.3 fixes/story average. All were semantic issues invisible to linters.
- **Worktree isolation** kept E301 independent from E325 development.
