# RAISE-482: Root Cause Analysis

## Method: 5 Whys (Tier S)

**Problem:** "No module named 'rai_cli'" warnings on every CLI invocation after upgrade.

1. **Why do stale entry points load?**
   Because `rai-cli 2.1.0` dist-info persists in site-packages with entry points pointing to `rai_cli.hooks.builtin.*`.

2. **Why does the old package persist?**
   Because `pip install raise-cli` does not uninstall `rai-cli` — pip treats differently-named packages as independent.

3. **Why is there no detection?**
   Because no runtime check validates that legacy packages are removed after the rename.

4. **Why are the warnings confusing?**
   Because the registry catches `ImportError` generically and logs "Skipping hook entry point ... No module named 'rai_cli'" — no context about the rename or how to fix it.

## Root Cause

Package rename without runtime detection of co-installed legacy packages.

## Fix Approach

Add a startup check in the CLI entrypoint that:
1. Uses `importlib.metadata` to detect if `rai-cli` or `rai-core` are installed
2. Emits a clear warning with the uninstall command
3. Runs early (before hook/adapter discovery) so the user sees it first

Location: `raise_cli/cli/main.py` or a dedicated `raise_cli/compat.py` module.
