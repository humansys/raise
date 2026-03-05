# Rai Memory — raise-commons

> Permanent knowledge for this project. Loaded into system prompt.

---

## RaiSE Framework Process

### Work Lifecycle (Always Follow)

```
EPIC LEVEL:
  /rai-epic-start → /rai-epic-design → /rai-epic-plan → [stories] → /rai-epic-close

STORY LEVEL (per story):
  /rai-story-start → /rai-story-design* → /rai-story-plan → /rai-story-implement → /rai-story-review → /rai-story-close

* *design optional for S/XS stories

SESSION LEVEL:
  /rai-session-start → [work] → /rai-session-close
```

## Available Skills (19 total)

### Session Skills
- `/rai-session-start` — Load memory, analyze progress, propose focused work
- `/rai-session-close` — Capture learnings, update memory, log session

### Epic Skills
- `/rai-epic-start` — Initialize epic scope and directory structure
- `/rai-epic-design` — Design epic scope, stories, architecture
- `/rai-epic-plan` — Sequence stories with milestones and dependencies
- `/rai-epic-close` — Epic retrospective, metrics capture, tracking update

### Story Skills
- `/rai-story-start` — Create story branch and scope commit
- `/rai-story-design` — Create lean specification for complex stories
- `/rai-story-plan` — Decompose into atomic executable tasks
- `/rai-story-implement` — Execute tasks with TDD and validation gates
- `/rai-story-review` — Extract learnings, identify improvements
- `/rai-story-close` — Verify, merge, cleanup

### Discovery Skills
- `/rai-discover-start` — Initialize codebase discovery
- `/rai-discover-scan` — Extract symbols and synthesize descriptions
- `/rai-discover-validate` — Human review of synthesized descriptions, then export to graph format

### Meta Skills
- `/rai-skill-create` — Create new skills with framework integration

### Other Skills
- `/rai-research` — Epistemologically rigorous research
- `/rai-debug` — Root cause analysis using lean methods
- `/rai-framework-sync` — Sync framework files across locations

---

### Gate Requirements

| Gate | Required Before |
|------|-----------------|
| **Epic directory and scope initialized** | **Epic design** (/rai-epic-start) |
| **Story branch and scope commit** | **Story work** (/rai-story-start) |
| **Plan exists** | **Implementation** (/rai-story-plan) |
| **Retrospective complete** | **Story close** (/rai-story-review) |
| **Epic retrospective complete** | **Epic close** (/rai-epic-close) |
| Tests pass | Before any commit |
| Type checks pass | Before any commit |
| Linting passes | Before any commit |

---

## Critical Process Rules

1. **TDD Always** — RED-GREEN-REFACTOR, no exceptions
2. **Commit After Task** — Commit after each completed task, not just story end
3. **Full Skill Cycle** — Use skills even for small stories
4. **Ask Before Subagents** — Get permission before spawning subagents
5. **Delete Branches After Merge** — Clean up merged branches immediately
6. **HITL Default** — Pause after significant work for human review
7. **Direct Communication** — No praise-padding, say what needs saying
8. **Redirect When Dispersing** — Gently redirect tangents to parking lot
9. **Type Everything** — Type annotations on all code
10. **Pydantic Models** — Use Pydantic for all data structures
11. **Simple First** — Simple heuristics over complex solutions

---

## Branch Model

```
main (stable)
  └── dev (development)
        └── story/s{N}.{M}/{name}
```

- Stories branch from and merge to dev
- dev merges to main at release
- Epics are logical containers (directory + tracker), not branches

---

## Key Patterns (from memory)

- **PAT-E-589:** Module-level Path constant (_JIRA_YAML_PATH) as test seam: makes config readers testable via simple patch() without tmp_path fixtures threading through constructor. Trade-off: global state, but acceptable for read-only config files.
- **PAT-E-590:** Hook extension pattern: typed frozen event + LifecycleHook subscriber + entry point + error isolation. Zero changes to existing code.
- **PAT-E-591:** Module-level Path constant as test seam for config readers — testable via simple patch() without constructor injection
- **PAT-E-592:** Dogfood stories need ~50% time buffer beyond task estimates for root cause analysis of discovered friction. F1 in S301.7 turned from 'Low friction' to 'High bug' requiring investigation + config fix.
- **PAT-E-593:** Confluence CQL search does not index spaces with unusual mixed-case keys (e.g. rAIse). Use simple keys (e.g. RaiSE1). get_page by ID/title works regardless — only search is affected.
- **PAT-E-594:** Environment-specific cache files (page ID mappings, sync state) must be gitignored from project creation. Committing them couples the repo to one developer's environment.
- **PAT-E-595:** CLI read commands (get, get-comments) should be separate from write commands and from each other — agents control context budget by choosing which to call. Predictable output size per command.
- **PAT-E-596:** Markdown table round-trip: when reusing an existing parser for reads, validate write→read consistency before assuming display format maps back correctly. normalize_status('📋 Backlog')→'draft' not 'pending' caught by TDD.
- **PAT-E-597:** from __future__ import annotations masks NameError for unimported names used in method bodies. Type annotations become lazy strings, so bare except swallows NameError silently. Always verify runtime imports match annotation imports when using future annotations.
- **PAT-E-598:** Bare except Exception in error-isolation patterns can hide import errors, type errors, and other bugs. Log the actual exception (at least at debug level) in catch-all handlers to avoid silent failures.

---

*Last updated: 2026-03-05*
*Generated by `rai graph build`*
