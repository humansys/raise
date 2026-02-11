# S14.4: Bootstrap on Init — Design Spec

---
id: S14.4
title: Bootstrap on Init
epic: E14
size: M
sp: 3
status: design
components: [onboarding/bootstrap, cli/commands/init, config/paths]
dependencies: [F14.1, F14.2, F14.3]
---

## What & Why

**Problem:** After `rai init`, `.raise/rai/` is empty — no identity, no patterns, no methodology. Users get a CLI but not Rai. The "reliable" promise depends entirely on user discipline until they manually set up Rai.

**Value:** New users get a capable AI partner from the first `rai init`. Base identity and universal patterns are available immediately, enabling skills and memory to function from day one.

## Approach

Add a bootstrap step to `rai init` that copies bundled base assets from the `raise_cli.rai_base` package to the project's `.raise/rai/` directory.

**Components affected:**

| Component | Change | Why |
|-----------|--------|-----|
| `onboarding/bootstrap.py` | **CREATE** | Bootstrap logic: resolve source, copy files |
| `cli/commands/init.py` | MODIFY | Call bootstrap after `save_manifest()` |
| `config/paths.py` | MODIFY | Add `get_identity_dir()` helper |

### Key Decisions

**1. How to read bundled files:** `importlib.resources.files()` (Python 3.9+). Returns a `Traversable` — use `.read_text()` for content, iterate subdirectories with `/` operator. No temp file extraction needed.

**2. Pattern merge strategy:** Copy entire `patterns-base.jsonl` to `.raise/rai/memory/patterns.jsonl` only if the target file doesn't exist. If it already exists, skip (don't merge). Rationale: merging requires deduplication by ID which is F14.6 (versioning) scope. For F&F, init happens once per project.

**3. Idempotency:** Per-file check. Each file is copied only if it doesn't exist at destination. This allows partial re-runs (e.g., if identity was copied but patterns weren't).

**4. Init flow insertion point:** After `save_manifest()` (line 218), before output messages (line 220). Bootstrap must create directories before printing "created" messages so we can include `.raise/rai/` in output.

**5. methodology.yaml:** Copy to `.raise/rai/framework/methodology.yaml` for F14.5 to consume later. Same idempotency: skip if exists.

## Examples

### CLI Usage

```bash
# First init — bootstrap copies base
$ raise init
Welcome to RaiSE!
...
Created: .raise/manifest.yaml
Created: .raise/rai/identity/       — Rai's base identity
Created: .raise/rai/memory/         — 20 universal patterns
Bootstrapped: Rai base v1.0.0

# Second init — bootstrap skips existing
$ raise init
...
Created: .raise/manifest.yaml
Loaded:  .raise/rai/                — Rai base already present
```

### API Usage (from init.py)

```python
from raise_cli.onboarding.bootstrap import bootstrap_rai_base

result = bootstrap_rai_base(project_path)
# result.identity_copied == True
# result.patterns_copied == True
# result.methodology_copied == True
# result.base_version == "1.0.0"
# result.already_existed == False
```

### Data Flow

```
importlib.resources.files("raise_cli.rai_base")
    ├── identity/core.md         → .raise/rai/identity/core.md
    ├── identity/perspective.md  → .raise/rai/identity/perspective.md
    ├── memory/patterns-base.jsonl → .raise/rai/memory/patterns.jsonl
    └── framework/methodology.yaml → .raise/rai/framework/methodology.yaml
```

### Result Model

```python
class BootstrapResult(BaseModel):
    """Result of base Rai bootstrap operation."""

    identity_copied: bool = False
    patterns_copied: bool = False
    methodology_copied: bool = False
    base_version: str = ""
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
```

### File System After Bootstrap

```
.raise/
├── manifest.yaml                  # Existing (save_manifest)
└── rai/
    ├── identity/
    │   ├── core.md                # ← Copied from rai_base
    │   └── perspective.md         # ← Copied from rai_base
    ├── memory/
    │   └── patterns.jsonl         # ← Copied from patterns-base.jsonl
    ├── framework/
    │   └── methodology.yaml       # ← Copied from rai_base
    └── personal/                  # Existing (F14.15, gitignored)
```

## Acceptance Criteria

**MUST:**
- `rai init` copies base identity (core.md, perspective.md) to `.raise/rai/identity/`
- `rai init` copies base patterns to `.raise/rai/memory/patterns.jsonl`
- `rai init` copies methodology.yaml to `.raise/rai/framework/`
- Existing files are never overwritten (idempotent)
- Bootstrap reports what was copied vs skipped
- Works on fresh project (no `.raise/` exists yet)

**SHOULD:**
- Include base version in result for future update detection
- Output message adapts to Shu/Ha/Ri experience level

**MUST NOT:**
- Overwrite existing identity, patterns, or methodology files
- Fail if `.raise/rai/` partially exists
- Import anything from `rai_base` at module level in init.py (lazy import for startup speed)
