# RAISE-398 Bug Scope

WHAT:      pyright reports 7 errors blocking CI: 6 type-unknown errors in
           mcp_jira.py and 1 unused import in queries.py
WHEN:      Always — pyright stage runs on every CI push
WHERE:     src/rai_cli/adapters/mcp_jira.py:279-282
           packages/rai-server/src/rai_server/db/queries.py:11
EXPECTED:  pyright exits 0; no type errors
Done when: `uv run pyright src/rai_cli/adapters/mcp_jira.py
           packages/rai-server/src/rai_server/db/queries.py`
           exits 0 with "0 errors"
