---
name: rai-mcp-remove
description: Remove an MCP server with dependency checking. Use to unregister a server.
disable-model-invocation: true

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - server_name: string, optional, argument (e.g. "context7")
  raise.outputs: |
    - removed: boolean
---

# MCP Remove

## Purpose

Safely remove an MCP server from the project, checking for adapter dependencies before deletion.

## Mastery Levels (ShuHaRi)

- **Shu**: Show each check step, explain dependencies found
- **Ha**: Skip listing if server name provided, streamline confirmation
- **Ri**: Remove immediately if no dependencies, warn only when needed

## Context

**When to use:** Developer wants to remove a registered MCP server.

**When to skip:** Developer prefers to delete the YAML file manually.

## Steps

### Step 1: Identify Server

If no server name provided as argument:

1. List registered servers using `rai mcp list`
2. Ask: "Which server would you like to remove?"

If server name provided, verify it exists in `.raise/mcp/`.

<verification>
Target server identified and exists.
</verification>

### Step 2: Check Dependencies

Search for references to this server in declarative adapter configs:

```bash
grep -rl "ref:.*{server_name}" .raise/adapters/ 2>/dev/null
```

If references found, present them:

```
⚠ Found adapters referencing '{server_name}':
  - .raise/adapters/{adapter1}.yaml
  - .raise/adapters/{adapter2}.yaml

Removing this server will break these adapters.
```

If no references found: "No adapter dependencies found."

<verification>
Dependencies checked and reported.
</verification>

### Step 3: Confirm and Remove

If dependencies exist, ask for explicit confirmation: "Remove anyway? This will break the listed adapters."

If no dependencies (or confirmed), delete the config:

```bash
rm .raise/mcp/{server_name}.yaml
```

Report: "Removed .raise/mcp/{server_name}.yaml"

If dependencies were found, add: "Update the listed adapters to use inline config or reference another server."

<verification>
Config file deleted. Developer informed of any follow-up actions.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Deleted config | `.raise/mcp/{name}.yaml` removed |
| Next | Update dependent adapters if any |

## Quality Checklist

- [ ] Server existence verified before attempting removal
- [ ] Adapter dependencies checked via grep
- [ ] Explicit confirmation required when dependencies exist
- [ ] Follow-up guidance provided for broken adapters
- [ ] NEVER delete without checking dependencies first

## References

- CLI: `rai mcp list`
- Complement: `/rai-mcp-add`, `/rai-mcp-status`
- Adapter config: `.raise/adapters/*.yaml` (`server.ref` field)
- Epic: E338 MCP Platform
