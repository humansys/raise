# Research: Skill/Template Distribution & Upgrade Strategies

**15-min overview for decision-makers.**

## Question

How should `rai init` update skill files when users upgrade `rai-cli`, without destroying customizations?

## Context

`rai-cli` distributes ~24 skill files (YAML frontmatter + Markdown body) to project directories. Today, `scaffold_skills()` skips existing files entirely — bug fixes and improvements never propagate after first `rai init`.

## Key Finding

**The dpkg three-hash algorithm** is the universal standard for this problem, validated across 5+ production ecosystems over 25+ years. Store the hash of what was distributed; compare against on-disk and new version to determine: auto-update (user didn't touch it), keep (upstream didn't change), or conflict (both changed).

## Recommendation

1. **SHA256 manifest** in `.raise/manifests/skills.json` — per-file hash + version
2. **dpkg detection** — three-hash comparison on each `rai init`
3. **Rails-style UX** — `--dry-run`, `--force`, `--skip` flags + interactive prompt for conflicts
4. **Default = keep** — protect user work, never overwrite without consent
5. **Non-TTY = skip** — CI-safe, explicit `--force` required for automation

## Confidence

HIGH — 6 triangulated claims, 50+ sources, zero disagreement on core model.

## Artifacts

| File | Content |
|------|---------|
| `sources/evidence-catalog.md` | 31 evidence entries across 4 domains |
| `synthesis.md` | 6 triangulated claims + patterns + gaps |
| `recommendation.md` | Architecture, trade-offs, risks, alternatives |

## Research Metadata

- **Tool:** Claude Opus 4.6 — 4 parallel research agents via WebSearch + WebFetch
- **Search date:** 2026-02-20
- **Prompt version:** 1.0
- **Researcher:** Rai (for Emilio Osorio)
- **Domains covered:** Scaffolding tools, plugin ecosystems, content hash strategies, DX patterns
- **Total sources:** 50+
- **Total agents:** 4 (parallel)
