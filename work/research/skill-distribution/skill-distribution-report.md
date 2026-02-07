# Skill Distribution for AI IDEs — Research Report

**Research ID:** RES-SKILL-DIST-001
**Date:** 2026-02-06
**Author:** Rai

---

## Research Question

How should `raise init` distribute AI assistant skills/prompts to user projects, supporting Claude Code, Cursor, Windsurf, GitHub Copilot, and other AI IDEs?

---

## Key Findings

### 1. IDE Configuration Landscape (2026)

Each IDE uses a different file convention:

| IDE | Config Location | Format | Notes |
|-----|----------------|--------|-------|
| **Claude Code** | `.claude/skills/{name}/SKILL.md` | MD + YAML frontmatter | Skills = slash commands |
| **Claude Code** | `CLAUDE.md` | Markdown | Project-level instructions |
| **Cursor** | `.cursor/rules/*.mdc` | MD + YAML frontmatter | 4 rule types (always/auto/glob/manual) |
| **Windsurf** | `.windsurfrules` or `.windsurf/rules/*.md` | Markdown | 6000 char limit |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown | Repo-wide |
| **GitHub Copilot** | `.github/instructions/*.instructions.md` | MD + `applyTo` frontmatter | Path-specific |
| **Copilot/Cursor** | `AGENTS.md` | Markdown | Emerging cross-IDE standard |
| **Aider** | `CONVENTIONS.md` via `.aider.conf.yml` | Markdown | Read-only, cached |

**Confidence:** HIGH (all from primary docs)

### 2. The "Single Source, Multiple Targets" Pattern Is Established

Multiple tools (ai-rulez, ruler, rulesync, vibe-rules) solve the same problem: define rules once, generate for each IDE.

| Tool | Stars | Approach | IDEs Supported |
|------|-------|----------|----------------|
| ai-rulez | ~1k | YAML+MD source → 18 generators | Claude, Cursor, Copilot, Windsurf, + |
| ruler | ~500 | MD source → toml config → 25 agents | Most IDEs |
| rulesync | ~200 | Sync existing files between IDEs | Most IDEs |

**Claim:** Single-source-of-truth with IDE adapters is the consensus pattern.
**Confidence:** HIGH (4+ independent implementations)
**Triangulation:** S5, S6, S7, S8

### 3. AGENTS.md Is Emerging as Cross-IDE Standard

GitHub Copilot, Cursor, and others recognize `AGENTS.md` as a universal agent instruction file. This is the closest thing to a cross-IDE standard.

**Confidence:** MEDIUM (emerging, not yet universal — Claude Code uses CLAUDE.md)
**Triangulation:** S4, S10

### 4. Skills vs Rules — Different Abstractions

| Concept | What It Is | Who Uses It |
|---------|-----------|-------------|
| **Rules** | Always-on project instructions | Cursor, Copilot, Windsurf |
| **Skills** | Invocable slash commands with process steps | Claude Code |
| **Agents** | Specialized personas/behaviors | ai-rulez, Cursor |
| **Instructions** | Passive context injection | Copilot, Aider |

**Key insight:** Claude Code's `/skill` concept (multi-step process with instructions) doesn't map directly to other IDEs' "rules" (passive context). RaiSE skills are process guides, not just coding conventions.

**Confidence:** HIGH
**Triangulation:** S1, S2, S3, S4

### 5. What RaiSE Actually Needs to Distribute

Two distinct types of content:

**A. Project Rules (passive context):**
- Coding conventions, architecture patterns, project instructions
- Maps to: `CLAUDE.md`, `.cursor/rules/`, `.windsurfrules`, `.github/copilot-instructions.md`
- `raise init --detect` already generates `CLAUDE.md` and `governance/guardrails.md`

**B. Process Skills (active invocable):**
- `/session-start`, `/discover-*`, `/story-*`
- Maps to: `.claude/skills/` (Claude Code native)
- **No direct equivalent in other IDEs** — Cursor/Copilot don't have skill invocation
- For other IDEs: could be distributed as markdown reference docs or rules

---

## Patterns & Insights

### P1: Two-Layer Distribution

```
raise init
├── Layer 1: Project Rules (all IDEs)
│   ├── CLAUDE.md (Claude Code)
│   ├── .cursor/rules/raise.mdc (Cursor)
│   ├── .windsurfrules (Windsurf)
│   ├── .github/copilot-instructions.md (Copilot)
│   └── AGENTS.md (universal fallback)
│
└── Layer 2: Process Skills (Claude Code only, for now)
    └── .claude/skills/{name}/SKILL.md
```

### P2: Canonical Source in .raise/

Store the canonical version of rules/skills in `.raise/` (RaiSE's territory), then generate IDE-specific files. This avoids vendor lock-in and enables future IDE support without changing the source.

```
.raise/
├── rules/          # Canonical project rules (markdown)
└── skills/         # Canonical process skills (markdown)
    ├── session-start/SKILL.md
    ├── discover-start/SKILL.md
    └── ...
```

### P3: Progressive Complexity (PAT-158)

For F&F (Feb 9), simplest viable approach:
1. Copy skills directly to `.claude/skills/` (Claude Code is primary target)
2. Generate `CLAUDE.md` with project context (already works)
3. Defer multi-IDE generation to post-F&F

---

## Gaps & Unknowns

1. **Skill portability:** Claude Code skills don't map to Cursor/Copilot. Would need to be adapted as rules/instructions with different invocation patterns.
2. **Version management:** When RaiSE updates skills, how do user projects get updates? (skill update/sync — out of scope for now)
3. **Skill selection:** Should `raise init` copy all skills or ask which ones? User might not need discovery skills for greenfield.

---

## Recommendation

**Decision:** Two-phase approach aligned with PAT-158 (progressive complexity).

### Phase 1: F&F (Feb 9) — Claude Code Skills

```bash
raise init  # copies essential skills to .claude/skills/
```

- Package onboarding skills as distributable assets in `raise_cli`
- Copy to `.claude/skills/` during init
- Skills: `session-start`, `discover-start`, `discover-scan`, `discover-validate`, `discover-complete`
- `CLAUDE.md` generation already exists
- **No multi-IDE support yet** — Claude Code is our F&F audience

### Phase 2: Post-F&F — Multi-IDE Rules

```bash
raise init --ide cursor     # generates .cursor/rules/raise.mdc
raise init --ide copilot    # generates .github/copilot-instructions.md
raise init --ide all        # generates for all detected IDEs
```

- Canonical rules stored in `.raise/rules/`
- IDE adapters generate native format files
- Consider using or contributing to `ai-rulez` / `ruler` ecosystem
- Process skills remain Claude Code-specific until other IDEs support similar concepts

**Confidence:** HIGH
**Rationale:**
- F&F users are Claude Code users (our primary channel)
- Multi-IDE is real demand but not F&F critical
- The two-phase approach lets us ship value now and expand later
- Canonical source in `.raise/` keeps options open

**Trade-offs:**
- Phase 1 is Claude Code-only (acceptable for F&F)
- Skills won't auto-update when RaiSE updates (acceptable — manual for now)

**Risks:**
- Skills going stale in user projects after init → mitigate with version check in `/session-start`
- `.claude/skills/` directory polluting user's git → mitigate with clear README and optional `.gitignore` entries

---

## Governance Linkage

- **Story:** `story/init/skill-scaffolding` (active branch)
- **Parking lot:** "Feature pre-verification in /story-start" — skill version checking
- **Future epic:** Multi-IDE rules distribution (post-F&F)
