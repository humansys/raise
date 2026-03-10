---
epic_id: "E347"
name: "Backlog Automation"
status: "complete"
started: "2026-03-03"
completed: "2026-03-03"
---

# Epic Retrospective: E347 — Backlog Automation

## Summary

Delivered adapter-agnostic backlog automation for the RaiSE framework. The epic replaced fragile, Jira-hardcoded workflows with a pluggable adapter layer backed by YAML file storage, enabling offline-first operation and future adapter extensibility.

## Deliverables

| Story | Name | Size | Key Deliverable |
|-------|------|:----:|-----------------|
| S347.1 | Adapter default in manifest | S | `backlog.adapter_default` in manifest.yaml |
| S347.2 | FileAdapter parity | M | YAML file store at `.raise/backlog/items/{KEY}.yaml` |
| S347.3 | Skills via backlog CLI | S | 4 lifecycle skills use `rai backlog` instead of direct file manipulation |
| S347.4 | BacklogHook adapter-aware | S | Label-first search, isinstance dispatch, adapter-agnostic resolution |
| S347.5 | Session-start live query | S | `LiveBacklogStatus` with ThreadPoolExecutor timeout |
| S347.6 | Backlog sync command | M | `rai backlog sync` — pull from remote, write governance/backlog.md |
| S347.7 | Integration tests + dogfood | M | 13 cross-component integration tests |

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 7 (2S + 2M + 2S + 1M) |
| Commits | 166 |
| Lines changed | +8,080 / -1,702 |
| Files changed | 156 |
| Tests added | ~120 new tests (3502 total, up from ~3400) |
| Patterns captured | 20 (PAT-E-614 through PAT-E-635) |
| Duration | 1 session (~6 hours) |

## What Went Well

1. **Human-driven design pivot (S347.2):** User questioned markdown parsing and proposed YAML file store. This eliminated all fragile regex, made round-trips deterministic, and simplified every subsequent story. The single best decision in the epic.

2. **Subagent delegation worked smoothly:** Each story phase ran as an independent subagent. The orchestrator (story-run) maintained context while subagents executed focused work. ~95% autonomous execution.

3. **Risk-first ordering paid off:** T1/T2 in each story tackled the hardest unknowns first. No late-cycle surprises.

4. **QR caught real bugs:** Immutable fields guard (S347.2), ThreadPoolExecutor SystemExit escape (S347.5), atomic write suffix bug (S347.6), pipe escaping in markdown tables (S347.6). None of these would have been caught by linting or type checking.

5. **Consistent velocity:** Stories completed near estimates (0.86x to 1.33x range). No major over/underestimates.

## What To Improve

1. **Interactive design for non-obvious decisions:** S347.4 design was done interactively (adapter-aware query strategy) and produced a better result than S347.2's initial design (which needed a pivot). Consider making design interactive by default for M+ stories.

2. **Jira ticket coverage:** S347.5 and S347.7 had no Jira tickets. The epic plan should create all story tickets upfront via `rai backlog create`.

3. **Story-run DX iterated mid-epic:** Completion banners were added and refined twice during the epic. This is fine but ideally would be done before the epic starts.

4. **isinstance coupling:** S347.4 and S347.6 both use `isinstance(adapter, FilesystemPMAdapter)`. At 2 adapters this is proportional (PAT-E-628), but a third adapter will need a protocol attribute like `adapter.query_dialect`.

## Architectural Decisions

| Decision | Story | Rationale |
|----------|-------|-----------|
| YAML file store over markdown parsing | S347.2 | Deterministic round-trips, Pydantic validation, AI-first design |
| One YAML file per issue | S347.2 | Zero merge conflicts between branches, consistent with .raise/mcp/ pattern |
| Label-first search with summary fallback | S347.4 | Deterministic labels before fuzzy text (PAT-E-627) |
| isinstance dispatch for 2 adapters | S347.4/6 | Proportional for current scale, refactor at 4+ (PAT-E-628) |
| ThreadPoolExecutor for timeout | S347.5 | Portable, thread-safe, covers resolve_adapter + get_issue |
| Atomic write via os.replace | S347.6 | Cross-platform atomic, prevents partial writes |

## Patterns Captured

| ID | Type | Key Insight |
|----|------|-------------|
| PAT-E-614 | process | Manifest-based adapter default enables adapter-agnostic skills |
| PAT-E-616 | architecture | YAML file store over markdown for structured CRUD |
| PAT-E-617 | process | Design pivots during story are healthy when human-driven |
| PAT-E-618 | architecture | Legacy fallback via feature flag during migration |
| PAT-E-621 | technical | SystemExit is BaseException — catch explicitly in ThreadPoolExecutor |
| PAT-E-622 | architecture | Graceful degradation: never-fail functions with descriptive warnings |
| PAT-E-623 | technical | In-process adapter call saves 500ms over subprocess |
| PAT-E-624 | process | Prose-only edits benefit from explicit change maps |
| PAT-E-625 | process | Conditional CLI steps with "if ticket exists" guard |
| PAT-E-627 | technical | Label-first search before fuzzy text |
| PAT-E-628 | architecture | isinstance acceptable for 2-3 branches, refactor at 4+ |
| PAT-E-629 | process | Interactive design yields better non-obvious tradeoffs |
| PAT-E-630 | technical | Atomic write via temp file + os.replace |
| PAT-E-631 | process | Adapter type guard before sync (fail-fast) |
| PAT-E-632 | technical | Pipe escaping in markdown tables |
| PAT-E-633 | process | Shared fixtures in conftest keep test modules focused |
| PAT-E-634 | technical | yaml.safe_load over private methods for disk verification |
| PAT-E-635 | process | Risk-first ordering eliminates cascading failures |

## Next

- Merge epic to `dev`
- E347 enables: E349 (Adapter Integration Validation), E350 (Experience Portability)
- Technical debt: remove legacy markdown fallback in filesystem.py (deferred from S347.2)
