# Bug RAISE-396 — Scope

WHAT:      CI test stage fails with 43 ModuleNotFoundError on `mcp` module
WHEN:      Every pipeline run (MR to dev or direct commit to dev)
WHERE:     .gitlab-ci.yml:23 — `uv sync --extra dev` (missing `--extra mcp`)
EXPECTED:  Test stage installs all required deps and pytest collects successfully
Done when: CI test stage passes with `mcp` available; pytest collects all test files

## Analysis (XS — evident cause)

Root cause: `.gitlab-ci.yml` line 23 runs `uv sync --extra dev` but `mcp` is a
separate optional dependency group in `pyproject.toml`. The MCP bridge module
(`src/rai_cli/mcp/bridge.py`) does `from mcp import ClientSession, StdioServerParameters`
at module level, and nearly every test file transitively imports it.

Countermeasure: Add `--extra mcp` to the `uv sync` command in the test stage.
