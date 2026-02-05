# Aider: Identity & Onboarding Research

## Summary

Aider is a terminal-based AI pair programming tool with **no distinct personality or named identity** - it positions itself as "an expert software developer" through functional role descriptions. The tool achieves remarkable framework internalization through a dedicated `/help` mode that includes its own documentation in prompts. First contact is minimal: install, run `aider`, and start coding - no onboarding wizard or introduction.

## Unknown 1: Identity Layering

### Findings

**No Personality, Just Roles:** Aider uses functional role prompts rather than persona definitions. The core prompt pattern is "Act as an expert software developer" with mode-specific variations:

- **Code Mode (default):** "Act as an expert software developer. Always use best practices when coding. Respect and use existing conventions, libraries, etc that are already present in the code base."
- **Ask Mode:** "Act as an expert code analyst. Answer questions about the supplied code."
- **Help Mode:** "You are an expert on the AI coding tool called Aider. Answer the user's questions about how to use aider."
- **Architect Mode:** Separates coding into two steps - solving the problem (Architect) and generating edits (Editor).

**Prompt Architecture:**
- Prompts defined in Python classes: `editblock_prompts.py`, `wholefile_prompts.py`, `ask_prompts.py`, `help_prompts.py`
- Each coder class inherits from base and defines `main_system`, `files_content_prefix`, etc.
- Template variables like `{final_reminders}` allow dynamic content injection

