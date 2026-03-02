# Epic Scope: Skill Set Ecosystem

| Field | Value |
|-------|-------|
| ID | RAISE-340 |
| Branch | `epic/e340/skill-set-ecosystem` |
| Base | `dev` |
| Research | `work/research/skill-set-patterns/` |

## Strategic Objective

Enable team-level skill customization with named skill sets so teams can
maintain their own skill variants without losing changes on framework
upgrades. Market differentiator — no AI coding tool offers this.

## Value

After this epic, a tech lead can:
1. Create `.raise/skills/my-company/rai-story-run/SKILL.md` with custom steps
2. Run `rai init --skill-set my-company` → team gets customized story-run
3. Upgrade rai-cli → builtins update normally, `my-company/` untouched

## In Scope (MUST)

- `--skill-set` flag on `rai init` for overlay deployment
- Same-name-wins override (overlay replaces builtin in `.claude/skills/`)
- `.raise/skills/{set}/` as user-owned overlay directory
- Manifest tracks `origin` per skill (framework vs project)
- `/rai-skill-create` targets `.raise/skills/{set}/`

## In Scope (SHOULD)

- "Customize builtin" mode in `/rai-skill-create` (copy builtin as base)
- `rai skill scaffold --set` parameter

## Out of Scope

- Skill registry or package manager (Pro/Enterprise)
- Skill inheritance or `extends:` mechanism
- Per-section override (whole-skill granularity only)
- Remote skill set URLs
- Multi-IDE simultaneous deployment
- Intermediate `.raise/skills/default/` directory (deferred to v2.3 — AR Q2)

## Architecture

### Model: Overlay-Only (AR-simplified from two-hop)

Architecture review (Q2) determined that two-hop (builtins → `default/` →
`.claude/skills/`) adds complexity disproportionate for first public release.
Overlay-only preserves the existing builtin flow and adds team customization
on top.

### Directory Layout

```
.raise/skills/
  my-company/                 ← team set (user-owned, never auto-updated)
    rai-story-run/            ← overrides builtin (same-name wins)
      SKILL.md
    company-review/           ← team-only skill (no builtin equivalent)
      SKILL.md

.claude/skills/               ← deployment target (builtins + overlay merged)
  rai-session-start/SKILL.md  ← from builtin (no override)
  rai-story-run/SKILL.md      ← from my-company (override won)
  company-review/SKILL.md     ← from my-company (addition)
```

### Deployment Flow

```
rai init --skill-set <name>   (default: none — builtins only, same as today)

1. Builtins → .claude/skills/           (existing three-hash flow, unchanged)
2. If --skill-set provided:
   Read .raise/skills/{name}/
   For each skill in overlay:
     Copy to .claude/skills/ (overwrite, no three-hash — user owns overlay)
   Mark overlay skills with origin: "project" in manifest
```

### Key Decisions

| ID | Decision | Rationale | Evidence |
|----|----------|-----------|----------|
| D1 | Overlay-only (no intermediate default/) | AR Q2: simpler for first release, two-hop can be added later | Proportionality |
| D2 | Same-name = full replacement | No merge, most battle-tested | C2: Oh My Zsh, Helm, ESLint, Ansible |
| D3 | Overlay skills NOT three-hash managed | User-owned, never auto-updated by framework | C3: universal across 14 projects |
| D4 | `--skill-set` flag (explicit) | No magic detection, clear mental model | C5: market gap |
| D5 | No registry | YAGNI for open core | Brief constraint |
| D6 | Unify `_copy_skill_tree` to accept `Path | Traversable` | AR R1: avoid duplicate function | H7/H9 |

## Stories

| ID | Story | Size | Description |
|----|-------|------|-------------|
| S340.1 | Skill set overlay deployment | S | Add `--skill-set` to `rai init`. After builtin deployment, overlay `.raise/skills/{set}/` → `.claude/skills/`. Same-name wins. Manifest tracks origin. Unify `_copy_skill_tree` (AR R1). |
| S340.2 | Skill creation targets sets | S | `/rai-skill-create` generates into `.raise/skills/{set}/`. `rai skill scaffold --set`. "Customize builtin" mode copies installed builtin as base. |

## Plan

### Milestones

| M# | Milestone | Stories | Gate |
|----|-----------|---------|------|
| M1 | Overlay deployment | S340.1 | `rai init --skill-set X` produces correct merged `.claude/skills/` |
| M2 | Skill creation UX | S340.2 | `/rai-skill-create --set X` generates into `.raise/skills/{set}/` |

### Sequence

```
S340.1 (S) → S340.2 (S)
  M1           M2
```

Linear: S340.2 needs `--skill-set` concept from S340.1.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|------|--------|--------|----------|-------|
| S340.1 | S | Done | S | 1.0x | 8 tests, overlay-only, AR R1 adopted |
| S340.2 | S | Done | S | 1.0x | 4 tests, scaffold --set + --from-builtin |

## Done Criteria

- [ ] `rai init --skill-set X` deploys builtins + overlay merged to `.claude/skills/`
- [ ] Same-name-wins override verified (overlay skill replaces builtin)
- [ ] Overlay skills NOT touched by subsequent `rai init` without `--skill-set`
- [ ] `/rai-skill-create` generates into `.raise/skills/{set}/`
- [ ] Manifest tracks `origin: "project"` for overlay skills
- [ ] All existing tests pass + new tests per story
- [ ] Retrospective complete

## Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Overlay skill left in `.claude/skills/` after removing `--skill-set` | Med | Low | Document: user must re-run `rai init` without `--skill-set` to clean |
| `_copy_skill_tree` typing change (`Path | Traversable`) | Low | Low | Both types share the same interface; test both paths |

## Architecture Review

Formal AR completed pre-implementation. Verdict: **PASS WITH QUESTIONS**.
Key resolution: Q2 → overlay-only for v2.2 (two-hop deferred to v2.3).
Adopted: R1 (unify copy function), R2/R3 (deferred — not needed for overlay-only).
