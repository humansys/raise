# Research: Secure Python Development Practices

> Evidence-based security guidelines for Python CLI tools with Pydantic and Typer

---

## Research Metadata

| Field | Value |
|-------|-------|
| **Research ID** | RES-PYTHON-SEC-20260205 |
| **Primary Question** | What are the essential secure Python development practices for CLI tools built with Pydantic, Typer, and standard library? |
| **Decision Context** | Security guardrails for raise-cli (governance/solution/guardrails.md) |
| **Depth** | Standard (4-8h equivalent) |
| **Tool Used** | WebSearch + manual synthesis |
| **Search Date** | 2026-02-05 |
| **Researcher** | Rai |
| **Total Sources** | 25 |

---

## 15-Minute Overview

### Key Findings (TL;DR)

1. **Input validation is #1 priority** - Use Pydantic for strict type enforcement; user input is the primary attack vector (HIGH confidence)

2. **Never use dangerous functions with untrusted input** - `eval()`, `exec()`, `pickle.loads()`, `yaml.load()` enable RCE (VERY HIGH confidence)

3. **Subprocess requires shell=False** - Always pass arguments as list, use `shlex` for parsing (VERY HIGH confidence)

4. **Path traversal prevention requires pathlib** - Use `Path.resolve()` + ancestry checks (HIGH confidence)

5. **Secrets belong in environment or keyring** - Never hardcode, use `python-dotenv` for dev, keyring for desktop (HIGH confidence)

6. **Dependency scanning is mandatory** - Use `pip-audit` and `detect-secrets` in CI (HIGH confidence)

7. **Logging must filter PII/secrets** - Implement custom log filters, never log passwords (HIGH confidence)

8. **Use `secrets` module for tokens** - Never `random` for security purposes (VERY HIGH confidence)

9. **Bandit catches 80% of issues** - Run with `-ll` flag in pre-commit (HIGH confidence)

### Security Checklist (Quick Reference)

See `security-checklist.md` for the actionable checklist.

---

## Navigation

| Document | Purpose |
|----------|---------|
| `sources/evidence-catalog.md` | All 25 sources with ratings |
| `synthesis.md` | Triangulated claims with evidence |
| `recommendation.md` | Actionable recommendations |
| `security-checklist.md` | Copy-paste checklist for guardrails |

---

## Secondary Questions Covered

1. OWASP Python security guidelines
2. Input validation and sanitization (CLI args)
3. Secret management (env vars, keyring)
4. Dependency security (pip-audit, safety)
5. Code injection prevention (eval, exec, subprocess)
6. Path traversal prevention (pathlib)
7. Logging security (no PII/secrets)
8. SonarQube/SonarCloud Python issues
9. Bandit security linter rules

---

*Generated: 2026-02-05*
*Version: 1.0*
