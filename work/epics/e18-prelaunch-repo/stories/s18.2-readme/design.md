# Design: S18.2 — README

> Lean spec — moderate breadth. Content rewrite, no source code changes.

## What & Why

**Problem:** Current README is 312 lines of internal developer documentation with GitLab URLs, branch model details, and repo structure. A visitor scanning for "should I try this?" bounces in 5 seconds.

**Value:** The README is the #1 conversion asset. A developer who finds RaiSE via PyPI, GitHub, or a blog post decides in 30 seconds: install or leave. Every line must earn its place.

## Approach: FastAPI/Ruff Pattern (D4)

The D4 decision (from E18 epic design, 7 exemplars analyzed) converged on:

```
1. Title + one-liner + badges         (2 seconds — "what is this?")
2. Code example / session transcript   (10 seconds — "what does it look like?")
3. Feature highlights                  (10 seconds — "what can it do?")
4. Quick start                         (5 seconds — "how do I try it?")
5. Community / links                   (3 seconds — "where do I go next?")
```

**Total: ~30 seconds to decision.**

### What Changes

| Section | Current | New |
|---------|---------|-----|
| Title + tagline | RaiSE + long description | RaiSE + one-liner + 3 badges |
| First visual | ASCII triad diagram | Session transcript (D8) |
| Quick start | 2 separate sections (PyPI + dev) | Single `pip install` + 3 commands |
| Features | Scattered across 8 sections | Consolidated feature grid |
| Skills list | Full 24-skill table | Collapsed — link to docs |
| Repo structure | Full tree | Removed (contributor docs) |
| Branch model | Full diagram | Removed (contributor docs) |
| Core concepts | Table + glossary link | Removed (docs site later) |
| Key principles | 5 principles listed | Woven into description |
| Status/feedback | GitLab URLs | GitHub URLs (placeholder until S18.3 confirms) |
| License | Apache-2.0 | Apache-2.0 (unchanged) |

### What Moves to CONTRIBUTING.md

- Development setup (clone, install dev deps)
- Branch model
- Repository structure details

## Session Transcript (D8)

D8 decided: session transcript over GIF (Claude Code is text-based). This is the "hero image" equivalent.

```
$ pip install rai-cli
$ cd your-project
$ rai init --detect
✓ Detected: Python 3.12, pytest, ruff, pyright
✓ Scaffolded .raise/ governance structure
✓ Built knowledge graph (47 components, 12 modules)

# Open Claude Code and start working
$ claude
> /rai-session-start

Session: 2026-02-12
Context: your-project, 47 components mapped
Focus: Ready for first story
Signals: None

Go.
```

## README Structure (Target)

```markdown
# RaiSE

**Reliable AI Software Engineering** — Governance that makes AI-assisted development actually reliable.

[![PyPI](badge)][pypi] [![Python](badge)][python] [![License](badge)][license]

---

## What does it look like?

[Session transcript — the "hero"]

## Why RaiSE?

[3-4 bullet problem/solution pairs]

## Features

[Feature grid — 4-6 items with emoji-free headers]

## Quick Start

[pip install + 3 commands, copy-paste ready]

## How It Works

[Brief lifecycle: session-start → story → session-close]

## Documentation

[Links to framework/, CONTRIBUTING, etc.]

## Community

[Contributing, Code of Conduct, Security, support channels]

## License

Apache-2.0
```

**Target length:** ~120-150 lines (vs current 312).

## Acceptance Criteria

**MUST:**
- [ ] Opens with title + one-liner + badges (PyPI version, Python, License)
- [ ] Session transcript within first scroll (no clicking needed)
- [ ] Quick start is copy-paste: 4 commands, works on clean environment
- [ ] No GitLab URLs anywhere
- [ ] No internal details (branch model, repo structure, full skill list)
- [ ] Links to CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG
- [ ] All existing tests still pass

**SHOULD:**
- [ ] Under 150 lines
- [ ] Each section earnable — remove if it doesn't convert
- [ ] GitHub URLs use placeholder `https://github.com/humansys-ai/raise-commons`

**MUST NOT:**
- [ ] Include GIF/video (text-based per D8)
- [ ] List all 24 skills (link instead)
- [ ] Include development setup (that's CONTRIBUTING.md)
- [ ] Use emojis in section headers

---

*Design created: 2026-02-12*
*Next: `/rai-story-plan`*
