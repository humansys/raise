---
epic_id: "E1134"
title: "Skill CC-Alignment"
status: "draft"
created: "2026-04-02"
---

# Epic Brief: Skill CC-Alignment

## Hypothesis
For RaiSE developers who use Claude Code as their primary AI coding assistant,
aligning skill metadata with CC's proven patterns (description, allowed-tools, disable-model-invocation)
is a product quality improvement
that enables precise automatic skill selection, reduced permission prompts, and controlled blast radius.
Unlike the current state (zero coverage on all three fields), our solution closes a measurable gap validated against Anthropic's own codebase.

## Success Metrics
- **Leading:** All 35+ skills pass a metadata completeness check (description <250 chars, allowed-tools declared, invocation control set)
- **Lagging:** Reduced user permission prompts during skill execution; accurate automatic skill selection by CC

## Appetite
S — 4 stories, estimated 6-10h total

## Scope Boundaries
### In (MUST)
- Optimize all skill descriptions for CC's 250-char truncation and verb-first pattern
- Add allowed-tools with Bash glob patterns to all skills
- Add disable-model-invocation to skills with side effects
- Before/after validation report

### In (SHOULD)
- Include MCP tool namespaces in allowed-tools where applicable
- Consider effort/model overrides for simple skills

### No-Gos
- Do not change skill content/instructions — only metadata/frontmatter
- Do not refactor skill directory structure
- Do not implement runtime enforcement (that's E14/RAISE-1006 scope)

### Rabbit Holes
- File-type globs in allowed-tools (e.g., `Read(**/*.ts)`) — community-documented but not validated in CC's own code. Don't adopt without empirical testing.
- Optimizing for `user-invocable: false` — no current need, defer.
