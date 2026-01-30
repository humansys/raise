# RaiSE Policy DSL Specification (v1.0)

**Document ID**: SPEC-POLICY-DSL-001
**Date**: 2026-01-29
**Status**: Draft
**Version**: 1.0.0-draft
**Related Research**: `governance-patterns-research.md`

---

## 1. Overview

The RaiSE Policy DSL (Domain-Specific Language) defines how governance rules are encoded as executable artifacts. This specification provides the YAML schema, built-in validators, and usage patterns for the Kata Executor Harness.

### 1.1 Design Principles

1. **Human-Readable**: YAML format familiar to developers
2. **LLM-Parseable**: Agent can read and explain policies
3. **Executable**: Deterministic evaluation, no interpretation needed
4. **Minimal**: Start with 5 core policy types, expand as needed
5. **Git-Friendly**: Textual format, reviewable diffs
6. **Type-Safe**: JSON Schema validation for policy files

### 1.2 Policy Types

| Type | Purpose | Timing | Example Use Case |
|------|---------|--------|------------------|
| `precondition_check` | Validate before kata starts | Pre-execution | Check file existence |
| `artifact_schema` | Validate output structure | Post-execution | Verify frontmatter fields |
| `validation_gate` | Quality checks | Post-execution | Count requirements, check criteria |
| `handoff_gate` | Validate before next kata | Inter-kata | Ensure Vision complete before Design |
| `jidoka_trigger` | Auto-stop conditions | Any | Detect critical failures |

---

## 2. Core Schema

### 2.1 Base Policy Structure

```yaml
# Required fields for all policies
policy_id: string              # Unique identifier (kebab-case)
policy_version: string         # SemVer (MAJOR.MINOR.PATCH)
policy_type: enum              # One of 5 core types
description: string            # Human-readable summary

applies_to:
  katas: [string]              # List of kata IDs
  artifacts: [string]          # List of file paths (optional)

metadata:                      # Optional metadata
  author: string
  created: date (ISO 8601)
  last_modified: date
  tags: [string]

checks: [Check]                # Array of validation checks

changelog: [ChangelogEntry]    # Optional: version history
```

### 2.2 Check Object Schema

```yaml
check_id: string               # Unique within policy (e.g., CHK-001)
description: string            # What this check validates
validator: string              # Validator name (from built-in or custom)
params: object                 # Validator-specific parameters
severity: enum                 # error | warning | info
on_fail: OnFailConfig          # What to do when check fails
enabled: boolean               # Default: true
```

### 2.3 OnFailConfig Schema

```yaml
action: enum                   # stop_execution | log_warning | log_info
message: string                # Error message shown to user
recovery_guidance: [string]    # Step-by-step fix instructions
related_docs: [string]         # Links to relevant documentation
escalation:                    # Optional escalation config
  notify: enum                 # user | tech_lead | team
  create_issue: boolean
  block_handoff: boolean
```

