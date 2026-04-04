---
name: rai-mcp-add
description: Register an MCP server conversationally. Use to add a new MCP integration.

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
    - server_intent: string, optional, argument (e.g. "Context7", "GitHub MCP")
  raise.outputs: |
    - config_path: file_path (.raise/mcp/<name>.yaml)
---

# MCP Add

## Purpose

Guide a developer through MCP server registration without requiring CLI knowledge. Collect intent, resolve details conversationally, delegate to CLI.

## Mastery Levels (ShuHaRi)

- **Shu**: Ask each question individually, explain what each answer means
- **Ha**: Batch questions when context is clear, suggest defaults
- **Ri**: One-shot if intent is unambiguous (e.g. "add Context7" → install directly)

## Context

**When to use:** Developer wants to add an MCP server to their project.

**When to skip:** Developer already knows the exact CLI command and prefers to run it directly.

## Steps

### Step 1: Understand Intent

Ask the developer what MCP server they want to add. Accept free-text descriptions:
- "Context7 for documentation lookups"
- "GitHub MCP server"
- "a Snyk security scanner"
- "I have a custom server running locally"

If the developer provides a name as an argument (e.g. `/rai-mcp-add context7`), skip this question.

<verification>
Server intent captured.
</verification>

### Step 2: Resolve Package Details

Based on the intent, determine:

1. **Package type** — ask: "Is this an npm package (npx), a Python package (uvx/pip), or a locally running server?"
2. **Package identifier** — ask for the exact package name (e.g. `@upstash/context7-mcp`, `mcp-github`)
3. **Server name** — suggest a slug derived from the package name, let the developer override
4. **Environment variables** — ask: "Does this server need any API keys or tokens? (e.g. GITHUB_TOKEN)"
5. **Python module** (pip only) — ask: "What's the Python module name to run? (e.g. mcp_server_fetch)"

**For known servers, read `.raise/mcp/catalog.yaml`:**

If the developer's intent matches a server name in the catalog, pre-fill all fields (package, type, env, module) from the catalog entry. No need to ask questions already answered by governance data.

If the catalog is missing or the server isn't in it, ask the developer for each field individually.

If uncertain, ask. Never guess package names.

<verification>
All required fields collected: type, package, name, env (if any), module (if pip).
</verification>

### Step 3: Confirm Before Installing

Present a summary of what will be installed:

```
I'll set up the following MCP server:

  Name:    {name}
  Package: {package}
  Type:    {type}
  Env:     {env_vars or "none"}
  Config:  .raise/mcp/{name}.yaml

Proceed?
```

Wait for confirmation.

<verification>
Developer confirmed installation.
</verification>

### Step 4: Install

Run the appropriate CLI command:

```bash
rai mcp install {package} --type {type} --name {name} [--env {env}] [--module {module}]
```

If the config file already exists, ask whether to overwrite (adds `--force`).

For a locally running server (no package to install), use scaffold instead:

```bash
rai mcp scaffold {name} --command {command} --args "{args}" [--env {env}]
```

<verification>
CLI command executed successfully. Config file created.
</verification>

### Step 5: Report Result

After installation, report:
- Config file location
- Health check result (healthy/unhealthy)
- Number of tools discovered
- List of available tools

If health check failed, suggest troubleshooting:
- Check if the package is installed correctly
- Verify environment variables are set
- Try `rai mcp health {name}` manually

```
✓ MCP server '{name}' added successfully!

  Config:  .raise/mcp/{name}.yaml
  Health:  healthy
  Tools:   {count} available
           - {tool1}
           - {tool2}

  Use `rai mcp call {name} <tool> --args '{{...}}'` to invoke tools.
```

<verification>
Result reported. Developer knows the server is ready (or what to fix).
</verification>

## Output

| Item | Destination |
|------|-------------|
| MCP config | `.raise/mcp/{name}.yaml` |
| Next | Use the server via `rai mcp call` or reference via `server.ref` in adapters |

## Quality Checklist

- [ ] Intent captured before asking technical details
- [ ] Catalog read from `.raise/mcp/catalog.yaml` for known server defaults
- [ ] Confirmation shown before running install
- [ ] Health check result reported
- [ ] Available tools listed after successful install
- [ ] NEVER require the human to know CLI syntax
- [ ] NEVER guess package names — ask when uncertain

## References

- CLI: `rai mcp install`, `rai mcp scaffold`, `rai mcp health`, `rai mcp tools`
- Catalog: `.raise/mcp/catalog.yaml` (governance — known servers + package details)
- Complement: `/rai-mcp-remove`, `/rai-mcp-status`
- Pattern: CLI = agent tools, Skills = human interface
