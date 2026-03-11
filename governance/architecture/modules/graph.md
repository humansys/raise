---
type: module
name: graph
purpose: "Knowledge graph persistence backends"
status: current
depends_on: [context, adapters]
depended_by: [cli, memory]
entry_points: ["rai.graph.backends"]
public_api:
  - "FilesystemGraphBackend"
  - "get_active_backend"
layer: domain
bounded_context: adapters
---

# Module: graph

## Overview

Built-in graph backend implementations. `FilesystemGraphBackend` persists the
knowledge graph to local JSON files (COMMUNITY tier). Entry point
`rai.graph.backends` enables plugin backends (e.g., Supabase for PRO).

## Key Files

| File | Purpose |
|------|---------|
| `filesystem_backend.py` | `FilesystemGraphBackend` — JSON persistence, `get_active_backend()` factory |

## Data Flow

- `get_active_backend(path)` returns the active backend (currently always filesystem)
- Called by `rai memory build` (discover.py), `rai release` (release.py), and memory commands
- Persists to `.raise/rai/memory/index.json` (personal) or `.raise/graph/unified.json` (project)

## Architecture

- ADR-036: KnowledgeGraphBackend
- Implements `KnowledgeGraphBackend` Protocol from `adapters.protocols`
