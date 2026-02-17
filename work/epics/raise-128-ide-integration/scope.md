# Epic RAISE-128: IDE Integration — Scope

> **Status:** IN PROGRESS
> **JIRA:** [RAISE-128](https://humansys.atlassian.net/browse/RAISE-128)
> **Branch:** `epic/raise-128/ide-integration`
> **Created:** 2026-02-17
> **Focus:** Antigravity (Google)

---

## Objective

Make `rai init` work with Antigravity by introducing an IDE abstraction layer, decoupling 6 hardcoded Claude Code paths, and scaffolding to `.agent/` conventions.

**Value:** First concrete multi-IDE support. Strategic positioning as IDE-agnostic framework.

---

## Features

| # | ID | Feature | Size | Status | Description |
|---|-----|---------|:----:|:------:|-------------|
| 1 | F128.1 | IDE Configuration Model | S | Done | `IdeType` literal, `IdeConfig` Pydantic model (frozen), factory, manifest schema extension |
| 2 | F128.2 | Decouple Init from Claude Paths | M | Pending | Refactor 6 hardcoded `.claude/` references to use `IdeConfig` |
| 3 | F128.3 | Antigravity Scaffolding | S | Pending | Generate `.agent/skills/`, `.agent/rules/raise.md`, `.agent/workflows/` |
| 4 | F128.4 | Init --ide Flag + E2E Tests | S | Pending | Wire CLI flag, end-to-end validation for both IDEs |

**Total:** 4 features (S+M+S+S)

---

## In Scope

**MUST:**
- `IdeConfig` abstraction (ADR-031)
- Refactor all 6 coupling points to use `IdeConfig`
- `rai init --ide antigravity` generates correct `.agent/` structure
- `rai init` (no flag) defaults to `claude` — backward compatible
- IDE choice persisted in `.raise/manifest.yaml`
- Tests for both IDEs

**SHOULD:**
- `.agent/workflows/*.md` generation (slash command shims for Antigravity)

---

## Out of Scope

- Gemini CLI support → future story in this epic
- Other IDEs (Cursor, Windsurf, Continue) → future epic
- Runtime IDE detection → RAISE-127
- IDE-specific memory paths for Antigravity → skip (no equivalent)
- Migration of existing projects (`rai migrate --ide`) → parking lot

---

## Coupling Points Inventory

| # | File | Line | What | Feature |
|---|------|------|------|---------|
| 1 | `onboarding/skills.py` | 92 | `.claude/skills/` hardcoded in `scaffold_skills()` | F128.2 |
| 2 | `onboarding/claudemd.py` | 15-52 | `ClaudeMdGenerator` naming and CLAUDE.md path | F128.2 |
| 3 | `config/paths.py` | 262-290 | `get_claude_memory_path()` Claude-specific | F128.2 |
| 4 | `skills/locator.py` | 16-26 | `get_default_skill_dir()` hardcoded `.claude/skills/` | F128.2 |
| 5 | `context/builder.py` | 295 | `load_skills()` hardcoded `.claude/skills/` | F128.2 |
| 6 | `cli/commands/init.py` | 354-425 | Orchestration of all the above | F128.4 |

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] `rai init --ide antigravity` produces working `.agent/` structure
- [ ] `rai init` still works identically (backward compat)
- [ ] ADR-031 accepted
- [ ] All 4 features complete
- [ ] Epic retrospective done
- [ ] Merged to `v2`

---

## Dependencies

```
F128.1 (IDE Config Model)
  ↓
F128.2 (Decouple from Claude paths)
  ↓
F128.3 (Antigravity scaffolding)
  ↓
F128.4 (--ide flag + E2E tests)
```

**External blockers:** None

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| IDE abstraction pattern | ADR-031 | `IdeConfig` dataclass + factory, persist in manifest |

---

## Research Foundation

- SES-006: 9 IDEs mapped, 3 coupling points identified (expanded to 6 in gemba review)
- `dev/rai-architecture-discovery.md` §7-8: portability analysis + identity flow
- Antigravity conventions: `.agent/` dir, rules (always-on), skills (on-demand), workflows (user-triggered)

---

## Antigravity Mapping Reference

