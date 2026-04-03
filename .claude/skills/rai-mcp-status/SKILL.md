---
name: rai-mcp-status
description: Check health of registered MCP servers. Use to diagnose MCP connectivity.

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
    - server_name: string, optional, argument (check single server)
  raise.outputs: |
    - status_report: text (markdown table)
---

# MCP Status

## Purpose

Show the health and availability of all registered MCP servers in one view.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain each server's status and what it means
- **Ha**: Show summary table, explain only issues
- **Ri**: Table only, no explanation unless problems found

## Context

**When to use:** Developer wants to check if their MCP servers are working.

**When to skip:** Checking a single server — use `rai mcp health <name>` directly.

## Steps

### Step 1: Discover Servers

Run `rai mcp list` to get all registered servers.

If no servers registered: "No MCP servers registered. Use `/rai-mcp-add` to add one."

<verification>
Server list retrieved (or empty state handled).
</verification>

### Step 2: Health Check Each Server

For each registered server, run `rai mcp health <name>`.

Collect: status (healthy/unhealthy), tool count, latency, error message (if any).

<verification>
All servers checked.
</verification>

### Step 3: Present Summary

Present a markdown table:

```
MCP Server Status:

| Server   | Status    | Tools | Latency | Notes        |
|----------|-----------|-------|---------|--------------|
| context7 | ✓ healthy | 2     | 1.2s    |              |
| github   | ✗ error   | —     | —       | timeout      |

{healthy_count}/{total_count} servers healthy.
```

If all healthy: "{count} servers, all healthy."

If any unhealthy, suggest: "Run `/rai-mcp-add` to reinstall problematic servers, or check environment variables."

<verification>
Summary presented with actionable guidance for issues.
</verification>

### Step 4: Recommend Missing Capabilities

Read the governance catalog at `.raise/mcp/catalog.yaml`. If catalog is missing, skip this step gracefully.

**Detect project languages:**
1. Read `work/discovery/analysis.json` if it exists — derive languages from file extensions in `components[].file`
2. If no analysis artifact, glob for source files: `**/*.py`, `**/*.ts`, `**/*.js`, `**/*.php`, `**/*.cs`, `**/*.dart`
3. Map extensions to languages using scanner's `EXTENSION_TO_LANGUAGE`

**Filter recommendations:**
1. For each catalog server, check `recommended_for` (note: value is either the string `all` or a list):
   - String `all` → always recommend regardless of detected languages
   - List of languages (e.g. `[python, typescript]`) → recommend if any detected language matches
   - Empty list `[]` → never recommend (opt-in only, must use `/rai-mcp-add` explicitly)
2. Exclude servers already registered in `.raise/mcp/`
3. If no recommendations remain: skip section silently

**Present recommendations:**

```
Recommended for your stack ({detected_languages}):

| Server | Description                  | Add with              |
|--------|------------------------------|-----------------------|
| github | GitHub repository operations | /rai-mcp-add github   |
| fetch  | HTTP fetch for web content   | /rai-mcp-add fetch    |

Use /rai-mcp-add <name> to install.
```

<verification>
Recommendations shown (or skipped if none). Already-registered servers excluded.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Status report | Displayed inline |
| Next | Fix unhealthy servers via `/rai-mcp-add` or manual troubleshooting |

## Quality Checklist

- [ ] All registered servers checked (not just a subset)
- [ ] Unhealthy servers show error details
- [ ] Actionable guidance provided for issues
- [ ] Empty state handled gracefully
- [ ] Catalog read from `.raise/mcp/catalog.yaml` (graceful if missing)
- [ ] Already-registered servers excluded from recommendations
- [ ] Languages detected from discovery artifact or file glob fallback

## References

- CLI: `rai mcp list`, `rai mcp health`
- Catalog: `.raise/mcp/catalog.yaml` (governance — known servers + stack mapping)
- Discovery: `work/discovery/analysis.json` (stack detection source)
- Complement: `/rai-mcp-add`, `/rai-mcp-remove`
- Epic: E338 MCP Platform