### 2.4 Full JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RaiSE Policy Schema",
  "type": "object",
  "required": ["policy_id", "policy_version", "policy_type", "description", "applies_to", "checks"],
  "properties": {
    "policy_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Unique policy identifier (kebab-case)"
    },
    "policy_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version"
    },
    "policy_type": {
      "enum": ["precondition_check", "artifact_schema", "validation_gate", "handoff_gate", "jidoka_trigger"]
    },
    "description": {
      "type": "string",
      "minLength": 10,
      "description": "Human-readable summary of policy purpose"
    },
    "applies_to": {
      "type": "object",
      "required": ["katas"],
      "properties": {
        "katas": {
          "type": "array",
          "items": {"type": "string"},
          "minItems": 1
        },
        "artifacts": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": {"type": "string"},
        "created": {"type": "string", "format": "date"},
        "last_modified": {"type": "string", "format": "date"},
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "checks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/definitions/Check"
      }
    },
    "changelog": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["version", "date", "changes"],
        "properties": {
          "version": {"type": "string"},
          "date": {"type": "string", "format": "date"},
          "changes": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  },
  "definitions": {
    "Check": {
      "type": "object",
      "required": ["check_id", "description", "validator", "severity", "on_fail"],
      "properties": {
        "check_id": {
          "type": "string",
          "pattern": "^[A-Z]+-[0-9]{3}$",
          "description": "Unique check ID (e.g., CHK-001)"
        },
        "description": {"type": "string"},
        "validator": {"type": "string"},
        "params": {"type": "object"},
        "severity": {"enum": ["error", "warning", "info"]},
        "on_fail": {"$ref": "#/definitions/OnFailConfig"},
        "enabled": {"type": "boolean", "default": true}
      }
    },
    "OnFailConfig": {
      "type": "object",
      "required": ["action", "message"],
      "properties": {
        "action": {"enum": ["stop_execution", "log_warning", "log_info"]},
        "message": {"type": "string"},
        "recovery_guidance": {
          "type": "array",
          "items": {"type": "string"}
        },
        "related_docs": {
          "type": "array",
          "items": {"type": "string"}
        },
        "escalation": {
          "type": "object",
          "properties": {
            "notify": {"enum": ["user", "tech_lead", "team"]},
            "create_issue": {"type": "boolean"},
            "block_handoff": {"type": "boolean"}
          }
        }
      }
    }
  }
}
```

---

## 3. Built-In Validators

### 3.1 Validator Library (MVP)

| Validator | Purpose | Parameters | Example |
|-----------|---------|------------|---------|
| `file_exists` | Check file exists | `path: string` | Validate solution_vision.md exists |
| `file_exists_any` | Check any file exists | `paths: [string]` | Validate context docs (any of 3) |
| `directory_writable` | Check write permissions | `path: string` | Ensure specs/main/ writable |
| `frontmatter_valid` | YAML frontmatter parseable | `file: string` | Validate kata YAML header |
| `frontmatter_field_exists` | Field present in frontmatter | `file: string, field: string` | Check 'titulo' exists |
| `section_present` | Markdown heading exists | `file: string, heading: string` | Validate "Requisitos Funcionales" section |
| `count` | Count items in section | `file: string, selector: string, operator: string, threshold: number` | Count >= 5 FR items |
| `pattern_match` | Regex match in file | `file: string, pattern: string` | Find "Criterios de Aceptación" |
| `pattern_match_all` | All instances match | `file: string, selector: string, pattern: string` | All FR-* have acceptance criteria |
| `schema_validation` | JSON Schema validation | `file: string, schema: object` | Validate JSON/YAML structure |

### 3.2 Validator Specifications

#### 3.2.1 file_exists

**Purpose**: Validate file exists at specified path.

**Parameters**:
```yaml
params:
  path: string  # Absolute or relative to project root
```

**Returns**: `ValidationResult(passed: bool, message: string)`

**Example**:
```yaml
checks:
  - check_id: CHK-001
    validator: file_exists
    params:
      path: specs/main/solution_vision.md
    severity: error
    on_fail:
      action: stop_execution
      message: "Solution Vision not found at {path}"
```

#### 3.2.2 count

**Purpose**: Count items matching selector, compare to threshold.

**Parameters**:
```yaml
params:
  file: string           # File to analyze
  selector: string       # XPath-like selector (simplified)
  operator: string       # >= | > | == | < | <=
  threshold: number      # Comparison value
```

**Selector Syntax** (simplified):
- `## Heading > list items` - Count list items under "## Heading"
- `### FR-* > subsection[heading='Criterios']` - Count subsections with specific heading
- `list items[starts-with='FR-']` - Count items starting with "FR-"

**Example**:
```yaml
checks:
  - check_id: CHK-005
    validator: count
    params:
      file: specs/main/project_requirements.md
      selector: "## Requisitos Funcionales > list items[starts-with='FR-']"
      operator: ">="
      threshold: 5
    severity: error
    on_fail:
      action: stop_execution
      message: "Insufficient functional requirements (found: {count}, expected: >= {threshold})"
```

#### 3.2.3 pattern_match_all

**Purpose**: Ensure all instances of selector match pattern.

**Parameters**:
```yaml
params:
  file: string
  selector: string       # Select elements to check
  pattern: string        # Regex or substring
```

