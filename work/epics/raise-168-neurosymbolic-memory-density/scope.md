## Epic Scope: RAISE-168 Neurosymbolic Memory Density

**Jira:** RAISE-168
**Branch:** `epic/raise-168/neurosymbolic-memory-density`
**Base:** `v2`
**Objective:** Transform RaiSE's memory serialization from human-readable markdown to semantically dense, edge-aware, task-relevant context that maximizes accuracy-per-token for LLM comprehension.

**Research Foundation:** `work/research/memory-systems/RES-MEMORY-002-research-report.md` — 4 RQs, 50+ sources, triangulated claims.

**In Scope:**
- Compact query format (`--format compact`) with header-based serialization
- Fix concept_lookup (broken BFS) + edge-aware results
- Truncation transparency indicator
- Task-relevant context bundle (parametrize by session type)
- Temporal decay and pattern scoring
- Meta-cognition indicators (coverage, confidence, gaps)

**Out of Scope:**
- Changing graph backend (NetworkX → Neo4j) → future epic
- Adding vector embeddings / similarity search → future epic
- Bi-temporal model (Zep-style) → future epic
- Benchmark infrastructure → future epic
- MCP tool tax reduction → external to rai-cli

**Stories:**
- [x] RAISE-166: Compact query format + concept_lookup fix + truncation (S) ✓ (2026-02-18)
- RAISE-165: Session startup overhead reduction (S) — depends on RAISE-166
- RAISE-169: Task-relevant context bundle (M)
- RAISE-170: Temporal decay and pattern scoring (M)
- RAISE-171: Meta-cognition indicators (L)

**Done when:**
- [ ] All stories complete
- [ ] Epic retrospective done
- [ ] Merged to `v2`
