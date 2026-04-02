# RAISE-218 Scope

WHAT:      manifest.yaml siempre escribe `ide.type: claude` aunque el agente configurado sea otro (cursor, windsurf, etc.)
WHEN:      `rai init --agent cursor` o cualquier agente ≠ claude
WHERE:     src/raise_cli/cli/commands/init.py:574 — construcción de ProjectManifest sin `ide=`
EXPECTED:  `ide.type` debe reflejar el agente primario elegido (agents.types[0])
Done when: `rai init --agent cursor` produce `ide.type: cursor` y `agents.types: [cursor]` — consistentes

TRIAGE:
  Bug Type:    Configuration
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Incorrect
