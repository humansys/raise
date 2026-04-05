# RAISE-1301: Scope

WHAT:      `rai docs search` reportedly fails with "Missing space_key" on multi-instance confluence.yaml
WHEN:      Multi-instance confluence.yaml format used
WHERE:     packages/raise-cli/src/raise_cli/adapters/confluence_adapter.py (constructor)
EXPECTED:  CLI resolves space_key from instances.{name}.space_key via ConfluenceConfig.from_dict()
Done when: Verified not reproducible, bug closed

## Investigation

Cannot reproduce. The adapter constructor calls:
1. `load_confluence_config(root)` → `ConfluenceConfig.from_dict(data)`
2. `from_dict()` detects multi-instance format (has "instances" key) and uses `model_validate(data)`
3. `get_instance()` returns the default instance with correct `space_key`

Tested with both multi-instance and flat formats — both work correctly.

The error message in the bug ("Missing 'space_key' in .raise/confluence.yaml and CONFLUENCE_SPACE_KEY env var not set") does not exist anywhere in the codebase. `CONFLUENCE_SPACE_KEY` env var is never referenced.

The `from_dict` normalization was added in 06348fd6 (2026-03-29), 6 days before the bug was filed (2026-04-04).

## Resolution
**Cannot reproduce.** The multi-instance format is correctly handled by `ConfluenceConfig.from_dict()` → `model_validate()`. The bug was likely observed on an older version or with a different config file state. Closing as resolved.
