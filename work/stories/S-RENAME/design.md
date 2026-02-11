---
story_id: S-RENAME
title: "Rename raise command to rai, raise-cli package to rai-cli"
complexity: moderate
estimated_sp: 5
---

## What & Why

**Problem:** The CLI command is `rai` and the package is `rai-cli`, but we decided on `rai` as the command name and `rai-cli` as the package (SES-137). The word "raise" in the CLI context conflicts with Python's `rai` keyword and doesn't distinguish between RaiSE-the-framework and the tool you type in the terminal.

**Value:** After this rename, `rai --help` works, `pip install rai-cli` installs the right thing, and the codebase consistently uses `rai`/`rai-cli` for the tool while preserving "RaiSE" for the methodology/framework.

## Naming Distinction (CRITICAL)

This is the core design decision — what changes vs. what stays:

| Concept | Current | After | Rule |
|---------|---------|-------|------|
| **CLI command** | `rai` | `rai` | **RENAME** |
| **Python package name** | `rai-cli` | `rai-cli` | **RENAME** |
| **Python module** | `rai_cli` | `rai_cli` | **RENAME** (directory + all imports) |
| **Environment vars** | `RAISE_*` | `RAI_*` | **RENAME** (already have `RAI_HOME`) |
| **TOML table** | `[tool.raise]` | `[tool.rai]` | **RENAME** |
| **XDG dirs** | `~/.config/raise/` | `~/.config/rai/` | **RENAME** |
| **Project dir** | `.raise/` | `.raise/` | **NO CHANGE** — framework marker |
| **Framework name** | RaiSE | RaiSE | **NO CHANGE** — methodology name |
| **`RAISE_PROJECT_DIR`** | `".raise"` | `".raise"` | **NO CHANGE** — refers to the `.raise/` dir |
| **`RaiseError`** | `RaiseError` | `RaiError` | **RENAME** — it's the CLI's error class |
| **`RaiseSettings`** | `RaiseSettings` | `RaiSettings` | **RENAME** |
| **`RAISE_SKILL_NAME`** env** | `RAISE_SKILL_NAME` | Keep | **ASSESS** — used in skill scripts |
| **Doc references to "RaiSE CLI"** | "RaiSE CLI" | "RaiSE CLI" | **NO CHANGE** — framework's CLI |
| **Doc references to `` `rai` `` command** | `` `rai` `` | `` `rai` `` | **RENAME** |

### Disambiguation Heuristic

When reviewing each occurrence of "raise" in the codebase:

1. **Is it the Python keyword `rai`?** → NO CHANGE
2. **Does it refer to the framework/methodology ("RaiSE")?** → NO CHANGE
3. **Is it the `.raise/` directory name?** → NO CHANGE (framework marker, not CLI)
4. **Is it the CLI command you type in a terminal (`rai memory`, `rai session`)?** → RENAME to `rai`
5. **Is it the Python package/module (`rai_cli`, `rai-cli`, `from raise_cli`)?** → RENAME to `rai_cli`/`rai-cli`
6. **Is it a class/variable derived from the CLI identity (`RaiseError`, `RaiseSettings`, `RAISE_` env prefix)?** → RENAME to `Rai*`/`RAI_*`
7. **Is it an XDG path (`~/.config/raise/`)?** → RENAME to `~/.config/rai/`

## Components Affected

| Component | Change Type | Ref Count | Risk |
|-----------|-------------|-----------|------|
| `src/rai_cli/` → `src/rai_cli/` | **Directory rename** | ~78 files | HIGH — all imports break |
| `pyproject.toml` | Modify | 1 file, ~10 refs | HIGH — package identity |
| All Python imports (`from raise_cli...`) | Modify | ~78 files | HIGH — mechanical but many |
| All test files (`from raise_cli...`) | Modify | ~30 files | MEDIUM |
| Entry point (`rai` → `rai`) | Modify | 1 | LOW |
| `RaiseError` → `RaiError` | Modify | ~15 refs | MEDIUM |
| `RaiseSettings` → `RaiSettings` | Modify | ~10 refs | MEDIUM |
| `RAISE_` env prefix → `RAI_` | Modify | ~5 refs | LOW |
| TOML table `[tool.raise]` → `[tool.rai]` | Modify | ~3 refs | LOW |
| XDG paths `rai` → `rai` | Modify | ~3 refs | LOW |
| Skills (`.md` files with `rai` CLI refs) | Modify | ~15 files | LOW |
| Docs/ADRs with `rai` CLI refs | Modify | ~50+ files | LOW |
| `uv.lock` | Regenerate | 1 | LOW |

## Approach

**Strategy: Inside-out rename in 4 layers**

1. **Layer 1 — Package identity:** `pyproject.toml` (name, entry point, tool config, hatch build paths)
2. **Layer 2 — Module rename:** `src/rai_cli/` → `src/rai_cli/` (directory move + all internal imports)
3. **Layer 3 — Symbol rename:** `RaiseError` → `RaiError`, `RaiseSettings` → `RaiSettings`, env prefix
4. **Layer 4 — External references:** Tests, skills, docs, config files, CLAUDE.md

Each layer is validated before proceeding to the next: tests must pass after layer 2+3 before touching layer 4.

**IMPORTANT:** The `.raise/` directory and `RAISE_PROJECT_DIR` constant stay unchanged — they refer to the framework's project presence, not the CLI command.

## Examples

### Before
```bash
rai memory build
rai session start --context
rai discover scan
pip install raise-cli
```

### After
```bash
rai memory build
rai session start --context
rai discover scan
pip install rai-cli
```

### Import Before
```python
from raise_cli.config import RaiseSettings
from raise_cli.exceptions import RaiseError
```

### Import After
```python
from rai_cli.config import RaiSettings
from rai_cli.exceptions import RaiError
```

### Config Before
```toml
[tool.raise]
output_format = "human"
```

### Config After
```toml
[tool.rai]
output_format = "human"
```

## Acceptance Criteria

**MUST:**
- [ ] `rai --help` works
- [ ] `rai --version` shows `rai-cli version X.Y.Z`
- [ ] All imports use `rai_cli` module
- [ ] `RaiseError` → `RaiError`, `RaiseSettings` → `RaiSettings`
- [ ] Environment variables use `RAI_` prefix
- [ ] All tests pass with >90% coverage
- [ ] Pyright strict passes
- [ ] Ruff passes
- [ ] `.raise/` directory name unchanged

**MUST NOT:**
- Rename "RaiSE" (framework name) to anything else
- Rename `.raise/` project directory
- Change `RAISE_PROJECT_DIR` constant value (it holds `".raise"`)
- Make any functional changes — purely mechanical rename
- Break backward compatibility of `.raise/` directory detection

**SHOULD:**
- Update skill `.md` files that reference `rai` CLI command
- Update docs/ADRs that reference `rai` as CLI command
