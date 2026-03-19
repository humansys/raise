# Guardrail: CI = Skills Parity

## 1. Principle

The CI pipeline and local gates MUST check the same things.
The single source of truth for gate commands is `.raise/manifest.yaml`.

Any change to a gate command updates the manifest first; all enforcement
points (local CLI, pre-commit hook, CI pipeline) derive from that manifest.
Drift between local and remote checks is a defect.

---

## 2. Architecture Flow

```
.raise/manifest.yaml  (source of truth)
        |
        +---> rai gate check --all     (local, on-demand)
        |         reads manifest keys
        |         runs all 5 gates
        |
        +---> pre-commit hook          (local, automatic on git commit)
        |         rai gate install-hook
        |         runs lint, format, type-check from manifest
        |         skips test_command (commit-time speed)
        |
        +---> .gitlab-ci.yml           (remote, on push / MR)
              test stage runs same commands
              adds coverage + security scanning
```

**How it works:**

1. `rai init` detects the project language and populates manifest
   keys (`test_command`, `lint_command`, `type_check_command`,
   `format_command`).
2. Gate implementations (`rai.gates` entry points in `pyproject.toml`)
   each read one manifest key and execute the configured command.
3. `rai gate check --all` loads every registered gate and runs them.
4. The pre-commit hook (`src/raise_cli/gates/hook.py`) loads the
   manifest and runs lint, format, and type-check commands directly.
5. The CI pipeline (`.gitlab-ci.yml`) runs the same commands in the
   `test` stage.

---

## 3. Current Commands

Commands as configured in `.raise/manifest.yaml` for raise-commons:

| Gate | Manifest Key | Command | Pre-commit | CI |
|------|-------------|---------|:----------:|:--:|
| Tests | `test_command` | `uv run pytest --tb=short` | No | Yes |
| Lint | `lint_command` | `uv run ruff check` | Yes | Yes |
| Format | `format_command` | `uv run ruff format --check` | Yes | Yes |
| Types | `type_check_command` | `uv run pyright` | Yes | Yes |
| Coverage | `test_command` + flags | `uv run pytest --cov...` | No | Yes |

**Entry points** (from `pyproject.toml [project.entry-points."rai.gates"]`):

| Entry Point | Implementation |
|-------------|---------------|
| `tests` | `raise_cli.gates.builtin.tests:TestGate` |
| `lint` | `raise_cli.gates.builtin.lint:LintGate` |
| `types` | `raise_cli.gates.builtin.types:TypeGate` |
| `format` | `raise_cli.gates.builtin.format:FormatGate` |
| `coverage` | `raise_cli.gates.builtin.coverage:CoverageGate` |

---

## 4. Developer Checklist -- Adding or Changing a Gate

When adding a new gate command or modifying an existing one:

1. **Update `.raise/manifest.yaml`** -- add or change the relevant key
   under `project:`.
2. **Verify locally** -- run `rai gate check --all` and confirm the new
   or changed gate passes.
3. **Update CI if needed** -- if the command changed, update the
   `script:` section in `.gitlab-ci.yml` to match.
4. **Reinstall hook** -- run `rai gate install-hook --force` so the
   pre-commit hook picks up the new manifest values.
5. **Verify hook** -- stage a file and run `git commit` to confirm the
   hook executes the expected checks.

If adding a completely new gate (not just changing a command):

6. **Create gate implementation** -- add a new module in
   `src/raise_cli/gates/builtin/` implementing the `GateProtocol`.
7. **Register entry point** -- add the gate to
   `[project.entry-points."rai.gates"]` in `pyproject.toml`.
8. **Decide hook inclusion** -- update `_HOOK_COMMANDS` in
   `src/raise_cli/gates/hook.py` if the gate should run at commit time.
9. **Update this document** -- add the gate to the Current Commands
   table above.

---

## 5. Known Asymmetries

These differences between enforcement points are **intentional**:

| Asymmetry | Reason |
|-----------|--------|
| Pre-commit skips `test_command` | Tests are too slow for commit-time feedback. Tests run in CI and via `rai gate check --all`. |
| Pre-commit skips `coverage` | Coverage collection adds overhead; only needed in CI for reporting. |
| CI runs Snyk (SCA, SAST, IaC) | Security scanning requires network access and external tooling not suitable for local gates. |
| CI runs SonarQube | Code analysis server not available locally. |
| CI runs GitLab SAST, Secret Detection, Dependency Scanning | GitLab-native templates, remote-only. |

These asymmetries are acceptable because:
- All **code quality** gates (lint, format, types) run in both local and remote contexts.
- Tests run locally via `rai gate check --all` and in CI; only the pre-commit hook skips them.
- Security scanning is additive (CI-only) and does not overlap with code quality gates.

---

## 6. Cross-references

- [Gate-Code governance document](../../gates/gate-code.md) -- full gate specification and validation criteria
- [S474.2 story](../../../work/epics/e474-gate-reliability/stories/s474.2-scope.md) -- manifest-driven gates technical design
- [S474.4 pre-commit hook](../../../src/raise_cli/gates/hook.py) -- hook implementation
- [Manifest schema](../../../src/raise_cli/onboarding/manifest.py) -- manifest loading and validation
- [CI pipeline](../../../.gitlab-ci.yml) -- remote enforcement
- [Gate entry points](../../../pyproject.toml) -- `[project.entry-points."rai.gates"]` section
