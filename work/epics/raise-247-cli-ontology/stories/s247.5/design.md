---
story_id: "S247.5"
title: "Merge publish+release, flatten singletons"
epic_ref: "E247"
jira: "RAISE-254"
size: "S"
phase: "design"
created: "2026-02-23"
---

# Design: Merge publish+release, flatten singletons

## 1. What & Why

**Problem:** The CLI has two overlapping release groups (`publish` with check+release, `release` with list) and two singleton wrappers (`base show`, `profile show`) that add namespace depth without value.

**Value:** Clean taxonomy where release management lives in one group and top-level commands don't require unnecessary subcommands. Completes M2 (Clean Taxonomy) milestone.

## 2. Approach

Three independent changes, all in `cli/commands/` + `cli/main.py`:

1. **Merge publish → release:** Move `publish check` and `publish release` into `release.py` as `release check` and `release publish`. The existing `release list` stays. `publish.py` becomes a deprecation shim (like `memory.py` after S1-S3).
2. **Flatten base → info:** Move `base show` logic into a new top-level `rai info` command (registered via `app.command("info")`). `base.py` becomes a deprecation shim.
3. **Flatten profile:** Change `profile_app` from `no_args_is_help=True` to `invoke_without_command=True` with a callback that runs `show` logic. `rai profile show` still works. No shim needed — same group, just callable without subcommand.

**Pattern:** Same deprecation shim pattern from S1-S3 (`_deprecation_warning` + lazy import + delegate).

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `cli/commands/publish.py` | `publish_app` with `check`, `release` commands | Becomes deprecation shim. Commands move to `release.py`. | Private helpers `_find_project_paths`, `_read_current_version`, `_display_results` move with commands. |
| `cli/commands/release.py` | `release_app` with `list` command | Absorbs `check` + `publish` (renamed from `release`) commands | `list` unchanged |
| `cli/commands/base.py` | `base_app` with `show` command | Becomes deprecation shim. Logic moves to top-level `info` command. | — |
| `cli/commands/profile.py` | `profile_app` with `show` command, `no_args_is_help=True` | `invoke_without_command=True` + callback runs show logic | `show` subcommand still works |
| `cli/main.py` | Registers all groups | Add `app.command("info")`, keep `base`/`publish` as shims | Other registrations unchanged |

## 4. Target Interfaces

### New/Modified Commands

```python
# release.py — absorbs publish commands
@release_app.command("check")
def check_command(project: Path = Path(".")) -> None: ...

@release_app.command("publish")  # was "publish release"
def publish_command(bump: BumpType | None = None, version: str | None = None,
                    dry_run: bool = False, skip_check: bool = False,
                    project: Path = Path(".")) -> None: ...

# main.py — new top-level command
@app.command("info")
def info_command() -> None: ...  # moved from base.show

# profile.py — invoke_without_command
@profile_app.callback(invoke_without_command=True)
def profile_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        show()  # default behavior
```

### Deprecation Shims

```python
# publish.py — shim only
@publish_app.command("check")
def check_shim(project: Path = Path(".")) -> None:
    _deprecation_warning("publish check", "release check")
    from rai_cli.cli.commands.release import check_command
    check_command(project=project)

@publish_app.command("release")
def release_shim(...) -> None:
    _deprecation_warning("publish release", "release publish")
    from rai_cli.cli.commands.release import publish_command
    publish_command(...)

# base.py — shim only
@base_app.command()
def show() -> None:
    _deprecation_warning("base show", "info")
    from rai_cli.cli.commands.main_commands import info_command
    info_command()
```

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **MUST:** Backward-compat aliases print deprecation to stderr + delegate (same pattern as S1-S3)
- **MUST:** `rai release check|publish|list` all work
- **MUST:** `rai info` works as top-level command
- **MUST:** `rai profile` (no subcommand) shows profile
- **MUST NOT:** Break existing `rai publish check` or `rai publish release` invocations
- **PAT-E-444:** No tests for CLI plumbing/shims — test domain logic only
