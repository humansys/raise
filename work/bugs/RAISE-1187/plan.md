# RAISE-1187: Plan

## Tasks

### T1: Regression test — discover fails for space missing from get_all_spaces (RED)
- Test that ConfluenceDiscovery.discover(space_key="RaiSE1") succeeds when get_spaces() omits "RaiSE1" but direct lookup works
- Test that ConfluenceDiscoveryService.build_space_map("RaiSE1") succeeds with same fallback
- Test that truly nonexistent spaces still raise errors
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_discovery.py -x -k "mixed_case or fallback"` — FAILS
- Commit: `test(RAISE-1187): regression tests for mixed-case space key fallback`

### T2: Add get_space_direct() to ConfluenceClient (GREEN step 1)
- New method: `get_space_direct(space_key) -> SpaceInfo | None` using `self._client.get_space(space_key)`
- Returns SpaceInfo or None if 404
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_discovery.py -x -k "mixed_case or fallback"` — still FAILS (client added but not wired)
- Commit: `fix(RAISE-1187): add get_space_direct() for direct space lookup`

### T3: Wire fallback in both discovery classes (GREEN step 2)
- ConfluenceDiscovery.discover(): if space_key not in get_spaces() results, try client.get_space_direct() before raising
- ConfluenceDiscoveryService.build_space_map(): same fallback
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_discovery.py -x` — PASSES
- Commit: `fix(RAISE-1187): fallback to direct lookup for mixed-case space keys`
