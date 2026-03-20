# RAISE-594: CLI Extension Mechanism

## User Story

**As** an external RaiSE package developer,
**I want** to register Typer command groups under the `rai` namespace via entry points,
**So that** packages like rai-agent can add CLI commands without modifying raise-commons.

## Acceptance Criteria

```gherkin
Scenario: External package registers a command group
  Given an installed package with entry point group "rai.cli.commands"
  And the entry point name is "knowledge" pointing to a Typer app
  When the user runs "rai knowledge --help"
  Then the command group is available and functional

Scenario: Extension appears in help
  Given an installed package with "rai.cli.commands" entry point
  When the user runs "rai --help"
  Then the extension command appears alongside built-in commands

Scenario: Broken extension does not crash CLI
  Given an installed package with a broken entry point (import error)
  When the user runs "rai --help"
  Then the CLI loads normally without the broken extension
  And no error is shown to the user

Scenario: No extensions installed
  Given no packages with "rai.cli.commands" entry points
  When the user runs "rai --help"
  Then all built-in commands work as before
```

## Size

XS — ~8 lines of code, 0 new dependencies, follows existing entry point pattern.
