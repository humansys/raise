# F128.1: IDE Configuration Model — Design

## What & Why

**Problem:** All IDE-specific paths are hardcoded to Claude Code across 6 files. There's no data model to represent IDE conventions, making multi-IDE support impossible.

**Value:** Foundation for the entire RAISE-128 epic. Once IdeConfig exists, F128.2-F128.4 have a clean abstraction to consume.

## Architectural Context

- **Module:** `mod-config` (bc-shared-kernel, lyr-leaf)
- **New file:** `src/rai_cli/config/ide.py`
- **Modified:** `src/rai_cli/onboarding/manifest.py` (schema extension)
- **Pattern:** Follows existing Pydantic BaseModel convention (guardrail-must-arch-002)
- **ADR:** ADR-031 (IdeConfig dataclass + factory — adapted to Pydantic per guardrails)

## Approach

Create `IdeConfig` as a Pydantic BaseModel with relative paths per IDE convention. Factory function maps `IdeType` to pre-built configs. Manifest gets an `ide` section to persist the choice. `claude` is default everywhere — backward compatible.

**Components:**

| Component | File | Change |
|-----------|------|--------|
| `IdeType` literal | `config/ide.py` | Create |
| `IdeConfig` model | `config/ide.py` | Create |
| `get_ide_config()` factory | `config/ide.py` | Create |
| `IDE_CONFIGS` registry | `config/ide.py` | Create |
| `IdeManifest` model | `onboarding/manifest.py` | Create |
| `ProjectManifest.ide` field | `onboarding/manifest.py` | Modify |

## Examples

### IdeType and IdeConfig

```python
from typing import Literal
from pydantic import BaseModel

IdeType = Literal["claude", "antigravity"]

class IdeConfig(BaseModel):
    ide_type: IdeType
    skills_dir: str          # relative to project root
    instructions_file: str   # relative to project root
    workflows_dir: str | None = None

# Pre-built configs
IDE_CONFIGS: dict[IdeType, IdeConfig] = {
    "claude": IdeConfig(
        ide_type="claude",
        skills_dir=".claude/skills",
        instructions_file="CLAUDE.md",
        workflows_dir=None,
    ),
    "antigravity": IdeConfig(
        ide_type="antigravity",
        skills_dir=".agent/skills",
        instructions_file=".agent/rules/raise.md",
        workflows_dir=".agent/workflows",
    ),
}
```

### Factory Function

```python
def get_ide_config(ide_type: IdeType = "claude") -> IdeConfig:
    return IDE_CONFIGS[ide_type]

# Usage
config = get_ide_config("antigravity")
assert config.skills_dir == ".agent/skills"
assert config.instructions_file == ".agent/rules/raise.md"
assert config.workflows_dir == ".agent/workflows"

config = get_ide_config()  # defaults to claude
assert config.skills_dir == ".claude/skills"
```

### Manifest Extension

```python
class IdeManifest(BaseModel):
    type: IdeType = "claude"

class ProjectManifest(BaseModel):
    version: str = "1.0"
    project: ProjectInfo
    branches: BranchConfig = Field(default_factory=BranchConfig)
    ide: IdeManifest = Field(default_factory=IdeManifest)
```

```yaml
# .raise/manifest.yaml — existing projects (no ide key) default to claude
version: '1.0'
project:
  name: my-project
  project_type: brownfield
branches:
  development: main

# .raise/manifest.yaml — after rai init --ide antigravity
version: '1.0'
project:
  name: my-project
  project_type: brownfield
branches:
  development: main
ide:
  type: antigravity
```

## Acceptance Criteria

**MUST:**
- `IdeType` is `Literal["claude", "antigravity"]`
- `IdeConfig` is Pydantic BaseModel with `ide_type`, `skills_dir`, `instructions_file`, `workflows_dir`
- `get_ide_config()` returns correct config for both IDE types
- `get_ide_config()` defaults to `"claude"` when called with no args
- `ProjectManifest` accepts optional `ide` field, defaults to `claude`
- Existing manifests without `ide` field load without error (backward compat)

**SHOULD:**
- `IdeConfig` is frozen (immutable after creation)
- `config/ide.py` exports via `config/__init__.py`

**MUST NOT:**
- Touch any of the 6 coupling point files (that's F128.2)
- Change behavior of any existing CLI command
- Add CLI flags (that's F128.4)
