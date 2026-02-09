---
id: E7
title: "Onboarding"
status: in-progress
branch: epic/e7/onboarding
base: v2
priority: P1 (F&F critical path)
estimated: M (3 stories)
---

# E7: Onboarding

## Objective

Enable any developer to go from `pip install raise-cli` to a fully RaiSE-ready project — working knowledge graph, governance structure, and first `/session-start` — through guided, scenario-specific skills.

**Value proposition:** Without onboarding, new users face a cold gap between installation and productive use. The graph has no governance concepts, skills have no context, and the methodology provides no value. Onboarding is what makes RaiSE *work* for someone who didn't build it.

**Success criteria:** A fresh clone + `pip install` + appropriate skill produces a project with parseable governance docs, a graph with 30+ nodes, and a successful `/session-start`.

## Context

E7 was originally scoped as "Distribution & Onboarding." E14 delivered the distribution half: base Rai bundling, bootstrap on `raise init`, MEMORY.md generation, skills scaffolding. What remains is the **onboarding experience**.

`raise init` creates infrastructure (manifest, profile, Rai base, skills) but leaves the governance content layer empty. The onboarding skills bridge that gap with two scenario-specific experiences:

- **Greenfield** is creative — "what do you want to build?" Rai as co-creator.
- **Brownfield** is analytical — "let me understand what you have." Rai as analyst.

These are fundamentally different experiences. Separate skills provide better DX than one skill trying to serve both (YAGNI on a router — `raise init` output recommends the right skill).

## Architectural Context

- **Module:** mod-onboarding (bc-experience domain, integration layer)
- **Pattern:** Skills orchestrate, CLI provides deterministic data (ADR-012, ADR-024)
- **Key insight:** Governance doc **structure** must be deterministic (CLI) for graph parser compatibility. Governance doc **content** is inference (skill) from user conversation.
- **Dependencies:** mod-session, mod-config, mod-cli, mod-rai_base, mod-skills_base, mod-discovery

## Features

| ID | Story | Size | Description |
|----|-------|:----:|-------------|
| S7.1 | Governance scaffolding CLI | S | Extend `raise init` to scaffold `governance/` with parser-compatible templates; output skill recommendation based on detected project type |
| S7.2 | `/project-create` skill | M | Greenfield: ask about project, fill governance content from conversation, build graph |
| S7.3 | `/project-onboard` skill | M | Brownfield: discovery pipeline + convention detection + ask about intent, fill governance content, build graph |

**Total:** 3 stories (S + M + M)

## In Scope

**MUST:**
- Governance template scaffolding with correct YAML frontmatter for graph parsers (CLI, deterministic)
- `/project-create` skill for greenfield projects
- `/project-onboard` skill for brownfield projects
- Generated docs: PRD, vision, guardrails, architecture (system-context, system-design, domain-model)
- Graph build + verification as final gate in both skills
- Both skills distributed via `DISTRIBUTABLE_SKILLS`
- `raise init` recommends the right skill in its output

**SHOULD:**
- Greenfield guardrails defaults per language/framework (without code to analyze)
- Already-initialized detection with governance gap analysis
- Experience-level adaptive verbosity (Shu/Ha/Ri)

## Out of Scope

- `raise status` health check → post-F&F
- `raise doctor` coherence audit → post-F&F
- Router skill (`/onboard`) → YAGNI, `raise init` recommends
- Multi-language convention detection → Python first
- Auto Shu→Ha→Ri progression → manual for now

## Dependencies

```
S7.1 (CLI: governance scaffolding)
  ↓
S7.2 (skill: project-create) ──┐
                                │ (parallel, independent)
S7.3 (skill: project-onboard) ─┘
```

S7.1 must complete first — both skills depend on CLI-generated governance templates.
S7.2 and S7.3 are independent and can be worked in parallel.

**External:** All CLI commands exist (`raise init`, `raise discover scan`, `raise discover analyze`, `raise memory build`).

## Architecture Decisions

