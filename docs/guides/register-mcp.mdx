---
title: Register an MCP Server
description: How to register an MCP server in RaiSE — install packages, scaffold configs, and verify health.
---

MCP (Model Context Protocol) servers extend your AI assistant with external tools. RaiSE manages server registration, configuration, and health checking through the `rai mcp` command group.

## Two Registration Methods

### Method 1: Install a Package

For published MCP servers, use `rai mcp install`:

```bash
# npx package (Node.js)
rai mcp install "@upstash/context7-mcp" --type npx --name context7

# uvx package (Python)
rai mcp install "semgrep-mcp" --type uvx --name semgrep --env SEMGREP_APP_TOKEN

# pip package (Python module)
rai mcp install "mcp-server-fetch" --type pip --name fetch --module mcp_server_fetch
```

### Method 2: Scaffold Manually

For custom or local servers, use `rai mcp scaffold`:

```bash
rai mcp scaffold my-server \
  --command "node" \
  --args "path/to/server.js" \
  --env "MY_API_KEY"
```

## Config File Format

Both methods create a YAML config in `.raise/mcp/`. The catalog format:

```yaml
# .raise/mcp/catalog.yaml
servers:
  context7:
    package: "@upstash/context7-mcp"
    type: npx
    description: "Documentation lookups for any library via Context7"
    recommended_for: all

  github:
    package: "@modelcontextprotocol/server-github"
    type: npx
    env: [GITHUB_TOKEN]
    description: "GitHub repository operations"
    recommended_for: all

  semgrep:
    package: "semgrep-mcp"
    type: uvx
    env: [SEMGREP_APP_TOKEN]
    description: "SAST + SCA + secret detection"
    recommended_for: all
```

Config fields:
- `package` — Package identifier for installation
- `type` — `npx`, `uvx`, or `pip`
- `module` — Python module name (pip only)
- `env` — Required environment variable names
- `description` — Human-readable purpose
- `recommended_for` — Language list, or `all` for universal

## Verification

After registration, verify your server works:

```bash
# List registered servers
rai mcp list

# Check server health
rai mcp health context7

# List available tools on a server
rai mcp tools context7

# Call a specific tool
rai mcp call context7 resolve-library-id --args '{"libraryName": "react"}'
```

## Example: Registering Context7

Context7 provides documentation lookups for any library. Here is the full flow:

```bash
# Install
rai mcp install "@upstash/context7-mcp" --type npx --name context7

# Verify
rai mcp health context7
rai mcp tools context7
```

No environment variables needed. The server is immediately available to your AI assistant for documentation queries.
