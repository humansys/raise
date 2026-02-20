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

- **PAT-E-320:** Flat file as transient buffer between sessions — close writes to flat file for cross-session continuity, next start migrates to per-session dir for isolation. Two lifecycle roles require two storage locations.
- **PAT-T-001:** Existing content in other repos should be audited before writing new docs — raise-gtm had 9 high-quality bilingual docs pages that only need migration and updating, not rewriting
- **PAT-T-002:** Sync scripts that modify source files can introduce syntax errors (skills_base/__init__.py duplicated list assignment) — always run quality gates after sync
- **PAT-T-003:** Verify subagent bulk transforms before committing — grep for expected changes and residual old values. Subagents doing find-and-replace across many files frequently miss edge cases (code blocks, headings, anchor links).
- **PAT-T-004:** Verify subagent bulk transforms before committing — grep for expected changes and residual old values. Subagents doing find-and-replace across many files frequently miss edge cases.
- **PAT-T-005:** CLI --help shows all commands including internal/PRO — use memory cli-reference.md as authoritative scope for public docs, not raw --help output. Core commands: init, session, memory, discover, skill, profile, base, release. PRO/internal: backlog, publish.
- **PAT-F-002:** Official Atlassian Rovo MCP has severe token verbosity (24k tokens for trivial queries, 80k+ for edits). Community alternative sooperset/mcp-atlassian is more practical for daily use. aashari TOON format offers 30-60% token savings but uses generic HTTP tools.
- **PAT-F-003:** Discovery del propio sistema requiere leer código fuente como fuente de verdad, no docs — el código revela la arquitectura real (17 NodeTypes, 11 EdgeTypes, 3 memory tiers)
- **PAT-F-004:** Portability is distribution, not content: when the core artifact format (SKILL.md) is already cross-compatible, multi-platform support reduces to a path-mapping problem in the scaffolding layer
- **PAT-F-005:** Verify claims against primary sources before synthesizing: initial research mixed .antigravity/ with .agent/, skills with workflows, .md with .toml — second pass against official docs corrected 4 factual errors
- **PAT-F-006:** scaffold_skills() idempotency blocks upgrades — no mechanism to sync skills after pip upgrade. Version tracking exists in frontmatter but is not compared.
- **PAT-F-007:** Pydantic v2 frozen models: use model_config = ConfigDict(frozen=True), not class keyword frozen=True — pyright strict mode rejects the class keyword form
- **PAT-F-008:** from __future__ import annotations breaks Typer runtime type inspection for custom types (Enum, Literal). Typer needs real types at runtime, not string annotations. Remove __future__ import from CLI command modules.
- **PAT-F-009:** uv tool install creates a global install separate from project editable install. During development, uv run ensures project code is used. Bare command uses global tool.
- **PAT-F-010:** Typer CliRunner resolves types differently than real CLI — tests can pass while actual CLI is broken. E2E tests via CliRunner give false confidence for type-resolution bugs.
- **PAT-F-015:** Deterministic vs inference split is a core teaching concept for RaiSE adoption. CLI = facts (rai init --detect, rai memory build). Skills = judgment (/rai-project-onboard, /rai-epic-design). Users need to understand this boundary to trust the system.
- **PAT-F-016:** Reopening a closed epic for new milestones preserves traceability — same domain, same JIRA parent, new branch. Better than creating a new epic for continuation work.

---

*Last updated: 2026-02-20*
*Generated by `raise memory generate`*
