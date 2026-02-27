# Epic Scope: RAISE-242 Skill Ecosystem

> **Status**: In Progress
> **Branch**: `epic/raise-242/skill-ecosystem`
> **Base**: `v2`
> **Jira**: [RAISE-242](https://humansys.atlassian.net/browse/RAISE-242)

---

## Objective

Build the meta-skill infrastructure: a skill that generates new skills by composing existing CLI tools and following established patterns. Validate with a concrete client skill (rai-bugfix).

**Value proposition:** Standardized skill creation reduces errors, ensures consistency across the ecosystem, and lowers the barrier for expanding RaiSE's capability surface. Every future skill benefits from this investment.

---

## Architectural Context

**Affected module:** `mod-skills` (domain layer, `bc-skills` bounded context)

**Existing infrastructure (no changes needed):**

| Component | Location | Purpose |
|-----------|----------|---------|
| `schema.py` | `src/rai_cli/skills/` | Pydantic models: `Skill`, `SkillFrontmatter`, `SkillMetadata` |
| `scaffold.py` | `src/rai_cli/skills/` | Template generation with lifecycle inference |
| `validator.py` | `src/rai_cli/skills/` | Structural validation (required fields + sections) |
| `name_checker.py` | `src/rai_cli/skills/` | `{domain}-{action}` pattern, conflict detection |
| `locator.py` | `src/rai_cli/skills/` | Directory-based auto-discovery |
| `parser.py` | `src/rai_cli/skills/` | YAML frontmatter extraction |

**Key architectural decision:** ADR-012 (Skills orchestrate, CLI provides data). The skill creator is a pure orchestration skill — no CLI code changes needed.

**Discovery mechanism:** Convention-based. Any `{skill_dir}/{name}/SKILL.md` is auto-discovered. No manifest, no registration.

**Required SKILL.md sections:** Purpose, Context, Steps, Output (validated by `validator.py`).

**Naming pattern:** `{domain}-{action}(-{qualifier})*` with known lifecycle domains (session, epic, story, discover, skill, research, debug, framework, project, docs).

---

## In Scope

**MUST:**
- `rai-skill-create` skill — conversational skill generator that:
  - Validates name via `rai skill check-name`
  - Scaffolds structure via `rai skill scaffold`
  - Fills template with conversational input (replacing TODOs)
  - Reads reference skills for pattern matching
  - Validates result via `rai skill validate`
- `rai-bugfix` skill — systematic bug fixing skill created using the creator
- Both skills live in `.claude/skills/` (project-specific)

**SHOULD:**
- Skill creator adapts to mastery level (ShuHaRi)
- Reference skill selection is intelligent (picks relevant patterns by domain)

## Out of Scope

- Skill marketplace or distribution → future epic
- Modifications to `skills_base/` or CLI scaffold code → existing infra is sufficient
- Skill versioning or dependency management → premature
- Agent-specific adaptations (Cursor, Copilot plugins) → separate concern

---

## Stories

| # | JIRA | Story | Size | Depends On | Description |
|---|------|-------|------|------------|-------------|
| 1 | [RAISE-243](https://humansys.atlassian.net/browse/RAISE-243) | `rai-skill-create` | M | — | Conversational skill that composes CLI tools to generate valid skills |
| 2 | [RAISE-244](https://humansys.atlassian.net/browse/RAISE-244) | `rai-bugfix` | S | RAISE-243 | First client skill — validates the creator works end-to-end |

```
RAISE-243 (skill creator)
    ↓
RAISE-244 (bugfix — validation client)
```

**No parallel tracks** — RAISE-244 is both a deliverable and a validation gate for RAISE-243.

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage)
- [ ] Quality checks pass (ruff, pyright, bandit)
- [ ] Story retrospective complete

### Epic Complete
- [ ] `rai-skill-create` generates valid skills from conversation
- [ ] Generated skills pass `rai skill validate` without errors
- [ ] `rai-bugfix` created using `rai-skill-create` and works correctly
- [ ] All tests pass, types clean, lint clean
- [ ] Epic retrospective complete
- [ ] Merged to `v2`

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Skill creator produces skills that pass validation but are low quality | Medium | Medium | Use rai-bugfix as E2E quality gate; read reference skills for pattern matching |
| Over-engineering the creator with too many options | Medium | Low | Start minimal — name, purpose, steps. Iterate if needed |
| Template drift — scaffold template vs real skills diverge | Low | Low | Creator reads actual skills as patterns, not just the template |

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Skills orchestrate, CLI provides data | ADR-012 | Skill creator is pure orchestration — no CLI changes needed |

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-20

### Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | RAISE-243 `rai-skill-create` | M | None | M1 | Foundation — the creator must exist before any client skill |
| 2 | RAISE-244 `rai-bugfix` | S | RAISE-243 | M2 | Validation gate — proves the creator works E2E |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Creator works** | RAISE-243 | `rai-skill-create` generates a valid SKILL.md from conversation, passes `rai skill validate` |
| **M2: Epic complete** | +RAISE-244 | `rai-bugfix` created via creator, works correctly, epic retro done |

### Progress Tracking

| Story | Size | Status | Notes |
|-------|:----:|:------:|-------|
| RAISE-243 | M | ✅ Done | 1.33x velocity (original) + ADR-040 compliance 0.83x (reopen) |
| RAISE-244 | S | ✅ Done | 0.67x velocity — design pivot (single vs family) + language-agnostic fix |

**Milestones:**
- [x] M1: Creator works (2026-02-20)
- [x] M2: Epic complete (2026-02-27)

---

## Notes

### Design Philosophy
The skill creator is an **orchestration skill**, not a code generator. It composes existing CLI tools (`check-name` → `scaffold` → `validate`) and fills the template through conversation. The intelligence is in the conversation design, not in new infrastructure.

### Reference Skills
Best patterns to study: `rai-debug` (utility, methodology-driven), `rai-research` (utility, multi-step), `rai-story-design` (story lifecycle, structured output).

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-02-20 | Rai | Implementation plan — linear sequence, 2 milestones |
| 2026-02-20 | Rai | Epic design — architectural context, risk assessment, design philosophy |
| 2026-02-20 | Rai | Initial scope |
| 2026-02-26 | Rai | RAISE-243 reopened for ADR-040 compliance (E257): 508 → 150 lines |
| 2026-02-27 | Rai | RAISE-243 closed (ADR-040 iteration) |
| 2026-02-27 | Rai | RAISE-244 closed — rai-bugfix created via rai-skill-create, M2 achieved |
