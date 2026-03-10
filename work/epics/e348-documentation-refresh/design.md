---
epic_id: "E348"
title: "Documentation Refresh — Design"
status: "draft"
created: "2026-03-05"
---

# E348: Documentation Refresh — Design

## Gemba: Current Documentation Architecture

```
docs/                          ← Astro doc site (Starlight theme)
├── src/content/docs/
│   ├── docs/                  ← English docs
│   │   ├── index.mdx          ← Landing page
│   │   ├── getting-started.mdx ← Install + first session
│   │   ├── cli/
│   │   │   └── index.mdx      ← CLI reference (INCOMPLETE)
│   │   ├── concepts/
│   │   │   ├── governance.mdx
│   │   │   ├── memory.mdx
│   │   │   ├── knowledge-graph.mdx
│   │   │   └── skills.mdx
│   │   └── guides/
│   │       ├── setting-up.mdx
│   │       └── first-story.mdx
│   └── es/docs/               ← Spanish mirror (same structure)
│
README.md                      ← 362 lines, needs refresh
CONTRIBUTING.md                ← Exists
CODE_OF_CONDUCT.md             ← Exists
CHANGELOG.md                   ← Exists
LICENSE                        ← Exists
AGENTS.md                      ← Placeholder (12 lines)
CLAUDE.md                      ← Rich, auto-generated from .raise/
llms.txt                       ← MISSING
```

## Target Architecture

### Diataxis Mapping

| Diataxis Type | Location | Status | This Epic |
|---------------|----------|--------|-----------|
| Tutorial | `docs/.../getting-started.mdx` | Exists | Validate only |
| Tutorial | `docs/.../guides/first-story.mdx` | Exists | Validate only |
| How-to | `docs/.../guides/setting-up.mdx` | Exists | Validate only |
| How-to | `docs/.../guides/create-adapter.mdx` | MISSING | S348.4 |
| How-to | `docs/.../guides/register-mcp-server.mdx` | MISSING | S348.4 |
| How-to | `docs/.../guides/create-skill.mdx` | MISSING | S348.4 |
| How-to | `docs/.../guides/wire-hook.mdx` | MISSING | S348.4 |
| Reference | `docs/.../cli/index.mdx` | PARTIAL (~40%) | S348.2 |
| Reference | `docs/.../cli/config.mdx` | MISSING | S348.2 |
| Explanation | `docs/.../concepts/*.mdx` | Exists (4) | Validate only |

### Agent Documentation Layer

```
llms.txt                       ← NEW: curated index per llmstxt.org spec
AGENTS.md                      ← EXPAND: cross-agent context + extension patterns
CLAUDE.md                      ← EXISTS: auto-generated, no changes needed
.claude/skills/*/SKILL.md      ← EXISTS: per-skill agent instructions
```

### llms.txt Structure (Target)

```markdown
# RaiSE

> Reliable AI Software Engineering — methodology + CLI toolkit for professional
> developers who use AI assistants. Governance, memory, structured workflows.

## Docs

- [Getting Started](docs/src/content/docs/docs/getting-started.mdx): Install, init, first session
- [CLI Reference](docs/src/content/docs/docs/cli/index.mdx): All commands with flags and examples
- [Configuration](docs/src/content/docs/docs/cli/config.mdx): .raise/ directory, manifest.yaml
- [Concepts: Memory](docs/src/content/docs/docs/concepts/memory.mdx): Patterns, sessions, calibration
- [Concepts: Skills](docs/src/content/docs/docs/concepts/skills.mdx): Skill lifecycle, SKILL.md
- [Concepts: Governance](docs/src/content/docs/docs/concepts/governance.mdx): Principles, guardrails
- [Concepts: Knowledge Graph](docs/src/content/docs/docs/concepts/knowledge-graph.mdx): Unified graph

## Guides

- [Setting Up](docs/src/content/docs/docs/guides/setting-up.mdx): Greenfield and brownfield
- [First Story](docs/src/content/docs/docs/guides/first-story.mdx): Full story lifecycle
- [Create an Adapter](docs/src/content/docs/docs/guides/create-adapter.mdx): Extension point
- [Register MCP Server](docs/src/content/docs/docs/guides/register-mcp-server.mdx): Extension point
- [Create a Skill](docs/src/content/docs/docs/guides/create-skill.mdx): Extension point
- [Wire a Hook](docs/src/content/docs/docs/guides/wire-hook.mdx): Extension point

## Development

- [Contributing](CONTRIBUTING.md): How to contribute
- [Changelog](CHANGELOG.md): Version history

## Optional

- [README](README.md): Project overview
- [AGENTS.md](AGENTS.md): Cross-agent context
```

## Key Contracts

### CLI Reference Pattern (per command group)

Each command group section follows this template:

```markdown
## {Group Name}

### `rai {group} {command}`

{1-2 sentence description.}

| Flag | Short | Description |
|------|-------|-------------|
| ... | ... | ... |

\`\`\`bash
# Example with comment
rai {group} {command} --flag value
\`\`\`
```

Source of truth: `rai {group} {command} --help` output + actual execution.

### Extension Guide Pattern (per extension point)

Each extension guide follows:

1. **What it is** — 2-3 sentences
2. **Protocol/interface** — what to implement
3. **Step-by-step** — create, register, test
4. **Working example** — minimal but complete
5. **Reference** — link to relevant CLI commands

Target: <5000 chars per page (agent-friendly).

## Components Affected

| Component | Change Type |
|-----------|-------------|
| `docs/src/content/docs/docs/cli/index.mdx` | EXTEND (add missing commands) |
| `docs/src/content/docs/docs/guides/*.mdx` | ADD (4 new extension guides) |
| `llms.txt` | CREATE |
| `AGENTS.md` | REWRITE |
| `README.md` | UPDATE |
| `docs/src/content/docs/docs/cli/config.mdx` | CREATE (config reference) |
