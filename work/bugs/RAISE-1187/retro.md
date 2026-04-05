# Retrospective: RAISE-1187

## Summary
- Root cause: atlassian-python-api's get_all_spaces() omits spaces with mixed-case keys; both discovery classes filter from that list
- Fix approach: Added get_space_direct() to ConfluenceClient and wired as fallback in both ConfluenceDiscovery.discover() and ConfluenceDiscoveryService.build_space_map()
- Classification: Interface/S2-Medium/Integration/Missing

## Process Improvement
**Prevention:** Any "list-all then filter" pattern against external APIs should include a direct lookup fallback. The enumeration endpoint is a convenience, not a guarantee.
**Pattern:** Interface + Integration + Missing → upstream API omits items from enumeration that direct lookup finds.

## Heutagogical Checkpoint
1. Learned: External API enumeration endpoints can have edge-case gaps that direct lookups don't share.
2. Process change: Test "item exists but not in list" scenario alongside standard positive/negative tests.
3. Framework improvement: None — fix is self-contained.
4. Capability gained: Resilient discovery pattern against unreliable enumeration endpoints.

## Patterns
- Added: PAT-E-731 (enumeration fallback to direct lookup)
- Reinforced: none evaluated