No new ADRs needed. Existing decisions apply:
- ADR-012: Skills + Toolkit architecture (skills orchestrate, CLI provides data)
- ADR-024: Deterministic session protocol (CLI bundles, skills interpret)
- ADR-021: Brownfield-first onboarding (convention detection, discovery pipeline)

## Done Criteria

### Per Story
- [ ] Code/skill implemented with correct structure
- [ ] Tests passing (CLI: >90% coverage; Skills: manual validation)
- [ ] Quality checks pass (ruff, pyright, bandit for CLI code)
- [ ] Skill included in DISTRIBUTABLE_SKILLS

### Epic Complete
- [ ] All 3 stories complete
- [ ] Fresh greenfield project: `/project-create` → graph with 30+ governance nodes
- [ ] Fresh brownfield project: `/project-onboard` → graph with governance + architecture nodes
- [ ] `raise init` output recommends correct skill
- [ ] Epic retrospective completed (`/epic-close`)
- [ ] Merged to v2

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Governance doc format drift from parsers | Medium | High | S7.1 generates templates deterministically; integration test verifies `raise memory build` parses them |
| Greenfield guardrails too generic | Low | Medium | Start with Python defaults; expand per-language post-F&F |
| Discovery pipeline too slow for onboarding | Low | Low | Existing CLI is fast; skill can show progress |

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-08

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S7.1: Governance scaffolding CLI | S | None | M1 | Foundation — both skills depend on parser-compatible templates. Risk-first: if templates don't parse, nothing works. |
| 2 | S7.2: `/project-create` skill | M | S7.1 | M2 | Greenfield is simpler (no discovery), validates governance flow end-to-end. Quick win, patterns inform S7.3. |
| 3 | S7.3: `/project-onboard` skill | M | S7.1 | M3 | Brownfield adds discovery complexity. Reuses governance patterns from S7.2, adds codebase analysis layer. |

### Milestones

| Milestone | Stories | Success Criteria | Demo |
|-----------|---------|------------------|------|
| **M1: Governance Templates** | S7.1 | `raise init` scaffolds `governance/` with correct frontmatter; `raise memory build` produces governance nodes from templates | Run `raise init` on empty dir → `governance/` exists → `raise memory build` → nodes in graph |
| **M2: Greenfield Ready** | +S7.2 | `/project-create` on empty project → governance docs filled from conversation → graph with 30+ nodes → `/session-start` works | Full greenfield walkthrough: name → project description → governance generated → graph built → session starts |
| **M3: Brownfield Ready (Epic Complete)** | +S7.3 | `/project-onboard` on existing codebase → discovery + conventions + governance → graph with architecture nodes → `/session-start` works | Full brownfield walkthrough on a real Python project |

### Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S7.1 (CLI) ──► S7.2 (greenfield) ──► S7.3 (brownfield)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Sequential — single developer + AI, and S7.2 patterns directly inform S7.3.

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S7.1: Governance scaffolding CLI | S | ✅ Done | 30 min | 1.5x velocity, PAT-202 |
| S7.2: `/project-create` skill | M | ✅ Done | 50 min | 1.5x velocity, PAT-204 |
| S7.3: `/project-onboard` skill | M | ✅ Done | 45 min | 1.33x velocity, PAT-205, guardrails format fix |

**Milestones:**
- [x] M1: Governance Templates
- [x] M2: Greenfield Ready
- [x] M3: Brownfield Ready (Epic Complete)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| S7.1 templates don't match parser expectations | Medium | High | Integration test: scaffold → build → verify nodes. Do this BEFORE moving to S7.2. |
| S7.2 governance content too thin for useful graph | Low | Medium | Define minimum viable content per doc type. 30+ nodes as gate. |
| S7.3 discovery pipeline output doesn't map cleanly to architecture docs | Low | Medium | Discovery CLI already tested. Mapping is inference work in the skill. |

---

*Created: 2026-02-08*
*Plan added: 2026-02-08*
*Next: `/story-start` for S7.2*
