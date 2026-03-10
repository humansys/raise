# E476: Skillset Evolution — Design

## Architecture Approach

**Key insight:** The indirection mechanism already exists. Manifest has `project.test_command`,
`project.lint_command`, `project.type_check_command`. Five skills already use it. The work is
closing the gaps — not building something new.

## Target Components

### 1. Builtin Gates (S476.1)
**Current:** `src/raise_cli/gates/builtin/{tests,lint,types,coverage}.py` hardcode subprocess commands.
**Target:** Each gate reads manifest first, falls back to current default.

```python
# Pattern for each gate:
def _get_command(self, context: GateContext) -> list[str]:
    manifest = load_manifest(context.working_dir)
    if manifest and manifest.project:
        cmd = manifest.project.test_command  # or lint_command, type_check_command
        if cmd:
            return shlex.split(cmd)
    return ["pytest", "-x", "--tb=short"]  # hardcoded default preserved
```

### 2. Skill Markdown (S476.2)
**Current:** `rai-story-implement`, `rai-story-plan`, `rai-bugfix` hardcode `pytest`, `ruff check`, `pyright`.
**Target:** Use the same pattern as `rai-story-review` and `rai-story-close`:

```markdown
### Verification
1. Check `.raise/manifest.yaml` for `project.test_command`, `project.lint_command`, `project.type_check_command`
2. If not found, detect language from `project.project_type` or file extensions
3. Use language-appropriate defaults
```

### 3. Skillsets (S476.3, S476.4)
**Current:** No skill sets exist. System supports create/list/diff.
**Target:** `raise-dev` skillset with Python-specific skill overlays.

Structure:
```
.raise/skills/raise-dev/
  rai-story-implement/SKILL.md   # Python-specific verification section
  rai-bugfix/SKILL.md            # Python-specific fix verification
  rai-story-plan/SKILL.md        # Python-specific task verification
```

Each overlay replaces only the verification sections with explicit Python commands,
while the base skill remains language-agnostic.

## Key Contracts

1. **Manifest is the single source of truth** for tool commands
2. **Graceful degradation** — missing manifest → language detection → hardcoded defaults
3. **Backwards compatible** — no manifest change required for existing Python users
4. **Skillset overlays** are optional — base skills work without them

## Manifest Schema (existing, no changes needed)

```yaml
project:
  test_command: "uv run pytest --tb=short"
  lint_command: "uv run ruff check"
  type_check_command: "uv run pyright"
  project_type: python  # or typescript, go, etc.
```
