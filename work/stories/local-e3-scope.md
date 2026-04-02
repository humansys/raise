# LOCAL-E3: Limpiar entorno raise-cli

## User Story

**As a** raise-cli developer,
**I want** a clean dual-installation setup using only uv,
**So that** I have stable `rai` globally and dev `rai` in raise-commons without conflicts.

## Current State (the mess)

- conda base: raise-cli 2.2.3 editable **BROKEN** (ModuleNotFoundError)
- ~/.local/bin/rai: symlink → conda (broken)
- raise-pro 2.2.2 in conda (editable, likely broken)
- raise-commons .venv: raise-cli 2.4.0a2 (working, editable via `uv run`)
- No uv tools installed

## Target State

| Context | Command | Version | Source |
|---------|---------|---------|--------|
| Anywhere (default) | `rai` | 2.3.0 | PyPI via `uv tool install` |
| raise-commons only | `uv run rai` | 2.4.0a2 | Editable from source |

## In Scope

- Remove ~/.local/bin/rai symlink
- Uninstall raise-cli and raise-pro from conda
- Remove miniconda3 entirely
- Install raise-cli stable via `uv tool install raise-cli`
- Verify both paths work
- Document the setup for future reference

## Out of Scope

- raise-pro in global install (not on PyPI, not needed now)
- dev/stable switching mechanism (YAGNI — evaluate later)
- Changes to raise-commons repo code

## Done When

- `which rai` → `~/.local/bin/rai` (uv tool managed)
- `rai --version` → 2.3.0 (PyPI stable)
- `cd raise-commons && uv run rai --version` → 2.4.0a2 (dev)
- conda fully removed
- No broken symlinks
- Shell config cleaned (no conda init blocks)
