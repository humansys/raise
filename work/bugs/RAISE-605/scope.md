# RAISE-605: Scope

WHAT:      `rai docs publish` creates pages at space root — no way to specify parent page for ad-hoc publishing
WHEN:      Publishing without routing config, or when needing to override routing's parent
WHERE:     CLI: packages/raise-cli/src/raise_cli/cli/commands/docs.py (no --parent flag)
           Adapter: packages/raise-cli/src/raise_cli/adapters/confluence_adapter.py (ignores metadata["parent_id"])
EXPECTED:  CLI accepts `--parent PAGE_ID`, adapter uses it as parent override before routing fallback
Done when: `rai docs publish <type> --parent <id>` places page under specified parent; routing still works as default

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
