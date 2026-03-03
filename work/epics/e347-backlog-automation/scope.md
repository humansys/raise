---
epic_id: "E347"
title: "Backlog Automation"
jira_key: "RAISE-347"
status: "in_progress"
branch: "epic/e347/backlog-automation"
base: "dev"
created: "2026-03-03"
appetite: "M (7 stories)"
---

# Epic Scope: Backlog Automation

## Objective
Make `rai backlog` the single reliable channel for reading and writing work state — transparent to backend (Jira or files) — so that skills, session-start, and humans always operate with real information.

## Value
Eliminates fragmentation that causes stale context in sessions, enables team visibility in Jira without manual intervention, and unblocks scaling to more developers/clients.

## Context
The backlog subsystem has two adapters (McpJiraAdapter, FilesystemPMAdapter) that aren't at parity. Skills edit `governance/backlog.md` directly instead of using `rai backlog` CLI. Session-start reads stale `session-state.yaml` instead of querying live state. BacklogHook hardcodes "jira" and uses fuzzy JQL search. Result: three disconnected worlds (Jira, backlog.md, session-state) that diverge silently.

**Problem Brief:** `work/problem-briefs/backlog-automation-2026-03-03.md`

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Offline mode (Jira down) | Fail fast | Zero divergence, one source of truth |
| backlog.md when Jira configured | Read-only mirror | Regenerated via `rai backlog sync`, never edited directly |
| Skills → backlog | Via CLI (`rai backlog`) | One path, auditable. Skills don't know what adapter is behind |
| Session-start → state | Live query via `rai backlog` | Real state, not stale snapshot. Explicit failure if unavailable |
| Adapter default | Configurable in manifest.yaml | Auto-detect if one, default if configured, `-a` for override |

**Architectural principle:** The adapter protocol is THE abstraction. All consumers (skills, hooks, session, humans) talk to `rai backlog` CLI. They never know or care what's behind it.

## In Scope (MUST)

1. Adapter default in manifest.yaml — eliminate mandatory `-a` flag
2. FileAdapter: stories, links, comments — full protocol parity
3. Skills via `rai backlog` CLI — no more direct backlog.md edits
4. BacklogHook adapter-aware — respects default, exact key resolution
5. Session-start live backlog query — real state, explicit failure
6. `rai backlog sync` — regenerate backlog.md from active adapter
7. Integration test suite — both adapters, same assertions

## Out of Scope

- New adapter types (GitHub Issues, Linear) — separate epic
- Real-time sync / webhooks — CLI-driven only
- Backlog visualization UI
- Bidirectional sync (Jira ↔ files) — one source of truth, not two

## Stories

| ID | Story | Description | Size | Dependencies |
|----|-------|-------------|------|-------------|
| S347.1 | Adapter default in manifest | Add `backlog.adapter_default` to manifest.yaml, update resolver | S | — |
| S347.2 | FileAdapter: stories + links + comments | Full protocol parity, not just epics | M | — |
| S347.3 | Skills via `rai backlog` CLI | Rewrite epic-start, epic-close, story-start, story-close | M | S347.1 |
| S347.4 | BacklogHook adapter-aware | Respect adapter default, exact key resolution | S | S347.1 |
| S347.5 | Session-start live backlog query | Bundle queries `rai backlog get` for current work | S | S347.1 |
| S347.6 | `rai backlog sync` — mirror generation | New command, regenerates backlog.md from active adapter | S | S347.1 |
| S347.7 | Integration tests + dogfood | Both adapters, same protocol assertions, dogfood on real epic | M | S347.2-6 |

### Dependency Graph

```
S347.1 (adapter default)
  ├── S347.3 (skills via CLI)
  ├── S347.4 (hook adapter-aware)
  ├── S347.5 (session-start live)
  └── S347.6 (sync command)
S347.2 (FileAdapter parity) ──┐
S347.3 ──────────────────────┤
S347.4 ──────────────────────┼── S347.7 (integration tests)
S347.5 ──────────────────────┤
S347.6 ──────────────────────┘
```

## Done Criteria

1. `rai backlog` works without `-a` when default configured in manifest
2. All lifecycle skills use `rai backlog` CLI — none edit backlog.md directly
3. Session-start shows live state of current epic/story
4. BacklogHook respects adapter default, resolves keys exactly
5. FileAdapter passes all protocol methods (including stories)
6. `rai backlog sync` regenerates backlog.md from active adapter
7. Integration test suite runs both adapters against same assertions
8. Dogfooded on a real epic lifecycle

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP bridge timeout adds latency to session-start | Medium | High | Aggressive timeout (5s), explicit message on failure |
| FileAdapter stories complicates backlog.md format | Low | Medium | Separate section or per-epic file |
| Rewritten skills break existing flow | Medium | High | Dogfood in S347.7 on real epic before merge |

## Progress

| Story | Status | Notes |
|-------|--------|-------|
| S347.1 | Pending | |
| S347.2 | Pending | |
| S347.3 | Pending | |
| S347.4 | Pending | |
| S347.5 | Pending | |
| S347.6 | Pending | |
| S347.7 | Pending | |
