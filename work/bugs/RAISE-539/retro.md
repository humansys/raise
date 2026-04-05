# Retrospective: RAISE-539

## Summary
- Root cause: `_resolve_env` used `KEY=VALUE` strings as `os.environ` lookup keys instead of parsing the inline value
- Fix approach: Split on first `=` — inline values used directly, key-only entries read from environ
- Classification: Interface/S2-Medium/Code/Incorrect

## Process Improvement
**Prevention:** When a CLI flag accepts a string that could be either a name or a key-value pair, parse both formats at the boundary (input time) and validate. Don't defer interpretation to a downstream function that assumes one format.
**Pattern:** Interface + Code + Incorrect → input format ambiguity passed through without parsing at boundary.

## Heutagogical Checkpoint
1. Learned: `_resolve_env` merges `os.environ` with resolved entries — full parent env is always inherited. `env` list adds/overrides on top.
2. Process change: CLI `--env` help text should document both `KEY` and `KEY=VALUE` formats explicitly.
3. Framework improvement: `ServerConnection.env: list[str]` is ambiguous. Future: `dict[str, str | None]` where None = read from environ.
4. Capability gained: Full MCP config lifecycle understanding: install → YAML → health/call resolution.

## Patterns
- Added: PAT-E-727 (MCP env KEY=VALUE parsing)
- Reinforced: none evaluated
