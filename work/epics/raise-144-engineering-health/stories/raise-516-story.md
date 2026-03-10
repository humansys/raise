# RAISE-516: Move raise-core into src/ and eliminate uv workspace

## User Story

As a **contributor to the public GitHub repo**,
I want **the project to build without workspace members**,
so that **CI passes and `uv sync` works out of the box**.

## Acceptance Criteria

```gherkin
Scenario: GitHub CI passes without pyproject.toml patching
  Given the public GitHub repo excludes packages/
  When uv sync --extra dev runs
  Then it succeeds without workspace resolution errors

Scenario: raise-core modules importable from src/
  Given raise_core/ lives under src/ alongside raise_cli/
  When importing from raise_core
  Then all existing imports resolve correctly

Scenario: Private code excluded from public repo
  Given src/rai_pro/ contains private code
  When sync-github.sh runs
  Then src/rai_pro/ is excluded from the GitHub mirror
```
