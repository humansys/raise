# Implementation Plan: RAISE-197 Multi-Agent Skill Distribution

## Overview
- **Story:** RAISE-197
- **Size:** L
- **Created:** 2026-02-18
- **Design:** `work/stories/raise-197-ide-standardization/design.md`

## Impact Analysis

**Files to modify (rename/refactor):**
- `src/rai_cli/config/ide.py` → `src/rai_cli/config/agents.py`
- `src/rai_cli/onboarding/claudemd.py` → `src/rai_cli/onboarding/instructions.py`
- `src/rai_cli/config/__init__.py` (re-exports)
- `src/rai_cli/onboarding/__init__.py` (re-exports)
- `src/rai_cli/cli/commands/init.py` (orchestrator)
- `src/rai_cli/onboarding/manifest.py` (schema change)
- `src/rai_cli/onboarding/skills.py` (AgentConfig)
- `src/rai_cli/onboarding/workflows.py` (AgentConfig)
- `src/rai_cli/skills/locator.py` (AgentConfig)
- `src/rai_cli/context/builder.py` (AgentConfig)

**Files to create:**
- `src/rai_cli/config/agent_registry.py` (YAML loader + registry)
- `src/rai_cli/config/agent_plugin.py` (Protocol + default impl)
- `src/rai_cli/agents/` (YAML configs directory, bundled in package)
- `src/rai_cli/agents/copilot_plugin.py` (CopilotPlugin)

**Test files to modify:**
- `tests/config/test_ide.py` → `tests/config/test_agents.py`
- `tests/onboarding/test_claudemd.py` → `tests/onboarding/test_instructions.py`
- `tests/onboarding/test_skills.py`
- `tests/onboarding/test_workflows.py`
- `tests/skills/test_locator.py`
- `tests/context/test_builder.py`

**Test files to create:**
- `tests/config/test_agent_registry.py`
- `tests/config/test_agent_plugin.py`
- `tests/agents/test_copilot_plugin.py`

## Tasks

### Task 1: Rename `ide.py` → `agents.py` + model rename
- **Description:** Rename file, rename `IdeConfig` → `AgentConfig`, `IdeType` → `BuiltinAgentType`, `IdeChoice` → `AgentChoice`, `IDE_CONFIGS` → `BUILTIN_AGENTS`, `get_ide_config` → `get_agent_config`. Add new fields (`name`, `detection_markers`, `plugin`). Update `skills_dir` to `str | None`. Keep backward compat aliases in old location.
- **Files:** `src/rai_cli/config/ide.py` → `src/rai_cli/config/agents.py`, `src/rai_cli/config/__init__.py`, `tests/config/test_ide.py` → `tests/config/test_agents.py`
- **TDD Cycle:** RED (test AgentConfig with 5 targets, new fields) → GREEN (implement model) → REFACTOR
- **Verification:** `uv run pytest tests/config/test_agents.py -v && uv run pyright src/rai_cli/config/agents.py`
- **Size:** M
- **Dependencies:** None

### Task 2: Update all import sites
- **Description:** Update every file that imports from `config.ide` or references `IdeConfig`/`IdeType`/`IdeChoice` to use new names from `config.agents`. This includes source files and test files. Keep old `config/ide.py` as a thin re-export shim for any external consumers.
- **Files:** All files from Impact Analysis (imports section)
- **TDD Cycle:** GREEN (mechanical find-replace) → Verify all tests still pass
- **Verification:** `uv run pytest --tb=short -q && uv run ruff check src/ tests/`
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Rename `claudemd.py` → `instructions.py`
- **Description:** Rename file, rename `ClaudeMdGenerator` → `InstructionsGenerator`, `generate_claude_md` → `generate_instructions`. Update all imports. Update `onboarding/__init__.py` re-exports.
- **Files:** `src/rai_cli/onboarding/claudemd.py` → `src/rai_cli/onboarding/instructions.py`, `src/rai_cli/onboarding/__init__.py`, `src/rai_cli/cli/commands/init.py`, `tests/onboarding/test_claudemd.py` → `tests/onboarding/test_instructions.py`
- **TDD Cycle:** GREEN (mechanical rename) → Verify all tests still pass
- **Verification:** `uv run pytest tests/onboarding/test_instructions.py -v && uv run pytest --tb=short -q`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: AgentPlugin protocol + default handler
- **Description:** Define `AgentPlugin` Protocol with 3 hooks (`transform_instructions`, `transform_skill`, `post_init`). Implement `DefaultAgentPlugin` that passes through unchanged. Write tests for protocol compliance.
- **Files:** Create `src/rai_cli/config/agent_plugin.py`, create `tests/config/test_agent_plugin.py`
- **TDD Cycle:** RED (test protocol methods, default pass-through) → GREEN (implement) → REFACTOR
- **Verification:** `uv run pytest tests/config/test_agent_plugin.py -v && uv run pyright src/rai_cli/config/agent_plugin.py`
- **Size:** S
- **Dependencies:** Task 1

