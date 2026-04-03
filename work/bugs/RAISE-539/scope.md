WHAT:      rai mcp install saves env as KEY=VALUE list, but _resolve_env expects env var names only
WHEN:      rai mcp install with --env KEY=VALUE, then rai mcp health
WHERE:     cli/commands/mcp.py:57 (_resolve_env) — treats full KEY=VALUE string as env var name
           cli/commands/mcp.py:358,488 — install/scaffold store KEY=VALUE as list items
EXPECTED:  Either install stores only names (and values go to .env), or _resolve_env parses KEY=VALUE
Done when: rai mcp health works after rai mcp install with --env KEY=VALUE

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Incorrect

STATUS: Still valid — verified _resolve_env (line 64) uses env_names as dict keys without parsing =.