**Example**:
```yaml
checks:
  - check_id: CHK-007
    validator: pattern_match_all
    params:
      file: specs/main/project_requirements.md
      selector: "### FR-*"  # All FR sections
      pattern: "\\*\\*Criterios de Aceptación:\\*\\*"  # Must contain this
    severity: error
    on_fail:
      action: stop_execution
      message: "Some requirements missing acceptance criteria"
```

### 3.3 Custom Validators

**Plugin System**: Allow projects to define custom validators.

**Example** (`.raise/policies/custom_validators/has_mermaid_diagram.py`):
```python
from raise.policy_engine import Validator, ValidationResult

class HasMermaidDiagram(Validator):
    """Validate Markdown file contains at least one Mermaid diagram."""

    validator_name = "has_mermaid_diagram"

    def validate(self, file_path: str, params: dict) -> ValidationResult:
        with open(file_path, 'r') as f:
            content = f.read()

        if '```mermaid' not in content:
            return ValidationResult(
                passed=False,
                message=f"No Mermaid diagram found in {file_path}",
                details={"file": file_path, "expected": "```mermaid block"}
            )

        return ValidationResult(
            passed=True,
            message="Mermaid diagram found"
        )

# Register validator
Validator.register(HasMermaidDiagram)
```

**Usage**:
```yaml
checks:
  - check_id: CHK-010
    validator: has_mermaid_diagram
    params:
      file: specs/main/tech_design.md
    severity: warning
    on_fail:
      action: log_warning
      message: "Tech Design should include architecture diagram"
```

---

## 4. Policy Examples

### 4.1 Precondition Check Policy

**Use Case**: Validate prerequisites before kata starts.

```yaml
policy_id: pre-discovery-policy
policy_version: 1.0.0
policy_type: precondition_check
description: Validate prerequisites before running Discovery kata

applies_to:
  katas:
    - flujo-01-discovery

metadata:
  author: RaiSE Team
  created: 2026-01-29
  tags: [precondition, discovery, prerequisites]

checks:
  - check_id: PRE-001
    description: Context documents available (at least one)
    validator: file_exists_any
    params:
      paths:
        - docs/context.md
        - docs/product-brief.md
        - docs/business-case.md
    severity: warning
    on_fail:
      action: log_warning
      message: "No context documents found. PRD will be based solely on user input."
      recovery_guidance:
        - "If context exists, add to docs/ directory"
        - "Or provide context in command: /raise.1.discovery --context '...'"

  - check_id: PRE-002
    description: User has write access to specs/main/
    validator: directory_writable
    params:
      path: specs/main/
    severity: error
    on_fail:
      action: stop_execution
      message: "Cannot write to specs/main/. Check permissions."
      recovery_guidance:
        - "Run: chmod u+w specs/main/"
        - "Or run kata with appropriate permissions"

  - check_id: PRE-003
    description: Template file exists
    validator: file_exists
    params:
      path: .raise/templates/solution/project_requirements.md
    severity: error
    on_fail:
      action: stop_execution
      message: "PRD template not found. RaiSE installation may be incomplete."
      recovery_guidance:
        - "Run: raise setup --verify"
        - "Or reinstall RaiSE: pip install --upgrade raise-framework"

changelog:
  - version: 1.0.0
    date: 2026-01-29
    changes:
      - "Initial version with 3 precondition checks"
```

### 4.2 Validation Gate Policy

**Use Case**: Post-execution quality checks for Discovery kata output.

```yaml
policy_id: gate-discovery-policy
policy_version: 2.0.0
policy_type: validation_gate
description: Validate PRD quality after Discovery kata completes

applies_to:
  katas:
    - flujo-01-discovery
  artifacts:
    - specs/main/project_requirements.md

metadata:
  author: RaiSE Team
  created: 2025-12-15
  last_modified: 2026-01-29
  tags: [gate, discovery, prd, quality]

