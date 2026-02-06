# Python Security Checklist for raise-cli

> Copy-paste checklist for guardrails integration
> Based on RES-PYTHON-SEC-20260205 (25 sources, HIGH confidence)

---

## Quick Reference: What to NEVER Do

```python
# NEVER: Dynamic code execution with untrusted input
eval(user_input)
exec(user_input)
compile(user_input, '<string>', 'exec')

# NEVER: Shell=True with user input
subprocess.run(f"cmd {user_input}", shell=True)
os.system(f"cmd {user_input}")

# NEVER: Deserialize untrusted data
pickle.loads(untrusted_data)
yaml.load(untrusted_data)  # Use yaml.safe_load()

# NEVER: Hardcode secrets
password = "secret123"
API_KEY = "sk-abc..."

# NEVER: Use random for security
token = ''.join(random.choices(...))

# NEVER: Assert for security validation
assert user.is_authorized

# NEVER: Trust user paths without validation
open(user_provided_path)
```

---

## Security Guardrails Checklist

### 1. Input Validation (Priority: CRITICAL)

- [ ] **All external input passes through Pydantic models**
  - CLI arguments validated via Typer + Pydantic
  - Environment variables loaded via `pydantic-settings`
  - File content parsed with explicit schemas

- [ ] **Use allowlist validation, not denylist**
  ```python
  # CORRECT: Allowlist
  ALLOWED_COMMANDS = {"status", "log", "diff"}
  if cmd not in ALLOWED_COMMANDS:
      raise ValueError(f"Unknown command: {cmd}")

  # INCORRECT: Denylist
  BLOCKED = {"rm", "sudo", "chmod"}
  if cmd in BLOCKED:
      raise ValueError("Blocked command")
  ```

- [ ] **Validate string lengths and formats**
  ```python
  class PathInput(BaseModel):
      path: str = Field(max_length=4096, pattern=r'^[a-zA-Z0-9_\-./]+$')
  ```

### 2. Command Execution (Priority: CRITICAL)

- [ ] **Never use shell=True with subprocess**
  ```python
  # CORRECT
  subprocess.run(["git", "log", "--oneline"], check=True)

  # INCORRECT
  subprocess.run("git log --oneline", shell=True)
  ```

- [ ] **Use shlex for parsing/quoting user input**
  ```python
  import shlex
  args = shlex.split(user_command_string)
  safe_arg = shlex.quote(user_provided_value)
  ```

- [ ] **Never use os.system()**
  - Replace with `subprocess.run()` with explicit arguments

### 3. Code Execution (Priority: CRITICAL)

- [ ] **Prohibit eval(), exec(), compile() on external data**
  - Use AST parsing for analysis only (read-only)
  - Use dispatch tables for dynamic selection

- [ ] **No dynamic imports from user input**
  ```python
  # NEVER
  module = importlib.import_module(user_input)

  # IF NEEDED: Whitelist
  ALLOWED_MODULES = {"json", "csv"}
  if name not in ALLOWED_MODULES:
      raise ValueError("Module not allowed")
  ```

### 4. Deserialization (Priority: CRITICAL)

- [ ] **Never unpickle untrusted data**
  - Use JSON for data exchange
  - If pickle required internally, verify with cryptographic signature

- [ ] **Use yaml.safe_load() exclusively**
  ```python
  # CORRECT
  data = yaml.safe_load(file_content)

  # NEVER
  data = yaml.load(file_content, Loader=yaml.FullLoader)
  ```

### 5. Path Handling (Priority: HIGH)

- [ ] **Validate paths against traversal attacks**
  ```python
  from pathlib import Path

  def safe_path(base: Path, user_input: str) -> Path:
      """Resolve path and verify within base directory."""
      resolved = (base / user_input).resolve()
      base_resolved = base.resolve()
      if not resolved.is_relative_to(base_resolved):
          raise ValueError("Path traversal detected")
      return resolved
  ```

- [ ] **Use pathlib over os.path**
  - `Path.resolve()` canonicalizes and removes `..`
  - `is_relative_to()` for ancestry checks

- [ ] **Whitelist allowed paths when possible**

### 6. Secret Management (Priority: HIGH)

- [ ] **No hardcoded secrets (Bandit B105-B107)**
  ```python
  # CORRECT
  api_key = os.environ.get("API_KEY")

  # NEVER
  api_key = "sk-abc123..."
  ```

- [ ] **Use appropriate storage by context**
  | Context | Solution |
  |---------|----------|
  | Development | `python-dotenv` with `.env` in `.gitignore` |
  | Desktop CLI | `keyring` library |
  | CI/CD | Platform secrets (GitLab CI variables) |
  | Production | Secrets manager (Vault, AWS SM) |

- [ ] **Add .env to .gitignore**

- [ ] **Use detect-secrets in pre-commit**

### 7. Cryptographic Security (Priority: HIGH)