| Concept | Claude Code | Antigravity |
|---------|-----------|-------------|
| Skills dir | `.claude/skills/` | `.agent/skills/` |
| Instructions | `CLAUDE.md` | `.agent/rules/raise.md` |
| Slash commands | Skills = slash commands | `.agent/workflows/*.md` |
| Memory path | `~/.claude/projects/{encoded}/memory/MEMORY.md` | N/A (skip) |
| Loading | All skills always loaded | Progressive disclosure (lazy by description) |

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-17

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 1 | F128.1: IDE Configuration Model | S | None | M1 | Foundation — `IdeConfig` dataclass, factory, manifest schema. All other features consume this. |
| 2 | F128.2: Decouple Init from Claude Paths | M | F128.1 | M1 | Largest risk — 6 coupling points, backward compat required. Risk-early while energy high. |
| 3 | F128.3: Antigravity Scaffolding | S | F128.2 | M2 | First real multi-IDE output — validates the abstraction works for a second IDE. |
| 4 | F128.4: Init --ide Flag + E2E Tests | S | F128.3 | M3 | Integration — wires CLI, validates both IDEs end-to-end. |

**Sequencing strategy:** Dependency-driven (linear chain) + risk-early (F128.2 is largest/riskiest, positioned second).

**Parallel opportunities:** None. Strictly linear dependencies — each feature consumes the previous. Expected for a refactoring epic.

### Milestones

| Milestone | Features | Success Criteria | Demo |
|-----------|----------|------------------|------|
| **M1: Abstraction Ready** | F128.1, F128.2 | `IdeConfig` exists, all 6 coupling points use it, `rai init` backward compat passes | `rai init` works identically — invisible refactoring |
| **M2: Multi-IDE MVP** | +F128.3 | `.agent/skills/`, `.agent/rules/raise.md`, `.agent/workflows/` generated correctly | `rai init --ide antigravity` produces working structure |
| **M3: Epic Complete** | +F128.4 | `--ide` flag wired, E2E tests pass for both IDEs, all done criteria met | Full demo of both IDEs, ready for `/rai-epic-close` |

### Sequencing Rationale

**F128.1: IDE Configuration Model** (1st)
- Foundation required by everything. `IdeType` literal, `IdeConfig` dataclass, `get_ide_config()` factory, manifest `ide` field.
- Low risk: well-defined by ADR-031, pure new code (no refactoring yet).
- Enables: F128.2, F128.3, F128.4.

**F128.2: Decouple Init from Claude Paths** (2nd)
- Highest risk and largest feature. 6 files to refactor while maintaining backward compat.
- Risk-early: if the abstraction doesn't work cleanly across all 6 coupling points, better to discover now.
- Proves architecture: after this, `rai init` uses `IdeConfig` throughout but produces identical output.
- Enables: F128.3 (Antigravity needs decoupled code to plug into).

**F128.3: Antigravity Scaffolding** (3rd)
- First payoff — the abstraction produces real multi-IDE output.
- Medium risk: new territory (Antigravity conventions) but small scope.
- Validates: the `IdeConfig` pattern truly supports a second IDE.

**F128.4: Init --ide Flag + E2E Tests** (4th)
- Integration and validation. Wires the CLI entry point, adds comprehensive tests.
- Lowest risk: all pieces exist, this connects them.
- Epic done criteria gate.

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| F128.2 breaks backward compat | M | H | Test `rai init` output before/after each coupling point refactor. Gemba review already mapped all 6. |
| Antigravity conventions have undocumented requirements | L | M | Research foundation from SES-006 covers core conventions. Validate against Antigravity docs during F128.3 design. |
| Memory path asymmetry causes edge cases | L | L | `IdeConfig.memory_path` returns `None` for Antigravity. Consumers must handle `Optional`. |

### Progress Tracking

| Feature | Size | Status | Actual | Notes |
|---------|:----:|:------:|:------:|-------|
| F128.1: IDE Configuration Model | S | Done | 20 min | 3.0x velocity |
| F128.2: Decouple Init from Claude Paths | M | Pending | - | |
| F128.3: Antigravity Scaffolding | S | Pending | - | |
| F128.4: Init --ide Flag + E2E Tests | S | Pending | - | |

**Milestone Progress:**
- [ ] M1: Abstraction Ready (F128.1 + F128.2)
- [ ] M2: Multi-IDE MVP (+F128.3)
- [ ] M3: Epic Complete (+F128.4)

---

*Created: 2026-02-17*
*Plan added: 2026-02-17*
*F128.1 closed: 2026-02-17*
*Next: `/rai-story-start` for F128.2*
