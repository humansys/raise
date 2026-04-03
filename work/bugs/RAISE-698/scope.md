WHAT:      rai-agent package missing entry points, raise-cli dependency, and core deps
WHEN:      After S11.4 migration split packages — rai-agent pyproject.toml lost config
WHERE:     packages/rai-agent/pyproject.toml
EXPECTED:  Package has CLI entry points for daemon/knowledge, raise-cli dep, and required deps
Done when: rai daemon and rai knowledge subcommands work from rai-agent install

TRIAGE:
  Bug Type:    Configuration
  Severity:    S2-Medium
  Origin:      Integration
  Qualifier:   Missing
