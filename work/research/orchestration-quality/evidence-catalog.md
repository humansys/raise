# Evidence Catalog: Orchestration Quality Preservation

## Research Question
How do teams run long-running, multi-phase AI agent workflows with Claude Code without quality degradation from context saturation?

## Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 1 | [Claude Code Docs: Subagents](https://code.claude.com/docs/en/sub-agents) | Primary (official docs) | Very High | Subagents run in own context window. Skills can preload into subagents via `skills` field. Custom agents definable in `.claude/agents/`. |
| 2 | [Claude Code Docs: Agent Teams](https://code.claude.com/docs/en/agent-teams) | Primary (official docs) | Very High | Agent teams = independent Claude Code sessions. Each teammate has own context. Shared task list for coordination. Experimental feature. |
| 3 | [Claude Code Docs: Skills](https://code.claude.com/docs/en/skills) | Primary (official docs) | Very High | `context: fork` runs skill in isolated subagent context. `agent` field selects agent type. Skill content becomes subagent prompt. |
| 4 | [Shrivu Shankar: How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature) | Secondary (practitioner) | High | "Document & Clear" pattern: write plan to markdown, reset session, read file and continue. Avoids auto-compaction. Prefers main agent delegation over custom subagents. |
| 5 | [ClaudeFast: Sub-Agent Best Practices](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) | Secondary (community) | Medium | Sequential chaining: agent A completes, results return to main, main passes to agent B. "Constitutional invocation" = comprehensive context per dispatch. |
| 6 | [VentureBeat: Claude Code Tasks](https://venturebeat.com/orchestration/claude-codes-tasks-update-lets-agents-work-longer-and-coordinate-across-sessions) | Secondary (journalism) | Medium | Tasks support DAGs with dependency blocking. UNIX-philosophy state management to filesystem. |
| 7 | [GitHub Issue #17283](https://github.com/anthropics/claude-code/issues/17283) | Primary (Anthropic) | High | Feature request for Skill tool to honor `context: fork` and `agent:` fields. Confirms these are supported features. |
| 8 | [SFEIR Institute: Context Management](https://institute.sfeir.com/en/claude-code/claude-code-context-management/examples/) | Secondary (training) | Medium | Exceeding 60% of context window degrades accuracy by 15-25%. Recommendation: targeted manual compaction + subagents for isolation. |
| 9 | [GitHub Issue #28962](https://github.com/anthropics/claude-code/issues/28962) | Primary (community) | Medium | Context window usage indicator request. Sessions "silently degrade" as context fills. |
| 10 | [Eesel: Multi-agent systems guide](https://www.eesel.ai/blog/claude-code-multiple-agent-systems-complete-2026-guide) | Tertiary (aggregator) | Medium | Industry pattern: single agent → orchestrated specialists. Gas Town/Multiclaude use "mayor" agent pattern. |

## Internal Evidence

| # | Source | Finding |
|---|--------|---------|
| I1 | Conversation log `fb0aeca7` | QR in orchestrator: 2,196 chars, 1 tool call. QR standalone: 10,064 chars, 28 tool calls. **4.6x quality gap.** |
| I2 | Conversation log `fb0aeca7` | All 8 SKILL.md files were loaded (Read tool calls confirmed). Compression is behavioral, not loading failure. |
| I3 | `rai-story-run` SKILL.md | Lines 107-113 explicitly say "no compression, no skipping". Lines 179-182 checklist items. Instructions present but ineffective. |
