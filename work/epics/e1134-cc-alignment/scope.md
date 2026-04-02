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
