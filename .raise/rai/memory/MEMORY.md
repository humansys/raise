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
- `/rai-epic-start` — Create epic branch from development branch
- `/rai-epic-design` — Design epic scope, stories, architecture
- `/rai-epic-plan` — Sequence stories with milestones and dependencies
- `/rai-epic-close` — Epic retrospective, metrics capture, merge to dev

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
| **Epic branch exists** | **Epic design** (/rai-epic-start) |
| **Story branch and scope commit** | **Story work** (/rai-story-start) |
| **Plan exists** | **Implementation** (/rai-story-plan) |
| **Retrospective complete** | **Story close** (/rai-story-review) |
| **Epic retrospective complete** | **Epic merge** (/rai-epic-close) |
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

- **PAT-E-440:** _deprecation_warning new_cmd param: cuando el nombre del subcomando canónico difiere del legado (add-pattern→add), pasar new_cmd explícito para mensaje correcto
- **PAT-E-441:** import location trap: get_memory_dir_for_scope vive en rai_cli.memory, no en rai_cli.config.paths — verificar imports en Gemba antes de copiar de memoria
- **PAT-E-442:** Repetitive extractions compound: 1st establishes pattern, 2nd refines, 3rd is mechanical. Plan decompositions in 3+ reps. (E247: 1.6x→1.33x→2.86x)
- **PAT-E-443:** Extraction compounding — repetitive God Object extractions show compounding velocity: first establishes pattern (M, 1.6x), second refines (S, 1.33x), third is mechanical (S, 2.86x). Plan decompositions in 3+ reps.
- **PAT-E-444:** Fixed coverage gates (e.g. --cov-fail-under=90) create Goodhart dynamics: penalize cleanup, incentivize test muda. Use coverage as diagnostic, not gate. Cover domain logic and edge cases, not glue/wrappers.
- **PAT-E-445:** For deletion stories, the grep gate IS the design — blast radius discovery replaces formal design
- **PAT-E-446:** Typer RED test gotcha: exit_code \!= 0 passes for both 'command doesnt exist' and 'command validation error'. Always add content assertions alongside exit code checks.
- **PAT-E-447:** Pre-implementation arch review + test muda analysis: run together, integrate muda cleanup into implementation tasks. Avoids separate cleanup stories and catches waste before its written.
- **PAT-E-448:** Typer RED test gotcha: exit_code != 0 passes for both command-not-found and validation-error. Always add content assertions.
- **PAT-E-449:** Pre-implementation arch review + test muda analysis as combo. Integrate cleanup into implementation tasks.

---

*Last updated: 2026-02-23*
*Generated by `rai graph build`*