checks:
  - check_id: VAL-001
    description: Frontmatter has required fields
    validator: frontmatter_field_exists
    params:
      file: specs/main/project_requirements.md
      field: titulo
    severity: error
    on_fail:
      action: stop_execution
      message: "PRD missing 'titulo' field in frontmatter"
      recovery_guidance:
        - "Add YAML frontmatter at top of file"
        - "Include: titulo: 'Your Project Title'"

  - check_id: VAL-002
    description: At least 5 functional requirements
    validator: count
    params:
      file: specs/main/project_requirements.md
      selector: "## Requisitos Funcionales > list items[starts-with='FR-']"
      operator: ">="
      threshold: 5
    severity: error
    on_fail:
      action: stop_execution
      message: "Insufficient functional requirements (found: {count}, expected: >= 5)"
      recovery_guidance:
        - "Review context documents for more requirements"
        - "Ask user for additional scope"
        - "Break down existing requirements into smaller units"
      related_docs:
        - docs/katas/flujo-01-discovery.md
        - docs/templates/solution/project_requirements.md

  - check_id: VAL-003
    description: Each requirement has acceptance criteria
    validator: pattern_match_all
    params:
      file: specs/main/project_requirements.md
      selector: "### FR-*"
      pattern: "\\*\\*Criterios de Aceptación:\\*\\*"
    severity: error
    on_fail:
      action: stop_execution
      message: "Some requirements missing 'Criterios de Aceptación' section"
      recovery_guidance:
        - "Review each FR-* section"
        - "Add '**Criterios de Aceptación:**' subsection"
        - "Define measurable criteria for completion"

  - check_id: VAL-004
    description: Non-functional requirements documented
    validator: section_present
    params:
      file: specs/main/project_requirements.md
      heading: "## Requisitos No Funcionales"
    severity: warning
    on_fail:
      action: log_warning
      message: "No non-functional requirements section. Consider adding performance, security, etc."

  - check_id: VAL-005
    description: Success criteria defined
    validator: section_present
    params:
      file: specs/main/project_requirements.md
      heading: "## Criterios de Éxito"
    severity: warning
    on_fail:
      action: log_warning
      message: "No success criteria section. Recommend defining measurable project goals."

changelog:
  - version: 2.0.0
    date: 2026-01-29
    changes:
      - "Migrated from Markdown checklist to YAML executable format"
      - "Added 5 validation checks (3 error, 2 warning)"
  - version: 1.0.0
    date: 2025-12-15
    changes:
      - "Initial Markdown gate version"
```

### 4.3 Handoff Gate Policy

**Use Case**: Validate prerequisites before allowing next kata.

```yaml
policy_id: handoff-discovery-to-vision-policy
policy_version: 1.0.0
policy_type: handoff_gate
description: Validate Discovery complete before allowing Vision kata

applies_to:
  katas:
    - flujo-02-solution-vision  # Target kata (blocked until this passes)

metadata:
  author: RaiSE Team
  created: 2026-01-29
  tags: [handoff, discovery, vision, prerequisites]

checks:
  - check_id: HO-001
    description: PRD exists
    validator: file_exists
    params:
      path: specs/main/project_requirements.md
    severity: error
    on_fail:
      action: stop_execution
      message: "Cannot start Vision kata. PRD not found."
      recovery_guidance:
        - "Run: /raise.1.discovery"
        - "Ensure gate-discovery passes"
        - "Then retry: /raise.2.vision"

  - check_id: HO-002
    description: Discovery gate passed
    validator: gate_passed
    params:
      gate_id: gate-discovery
      artifact: specs/main/project_requirements.md
    severity: error
    on_fail:
      action: stop_execution
      message: "Discovery gate did not pass. Fix PRD issues before proceeding."
      recovery_guidance:
        - "Run: raise gate run gate-discovery"
        - "Review failures and fix"
        - "Re-run gate until pass"
      escalation:
        block_handoff: true

changelog:
  - version: 1.0.0
    date: 2026-01-29
    changes:
      - "Initial handoff gate between Discovery and Vision"
```

### 4.4 Jidoka Trigger Policy

**Use Case**: Auto-stop conditions for critical failures.

```yaml
policy_id: jidoka-critical-failures-policy
policy_version: 1.0.0
policy_type: jidoka_trigger
description: Critical failure conditions that trigger immediate stop

applies_to:
  katas:
    - "*"  # Applies to all katas

metadata:
  author: RaiSE Team
  created: 2026-01-29
  tags: [jidoka, critical, safety]