- [ ] **Use secrets module for tokens**
  ```python
  import secrets

  # CORRECT
  token = secrets.token_urlsafe(32)
  reset_code = secrets.token_hex(16)

  # NEVER
  import random
  token = ''.join(random.choices(string.ascii_letters, k=32))
  ```

- [ ] **Never disable SSL verification in production**
  ```python
  # NEVER in production
  requests.get(url, verify=False)
  ```

### 8. Logging Security (Priority: MEDIUM)

- [ ] **Never log passwords, tokens, or PII**

- [ ] **Implement log filter for sensitive patterns**
  ```python
  import logging
  import re

  class SensitiveFilter(logging.Filter):
      PATTERNS = [
          (re.compile(r'password["\']?\s*[:=]\s*["\']?[^\s"\']+', re.I), 'password=***'),
          (re.compile(r'token["\']?\s*[:=]\s*["\']?[^\s"\']+', re.I), 'token=***'),
          (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[^\s"\']+', re.I), 'api_key=***'),
      ]

      def filter(self, record: logging.LogRecord) -> bool:
          msg = str(record.msg)
          for pattern, replacement in self.PATTERNS:
              msg = pattern.sub(replacement, msg)
          record.msg = msg
          return True
  ```

- [ ] **Don't include sensitive data in URLs**

### 9. File Operations (Priority: MEDIUM)

- [ ] **Use secure temporary files**
  ```python
  import tempfile

  # CORRECT
  with tempfile.NamedTemporaryFile(delete=True) as f:
      f.write(data)

  # NEVER (race condition)
  filename = tempfile.mktemp()
  ```

- [ ] **Set restrictive file permissions**
  ```python
  import stat
  os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 600
  ```

### 10. Dependency Security (Priority: HIGH)

- [ ] **Run pip-audit in CI**
  ```bash
  pip-audit --require-hashes --strict
  ```

- [ ] **Pin dependency versions in requirements**

- [ ] **Review dependency updates before merging**

---

## Pre-commit Configuration

```yaml
# .pre-commit-config.yaml additions
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-r", "src/", "-ll", "-x", "tests/"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

---

## Bandit Rules Reference

| Rule | Description | Priority |
|------|-------------|----------|
| B101 | assert_used | Skip in tests |
| B102 | exec_used | BLOCK |
| B103 | set_bad_file_permissions | BLOCK |
| B104 | hardcoded_bind_all_interfaces | WARN |
| B105 | hardcoded_password_string | BLOCK |
| B106 | hardcoded_password_funcarg | BLOCK |
| B107 | hardcoded_password_default | BLOCK |
| B108 | hardcoded_tmp_directory | WARN |
| B110 | try_except_pass | WARN |
| B112 | try_except_continue | WARN |
| B301 | pickle | BLOCK |
| B302 | marshal | BLOCK |
| B303 | md5/sha1 for security | WARN |
| B304 | ciphers | WARN |
| B305 | cipher_modes | WARN |
| B306 | mktemp_q | BLOCK |
| B307 | eval | BLOCK |
| B308 | mark_safe | WARN |
| B310 | urllib_urlopen | WARN |
| B311 | random | WARN |
| B312 | telnetlib | BLOCK |
| B313-B320 | XML parsing | WARN |
| B321 | ftplib | WARN |
| B323 | unverified_context | BLOCK |
| B324 | hashlib | WARN |
| B501 | request_with_no_cert_validation | BLOCK |
| B502 | ssl_with_bad_version | BLOCK |
| B503 | ssl_with_bad_defaults | BLOCK |
| B504 | ssl_with_no_version | WARN |
| B505 | weak_cryptographic_key | BLOCK |
| B506 | yaml_load | BLOCK |
| B507 | ssh_no_host_key_verification | BLOCK |
| B601 | paramiko_calls | WARN |
| B602 | subprocess_popen_with_shell_equals_true | BLOCK |
| B603 | subprocess_without_shell_equals_true | WARN |
| B604 | any_other_function_with_shell_equals_true | BLOCK |
| B605 | start_process_with_a_shell | BLOCK |
| B606 | start_process_with_no_shell | WARN |
| B607 | start_process_with_partial_path | WARN |
| B608 | hardcoded_sql_expressions | BLOCK |
| B609 | linux_commands_wildcard_injection | WARN |
| B610 | django_extra_used | WARN |
| B611 | django_rawsql_used | WARN |
| B701 | jinja2_autoescape_false | WARN |
| B702 | use_of_mako_templates | WARN |
| B703 | django_mark_safe | WARN |

---

## Verification Commands

```bash
# Run security checks locally
bandit -r src/ -ll -x tests/

# Check for secrets
detect-secrets scan

# Audit dependencies
pip-audit

# Full security check
make security  # If Makefile target exists
```

---

*Generated from RES-PYTHON-SEC-20260205*
*Confidence: HIGH (25 sources, 7 Very High, 11 High)*
