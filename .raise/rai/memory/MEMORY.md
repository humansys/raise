# Rai Memory — raise-cli

> Permanent knowledge for this project. Loaded into system prompt.

---

## RaiSE Framework Process

### Work Lifecycle (Always Follow)

```
EPIC LEVEL:
  /epic-start → /epic-design → /epic-plan → [stories] → /epic-close

STORY LEVEL (per story):
  /story-start → /story-design* → /story-plan → /story-implement → /story-review → /story-close

* *design optional for S/XS stories

SESSION LEVEL:
  /session-start → [work] → /session-close
```

## Available Skills (20 total)

### Session Skills
- `/session-start` — Load memory, analyze progress, propose focused work
- `/session-close` — Capture learnings, update memory, log session

### Epic Skills
- `/epic-start` — Create epic branch from development branch
- `/epic-design` — Design epic scope, stories, architecture
- `/epic-plan` — Sequence stories with milestones and dependencies
- `/epic-close` — Epic retrospective, metrics capture, merge to dev

### Story Skills
- `/story-start` — Create story branch and scope commit
- `/story-design` — Create lean specification for complex stories
- `/story-plan` — Decompose into atomic executable tasks
- `/story-implement` — Execute tasks with TDD and validation gates
- `/story-review` — Extract learnings, identify improvements
- `/story-close` — Verify, merge, cleanup

### Discovery Skills
- `/discover-start` — Initialize codebase discovery
- `/discover-scan` — Extract symbols and synthesize descriptions
- `/discover-validate` — Human review of synthesized descriptions
- `/discover-complete` — Export to graph format

### Meta Skills
- `/skill-create` — Create new skills with framework integration

### Other Skills
- `/research` — Epistemologically rigorous research
- `/debug` — Root cause analysis using lean methods
- `/framework-sync` — Sync framework files across locations

---

### Gate Requirements

| Gate | Required Before |
|------|-----------------|
| **Epic branch exists** | **Epic design** (/epic-start) |
| **Story branch and scope commit** | **Story work** (/story-start) |
| **Plan exists** | **Implementation** (/story-plan) |
| **Retrospective complete** | **Story close** (/story-review) |
| **Epic retrospective complete** | **Epic merge** (/epic-close) |
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
  └── v2 (development)
        └── epic/e{N}/{name}
              └── story/s{N}.{M}/{name}
```

- Stories merge to epic branch
- Epics merge to development branch (v2)
- Development merges to main at release

---

## Key Patterns (from memory)

- **PAT-194:** Infrastructure without wiring is invisible debt — functions that exist but are never called create false confidence
- **PAT-195:** Scope wiring bugs are silent — new code paths may default to the wrong scope (project vs personal) without errors, causing data fragmentation and ID resets. Integration tests that verify end-to-end data flow catch these.
- **PAT-196:** Architecture docs are the map for future sessions — if they're stale, new code uses wrong paths. Structural changes (directory splits, scope migrations) must update module docs before story close.
- **PAT-197:** Governance drift between skills and patterns — skills can encode stale guidance that pattern memory has already corrected. Periodic reconciliation needed when patterns evolve faster than skill definitions.
- **PAT-198:** Module names in raise memory context require mod- prefix — document naming conventions in downstream consumer skills
- **PAT-199:** Module names in raise memory context require mod- prefix — document naming conventions in downstream consumer skills
- **PAT-200:** Governance doc structure (YAML frontmatter, section format) must be deterministic (CLI) for graph parser compatibility. Content is inference (skill). Mixing both in a skill is fragile.
- **PAT-201:** Separate skills for fundamentally different user experiences (greenfield vs brownfield) produce better DX than a single skill with branching logic.
- **PAT-202:** Templates-as-contract: when CLI scaffolds files that parsers later consume, template files ARE the contract. Store them as inspectable assets (not Python strings) so the integration test catches drift. Follow existing distribution patterns (rai_base + importlib.resources) before inventing new ones.
- **PAT-203:** Templates-as-contract: when CLI scaffolds files that parsers later consume, template files ARE the contract. Store as inspectable assets (not Python strings), follow existing distribution patterns (rai_base + importlib.resources).

---

*Last updated: 2026-02-08*
*Generated by `raise memory generate`*
