# RAISE-1007: Governance hooks disabled — ProcessTransport crash on SDK shutdown

WHAT:      Governance hooks (PreToolUse, PostToolUse, Stop) disabled via `and False` hack in runtime.py:305
WHEN:      claude-agent-sdk v0.1.48 — hooks cause ProcessTransport crash during SDK subprocess shutdown
WHERE:     packages/rai-agent/src/rai_agent/daemon/runtime.py:305
EXPECTED:  Governance hooks active — tool auditing, sensitive pattern blocking, HITL approval, turn limits
Done when: `and False` removed, SDK bumped to >=0.1.51, 3 skipped tests passing, no ProcessTransport crash
