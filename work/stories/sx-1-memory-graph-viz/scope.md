## Story Scope: SX-1 Memory Graph Visualization

**Type:** Standalone tooling (no epic)
**Size:** S
**Priority:** Demo-day (2026-02-10)

**In Scope:**
- Interactive HTML viewer for `.raise/rai/memory/index.json`
- Color-coded nodes by type (component, pattern, session, etc.)
- Filterable by node type
- Zoomable/pannable force-directed layout
- CLI command to generate the HTML (`raise memory viz` or similar)
- Self-contained single HTML file (no external dependencies at runtime)

**Out of Scope:**
- Editing graph from the UI
- Real-time updates / watch mode
- Server-side rendering
- Integration with external graph databases
- Styling beyond functional demo-readiness

**Done Criteria:**
- [ ] `raise memory viz` (or equivalent) generates an interactive HTML file
- [ ] HTML opens in browser showing graph with colored nodes and labeled edges
- [ ] User can filter by node type
- [ ] User can zoom/pan and hover for details
- [ ] Works with raise-commons graph (1K+ nodes, 11K+ edges)
- [ ] Tests pass
- [ ] Retrospective complete
