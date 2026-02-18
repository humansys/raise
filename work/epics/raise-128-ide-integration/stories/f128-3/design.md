---
story_id: "F128.3"
title: "Antigravity Scaffolding"
epic_ref: "RAISE-128 IDE Integration"
story_points: 3
complexity: "simple"
status: "draft"
version: "1.0"
created: "2026-02-18"
updated: "2026-02-18"
template: "lean-feature-spec-v2"
---

# Feature: Antigravity Scaffolding

> **Epic**: RAISE-128 - IDE Integration
> **Complexity**: simple | **SP**: 3

---

## 1. What & Why

**Problem**: When `rai init` runs with an Antigravity IDE config, skills scaffold correctly (F128.2), but there's no way to generate workflow shim files (`.agent/workflows/*.md`). Antigravity uses workflows as user-triggered entry points — without them, skills exist but users can't invoke them.

**Value**: After this, a `scaffold_workflows()` function exists that generates one workflow file per distributable skill. F128.4 will wire this into `rai init --ide antigravity` for a complete Antigravity project setup.

---

## 2. Approach

Create a single new function `scaffold_workflows()` in `onboarding/workflows.py` that iterates over `DISTRIBUTABLE_SKILLS`, reads each skill's YAML frontmatter (name + description), and writes a workflow shim file to `{project_root}/.agent/workflows/{skill_name}.md`.

**Components affected**:
- **`onboarding/workflows.py`** (create): New module with `scaffold_workflows()` function
- **`tests/onboarding/test_workflows.py`** (create): Tests for workflow scaffolding

**Architectural context**:
- `mod-onboarding` (lyr-integration) — this is where scaffolding functions live
- Follows same pattern as `scaffold_skills()`: accepts `project_root` + `ide_config`, returns a result model
- Skips workflow generation when `ide_config.workflows_dir` is `None` (Claude has no workflows)

**What's NOT in scope**:
- `init.py` orchestration changes → F128.4
- Instructions file writing to `.agent/rules/raise.md` → F128.4 (the content function exists; the path wiring is in init.py)

---

## 3. Interface / Examples

### API Usage — scaffold_workflows

```python
from rai_cli.onboarding.workflows import scaffold_workflows
from rai_cli.config.ide import get_ide_config

# Antigravity — generates workflow files
config = get_ide_config("antigravity")
result = scaffold_workflows(project_root=Path("/home/user/project"), ide_config=config)
# => WorkflowScaffoldResult(workflows_created=22, already_existed=False)
# Creates: .agent/workflows/rai-session-start.md, rai-session-close.md, ...

# Claude — no-op (workflows_dir is None)
config = get_ide_config("claude")
result = scaffold_workflows(project_root=Path("/home/user/project"), ide_config=config)
# => WorkflowScaffoldResult(workflows_created=0, already_existed=False, skipped_no_workflows_dir=True)
```

### Generated Workflow File — `.agent/workflows/rai-session-start.md`

```markdown
---
name: rai-session-start
description: >
  Begin a session by loading context bundle, interpreting it, and proposing work.
  CLI does all data plumbing; skill does inference interpretation.
---

Run the `rai-session-start` skill from `.agent/skills/rai-session-start/SKILL.md`.
```

### Data Structures

```python
class WorkflowScaffoldResult(BaseModel):
    """Result of workflow scaffolding operation."""
    workflows_created: int = 0
    already_existed: bool = False
    skipped_no_workflows_dir: bool = False
    files_created: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `scaffold_workflows()` generates one `.md` file per distributable skill in `{workflows_dir}/`
- [ ] Each workflow file has YAML frontmatter with `name` and `description` from the skill's SKILL.md
- [ ] Returns `WorkflowScaffoldResult` with counts and file lists
- [ ] No-op when `ide_config.workflows_dir` is `None` (Claude Code)
- [ ] Per-file idempotency: existing workflow files are never overwritten (same pattern as `scaffold_skills`)

### Should Have

- [ ] Workflow files are minimal — frontmatter + one-line reference to the skill

### Must NOT

- [ ] **MUST NOT** modify `init.py` — that's F128.4
- [ ] **MUST NOT** change existing `scaffold_skills()` behavior
- [ ] **MUST NOT** add CLI flags — that's F128.4

---

## References

**Related ADRs**:
- ADR-031: IdeConfig pattern

**Related Features**:
- F128.1: IDE Configuration Model (Done)
- F128.2: Decouple Init from Claude Paths (Done)
- F128.4: Init --ide Flag + E2E Tests (next — consumes this)

**Dependencies**:
- F128.2 complete (provides decoupled `scaffold_skills()` and `IdeConfig` threading)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-18
