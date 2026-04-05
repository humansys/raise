# RAISE-539: Analysis

## Method: Stack trace analysis

Traced from `_resolve_env` (line 57) through the data flow:

1. `rai mcp install --env "GITHUB_TOKEN=ghp_xxx"` or `--env "TOKEN,API_KEY=abc"`
2. `env.split(",")` in install/scaffold → `["GITHUB_TOKEN=ghp_xxx"]` (preserves `=value`)
3. Stored in `ServerConnection.env: list[str]` → model accepts any string, no validation
4. `_resolve_env` reads `config.server.env` as `env_names`
5. Uses as dict keys: `os.environ.get("GITHUB_TOKEN=ghp_xxx", "")` → returns `""` (no such env var)
6. Server subprocess receives empty value → fails

## Root Cause

`_resolve_env` assumes `ServerConnection.env` contains only environment variable **names**, but there is no validation at input time (install/scaffold) or resolution time. `KEY=VALUE` strings pass through silently and break at runtime.

## Fix Approach

Parse `KEY=VALUE` in `_resolve_env` — if an entry contains `=`, split on first `=` and use the value directly. If no `=`, look up from `os.environ` as today. This handles:
- Legacy configs that stored `KEY=VALUE` (tolerant read)
- New installs that pass `--env KEY=VALUE` (works immediately)
- Existing correct usage `--env KEY` (unchanged behavior)
