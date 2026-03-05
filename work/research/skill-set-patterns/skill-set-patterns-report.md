# Research Report: Skill Set Management Patterns

> Date: 2026-03-02
> Decision: Skill ecosystem architecture for RaiSE v2.2 open core
> Depth: Standard (14 projects, 30+ sources)
> Evidence catalog: `sources/evidence-catalog.md`

## Research Question

What are the proven patterns for managing distributable, customizable
configuration/skill sets — specifically: defaults distribution, team
customization, safe upgrades, and set selection?

## Executive Summary

Across 14 projects (7 established OSS tools + 7 AI coding tools), five
patterns emerge with high confidence. The recommended architecture for
RaiSE combines the **Oh My Zsh custom directory pattern** with
**Helm's overlay model** and introduces **skill sets as a named concept**
— a differentiator no AI competitor currently offers.

## Convergent Patterns

### Pattern 1: Separate Defaults from Customizations (Structural)

Every successful project physically separates what ships from what the
user/team customizes. The separation mechanism varies:

| Mechanism | Used by | Complexity |
|-----------|---------|------------|
| **Directory** | Oh My Zsh (`$ZSH` vs `$ZSH_CUSTOM`) | Low |
| **File** | Helm (`values.yaml` vs `-f custom.yaml`) | Low |
| **Precedence layer** | Ansible (`defaults/` vs `group_vars/`) | Medium |
| **Scope** | Cursor (user vs project rules) | Low |
| **Caller/callee** | Terraform (module defaults vs caller params) | Medium |

**Recommendation for RaiSE:** Directory separation (Oh My Zsh model).
`.raise/skills/{set-name}/` contains skill sets; `.claude/skills/` is
the deployment target. Simple, visible, git-friendly.

### Pattern 2: Same-Name = Custom Wins

The simplest override mechanism: if a custom version exists with the same
name as a default, the custom version is used. No merge, no diff, no
conflict markers.

- Oh My Zsh: `$ZSH_CUSTOM/plugins/git/` shadows bundled `git`
- Helm: user values override chart values for same keys
- ESLint: rules after `extends` override extended rules
- Ansible: `group_vars` override `defaults` for same variable name

**Recommendation for RaiSE:** When deploying a skill set to `.claude/skills/`,
if a skill with the same name exists in the set, it replaces the builtin.
No merge — full replacement. User's version is their responsibility.

### Pattern 3: Updates Never Touch Custom

Universal across all 14 projects. The strongest consensus in this research.

- Oh My Zsh: `omz update` never touches `$ZSH_CUSTOM/`
- Helm: user values survive `helm upgrade` (with correct flags)
- All AI tools: workspace rules are user-owned, tool updates don't touch them

**Recommendation for RaiSE:** Already implemented via three-hash manifest.
Extend to support skill set origin tracking.

### Pattern 4: Directory-of-Files (AI Tool Trend 2025-2026)

Every major AI coding tool migrated from single-file to directory-of-files:

| Tool | Before | After |
|------|--------|-------|
| Cursor | `.cursorrules` | `.cursor/rules/*.mdc` |
| Cline | `.clinerules` file | `.clinerules/*.md` directory |
| Windsurf | `.windsurfrules` | `.windsurf/rules/*.md` |
| Copilot | single `.md` | `.github/instructions/*.md` |

**Recommendation for RaiSE:** Already ahead — skill-per-directory model
(`skill-name/SKILL.md`) is more granular than competitors.

### Pattern 5: Skill Sets as Named Concept (Market Gap)

No AI tool currently offers named, switchable instruction sets:

- Cursor: activation modes (always/glob/agent/manual) — not named sets
- Roo Code: mode-based directories — closest, but modes ≠ sets
- Continue: `uses:` blocks — compositional, not switchable sets
- Aider: `read:` array — file list, not a named concept

**This is a RaiSE differentiator.** The concept of "choose your skill set"
maps directly to team/org customization needs that no competitor addresses.

## Recommended Architecture

### Model: Oh My Zsh + Helm Hybrid

```
.raise/skills/
  default/                    ← builtin skill set (rai init creates this)
    rai-session-start/
      SKILL.md
    rai-story-run/
      SKILL.md
    ...
  my-company/                 ← team skill set (created by /rai-skill-create)
    rai-story-run/            ← overrides builtin version
      SKILL.md
    company-review/           ← team-specific skill (no builtin equivalent)
      SKILL.md

.claude/skills/               ← deployment target (derived, gitignored)
  rai-session-start/SKILL.md  ← from default (no override in my-company)
  rai-story-run/SKILL.md      ← from my-company (overrides default)
  company-review/SKILL.md     ← from my-company (no builtin equivalent)
```

### Deployment Logic (rai init)

```
1. Read --skill-set flag (default: "default")
2. Base layer: load .raise/skills/default/
3. Overlay: load .raise/skills/{set-name}/ (if != default)
4. Merge: same-name in overlay replaces base (no diff, full replace)
5. Deploy: write merged set to .claude/skills/
6. Manifest: track origin per skill (framework/project/overlay)
```

### First-Time Init

```
rai init --agent claude
  → Copies builtins to .raise/skills/default/
  → Deploys .raise/skills/default/ → .claude/skills/
  → Creates manifest with origin: "framework" for each
```

### Team Customization

```
# Tech lead creates team set
/rai-skill-create --set my-company

# Or manually
mkdir -p .raise/skills/my-company/rai-story-run/
cp .raise/skills/default/rai-story-run/SKILL.md .raise/skills/my-company/rai-story-run/
# Edit to customize
git add .raise/skills/my-company/ && git commit

# Team members
rai init --skill-set my-company
```

### Upgrade (new rai-cli version)

```
rai init --agent claude
  → Updates .raise/skills/default/ (three-hash: only untouched skills)
  → Re-deploys with current --skill-set overlay
  → Team customizations in their set are untouched
```

## Why This Works (Traced to Evidence)

| Design decision | Evidence |
|-----------------|----------|
| Directory separation | Oh My Zsh (175k stars), Cursor, all AI tools trending this way |
| Same-name override | Oh My Zsh, Helm, ESLint, Ansible — simplest, most battle-tested |
| Three-hash for default/ updates | Helm's --reset-then-reuse-values problem solved by our existing manifest |
| Named skill sets | Market gap (C5) — no AI tool has this concept |
| .raise/skills/ as source of truth | Git-versionable (team sharing), like Copilot's .github/instructions/ |
| .claude/skills/ as derived deployment | Separation of concern — like Helm's computed release values |

## Trade-offs

| Pro | Con |
|-----|-----|
| KISS — no merge, no inheritance | Full skill replacement (can't override just one section) |
| Git-native sharing | No registry (deferred to Pro/Enterprise) |
| Named sets = clear mental model | One more directory level to understand |
| Market differentiator | No prior art to validate the UX |

## What This Is NOT (YAGNI)

- **NOT a package registry** — skill sets are directories, not packages (Pro/Enterprise scope)
- **NOT inheritance** — no `extends:` mechanism, full replacement only
- **NOT per-section override** — whole-skill granularity, not partial
- **NOT multi-IDE aware** — deployment targets per agent come later

## Implementation Scope

| Story | Size | What |
|-------|------|------|
| A | S | `rai init` creates `.raise/skills/default/` from builtins |
| B | S | `rai init --skill-set X` deploys overlay merged with default |
| C | XS | Update `/rai-skill-create` to target `.raise/skills/{set}/` |

Estimated total: 1-2 days implementation.

## References

See `sources/evidence-catalog.md` for full source list with evidence levels.