checks:
  - check_id: JID-001
    description: No secrets in generated files
    validator: no_secrets
    params:
      file_pattern: "specs/**/*.md"
      secret_patterns:
        - "password\\s*=\\s*['\"][^'\"]+['\"]"
        - "api_key\\s*=\\s*['\"][^'\"]+['\"]"
        - "token\\s*=\\s*['\"][^'\"]+['\"]"
    severity: error
    on_fail:
      action: stop_execution
      message: "🚨 JIDOKA: Secrets detected in generated files. STOP."
      recovery_guidance:
        - "Remove secrets from files"
        - "Use environment variables or secret manager"
        - "Never commit secrets to Git"
      escalation:
        notify: tech_lead
        create_issue: true
        block_handoff: true

  - check_id: JID-002
    description: Token budget not exceeded
    validator: token_count
    params:
      max_tokens: 50000
    severity: error
    on_fail:
      action: stop_execution
      message: "🚨 JIDOKA: Token budget exceeded. Possible infinite loop."
      recovery_guidance:
        - "Review kata execution logs"
        - "Check for recursive or repetitive generation"
        - "Simplify kata scope if too complex"

  - check_id: JID-003
    description: No destructive file operations
    validator: file_operation_safety
    params:
      forbidden_operations:
        - delete_outside_scope
        - modify_source_code  # Discovery/Vision should not touch src/
    severity: error
    on_fail:
      action: stop_execution
      message: "🚨 JIDOKA: Unsafe file operation detected. STOP."
      recovery_guidance:
        - "Review kata instructions for scope"
        - "Ensure agent only modifies allowed files"

changelog:
  - version: 1.0.0
    date: 2026-01-29
    changes:
      - "Initial Jidoka safety checks (secrets, token budget, file safety)"
```

---

## 5. Policy Execution Model

### 5.1 Execution Flow

```
User: /raise.1.discovery --context "..."

Kata Executor:
  1. Load kata (flujo-01-discovery.md)
  2. Load policy (pre-discovery-policy.yaml)
  3. RUN PRE-EXECUTION GATE
     - Evaluate all checks in policy
     - If any severity=error fails → STOP
     - If any severity=warning fails → LOG WARNING
  4. EXECUTE KATA
     - Display steps to LLM agent
     - Agent generates output
  5. RUN POST-EXECUTION GATE
     - Load gate policy (gate-discovery-policy.yaml)
     - Evaluate all checks
     - If any severity=error fails → STOP
  6. HANDOFF
     - If gate passed, suggest next kata
     - If gate failed, display recovery guidance
```

### 5.2 Validator Resolution

**Order** (validator lookup):
1. Built-in validators (shipped with RaiSE)
2. Project-specific validators (`.raise/policies/custom_validators/`)
3. Team shared validators (from MCP resource `raise://validators`)

**Example**:
```python
# Pseudo-code for validator resolution
def resolve_validator(validator_name: str) -> Validator:
    # 1. Check built-ins
    if validator_name in BUILTIN_VALIDATORS:
        return BUILTIN_VALIDATORS[validator_name]

    # 2. Check project custom validators
    custom_path = f".raise/policies/custom_validators/{validator_name}.py"
    if os.path.exists(custom_path):
        return load_custom_validator(custom_path)

    # 3. Check MCP resource (future)
    # validator = mcp_client.get_resource(f"raise://validators/{validator_name}")
    # if validator:
    #     return validator

    # 4. Not found
    raise ValidatorNotFoundError(f"Validator '{validator_name}' not found")
```

### 5.3 Policy Versioning

**Compatibility Matrix**:
```yaml
# Policy declares compatible kata versions
policy_id: gate-discovery-policy
policy_version: 2.0.0
compatible_kata_versions:
  - "1.x"  # Works with kata v1.0, v1.1, etc.
  - "2.x"  # Works with kata v2.0, v2.1, etc.
```

**Loading Logic**:
```python
def load_policy(kata_id: str, kata_version: str) -> Policy:
    policy_file = f".raise/policies/{kata_id}-policy.yaml"
    policy = parse_yaml(policy_file)

    # Check compatibility
    if not is_compatible(kata_version, policy.compatible_kata_versions):
        raise PolicyIncompatibleError(
            f"Policy {policy.policy_id} v{policy.policy_version} "
            f"not compatible with kata v{kata_version}"
        )

    return policy
```

