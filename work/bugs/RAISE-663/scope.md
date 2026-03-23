# RAISE-663 — Scope

WHAT:      `rai backlog get <key>` displays Python dict repr instead of readable description text
WHEN:      Any Jira issue with a description stored in ADF (Atlassian Document Format)
WHERE:     `packages/raise-pro/src/rai_pro/adapters/acli_jira.py:220` (ADF→str conversion)
           `src/raise_cli/cli/commands/backlog.py:231` (hard-cap 500 chars truncates the repr)
EXPECTED:  Description renders as plain text (paragraphs, lists, code blocks as readable text)
Done when: `rai backlog get RAISE-663` shows the description as human-readable text, not ADF repr
