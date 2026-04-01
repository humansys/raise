WHAT:      rai backlog update --assignee passes plain string to Jira; rai backlog create has no --assignee at all
WHEN:      rai backlog update RAISE-XXX --assignee "username" — Jira rejects or silently ignores the field
WHERE:     backlog.py:149 — CLI sends {"assignee": "string"}; jira_adapter.py:226-230 — passes through raw;
           Jira REST API expects {"assignee": {"accountId": "..."}} — format mismatch
           IssueSpec (pm.py:21-29) — no assignee field, so create_issue cannot set it at all
EXPECTED:  --assignee resolves to Jira accountId and sets correctly on create and update
Done when: assignee is set in Jira after both create and update operations

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing

STATUS: Reproduced — rai backlog update RAISE-1152 --assignee "fernando@rhumanys.ai" fails with
        "one of 'fields' or 'update' required"
