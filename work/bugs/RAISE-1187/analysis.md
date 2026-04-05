# RAISE-1187: Analysis

## Method: Direct (cause evident from upstream behavior)

Error path:
1. User runs `/rai-adapter-setup` targeting space "RaiSE1"
2. Discovery calls `client.get_spaces()` → paginates through `get_all_spaces()`
3. `get_all_spaces()` omits "RaiSE1" (upstream quirk with mixed-case keys)
4. `discover(space_key="RaiSE1")` filters empty list → raises ConfluenceNotFoundError
5. Same pattern in `build_space_map("RaiSE1")` → raises DiscoveryError

## Root Cause

`atlassian-python-api`'s `get_all_spaces()` does not reliably enumerate all spaces — mixed-case keys and certain space types are omitted. This is an upstream API behavior we cannot fix. However, direct lookups (get_space_homepage_id, get_page_by_id) work fine for these spaces.

## Fix Approach

When a specific space_key is requested and not found in `get_spaces()` results, fall back to direct space lookup:

1. Add `get_space_direct(key)` to ConfluenceClient — calls the Confluence REST endpoint `/rest/api/space/{key}` directly, returns SpaceInfo or None
2. In `ConfluenceDiscovery.discover()`: if space_key not in get_spaces() results, try get_space_direct() before raising error
3. In `ConfluenceDiscoveryService.build_space_map()`: same fallback pattern
