---
title: rai mcp
description: Manage and invoke MCP servers registered in .raise/mcp/.
---

Manage and invoke MCP (Model Context Protocol) servers. Servers are registered in `.raise/mcp/*.yaml` and provide tools to AI agents.

## `rai mcp list`

List all registered MCP servers. Shows servers with their names, descriptions, and commands.

```bash
rai mcp list
```

---

## `rai mcp health`

Check connectivity of a registered MCP server. Connects, lists tools, and reports status, latency, and tool count.

| Argument | Description |
|----------|-------------|
| `SERVER` | Registered MCP server name (**required**) |

```bash
rai mcp health context7
```

---

## `rai mcp tools`

List available tools on a registered MCP server.

| Argument | Description |
|----------|-------------|
| `SERVER` | Registered MCP server name (**required**) |

```bash
rai mcp tools context7
```

---

## `rai mcp call`

Invoke a tool on a registered MCP server. Prints the result as JSON to stdout.

| Argument | Description |
|----------|-------------|
| `SERVER` | Registered MCP server name (**required**) |
| `TOOL` | Tool name to invoke (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--args` | | Tool arguments as JSON string. Default: `{}` |
| `--verbose` | | Show call details on stderr |

```bash
rai mcp call context7 resolve-library-id --args '{"query":"next.js","libraryName":"next.js"}'
```

---

## `rai mcp scaffold`

Connect to an MCP server, introspect tools, and generate config. Creates `.raise/mcp/<name>.yaml` by connecting, discovering tools, and writing a valid config.

| Argument | Description |
|----------|-------------|
| `NAME` | Server name (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--command` | | Server command, e.g. `npx`, `uvx` (**required**) |
| `--args` | | Server arguments as space-separated string |
| `--env` | | Comma-separated env var names |
| `--force` | | Overwrite existing config file |

```bash
rai mcp scaffold context7 --command npx --args "-y @upstash/context7-mcp"
```

---

## `rai mcp install`

Install an MCP server package and generate config. Installs the package, verifies connectivity, and generates `.raise/mcp/<name>.yaml`.

| Argument | Description |
|----------|-------------|
| `PACKAGE` | Package identifier (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--type` | | Package type: `uvx`, `npx`, `pip` (**required**) |
| `--name` | | Server name for config file (**required**) |
| `--env` | | Comma-separated env var names |
| `--module` | | Python module name (required for `--type pip`) |
| `--force` | | Overwrite existing config file |

```bash
# NPX package
rai mcp install @upstash/context7-mcp --type npx --name context7

# UVX package with env vars
rai mcp install mcp-github --type uvx --name github --env GITHUB_TOKEN

# Pip package with module
rai mcp install mcp-server-fetch --type pip --name fetch --module mcp_server_fetch
```

**See also:** [`rai adapter`](adapter.md/
