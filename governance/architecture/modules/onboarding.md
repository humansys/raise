---
type: module
name: onboarding
purpose: "Project initialization, developer profile management, convention detection, and CLAUDE.md generation"
status: current
depends_on: [config, core, rai_base, skills_base]
depended_by: [cli]
entry_points:
  - "raise init"
  - "raise profile show"
public_api:
  - "detect_project_type"
  - "detect_conventions"
  - "generate_claude_md"
  - "generate_guardrails"
  - "load_developer_profile"
  - "save_developer_profile"
  - "DeveloperProfile"
  - "ProjectManifest"
components: 60
constraints:
  - "Must work on fresh repos with zero RaiSE artifacts"
  - "Convention detection is heuristic — confidence levels, not certainty"
  - "Profile lives in ~/.rai/developer.yaml, not in the project"
---

## Purpose

The onboarding module handles everything needed to get a developer or project started with RaiSE. It has three main responsibilities: **project initialization** (`raise init` — detect project type, generate guardrails, install skills, create CLAUDE.md), **developer profile** (manage `~/.rai/developer.yaml` with experience level, preferences, and session tracking), and **convention detection** (analyze existing code to infer naming, formatting, and structure conventions).

This is the largest module by component count (60) because it covers the entire first-use experience — from detecting "is this a Python project?" to generating a complete `CLAUDE.md` with project-specific rules.

## Architecture

```
raise init → detect_project_type() → DetectionResult
                ↓
           detect_conventions() → ConventionResult
                ↓
           generate_guardrails() → guardrails.md
                ↓
           install skills → .claude/skills/
                ↓
           generate_claude_md() → CLAUDE.md
                ↓
           bootstrap() → .raise/ directory structure
```

## Key Files

- **`detection.py`** — Project type detection (Python, TypeScript, monorepo, etc.) by analyzing file extensions and config files.
- **`conventions.py`** — Code convention detection: indentation, line length, quotes, naming patterns. Uses sampling and confidence scoring.
- **`governance.py`** — `GuardrailGenerator` creates project-specific `guardrails.md` from detected conventions.
- **`claudemd.py`** — `ClaudeMdGenerator` produces a complete `CLAUDE.md` from project analysis results.
- **`profile.py`** — `DeveloperProfile` Pydantic model with ShuHaRi experience levels, communication preferences, and session tracking.
- **`bootstrap.py`** — Creates `.raise/` directory structure and copies base content from `rai_base` and `skills_base`.
- **`skills.py`** — Copies distributable skills from `skills_base` package to `.claude/skills/`.
- **`manifest.py`** — `ProjectManifest` for tracking initialization state.
- **`memory_md.py`** — Generates `MEMORY.md` from accumulated patterns for system prompt context.
- **`migration.py`** — One-time migration utilities for profile data format changes.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Directory paths, settings |
| `core` | File operations, git utilities |
| `rai_base` | Base identity, patterns, and framework files to copy on init |
| `skills_base` | Distributable skills to install on init |

## Conventions

- Profile is global (per-developer, not per-project) at `~/.rai/developer.yaml`
- Convention detection uses sampling (not exhaustive scan) for performance
- Confidence levels: high (>80% agreement), medium (60-80%), low (<60%)
- CLAUDE.md generation is idempotent — running init again updates without data loss
