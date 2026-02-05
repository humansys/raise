# Evidence Catalog: Python Security Research

> 25 sources collected and rated for secure Python development practices

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Sources** | 25 |
| **Very High Evidence** | 7 (28%) |
| **High Evidence** | 11 (44%) |
| **Medium Evidence** | 6 (24%) |
| **Low Evidence** | 1 (4%) |
| **Temporal Coverage** | 2021-2026 |

---

## Sources by Category

### 1. OWASP & Security Standards

**Source 1**: [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025 (continuously updated)
- **Key Finding**: Comprehensive security guidance including Input Validation, Authentication, Injection Prevention cheat sheets
- **Relevance**: Authoritative source for security best practices; Python-applicable patterns

**Source 2**: [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: A03 Software Supply Chain Failures is new; Broken Access Control remains #1
- **Relevance**: Defines priority security risks; supply chain security now critical

**Source 3**: [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: Allowlist over denylist; validate server-side; syntactic + semantic validation
- **Relevance**: Core input validation principles applicable to CLI args

---

### 2. Bandit Security Linter

**Source 4**: [Bandit Documentation - Test Plugins](https://bandit.readthedocs.io/en/latest/plugins/index.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: 40+ security checks including B101 (assert), B102 (exec), B301 (pickle), B601 (shell)
- **Relevance**: Core security linter for Python; all rules documented with examples

**Source 5**: [B101: assert_used](https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2025
- **Key Finding**: Assert removed with -O flag; don't use for security validation
- **Relevance**: Common mistake in production code

**Source 6**: [B105-B107: Hardcoded Password Detection](https://mcginniscommawill.com/posts/2025-05-27-hardcoded-password-detection-b105-b107/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025-05
- **Key Finding**: B105 (string), B106 (funcarg), B107 (default param) detect embedded secrets
- **Relevance**: Critical for preventing credential leaks

**Source 7**: [Bandit Python SAST Guide (DEV.to)](https://dev.to/angelvargasgutierrez/bandit-python-static-application-security-testing-guide-47l0)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Comprehensive Bandit setup guide with CI/CD integration patterns
- **Relevance**: Practical implementation guidance

---

### 3. Input Validation & Pydantic

**Source 8**: [Pydantic Official Documentation](https://docs.pydantic.dev/latest/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2026 (v2.x)
- **Key Finding**: Strict type enforcement, validators, custom types prevent malformed input
- **Relevance**: Core validation library for raise-cli

**Source 9**: [Pydantic Validation Layers for ML Input Sanitization](https://johal.in/pydantic-validation-layers-secure-python-ml-input-sanitization-2025/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Input vulnerabilities account for 62% of production ML failures; Pydantic as defense layer
- **Relevance**: Validates Pydantic as security boundary

**Source 10**: [Python Security Best Practices (Medium)](https://elshad-karimov.medium.com/top-10-python-security-best-practices-every-developer-should-follow-371159a54ebc)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Finding**: Validate/sanitize input, use type hints, avoid dynamic code execution
- **Relevance**: General security hygiene

---

### 4. Command & Code Injection Prevention

**Source 11**: [Command Injection in Python (Snyk)](https://snyk.io/blog/command-injection-python-prevention-examples/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: shell=True enables injection; use argument lists; shlex.quote for sanitization
- **Relevance**: Critical for subprocess security

**Source 12**: [Command Injection Cheat Sheet (Semgrep)](https://semgrep.dev/docs/cheat-sheets/python-command-injection)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Comprehensive patterns for safe subprocess use; avoid os.system entirely
- **Relevance**: Detection patterns for code review

**Source 13**: [Code Injection in Python (Semgrep)](https://semgrep.dev/docs/cheat-sheets/python-code-injection)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: eval(), exec(), compile() are dangerous; no safe alternative exists for untrusted input
- **Relevance**: Confirms prohibition of dynamic code execution

**Source 14**: [Python Subprocess Documentation](https://docs.python.org/3/library/subprocess.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2026
- **Key Finding**: Official warning about shell=True; recommends shlex for parsing
- **Relevance**: Authoritative guidance on subprocess security

---

### 5. Secret Management

**Source 15**: [Python Secrets Management (GitGuardian)](https://blog.gitguardian.com/how-to-handle-secrets-in-python/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Use env vars, python-dotenv, or secrets managers; never hardcode; keyring for desktop
- **Relevance**: Comprehensive secret management guide

**Source 16**: [Keyring for Secure Credential Storage (Medium)](https://medium.com/@forsytheryan/securely-storing-credentials-in-python-with-keyring-d8972c3bd25f)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Keyring uses OS-native secure storage (Keychain, Credential Locker, GNOME)
- **Relevance**: Desktop CLI secret storage pattern

**Source 17**: [detect-secrets (Microsoft Engineering Playbook)](https://microsoft.github.io/code-with-engineering-playbook/CI-CD/dev-sec-ops/secrets-management/recipes/detect-secrets/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Pre-commit hook with baseline file; enterprise-friendly; custom plugin API
- **Relevance**: CI/CD secret detection pattern

---

### 6. Dependency Security

**Source 18**: [pip-audit (PyPI)](https://pypi.org/project/pip-audit/)
- **Type**: Primary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: PyPA official tool; audits against Python Advisory Database; auto-fix capability
- **Relevance**: Primary dependency security tool

**Source 19**: [Dependency Security with pip-audit (McGinnis)](https://mcginniscommawill.com/posts/2025-01-27-dependency-security-pip-audit/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025-01
- **Key Finding**: Vulnerable dependencies affect downstream users; integrate in CI pipeline
- **Relevance**: Practical pip-audit implementation

**Source 20**: [Safety vs pip-audit Comparison (SixFeetUp)](https://www.sixfeetup.com/blog/safety-pip-audit-python-security-tools)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Finding**: Both tools complement each other; Safety uses Safety DB, pip-audit uses PyPI JSON API
- **Relevance**: Tool selection guidance

---

### 7. Path Traversal Prevention

**Source 21**: [Preventing Directory Traversal (Salvatore Security)](https://salvatoresecurity.com/preventing-directory-traversal-vulnerabilities-in-python/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Use pathlib.Path.resolve() + is_relative_to() for secure path handling
- **Relevance**: Core path traversal prevention technique

**Source 22**: [OpenStack Security Guidelines - File Paths](https://security.openstack.org/guidelines/dg_using-file-paths.html)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Two-layer defense: validate input + verify resolved path; whitelist when possible
- **Relevance**: Production-proven patterns from large project

---

### 8. Logging Security

**Source 23**: [Logging Sensitive Data Best Practices (BetterStack)](https://betterstack.com/community/guides/logging/sensitive-data/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Finding**: Use logging.Filter to mask PII; encrypt logs at rest; avoid hash-based obfuscation
- **Relevance**: Practical logging filter implementation

**Source 24**: [Handling Sensitive Data in Python (McGinnis)](https://mcginniscommawill.com/posts/2025-01-29-handling-sensitive-data/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025-01
- **Key Finding**: Overwrite sensitive variables after use; avoid string concatenation with secrets
- **Relevance**: Memory management for secrets

---

### 9. Cryptographic Security

**Source 25**: [Python secrets Module Documentation](https://docs.python.org/3/library/secrets.html)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2026
- **Key Finding**: Use secrets instead of random for tokens, passwords, URLs; CSPRNG-backed
- **Relevance**: Authoritative guidance on secure random generation

---

## Sources Not Used (Low Quality or Irrelevant)

- Multiple personal blog posts without corroboration
- Outdated Python 2.x documentation
- Framework-specific guides (Django, Flask) not applicable to CLI

---

*Generated: 2026-02-05*
