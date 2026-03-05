WHAT:      `rai backlog search` with JQL containing `!=` returns "No results" when invoked from Claude Code Bash tool
WHEN:      Claude Code Bash tool escapes `!` to `\!` before passing to the CLI
WHERE:     src/rai_cli/adapters/mcp_jira.py:search() — no input sanitization at system boundary
EXPECTED:  JQL with `!=` returns matching issues regardless of shell escaping
Done when: `rai backlog search 'status \!= Done AND project = RAISE'` returns the same results as `status != Done`
