# RAISE-1187: Scope

WHAT:      ConfluenceDiscovery.discover() and ConfluenceDiscoveryService.build_space_map() fail to find spaces with mixed-case keys (e.g., RaiSE1) because get_all_spaces() from atlassian-python-api doesn't return them
WHEN:      Running /rai-adapter-setup or any discovery on a space with a mixed-case key
WHERE:     confluence_discovery.py:58-64 (v1) and confluence_discovery.py:203-206 (v2)
EXPECTED:  Discovery should find the space and build its page tree normally
Done when: discover(space_key="RaiSE1") and build_space_map("RaiSE1") succeed even when get_all_spaces() omits the space

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Integration
  Qualifier:   Missing
