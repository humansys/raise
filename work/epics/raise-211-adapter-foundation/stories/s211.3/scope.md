## Feature Scope: S211.3

**In Scope:**
- Wrap existing governance parsers to conform to GovernanceParser Protocol
- Register wrapped parsers as entry points in pyproject.toml (`rai.governance.parsers`)
- Refactor GovernanceExtractor to discover parsers via registry
- Refactor UnifiedGraphBuilder.load_governance() to use registry path
- Extract glob logic from adr/guardrails/glossary parsers so ArtifactLocator works
- Graceful degradation for broken/missing parsers

**Out of Scope:**
- GovernanceSchemaProvider formal class (YAGNI — builder locates internally)
- External parser packages (validated by entry point mechanism, not implemented)
- Refactoring non-governance builder methods (load_memory, load_work, etc.)
- Changing ConceptNode/GraphNode model hierarchy

**Done Criteria:**
- [ ] All 10 governance parsers registered as entry points
- [ ] GovernanceExtractor uses registry instead of hardcoded imports
- [ ] `rai memory build` produces functionally identical graph
- [ ] Broken parser logs warning, doesn't break build
- [ ] Tests pass (pyright + ruff + pytest)
- [ ] Retrospective complete