### Task 5: YAML agent registry
- **Description:** Create `AgentRegistry` that loads agent configs from: (1) built-in YAML files bundled in package, (2) project `.raise/agents/*.yaml`, (3) user `~/.rai/agents/*.yaml`. Registry resolves plugin references and returns `AgentConfig` + `AgentPlugin` pairs. Create 5 built-in YAML configs.
- **Files:** Create `src/rai_cli/config/agent_registry.py`, create `src/rai_cli/agents/` with 5 YAML files (`claude.yaml`, `cursor.yaml`, `windsurf.yaml`, `copilot.yaml`, `antigravity.yaml`), create `tests/config/test_agent_registry.py`
- **TDD Cycle:** RED (test loading built-in, project, user YAML; test override precedence; test plugin resolution) → GREEN (implement) → REFACTOR
- **Verification:** `uv run pytest tests/config/test_agent_registry.py -v && uv run pyright src/rai_cli/config/agent_registry.py`
- **Size:** L
- **Dependencies:** Task 1, Task 4

### Task 6: CopilotPlugin implementation
- **Description:** Implement `CopilotPlugin` that transforms skill frontmatter (adds `tools`, `infer`, removes `license`/`compatibility`) and generates `.prompt.md` files in `post_init`. This validates the plugin protocol with a real use case.
- **Files:** Create `src/rai_cli/agents/copilot_plugin.py`, create `tests/agents/test_copilot_plugin.py`
- **TDD Cycle:** RED (test frontmatter transform, test prompt file generation) → GREEN (implement) → REFACTOR
- **Verification:** `uv run pytest tests/agents/test_copilot_plugin.py -v`
- **Size:** M
- **Dependencies:** Task 4

### Task 7: Wire `init` command to agent registry + detection
- **Description:** Refactor `init_command` to use `AgentRegistry` instead of `get_ide_config()`. Change `--ide` to `--agent` (keep `--ide` as deprecated alias). Implement `--detect` using `detect_agents()`. Support repeatable `--agent`. Wire plugin hooks into skill/workflow scaffolding. Generate AGENTS.md as bonus on `--detect`.
- **Files:** `src/rai_cli/cli/commands/init.py`, `src/rai_cli/onboarding/skills.py`, `src/rai_cli/onboarding/workflows.py`
- **TDD Cycle:** RED (test multi-agent init, test detection, test plugin wiring) → GREEN (implement) → REFACTOR
- **Verification:** `uv run pytest tests/cli/ tests/onboarding/ -v --tb=short && uv run pyright src/rai_cli/cli/commands/init.py`
- **Size:** L
- **Dependencies:** Task 3, Task 5, Task 6

### Task 8: Manifest schema migration
- **Description:** Change `IdeManifest` to `AgentsManifest` with `types: list[str]` (plural). Implement backward compat: read old `ide.type` (singular), write new `agents.types` (plural). Update tests.
- **Files:** `src/rai_cli/onboarding/manifest.py`, `tests/onboarding/test_manifest.py`
- **TDD Cycle:** RED (test old schema reads correctly, test new schema writes) → GREEN (implement) → REFACTOR
- **Verification:** `uv run pytest tests/onboarding/test_manifest.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 9: Full quality gate
- **Description:** Run full test suite, ruff, pyright. Fix any regressions from the rename chain. Verify no stale references to old names (`IdeConfig`, `claudemd`, `generate_claude_md`).
- **Files:** All
- **Verification:** `uv run pytest --tb=short && uv run ruff check src/ tests/ && uv run pyright src/ && grep -ri "IdeConfig\|claudemd\|generate_claude_md" src/ tests/ --include="*.py" | grep -v "__pycache__" | grep -v "\.pyc"`
- **Size:** M
- **Dependencies:** Task 7, Task 8

### Task 10 (Final): Manual Integration Test
- **Description:** Validate end-to-end by running `rai init --detect` on a test project with multiple IDE markers. Verify instructions, skills, and workflows are generated for each detected agent. Test `rai init --agent copilot` specifically to validate plugin hooks. Test user-defined YAML in `~/.rai/agents/`.
- **Verification:** Demo working interactively — show generated files for each agent
- **Size:** S
- **Dependencies:** Task 9

## Execution Order

```
Task 1: AgentConfig model (foundation)
  ├── Task 2: Update imports (depends on 1)
  │     └── Task 3: Rename claudemd.py (depends on 2)
  ├── Task 4: AgentPlugin protocol (depends on 1)
  │     ├── Task 5: YAML registry (depends on 1, 4)
  │     └── Task 6: CopilotPlugin (depends on 4)
  └── Task 8: Manifest migration (depends on 1)

Task 7: Wire init command (depends on 3, 5, 6) ← convergence point
Task 9: Quality gate (depends on 7, 8)
Task 10: Integration test (depends on 9)
```

**Parallelizable:** Tasks 4+8 can run parallel to Tasks 2+3. Tasks 5+6 can run parallel once Task 4 is done.

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rename long tail (PAT-E-151) | Stale references break imports | Task 9 includes grep for old names |
| Plugin protocol too rigid/loose | Third-party adoption friction | Validate with CopilotPlugin (real case) before freezing |
| YAML loading edge cases | Missing files, bad YAML, circular plugins | Defensive loading with clear error messages in Task 5 |
| Backward compat break | Existing `rai init` users break | Task 8 reads old format; `--ide` alias preserved |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1 | M | 45 min | -- | |
| 2 | M | 30 min | -- | Mechanical |
| 3 | S | 20 min | -- | Mechanical |
| 4 | S | 20 min | -- | |
| 5 | L | 60 min | -- | Riskiest task |
| 6 | M | 30 min | -- | Validates protocol |
| 7 | L | 60 min | -- | Convergence point |
| 8 | S | 20 min | -- | |
| 9 | M | 30 min | -- | Cleanup |
| 10 | S | 15 min | -- | |
| **Total** | **L** | **~330 min** | -- | |
