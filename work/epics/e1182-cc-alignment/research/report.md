# E1134 Pre-Design Research: CC Skill Metadata Best Practices

**Date:** 2026-04-02
**Epic:** E1134 (Skill CC-Alignment)
**Jira:** RAISE-1182
**Confidence:** HIGH (4 primary sources, 4 secondary, 2 tertiary; code-validated)

---

## 1. Research Questions

1. What metadata fields does Claude Code use for skill selection and tool restriction?
2. How should `description` be written for optimal automatic invocation?
3. How should `allowed-tools` be declared for effective blast radius control?
4. How does Anthropic apply these practices in their own codebase?
5. What do power users and the community recommend?

## 2. Executive Summary

Claude Code skills support rich YAML frontmatter for controlling invocation, tool access, and execution context. Two fields are critical for E1134:

- **`description`**: The primary mechanism for automatic skill selection. Truncated at 250 chars in listings. Total budget across all skills = 1% of context window (~8K chars). Must be verb-first, trigger-phrase rich, and concise.
- **`allowed-tools`**: Restricts which tools a skill can use without permission prompts. Supports glob patterns for granular Bash control (`Bash(git add:*)`). Anthropic uses it on 100% of their own commands.

A third field, `disable-model-invocation`, prevents Claude from automatically invoking skills with side effects. Essential for lifecycle commands like close, merge, publish.

Our codebase has **zero coverage** on `allowed-tools` and `disable-model-invocation`, and all 35 descriptions exceed the 250-char truncation threshold.

## 3. Findings

### 3.1 Complete Frontmatter Field Reference (from official docs, S1)

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name, lowercase+hyphens, max 64 chars. Defaults to directory name. |
| `description` | Recommended | What skill does and when to use it. Truncated at 250 chars. |
| `argument-hint` | No | Hint for autocomplete (e.g., `[issue-number]`). |
| `disable-model-invocation` | No | `true` = only user can invoke. Removes description from context. |
| `user-invocable` | No | `false` = hide from `/` menu, only Claude invokes. |
| `allowed-tools` | No | Tools Claude can use without asking permission. |
| `model` | No | Model override (sonnet, opus, haiku). |
| `effort` | No | Effort level override (low, medium, high, max). |
| `context` | No | `fork` = run in subagent isolation. |
| `agent` | No | Subagent type when `context: fork`. |
| `hooks` | No | Skill-scoped lifecycle hooks. |
| `paths` | No | Glob patterns limiting when skill activates. |
| `shell` | No | Shell for `!command` blocks (bash or powershell). |

### 3.2 `description` Field

#### How CC uses it

