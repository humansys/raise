# Evidence Catalog: Session Memory Continuity in AI Coding Agents

> Research ID: RES-SESSION-MEM-001
> Date: 2026-02-14
> Decision context: Session narrative design for RaiSE hotfix

---

## Sources

### S1: Cline — new_task Tool
- **URL:** https://docs.cline.bot/exploring-clines-tools/new-task-tool
- **Type:** Primary (official docs)
- **Evidence Level:** High
- **Key Finding:** Structured context handoff via XML `<new_task><context>` block with sections: Completed Work, Current State, Next Steps, Reference Information. Triggered at configurable context % threshold.
- **Relevance:** Direct parallel to our session close/start flow. Their "context block" = our "narrative".

### S2: Cline — Memory Bank
- **URL:** https://cline.bot/blog/memory-bank-how-to-make-cline-an-ai-agent-that-never-forgets
- **Type:** Primary (official blog)
- **Evidence Level:** High
- **Key Finding:** 6 markdown files (projectbrief.md, productContext.md, systemPatterns.md, techContext.md, activeContext.md, progress.md). Community-created, loaded via custom instructions. Read-verify-execute-update cycle.
- **Relevance:** Long-term project memory (like our governance docs), not session handoff. activeContext.md is closest to our narrative — "current development state, updated most frequently."

### S3: Claude Code — Session Memory
- **URL:** https://claudefa.st/blog/guide/mechanics/session-memory
- **Type:** Secondary (community documentation)
- **Evidence Level:** High
- **Key Finding:** Background extraction every ~5k tokens/3 tool calls. Stored as structured markdown in `~/.claude/projects/<hash>/<session>/session-memory/summary.md`. Compaction loads pre-written summary. Past sessions injected as "might not be related" background.
- **Relevance:** This is the platform we run on. Our session system needs to complement, not duplicate, Claude Code's auto-memory.

### S4: OpenClaw — Mem0 Integration
- **URL:** https://mem0.ai/blog/mem0-memory-for-openclaw
- **Type:** Primary (vendor integration)
- **Evidence Level:** Medium
- **Key Finding:** Two memory tiers: long-term (user-scoped, cross-session: name, stack, decisions) and short-term (session-scoped: current task). Auto-Recall pulls relevant memories at session start. Plugin-based (@mem0/openclaw-mem0).
- **Relevance:** Two-tier model validates our approach (patterns = long-term, narrative = short-term). But they use vector search for recall; we use deterministic loading.

### S5: Cursor — Rules + Notepads + Memories
- **URL:** https://webpeak.org/blog/does-cursor-ai-track-memory-across-conversations/
- **Type:** Secondary (community analysis)
- **Evidence Level:** Medium
- **Key Finding:** Does NOT persist memory across conversations by default. Three workarounds: .cursorrules (project-level instructions), Notepads (reusable context snippets), Memories feature (remembers facts from conversations). MCP-based memory systems emerging.
- **Relevance:** Cursor's lack of built-in session continuity validates that this is a real gap in the market. Their Memories feature is closest to our patterns.

### S6: Aider — Chat History
- **URL:** https://aider.chat/docs/faq.html
- **Type:** Primary (official docs)
- **Evidence Level:** Medium
- **Key Finding:** `.aider.chat.history.md` persists full chat history as markdown. Repo map provides code context. No structured session handoff — history is append-only, full reload. Context managed via /read, /context commands.
- **Relevance:** Brute-force approach (keep everything). Works for single-session-per-task. Doesn't scale for multi-session workflows like ours.

### S7: OpenAI Agents SDK — Sessions
- **URL:** https://openai.github.io/openai-agents-python/sessions/
- **Type:** Primary (official docs)
- **Evidence Level:** Very High
- **Key Finding:** Built-in session memory with SQLite/SQLAlchemy backends. Two strategies: context trimming (drop older turns) and context summarization (compress to structured summaries). Session = memory object with get/add/pop/clear protocol.
- **Relevance:** Framework-level approach. Their summarization strategy = our narrative concept. Their trimming = our "only load last session."

### S8: Cline — Context Engineering
- **URL:** https://cline.bot/blog/how-to-think-about-context-engineering-in-cline
- **Type:** Primary (official blog)
- **Evidence Level:** High
- **Key Finding:** .clinerules automate handoff triggers. Context block should include: completed work, current state, next steps, reference info, actionable start. Emphasizes "immediately resumable" as the goal.
- **Relevance:** "Immediately resumable" is exactly our design goal. Their structure maps well to our narrative fields.

### S9: Claude Code — Auto Memory
- **URL:** https://yuanchang.org/en/posts/claude-code-auto-memory-and-hooks/
- **Type:** Secondary (community analysis)
- **Evidence Level:** Medium
- **Key Finding:** Auto memory writes to `~/.claude/projects/<hash>/memory/`. PreCompact hooks run before compaction. MEMORY.md loaded into system prompt (200 line limit). Memory is Claude's notes for itself, not user instructions.
- **Relevance:** We already use this (our MEMORY.md). Our session narrative should complement auto-memory, not compete with it.

### S10: Context Recovery Hook
- **URL:** https://medium.com/@CodeCoup/context-recovery-hook-for-claude-code-never-lose-work-to-compaction-7ee56261ee8f
- **Type:** Secondary (community hack)
- **Evidence Level:** Low
- **Key Finding:** Community workaround using hooks to save context before compaction. Indicates Claude Code's built-in session memory isn't sufficient for complex workflows.
- **Relevance:** Validates our problem — even with Claude Code's auto-memory, complex workflows lose context.
