# Evidence Catalog: OpenClaw Architecture

> Sources collected for OpenClaw/Moltbot architecture research.

---

## Primary Sources (Official Documentation)

### Source: OpenClaw Memory Documentation
- **URL:** https://docs.openclaw.ai/concepts/memory
- **Type:** Primary
- **Evidence Level:** Very High
- **Key Finding:** Two-layer memory (daily logs + MEMORY.md), pre-compaction flush with soft threshold, hybrid vector+BM25 search
- **Relevance:** Directly applicable to Rai session memory design

### Source: OpenClaw Agent Workspace Documentation
- **URL:** https://docs.openclaw.ai/concepts/agent-workspace
- **Type:** Primary
- **Evidence Level:** Very High
- **Key Finding:** Standardized file conventions (AGENTS.md, SOUL.md, USER.md, IDENTITY.md), truncation limits, today+yesterday memory loading
- **Relevance:** Template for Rai workspace structure

### Source: OpenClaw Session Compaction Documentation
- **URL:** https://docs.openclaw.ai/reference/session-management-compaction
- **Type:** Primary
- **Evidence Level:** Very High
- **Key Finding:** Auto-compaction triggers, reserveTokens/keepRecentTokens config, NO_REPLY flush mechanism
- **Relevance:** Critical for V3 long-running sessions

### Source: Lobster Documentation
- **URL:** https://docs.openclaw.ai/tools/lobster
- **Type:** Primary
- **Evidence Level:** Very High
- **Key Finding:** Typed pipelines, approval gates, resume tokens, JSON schema validation for LLM outputs
- **Relevance:** Pattern for RaiSE deterministic workflows

### Source: OpenClaw GitHub Repository
- **URL:** https://github.com/openclaw/openclaw
- **Type:** Primary
- **Evidence Level:** Very High
- **Key Finding:** Gateway WebSocket architecture, multi-channel support, Pi agent runtime, sandbox execution
- **Relevance:** Reference architecture for multi-interface support

---

## Secondary Sources (Expert Analysis)

### Source: Pi Agent Runtime (Armin Ronacher)
- **URL:** https://lucumr.pocoo.org/2026/1/31/pi/
- **Type:** Secondary (expert practitioner)
- **Evidence Level:** High
- **Key Finding:** Minimal 4-tool core (Read, Write, Edit, Bash), self-extensibility, sessions as trees not linear, extension tools vs context tools distinction
- **Relevance:** Design philosophy for minimal agent core

### Source: Multi-Agent Orchestration Issue #4561
- **URL:** https://github.com/openclaw/openclaw/issues/4561
- **Type:** Secondary (community best practices)
- **Evidence Level:** High
- **Key Finding:** Context overflow patterns, token growth drivers (~2500 tokens for browser tool alone), knowledge artifacts (DECISIONS.md, RUNBOOK.md), agent topology recommendations
- **Relevance:** Scaling patterns for multi-agent V3

### Source: DEV Community OpenClaw Guide
- **URL:** https://dev.to/mechcloud_academy/unleashing-openclaw-the-ultimate-guide-to-local-ai-agents-for-developers-in-2026-3k0h
- **Type:** Secondary
- **Evidence Level:** High
- **Key Finding:** Gateway/Brain/Sandbox/Skills four-layer architecture, Docker containerization for execution, persistent memory across sessions
- **Relevance:** Architecture overview validation

### Source: Awesome OpenClaw Skills Registry
- **URL:** https://github.com/VoltAgent/awesome-openclaw-skills
- **Type:** Secondary
- **Evidence Level:** High
- **Key Finding:** 700+ skills across 27 categories, memory as skills (git-notes-memory, triple-memory), API wrapper/CLI orchestrator/service bridge patterns
- **Relevance:** Skills ecosystem architecture patterns

---

## Tertiary Sources (News & Analysis)

### Source: DoControl Security Analysis
- **URL:** https://www.docontrol.io/blog/what-is-moltbot
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Key Finding:** No built-in guardrails by design, prompt injection risks, shadow infrastructure concerns for enterprises
- **Relevance:** Contrast with RaiSE governance approach

### Source: DEV Community Ultimate Guide
- **URL:** https://dev.to/czmilo/moltbot-the-ultimate-personal-ai-assistant-guide-for-2026-d4e
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Key Finding:** "Personal operating system for AI" framing, multi-channel consolidation, proactive autonomy
- **Relevance:** Market positioning context

### Source: Fortune Moltbook Article
- **URL:** https://fortune.com/2026/01/31/ai-agent-moltbot-clawdbot-openclaw-data-privacy-security-nightmare-moltbook-social-network/
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Key Finding:** Moltbook AI-only social network (36k+ agents), ecosystem emergence velocity
- **Relevance:** Community dynamics understanding

### Source: Scientific American Overview
- **URL:** https://www.scientificamerican.com/article/moltbot-is-an-open-source-ai-agent-that-runs-your-computer/
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Key Finding:** Mainstream adoption signals, general-purpose positioning
- **Relevance:** Market context

### Source: NXCode OpenClaw Complete Guide
- **URL:** https://www.nxcode.io/resources/news/openclaw-complete-guide-2026
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Key Finding:** 100k+ stars trajectory, rebranding history, adoption velocity
- **Relevance:** Community growth patterns

---

## Source Summary

| Level | Count | Notes |
|-------|-------|-------|
| Very High | 5 | Official documentation |
| High | 4 | Expert practitioners, GitHub issues |
| Medium | 5 | News, guides, analysis |
| **Total** | **14** | Exceeds 10+ threshold |

**Triangulation Status:** Major claims verified across 3+ sources.