---

## 6. CLI Interface

### 6.1 Policy Management Commands

```bash
# Validate policy YAML syntax
$ raise policy validate .raise/policies/gate-discovery-policy.yaml
✅ Policy valid: gate-discovery-policy v2.0.0

# List all policies
$ raise policy list
pre-discovery-policy         v1.0.0  [precondition_check]
gate-discovery-policy        v2.0.0  [validation_gate]
gate-vision-policy           v1.5.0  [validation_gate]
handoff-discovery-vision     v1.0.0  [handoff_gate]

# Show policy details
$ raise policy show gate-discovery-policy
Policy: gate-discovery-policy
Version: 2.0.0
Type: validation_gate
Applies To: flujo-01-discovery
Checks: 5 (3 errors, 2 warnings)

# Test policy against artifact
$ raise policy test gate-discovery-policy --artifact specs/main/project_requirements.md
Running gate-discovery-policy v2.0.0...
  [✅ PASS] VAL-001: Frontmatter has required fields
  [✅ PASS] VAL-002: At least 5 functional requirements (found: 7)
  [❌ FAIL] VAL-003: Each requirement has acceptance criteria
    → FR-003 missing 'Criterios de Aceptación'
  [⚠️  WARN] VAL-004: Non-functional requirements documented

Result: FAIL (1 error, 1 warning)

# Upgrade policy version
$ raise policy upgrade gate-discovery-policy
Current: v1.5.0
Latest: v2.0.0
⚠️  Breaking changes:
  - Check VAL-003 now mandatory (was warning)
  - New check VAL-005 added
Continue? [y/N] y
✅ Upgraded to v2.0.0

# Create new policy from template
$ raise policy create my-custom-gate --type validation_gate --kata flujo-04-backlog
Created: .raise/policies/my-custom-gate-policy.yaml
Edit file and add validation checks.
```

### 6.2 Gate Execution Commands

```bash
# Run gate manually
$ raise gate run gate-discovery
Running gate: gate-discovery (v2.0.0)
Artifact: specs/main/project_requirements.md

Validating...
  [✅ PASS] VAL-001: Frontmatter has required fields
  [✅ PASS] VAL-002: >= 5 functional requirements (found: 7)
  [✅ PASS] VAL-003: Each requirement has acceptance criteria
  [⚠️  WARN] VAL-004: Non-functional requirements (none found)
  [⚠️  WARN] VAL-005: Success criteria (none found)

Gate Result: PASS (0 errors, 2 warnings)

# Run all gates for a kata
$ raise gate run-all --kata flujo-01-discovery
Running gates for flujo-01-discovery...
  [✅ PASS] pre-discovery-policy (precondition)
  [✅ PASS] gate-discovery-policy (validation)
  [✅ PASS] handoff-discovery-vision (handoff)

All gates passed. Ready to proceed.

# Generate gate report
$ raise gate report --since 2026-01-01
Gate Execution Report (2026-01-01 to 2026-01-29)

Total Gate Runs: 45
Passed: 38 (84.4%)
Failed: 7 (15.6%)

Failed Gates:
  gate-discovery: 2 failures
  gate-design: 4 failures
  gate-backlog: 1 failure

Top Failing Checks:
  VAL-003 (acceptance criteria): 3 occurrences
  VAL-008 (architecture diagram): 2 occurrences
```

---

## 7. Implementation Notes

### 7.1 Parser Requirements

**YAML Parsing**:
- Use `PyYAML` or `ruamel.yaml` (preserves comments)
- Validate against JSON Schema before execution
- Support includes/references (future: `!include other-policy.yaml`)

**Markdown Parsing** (for validators):
- Use `mistune` or `markdown-it-py` for AST parsing
- Support frontmatter extraction (YAML between `---` delimiters)
- Enable selector queries (XPath-like for Markdown structure)

### 7.2 Validator Implementation Pattern

