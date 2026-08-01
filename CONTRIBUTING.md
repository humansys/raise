# Contributing to RaiSE Commons

Thank you for your interest in contributing to RaiSE Commons.

## What This Repository Contains

RaiSE Commons includes both **methodology** and **tooling**:

- **Framework** — Methodology, katas, templates, governance artifacts
- **raise-cli** — CLI tool for governance operations (`src/raise_cli/`)

Contributions can focus on either area.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- Git

### Quick Start

```bash
# Clone and enter the repository
git clone https://github.com/humansys/raise.git
cd raise

# Install dependencies
uv sync

# Run CLI via uv
uv run rai --version
```

### Kimi Runtime Verification

Before validating Kimi Code CLI integration changes, capture the runtimes owned by
this checkout:

```bash
uv run python scripts/verify-kimi-runtime.py
```

The command emits JSON with the authoritative worktree RaiSE executable and version,
the Kimi executable and version, and optional information about a global `rai`.
Global-version drift is a warning; contributor and governance commands in this
repository must continue to use `uv run rai`.

### Running Tests

```bash
uv run pytest                          # All tests
uv run pytest --cov=src                # With coverage
uv run pytest tests/cli/               # Specific directory
```

### Code Quality

```bash
uv run ruff check packages/raise-cli/src packages/raise-cli/tests  # Linting
uv run ruff format --check packages/raise-cli/src packages/raise-cli/tests  # Formatting
uv run pyright                                          # Type checking
```

### Pre-commit Hooks

Install git hooks to catch lint/format issues before every commit:

```bash
git config core.hooksPath .githooks
```

The pre-commit hook runs `ruff check` and `ruff format --check` on
`packages/raise-cli/src` and `packages/raise-cli/tests`. If it blocks
your commit, run the following to auto-fix:

```bash
uv run ruff check --fix packages/raise-cli/src packages/raise-cli/tests
uv run ruff format packages/raise-cli/src packages/raise-cli/tests
git add -A
git commit
```

## How to Provide Feedback

### Questions and Discussion

Open an [Issue](../../issues) with the `question` label.

### Bug Reports

For documentation errors, broken links, or terminology inconsistencies:

1. Open an [Issue](../../issues)
2. Describe what you found
3. Include the file path and line number if applicable
4. Suggest a correction if you have one

### Suggestions

For methodology improvements or new content:

1. Open an [Issue](../../issues) with the `enhancement` label
2. Describe the proposed change
3. Explain the rationale

## Contribution Process

1. **Open an Issue** describing the change
2. **Fork** the repository
3. **Create a feature branch** from the active release branch (see Branch Model below)
4. **Make your changes** following the style guidelines
5. **Run tests and quality checks** (see Development Setup)
6. **Submit a Merge Request** targeting the active release branch

## Branch Model

RaiSE uses explicit release branches (ADR-033). Each long-lived branch carries its version target in its name:

| Branch | Purpose |
|--------|---------|
| `main` | Stable releases only — tagged commits, no direct work |
| `release/3.1.0` | Active development for RaiSE 3.1 |
| `release/2.4.0` | Maintenance for RaiSE 2.4 |

**For new contributions targeting 3.1:** branch from `release/3.1.0`.

```bash
git fetch origin
git checkout -b feat/my-feature origin/release/3.1.0
```

Hotfixes for a released version branch from that version's release branch and are cherry-picked forward as needed.

## Style Guidelines

### Terminology

Use canonical terminology from the [Glossary](framework/reference/glossary.md):

| Use | Don't Use |
|-----|-----------|
| Validation Gate | DoD, Definition of Done |
| Guardrail | Rule, constraint |
| RaiSE Engineer | Developer, user |
| Kata | Tutorial, lesson |

### Writing Style

- **Empowering, not prescriptive** — Provide frameworks, let users decide
- **Precise and unambiguous** — Every term has a specific meaning
- **Concise and direct** — Cover 80% of cases, avoid over-documentation
- **Action-oriented** — Focus on what users can do

### Language

- New content: American English
- File names and directories: Always English

### Format

- Markdown (CommonMark spec)
- Clear, action-oriented headings
- Numbered steps for instructions
- Tables for structured information

## EN/ES Documentation Parity

Every page in `docs/concepts/` and `docs/guides/` must have a Spanish equivalent in `docs/es/concepts/` or `docs/es/guides/`. This is enforced by CI (`ci-docs-i18n.yml`).

**When adding a new EN page:**

1. Create the EN page as usual.
2. Create the ES equivalent in the same PR — either a full translation or a stub:

```markdown
---
title: <Page Title>
---

!!! warning "Página pendiente de traducción"
    Esta página aún no está disponible en español.
    [Ver versión en inglés](../<page>.md)
```

3. Run the parity check locally before opening a PR:

```bash
python scripts/check-i18n-parity.py
```

To generate stubs automatically for all missing pages:

```bash
python scripts/check-i18n-parity.py --fix
```

**CLI pages** (`docs/cli/`) are warn-only — stubs are encouraged but not required.

## Review Checklist

Before submitting:

- [ ] Uses canonical terminology
- [ ] Active voice throughout
- [ ] Concise (no unnecessary words)
- [ ] Links use descriptive text
- [ ] American English spelling
- [ ] ES equivalent exists for any new EN page in concepts/ or guides/

---

*Thank you for contributing to RaiSE Commons.*
