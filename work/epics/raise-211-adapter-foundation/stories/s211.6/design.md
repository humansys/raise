---
story_id: "S211.6"
title: "rai adapters list/check"
epic_ref: "E211"
size: "S"
phase: "design"
created: "2026-02-23"
---

# Design: rai adapters list/check

## 1. What & Why

**Problem:** Installed adapters are invisible. A developer who `pip install raise-pro` has no way to verify which adapters registered, whether they loaded correctly, or if they satisfy their Protocol contracts.

**Value:** `rai adapters list` shows what's installed. `rai adapters check` validates it works. Together they close the feedback loop for the plugin architecture built in S211.0–S211.5.

## 2. Approach

Two subcommands under a new `rai adapters` command group:

- **`list`** — Iterates all 5 entry point groups, calls registry `_discover()` for each, displays a table with group name, adapter name, source package, and current tier.
- **`check`** — Same iteration but also performs `isinstance()` against the corresponding `@runtime_checkable` Protocol. Reports pass/fail per adapter.

Both support `--format human|json` (project convention from `skill` and `discover` commands).

**Components:**
- **Create:** `src/rai_cli/cli/commands/adapters.py` — Typer command group + `ADAPTER_GROUPS` mapping
- **Create:** `src/rai_cli/output/formatters/adapters.py` — human/json formatters
- **Modify:** `src/rai_cli/cli/main.py` — register `adapters_app`

## 3. Gemba: Current State

- `adapters/registry.py` — 5 `get_*()` functions wrapping `_discover(group)`. `_dist_name(ep)` extracts package name. No group→Protocol mapping exposed.
- `adapters/protocols.py` — 5 `@runtime_checkable` Protocols.
- `tier/context.py` — `TierContext.from_manifest()` for tier display.
- `cli/main.py` — 9 command groups registered via `app.add_typer()`.
- `cli/commands/skill.py` — reference pattern: `skill_app`, `--format` option, formatters in `output/formatters/skill.py`.
- `pyproject.toml` — 9 governance parsers + 1 graph backend registered as entry points. No PM, schema, or doc target entries yet.

## 4. Target Interfaces

### New Functions

```python
# cli/commands/adapters.py
def list_command(format: str = "human") -> None:
    """List all registered adapters by entry point group."""

def check_command(format: str = "human") -> None:
    """Validate adapters against their Protocol contracts."""
```

```python
# output/formatters/adapters.py
def format_list_human(tier: str, groups: list[dict[str, Any]], console: Console) -> None:
    """Rich output: tier header, then group/name/package per group."""

def format_list_json(tier: str, groups: list[dict[str, Any]]) -> str:
    """JSON object with tier + groups array."""

def format_check_human(results: list[dict[str, Any]], console: Console) -> None:
    """Rich output: pass/fail per adapter with summary line."""

def format_check_json(results: list[dict[str, Any]]) -> str:
    """JSON object with results array + summary."""
```

```python
# cli/commands/adapters.py (group→Protocol mapping, only consumer)
ADAPTER_GROUPS: dict[str, tuple[str, type]] = {
    EP_PM_ADAPTERS: ("ProjectManagementAdapter", ProjectManagementAdapter),
    EP_GOVERNANCE_SCHEMAS: ("GovernanceSchemaProvider", GovernanceSchemaProvider),
    EP_GOVERNANCE_PARSERS: ("GovernanceParser", GovernanceParser),
    EP_DOC_TARGETS: ("DocumentationTarget", DocumentationTarget),
    EP_GRAPH_BACKENDS: ("KnowledgeGraphBackend", KnowledgeGraphBackend),
}
```

**No Pydantic models.** Data is ephemeral display-only (registry → format → print). Formatters receive plain dicts, same pattern as `format_skill_list_json`. Build dicts inline in command functions.

### Integration Points
- `list_command()` calls `_discover()` for each group in `ADAPTER_GROUPS`
- `check_command()` calls `_discover()` then `isinstance(cls, Protocol)` for each
- `TierContext.from_manifest()` called once to display current tier in `list` header
- `main.py` registers `adapters_app` via `app.add_typer()`

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Examples

### `rai adapters list`
```
Tier: community

rai.governance.parsers (GovernanceParser)
  prd            rai-cli
  vision         rai-cli
  constitution   rai-cli
  roadmap        rai-cli
  backlog        rai-cli
  epic_scope     rai-cli
  adr            rai-cli
  guardrails     rai-cli
  glossary       rai-cli

rai.graph.backends (KnowledgeGraphBackend)
  local          rai-cli

rai.adapters.pm (ProjectManagementAdapter)
  (none)

rai.governance.schemas (GovernanceSchemaProvider)
  (none)

rai.docs.targets (DocumentationTarget)
  (none)
```

### `rai adapters check`
```
Checking adapters...

rai.governance.parsers
  ✓ prd            GovernanceParser compliant
  ✓ vision         GovernanceParser compliant
  ...

rai.graph.backends
  ✓ local          KnowledgeGraphBackend compliant

All 10 adapters passed.
```

### `rai adapters check` (failure case)
```
Checking adapters...

rai.adapters.pm
  ✗ broken-jira    Failed to load: ModuleNotFoundError('raise_pro')

1 of 11 adapters failed.
```

### `rai adapters list --format json`
```json
{
  "tier": "community",
  "groups": [
    {
      "group": "rai.governance.parsers",
      "protocol_name": "GovernanceParser",
      "adapters": [
        {"name": "prd", "package": "rai-cli"},
        {"name": "vision", "package": "rai-cli"}
      ]
    }
  ]
}
```
