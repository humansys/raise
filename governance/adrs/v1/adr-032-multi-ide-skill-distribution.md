---
id: "ADR-032"
title: "Multi-IDE Skill Distribution — Universal scaffolding for 5 IDEs"
date: "2026-02-18"
status: "Draft"
---

# ADR-032: Multi-IDE Skill Distribution

## Context

RAISE-128 introduced `IdeConfig` for Claude and Antigravity. Research (SES-212) revealed that 4 of 5 market-relevant IDEs support skills/agents, not just instructions. The skill format (YAML frontmatter + markdown body) is nearly identical across Windsurf, Antigravity, and RaiSE. Copilot has a richer model with tool restrictions and MCP integration.

## Decision (DRAFT — pending final design)

### 1. Expand IdeType to 5 IDEs

```python
IdeType = Literal["claude", "cursor", "windsurf", "copilot", "antigravity"]
```

### 2. Expand IdeConfig with skills + workflows + prompts

```python
class IdeConfig(BaseModel):
    ide_type: IdeType
    instructions_file: str
    skills_dir: str | None = None        # Skills/agents directory
    workflows_dir: str | None = None     # Workflows/prompts directory
    detection_markers: list[str]         # Paths to check for IDE presence
    skill_format: SkillFormat = "raise"  # How to transform SKILL.md
```

### 3. IDE-specific file mapping

| IDE | Instructions | Skills | Workflows | Format notes |
|-----|-------------|--------|-----------|--------------|
| claude | `CLAUDE.md` | `.claude/skills/` | — (skills = commands) | Native SKILL.md |
| cursor | `.cursor/rules/raise.mdc` | — | — | No skills support |
| windsurf | `.windsurf/rules/raise.md` | `.windsurf/skills/` | `.windsurf/workflows/` | Same SKILL.md format |
| copilot | `.github/copilot-instructions.md` | `.github/agents/` | `.github/prompts/` | Different frontmatter (`tools`, `infer` for agents; `agent`, `tools` for prompts) |
| antigravity | `.agent/rules/raise.md` | `.agent/skills/` | `.agent/workflows/` | Same SKILL.md format |

### 4. Skill format transformation

- **Windsurf, Antigravity**: Copy SKILL.md as-is (identical format)
- **Copilot agents**: Transform frontmatter (`name`, `description` → add `tools`, `infer: true`)
- **Copilot prompts**: Transform to `.prompt.md` format (add `agent: agent`, `tools`)
- **Cursor**: No skills (only instructions)

### 5. Auto-detection via `rai init --detect`

Scan project root for IDE markers. Generate instructions + skills for all detected IDEs.

### 6. AGENTS.md as bonus output

Generate `AGENTS.md` at project root — supported by Cursor, Windsurf, and Copilot. Cross-tool compatible. Content equivalent to instructions but in the universal format.

## Consequences

| Type | Impact |
|------|--------|
| + | `rai init` configures ANY developer's IDE automatically |
| + | Skills distributed to 4/5 IDEs (all except Cursor) |
| + | Same canonical source → N projections (ADR-012 extended) |
| + | AGENTS.md gives cross-tool coverage for free |
| - | Copilot frontmatter transformation adds complexity |
| - | 5 IdeConfigs to maintain and test |
| - | Cursor gets minimal support (instructions only) |

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Only Claude + Antigravity | Misses 80%+ of market (Cursor, Copilot, Windsurf) |
| Only instructions, no skills | Wastes the fact that 4/5 IDEs support skills |
| AGENTS.md only | Lowest common denominator, misses IDE-specific features |

## Research Evidence

See `work/research/raise-197-ide-skills-*.md` for detailed per-IDE analysis:
- `raise-197-ide-skills-cursor.md`
- `raise-197-ide-skills-windsurf.md`
- `raise-197-ide-skills-copilot.md`
- `raise-197-ide-skills-antigravity.md`

## Open Questions

1. Should `rai init --detect` also generate `AGENTS.md`?
2. Copilot agent `tools` field — should we restrict or allow all?
3. Cursor Custom Modes (`.cursor/modes.json`) — wait for stable or skip?
4. Should we generate per-directory `.instructions.md` for Copilot monorepo support?

---

*Status: Draft — pending implementation in RAISE-197*
*Created: 2026-02-18 (SES-212)*
