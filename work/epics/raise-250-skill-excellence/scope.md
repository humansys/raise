# Epic E250: Skill Excellence — Scope

> **Status:** IN PROGRESS
> Branch: `epic/e250/skill-excellence`
> Created: 2026-02-23
> Base: `v2`

---

## Objective

Redesign the 23 built-in RaiSE skills with a conscious, evidence-based structural pattern that maximizes agent reliability. These skills are the open-core reference implementation — they should represent our best work.

**Value proposition:** Skills that agents follow reliably, with minimal token waste, consistent structure, and zero stale references. Every line earns its place.

---

## In Scope

**MUST:**
- Define a canonical skill structure pattern (the "Skill Contract")
- Fix all critical issues (stale refs, broken commands, naming inconsistencies)
- Reduce token bloat (target: 50%+ substance ratio across all skills)
- Unify feature/story terminology
- Remove dead weight (stale ShuHaRi, obsolete memory model refs, orphan telemetry promises)

**SHOULD:**
- Deduplicate shared content across skills
- Establish frontmatter schema standard
- Improve agent-friendliness score to 4+ for all skills

---

## Out of Scope (defer)

- Skill Builder (RAISE-242/S2) — separate epic, builds on this foundation
- Semantic Validator CLI code (RAISE-242/S1) — reassess after this epic
- New skills — this epic improves existing, doesn't create new
- Skill runtime/execution engine — skills remain markdown instructions

---

## Done when

- [ ] All 23 skills follow the canonical structure pattern
- [ ] Zero stale references (files, commands, terminology)
- [ ] All skills ≥50% substance ratio
- [ ] Consistent naming (story vs feature resolved)
- [ ] Tests pass, skills_base/ synced to .claude/skills/
- [ ] Epic retrospective done
- [ ] Merged to `v2`
