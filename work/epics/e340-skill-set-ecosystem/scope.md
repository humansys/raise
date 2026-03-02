# Epic Scope: Skill Set Ecosystem

| Field | Value |
|-------|-------|
| ID | RAISE-340 |
| Branch | `epic/e340/skill-set-ecosystem` |
| Base | `dev` |
| Research | `work/research/skill-set-patterns/` |

## Strategic Objective

Enable team-level skill customization with named skill sets so teams can
maintain their own skill variants without losing changes on framework
upgrades. Market differentiator — no AI coding tool offers this.

## Value

After this epic, a tech lead can:
1. Run `rai init` → gets builtins in `.raise/skills/default/`
2. Create `.raise/skills/my-company/rai-story-run/SKILL.md` with custom steps
3. Run `rai init --skill-set my-company` → team gets customized story-run
4. Upgrade rai-cli → `default/` updates safely, `my-company/` untouched

## In Scope (MUST)

- `.raise/skills/default/` populated from builtins on `rai init`
- Three-hash upgrade on `.raise/skills/default/`
- `--skill-set` flag on `rai init` for overlay deployment
- Same-name-wins override (overlay replaces default, no merge)
- Manifest tracks `origin` per skill (framework vs project)
- `/rai-skill-create` targets `.raise/skills/{set}/`

## In Scope (SHOULD)

- "Customize builtin" mode in `/rai-skill-create` (copy from default as base)
- `rai skill scaffold --set` parameter

## Out of Scope

- Skill registry or package manager (Pro/Enterprise)
- Skill inheritance or `extends:` mechanism
- Per-section override (whole-skill granularity only)
- Remote skill set URLs
- Multi-IDE simultaneous deployment

## Architecture

### Model: Oh My Zsh + Helm Hybrid (Research-Grounded)

5 convergent patterns from 14 projects. See `work/research/skill-set-patterns/`.

### Directory Layout

```
.raise/skills/
  default/                    ← builtin set (rai init populates, three-hash managed)
    rai-session-start/
      SKILL.md
    rai-story-run/
      SKILL.md
    ...
  my-company/                 ← team set (user-owned, never auto-updated)
    rai-story-run/            ← overrides default (same-name wins)
      SKILL.md
    company-review/           ← team-only skill
      SKILL.md

.claude/skills/               ← deployment target (derived from merged set)
```

### Deployment Flow

```
rai init --skill-set <name>   (default: "default")

1. Builtins → .raise/skills/default/     (three-hash sync)
2. If skill-set != "default":
   Load default/ as base
   Load {set}/ as overlay
   Same-name in overlay replaces base
3. Deploy merged → .claude/skills/        (plugin transforms applied here)
4. Update manifest with origin per skill
```

### Key Decisions

| ID | Decision | Rationale | Evidence |
|----|----------|-----------|----------|
| D1 | Directory separation | Oh My Zsh (175k stars), all AI tools trending | C1 in evidence catalog |
| D2 | Same-name = full replacement | No merge complexity, most battle-tested | C2: Oh My Zsh, Helm, ESLint, Ansible |
| D3 | Three-hash only on default/ | Overlays are user-owned, never auto-updated | C3: universal across 14 projects |
| D4 | `--skill-set` flag (explicit) | No magic detection, clear mental model | C5: market gap |
| D5 | No registry | YAGNI for open core | Constraint from brief |
| D6 | Plugin transforms at deployment | Builtins stored raw, transforms per-agent | Gemba: `_apply_plugin_transform` |
| D7 | Path-based copy for overlay | `_copy_skill_tree` uses Traversable for bundled; need parallel for filesystem | Gemba: skills.py L104-157 |

## Stories

| ID | Story | Size | Description |
|----|-------|------|-------------|
| S340.1 | Populate default skill set | S | `scaffold_skills()` writes builtins to `.raise/skills/default/` then deploys to `.claude/skills/`. Three-hash applies to default set. Backward compat for existing projects. |
| S340.2 | Overlay deployment | M | `rai init --skill-set X` merges default + overlay → `.claude/skills/`. Same-name wins. Manifest tracks origin. New `_copy_skill_tree_path()` for filesystem overlay. |
| S340.3 | Skill creation targets sets | S | `/rai-skill-create` generates into `.raise/skills/{set}/`. `rai skill scaffold --set`. "Customize builtin" mode. |

## Done Criteria

- [ ] `rai init` populates `.raise/skills/default/` with 23 builtins
- [ ] `rai init --skill-set X` deploys merged default + overlay
- [ ] Three-hash upgrade works on `.raise/skills/default/`
- [ ] Same-name-wins override verified (overlay skill replaces default)
- [ ] `/rai-skill-create` generates into `.raise/skills/{set}/`
- [ ] Existing projects without `.raise/skills/default/` handle LEGACY gracefully
- [ ] All tests pass + new tests per story
- [ ] Retrospective complete

## Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Backward compat: existing `.claude/skills/` without `.raise/skills/default/` | High | Med | LEGACY detection: first run creates default/ from builtins, treats existing `.claude/skills/` as user-modified |
| Plugin transforms on two-hop path | Low | Med | D6: transforms at deployment only, builtins stored raw |
| `_copy_skill_tree` uses Traversable not Path | Med | Low | D7: new `_copy_skill_tree_path()` for overlay (filesystem Path source) |
