# Security Scan Report

> Scanned `src/raise_cli/` against `governance/solution/guardrails-stack.md` Section 3 (Security)
> Date: 2026-02-05

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | PASS |
| High | 0 | PASS |
| Medium | 1 | NEEDS ATTENTION |
| Low | 0 | PASS |

**Overall:** The codebase follows security best practices. One medium-severity gap identified in path traversal prevention.

---

## Detailed Findings

### 1. eval/exec/compile Usage

**Status:** PASS

No usage of `eval()`, `exec()`, or `compile()` with user input found.

**Searched patterns:**
- `\beval\s*\(` - No matches
- `\bexec\s*\(` - No matches
- `compile\(` - No matches (only regex.compile used correctly)

---

### 2. Subprocess with shell=True

**Status:** PASS

The subprocess wrapper in `tools.py` correctly uses argument lists without shell=True.

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/core/tools.py:152`

```python
result = subprocess.run(
    args,
    cwd=cwd,
    capture_output=True,
    text=True,
    check=check,
)
```

All subprocess calls go through `run_tool()` which requires a list of arguments and never enables shell mode.

---

### 3. os.system() Calls

**Status:** PASS

No usage of `os.system()` found. All shell commands use the `subprocess` module via `run_tool()`.

---

### 4. Hardcoded Secrets/Credentials

**Status:** PASS

No hardcoded secrets, API keys, passwords, or tokens found.

**Searched patterns:**
- `(password|secret|api_key|token|credential)\s*=\s*["'][^"']+["']` - No matches

The codebase uses environment variables appropriately for any configuration.

---

### 5. Safe Deserialization

**Status:** PASS

All YAML loading uses `yaml.safe_load()`:

| File | Line | Usage |
|------|------|-------|
| `cli/commands/status.py` | 42 | `yaml.safe_load(manifest_path.read_text())` |
| `onboarding/profile.py` | 162 | `yaml.safe_load(content)` |
| `onboarding/manifest.py` | 95 | `yaml.safe_load(content)` |
| `governance/parsers/adr.py` | 52 | `yaml.safe_load(frontmatter_text)` |
| `context/extractors/skills.py` | 50 | `yaml.safe_load(match.group(1))` |

No `pickle.load()` or `yaml.load()` (unsafe) found.

---

### 6. Path Traversal Vulnerabilities

**Status:** MEDIUM SEVERITY - Missing path validation

**Finding:** CLI commands accept user-provided paths for output files and write to them without validating that the path is within the project directory.

**Affected Commands:**

#### 6.1 context query --output

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/context.py:297`

```python
# Write to file or stdout
if output:
    output.write_text(output_text)  # No path validation
```

#### 6.2 memory query --output

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/memory.py:158`

```python
# Write to file or stdout
if output:
    output.write_text(output_text)  # No path validation
```

**Risk:** A user could write to arbitrary file locations using paths like `--output ../../../etc/cron.d/malicious`.

**Suggested Fix:**

Add a `safe_path()` utility as recommended in `guardrails-stack.md` Section 3.4:

```python
# Add to src/raise_cli/core/paths.py (new file) or core/__init__.py

from pathlib import Path

def safe_write_path(base: Path, user_path: Path) -> Path:
    """Resolve and verify path is within base directory for writes.

    Args:
        base: The base directory (e.g., project root or cwd)
        user_path: User-provided path

    Returns:
        Resolved path verified to be within base

    Raises:
        ValueError: If path would escape base directory
    """
    resolved = (base / user_path).resolve()
    base_resolved = base.resolve()

    if not resolved.is_relative_to(base_resolved):
        raise ValueError(
            f"Path traversal detected: {user_path} escapes {base}"
        )
    return resolved
```

Then update CLI commands:

```python
# In cli/commands/context.py
from pathlib import Path
from raise_cli.core.paths import safe_write_path

# ...

if output:
    safe_output = safe_write_path(Path.cwd(), output)
    safe_output.write_text(output_text)
```

**Note:** For CLI tools where users have shell access, this is lower risk since they already have file system access. However, implementing path validation is good defense-in-depth and aligns with the guardrails.

---

### 7. SQL Injection

**Status:** N/A - No Database Code

No database connections (sqlite, mysql, postgres) or SQL queries found in the codebase.

---

## Good Practices Observed

1. **Type Safety:** All code uses type annotations, reducing risk of type confusion attacks
2. **Pydantic Validation:** Input data validated through Pydantic models at boundaries
3. **Centralized Tool Execution:** All subprocess calls go through `run_tool()` wrapper
4. **Safe YAML:** Consistent use of `yaml.safe_load()` throughout
5. **Typer Path Validation:** CLI uses `exists=True`, `resolve_path=True` for input paths

---

## Recommendations

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | Add `safe_write_path()` utility | S (1-2 hours) |
| 2 | Apply path validation to all `--output` options | S (1-2 hours) |
| 3 | Add bandit to pre-commit hooks (per guardrails) | S (30 min) |
| 4 | Add detect-secrets baseline scan | S (30 min) |

---

## Appendix: Search Commands Used

```bash
# eval/exec
rg '\beval\s*\(' src/raise_cli/
rg '\bexec\s*\(' src/raise_cli/

# subprocess
rg 'shell\s*=\s*True' src/raise_cli/
rg 'subprocess\.(run|call|Popen)' src/raise_cli/

# os.system
rg 'os\.system\s*\(' src/raise_cli/

# Secrets
rg -i '(password|secret|api_key|token|credential)\s*=\s*["'\''][^"'\'']+["'\'']' src/raise_cli/

# YAML
rg 'yaml\.' src/raise_cli/

# pickle
rg 'pickle\.' src/raise_cli/

# Path traversal patterns
rg 'is_relative_to|safe_path' src/raise_cli/
```

---

*Generated by security scan for F14.0 DX Quality Gate*
