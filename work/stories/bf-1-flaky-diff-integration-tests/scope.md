## Story Scope: BF-1

**Type:** Bugfix (standalone, no epic)
**Branch:** `story/bugfix/flaky-diff-integration-tests`

**Problem:**
`tests/context/test_diff_integration.py` builds the real unified graph from live
`.raise/` files on every run. This couples test assertions to codebase state — any
governance file change (new patterns, modules, node count shifts) can break tests.

**In Scope:**
- Make diff integration tests deterministic (not dependent on live graph state)
- Preserve test intent: diff_graphs correctly detects added/modified/removed nodes
- Keep tests as integration-level (not unit mocks of everything)

**Out of Scope:**
- Refactoring diff_graphs itself
- Adding new diff test scenarios
- Changes to the graph builder

**Done Criteria:**
- [ ] Tests pass regardless of current graph state
- [ ] Tests still exercise real diff_graphs logic (not fully mocked)
- [ ] All existing tests pass
- [ ] Retrospective complete
