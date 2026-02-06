# Evidence Catalog: Typer CLI Design Best Practices

> Research ID: TYPER-CLI-BP-20260205
> Search Date: 2026-02-05
> Tool Used: WebSearch + Context7 + WebFetch
> Researcher: Rai
> Total Sources: 22

---

## Summary Statistics

| Evidence Level | Count | Percentage |
|----------------|-------|------------|
| Very High | 5 | 23% |
| High | 9 | 41% |
| Medium | 7 | 32% |
| Low | 1 | 4% |

**Temporal Coverage:** 2013-2026 (majority 2022-2026)

---

## Sources

### S01: Typer Official Documentation

**Source:** [Typer Documentation](https://typer.tiangolo.com/)
- **Type:** Primary
- **Evidence Level:** Very High
- **Date:** 2026 (actively maintained)
- **Key Finding:** Typer provides official patterns for command groups, subcommands, callbacks, testing, and help text organization using Python type hints.
- **Relevance:** Authoritative source for all Typer-specific patterns; basis for implementation decisions.

---

### S02: Click Official Documentation

**Source:** [Click Documentation](https://click.palletsprojects.com/)
- **Type:** Primary
- **Evidence Level:** Very High
- **Date:** 2026 (v8.3.x)
- **Key Finding:** Click (underlying Typer) provides patterns for command groups, context passing, testing with CliRunner, and complex CLI architectures.
- **Relevance:** Understanding Click patterns enables advanced Typer usage since Typer is built on Click.

---

### S03: Command Line Interface Guidelines (clig.dev)

**Source:** [Command Line Interface Guidelines](https://clig.dev/)
- **Type:** Primary
- **Evidence Level:** Very High
- **Date:** 2020-2026 (community maintained)
- **Key Finding:** Comprehensive human-first CLI design principles covering output formatting, error handling, help text, arguments/flags, composability, and robustness.
- **Relevance:** Industry-standard reference for CLI UX; triangulates with other sources on all major claims.

---

### S04: Heroku CLI Style Guide

**Source:** [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide)
- **Type:** Primary
- **Evidence Level:** Very High
- **Date:** 2024-2026 (production CLI)
- **Key Finding:** Production-proven patterns: topics+commands structure, flags over arguments, JSON/terse output modes, color usage, backward compatibility requirements.
- **Relevance:** Battle-tested patterns from a major production CLI; validates clig.dev recommendations.

---

### S05: Rich Library Documentation

**Source:** [Rich Documentation](https://rich.readthedocs.io/)
- **Type:** Primary
- **Evidence Level:** Very High
- **Date:** 2026 (v14.x)
- **Key Finding:** Rich provides tables, panels, progress bars, and formatting utilities for terminal output with automatic TTY detection.
- **Relevance:** Recommended output formatting library for Typer applications.

---

### S06: Typer Testing Tutorial

**Source:** [Testing - Typer](https://typer.tiangolo.com/tutorial/testing/)
- **Type:** Primary
- **Evidence Level:** High
- **Date:** 2026
- **Key Finding:** CliRunner pattern for testing: invoke commands, check exit_code, assert on output, simulate user input.
- **Relevance:** Official testing approach for Typer applications.

---

### S07: Click Testing Documentation

**Source:** [Testing Click Applications](https://click.palletsprojects.com/en/stable/testing/)
- **Type:** Primary
- **Evidence Level:** High
- **Date:** 2026
- **Key Finding:** CliRunner provides isolated_filesystem(), input simulation, and Result object with output/exit_code/exception capture.
- **Relevance:** Advanced testing patterns applicable to Typer via Click.

---

### S08: PyTest with Eric - CLI Testing

**Source:** [How To Test CLI Applications With Pytest, Argparse And Typer](https://pytest-with-eric.com/pytest-advanced/pytest-argparse-typer/)
- **Type:** Secondary
- **Evidence Level:** High
- **Date:** 2024
- **Key Finding:** Best practices: parametrize tests, test from user perspective, validate error messages, separate business logic from CLI.
- **Relevance:** Practical testing patterns with pytest integration.

---

### S09: AWS CLI Output Format Documentation

**Source:** [Setting the output format in AWS CLI](https://docs.aws.amazon.com/cli/v1/userguide/cli-usage-output-format.html)
- **Type:** Primary
- **Evidence Level:** High
- **Date:** 2026
- **Key Finding:** Multiple output formats (json, table, text, yaml); table for human readability, json for machine parsing, --query for filtering.
- **Relevance:** Production-proven output format patterns from widely-used CLI.

---

### S10: Azure CLI Output Format Documentation

**Source:** [Output formats for Azure CLI commands](https://learn.microsoft.com/en-us/cli/azure/format-output-azure-cli)
- **Type:** Primary
- **Evidence Level:** High
- **Date:** 2026
- **Key Finding:** Similar patterns to AWS: json, jsonc, none, table, tsv, yaml; emphasizes choosing format based on use case.
- **Relevance:** Confirms AWS patterns; industry consensus on output formats.

---

### S11: Exit Code Best Practices

**Source:** [Best practices when designating exit codes](https://chrisdown.name/2013/11/03/exit-code-best-practises.html)
- **Type:** Secondary
- **Evidence Level:** High
- **Date:** 2013 (still referenced)
- **Key Finding:** Exit 0 for success, non-zero for errors; distinct codes for different failure modes; avoid codes >125.
- **Relevance:** Foundational reference for exit code conventions.

---

### S12: Python Exit Codes and Shell Scripts

**Source:** [Controlling Python Exit Codes and Shell Scripts](https://henryleach.com/2025/02/controlling-python-exit-codes-and-shell-scripts/)
- **Type:** Secondary
- **Evidence Level:** High
- **Date:** 2025
- **Key Finding:** Raise exceptions in business logic, catch at CLI boundary, map to exit codes; use custom exception types.
- **Relevance:** Python-specific patterns for exception-to-exit-code mapping.

---

### S13: UX Patterns for CLI Tools

**Source:** [UX patterns for CLI tools](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html)
- **Type:** Secondary
- **Evidence Level:** High
- **Date:** 2022
- **Key Finding:** Colors/emojis with TTY detection, error messages with "why" and next steps, command suggestions via Damerau-Levenshtein, interactive modes complement non-interactive.
- **Relevance:** Comprehensive UX patterns with anti-pattern identification.

---

### S14: Typer Project Rules (projectrules.ai)

**Source:** [Typer CLI Best Practices and Coding Standards](https://www.projectrules.ai/rules/typer)
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Date:** 2025
- **Key Finding:** Design commands stateless, orchestrate logic don't contain it, use add_typer for organization, comprehensive help messages.
- **Relevance:** Aggregated best practices; triangulates other sources.

---

### S15: Real Python - CLI Testing Techniques

**Source:** [4 Techniques for Testing Python Command-Line Apps](https://realpython.com/python-cli-testing/)
- **Type:** Secondary
- **Evidence Level:** Medium
- **Date:** 2024
- **Key Finding:** Multiple testing approaches: CliRunner, subprocess, mocking, property-based testing with Hypothesis.
- **Relevance:** Alternative testing approaches and when to use each.

---

### S16: Medium - Typer Powerful Python CLI Framework

**Source:** [Typer: Powerful Python CLI Framework with Type Hints](https://medium.com/top-python-libraries/typer-powerful-python-cli-framework-with-type-hints-6b16654daac7)
- **Type:** Tertiary
- **Evidence Level:** Medium
- **Date:** 2024
- **Key Finding:** Typer leverages type hints for automatic validation, help text generation, and shell completion.
- **Relevance:** Overview of Typer's type-hint-driven approach.

---

### S17: GitHub - Typer Repository

**Source:** [GitHub - fastapi/typer](https://github.com/fastapi/typer)
- **Type:** Primary
- **Evidence Level:** Medium
- **Date:** 2026 (17k+ stars)
- **Key Finding:** Active development, extensive examples, community contributions, integration with Rich for enhanced output.
- **Relevance:** Source repository; community validation through stars/issues.

---

### S18: Thoughtworks - CLI Design Guidelines

**Source:** [Elevate developer experiences with CLI design guidelines](https://www.thoughtworks.com/en-us/insights/blog/engineering-effectiveness/elevate-developer-experiences-cli-design-guidelines)
- **Type:** Secondary
- **Evidence Level:** Medium
- **Date:** 2024
- **Key Finding:** CLI design as developer experience, consistency across commands, progressive disclosure, error messages as documentation.
- **Relevance:** Enterprise perspective on CLI design.

---

### S19: Medium - Structuring a CLI

**Source:** [Structuring a CLI](https://medium.com/pon-tech-talk/structuring-a-cli-22e2492717de)
- **Type:** Secondary
- **Evidence Level:** Medium
- **Date:** 2023
- **Key Finding:** Separation of concerns: CLI layer (Typer), service layer (business logic), data layer; enables testing at each level.
- **Relevance:** Architectural pattern for larger CLI applications.

---

### S20: ArjanCodes - Rich Python Library for CLI

**Source:** [Rich Python Library for Advanced CLI Design](https://arjancodes.com/blog/rich-python-library-for-interactive-cli-tools/)
- **Type:** Secondary
- **Evidence Level:** Medium
- **Date:** 2024
- **Key Finding:** Integration patterns for Rich with Typer: tables, panels, progress bars, markdown rendering.
- **Relevance:** Practical integration examples.

---

### S21: InfoQ - CLI Guidelines Interview

**Source:** [CLI Guidelines Aim to Help You Write Better CLI Programs](https://www.infoq.com/news/2020/12/cli-guidelines-qa/)
- **Type:** Secondary
- **Evidence Level:** Medium
- **Date:** 2020
- **Key Finding:** clig.dev authors discuss motivation: lack of comprehensive resources, lessons from Docker Compose, human-first design philosophy.
- **Relevance:** Context for clig.dev authority; interviews with authors.

---

### S22: relay-sh - 3 Commandments for CLI Design

**Source:** [3 Commandments for CLI Design](https://medium.com/relay-sh/command-line-ux-in-2020-e537018ebb69)
- **Type:** Tertiary
- **Evidence Level:** Low
- **Date:** 2020
- **Key Finding:** Never require prompts, use non-standard conventions carefully, validate input immediately.
- **Relevance:** Quick reference; partially overlaps with clig.dev.

---

## Source Type Distribution

| Type | Count |
|------|-------|
| Primary | 10 |
| Secondary | 9 |
| Tertiary | 3 |

---

## Keywords Searched

- "Typer CLI design best practices"
- "Python CLI best practices error handling exit codes"
- "CLI output formats JSON table human readable"
- "Typer Click CLI testing pytest CliRunner"
- "CLI design anti-patterns common mistakes"
- "clig.dev command line interface guidelines"
- "Typer callback context state management"
- "Rich Python CLI output formatting"

---

*Evidence catalog created: 2026-02-05*
*Research: TYPER-CLI-BP-20260205*
