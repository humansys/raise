# GitHub Copilot: Identity & Onboarding Research

## Summary

GitHub Copilot has evolved from a code completion tool to a fully agentic development partner with customizable identity through chat modes (now called "agents"). It supports repository-level custom instructions via `.github/copilot-instructions.md` and path-specific instructions via `*.instructions.md` files. The onboarding experience prioritizes minimal friction with one-click enablement, while identity/personality is increasingly user-configurable rather than fixed.

## Unknown 1: Identity Layering

### Findings

**No Fixed Personality:** Copilot does not have a distinct, fixed personality. Instead, GitHub has moved toward a flexible identity system where personality and tone are customizable by users and teams.

**Custom Instructions System:**
- Repository-wide: `.github/copilot-instructions.md` in repo root
- Path-specific: `.github/instructions/*.instructions.md` with regex patterns
- Personal: VS Code settings for user-level instructions

**File Format:**
```markdown
# copilot-instructions.md

Natural language instructions in Markdown format.
- Short, self-contained statements
- Bullet points for easy scanning
- Imperative directives (not narrative paragraphs)
- Max ~1,000 lines recommended
```

**What's Configurable:**
- Coding standards and conventions
- Tech stack preferences
- Project structure descriptions
- Build/test workflows
- Agent-specific exclusions via `excludeAgent` frontmatter

**What's Fixed:**
- Core safety guidelines (not exposed)
- Base model capabilities
- Tool access patterns (MCP integration)

