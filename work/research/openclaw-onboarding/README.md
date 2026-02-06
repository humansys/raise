# Research: OpenClaw Onboarding & RaiSE DX Design

> **ID:** RES-ONBOARD-001
> **Status:** Complete
> **Date:** 2026-02-02
> **Decision:** Informs E7 Distribution — F7.1 Agent Skill / Onboarding

---

## Research Question

How does OpenClaw handle onboarding for new users? What can we learn to design the raise-cli onboarding experience for F&F users?

---

## Key Findings

### 1. OpenClaw Onboarding Flow

**Installation:**
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

**Wizard Steps:**
1. Model authentication (API keys or OAuth)
2. Gateway configuration (local/remote)
3. Channel setup (WhatsApp, Telegram, Slack, etc.)
4. Security settings (pairing codes)
5. Workspace bootstrap with skills
6. Optional daemon installation

**Files Created:**
```
~/.openclaw/
├── openclaw.json          # Configuration
└── workspace/
    ├── AGENTS.md          # Agent prompts
    ├── SOUL.md            # Identity/personality
    ├── TOOLS.md           # Available tools
    └── skills/            # Installed skills
        └── <skill>/SKILL.md
```

**Key Commands:**
- `openclaw onboard` — Interactive wizard
- `openclaw status` — Check health
- `openclaw doctor` — Diagnose issues
- `openclaw dashboard` — Web UI

### 2. What Makes OpenClaw DX Good

| Pattern | Why It Works |
|---------|--------------|
| **Single onboard command** | No manual config file editing |
| **Interactive wizard** | Guides through decisions |
| **Daemon mode** | "Set and forget" — always running |
| **Doctor command** | Self-diagnosis for troubleshooting |
| **Workspace isolation** | Per-project configuration |

### 3. What's Different for RaiSE

| OpenClaw | RaiSE |
|----------|-------|
| Multi-channel messaging | Single-channel (Claude Code) |
| Gateway daemon | No daemon needed |
| Global config (`~/.openclaw/`) | Per-project (governance/) |
| Node.js ecosystem | Python ecosystem |
| Agent-first (autonomous) | Human-first (collaborative) |

---

## RaiSE Onboarding Design (Proposed)

### User Journey

```
pip install raise-cli
    ↓
raise onboard [--template minimal|standard|full]
    ↓
Interactive wizard OR --yes for defaults
    ↓
Project ready with governance + skills + CLAUDE.md
    ↓
/session-start in Claude Code
```

### `raise onboard` Wizard Steps

**Step 1: Detect Project State**
- New project (greenfield) vs existing repo (brownfield)
- Detect existing governance files
- Detect .claude/ or .rai/ directories

**Step 2: Choose Template**
```
? Select governance template:
  > minimal   — Just CLAUDE.md + essential skills (F&F recommended)
    standard  — + governance/ structure + katas
    full      — + .rai/ identity + memory infrastructure
```

**Step 3: Configure Governance (if standard/full)**
- Project name
- Tech stack (for guardrails)
- Team size (solo/small/enterprise)

**Step 4: Install Skills**
```
? Install development lifecycle skills? (Y/n)
  - /session-start, /session-close
  - /story-design, /story-plan, /story-implement, /story-review
  - /research, /debug
```

**Step 5: Generate CLAUDE.md**
- Compile from governance artifacts
- Or create minimal template if no governance

**Step 6: Verify & Next Steps**
```
✓ RaiSE initialized successfully!

Created:
  - CLAUDE.md (AI context)
  - .claude/skills/ (11 skills)
  - governance/ (project governance)

Next steps:
  1. Open Claude Code in this directory
  2. Run /session-start to begin
  3. Read framework/reference/constitution.md for principles

Run 'raise status' to verify setup.
```

### Files Created (by template)

**Minimal:**
```
project/
├── CLAUDE.md              # AI context (generated)
└── .claude/skills/        # Development skills
    ├── session-start/
    ├── session-close/
    ├── story-design/
    └── ...
```

**Standard:**
```
project/
├── CLAUDE.md
├── .claude/skills/
├── governance/
│   └── solution/
│       ├── vision.md      # Project vision
│       └── guardrails.md  # Code standards
└── .raise/
    └── katas/             # Process definitions
```

**Full:**
```
project/
├── CLAUDE.md
├── .claude/skills/
├── governance/
├── .raise/
└── .rai/                  # Rai identity + memory
    ├── identity/
    └── memory/
```

### Additional Commands

| Command | Purpose |
|---------|---------|
| `raise onboard` | Interactive setup wizard |
| `raise status` | Check project health |
| `raise doctor` | Diagnose configuration issues |
| `raise sync` | Regenerate CLAUDE.md from governance |
| `raise upgrade` | Update skills to latest version |

---

## Recommendation

**Decision:** Implement `raise onboard` command with 3 templates

**Confidence:** HIGH

**Rationale:**
1. OpenClaw proves wizard-based onboarding works
2. Templates allow scaling from F&F (minimal) to enterprise (full)
3. Per-project config aligns with RaiSE philosophy (governance as code)
4. Skills copy enables offline use and customization

**For F&F (Feb 9):**
- Implement **minimal template only** — fastest path to value
- Standard/full templates can wait for v2.1

**Trade-offs:**
- No daemon = no background features (acceptable for v2)
- Per-project skills = duplication (but enables customization)

**Risks:**
- Skills directory size (~200KB) might feel heavy → mitigate with --no-skills flag
- Users might skip wizard → mitigate with sensible --yes defaults

---

## Implementation Estimate

| Feature | Size | Priority |
|---------|------|----------|
| `raise onboard --template minimal` | S | P0 (F&F) |
| `raise status` | XS | P0 (F&F) |
| `raise doctor` | S | P1 |
| Standard/full templates | M | P2 |
| `raise upgrade` | S | P2 |

**F&F scope:** `onboard` + `status` = ~2-3 hours with kata cycle

---

## Sources

- [OpenClaw Getting Started](https://docs.openclaw.ai/start/getting-started)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Complete Guide 2026](https://www.nxcode.io/resources/news/openclaw-complete-guide-2026)
- [Codecademy OpenClaw Tutorial](https://www.codecademy.com/article/open-claw-tutorial-installation-to-first-chat-setup)
- [BMAD Method Brownfield](https://docs.bmad-method.org/how-to/brownfield/)

---

*Research by: Rai*
*Informs: E7 Distribution, F7.1 Agent Skill*
