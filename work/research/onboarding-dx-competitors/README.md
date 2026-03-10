# Research: Competitor Onboarding DX for AI-Assisted Development

> **ID:** RES-ONBOARD-DX-001
> **Status:** Complete
> **Date:** 2026-02-04
> **Decision:** Informs E7 `/initial-setup` skill design
> **Depth:** Standard (2-3h)

---

## Research Question

**Primary:** How do AI-assisted development frameworks guide experienced developers from install to first productive work on an existing codebase?

**Secondary:**
- What questions do they ask during setup?
- How do they handle codebase discovery/understanding?
- What's the path from install → first real work?

---

## Evidence Catalog

### Primary Sources (Official Docs)

| Source | Evidence Level | Key Finding |
|--------|----------------|-------------|
| [Aider Repository Map Docs](https://aider.chat/docs/repomap.html) | Very High | Tree-sitter + PageRank for smart codebase understanding |
| [Cursor Features](https://cursor.com/features) | Very High | Project indexing, .cursorrules, AGENTS.md for context |
| [Continue.dev Docs](https://docs.continue.dev) | Very High | config.yaml, agent/chat/edit modes, gradual config |
| [Cline Wiki](https://github.com/cline/cline/wiki) | Very High | Custom instructions, permission-based workflow |
| [Windsurf Docs](https://docs.windsurf.com/) | Very High | .windsurf/memory.md, .windsurfrules, cascade modes |
| [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) | Very High | CLAUDE.md hierarchy, /init command |
| [OpenClaw Wizard](https://docs.openclaw.ai/start/wizard) | High | Interactive wizard, keep/modify/reset pattern |
| [GitHub Copilot Agent](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/) | Very High | Good docs = good onboarding, setup like new developer |

### Secondary Sources (Guides, Reviews)

| Source | Evidence Level | Key Finding |
|--------|----------------|-------------|
| [Aider Tree-sitter Blog](https://aider.chat/2023/10/22/repomap.html) | High | Graph-based ranking for token optimization |
| [Cursor Complete Guide (Medium)](https://medium.com/@hilalkara.dev/cursor-ai-complete-guide-2025) | Medium | Rules at personal, project, team levels |
| [Creating Perfect CLAUDE.md (Dometrain)](https://dometrain.com/blog/creating-the-perfect-claudemd-for-claude-code/) | Medium | Document commands, domain terms, architecture |
| [Windsurf DataCamp Tutorial](https://www.datacamp.com/tutorial/windsurf-ai-agentic-code-editor) | Medium | memory.md for project-specific style rules |
| [Cline Practical Guide (Sider)](https://sider.ai/blog/ai-tools/how-to-use-cline-a-practical-guide-to-the-ai-coding-agent-in-vs-code) | Medium | Custom instructions for team onboarding |

---

## Key Findings

### Finding 1: Codebase Understanding is Automatic, Not Manual

**Confidence:** HIGH (5 sources)

| Tool | Approach |
|------|----------|
| **Aider** | Repo-map via tree-sitter + PageRank (automatic) |
| **Cursor** | Project indexing on open (automatic) |
| **Windsurf** | Full project scan with parallel analysis (automatic) |
| **Continue.dev** | Context from open files + workspace (automatic) |

**Pattern:** None require manual "discovery" step. They index automatically.

**RaiSE implication:** Our `/discover-*` skills are valuable but shouldn't be required for first use. Auto-discovery on setup is the standard.

### Finding 2: Configuration Files, Not Interactive Wizards (Mostly)

**Confidence:** HIGH (6 sources)

| Tool | Config Approach |
|------|-----------------|
| **Cursor** | `.cursorrules`, `AGENTS.md` (files, not wizard) |
| **Windsurf** | `.windsurf/memory.md`, `.windsurfrules` (files) |
| **Continue.dev** | `config.yaml`, `.continuerc.json` (files) |
| **Cline** | Settings UI + custom instructions (UI, not wizard) |
| **Claude Code** | `CLAUDE.md` + `/init` command (file + simple command) |
| **OpenClaw** | Interactive wizard (exception) |

**Pattern:** Most tools use **config files** that users edit, not wizards. OpenClaw is the exception with a full interactive wizard.

**RaiSE implication:** A wizard is not the industry standard. A simple `/init`-like command that generates good defaults + a config file to edit is more common.

### Finding 3: The "/init" or "First Run" Pattern

**Confidence:** HIGH (4 sources)

| Tool | First Run |
|------|-----------|
| **Claude Code** | `/init` scans project, generates CLAUDE.md |
| **Windsurf** | Opens project → auto-scans → runs linters in parallel |
| **Cursor** | First open → indexes codebase |
| **Continue.dev** | Install → default config created → customize |

**Pattern:** First interaction does auto-setup. User refines after.

**Key insight from Claude Code:** `/init` "scans the project files to identify architectural patterns and documents them." Then user reviews and corrects.

### Finding 4: Memory/Rules Hierarchy

**Confidence:** HIGH (4 sources)

| Tool | Hierarchy |
|------|-----------|
| **Cursor** | Personal → Project → Team rules |
| **Claude Code** | ~/.claude/CLAUDE.md → project/CLAUDE.md → subdirs |
| **Windsurf** | Global settings → .windsurf/memory.md |
| **Continue.dev** | ~/.continue/config.yaml → .continuerc.json |

**Pattern:** Global (user) → Project → Subdirectory cascade

**RaiSE implication:** We have project-level only. Consider global ~/.rai/ for user patterns (but YAGNI for F&F).

### Finding 5: Modes for Different Work Types

**Confidence:** MEDIUM (3 sources)

| Tool | Modes |
|------|-------|
| **Aider** | Code, Architect, Ask, Help modes |
| **Continue.dev** | Agent, Chat, Autocomplete, Edit modes |
| **Windsurf** | Write, Chat, Turbo modes |

**Pattern:** Different modes for different intentions (thinking vs doing vs asking).

**RaiSE implication:** Our skills implicitly provide this (research vs implement), but we don't have explicit "modes."

### Finding 6: What They Ask During Setup

**Confidence:** MEDIUM (3 sources)

**OpenClaw wizard asks:**
1. API keys/authentication
2. Model selection
3. Channel configuration (messaging platforms)
4. Security settings

**Aider asks:**
- Model + API key (CLI flags or prompts)
- Nothing else — starts immediately

**Cursor asks:**
- Import from VS Code? (settings, extensions)
- Theme preference
- Then opens project

**Claude Code /init:**
- Nothing — just scans and generates

**Pattern:** Most ask very little upfront. OpenClaw is an outlier because it's multi-channel.

**RaiSE implication:** Less is more. Don't ask questions that can be inferred or defaulted.

### Finding 7: Time to First Value

**Confidence:** HIGH (triangulated)

| Tool | Time to First Value |
|------|---------------------|
| **Aider** | ~2 min (install → cd → aider → working) |
| **Cursor** | ~5 min (install → open project → start asking) |
| **Cline** | ~10 min (install → configure API → start) |
| **Windsurf** | ~5 min (install → import → open → working) |
| **Claude Code** | ~5 min (install → open → /init → working) |

**Pattern:** 2-10 minutes is the standard. No tool requires extensive setup.

---

## Synthesis: What Works

### Pattern: "Scan First, Ask Later"

The most successful pattern is:
1. **Install** (one command)
2. **Auto-scan** codebase on first use
3. **Generate** sensible defaults
4. **User refines** config file as needed

NOT:
1. Install
2. Answer 10 questions
3. Configure everything
4. Then start

### Pattern: "Config as Documentation"

Instead of asking questions, tools create a config file that:
- Documents what can be configured
- Has sensible defaults
- User edits when they want to change behavior

Examples: CLAUDE.md, .cursorrules, .windsurf/memory.md

### Pattern: "Progressive Disclosure"

- Start with minimal config
- Add complexity as user needs it
- Don't front-load all options

From Continue.dev: "Don't try to configure everything at once. Start with basic model configurations and add features gradually."

---

## Contrary Evidence

### Wizard-Based Onboarding (OpenClaw)

OpenClaw uses an interactive wizard because:
- Multi-channel (WhatsApp, Telegram, Slack) requires choices
- Gateway configuration is complex
- User can't infer these settings

**When wizard makes sense:** When user must make choices that can't be inferred.

### BMAD Method (Brownfield)

BMAD recommends explicit project discovery:
- Generate AI-optimized docs
- Create Product Overview, Tech Stack docs
- Then start development

**When explicit discovery makes sense:** Large legacy codebases where auto-indexing isn't enough.

---

## Recommendation for RaiSE

### Design: Hybrid Approach

**Phase 1: Quick Start (like Claude Code /init)**
```bash
rai init    # or `rai setup`
```
- Scans project structure
- Detects languages, frameworks
- Generates CLAUDE.md with detected context
- Copies essential skills
- Done in <30 seconds

**Phase 2: Guided Refinement (like interactive session)**
```
/session-start (first time)
→ "I've scanned your project. Here's what I found:
   - Python 3.12, FastAPI, SQLAlchemy
   - 47 files, 3200 LOC
   - No governance artifacts yet

   Would you like me to:
   1. Start working (I have enough context)
   2. Create governance artifacts (vision, guardrails)
   3. Run deeper discovery (component catalog)

   Or just tell me what you want to build."
```

**Why hybrid:**
- Fast path for experienced devs who want to start immediately
- Guided path for those who want more structure
- No mandatory wizard — wizard is optional

### What to Ask (If Anything)

| Question | When to Ask | Why |
|----------|-------------|-----|
| Project name | Only if can't detect from directory/git | Personalization |
| Template level | Never (default minimal) | YAGNI — add when needed |
| Tech stack | Never (detect automatically) | Inference is better |
| What to build first? | In /session-start | Most valuable question |

**The only question that matters:** "What do you want to build?"

Everything else can be inferred or defaulted.

### Implementation Recommendation

**For F&F:**

1. **`rai init`** (CLI command)
   - Scan project
   - Generate minimal CLAUDE.md
   - Copy skills to .claude/skills/
   - Print next steps
   - No questions

2. **Enhanced `/session-start`** (skill)
   - Detect first-time user
   - Show what was detected
   - Offer guidance path or direct start
   - Ask "What do you want to build?"

**Effort:**
- `rai init`: ~2h
- Enhanced session-start: ~1h
- Total: ~3h

**Trade-off accepted:**
- Not wizard-based (against OpenClaw pattern)
- Rationale: We're Claude Code only, not multi-channel. Wizard is overkill.

---

## Confidence Assessment

| Finding | Confidence | Evidence |
|---------|------------|----------|
| Auto-discovery is standard | HIGH | 5 tools do this |
| Config files > wizards | HIGH | 5/6 tools use files |
| "Scan first" pattern | HIGH | 4 sources |
| Time to value <10min | HIGH | All tools |
| Ask only essential questions | MEDIUM | 3 sources (others ask nothing) |

---

## Open Questions

1. **Should we do component discovery automatically?**
   - Current: `/discover-*` skills are manual
   - Consider: Auto-run on `rai init`?
   - Risk: Slow for large codebases

2. **Global ~/.rai/ for user patterns?**
   - Current: Project-only
   - Evidence: 4 tools have global → project cascade
   - Recommendation: Defer to post-F&F, validate need first

---

## Sources

- [Aider Repository Map](https://aider.chat/docs/repomap.html)
- [Aider Tree-sitter Blog](https://aider.chat/2023/10/22/repomap.html)
- [Cursor Features](https://cursor.com/features)
- [Cursor Complete Guide](https://medium.com/@hilalkara.dev/cursor-ai-complete-guide-2025)
- [Continue.dev Documentation](https://docs.continue.dev)
- [Cline GitHub Wiki](https://github.com/cline/cline/wiki)
- [Windsurf Documentation](https://docs.windsurf.com/)
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart)
- [Creating Perfect CLAUDE.md](https://dometrain.com/blog/creating-the-perfect-claudemd-for-claude-code/)
- [OpenClaw Onboarding Wizard](https://docs.openclaw.ai/start/wizard)
- [GitHub Copilot Agent Onboarding](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/)
- [Agentic Coding Flywheel Setup](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup)

---

*Research by: Rai*
*Informs: E7 Onboarding, `/initial-setup` skill design*
