# OpenClaw: Identity & Onboarding Research

> **Research ID:** RES-E14-OPENCLAW
> **Date:** 2026-02-05
> **Prior Research:** RES-OPENCLAW-001, RES-ONBOARD-001
> **Focus:** Identity layering, framework internalization, first contact

---

## Summary

OpenClaw uses a **file-based identity system** with clear separation of concerns: SOUL.md (personality/boundaries), IDENTITY.md (name/vibe), AGENTS.md (operational instructions), and USER.md (user profile). The agent internalizes its capabilities through dynamic system prompt assembly that includes tool definitions and documentation pointers. First contact is wizard-driven with `openclaw onboard`, followed by agent self-bootstrap.

---

## Unknown 1: Identity Layering

### Findings

OpenClaw separates identity into four distinct files, each with specific purpose:

| File | Purpose | Configurable |
|------|---------|--------------|
| **SOUL.md** | Personality, tone, ethical boundaries | Fully user-defined |
| **IDENTITY.md** | Agent name, emoji, vibe | Fully user-defined |
| **AGENTS.md** | Operational instructions, memory | Fully user-defined |
| **USER.md** | User profile, preferred address | Fully user-defined |

**Key insight from medium article:** "people dump everything into SOUL.md" — the architecture deliberately separates these concerns to prevent context bloat and conflicting directives.

**What's fixed vs configurable:**
- **Fixed:** Core tool set (Read, Write, Edit, Bash), system prompt structure, injection order
- **Configurable:** Everything in workspace files — personality is 100% user-defined

**Identity resolution cascade:**
1. Global defaults (minimal — "assistant" personality)
2. Workspace-level files (SOUL.md, IDENTITY.md, AGENTS.md)
3. Per-channel overrides (optional)

