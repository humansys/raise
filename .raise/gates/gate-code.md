---
id: gate-code
fase: 6
titulo: "Gate-Code: Manifest-Driven Code Validation"
blocking: true
version: 2.0.0
---

# Gate-Code: Manifest-Driven Code Validation

## Purpose

Verify that implemented code passes all quality checks before merge.
All automated gates read their commands from `.raise/manifest.yaml`,
making them language-agnostic and project-configurable.

## When to Apply

- After completing implementation tasks
- Before creating a Pull Request
- As pre-merge checklist

---

## Automated Gates (5 total)

All gates are registered via `rai.gates` entry points and executed
by `rai gate check --all`. Each reads its command from the manifest.

| Gate | Manifest Key | Default (Python) | Purpose |
|------|-------------|-------------------|---------|
| **gate-tests** | `test_command` | `uv run pytest --tb=short` | All tests pass |
| **gate-lint** | `lint_command` | `uv run ruff check` | No lint errors |
| **gate-types** | `type_check_command` | `uv run pyright` | No type errors |
| **gate-format** | `format_command` | `uv run ruff format --check` | Code formatting passes |
| **gate-coverage** | `test_command` + coverage flags | `uv run pytest --cov` | Coverage collection succeeds |

### Skip Behavior

If a manifest key is not configured (null), the gate **skips** with
`passed=True` and a "not configured" message. This allows projects
to opt out of specific checks without failing.

### Manifest Configuration

Commands are set in `.raise/manifest.yaml` during `rai init`:

```yaml
project:
  test_command: "uv run pytest --tb=short"
  lint_command: "uv run ruff check"
  type_check_command: "uv run pyright"
  format_command: "uv run ruff format --check"
```

Language detection populates these automatically for 13 supported
languages. Override by editing the manifest directly.

---

## Validation Criteria

### Must Pass (Automated)

| # | Criterion | Gate |
|---|-----------|------|
| 1 | Tests pass | gate-tests |
| 2 | Linting clean | gate-lint |
| 3 | No type errors | gate-types |
| 4 | Formatting correct | gate-format |
| 5 | Coverage collection succeeds | gate-coverage |

### Must Pass (Manual)

| # | Criterion | Verification |
|---|-----------|--------------|
| 6 | AC covered | Each acceptance criterion implemented |
| 7 | Guardrails followed | Code follows project guardrails |
| 8 | Human review | Orchestrator has reviewed the code |
| 9 | Clean commits | Messages follow convention |

### Recommended

| # | Criterion | Verification |
|---|-----------|--------------|
| 10 | Coverage threshold | >= 80% on new code |
| 11 | Documentation | Public functions documented |
| 12 | No regressions | Existing tests still passing |

---

## Quick Checklist

```bash
# Run all automated gates
uv run rai gate check --all

# Or run individually
uv run pytest --tb=short        # tests
uv run ruff check               # lint
uv run pyright                  # types
uv run ruff format --check      # format
```

---

## Validation Process

### Pre-PR
1. Run `rai gate check --all`
2. Self-review the code
3. Verify against acceptance criteria

### PR Creation
```bash
# Verify everything passes
uv run rai gate check --all

# Push and create PR
git push origin story/sN.M/name
```

### Post-PR
1. Code review by peer
2. CI/CD pipeline
3. Merge if all gates pass

---

## Escalation Triggers

| Condition | Action |
|-----------|--------|
| Tests fail without clear cause | Debug before continuing |
| Guardrail impossible to meet | Escalate to Architect |
| Code incomprehensible to reviewer | Refactor before merge |
| Performance degraded | Profiling before merge |

---

## References

- Gate implementations: `src/raise_cli/gates/builtin/`
- Manifest schema: `src/raise_cli/onboarding/manifest.py`
- Language detection: `src/raise_cli/onboarding/detection.py`
- Gate protocol: `src/raise_cli/gates/protocol.py`

---

## See Also

- [CI=Skills Parity Guardrail](../governance/guardrails/ci-skills-parity.md) -- documents how CI pipeline, pre-commit hook, and local gates stay aligned through the manifest
