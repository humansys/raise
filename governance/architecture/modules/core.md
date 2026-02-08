---
type: module
name: core
purpose: "Subprocess wrappers for git, ast-grep, and ripgrep — the foundation tools everything else builds on"
status: current
depends_on: []
depended_by: [governance, context, onboarding, telemetry]
entry_points: []
public_api:
  - "run_tool"
  - "check_tool"
  - "require_tool"
  - "git_root"
  - "git_branch"
  - "git_status"
  - "git_diff"
  - "rg_search"
  - "sg_search"
components: 18
constraints:
  - "No internal dependencies — leaf module"
  - "All external tool calls go through run_tool()"
---

## Purpose

The core module wraps external CLI tools (git, ripgrep, ast-grep) into typed Python functions. Instead of scattering `subprocess.run()` calls throughout the codebase, every module calls `run_tool()` or its specialized variants (`git_status()`, `rg_search()`, etc.), which return typed `ToolResult` objects with stdout, stderr, and return codes.

This matters because raise-cli is a **toolkit that orchestrates other tools** — it doesn't reimplement git or AST parsing. Core provides the bridge between Python and those external tools with consistent error handling.

## Key Files

- **`tools.py`** — All subprocess wrappers. `run_tool()` is the primitive; `git_*()` and `rg_search()`/`sg_search()` are higher-level wrappers returning typed results (`GitStatus`, `SearchMatch`).
- **`text.py`** — Text processing utilities including stopwords list for keyword extraction in the context graph.
- **`files.py`** — File operation helpers (read/write with encoding handling).

## Dependencies

None — this is a leaf module. It depends only on Python stdlib (`subprocess`, `pathlib`).

## Conventions

- All tool wrappers return Pydantic models, never raw strings or dicts
- Tool availability is checked via `check_tool()` before use
- `require_tool()` raises `ToolNotFoundError` if a tool is missing
- Git operations assume the working directory is inside a git repo
