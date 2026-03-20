# RAISE-594: Scope

## In Scope

- Entry point discovery loop in `src/raise_cli/cli/main.py` using `importlib.metadata.entry_points(group="rai.cli.commands")`
- Silent skip on extension load failure
- Tests covering: successful registration, broken extension skip, no extensions installed

## Out of Scope

- Extension validation beyond load success
- Documentation for extension authors (separate task)
- Any changes to existing commands
- CLI plugin discovery caching or lazy loading

## Done When

- [ ] `rai.cli.commands` entry points are discovered and registered as Typer sub-apps
- [ ] `rai --help` shows extension commands when installed
- [ ] Broken extensions are silently skipped (no crash, no user-visible error)
- [ ] Zero new dependencies added
- [ ] All existing commands work identically
- [ ] Tests pass, types check, linting clean