**No "default personality"** — OpenClaw is intentionally neutral/blank by default. Users must define personality. This is deliberate: power users want full control.

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [Agent Workspace Docs](https://docs.openclaw.ai/concepts/agent-workspace) | Primary | Very High |
| [IDENTITY.md Medium article](https://alirezarezvani.medium.com) | Secondary | High |
| [MMNTM Deep Dive on Soul Files](https://www.mmntm.net) | Secondary | High |
| [soul.md GitHub repo](https://github.com/aaronjmars/soul.md) | Secondary | High |

---

## Unknown 2: Framework Internalization

### Findings

OpenClaw's agent "knows" its capabilities through **dynamic system prompt assembly**:

**Prompt Structure (from docs):**
```
Header
Tool Definitions (filtered by policy)
Memory Recall
OpenClaw Self-Update instructions
Workspace Files (SOUL.md, IDENTITY.md, etc.)
Documentation pointers
Runtime context
```

**Self-documentation mechanisms:**
1. **Tool schemas injected at session start** — Each tool has JSON schema describing capabilities
2. **Documentation section in prompt** — Points to local docs directory and public mirrors
3. **OpenClaw Self-Update section** — Instructions for `config.apply` and `update.run`
4. **Prompt modes** — `full` (default) vs `minimal` (sub-agents) to control context size

**How capabilities are surfaced to AI:**
- Tool names listed explicitly: "Tool names are case-sensitive. Call tools exactly as listed."
- Default tools: grep, find, ls, apply_patch, exec tools
- Extension tools registered dynamically (avoiding context bloat)
- Skills discovered via ClawHub reference in prompt

**Key insight:** "Shortest system prompt of any agent" (Armin Ronacher) — minimal core, self-extensibility. The agent learns capabilities through:
1. Explicit tool list in system prompt
2. Reading its own workspace files
3. Reading local documentation when needed

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [System Prompt Docs](https://docs.openclaw.ai) | Primary | Very High |
| [DeepWiki System Prompt Analysis](https://deepwiki.com) | Secondary | High |
| [Armin Ronacher Pi Analysis](https://lucumr.pocoo.org/2026/1/31/pi/) | Secondary | High |
| [GitHub Gist: open_claw_prompts.md](https://gist.github.com) | Secondary | High |

---

## Unknown 3: First Contact

### Findings

**Installation + Onboarding Flow:**
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

**Onboarding wizard steps:**
1. **Gateway location** — Local (this Mac), Remote (SSH/Tailnet), or Configure later
2. **Model authentication** — API keys or OAuth flows
3. **Channel setup** — WhatsApp, Telegram, Slack, etc.
4. **Security settings** — Pairing codes, token generation
5. **Workspace bootstrap** — Creates standard files
6. **Daemon installation** — Optional always-on service

**Cold start handling:**
- First session: Workspace files injected (SOUL.md, IDENTITY.md, etc.)
- If files are blank/missing: Skipped (no defaults injected)
- Agent self-bootstraps: Can create/edit its own workspace files
- Memory files: Today + yesterday loaded for continuity

**First conversation:**
- No explicit "introduction" mechanism built-in
- Personality emerges from SOUL.md content (or blank if undefined)
- Agent immediately functional — no tutorial mode
- User expected to customize personality post-install

**"Day 0" design goal (from docs):** "pick where the Gateway runs, connect auth, run the wizard, and let the agent bootstrap itself"

**Post-onboarding commands:**
- `openclaw status` — Check health
- `openclaw doctor` — Diagnose issues
- `openclaw dashboard` — Web UI

### Evidence

| Source | Type | Rating |
|--------|------|--------|
| [Onboarding Docs](https://docs.openclaw.ai) | Primary | Very High |
| [jangwook.net Tutorial](https://jangwook.net) | Secondary | High |
| [openclaw.im Docs](https://openclaw.im) | Secondary | High |
| RES-ONBOARD-001 (prior research) | Internal | High |

---

## Key Insights for RaiSE

### What OpenClaw Does Well

1. **Clean separation of identity concerns** — SOUL (personality), IDENTITY (name), AGENTS (instructions), USER (profile). Prevents conflicting directives.

2. **100% user-configurable personality** — No opinionated defaults. Power users want control.

3. **Self-documenting via workspace** — Agent reads its own config files, understands itself.

4. **Wizard-based onboarding** — Single command (`openclaw onboard`) handles all setup.

5. **Doctor command for troubleshooting** — Self-diagnosis built in.

### What's Different for Rai

| Aspect | OpenClaw | Rai (RaiSE) |
|--------|----------|-------------|
| **Default personality** | Blank (user must define) | Defined (professional partner) |
| **Identity source** | User workspace files | Framework + user customization |
| **Methodology** | None (capability only) | Built-in (katas, skills, governance) |
| **First contact** | Neutral, functional | Should introduce methodology |
| **Self-knowledge** | Tool list + docs pointer | Governance graph + capability model |

### Recommendations for E14

1. **Identity layering pattern** — Consider separating:
   - `core.md` — Fixed Rai personality/principles (framework-defined)
   - `perspective.md` — Adaptable voice/style (user-customizable)
   - `developer.md` — User profile + preferences

2. **First contact should differ** — OpenClaw is blank-slate; Rai should:
   - Introduce itself and its methodology
   - Explain what makes it different (governance, judgment)
   - Offer to learn user preferences

3. **Capability internalization** — Rai should know:
   - Available skills and their purposes
   - Governance constraints active in project
   - Its own calibration data (velocity, patterns)

4. **Onboarding command** — `raise init` should:
   - Detect brownfield/greenfield (already designed in E7)
   - Copy Rai identity files with clear explanation
   - Offer personality customization as second step (not first)

---

## Gaps

1. **Multi-agent identity resolution** — How does OpenClaw handle identity when multiple agents collaborate? Not fully documented.

2. **Identity evolution over time** — Does OpenClaw track personality drift? No evidence found.

3. **Enterprise identity management** — How do organizations standardize agent personalities? Not addressed in docs.

4. **Exact system prompt template** — Full prompt source not publicly documented (security concern).

---

## References

### Primary (Very High)
- [OpenClaw Agent Workspace](https://docs.openclaw.ai/concepts/agent-workspace)
- [OpenClaw System Prompt](https://docs.openclaw.ai)
- [OpenClaw Onboarding](https://docs.openclaw.ai)

### Secondary (High)
- [Armin Ronacher Pi Analysis](https://lucumr.pocoo.org/2026/1/31/pi/)
- [DeepWiki System Prompt](https://deepwiki.com)
- [IDENTITY.md Medium Article](https://alirezarezvani.medium.com)
- [MMNTM Soul Files Deep Dive](https://www.mmntm.net)
- [soul.md GitHub](https://github.com/aaronjmars/soul.md)

### Internal (High)
- RES-OPENCLAW-001 (Architecture report)
- RES-ONBOARD-001 (Onboarding research)

---

*Research by: Rai*
*For: E14 Rai Distribution*
