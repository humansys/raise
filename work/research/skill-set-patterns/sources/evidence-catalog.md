# Evidence Catalog: Skill Set Patterns

> Research date: 2026-03-02
> Depth: Standard (14 projects, 30+ sources)
> Decision: Skill ecosystem architecture for RaiSE v2.2 open core

## Sources

| # | Project | Type | Evidence Level | Stars/Usage | Key Pattern |
|---|---------|------|---------------|-------------|-------------|
| 1 | ESLint | Primary | Very High | 27k stars, 79M/wk npm | `extends` + npm package = composable configs |
| 2 | Prettier | Primary | Very High | 51k stars, 55M/wk npm | No extends — manual spread. Opinionated = fewer knobs |
| 3 | Ansible | Primary | Very High | 66k stars | `defaults/` = lowest precedence. 22-level override chain |
| 4 | Terraform | Primary | Very High | 44k stars | Variables + defaults + wrapper module pattern |
| 5 | Helm | Primary | Very High | 59k stars, 75% K8s | `values.yaml` defaults + `-f custom.yaml` overlay |
| 6 | Oh My Zsh | Primary | Very High | 175k stars | `$ZSH_CUSTOM/` directory. Same-name = custom wins |
| 7 | Copier | Primary | Medium | 2.5k stars | Three-way merge via `.copier-answers.yml` |
| 8 | Cookiecutter | Primary | High | 22k stars | Replay only, no update/merge |
| 9 | Cursor | Primary | High | Market leader | `.cursor/rules/*.mdc` with activation modes |
| 10 | GitHub Copilot | Primary | Very High | Largest user base | `.github/instructions/` + path scoping |
| 11 | Roo Code | Primary | High | Fast growing | Mode-based directories `.roo/rules-{mode}/` |
| 12 | Aider | Primary | High | Leading CLI tool | `CONVENTIONS.md` via `read:` array |
| 13 | Continue.dev | Primary | Medium | Growing | Mission Control hub, `uses:` blocks |
| 14 | Windsurf | Primary | High | Enterprise focus | `.windsurf/rules/*.md`, 12k char limit |
| 15 | Cline | Primary | High | OSS leader | `.clinerules/` directory migration |

## Triangulated Claims

### C1: Structural separation between defaults and customizations (6+ sources)
ESLint (extends vs local), Helm (values.yaml vs -f), Oh My Zsh ($ZSH vs $ZSH_CUSTOM),
Ansible (defaults/ vs group_vars/), Terraform (variable defaults vs module params),
Cursor (user rules vs project rules). UNIVERSAL pattern.

### C2: Same-name override is the simplest conflict resolution (4 sources)
Oh My Zsh, Helm, ESLint, Ansible. When custom exists with same name, custom wins.
No merge, no diff, no conflict markers.

### C3: Updates must never touch user customizations (universal)
Oh My Zsh (omz update skips $ZSH_CUSTOM), Helm (--reset-then-reuse-values),
all AI tools (workspace rules are user-owned). ZERO exceptions found.

### C4: Directory-of-files replaces single-file (AI tools 2025-2026 trend)
Cursor (.cursorrules → .cursor/rules/), Cline (.clinerules → .clinerules/),
Windsurf (.windsurfrules → .windsurf/rules/), Copilot (single .md → instructions/).

### C5: No AI tool has explicit "skill sets" (market gap)
Closest: Roo Code modes, Continue uses: blocks, Cursor activation modes.
None offers "install skill-set-X as your base". Potential differentiator.

## Contrary Evidence

- Prettier explicitly rejects composition — "opinionated = fewer knobs"
  → Does not apply: skills ARE the opinionatedness layer
- Helm --reuse-values silently ignores new defaults on upgrade
  → Our three-hash manifest avoids this specific gotcha
- Copier three-way merge produces .rej files on conflict
  → Complexity not justified; same-name-wins is simpler