```python
# raise/policy_engine/validators/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ValidationResult:
    passed: bool
    message: str
    details: dict = None

class Validator(ABC):
    """Base class for all validators."""

    validator_name: str = None  # Must be set by subclass

    @abstractmethod
    def validate(self, file_path: str, params: dict) -> ValidationResult:
        """Execute validation logic."""
        pass

    @classmethod
    def register(cls, validator_class):
        """Register validator in global registry."""
        VALIDATOR_REGISTRY[validator_class.validator_name] = validator_class

# Built-in validators registry
VALIDATOR_REGISTRY = {}
```

**Example Validator**:
```python
# raise/policy_engine/validators/file_exists.py
import os
from .base import Validator, ValidationResult

class FileExistsValidator(Validator):
    validator_name = "file_exists"

    def validate(self, file_path: str, params: dict) -> ValidationResult:
        path = params.get("path")
        if not path:
            return ValidationResult(
                passed=False,
                message="Validator 'file_exists' requires 'path' parameter"
            )

        if os.path.exists(path):
            return ValidationResult(
                passed=True,
                message=f"File exists: {path}"
            )
        else:
            return ValidationResult(
                passed=False,
                message=f"File not found: {path}",
                details={"path": path, "cwd": os.getcwd()}
            )

# Auto-register
Validator.register(FileExistsValidator)
```

### 7.3 Error Handling

**Policy Load Errors**:
- Invalid YAML syntax → Show line number, syntax error
- Schema validation failure → Show which field invalid, expected type
- Validator not found → List available validators, suggest fix

**Execution Errors**:
- Validator exception → Catch, log, treat as check failure (not harness crash)
- File not readable → Clear error message with recovery (check permissions)
- Timeout (validator taking too long) → Kill validator, mark check as error

---

## 8. Future Extensions

### 8.1 Policy Composition

**Use Case**: Reuse common checks across multiple policies.

```yaml
# .raise/policies/common-checks.yaml
common_checks:
  - check_id: CMN-001
    description: Frontmatter valid
    validator: frontmatter_valid

  - check_id: CMN-002
    description: No secrets
    validator: no_secrets
    params:
      secret_patterns: [...]

# .raise/policies/gate-discovery-policy.yaml
policy_id: gate-discovery-policy
imports:
  - common-checks.yaml

checks:
  - !include common-checks.CMN-001
  - !include common-checks.CMN-002
  - check_id: VAL-001
    # ... policy-specific checks
```

### 8.2 Conditional Checks

**Use Case**: Check only applies if condition met.

```yaml
checks:
  - check_id: VAL-010
    description: Integration tests required for backend projects
    validator: section_present
    params:
      file: specs/main/tech_design.md
      heading: "## Integration Testing"
    severity: error
    condition:  # Only check if project type is backend
      when: "project.type == 'backend'"
    on_fail:
      action: stop_execution
      message: "Backend projects must define integration testing strategy"
```

### 8.3 Dynamic Thresholds

**Use Case**: Threshold varies by project size/complexity.

```yaml
checks:
  - check_id: VAL-002
    validator: count
    params:
      file: specs/main/project_requirements.md
      selector: "## Requisitos Funcionales > list items"
      operator: ">="
      threshold: "{{ project.complexity == 'simple' ? 3 : 5 }}"  # Templating
    severity: error
```

### 8.4 Multi-File Validation

**Use Case**: Check consistency across multiple artifacts.

```yaml
checks:
  - check_id: VAL-020
    description: Tech Design references all PRD requirements
    validator: cross_reference
    params:
      source_file: specs/main/project_requirements.md
      target_file: specs/main/tech_design.md
      source_selector: "## Requisitos Funcionales > list items[id='FR-*']"
      target_pattern: "FR-\\d{3}"  # All FR-XXX from PRD must appear in Design
    severity: warning
    on_fail:
      action: log_warning
      message: "Some PRD requirements not referenced in Tech Design"
```

---

## 9. Appendix

### 9.1 Complete Example Policy

See Section 4.2 (`gate-discovery-policy.yaml`) for a complete, production-ready example.

### 9.2 JSON Schema Reference

See Section 2.4 for full JSON Schema definition.

### 9.3 Validator API Reference

See Section 3 for built-in validators and Section 3.3 for custom validator API.

---

**End of Specification**

**Status**: Draft (pending review by RaiSE team)
**Next Steps**: Prototype policy engine, implement 3 built-in validators, convert 1 gate to YAML
