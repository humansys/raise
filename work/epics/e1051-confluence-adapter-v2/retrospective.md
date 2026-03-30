# E1051: Confluence Adapter v2 — Epic Retrospective

## Summary

| Field | Value |
|-------|-------|
| **Epic** | E1051 |
| **Started** | 2026-03-28 |
| **Completed** | 2026-03-30 |
| **Stories planned** | 10 |
| **Stories delivered** | 7 (3 deferred to v2.5.0) |
| **Total tests** | 3781 (80+ new) |
| **Artifacts published** | 34 to Confluence |

## Delivered

1. **ConfluenceClient** — 11 methods wrapping atlassian-python-api, auth resolution, error normalization
2. **ConfluenceConfig** — multi-instance schema, 18 artifact routing types, flat config normalization
3. **PythonApiConfluenceAdapter** — DocumentationTarget with strict publish (routing + parent required)
4. **FilesystemDocsTarget** — local file write target for offline/git
5. **CompositeDocTarget** — dual-write (filesystem first for durability, remote last for URL)
6. **CLI extensions** — --file, --stdin, --path on `rai docs publish`
7. **14 skills updated** — all lifecycle + operational skills publish via adapter
8. **3 projects configured** — raise-commons, rai, raise-gtm

## Deferred (v2.5.0)

- S1051.4: Confluence discovery service
- S1051.5: Adapter doctor
- S1051.6: Config generator skill
- Reconciliation mechanism for sync-pending artifacts

## What Went Well

- **TDD caught every regression** — 80+ tests, zero bugs escaped to production
- **Architecture reviews found real issues** — permissive defaults → strict, result ordering in composite
- **Prerequisite discipline** — RAISE-1060 (models restructure) before building on shaky foundation
- **Dogfooding validated the chain** — this retrospective is published by the system we built
- **Cross-project setup** — 3 projects configured and verified in one session

## What Could Improve

- **Permissive defaults slipped through initial design** — AR caught it, but should have applied "reliable first" from the start
- **Resolver ordering (local vs remote)** — discovered during E2E, should have been designed in S1051.7
- **Skills update was iterative** — went from Write+publish → Write+--file → --stdin only. Should have designed the single-path approach first
- **Identity in config** — started with username in YAML, had to refactor to env vars mid-session

## Patterns Persisted

- backoff_and_retry built-in (don't build custom rate limiters)
- get_page_by_title falsy check (None OR {})
- set_page_label additive (diff + remove + add for replace)
- isinstance error mapping (not string matching)
- Identity in env vars, config PII-free

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Strict publish (require routing + parent) | Reliability over convenience | No orphan pages in Confluence |
| Composite auto-compose | Zero config for dual-write | Install [confluence] → automatic |
| Filesystem first in composite | Durability guarantee | Local copy always saved |
| --stdin + --path (single adapter path) | Skills never use Write tool for docs | Clean separation of concerns |
| Identity in env vars | Config shareable across team | PII-free yaml in git |

## Metrics

| Metric | Value |
|--------|-------|
| Stories: S1051.1 (Client) | M, 47 tests, 3 bugs found in QR/E2E |
| Stories: S1051.3 (Config) | S, 22 tests, 1 QR fix |
| Stories: S1051.2 (Adapter) | M, 16 tests, 2 AR strict fixes |
| Stories: S1051.7 (Composite) | M, 31 tests, reliability model |
| Stories: S1051.8 (Story skills) | S, 7 tests, CLI + 4 skills |
| Stories: S1051.9 (Epic skills) | S, 0 new tests, 4 skills |
| Stories: S1051.10 (Operational) | S, 0 new tests, 6 skills + routing |
| LOC src | ~450 new |
| LOC test | ~900 new |
| E2E verified | 9/9 adapter + 11/11 client |
