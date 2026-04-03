# Epic E1134: Skill CC-Alignment — Design

> **Status:** IN PROGRESS
> **Research:** [report](research/report.md) | [evidence](research/sources/evidence-catalog.md)

## Gemba: Current State (35 skills)

| Metric | Current | Target |
|--------|---------|--------|
| `allowed-tools` coverage | 0% (0/35) | 100% |
| `disable-model-invocation` coverage | 0% (0/35) | ~26% (9/35 side-effect skills) |
| Description avg length | ~300 chars | <100 chars |
| Descriptions within 250-char budget | 0% | 100% |
| Total description budget usage | ~10,500 chars (exceeds 8K limit) | ~2,600 chars (26 visible × ~100) |

## Design Decisions

### D1: Description Pattern

Follow Anthropic's own convention (S3, S4 from research):

```
Verb + object + context. <100 chars. Front-load trigger.
```

**Template:**
```yaml
description: >-
  {Verb} {what} {when/context}.
  Use when {trigger phrase}.
```

**Examples (before → after):**

| Skill | Before (truncated) | After |
|-------|-------|-------|
| `rai-session-start` | "Begin a session by loading context bundle, interpreting it, and proposing work. CLI does all data plumbing; skill does inference interpretation." (147 chars) | "Load context and propose session focus. Use at the start of every working session." (83 chars) |
| `rai-debug` | "Systematic root cause analysis using lean methods (5 Whys, Ishikawa, Gemba). Use when encountering unexpected behavior, errors, or defects to find and fix the true root cause rather than symptoms." (197 chars) | "Find root cause of bugs using 5 Whys, Ishikawa, Gemba. Use when encountering unexpected errors or defects." (108 chars) |
| `rai-publish` | "Guide the human through a structured release workflow with quality gates, version bumping, changelog management, and PyPI publishing via GitHub Actions." (153 chars) | "Publish a release with quality gates, version bump, and changelog. Use for PyPI releases." (90 chars) |

### D2: allowed-tools Classification

Classify skills into tiers based on their tool needs:

| Tier | Tools | Skills |
|------|-------|--------|
| **Read-only** | `Read, Grep, Glob` | session-start, mcp-status, doctor, code-audit, architecture-review, quality-review |
| **Read + CLI** | `Read, Grep, Glob, Bash(rai:*)` | story-review, session-close, epic-plan, story-plan |
| **Read + CLI + Git** | `Read, Grep, Glob, Bash(rai:*), Bash(git:*)` | story-start, epic-start, story-close, epic-close |
| **Full dev** | `Read, Edit, Write, Grep, Glob, Bash` | story-implement, bugfix, debug |
| **Research** | `Read, Grep, Glob, Bash(ddgr:*), WebFetch, WebSearch` | research, epic-research |
| **Orchestration** | `Read, Grep, Glob, Bash, Agent, Skill` | epic-run, story-run |

**Bash pattern convention for our skills:**
- `Bash(rai:*)` — RaiSE CLI commands
- `Bash(git:*)` — Git operations
- `Bash(uv:*)` — Python tooling
- `Bash(ddgr:*)` — Search
- Never bare `Bash` except for full-dev skills

**MCP tools** (where applicable):
- Skills using Jira: add `mcp__atlassian__jira_*` or specific tools
- Skills using Confluence: add `mcp__atlassian__confluence_*` or specific tools

### D3: Invocation Control Classification

| Category | `disable-model-invocation` | Skills |
|----------|:-:|--------|
| **Side effects (writes, merges, pushes)** | `true` | epic-start, epic-close, story-start, story-close, publish, framework-sync, session-close |
| **Orchestration (chains other skills)** | `true` | epic-run, story-run |
| **Auto-invocable (Claude should use when relevant)** | `false` (default) | All others (~26 skills) |

**Budget impact:** Removing 9 skills from context saves ~900 chars (9 × ~100 char descriptions that no longer load).

## Target Components

All changes are in `.claude/skills/*/SKILL.md` frontmatter. No Python code, no tests, no CLI changes.

```
.claude/skills/
├── rai-session-start/SKILL.md  ← frontmatter only
├── rai-story-implement/SKILL.md  ← frontmatter only
├── ... (35 total)
```

## Story Detail

### S1134.1: Description Optimization (M)

**Input:** Current 35 skill descriptions (all >150 chars)
**Output:** 35 rewritten descriptions, each <100 chars, verb-first, with trigger phrases
**Approach:** Read each SKILL.md, understand purpose, rewrite description following D1 pattern
**Verification:** `grep -c 'description:' | wc` + char count per skill

### S1134.2: allowed-tools Declaration (M)

**Input:** 35 skills with no allowed-tools
**Output:** 35 skills with allowed-tools following D2 tier classification
**Approach:** Read each SKILL.md body, identify tools referenced in steps, classify into tier, declare
**Verification:** `grep -c 'allowed-tools:' | wc` across all skills

### S1134.3: Invocation Control (S)

**Input:** 35 skills with no invocation control
**Output:** ~9 skills with `disable-model-invocation: true` per D3 classification
**Approach:** Apply classification, add frontmatter field
**Verification:** Count skills with `disable-model-invocation: true`

### S1134.4: Validation & Report (S)

**Input:** All changes from S1134.1-3
**Output:** Before/after metrics report
**Approach:** Script that audits all skill frontmatter and produces metrics table
**Verification:** Report shows 100% coverage on all dimensions

## Dependency Graph

```
S1134.1 (descriptions) ──┐
S1134.2 (allowed-tools) ──┼──→ S1134.4 (validation)
S1134.3 (invocation) ────┘
```

S1134.1, S1134.2, S1134.3 are independent — can run in parallel.
S1134.4 depends on all three completing first.
