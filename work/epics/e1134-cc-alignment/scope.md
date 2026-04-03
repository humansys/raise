# Epic E1134: Skill CC-Alignment — Scope

> **Status:** IN PROGRESS
> **Jira:** [RAISE-1182](https://humansys.atlassian.net/browse/RAISE-1182)
> **Release:** v2.4.0
> **Created:** 2026-04-02

## Objective

Align all RaiSE skill metadata with Claude Code's proven patterns for automatic selection, tool restriction, and invocation control. Close a validated gap: 0% coverage on `allowed-tools`, `disable-model-invocation`, and description optimization across 35+ skills.

**Value:** Skills become first-class CC citizens — precise auto-selection, fewer permission prompts, controlled blast radius per skill.

## Research

Pre-design research completed (see `research/` subdirectory):
- **Gemba:** Audited 35 skills — 0/35 have allowed-tools, 0/35 have disable-model-invocation, all descriptions exceed 250-char truncation
- **SOTA:** 10 sources (4 primary, 4 secondary, 2 tertiary) — CC official docs, Anthropic's own code, community guides
- **Key finding:** Anthropic uses allowed-tools on 100% of their own commands with Bash glob patterns at subcommand granularity

## Stories

| ID | Story | Size | Description | Deps |
|----|-------|:----:|-------------|------|
| S1134.1 | Description optimization | M | Rewrite 35 descriptions: verb-first, <100 chars, trigger phrases | — |
| S1134.2 | allowed-tools declaration | M | Add allowed-tools with Bash globs to 35 skills (5-tier classification) | — |
| S1134.3 | Invocation control | S | Add disable-model-invocation: true to 9 side-effect/orchestration skills | — |
| S1134.4 | Validation & report | S | Before/after metrics report across all dimensions | S1134.1, S1134.2, S1134.3 |

## Done Criteria

- [ ] All skills have description <250 chars (target <100)
- [ ] All skills declare allowed-tools
- [ ] Side-effect skills have disable-model-invocation: true
- [ ] Before/after report shows improvement across all metrics
- [ ] No skill content/instructions changed — metadata only
- [ ] Retrospective completed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| allowed-tools too restrictive breaks skill execution | Medium | Medium | Test each skill after adding restrictions |
| Description too short loses trigger accuracy | Low | Medium | Include key trigger phrases; test auto-selection |
| 35+ skills exceed CC description budget even after optimization | Low | High | Use disable-model-invocation to remove ~10 skills from budget |

## Implementation Plan

### Sequencing Strategy: Quick Wins

No architectural uncertainty. No hard external blockers. Sequence for momentum and de-risking: start with the smallest story that validates CC frontmatter parsing, then tackle the two larger stories with confidence.

### Story Sequence

| # | Story | Size | Strategy | Rationale |
|---|-------|:----:|----------|-----------|
| 1 | S1134.3 (Invocation control) | S | Quick win + de-risk | 9 skills, 1 field each. Validates CC parses new frontmatter correctly. Frees ~900 chars of description budget. |
| 2 | S1134.1 (Descriptions) | M | Leverage | Budget freed by S1134.3 gives more room. 35 rewrites requiring judgment. |
| 3 | S1134.2 (allowed-tools) | M | Core value | Most laborious: read each SKILL.md body, classify tier, declare tools. Parallel-safe with S1134.1 if desired. |
| 4 | S1134.4 (Validation) | S | Gate | Depends on S1134.1-3. Script + before/after report. |

### Parallelism

S1134.1 and S1134.2 modify different frontmatter fields in the same files — merge-safe if run in parallel. With a single developer, sequential is simpler.

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|-----------------|
| **M1: Quick Win** | S1134.3 | 9 side-effect skills have `disable-model-invocation: true`. CC no longer auto-invokes them. |
| **M2: Core Complete** | S1134.1 + S1134.2 | 35 skills have descriptions <100 chars AND allowed-tools declared. |
| **M3: Epic Complete** | S1134.4 | Before/after report shows 100% coverage. Retrospective done. |

### Progress Tracking

| Story | Status | Commit | Notes |
|-------|--------|--------|-------|
| S1134.3 | **Done** | `c5aa8af6` | 13 skills (9 original + 4 from QR). PAT-E-701. |
| S1134.1 | **Done** | `9aa6d748` | 35 descriptions rewritten. Budget: 10,500→1,744 chars (-78%). |
| S1134.2 | Pending | — | — |
| S1134.4 | Pending | — | — |