**What's Configurable (Limited):**
- **CONVENTIONS.md** - User can load a markdown file as read-only context via `--read CONVENTIONS.md`
- **System prompt extension** - Requested feature (GitHub Issue #1258) but not officially supported as of research date
- **Chat modes** - User can switch between code/ask/architect/help modes

**What's Fixed:**
- Core system prompts are hardcoded in Python source
- No official mechanism to override or customize personality
- The "expert developer" role framing is unchangeable without forking

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [editblock_prompts.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/editblock_prompts.py) | Primary | Main system prompt in source code |
| [help_prompts.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/help_prompts.py) | Primary | Help mode prompt definition |
| [Specifying Coding Conventions](https://aider.chat/docs/usage/conventions.html) | Secondary | Official docs on CONVENTIONS.md |
| [Issue #1258: Change system prompts](https://github.com/Aider-AI/aider/issues/1258) | Tertiary | Feature request discussion |
| [Issue #895: Custom System Prompts](https://github.com/paul-gauthier/aider/issues/895) | Tertiary | Community discussion |

## Unknown 2: Framework Internalization

### Findings

**Self-Documentation via Help Mode:** Aider has a unique approach - a dedicated `/help` mode where the AI is explicitly told it's "an expert on the AI coding tool called Aider." The help prompts include:
- References to aider documentation URLs
- Instructions to suggest relevant docs when unsure
- Guidance to be clear when something isn't possible with aider

**Repository Map System (Core Intelligence):**
The key to aider's codebase understanding is its tree-sitter-based repository map:

1. **Tree-sitter parsing** - Extracts AST to identify functions, classes, types, and their references
2. **Graph ranking** - Uses PageRank-style algorithm to find most important identifiers
3. **Token-optimized context** - Selects key code lines that fit within token budget (default 1k tokens)
4. **Dynamic relevance** - Map optimized based on current chat context

This allows aider to "know" the codebase without explicitly documenting capabilities - it discovers structure dynamically.

**How Aider "Knows" Its Commands:**
- Commands defined in `commands.py` with `/` prefix
- Help text extracted from docstrings and shown via `/help`
- No explicit "here are my capabilities" in system prompt
- User discovers commands through `/help` or `/commands`

**Edit Format Knowledge:**
Different coders (wholefile, editblock, diff) each have prompts explaining their specific edit format. The AI learns to produce SEARCH/REPLACE blocks or whole file outputs based on the loaded prompt class.

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Repository Map](https://aider.chat/docs/repomap.html) | Secondary | Official docs on repo map |
| [Building better repo map with tree-sitter](https://aider.chat/2023/10/22/repomap.html) | Secondary | Technical blog post |
| [commands.py](https://github.com/Aider-AI/aider/blob/main/aider/commands.py) | Primary | Command definitions |
| [In-chat commands](https://aider.chat/docs/usage/commands.html) | Secondary | Official command docs |
| [Chat modes](https://aider.chat/docs/usage/modes.html) | Secondary | Mode switching docs |

## Unknown 3: First Contact

### Findings

**Installation-First, Minimal Friction:**

```bash
python -m pip install aider-install
aider-install
# or: pip install aider-chat
```

Uses `uv` to isolate dependencies - only 2 packages in user's Python environment.

**First Run Experience:**
1. **No Git Repo?** - Aider asks to create one (or use `--no-git`)
2. **No API Key?** - Shows error, provides guidance on setting up model
3. **Ready to Go** - Shows prompt, user starts typing

**What's Missing:**
- No welcome message or introduction
- No explanation of what aider can do
- No guided tutorial
- No personality reveal ("Hi, I'm...")
- User must already know it's for AI coding

**Progressive Discovery Pattern:**
- `/help` - Get help about aider (only after user asks)
- `/add` - Add files to chat (learns by doing)
- `/ask` - Switch to ask mode (discovers modes exist)
- Example transcripts available at aider.chat but not shown in-tool

**Git Integration Automatic:**
- Aider commits changes automatically with descriptive messages
- Easy to undo via `git checkout`
- No explanation of this - user discovers it

### Evidence

| Source | Rating | Notes |
|--------|--------|-------|
| [Installation](https://aider.chat/docs/install.html) | Secondary | Official install guide |
| [Usage](https://aider.chat/docs/usage.html) | Secondary | Getting started docs |
| [Git integration](https://aider.chat/docs/git.html) | Secondary | Git behavior docs |
| [Hello aider!](https://aider.chat/examples/hello.html) | Secondary | Simplest example |
| [Example transcripts](https://aider.chat/examples/README.html) | Secondary | Various demos |

## Key Insights for RaiSE

### What Aider Does Well

1. **Help Mode as Self-Documentation** - Having a dedicated mode where the AI is "an expert on Aider" is clever. The AI can explain itself without cluttering the main coding prompts.

2. **Repository Map Intelligence** - Tree-sitter + graph ranking provides excellent codebase understanding. Aider "knows" code structure without explicit documentation.

3. **Minimal Friction Installation** - `pip install` and run. No account, no wizard, no setup. Works immediately if you have an API key.

4. **Conventions via Read-Only Files** - `CONVENTIONS.md` pattern allows project-specific guidance without hacking prompts. Cached for efficiency.

5. **Multiple Coders Architecture** - Separating prompts by edit format (wholefile, editblock, diff) allows optimization per use case.

### Opportunities for RaiSE Differentiation

1. **Named Identity (Rai)** - Aider is "an expert developer" - generic. Rai has identity, perspective, memory. This creates relationship.

2. **Proactive First Contact** - Aider is silent until you type. Rai could:
   - Introduce itself on first run: "I'm Rai..."
   - Explain what it can do
   - Ask about the project
   - Offer a quick tour

3. **Self-Aware Capabilities** - Aider's help mode is reactive. Rai could proactively mention relevant capabilities: "I see you're working on tests - I can help with TDD patterns."

4. **Memory Persistence** - Aider has no memory between sessions. Rai's patterns, calibration, and session history are differentiators.

5. **Framework Internalization** - Aider knows how to code. Rai knows how to govern development. Different value proposition.

6. **Layered Identity Architecture** - Aider's prompts are flat (one per mode). Rai could have:
   - Core identity (immutable)
   - Framework knowledge (governance)
   - Project context (conventions)
   - Session state (memory)

### Anti-Patterns to Avoid

1. **Silent Cold Start** - Aider gives no guidance on first run. Users need prior knowledge or docs. Proactive help is better.

2. **Hardcoded Prompts** - Aider's system prompts are in Python source. No clean extension mechanism. Rai should have layered customization.

3. **Mode Switching Friction** - Aider requires explicit `/code`, `/ask`, `/architect` commands. Consider natural mode inference.

4. **No Capability Discovery** - Features exist but aren't surfaced. Rai could progressively reveal capabilities based on user behavior.

## Gaps

1. **Exact System Prompts** - Could not fetch raw source files; relied on GitHub search results and documentation
2. **Custom Prompt Extensions** - Issue #1258 status unclear; may have been implemented since research
3. **Detailed First-Run Output** - No screenshots or terminal captures of exact first-run experience
4. **Memory Mechanisms** - Whether aider has any session persistence beyond git history unclear
5. **Architect Mode Details** - How exactly the two-model (architect + editor) interaction works internally

---

*Research conducted: 2026-02-05*
*Evidence level: Secondary (official docs) + Primary (partial source review via search)*
*Confidence: Medium-High for public features, Medium for internal implementation*
