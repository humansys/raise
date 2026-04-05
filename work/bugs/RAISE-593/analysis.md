# RAISE-593: Analysis

## Method: Stack trace analysis

Error path:
1. `rai backlog search "test" -a jira` → `resolve_adapter("jira")` in `_resolve.py`
2. `resolve_entrypoint()` calls `cls()` (JiraAdapter constructor)
3. Constructor calls `load_jira_config()` in `jira_config.py:108-111`
4. `config_path.exists()` → False → `raise FileNotFoundError("Jira config not found: {path}")`
5. Caught by `_resolve.py:88` generic `except Exception` → renders raw message

Current output:
```
Error: Failed to instantiate PM adapter 'jira': Jira config not found: /full/path/.raise/jira.yaml
```

## Root Cause

The generic `except Exception` handler in `resolve_entrypoint` (line 88-93) renders the raw exception message with no guidance. For `FileNotFoundError` specifically, the user needs to know *how* to create the config.

## Fix Approach

Catch `FileNotFoundError` separately in `resolve_entrypoint` and provide actionable guidance:
- What's missing (`.raise/jira.yaml`)
- How to fix it (`rai adapter-setup` or create manually)
- Keep the generic handler for other exceptions unchanged
