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

- Stories branch from and merge to development branch (dev)
- Development merges to main at release
- Epics are logical containers (directory + tracker), not branches

---

## Key Patterns (from memory)

- **PAT-E-480:** Sync script integration test: after running sync-skills.py, always run full test suite (not just validator tests) because the sync modifies __init__.py which other tests import
- **PAT-E-481:** Silent parse failures in validator: skills that fail Pydantic validation during parse are silently skipped by rai skill validate. When auditing all skills, also check for parse errors separately
- **PAT-E-482:** Sync script integration test: after running sync-skills.py, always run full test suite
- **PAT-E-483:** Silent parse failures in validator: skills failing Pydantic validation are silently skipped
- **PAT-E-484:** Gate check: run ruff on both src/ and tests/ — not just changed source files. Unused imports in tests slip through when only src/ is linted.
- **PAT-E-485:** Bug report mechanism ≠ root cause: bug descriptions often name the symptom or a historical mechanism. Always go to code (Genchi Genbutsu) before forming the fix hypothesis. In RAISE-136 the bug said 'NodeType Literal rejects' but Literal had already been changed to str — real crash was missing required fields in fallback model_validate.
- **PAT-E-486:** Gate check: run ruff on both src/ and tests/ — not just changed source files. Unused imports in tests slip through when only src/ is linted.
- **PAT-E-487:** Bug report mechanism != root cause: bug descriptions name the symptom or a historical mechanism. Always go to code (Genchi Genbutsu) before forming the fix hypothesis.
- **PAT-E-488:** Pre-publish verification should include: README command audit, CHANGELOG entry, deprecated CLI refs grep in skills
- **PAT-E-489:** Contract chain preservation: when compressing skills, verify inter-skill artifact contracts survive. Templates externalize format; skills reference.

---

*Last updated: 2026-03-02*
*Generated by `rai graph build`*