**Custom Agents (formerly Chat Modes):**
- Defined via `.chatmode.md` files
- Specify: role/persona, instructions, allowed tools, context
- Built-in modes: Ask, Edit, Agent
- Custom modes can define specialized personas (security reviewer, documentation writer)

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [GitHub Docs - Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) | Official | Secondary |
| [VS Code Docs - Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) | Official | Secondary |
| [5 Tips for Writing Custom Instructions](https://github.blog/ai-and-ml/github-copilot/5-tips-for-writing-better-custom-instructions-for-copilot/) | Official Blog | Secondary |
| [Copilot Chat Modes Explained](https://dev.to/anchildress1/github-copilot-chat-modes-explained-with-personality-2f4c) | Community | Tertiary |
| [Custom Chat Modes: AI Personas](https://thomasthornton.cloud/2025/09/10/github-copilot-custom-chat-modes-ai-personas-that-match-your-needs/) | Community | Tertiary |

## Unknown 2: Framework Internalization

### Findings

**Self-Awareness of Capabilities:**
Copilot's awareness of its own capabilities is managed through:
1. **Agent Skills** - Folders containing instructions, scripts, and resources that Copilot automatically loads when relevant
2. **MCP (Model Context Protocol)** integration for tool discovery
3. **Prompt files** that specify available tools

**Agent Skills Structure (December 2025):**
- Open standard working across VS Code, CLI, and coding agent
- Skills are folders with instructions + scripts
- Auto-loaded when relevant to the prompt
- Can automate repetitive tasks, present changes as reviewable diffs

**Built-in CLI Agents (January 2026):**
- Explore: Navigate codebase
- Task: Execute specific work
- Plan: Design implementation approach
- Code-review: Review changes
- Copilot delegates automatically and can run agents in parallel

**Feature Surfacing:**
- Agent mode handles multi-step tasks autonomously
- Edit mode for targeted changes
- Ask mode for Q&A
- Tools and capabilities exposed through MCP servers

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [GitHub Copilot Agent Skills Announcement](https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/) | Official | Secondary |
| [About Agent Skills - GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | Official | Secondary |
| [Copilot CLI Enhanced Agents](https://github.blog/changelog/2026-01-14-github-copilot-cli-enhanced-agents-context-management-and-new-ways-to-install/) | Official | Secondary |
| [VS Code Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) | Official | Secondary |
| [Copilot Customization Guide](https://blog.cloud-eng.nl/2025/12/22/copilot-customization/) | Community | Tertiary |

## Unknown 3: First Contact

### Findings

**Initial Setup Experience:**
- One-click enablement from IDE (VS Code, Visual Studio, JetBrains)
- Sign in with GitHub credentials
- Copilot becomes active immediately
- "Rarely takes more than a few minutes"

**Copilot Free Tier Flow:**
1. Click Copilot icon in editor top-right
2. Click "Sign up for Copilot Free" in sidebar
3. Sign in or create GitHub account
4. Ready to use

**No Explicit Introduction:**
- No tutorial or walkthrough by default
- No "meet your AI assistant" moment
- Immediate utility-first approach

**New Repository Experience:**
- When creating new repo with Copilot coding agent, it opens a draft PR
- Writes requested code
- Requests review from user
- Can choose starting branch and provide additional instructions

**Organizational Onboarding (Recommended):**
- 45 days before: Define success metrics, train champions
- 14 days: Share announcements, async resources
- 7 days: Host workshop
- Launch day: Slack channel, wiki, curated resources

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [GitHub Copilot Quickstart](https://docs.github.com/copilot/quickstart) | Official | Secondary |
| [Getting Started with Copilot Plan](https://docs.github.com/en/copilot/how-tos/manage-your-account/get-started-with-a-copilot-plan) | Official | Secondary |
| [Start New Repo with Copilot](https://github.blog/changelog/2025-09-30-start-your-new-repository-with-copilot-coding-agent/) | Official | Secondary |
| [Training and Onboarding Developers](https://github.com/resources/whitepapers/training-and-onboarding-developers-on-github-copilot) | Official Whitepaper | Secondary |
| [Onboarding AI Peer Programmer](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/) | Official Blog | Secondary |

## Key Insights for RaiSE

### What We Can Learn

1. **Identity is User-Owned, Not Tool-Owned**
   - Copilot deliberately avoids a fixed personality
   - Users/teams customize via instructions, not fighting defaults
   - Rai should consider: what's the right balance between personality and flexibility?

2. **Layered Instruction System Works**
   - Repository-wide + path-specific + user-level = comprehensive coverage
   - Frontmatter controls which agents see what
   - RaiSE already has similar patterns (CLAUDE.md hierarchy)

3. **Skills/Agents Pattern Validated**
   - Agent Skills are folders with instructions + scripts
   - Auto-loaded based on context relevance
   - Aligns with RaiSE `.claude/skills/` approach

4. **Friction-Free First Contact**
   - Copilot optimizes for immediate productivity, not introduction
   - No "personality reveal" moment
   - Rai could differentiate by having a "first meeting" experience

5. **MCP as Standard Protocol**
   - Copilot adopted MCP for tool integration
   - Industry convergence on this standard
   - RaiSE should consider MCP compatibility

### Differentiation Opportunities

1. **Rai Has Identity; Copilot Does Not**
   - Copilot is explicitly a "neutral tool"
   - Rai can offer a more relational experience
   - This is a feature, not a limitation

2. **Governance-First vs Completion-First**
   - Copilot optimizes for code suggestions
   - Rai optimizes for reliable, governed software engineering
   - Different value propositions

3. **Memory and Continuity**
   - Copilot has no persistent memory across sessions
   - Rai's memory system is differentiating

## Gaps

### Could Not Determine

1. **Default System Prompt** - Copilot's base instructions are not public
2. **Exact Personality Guidelines** - What constraints exist on persona customization
3. **First-Time User Flow Details** - No detailed walkthrough of the new user experience available
4. **Retention/Onboarding Metrics** - How effective is the friction-free approach

### Needs Further Research

1. Compare Copilot's Agent Skills structure with RaiSE skills
2. Evaluate MCP integration depth and compatibility requirements
3. User studies on personality-free vs personality-rich AI assistants

---

*Research conducted: 2026-02-05*
*Method: WebSearch (docs.github.com, official blog, community sources)*
*Evidence quality: Primarily Secondary (official documentation)*
