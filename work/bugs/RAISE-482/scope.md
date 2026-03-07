# RAISE-482: Stale rai-cli/rai-core entry points cause 'No module named rai_cli'

WHAT:      Old packages (rai-cli 2.1.0, rai-core 2.1.0) register stale entry points pointing to `rai_cli.*` which no longer exists after rename to `raise_cli`
WHEN:      Upgrade from v2.1.x to v2.2.x without uninstalling old packages (pip treats them as independent)
WHERE:     Entry point discovery (HookRegistry.discover, adapter registry._discover) — any `rai.hooks` / `rai.adapters.pm` entry point group
EXPECTED:  Clear warning at startup with actionable uninstall command, not confusing "No module named 'rai_cli'" errors
Done when: Runtime check detects co-installed legacy packages and emits clear warning with uninstall instructions
