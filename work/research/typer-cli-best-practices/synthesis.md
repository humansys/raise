# Synthesis: Typer CLI Design Best Practices

> Research ID: TYPER-CLI-BP-20260205
> Date: 2026-02-05

---

## Major Claims (Triangulated)

### Claim 1: Prefer Flags Over Positional Arguments

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "Prefer flags to args. It's a bit more typing, but it makes it much clearer what is going on... Flags can make it easier to make changes to how you accept input in the future."
2. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "Flags are more explicit, user-friendly, and allow any order specification. Enable better autocomplete."
3. [UX Patterns for CLI Tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html) - "Using positional arguments instead of flags reduces clarity. One argument is fine, two are questionable, three is an absolute no."

**Disagreement:** None found.

**Implication:** Design RaiSE CLI commands with flags for most parameters; reserve positional arguments for the single most common parameter (e.g., command name, file path).

---

### Claim 2: Support Multiple Output Formats (Human, JSON, Table)

**Confidence:** HIGH

**Evidence:**
1. [AWS CLI Documentation](https://docs.aws.amazon.com/cli/v1/userguide/cli-usage-output-format.html) - "json, table, text, yaml formats available; choose based on use case."
2. [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/format-output-azure-cli) - "json, jsonc, none, table, tsv, yaml; table for human readability, json for machine parsing."
3. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "Support --json flag for full structured data, --terse flag when valuable. Maintain backward compatibility."
4. [clig.dev](https://clig.dev/) - "If human-readable output isn't available, plain text is the most versatile option. Use --json for structured output; offer --plain for tabular data."

**Disagreement:** None found.

**Implication:** Implement `--format` option with values: human (default), json, table. Auto-detect TTY for color/formatting. JSON output should be stable for scripting.

---

### Claim 3: Exit Code 0 for Success, Non-Zero for Failure with Distinct Codes

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "Set exit code to 0 if the program completes successfully, and non-zero if it fails. Map important failure modes to distinct exit codes."
2. [Exit Code Best Practices](https://chrisdown.name/2013/11/03/exit-code-best-practises.html) - "Exit 0 for success, non-zero for errors; distinct codes for different failure modes; avoid codes >125."
3. [Python Exit Codes Article](https://henryleach.com/2025/02/controlling-python-exit-codes-and-shell-scripts/) - "Raise exceptions in business logic, catch at CLI boundary, map to exit codes using custom exception types."
4. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "Zero exit code for success, non-zero for errors is crucial for interoperability with CI/CD."

**Disagreement:** None found.

**Implication:** Create exception hierarchy with mapped exit codes. Catch exceptions at CLI boundary, not in business logic.

---

### Claim 4: Use CliRunner for Testing with pytest

**Confidence:** HIGH

**Evidence:**
1. [Typer Testing Tutorial](https://typer.tiangolo.com/tutorial/testing/) - "Import CliRunner from typer.testing, invoke app with arguments, assert on exit_code and output."
2. [Click Testing Docs](https://click.palletsprojects.com/en/stable/testing/) - "CliRunner provides isolated_filesystem(), input simulation, and Result object with output/exit_code/exception capture."
3. [PyTest with Eric](https://pytest-with-eric.com/pytest-advanced/pytest-argparse-typer/) - "Use @pytest.mark.parametrize for multiple scenarios, test from user perspective, validate error messages."

**Disagreement:** None found.

**Implication:** Test CLI commands using CliRunner, parametrize for multiple scenarios, test both success and error paths.

---

### Claim 5: Organize Large CLIs with One File Per Command or Command Group

**Confidence:** HIGH

**Evidence:**
1. [Typer One File Per Command](https://typer.tiangolo.com/tutorial/one-file-per-command/) - "When your CLI application grows, split into multiple files and modules. Use add_typer to create sub commands."
2. [Typer SubCommands Tutorial](https://typer.tiangolo.com/tutorial/subcommands/) - "Create arbitrarily complex trees of commands and groups using add_typer with name parameter."
3. [Medium - Structuring a CLI](https://medium.com/pon-tech-talk/structuring-a-cli-22e2492717de) - "Separation of concerns: CLI layer (Typer), service layer (business logic), data layer."

**Disagreement:** None found.

**Implication:** Structure RaiSE CLI with one module per command group, using `add_typer()` for composition.

---

### Claim 6: Human-First Design with Discoverability

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "CLIs should prioritize human users... Discoverable CLIs have comprehensive help texts, provide lots of examples, suggest what command to run next."
2. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "The Heroku CLI is for humans before machines. Primary goal: usability."
3. [UX Patterns for CLI Tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html) - "Reduce time-to-value by showing example commands within the CLI itself. Implement command suggestions using similarity algorithms."

**Disagreement:** None found.

**Implication:** Lead help text with examples, suggest corrections for typos, show next steps in output.

---

### Claim 7: Error Messages Must Explain Why and Suggest Fixes

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "Catch errors and rewrite them for humans... 'Can't write to file.txt. You might need to make it writable by running chmod +w file.txt.'"
2. [UX Patterns for CLI Tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html) - "Error messages must explain *why* something failed and who's responsible. Provide actionable next steps."
3. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "Always handle errors gracefully and provide informative error messages."

**Disagreement:** None found.

**Implication:** Error messages should: (1) state what went wrong, (2) explain why, (3) suggest how to fix.

---

### Claim 8: Use Callbacks for Shared State and Global Options

**Confidence:** HIGH

**Evidence:**
1. [Typer Callback Tutorial](https://typer.tiangolo.com/tutorial/commands/callback/) - "Use @app.callback() to define global options like --verbose that modify shared state."
2. [Typer Context Tutorial](https://typer.tiangolo.com/tutorial/commands/context/) - "Access typer.Context, check ctx.invoked_subcommand, use ctx.obj for state storage."
3. [Click Complex Applications](https://click.palletsprojects.com/en/stable/complex/) - "Store Repo object in ctx.obj for child commands to access."

**Disagreement:** None found.

**Implication:** Use callbacks for global options (--verbose, --format, --config), store shared state in ctx.obj.

---

### Claim 9: Respect TTY Detection for Colors and Interactivity

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "Disable color when output is not an interactive TTY, NO_COLOR is set, TERM=dumb, or user passes --no-color."
2. [UX Patterns for CLI Tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html) - "Check whether the user's terminal supports [colors/emojis]. Otherwise, people will see weird characters."
3. [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide) - "User can disable with --no-color, COLOR=false, or when output isn't a tty."
4. [Rich Documentation](https://rich.readthedocs.io/) - "Rich provides automatic TTY detection and NO_COLOR support."

**Disagreement:** None found.

**Implication:** Use Rich for output formatting (automatic TTY detection), respect NO_COLOR environment variable.

---

### Claim 10: Avoid Common Anti-Patterns

**Confidence:** HIGH

**Evidence:**
1. [clig.dev](https://clig.dev/) - "Don't have ambiguous or similarly-named commands (update vs upgrade). Don't support catch-all subcommands. Don't allow arbitrary abbreviations."
2. [UX Patterns for CLI Tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html) - "Not enabling progressive discovery... Failing to validate user input... Ignoring terminal capabilities."
3. [Typer Project Rules](https://www.projectrules.ai/rules/typer) - "Avoid doing too much inside a single command function. Make CLI orchestrate logic rather than contain it."

**Disagreement:** None found.

**Implication:** Clearly differentiate command names, validate input early, keep command functions thin.

---

## Patterns and Paradigm Shifts

### Pattern 1: Declarative CLI Definition via Type Hints

Typer (and similar modern frameworks) represent a shift from imperative CLI definition to declarative. Instead of manually parsing arguments, type hints declare intent and the framework handles parsing, validation, help generation, and completion.

**Sources:** S01 (Typer), S16 (Medium)

### Pattern 2: Three-Layer Architecture for CLI Applications

Modern CLI best practices recommend separating:
1. **CLI Layer:** Argument parsing, output formatting, error presentation
2. **Service Layer:** Business logic, domain operations
3. **Data Layer:** File I/O, network, database

This enables testing business logic independently and supports multiple interfaces (CLI, API, TUI).

**Sources:** S19 (Structuring a CLI), S08 (PyTest with Eric)

### Pattern 3: Output Format as First-Class Concern

Major CLIs (AWS, Azure, Heroku, kubectl) now treat output format as a fundamental design concern, not an afterthought. The `--output`/`--format` flag is expected.

**Sources:** S09, S10 (AWS/Azure), S04 (Heroku)

### Pattern 4: Commands as Thin Orchestrators

Commands should not contain business logic. They orchestrate: parse input, call service layer, format output. This inverts the traditional "fat command" pattern.

**Sources:** S14, S19, clig.dev

### Pattern 5: Conversation Metaphor for CLI UX

clig.dev introduces the idea that CLI interaction is a "conversation" - users iterate through trial-and-error, explore, and learn. Good CLIs support this through suggestions, confirmations, and helpful errors.

**Sources:** S03 (clig.dev), S13 (UX Patterns)

---

## Gaps and Unknowns

### Gap 1: Typer-Specific Exception Handling Patterns

While general Python exception handling is well-documented, Typer-specific patterns for mapping exceptions to exit codes and user-friendly messages are less formalized. Most examples show basic `typer.Exit()` or `rai typer.BadParameter()`.

**Recommendation:** Create RaiSE-specific exception hierarchy with exit code mapping.

### Gap 2: Long-Running Command Patterns in Typer

Documentation on progress bars and long-running operations in Typer is minimal. Rich integration examples exist but aren't formalized as patterns.

**Recommendation:** Reference Rich documentation directly for progress patterns.

### Gap 3: Configuration File Patterns

While clig.dev discusses configuration precedence (flags > env > project config > user config), Typer doesn't have built-in config file support. Click has it but Typer doesn't expose it directly.

**Recommendation:** Use Pydantic Settings for configuration management.

### Gap 4: Plugin Architecture

No standard pattern for plugin/extension architectures in Typer-based CLIs.

**Recommendation:** Use setuptools entry points or explicit add_typer composition.

---

## Key Takeaways

1. **Flags over arguments** - more explicit, composable, future-proof
2. **Multiple output formats** - human (default), json (stable), table (scannable)
3. **Exception hierarchy with exit codes** - catch at boundary, distinct codes
4. **One file per command group** - maintainable organization pattern
5. **CliRunner for testing** - parametrize, test user perspective
6. **Rich for output** - automatic TTY detection, tables, progress
7. **Callbacks for global options** - --verbose, --format, ctx.obj for state
8. **Human-first design** - examples in help, suggestions, actionable errors
9. **Thin commands** - orchestrate, don't contain business logic
10. **Avoid anti-patterns** - ambiguous names, catch-all commands, abbreviations

---

*Synthesis created: 2026-02-05*
*Research: TYPER-CLI-BP-20260205*
