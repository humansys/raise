---
type: module
name: viz
purpose: "Interactive HTML visualization of the memory graph — self-contained D3.js force-directed graph"
status: current
depends_on: []
depended_by: [cli]
entry_points:
  - "raise memory viz"
public_api:
  - "generate_viz_html"
components: 2
constraints:
  - "Output must be a single self-contained HTML file"
  - "All sizes viewport-relative for UHD compatibility"
  - "Edge sampling for graphs with >3000 edges"
---

# Module: viz

Generates interactive HTML visualization of the memory graph (`index.json`).

## Responsibilities

- Read NetworkX-compatible graph JSON
- Produce self-contained HTML with embedded D3.js force-directed graph
- Cluster nodes by domain (Governance, Architecture, Memory, Work, Skills)
- Sub-cluster patterns by primary context tag
- Viewport-responsive scaling for UHD displays

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API re-export |
| `generator.py` | HTML generation with embedded graph data and D3.js template |

## Data Flow

```
.raise/rai/memory/index.json → generate_viz_html() → graph.html (browser)
```

## Integration

- CLI command `rai memory viz` in `cli/commands/memory.py`
- No runtime dependencies beyond stdlib (`json`, `pathlib`)
- D3.js v7 loaded from CDN in generated HTML
