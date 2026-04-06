# RAISE-605: Analysis

## Root Cause (XS — cause evident)

Two missing pieces:
1. **CLI** (`docs.py:67-129`): No `--parent` option. Metadata dict only gets `title` and `path`.
2. **Adapter** (`confluence_adapter.py:42-86`): `publish()` resolves parent exclusively from routing config (`routing.parent_title`). Never reads `metadata["parent_id"]`.

If no routing is configured for a doc_type, publish fails with "No routing configured" — there's no fallback to an explicit parent.

## Fix Approach

1. **CLI**: Add `--parent PAGE_ID` option to `publish` command. Pass as `metadata["parent_id"]`.
2. **Adapter**: If `metadata["parent_id"]` is set, use it directly (skip routing parent lookup). If not set, fall back to routing config as today. If neither exists, fail with clear error.

Priority chain: `metadata["parent_id"]` > `routing.parent_title` > error.

No protocol changes needed — `metadata: dict[str, Any]` is already flexible.
