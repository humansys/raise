# Implementation Plan: F14.0 DX Quality Gate

> Decomposition of scope into atomic, executable tasks.
> **Philosophy:** Dogfood first, then publish. Prove standards work before making them official.

**Estimated SP:** 8 (M-sized feature, multi-phase)
**Sessions:** 2-3 (can checkpoint between phases)

---

## Task Breakdown

### Phase 1: Synthesize Standards

Create the reference document from research. Not yet integrated into framework.

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T1.1 | Synthesize Pydantic v2 research into guardrails section | — | 20m |
| T1.2 | Synthesize Typer CLI research into guardrails section | — | 20m |
| T1.3 | Synthesize Security research into guardrails section | — | 20m |
| T1.4 | Synthesize Pytest research into guardrails section | — | 15m |
| T1.5 | Synthesize DRY/SOLID research into guardrails section | — | 15m |
| T1.6 | Assemble `guardrails-stack.md` with all sections | T1.1-T1.5 | 15m |
| **T1.X** | **Commit: "docs(f14.0): synthesize stack guardrails from research"** | T1.1-T1.6 | — |

**Phase 1 Total:** ~1h 45m

---

### Phase 2: Scan and Fix Codebase

#### 2.1 Critical Fixes

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T2.1 | Fix `raise init` output — add CLI vs Skills explanation | — | 30m |
| T2.2 | Add post-init guidance — show manifest, next steps | T2.1 | 20m |
| T2.3 | Resolve MemoryGraph deprecation — assess and fix | — | 45m |
| **T2.X** | **Commit: "fix(init): clarify CLI vs Skills, resolve deprecations"** | T2.1-T2.3 | — |

#### 2.2 DRY Violations

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T2.4 | Extract `sanitize_id()` to `core/text.py` | — | 20m |
| T2.5 | Update vision.py and constitution.py to use shared sanitizer | T2.4 | 10m |
| T2.6 | Create `GraphBase` mixin with common graph methods | — | 30m |
| T2.7 | Apply GraphBase to ConceptGraph, UnifiedGraph | T2.6 | 20m |
| T2.8 | Extract `get_xdg_dir()` parameterized helper | — | 15m |
| T2.9 | Refactor paths.py to use helper | T2.8 | 10m |
| **T2.Y** | **Commit: "refactor: extract duplicated utilities (DRY)"** | T2.4-T2.9 | — |

#### 2.3 Code Hygiene

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T2.10 | Delete `.claude/skills/epic-close/skill.md` (old version) | — | 2m |
| T2.11 | Standardize session skill headers | — | 10m |
| T2.12 | Rename `dump` → `list` in memory CLI | — | 15m |
| T2.13 | Run new pre-commit hooks, fix any failures | T1.8 | 20m |
| **T2.Z** | **Commit: "chore: hygiene fixes (skill headers, CLI naming)"** | T2.10-T2.13 | — |

#### 2.4 Validate Against Guardrails

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T2.14 | Scan codebase against Pydantic guardrails | T1.6 | 20m |
| T2.15 | Scan codebase against Security guardrails | T1.6 | 20m |
| T2.16 | Fix violations found (estimated) | T2.14-T2.15 | 30m |
| **T2.W** | **Commit: "fix: address guardrail violations"** | T2.14-T2.16 | — |

**Phase 2 Total:** ~4h 45m

---

### Phase 3: Verification

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T3.1 | Run full test suite, ensure >90% coverage | Phase 2 | 10m |
| T3.2 | Run existing pre-commit hooks on full codebase | Phase 2 | 5m |
| T3.3 | Manual test: fresh `raise init` flow | T2.1-T2.2 | 10m |
| T3.4 | Review guardrails-stack.md against what we learned fixing code | Phase 2 | 15m |
| **T3.X** | **Commit: "test(f14.0): verify fixes, refine guardrails"** | T3.1-T3.4 | — |

**Phase 3 Total:** ~40m

---

### Phase 4: Framework Integration

Only after dogfooding proves the guardrails work, integrate into framework.

| Task | Description | Depends On | Est |
|------|-------------|------------|-----|
| T4.1 | Update `/feature-review` with Jidoka checkpoint | Phase 3 | 15m |
| T4.2 | Update `.pre-commit-config.yaml` (pip-audit, detect-secrets) | Phase 3 | 10m |
| T4.3 | Reference guardrails-stack.md from CLAUDE.md | Phase 3 | 5m |
| T4.4 | Update scope.md with completed items | Phase 3 | 5m |
| **T4.X** | **Commit: "feat(f14.0): integrate guardrails into framework"** | T4.1-T4.4 | — |

**Phase 4 Total:** ~35m

---

## Summary

| Phase | Purpose | Tasks | Time |
|-------|---------|-------|------|
| Phase 1: Synthesize | Define standards from research | 7 | 1h 45m |
| Phase 2: Fix | Apply standards to our code | 17 | 4h 45m |
| Phase 3: Verify | Prove it works | 4 | 40m |
| Phase 4: Integrate | Publish to framework | 4 | 35m |
| **Total** | | **32** | **~7h 45m** |

---

## Execution Order (Dogfood First)

```
Session 1:
├── T1.1-T1.5 (parallel synthesis)
├── T1.6 (assemble guardrails-stack.md)
└── Commit Phase 1

Session 2:
├── T2.1-T2.3 (critical fixes) → Commit
├── T2.4-T2.9 (DRY fixes) → Commit
├── T2.10-T2.13 (hygiene) → Commit
└── Checkpoint

Session 3:
├── T2.14-T2.16 (guardrail validation) → Commit
├── T3.1-T3.4 (verification) → Commit
├── T4.1-T4.4 (framework integration) → Commit
└── /feature-review → /feature-close
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| MemoryGraph migration complex | Assess first; if >1h, defer to post-F&F |
| Too many guardrail violations | Prioritize security > correctness > style |
| Tests break after refactor | Run tests after each commit, fix immediately |

---

## Dependencies

- Research completed (6 catalogs) ✓
- ISSUE-005 documented ✓
- On feature branch ✓

---

*Plan created: 2026-02-05*
*Ready for /feature-implement*
