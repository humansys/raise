# E494: ACLI Jira Adapter — Scope

## Objective

Replace the MCP bridge-based Jira adapter with a thin ACLI subprocess wrapper that
supports multi-instance Jira, simplifies the codebase, and preserves governance and
observability. Remove the MCP adapter entirely.

## Value

- Users already have ACLI installed and authenticated — align adapter with their tool
- Multi-instance unlocks working across rai-agent + humansys sites from one `rai backlog`
- Eliminates MCP subprocess + async bridge complexity for basic Jira CRUD
- ACLI returns raw Jira API JSON — the nested format our parsers already handle
- Removing MCP adapter reduces dependency surface (`mcp` package no longer needed for Jira)

## In Scope (MUST)

- `AcliJiraAdapter` implementing `AsyncProjectManagementAdapter` (11 methods)
- Core `_run_acli()` — subprocess, `--json` parsing, error handling, telemetry
- Multi-instance: `jira.yaml` with `instances:` section, site switching per call
- Delete `McpJiraAdapter` and its entry point
- Replace `jira` entry point with ACLI adapter
- Clear error if ACLI binary not found (`acli` not in PATH)

## In Scope (SHOULD)

- `rai doctor` check for ACLI availability and auth status
- JQL quoting for reserved words (RAISE → 'RAISE')

## Out of Scope

- Protocol changes (`AsyncProjectManagementAdapter` stays as-is)
- Data model changes (`IssueSpec`, `IssueDetail`, etc. stay as-is)
- CLI command changes (`rai backlog` interface unchanged)
- Confluence adapter (separate epic if needed)
- ACLI installation/auth setup (prerequisite, user responsibility)

## Stories

### S494.1: Spike — ACLI JSON mapping validation (XS)

Validate that ACLI `--json` output maps cleanly to existing adapter models.
No code — just a test script and documented findings.

**Dependencies:** None (foundation)

### S494.2: Core subprocess wrapper with telemetry (S)

`_run_acli(args) -> dict` — subprocess call, JSON parse, logfire span,
error handling. Single function that all protocol methods delegate to.

**Dependencies:** S494.1 findings

### S494.3: Full protocol implementation (M) ✓

All 11 `AsyncProjectManagementAdapter` methods via ACLI commands.
170 LOC adapter, 31 tests, nested-only parsers, convention-based status.

**Dependencies:** S494.2 | **Completed:** 2026-03-19

### S494.4: Multi-instance config and site switching (S) ✓

Extend `jira.yaml` schema with `instances:` section. Adapter resolves
project → instance → site. ACLI `auth switch` before calls when site differs.
61 tests, 5 design decisions, research grounding (7 tools analyzed).

**Dependencies:** S494.3 | **Completed:** 2026-03-19

### S494.5: Delete MCP adapter and migrate entry point (S) ✓

Remove `McpJiraAdapter`, its tests, and MCP-specific dependencies.
Register ACLI adapter as the sole `jira` entry point. Error on missing ACLI.
-1115 LOC, quality review clean.

**Dependencies:** S494.4 | **Completed:** 2026-03-20

### S494.6: Integration test suite for ACLI adapter (S)

On-demand integration tests that exercise the full round-trip: adapter → ACLI subprocess → Jira API → response parsing.
Validates epic done criteria with real infrastructure. Skips automatically when ACLI/credentials unavailable.

**Dependencies:** S494.5

## Done Criteria

- [ ] `rai backlog search/get/create/transition/comment` work via ACLI adapter
- [ ] Multi-instance tested: query RAISE (humansys) and RAI (rai-agent) in one session
- [ ] Logfire telemetry spans emitted per ACLI call (command, latency, success)
- [ ] Tests migrated to ACLI adapter
- [ ] MCP adapter and MCP Jira dependencies deleted
- [ ] Clear error message when ACLI not installed
- [ ] `rai doctor` reports ACLI availability (SHOULD)

## Risks

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| ACLI auth switch is slow (global state mutation) | Medium | Medium | Cache current site in adapter, only switch when needed |
| ACLI JSON output changes between versions | Low | High | Pin minimum ACLI version, test in CI |
| ACLI not installed on user machine | Medium | High | Clear error with install instructions, `rai doctor` check |

---

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Linear dependency chain. Each story builds on the previous. No parallelism.

| # | Story | Size | Strategy | Rationale |
| - | ----- | ---- | -------- | --------- |
| 1 | S494.1: Spike — ACLI JSON mapping | XS | Risk-first | Validates core hypothesis before writing production code |
| 2 | S494.2: Core subprocess wrapper | S | Walking skeleton | `_run_acli()` is the foundation; telemetry from day 1 |
| 3 | S494.3: Full protocol implementation | M | Dependency-driven | 11 methods, needs the core wrapper in place |
| 4 | S494.4: Multi-instance config + switching | S | Incremental | Extend working single-site adapter with site routing |
| 5 | S494.5: Delete MCP adapter + migrate entry point | S | Cleanup | Only after everything works on ACLI |

### Milestones

#### M1: Walking Skeleton (after S494.2)

- `_run_acli()` executes ACLI commands with JSON parsing
- Logfire telemetry span emitted per call
- At least one protocol method works E2E (e.g., `search`)
- **Demo:** `rai backlog search` works via ACLI wrapper (hardcoded adapter)

#### M2: Feature Complete (after S494.4)

- All 11 protocol methods work via ACLI
- Multi-instance tested: query RAI (rai-agent) and RAISE (humansys)
- `rai backlog` commands produce identical results to current MCP adapter
- **Demo:** `rai backlog search "..." -a jira` works across both Jira instances

#### M3: Epic Complete (after S494.5)

- MCP adapter deleted, ACLI is sole `jira` entry point
- All tests migrated
- Clear error on missing ACLI binary
- Done criteria met → ready for `/rai-epic-close`

### Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S494.1 Spike | ✓ done | ACLI JSON mapping validated |
| S494.2 Core wrapper | ✓ done | _run_acli() + telemetry |
| S494.3 Full protocol | ✓ done | 11 methods, 31 tests |
| S494.4 Multi-instance | ✓ done | 85 est / 80 actual, 1.06x |
| S494.5 Delete MCP | ✓ done | 15 est / 20 actual, 1.33x, -1115 LOC |
| S494.6 Integration tests | pending | Enabler — validates epic done criteria |
