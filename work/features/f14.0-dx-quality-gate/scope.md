# Feature Scope: F14.0 DX Quality Gate

> Pre-distribution cleanup to ensure raise-cli quality before F&F release.
> **Philosophy:** Clean house before inviting guests. Fix our code against our own standards.

**Epic:** E14 Rai Distribution
**Branch:** `feature/e14/f14.0-dx-quality-gate`
**Priority:** HIGH (blocks clean F&F distribution)

---

## In Scope

### Phase 1: Establish Standards (Guardrails)

**1.1 Synthesize Research into Guardrails**
- [ ] Create `governance/solution/guardrails-stack.md`
- [ ] Synthesize 6 research catalogs into actionable patterns:
  - Pydantic v2 patterns and anti-patterns
  - Typer CLI design principles
  - Security checklist (OWASP, Bandit rules)
  - Pytest best practices
  - DRY/SOLID for Python (Rule of Three)
- [ ] Format: Pattern | Anti-pattern | Why | Example

**1.2 Update Framework Integration**
- [ ] Add Jidoka checkpoint to `/feature-review` skill
- [ ] Update `.pre-commit-config.yaml` (add pip-audit, detect-secrets)
- [ ] Reference guardrails-stack.md from CLAUDE.md

### Phase 2: Scan and Fix Codebase

**2.1 Critical Fixes (ISSUE-005)**
- [ ] Fix `raise init` output — clarify CLI vs Claude Code skills gap
- [ ] Add post-init guidance — what to do next
- [ ] Resolve MemoryGraph deprecation — complete migration or remove

**2.2 DRY Violations (from audit)**
- [ ] Extract ID sanitization to `core/text.py` (vision.py, constitution.py)
- [ ] Extract graph methods to base class/mixin (ConceptGraph, UnifiedGraph)
- [ ] Extract XDG path helpers to parameterized function (paths.py)
- [ ] Consolidate memory loaders if rule-of-three applies

**2.3 Code Hygiene**
- [ ] Delete duplicate `/epic-close/skill.md` (old version)
- [ ] Standardize skill headers ("When to Use" → "Purpose")
- [ ] Rename `raise memory dump` → `raise memory list`
- [ ] Fix any security issues found by new pre-commit hooks

**2.4 Validate Against New Guardrails**
- [ ] Run full codebase scan against guardrails-stack.md
- [ ] Fix violations found (prioritize by severity)
- [ ] Document any intentional exceptions with rationale

### Phase 3: Verification

- [ ] All tests pass (>90% coverage)
- [ ] All pre-commit hooks pass (including new ones)
- [ ] Manual review of `raise init` flow
- [ ] Retrospective and learnings captured

---

## Out of Scope

### Deferred to Post-F&F
- Skill bloat refactoring (epic-plan 736 lines → <400)
- Split `raise context query` into two commands
- Schema consolidation (governance/query vs context/query)
- Telemetry boilerplate extraction from skills
- Convention schema flattening (8 models → 3)
- ISSUE-003/004 directory restructuring

### Deferred to V3
- Property-based testing adoption (Hypothesis)
- Performance optimization
- Full test coverage for edge cases

---

## Done Criteria

- [ ] `guardrails-stack.md` created with synthesized best practices
- [ ] `/feature-review` has Jidoka checkpoint for stack patterns
- [ ] Pre-commit hooks updated (pip-audit, detect-secrets)
- [ ] `raise init` output clearly distinguishes CLI/Skills
- [ ] No deprecated code warnings in normal usage paths
- [ ] Zero duplicated utility functions (sanitizers, paths, graph methods)
- [ ] Codebase passes scan against new guardrails
- [ ] All tests pass (>90% coverage maintained)
- [ ] All quality checks pass (ruff, pyright, bandit, new hooks)
- [ ] Retrospective complete

---

## Research Foundation

| Topic | Location | Key Takeaways |
|-------|----------|---------------|
| Pydantic v2 | `work/research/pydantic-v2-best-practices/` | BaseModel at boundaries, TypeAdapter singleton |
| Typer CLI | `work/research/typer-cli-best-practices/` | Flags over positional, multi-format output |
| Python Structure | `work/research/python-project-structure-2025/` | src layout validated, minimal __init__.py |
| Pytest | `work/research/pytest-best-practices/` | AAA pattern, factory fixtures |
| Security | `work/research/python-security/` | Input validation, subprocess shell=False |
| DRY/SOLID | `work/research/dry-solid-python/` | Rule of three, composition over inheritance |

---

## Related Issues

- ISSUE-003: Directory Structure Ontology
- ISSUE-004: Epic/Feature Tree Structure
- ISSUE-005: DX Audit Findings (primary driver)

---

*Created: 2026-02-05*
