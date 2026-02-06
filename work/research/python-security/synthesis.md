# Synthesis: Secure Python Development Practices

> Triangulated claims with evidence from 25 sources

---

## Major Claims (Triangulated)

### Claim 1: Input Validation Must Be Defense-in-Depth with Pydantic as Primary Layer

**Confidence**: HIGH

**Evidence**:
1. [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) - "Input validation should happen as early as possible... implement both syntactic and semantic validation"
2. [Pydantic Validation Layers](https://johal.in/pydantic-validation-layers-secure-python-ml-input-sanitization-2025/) - "Input vulnerabilities account for 62% of production failures; Pydantic provides gold standard defense"
3. [Python Security Best Practices](https://elshad-karimov.medium.com/top-10-python-security-best-practices-every-developer-should-follow-371159a54ebc) - "User input is the #1 attack vector; validate and sanitize to prevent injection attacks"

**Disagreement**: None found

**Implication**: All CLI input (arguments, environment variables, file content) must pass through Pydantic models before processing. Create strict validators for paths, identifiers, and any string that will be used in commands.

---

### Claim 2: Dynamic Code Execution (eval/exec) Must Be Prohibited with Untrusted Input

**Confidence**: VERY HIGH

**Evidence**:
1. [Code Injection Cheat Sheet (Semgrep)](https://semgrep.dev/docs/cheat-sheets/python-code-injection) - "There is no secure replacement for using exec() or eval() with untrusted input"
2. [Code Injection Prevention (Snyk)](https://snyk.io/blog/code-injection-python-prevention-examples/) - "eval() and exec() can be dangerous if used to execute dynamic content... leads to code injection vulnerabilities"
3. [Bandit B102](https://bandit.readthedocs.io/en/latest/plugins/index.html) - Security test specifically for exec/eval usage; flags as high severity

**Disagreement**: Some sources mention "restricted globals" as mitigation, but [Semgrep](https://semgrep.dev/docs/cheat-sheets/python-code-injection) explicitly warns: "Don't try to make exec safe with tricks such as `{'__builtins__':{}}`"

**Implication**: Completely prohibit eval(), exec(), compile() on any data that could be user-influenced. If dynamic behavior needed, use safe alternatives (AST parsing for analysis only, dispatch tables for selection).

---

### Claim 3: Subprocess Calls Require shell=False and Argument Lists

**Confidence**: VERY HIGH

**Evidence**:
1. [Python subprocess Documentation](https://docs.python.org/3/library/subprocess.html) - "Using shell=True is dangerous because it propagates current shell settings and variables"
2. [Command Injection (Snyk)](https://snyk.io/blog/command-injection-python-prevention-examples/) - "When shell=False (default), subprocess passes arguments directly to the program without shell interpretation, preventing command injection"
3. [Command Injection (Semgrep)](https://semgrep.dev/docs/cheat-sheets/python-command-injection) - "Use shlex.split to correctly parse a command string into an array and shlex.quote to sanitize input"

**Disagreement**: None found

**Implication**:
```python
# NEVER
subprocess.run(f"git log {user_input}", shell=True)

# ALWAYS
subprocess.run(["git", "log", shlex.quote(user_input)], shell=False)
```

---

### Claim 4: Deserialization of Untrusted Data (pickle, yaml.load) Enables RCE

**Confidence**: VERY HIGH

**Evidence**:
1. [Insecure Deserialization (Semgrep)](https://semgrep.dev/docs/learn/vulnerabilities/insecure-deserialization/python) - "Python's pickle should never be used to process untrusted input... leads to Remote Code Execution"
2. [Insecure Deserialization Attacks (SecureLayer7)](https://blog.securelayer7.net/insecure-deserialization-attacks-with-python-pickle-module/) - "By design, deserialization can execute code, meaning attacker-controlled input can run arbitrary commands"
3. [Bandit B301](https://bandit.readthedocs.io/en/latest/plugins/index.html) - Specifically flags pickle usage; recommends JSON as safe alternative

**Disagreement**: None found

**Implication**:
- Never use `pickle.loads()` on untrusted data
- Use `yaml.safe_load()` instead of `yaml.load()`
- Prefer JSON for serialization/deserialization
- If pickle required for internal use, add cryptographic signature verification

---

### Claim 5: Path Traversal Prevention Requires pathlib with Ancestry Verification

**Confidence**: HIGH

**Evidence**:
1. [Preventing Directory Traversal (Salvatore)](https://salvatoresecurity.com/preventing-directory-traversal-vulnerabilities-in-python/) - "Use Path.resolve() for both document root and requested path... checking that document root is an ancestor is more precise than string comparison"
2. [OpenStack Security Guidelines](https://security.openstack.org/guidelines/dg_using-file-paths.html) - "Using two layers of defense: validate user input before processing, and compare input with whitelist of permitted values"
3. [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal) - "Canonical path validation required; reject paths containing .. sequences"

**Disagreement**: None found

**Implication**:
```python
def safe_path(base: Path, user_input: str) -> Path:
    """Resolve path and verify it's within base directory."""
    resolved = (base / user_input).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError("Path traversal detected")
    return resolved
```

---

### Claim 6: Secrets Must Never Be Hardcoded; Use Environment Variables or OS Keyring

**Confidence**: HIGH

**Evidence**:
1. [Python Secrets Management (GitGuardian)](https://blog.gitguardian.com/how-to-handle-secrets-in-python/) - "Never hardcode secrets; use environment variables for deployment, keyring for desktop apps"
2. [Bandit B105-B107](https://mcginniscommawill.com/posts/2025-05-27-hardcoded-password-detection-b105-b107/) - "When you embed a password directly in source code, you're creating a permanent record... Git remembers everything"
3. [detect-secrets (Microsoft)](https://microsoft.github.io/code-with-engineering-playbook/CI-CD/dev-sec-ops/secrets-management/recipes/detect-secrets/) - "Pre-commit hook with baseline file prevents new secrets from being committed"

**Disagreement**: Some argue environment variables are not truly secure (can be viewed by other processes). Mitigation: Use secrets managers for production, keyring for interactive CLI.

**Implication**:
- Development: `python-dotenv` with `.env` in `.gitignore`
- Desktop CLI: `keyring` library for OS-native secure storage
- Production: HashiCorp Vault, AWS Secrets Manager, or equivalent
- CI/CD: Platform secret management (GitLab CI variables, GitHub Secrets)

---

### Claim 7: Dependency Scanning Must Be Part of CI Pipeline

**Confidence**: HIGH

**Evidence**:
1. [OWASP Top 10:2025](https://owasp.org/Top10/2025/) - "A03 Software Supply Chain Failures is new category; highest average exploit and impact scores from CVEs"
2. [pip-audit (PyPI)](https://pypi.org/project/pip-audit/) - "Official PyPA tool; audits against Python Advisory Database; can automatically fix vulnerabilities"
3. [Safety vs pip-audit](https://www.sixfeetup.com/blog/safety-pip-audit-python-security-tools) - "Both tools complement each other; integrate in CI for comprehensive coverage"

**Disagreement**: None found

**Implication**: Add to CI pipeline:
```yaml
- pip-audit --require-hashes --strict
- safety check --full-report
```

---

### Claim 8: Logging Must Filter Sensitive Data Using Custom Filters

**Confidence**: HIGH

**Evidence**:
1. [Logging Sensitive Data (BetterStack)](https://betterstack.com/community/guides/logging/sensitive-data/) - "Use logging.Filter to mask sensitive data; define regex patterns for PII and replace with asterisks"
2. [Handling Sensitive Data (McGinnis)](https://mcginniscommawill.com/posts/2025-01-29-handling-sensitive-data/) - "Request URLs are typically logged by proxies... if endpoints contain sensitive data, it ends up in logs"
3. [Sentry Sensitive Data](https://docs.sentry.io/platforms/python/guides/logging/data-management/sensitive-data/) - "Configure scrubbing for credentials, tokens, PII before sending to logging services"

**Disagreement**: Hash-based obfuscation sometimes suggested, but [BetterStack](https://betterstack.com/community/guides/logging/sensitive-data/) warns: "When input domain is small (SSNs), hashes can be reversed by running all inputs through function"

**Implication**:
```python
class SensitiveDataFilter(logging.Filter):
    PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'password=***'),
        (r'token["\']?\s*[:=]\s*["\']?[^"\'\s]+', 'token=***'),
    ]

    def filter(self, record):
        for pattern, replacement in self.PATTERNS:
            record.msg = re.sub(pattern, replacement, str(record.msg), flags=re.I)
        return True
```

---

### Claim 9: Use secrets Module Instead of random for Security Tokens

**Confidence**: VERY HIGH

**Evidence**:
1. [Python secrets Documentation](https://docs.python.org/3/library/secrets.html) - "secrets should be used in preference to random, which is designed for modelling and simulation, not security"
2. [CSPRNG (Snyk)](https://snyk.io/blog/csprng-random-algorithms-need-security-too/) - "Random module uses Mersenne Twister, which is predictable; secrets uses OS-provided CSPRNG"
3. [PEP 506](https://peps.python.org/pep-0506/) - Official rationale for secrets module: "common task of generating tokens requires cryptographic randomness"

**Disagreement**: None found

**Implication**:
```python
# NEVER
token = ''.join(random.choices(string.ascii_letters, k=32))

# ALWAYS
token = secrets.token_urlsafe(32)
```

---

### Claim 10: Assert Statements Must Not Be Used for Security Validation

**Confidence**: HIGH

**Evidence**:
1. [Bandit B101](https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html) - "Assert is removed when compiling to optimized byte code (python -O); should not be used for runtime validation"
2. [Ruff S101](https://docs.astral.sh/ruff/rules/assert/) - "Assertions are disabled when Python runs with optimization; use explicit error handling instead"
3. [Bandit Python Assert (Medium)](https://medium.com/pareture/bandit-python-assert-e4b23cb4c2ab) - "Assert for debugging/testing only; raise explicit exceptions for validation"

**Disagreement**: None found

**Implication**:
```python
# NEVER (for security validation)
assert user.is_authorized, "Unauthorized"

# ALWAYS
if not user.is_authorized:
    raise PermissionError("Unauthorized")
```

---

## Patterns & Paradigm Shifts

### Pattern 1: Supply Chain Security is Now Critical
The OWASP Top 10:2025 added "Software Supply Chain Failures" as A03 - reflecting the rise of supply chain attacks. This means dependency scanning is no longer optional but a core security requirement.

### Pattern 2: Pydantic as Security Boundary
Pydantic v2 is increasingly recognized not just for data validation but as a security layer - enforcing type safety at application boundaries before data reaches business logic.

### Pattern 3: Shift from Denylist to Allowlist
All major sources emphasize allowlist-based validation over denylist. This applies to input characters, file paths, and command arguments.

### Pattern 4: "Assume Breach" for Deserialization
The consensus is that pickle/yaml.load should be treated as inherently dangerous with no safe way to use with untrusted data - shifting from "use carefully" to "avoid entirely."

---

## Gaps & Unknowns

### Gap 1: Typer-Specific Security Guidance
Limited documentation exists specifically for Typer CLI security. Most CLI security guidance focuses on web frameworks. **Mitigation**: Apply general CLI security patterns + Pydantic validation (Typer uses Pydantic internally).

### Gap 2: Memory Security for Secrets in Python
Python's string immutability makes it difficult to securely erase secrets from memory. Some sources mention `ctypes.memset` but this is unreliable. **Status**: Accepted limitation; focus on minimizing secret exposure time and avoiding unnecessary copies.

### Gap 3: ReDoS Prevention Patterns
While ReDoS (Regular Expression Denial of Service) is mentioned, specific Python patterns for safe regex design are sparse. **Mitigation**: Use Pydantic's built-in validators over custom regex where possible; test regex with tools like redos-checker.

---

*Generated: 2026-02-05*