CC loads all skill descriptions into context at session start. The description is the **sole signal** for automatic invocation — there is no separate `when_to_use` field (confirmed deprecated by CC's plugin-dev reviewer, S9).

**Constraints:**
- Truncated at 250 characters in the skill listing (S1).
- Total budget = 1% of context window, ~8,000 char fallback (S1).
- Configurable via `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (S1).

**With 35 skills at 250 chars = 8,750 chars, we exceed the default budget.** CC is silently truncating or dropping some descriptions.

#### How to write effective descriptions

**Official guidance (S1, S2, S4):**
- Front-load the key use case — content after 250 chars is lost.
- Start with a verb: "Deploy", "Review", "Generate", "Fix".
- ~60 chars ideal for clean `/help` display (S4).
- If omitted, CC uses first paragraph of markdown content.

**Community consensus (S5, S6, S7, S8):**
- Include trigger phrases matching natural user language.
- Be task-specific, not feature-specific.
- Single responsibility per description.
- Shorter = less parsing overhead per message.

**Anthropic's own commands (S3) — measured:**

| Command | Description | Chars |
|---------|-------------|-------|
| `commit` | "Create a git commit" | 20 |
| `code-review` | "Code review a pull request" | 28 |
| `dedupe` | "Find duplicate GitHub issues" | 29 |
| `triage-issue` | "Triage GitHub issues by analyzing and applying labels" | 55 |
| `hookify` | "Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions" | 93 |

**Average: 45 chars. Maximum: 93 chars. All verb-first.**

#### Anti-patterns (S4)

- "This command reviews PRs" — unnecessary prefix.
- "Review" — too vague.
- Multi-line YAML `>` blocks producing 300+ chars — silently truncated. **This is our current state.**

### 3.3 `allowed-tools` Field

#### Supported formats (S1, S4)

```yaml
# String
allowed-tools: Read, Grep, Glob

# Array
allowed-tools:
  - Read
  - Bash(git:*)

# JSON array
allowed-tools: ["Read", "Grep"]
```

#### Bash glob patterns (S2, S3, S4)

```yaml
Bash(git:*)              # Any git subcommand
Bash(git add:*)          # Only git add
Bash(npm test:*)         # Only npm test
Bash(./scripts/gh.sh:*)  # Specific script only
```

#### Anthropic's own code demonstrates extreme granularity (S3)

```yaml
# commit-push-pr: only needed git/gh subcommands
allowed-tools: >
  Bash(git checkout --branch:*), Bash(git add:*),
  Bash(git status:*), Bash(git push:*),
  Bash(git commit:*), Bash(gh pr create:*)

# cancel-ralph: restricted to ONE specific file
allowed-tools:
  - Bash(test -f .claude/ralph-loop.local.md:*)
  - Bash(rm .claude/ralph-loop.local.md)
  - Read(.claude/ralph-loop.local.md)
```

#### MCP tool support (S3)

```yaml
allowed-tools:
  - mcp__github_inline_comment__create_inline_comment
```

Relevant for our skills using Jira/Confluence MCP servers.

#### Best practices (converged S1-S8)

1. **Least privilege** — only tools the skill actually needs (S4, S5).
2. **Always filter Bash** — never bare `Bash`, always `Bash(command:*)` (S3, S4).
3. **Read-only for analysis** — `Read, Grep, Glob` (S1, S5).
4. **Document why** tools are needed (S4).

### 3.4 `disable-model-invocation` Field

When `true`: Claude cannot auto-invoke. Description removed from context entirely (S1), freeing budget.

**When to use (S1, S4):** Destructive operations, manual-only workflows, interactive workflows.

**RaiSE skills that should use it:**

| Skill | Side effect | 
|-------|-------------|
| `rai-epic-close` | Pushes to origin, creates MR, updates tracker |
| `rai-story-close` | Merges branch, updates tracker |
| `rai-publish` | Publishes to PyPI |
| `rai-epic-start` | Creates tracker entries, emits signals |
| `rai-story-start` | Creates branches, commits |
| `rai-session-close` | Writes session state, emits signals |
| `rai-framework-sync` | Writes to multiple locations |
| `rai-epic-run` | Orchestrates full epic lifecycle |
| `rai-story-run` | Orchestrates full story lifecycle |

**Bonus:** Removing ~9 skills from context frees ~2,250 chars of budget for remaining skills.

### 3.5 Codebase Validation (Gemba)

Audited all 35 RaiSE skills:

| Metric | Value |
|--------|-------|
| Skills with `allowed-tools` | **0/35 (0%)** |
| Skills with `disable-model-invocation` | **0/35 (0%)** |
| Skills with `user-invocable` set | **0/35 (0%)** |
| Descriptions under 250 chars | **0/35 (0%)** |
| Descriptions under 60 chars | **0/35 (0%)** |
| Avg description length | ~250-400 chars |
| Total skills competing for budget | 35 |

### 3.6 Comparative: CC vs RaiSE

| Dimension | CC (Anthropic) | RaiSE |
|-----------|---------------|-------|
| `allowed-tools` | 100% coverage, Bash granular | **0%** |
| `description` | 20-93 chars, verb-first | 150-400+ chars, truncated |
| `disable-model-invocation` | On side-effect commands | **0%** |
| Bash patterns | Subcommand-level (`Bash(git add:*)`) | N/A |
| Principle | Least privilege, explicit | Implicit total access |

## 4. Recommendations

| # | Recommendation | Confidence | Sources |
|---|---------------|------------|---------|
| R1 | Rewrite all descriptions: verb-first, <100 chars, trigger phrases | HIGH | S1, S3, S4, S5, S6 |
| R2 | Add `allowed-tools` to all 35 skills with Bash globs | HIGH | S1, S3, S4, S5, S8 |
| R3 | Add `disable-model-invocation: true` to ~9 side-effect skills | HIGH | S1, S3, S4 |
| R4 | Validate file-type globs empirically before adopting | MEDIUM | S5 only (not triangulated) |

## 5. Contrary Evidence & Limitations

- **`when_to_use` deprecation**: Only documented in CC's plugin-dev reviewer (S9), not official docs. The field simply doesn't exist in CC — treating as "never existed" rather than "deprecated."
- **File-type globs** (`Read(**/*.ts)`) in `allowed-tools`: Community-documented (S5) but absent from Anthropic's own code. May have edge cases.
- **Budget overflow behavior**: Official docs say 250-char truncation per entry, but exact behavior when total budget exceeded (truncation vs. dropping) is undocumented.
- **35 skills may be too many** for optimal activation (S7 recommends 20-30). Using `disable-model-invocation` on ~9 effectively reduces visible count to ~26.

## 6. Scope Impact

Research **confirms** the original E1134 scope with one addition:
- S1134.1 (descriptions): Confirmed critical — we exceed budget
- S1134.2 (allowed-tools): Confirmed critical — 0% coverage vs 100% in CC
- **S1134.3 (invocation control): Added** — `disable-model-invocation` for side-effect skills
- S1134.4 (validation): Confirmed — before/after metrics needed

No scope reduction recommended. No new architectural decisions needed (applying established CC patterns, not choosing between alternatives).
