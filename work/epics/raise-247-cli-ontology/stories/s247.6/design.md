---
story_id: "S247.6"
title: "Update all skills and generated docs"
epic_ref: "E247"
size: "M"
phase: "design"
created: "2026-02-23"
---

# Design: S247.6 — Update all skills and generated docs

## 1. What & Why

**Problem:** After S1-S5 restructured the CLI (graph, pattern, signal, release, info/profile), all 23 skill files in `skills_base/` still reference the old commands (`rai memory *`, `rai publish *`, `rai base *`). Agents executing these skills get stale instructions.

**Value:** Skills match the actual CLI, so agent-executed workflows work correctly without relying on deprecation shims.

## 2. Approach

Systematic find-replace across skill files and CLAUDE.md. No code changes — purely Markdown content updates.

**Components affected:**
- `src/rai_cli/skills_base/*/SKILL.md` — 18 files with stale refs (modify)
- `CLAUDE.md` — CLI Quick Reference section (modify)
- `.raise/rai/memory/MEMORY.md` — if stale refs exist (modify)

**Strategy:** Batch by command family, verify after each batch.

## 3. Gemba: Current State

### Stale reference counts by skill file

| Skill | `rai memory` refs | `rai publish` refs | `rai base` refs |
|-------|------|------|------|
| rai-discover-validate | 3 | 0 | 0 |
| rai-story-implement | 5 | 0 | 0 |
| rai-epic-design | 8 | 0 | 0 |
| rai-epic-start | 1 | 0 | 0 |
| rai-epic-close | 1 | 0 | 0 |
| rai-discover-document | 2 | 0 | 0 |
| rai-epic-plan | 5 | 0 | 0 |
| rai-project-create | 5 | 0 | 0 |
| rai-project-onboard | 3 | 0 | 0 |
| rai-session-start | 1 | 0 | 0 |
| rai-docs-update | 7 | 0 | 0 |
| rai-welcome | 1 | 0 | 0 |
| rai-research | 2 | 0 | 0 |
| rai-story-review | 14 | 0 | 0 |
| rai-session-close | 1 | 0 | 0 |
| rai-story-start | 2 | 0 | 0 |
| rai-story-plan | 5 | 0 | 0 |
| rai-story-design | 4 | 0 | 0 |
| rai-story-close | 2 | 0 | 0 |
| **CLAUDE.md** | 8 | 0 | 0 |
| **Total** | ~80 | 0 | 0 |

**Key finding:** No `rai publish` or `rai base` refs in skills — those were already cleaned in S4/S5. Only `rai memory` refs remain.

### Command Mapping (confirmed from CLI --help)

| Old Command | New Command | Context |
|-------------|-------------|---------|
| `rai memory build` | `rai graph build` | Graph construction |
| `rai memory query` | `rai graph query` | Graph querying |
| `rai memory context` | `rai graph context` | Module context |
| `rai memory extract` | `rai graph extract` | Concept extraction |
| `rai memory list` | `rai graph list` | Graph listing |
| `rai memory add-pattern` | `rai pattern add` | Pattern creation |
| `rai memory reinforce` | `rai pattern reinforce` | Pattern voting |
| `rai memory emit-work` | `rai signal emit-work` | Work lifecycle |
| `rai memory emit-calibration` | `rai signal emit-calibration` | Calibration |
| `rai memory add-calibration` | `rai signal emit-calibration` | Calibration (alias) |

## 4. Target Interfaces

No code changes. All modifications are Markdown content in skill SKILL.md files and CLAUDE.md.

**CLAUDE.md CLI Quick Reference — target state:**
```
- cmd: rai graph build | sig: [--output PATH] [--no-diff] | notes: NO --project flag, runs from CWD
- cmd: rai graph query | sig: QUERY_STR [--types TYPE] [--strategy keyword_search|concept_lookup] [--limit N] [--format human|json|compact] | notes: QUERY_STR positional
- cmd: rai graph context | sig: MODULE_ID [--format human|json] | notes: MODULE_ID positional (e.g. mod-memory)
- cmd: rai pattern add | sig: CONTENT [--context KEYWORDS] [--type TYPE] [--from STORY_ID] [--scope SCOPE] | notes: CONTENT positional, --from NOT --source
- cmd: rai signal emit-work | sig: WORK_TYPE WORK_ID [--event EVENT] [--phase PHASE] | notes: WORK_TYPE=epic|story, EVENT=start|complete|blocked
```

**Common Mistakes — target state:**
```
- wrong: rai graph build --project . | right: rai graph build | why: no --project flag
- wrong: rai pattern add --content "..." | right: rai pattern add "..." | why: CONTENT positional
- wrong: rai pattern add --source F1 | right: --from F1 | why: flag is --from
```

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **MUST NOT** change any Python source code — this is a documentation-only sweep
- **MUST** preserve skill structure (YAML frontmatter, step numbering, etc.)
- **MUST** run `rai init` after to propagate changes to `.claude/skills/` and `.agent/skills/`
- **MUST** pass verification gate from scope.md (grep finds 0 stale refs)
- PAT-E-151: Methodical approach — verify after each batch, don't rush
