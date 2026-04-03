WHAT:      rai docs publish creates pages in Confluence space root — no parent_id support
WHEN:      rai docs publish any artifact type
WHERE:     mcp_confluence.py ~148 — publish() never reads parent_id from metadata
EXPECTED:  --parent flag passes parent_id to confluence_create_page
Done when: rai docs publish --parent PAGE_ID creates page under specified parent

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing

STATUS: Valid — publish() still ignores parent_id. 2-line fix proposed in ticket.
