# Contributing to RaiSE Commons

Thank you for your interest in contributing to RaiSE Commons.

## What This Repository Contains

RaiSE Commons includes both **methodology** and **tooling**:

- **Framework** — Methodology, katas, templates, governance artifacts
- **raise-cli** — CLI tool for governance operations (`src/raise_cli/`)

Contributions can focus on either area.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- Git

### Quick Start

```bash
# Clone and enter the repository
git clone https://gitlab.com/humansys/raise-commons.git
cd raise-commons

# Install dependencies
uv sync

# Run CLI via uv
uv run raise --version
```

### Recommended: direnv for Seamless CLI Access

To use `raise` directly (without `uv run` prefix):

```bash
# Install direnv (Ubuntu/Debian)
sudo apt install direnv

# Add hook to your shell (~/.bashrc or ~/.zshrc)
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc  # or ~/.zshrc for zsh

# Restart your shell or source the config
source ~/.bashrc

# In the project directory, create and allow .envrc
echo 'source .venv/bin/activate' > .envrc
direnv allow

# Now 'raise' works directly
raise --version
```

direnv auto-activates the virtual environment when you enter the project directory.

### Running Tests

```bash
uv run pytest                          # All tests
uv run pytest --cov=src                # With coverage
uv run pytest tests/cli/               # Specific directory
```

### Code Quality

```bash
uv run ruff check .                    # Linting
uv run ruff format .                   # Formatting
uv run pyright --strict src/           # Type checking
```

## How to Provide Feedback

### Questions and Discussion

Open a [GitLab Issue](../../issues) with the `question` label.

### Bug Reports

For documentation errors, broken links, or terminology inconsistencies:

1. Open a [GitLab Issue](../../issues)
2. Describe what you found
3. Include the file path and line number if applicable
4. Suggest a correction if you have one

### Suggestions

For methodology improvements or new content:

1. Open a [GitLab Issue](../../issues) with the `enhancement` label
2. Describe the proposed change
3. Explain the rationale

## Contribution Process

1. **Open an Issue** describing the change
2. **Fork** the repository
3. **Create a feature branch** from `v2` (development branch)
4. **Make your changes** following the style guidelines
5. **Run tests and quality checks** (see Development Setup)
6. **Submit a Merge Request** referencing the issue

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

## Review Checklist

Before submitting:

- [ ] Uses canonical terminology
- [ ] Active voice throughout
- [ ] Concise (no unnecessary words)
- [ ] Links use descriptive text
- [ ] American English spelling

## Code of Conduct

Be respectful and constructive. Focus on improving the framework for everyone.

---

*Thank you for contributing to RaiSE Commons.*
