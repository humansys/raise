# Governance-as-Code Patterns for AI Agent Systems

**Research ID**: RES-KATA-HARNESS-GOV-001
**Date**: 2026-01-29
**Researcher**: Claude Sonnet 4.5 (Assisted)
**Requestor**: Emilio (RaiSE Framework - Kata Harness)
**Version**: 1.0.0
**Status**: Complete

---

## Executive Summary

This research investigates how governance policies can be encoded as **executable artifacts** rather than suggested guidelines, specifically for the RaiSE Framework's Kata Harness. The fundamental question: **Can we enforce "STOP" (Jidoka) through policy rather than hoping the LLM follows instructions?**

### Key Findings

1. **Policy-Mechanism Separation is Feasible**: Modern governance frameworks (OPA, NeMo Guardrails, Guardrails AI) successfully separate policy definition from enforcement mechanism. RaiSE should adopt this pattern.

2. **Enforcement Timing Matters**: Three enforcement points exist - pre-execution (gate), mid-execution (runtime monitoring), post-execution (validation). RaiSE's current gates are post-execution only; pre-execution gates are missing.

3. **Executable Policies Beat Descriptive Text**: Formats with executable queries (Semgrep patterns, OPA Rego, ast-grep) achieve deterministic enforcement. Pure text guidelines rely on LLM compliance (unreliable).

4. **Trade-off is Real**: Strict enforcement (100% deterministic) sacrifices agent flexibility and adaptability. The sweet spot: 70-80% strict rules, 20-30% heuristic guidelines with runtime monitoring.

5. **YAML + Markdown Hybrid Optimal for RaiSE**: Policy definitions in YAML (machine-readable, executable), human guidance in Markdown (LLM-consumable), evidence chains in JSON (audit trail).

### Recommendations for RaiSE Kata Harness

1. **Adopt Three-Layer Architecture**:
   - **Layer 1**: Policy definitions (YAML) - deterministic, versionable, testable
   - **Layer 2**: Enforcement harness (Kata Executor) - interprets policies, enforces gates
   - **Layer 3**: Execution runtime (LLM agent) - operates within constraints

2. **Implement Pre-Execution Gates**: Before a kata step runs, validate preconditions (files exist, data schema correct, dependencies met). Fail fast.

3. **Add Runtime Monitoring**: During kata execution, track deviation from expected behavior (file modifications outside scope, API calls not in spec). Alert but don't block (UX consideration).

4. **Use Policy DSL for Gates**: Define validation gates in structured format (inspired by OPA/Guardrails) rather than Markdown checklists. Example: `gate-discovery.yaml` with testable predicates.

5. **Separate Jidoka from LLM Instructions**: Current approach embeds Jidoka in prompts ("Si no puedes continuar..."). Move to runtime enforcement: harness detects failure conditions and triggers stop automatically.

---

## 1. Policy Languages for Agents

### 1.1 OPA (Open Policy Agent) / Rego

**Overview**: General-purpose policy engine using Rego declarative language. Designed for Kubernetes, API gateways, but applicable to any decision point.

**Architecture**:
```
Policy Bundle (Rego files)
    ↓
OPA Engine (decision evaluator)
    ↓
Application (queries OPA for allow/deny)
```

**Rego Example**:
```rego
# Policy: Can this kata step execute?
package kata.execution

default allow = false

allow {
    input.preconditions_met == true
    input.previous_step_validated == true
    not gate_failed
}

gate_failed {
    input.gate_results[_].status == "FAIL"
}
```

**Applicability to LLM Agents**:
- **Pro**: Policy-as-code (versioned, testable, auditable)
- **Pro**: Separation of concerns (policy definition decoupled from agent code)
- **Pro**: Complex logic support (recursive rules, conditions)
- **Con**: Learning curve for Rego syntax
- **Con**: Not LLM-native (agent can't modify policies easily)
- **Con**: Overhead for simple boolean checks

**Use Case in RaiSE**:
- **Pre-execution gates**: "Can this kata step run given current state?"
- **Compliance checks**: "Does generated artifact meet constitution requirements?"
- **Handoff validation**: "Are preconditions for next command satisfied?"

**Confidence**: HIGH (industry-proven, extensive documentation, active community)

---

### 1.2 Cedar (AWS Policy Language)

**Overview**: Cedar is Amazon's policy language for fine-grained access control. Similar to OPA but with simpler syntax, type-safe, formally verified.

**Architecture**:
```
Policy Store (Cedar policies)
    ↓
Cedar Engine (authorization evaluator)
    ↓
Application (is principal authorized for action on resource?)
```

**Cedar Example**:
```cedar
// Policy: Orquestador can execute kata step IF preconditions met
permit(
  principal == Orquestador::"user123",
  action == Action::"executeKataStep",
  resource == KataStep::"discovery-step-3"
)
when {
  context.preconditions.file_exists == true &&
  context.gate_status == "PASS"
};
```

**Applicability to LLM Agents**:
- **Pro**: Simpler syntax than Rego (closer to natural language)
- **Pro**: Type-safe (fewer runtime errors)
- **Pro**: Formal verification possible
- **Con**: AWS-centric (less community adoption outside AWS ecosystem)
- **Con**: Permission-focused (not general-purpose policy)
- **Con**: Still requires learning new language

**Use Case in RaiSE**:
- **Resource access control**: "Can agent modify this file?"
- **Action authorization**: "Is agent allowed to skip validation gate?"
- **Audit logging**: "Track all policy evaluation decisions"

**Confidence**: MEDIUM-HIGH (proven in AWS, but narrow use case)

---

### 1.3 Custom DSL for Agent Governance

**Overview**: Define RaiSE-specific policy language tailored to kata execution, validation gates, and Jidoka enforcement.

**Design Principles**:
1. **Human-readable** (YAML or simplified Cedar-like syntax)
2. **LLM-parseable** (agent can read and understand policies)
3. **Executable** (deterministic evaluation, no LLM interpretation)
4. **Minimal** (KISS - start with 5 policy types, expand as needed)

**Proposed RaiSE Policy DSL (YAML-based)**:
```yaml
# .raise/policies/gate-discovery-policy.yaml
policy_id: POL-GATE-DISCOVERY-001
policy_type: validation_gate
applies_to:
  - katas: [flujo-01-discovery]
  - artifacts: [project_requirements.md]

preconditions:
  - file_exists: specs/main/project_requirements.md
  - frontmatter_valid: true
  - sections_present:
      - "Visión General"
      - "Requisitos Funcionales"
      - "Requisitos No Funcionales"

validation_rules:
  - rule_id: VR-001
    description: PRD must have >= 5 functional requirements
    check:
      type: count
      selector: "## Requisitos Funcionales > list items"
      operator: ">="
      threshold: 5
    severity: error
    on_fail: stop_execution

  - rule_id: VR-002
    description: Each requirement must have acceptance criteria
    check:
      type: pattern_match
      selector: "### FR-* > ** Criterios de Aceptación"
      match_all: true
    severity: warning
    on_fail: log_and_continue

enforcement:
  mode: strict  # strict | advisory | logging_only
  stop_on_error: true
  allow_override: false
  escalation:
    notify: tech_lead
    create_issue: true
```

**Advantages over OPA/Cedar**:
- **Domain-specific**: Optimized for kata execution, not general authorization
- **No new language**: YAML familiar to developers
- **LLM-friendly**: Agent can read/explain policies in natural language
- **Evolvable**: Add new `policy_type` as needs emerge

**Implementation Path**:
1. **Phase 1**: Define 5 core policy types (validation_gate, precondition_check, artifact_schema, handoff_gate, jidoka_trigger)
2. **Phase 2**: Build policy evaluator in Kata Executor Harness (Python/TypeScript)
3. **Phase 3**: CLI for policy testing (`raise policy test gate-discovery-policy.yaml`)
4. **Phase 4**: Visual policy editor (low-code UI for non-technical users)

**Use Case in RaiSE**:
- **All governance needs**: Pre-execution gates, validation gates, Jidoka enforcement, handoff validation

**Confidence**: HIGH for RaiSE-specific use case (custom DSL aligns with framework philosophy)

---

### 1.4 Comparison Matrix

| Aspect | OPA/Rego | Cedar | Custom DSL (Proposed) |
|--------|----------|-------|----------------------|
| **Learning Curve** | High | Medium | Low (YAML-based) |
| **Expressiveness** | Very High | Medium | Medium (extensible) |
| **LLM-Friendliness** | Low | Low | High |
| **Type Safety** | No | Yes | Optional (with JSON Schema) |
| **Execution Model** | Interpreted | Compiled | Interpreted |
| **Community Support** | High | Medium | None (new) |
| **Versioning** | Git-friendly | Git-friendly | Git-friendly |
| **Audit Trail** | External (logs) | Built-in | Built-in (design) |
| **Use Case Fit (RaiSE)** | 70% | 60% | 95% |

**Recommendation**: **Start with Custom DSL**, adopt OPA patterns for complex logic if needed later. Rationale: Learning curve matters for Heutagogy (self-directed learning); custom DSL lowers barrier.

---

## 2. Gate Enforcement Mechanisms

### 2.1 Enforcement Timing Taxonomy

| Timing | Description | Examples | Pros | Cons |
|--------|-------------|----------|------|------|
| **Pre-execution** | Validate BEFORE step runs | Precondition checks, resource availability, schema validation | Fail fast; prevent wasted computation | Requires upfront specification |
| **Runtime (continuous)** | Monitor DURING step execution | File modification tracking, API call logging, token usage monitoring | Detect deviations early | Performance overhead; complex to implement |
| **Post-execution** | Validate AFTER step completes | Current RaiSE gates (gate-discovery.md, gate-design.md) | Simple to implement; full artifact available | Wasted effort if fails; harder to debug |

**Current RaiSE State**: Post-execution only (gates run after kata completes).

**Gap**: No pre-execution gates → agents waste time executing katas that will fail validation.

---

### 2.2 Pre-Execution Validators

**Purpose**: Answer "Can this step run given current state?" BEFORE agent starts execution.

**Example Use Cases**:
1. **File existence check**: Discovery kata requires `docs/context.md` exists → check before running
2. **Schema validation**: Backlog kata expects PRD with specific frontmatter → validate structure before consuming
3. **Dependency validation**: Tech Design kata needs Solution Vision → verify Vision gate passed
4. **Resource check**: Code generation kata needs API keys in `.env` → check before API calls

**Implementation Pattern**:
```yaml
# Pre-execution gate definition
gate_id: PRE-DISCOVERY-001
gate_type: pre_execution
applies_to: flujo-01-discovery

checks:
  - check_id: CHK-001
    name: Context documents exist
    validator: file_exists
    params:
      paths:
        - docs/context.md
        - docs/product-brief.md
    severity: error
    failure_action: stop_execution
    failure_message: "Missing context documents. Run /raise.setup.analyze-codebase first."

  - check_id: CHK-002
    name: Kata prerequisites met
    validator: prerequisite_check
    params:
      required_katas: []  # Discovery is entry point
    severity: info
    failure_action: log_warning
```

**Execution Flow**:
```
User: /raise.1.discovery
    ↓
Kata Executor: Load kata flujo-01-discovery
    ↓
Kata Executor: Load pre-execution gate PRE-DISCOVERY-001
    ↓
Kata Executor: Run validators
    ↓ [PASS]
Kata Executor: Execute kata steps
    ↓ [FAIL]
Kata Executor: Display failure message, STOP
```

**Benefits**:
- **Jidoka enforcement**: Automatic stop on failed preconditions (no LLM interpretation needed)
- **Better UX**: Clear error message BEFORE agent starts working
- **Token savings**: Don't waste tokens on doomed execution

---

### 2.3 Runtime Validators (Continuous)

**Purpose**: Monitor agent behavior DURING execution to detect deviations.

**Example Use Cases**:
1. **Scope violation**: Agent modifies files outside kata scope (e.g., Discovery kata editing code files)
2. **API misuse**: Agent calls external APIs not declared in kata (e.g., Discovery kata calling GitHub API)
3. **Token budget exceeded**: Agent consuming excessive tokens (potential runaway loop)
4. **Time limit exceeded**: Kata taking >5 minutes (expected: 2 minutes)
5. **Unexpected tool usage**: Agent using tools not in kata skill list

**Implementation Pattern** (conceptual - requires runtime instrumentation):
```yaml
# Runtime monitoring policy
monitor_id: MON-DISCOVERY-001
monitor_type: runtime_behavior
applies_to: flujo-01-discovery

monitors:
  - monitor_id: MON-001
    name: File modification scope
    type: file_watcher
    allowed_paths:
      - specs/main/project_requirements.md
      - specs/main/*.md  # Allow auxiliary docs
    forbidden_paths:
      - src/**  # No code modification during Discovery
    violation_action: alert_and_continue  # Don't stop, but warn

  - monitor_id: MON-002
    name: API call monitoring
    type: api_interceptor
    allowed_apis: []  # Discovery should not call external APIs
    violation_action: stop_execution
    exception_message: "Discovery kata should not call external APIs. Use existing docs only."
```

**Implementation Challenges**:
- **Instrumentation required**: Need hooks into file system, network, LLM API calls
- **Performance overhead**: Monitoring adds latency
- **False positives**: Agent might have valid reason to violate policy (Shu-Ha-Ri progression)

**Recommendation**: **Phase 2 feature** (post-MVP). Start with pre/post-execution gates; add runtime monitoring when mature.

---

### 2.4 Post-Execution Validators (Current RaiSE Gates)

**Purpose**: Validate output artifact after kata completes.

**Current Implementation**:
- Markdown checklists (gate-discovery.md, gate-design.md, etc.)
- Human or LLM manually verifies criteria
- No automation (gate execution is interpretive, not deterministic)

**Example** (current gate-discovery.md):
```markdown
### Obligatorios
- [ ] 1. Título del proyecto claro
- [ ] 2. >= 5 requisitos funcionales
- [ ] 3. Cada requisito con criterios de aceptación
```

**Limitation**: Gates are descriptive, not executable. Relies on LLM or human to interpret checklist.

**Proposed Enhancement** (make gates executable):
```yaml
# gate-discovery-executable.yaml
gate_id: GATE-DISCOVERY-001
gate_type: post_execution
applies_to: flujo-01-discovery
artifact: specs/main/project_requirements.md

validations:
  - validation_id: VAL-001
    criterion: "Título del proyecto claro"
    check:
      type: frontmatter_field_exists
      field: titulo
    automated: true
    severity: error

  - validation_id: VAL-002
    criterion: ">= 5 requisitos funcionales"
    check:
      type: count
      selector: "## Requisitos Funcionales > list items starting with FR-"
      operator: ">="
      threshold: 5
    automated: true
    severity: error

  - validation_id: VAL-003
    criterion: "Cada requisito con criterios de aceptación"
    check:
      type: pattern_match_all
      selector: "### FR-* > subsection starting with '**Criterios de Aceptación'"
      match_all: true
    automated: true
    severity: error
```

**Benefits**:
- **Deterministic**: Same artifact always produces same gate result
- **Fast feedback**: Automated checks run in seconds
- **Auditable**: Gate results include evidence (which checks failed, line numbers)
- **CI/CD integration**: Run gates in pipeline, block PRs on failure

**Migration Path**:
1. Convert existing Markdown gates to YAML (dual format during transition)
2. Build gate executor CLI: `raise gate run gate-discovery`
3. Integrate with Kata Executor Harness (auto-run gates after kata)
4. Deprecate Markdown gates when YAML coverage complete

---

### 2.5 Handling Policy Violations Gracefully

**Design Principle**: Jidoka stops on defects, but UX should guide recovery.

**Violation Handling Strategies**:

| Severity | Action | Example |
|----------|--------|---------|
| **error** | Stop execution; display actionable error | "Missing file: specs/main/solution_vision.md → Run /raise.2.vision first" |
| **warning** | Log violation; allow continuation with user confirmation | "Low test coverage detected (45%, expected 70%). Continue? [y/N]" |
| **info** | Log for awareness; auto-continue | "Suggestion: Add API error handling examples in Tech Design" |

**Recovery Guidance Pattern**:
```yaml
validation:
  - rule_id: VR-005
    description: Solution Vision must exist before Tech Design
    check:
      type: file_exists
      path: specs/main/solution_vision.md
    severity: error
    on_fail:
      action: stop_execution
      message: "Solution Vision not found"
      recovery_guidance:
        - step: "Run /raise.2.vision to create Solution Vision"
        - step: "Ensure gate-vision passes"
        - step: "Re-run /raise.4.tech-design"
      related_docs:
        - docs/katas/flujo-02-solution-vision.md
```

**User Experience**:
```
Orquestador: /raise.4.tech-design

Kata Executor: Running pre-execution gate PRE-TECH-DESIGN-001...
Kata Executor: ❌ Validation failed: VR-005 (Solution Vision must exist)

📋 Recovery Guidance:
  1. Run /raise.2.vision to create Solution Vision
  2. Ensure gate-vision passes
  3. Re-run /raise.4.tech-design

📖 Reference: docs/katas/flujo-02-solution-vision.md

Execution stopped. Fix issues above and retry.
```

---

## 3. Guardrails Implementations (Prior Art)

### 3.1 Guardrails AI

**Website**: https://www.guardrailsai.com/
**GitHub**: https://github.com/guardrails-ai/guardrails

**Overview**: Python library for validating LLM inputs/outputs. Uses validators (pre-built or custom) to enforce constraints.

**Architecture**:
```
User Prompt → Guardrails → LLM → Guardrails → Validated Output
              (input validators)    (output validators)
```

**Validator Example** (built-in):
```python
from guardrails import Guard
from guardrails.validators import ValidLength, OneLine

# Define guard with validators
guard = Guard.from_string(
    validators=[
        ValidLength(min=10, max=100, on_fail="reask"),
        OneLine(on_fail="fix")
    ]
)

# Use with LLM
response = guard(
    llm_api=openai.ChatCompletion.create,
    prompt="Generate a project title",
    model="gpt-4"
)
```

**RAIL Spec** (XML-based schema for validation):
```xml
<rail version="0.1">
  <output>
    <string name="project_title"
            format="one-line"
            length="10 100"
            on-fail-one-line="reask"
            on-fail-length="reask"/>
  </output>
  <prompt>Generate a concise project title.</prompt>
</rail>
```

**Validators** (built-in library includes 50+):
- Text: ValidLength, RegexMatch, ValidURL, NoToxicity, PIIDetector
- Code: ValidPython, NoSecrets, ImportCheck
- Structured: ValidJSON, SchemaValidation, ValidChoices

**Custom Validator Example**:
```python
from guardrails.validators import Validator, register_validator

@register_validator("has_acceptance_criteria", data_type="string")
class HasAcceptanceCriteria(Validator):
    def validate(self, value, metadata):
        if "**Criterios de Aceptación:**" not in value:
            raise ValidationError("Missing acceptance criteria section")
        return value
```

**Failure Modes** (on_fail strategies):
- `reask`: Ask LLM to fix and retry
- `fix`: Apply programmatic fix (e.g., truncate, filter)
- `exception`: Raise error and stop
- `filter`: Remove invalid content
- `refrain`: Skip this output

**Applicability to RaiSE**:
- **Pro**: Input/output validation (ensure kata output meets schema)
- **Pro**: Reask pattern aligns with Jidoka (detect, stop, fix, continue)
- **Pro**: Extensive validator library (can reuse)
- **Con**: Python-only (RaiSE is CLI-agnostic)
- **Con**: RAIL spec (XML) less intuitive than YAML
- **Con**: Designed for single LLM call validation, not multi-step kata workflow

**Use Case in RaiSE**:
- **Output schema validation**: Ensure generated PRD matches expected structure
- **Compliance checks**: Validate frontmatter, sections, terminology
- **Content quality**: Check for clarity, completeness (via custom validators)

**Confidence**: HIGH (active project, well-documented, production-grade)

---

### 3.2 NeMo Guardrails (NVIDIA)

**Website**: https://github.com/NVIDIA/NeMo-Guardrails
**License**: Apache 2.0

**Overview**: Programmable guardrails for conversational AI. Uses Colang DSL to define dialog flows with safety rails.

**Architecture**:
```
User Message → Input Rails → LLM → Output Rails → Response
                  ↓                      ↓
            Dialog Rails (flow control during conversation)
```

**Colang DSL Example**:
```colang
# Define a flow for kata execution
define flow execute_discovery_kata
  user expressed intent to run discovery

  # Input rail: Check preconditions
  check preconditions for discovery
  if preconditions failed
    bot inform missing preconditions
    bot suggest resolution
    stop

  # Execute kata
  execute kata flujo-01-discovery

  # Output rail: Validate artifact
  validate artifact project_requirements.md
  if validation failed
    bot inform validation errors
    bot offer to retry
    stop

  bot confirm success
  bot suggest next step
```

**Three Types of Rails**:
1. **Input Rails**: Validate user input (intent detection, content moderation)
2. **Output Rails**: Validate LLM response (fact-checking, safety filters)
3. **Dialog Rails**: Control conversation flow (prevent jailbreaks, enforce workflow)

**Configuration** (YAML):
```yaml
# config.yml
models:
  - type: main
    engine: openai
    model: gpt-4

rails:
  input:
    flows:
      - check user input is not malicious
      - check user has required permissions
  output:
    flows:
      - check output is factually correct
      - check output does not leak sensitive info
  dialog:
    user_messages:
      embeddings_only_messages:
        - "run discovery kata"
        - "execute tech design"
    system_messages:
      task_complete:
        - "Kata completed successfully. Validation gate passed."
```

**Applicability to RaiSE**:
- **Pro**: Flow control (enforces kata sequence, prevents skipping steps)
- **Pro**: Intent detection (map user natural language to kata commands)
- **Pro**: Context-aware guardrails (rules change based on conversation state)
- **Con**: Colang learning curve
- **Con**: Designed for chat applications, not CLI workflows
- **Con**: Overkill for RaiSE's use case (katas are single-turn, not dialogs)

**Use Case in RaiSE**:
- **Input rails**: Validate user command before execution (e.g., reject `/raise.4.tech-design` if Vision missing)
- **Dialog rails**: Enforce kata sequence (must complete Discovery before Vision)
- **Output rails**: Validate generated artifacts (overlap with Guardrails AI)

**Confidence**: MEDIUM-HIGH (NVIDIA-backed, but niche use case)

---

### 3.3 Constitutional AI (Anthropic)

**Overview**: Training-time approach where LLM learns constitutional principles and self-critiques outputs during inference.

**Phases**:
1. **Training Phase (RLAIF)**:
   - LLM generates multiple responses
   - LLM critiques own responses against constitution
   - Self-revises to align with principles
   - Reinforcement learning on preferred responses

2. **Inference Phase**:
   - LLM internalizes constitutional principles
   - Applies self-critique during generation
   - Less reliance on explicit runtime guardrails

**Constitution Example** (principles embedded in training):
```
Principles:
1. Responses must be helpful, harmless, and honest
2. Avoid generating code with security vulnerabilities
3. Respect user privacy (never ask for PII)
4. Acknowledge uncertainty when knowledge is limited
```

**Applicability to RaiSE**:
- **Pro**: No runtime enforcement needed (behavior baked into model)
- **Pro**: Generalizes well (principles apply to novel scenarios)
- **Pro**: LLM self-corrects during generation (natural Jidoka)
- **Con**: Training-time only (RaiSE has no control over model training)
- **Con**: Not deterministic (principles are heuristic, not rules)
- **Con**: Cannot verify compliance (no audit trail)

**Use Case in RaiSE**:
- **Inspirational**: RaiSE Constitution (§1-§8 principles) could be embedded in agent prompts as "soft constraints"
- **Not enforceable**: Cannot guarantee compliance without runtime validation

**Confidence**: HIGH for conceptual alignment, LOW for practical enforcement

---

### 3.4 LlamaGuard (Meta)

**Overview**: Classifier model for content safety. Detects prompt injection, jailbreaks, toxic content, PII leakage.

**Architecture**:
```
User Input → LlamaGuard → [SAFE | UNSAFE] → LLM (if SAFE)
LLM Output → LlamaGuard → [SAFE | UNSAFE] → User (if SAFE)
```

**Categories** (content safety taxonomy):
- Violence & Hate
- Sexual Content
- Guns & Illegal Weapons
- Regulated Substances
- Self-Harm
- Criminal Activity
- Defamation
- Privacy Violations
- Specialized Advice (legal, medical, financial)

**Applicability to RaiSE**:
- **Pro**: Safety layer (prevents malicious prompts, toxic outputs)
- **Pro**: Fast inference (small model, <100ms latency)
- **Con**: Content safety focus (not governance/compliance)
- **Con**: Not extensible to RaiSE-specific rules (e.g., kata structure validation)

**Use Case in RaiSE**:
- **Input safety**: Filter malicious user input before kata execution
- **Output safety**: Detect if LLM leaks sensitive info in generated docs
- **Not applicable**: Governance enforcement (wrong domain)

**Confidence**: HIGH for safety use case, LOW for governance use case

---

### 3.5 Comparison Matrix

| Framework | Enforcement Timing | Policy Format | Extensibility | LLM-Friendliness | Use Case Fit (RaiSE) |
|-----------|-------------------|---------------|---------------|------------------|---------------------|
| **Guardrails AI** | Input/Output | RAIL (XML) + Python | High (custom validators) | Medium | 85% (output validation) |
| **NeMo Guardrails** | Input/Output/Dialog | Colang + YAML | Medium | Low | 60% (overkill for CLI) |
| **Constitutional AI** | Training-time | Natural language | None | High | 40% (not enforceable) |
| **LlamaGuard** | Input/Output | Predefined categories | Low | N/A | 30% (safety only) |

**Recommendation for RaiSE**: **Borrow patterns from Guardrails AI** (validators, reask, on_fail strategies), but implement with **Custom DSL** (YAML-based, simpler than RAIL).

---

## 4. Separation of Concerns: Policy vs Mechanism

### 4.1 The Principle

**Policy**: **WHAT** should be enforced (the rules)
**Mechanism**: **HOW** to enforce (the engine)

**Benefits**:
1. **Independent evolution**: Update policies without changing harness code
2. **Versioning**: Policies versioned in Git, diffs reviewable
3. **Testing**: Policies testable in isolation (unit tests for rules)
4. **Auditability**: Policy changes tracked, compliance verified
5. **Flexibility**: Different projects can use different policies

**Anti-Pattern** (current RaiSE commands):
```markdown
<!-- In .raise/commands/project/create-prd.md -->
## Outline

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`
   - Load template from `.specify/templates/raise/solution/project_requirements.md`

2. **Paso 1: Recopilar Contexto**:
   - Recopilar documentación existente
   - **Verificación**: La documentación existe y está accesible
   - > **Si no puedes continuar**: Documentación no encontrada → **JIDOKA**: Preguntar al usuario...
```

**Problem**: Policy (verificación, Jidoka trigger) embedded in command text. No separation.

**Refactored with Policy-Mechanism Separation**:

**Policy** (external YAML):
```yaml
# .raise/policies/create-prd-policy.yaml
kata_id: create-prd
steps:
  - step_id: step-1-gather-context
    preconditions:
      - check: file_exists
        path: docs/context.md
        on_fail:
          action: stop_execution
          message: "Documentation not found"
          recovery: "Ask user to provide context documents"
```

**Mechanism** (Kata Executor Harness):
```python
# Kata Executor (simplified pseudocode)
def execute_kata(kata_id, user_input):
    policy = load_policy(f"{kata_id}-policy.yaml")
    kata = load_kata(f"{kata_id}.md")

    for step in kata.steps:
        # Pre-execution gate
        step_policy = policy.get_step_policy(step.id)
        for precondition in step_policy.preconditions:
            result = evaluate_check(precondition)
            if not result.passed:
                handle_failure(precondition.on_fail)
                return  # JIDOKA: Stop on defect

        # Execute step
        execute_step(step, user_input)

        # Post-execution gate
        if step.has_validation_gate:
            gate_result = run_gate(step.validation_gate)
            if not gate_result.passed:
                handle_gate_failure(gate_result)
                return  # JIDOKA: Stop on defect
```

**Benefits**:
- **Kata content is pure process knowledge** (no enforcement logic)
- **Policy is declarative and testable** (YAML can be validated)
- **Harness is reusable** (same code for all katas)
- **Jidoka is automatic** (harness enforces stop, not LLM interpretation)

---

### 4.2 Version Control for Policies

**Challenge**: Policies evolve over time. How to track changes, deprecate old policies, migrate users?

**Solution Pattern** (SemVer for Policies):
```yaml
# .raise/policies/create-prd-policy.yaml
policy_version: 2.1.0  # SemVer: MAJOR.MINOR.PATCH
policy_id: create-prd-policy
compatible_kata_versions:
  - 2.x  # Works with kata v2.0, v2.1, etc.
deprecated: false
deprecation_date: null
replacement_policy: null

changelog:
  - version: 2.1.0
    date: 2026-01-29
    changes:
      - "Added precondition: check for solution_vision.md existence"
      - "Relaxed VR-003 severity from error to warning"
  - version: 2.0.0
    date: 2025-12-15
    changes:
      - "BREAKING: Migrated from Markdown checklist to YAML executable format"
      - "Added 5 new validation rules"
```

**Policy Lifecycle**:
1. **Active**: Default policy loaded by harness
2. **Deprecated**: Policy still works, but warning shown ("Policy v1.5 deprecated, upgrade to v2.0")
3. **Retired**: Policy no longer supported, harness refuses to load
4. **Archived**: Moved to `.raise/policies/archive/` for reference

**Migration Path**:
```bash
# CLI for policy management
$ raise policy list
create-prd-policy v2.1.0 (active)
tech-design-policy v1.8.0 (deprecated, upgrade to v2.0.0)

$ raise policy upgrade tech-design-policy
Upgrading tech-design-policy from v1.8.0 to v2.0.0...
⚠️  Breaking changes detected:
  - Validation rule VR-005 renamed to VR-012
  - Precondition CHK-003 now mandatory (was optional)
Continue? [y/N] y

✅ Upgraded to v2.0.0
```

---

### 4.3 How to Update Governance Without Changing Agent Code

**Current Problem**: If RaiSE wants to add new validation rule to Discovery gate, must:
1. Edit gate-discovery.md (Markdown checklist)
2. Re-prompt LLM to include new check
3. Hope LLM interprets correctly
4. No guarantee of enforcement

**With Policy-Mechanism Separation**:
1. Edit `.raise/policies/gate-discovery-policy.yaml`
2. Add new validation rule to YAML
3. Commit and push
4. Next kata execution automatically picks up new rule (no code change)

**Example**:
```yaml
# .raise/policies/gate-discovery-policy.yaml (before)
validations:
  - validation_id: VAL-002
    criterion: ">= 5 requisitos funcionales"
    check:
      type: count
      selector: "## Requisitos Funcionales > list items"
      operator: ">="
      threshold: 5
```

```yaml
# .raise/policies/gate-discovery-policy.yaml (after - new rule added)
validations:
  - validation_id: VAL-002
    criterion: ">= 5 requisitos funcionales"
    check:
      type: count
      selector: "## Requisitos Funcionales > list items"
      operator: ">="
      threshold: 5

  # NEW RULE (added 2026-01-29)
  - validation_id: VAL-006
    criterion: "Each requirement must have priority assigned"
    check:
      type: pattern_match_all
      selector: "### FR-* > line containing 'Prioridad:'"
      match_all: true
    automated: true
    severity: warning
    added_in_version: 2.1.0
```

**No agent code changes needed**. Policy engine reads YAML, executes checks.

---

## 5. Separation of Concerns: Kata vs Harness

### 5.1 Current Architecture (Conflated)

**Problem**: Current `.raise/commands/` files mix:
- **Process knowledge** (kata: what steps to perform)
- **Enforcement logic** (harness: when to stop, what to validate)
- **Execution instructions** (agent prompts: how to behave)

**Example** (`.raise/commands/project/create-prd.md`):
```markdown
## Outline

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`

2. **Paso 1: Recopilar Contexto**:
   - Recopilar documentación existente
   - **Verificación**: La documentación existe y está accesible
   - > **Si no puedes continuar**: Documentación no encontrada → **JIDOKA**: Preguntar al usuario...

3. **Paso 2: Crear Estructura del PRD**:
   [...]

N. **Finalize & Validate**:
   - Confirm file existence with check_file
   - Ejecutar gate `.specify/gates/raise/gate-discovery.md`
   - Run `.specify/scripts/bash/update-agent-context.sh`
```

**Conflation**:
- Step 1 has **harness concern** (run prerequisite script)
- Step 2 has **process knowledge** (what to do) AND **enforcement logic** (verificación, Jidoka)
- Step N has **harness concern** (execute gate)

---

### 5.2 Proposed Architecture (Separated)

**Three Layers**:
1. **Kata** (pure process knowledge, Markdown)
2. **Policy** (governance rules, YAML)
3. **Harness** (execution engine, Python/TypeScript)

**Kata** (`.raise/katas/flujo-01-discovery.md`):
```markdown
---
id: flujo-01-discovery
nivel: flujo
titulo: "Discovery: Creación del PRD"
template_asociado: templates/solution/project_requirements.md
validation_gate: gates/gate-discovery.md
policy: policies/discovery-policy.yaml
---

## Propósito

Transformar contexto del proyecto en un PRD estructurado.

## Pasos

### Paso 1: Recopilar Contexto

Recopilar documentación existente del proyecto:
- Business case
- Product briefs
- Stakeholder interviews
- Competitive analysis

**Output**: Lista de documentos relevantes.

### Paso 2: Identificar Requisitos Funcionales

Extraer requisitos funcionales clave del contexto. Documentar cada requisito con:
- ID único (FR-XXX)
- Descripción clara
- Prioridad (P0/P1/P2)
- Criterios de Aceptación

**Output**: >= 5 requisitos funcionales documentados.

[...más pasos...]
```

**Policy** (`.raise/policies/discovery-policy.yaml`):
```yaml
policy_id: discovery-policy
policy_version: 2.0.0
kata_id: flujo-01-discovery

preconditions:
  - check_id: PRE-001
    description: Context documents exist
    validator: file_exists_any
    params:
      paths:
        - docs/context.md
        - docs/product-brief.md
    severity: warning
    on_fail:
      action: log_warning
      message: "No context documents found. Consider running /raise.setup.analyze-codebase first."

step_policies:
  - step_id: step-2-identify-requirements
    validations:
      - rule_id: VR-001
        description: "Must have >= 5 functional requirements"
        check:
          type: count
          selector: "## Requisitos Funcionales > list items starting with FR-"
          operator: ">="
          threshold: 5
        severity: error
        on_fail:
          action: stop_execution
          message: "Insufficient functional requirements"
          recovery: "Add more requirements to reach minimum of 5"

post_validation:
  gate: gate-discovery
  gate_policy: gate-discovery-policy.yaml
```

**Harness** (Kata Executor):
```python
# Simplified pseudocode
class KataExecutor:
    def execute(self, kata_id, user_input):
        # Load artifacts
        kata = load_kata(kata_id)
        policy = load_policy(kata.policy)

        # Pre-execution gate
        self.run_preconditions(policy.preconditions)

        # Execute steps
        for step in kata.steps:
            # Display step to agent
            display_step_to_agent(step)

            # Agent executes (LLM generation)
            result = agent_execute_step(step, user_input)

            # Step validation (if policy defines checks for this step)
            step_policy = policy.get_step_policy(step.id)
            if step_policy:
                self.validate_step(result, step_policy)

        # Post-execution gate
        self.run_gate(policy.post_validation.gate)

    def run_preconditions(self, preconditions):
        for check in preconditions:
            result = self.evaluate_check(check)
            if not result.passed:
                self.handle_failure(check.on_fail)

    def validate_step(self, result, step_policy):
        for validation in step_policy.validations:
            check_result = self.evaluate_validation(result, validation)
            if not check_result.passed:
                self.handle_failure(validation.on_fail)

    def handle_failure(self, on_fail_config):
        if on_fail_config.action == "stop_execution":
            display_error(on_fail_config.message)
            display_recovery(on_fail_config.recovery)
            sys.exit(1)  # JIDOKA: Stop
        elif on_fail_config.action == "log_warning":
            log_warning(on_fail_config.message)
```

**Benefits**:
- **Kata is pure Markdown** (no YAML frontmatter with execution logic, just metadata)
- **Policy is declarative** (testable, versionable, reusable)
- **Harness is generic** (same code for all katas)
- **Jidoka is automatic** (harness stops on policy violation, no LLM interpretation)
- **LLM sees clean instructions** (kata steps are pure process guidance)

---

### 5.3 Harness Responsibilities

The Kata Executor Harness (to be built on spec-kit) should:

1. **Load Artifacts**:
   - Kata (Markdown from `.raise/katas/`)
   - Policy (YAML from `.raise/policies/`)
   - Templates (from `.raise/templates/`)
   - Gates (from `.raise/gates/`)

2. **Pre-Execution**:
   - Validate preconditions (policy-defined checks)
   - Check prerequisites (kata dependencies)
   - Display context to agent (relevant docs, previous artifacts)

3. **Execution**:
   - Display kata steps to LLM agent (one at a time or all at once)
   - Agent executes step (generates output)
   - Track progress (which step, time elapsed, tokens used)

4. **Mid-Execution** (optional, Phase 2):
   - Monitor agent behavior (file modifications, API calls)
   - Detect deviations (policy violations)
   - Trigger alerts or stops

5. **Post-Execution**:
   - Run validation gate (policy-defined checks)
   - Generate gate report (pass/fail, evidence)
   - Display results to user (✅ passed, ❌ failed with recovery guidance)

6. **Handoff**:
   - Suggest next command (based on kata handoff config)
   - Pass context to next kata (artifacts, state)

7. **Observability** (if telemetry enabled):
   - Log execution metrics (time, tokens, success/fail)
   - Track utilization (which kata sections used)
   - Report adherence (how well output matches policy)

---

## 6. Enterprise Patterns

### 6.1 How Enterprises Implement AI Governance Today

**Survey of Enterprise Practices** (based on industry patterns, not specific companies):

| Practice | Description | Adoption Level | Tooling |
|----------|-------------|----------------|---------|
| **Human-in-the-Loop Approval** | All AI outputs reviewed by human before deployment | High | Manual workflows, Slack/Email approvals |
| **Prompt Libraries** | Centralized, approved prompts; no ad-hoc prompting | Medium | Internal wikis, prompt management tools |
| **Output Filtering** | Keyword blacklists, regex filters on AI outputs | High | Custom scripts, Guardrails AI |
| **Model Fine-Tuning** | Train models on company-specific data with alignment | Low | Expensive, long cycles |
| **Audit Logging** | Log all AI interactions (prompts, outputs, users) | Medium | ELK stack, Datadog, Splunk |
| **Policy Enforcement** | Explicit policies encoded as rules | Low | Mostly manual checklists |
| **Red Teaming** | Regular adversarial testing of AI systems | Medium | Security teams, bug bounties |
| **Compliance Dashboards** | Real-time monitoring of AI usage against policies | Low | Custom dashboards, BI tools |

**Key Finding**: Most enterprises rely on **human review** and **post-hoc auditing** rather than **automated policy enforcement**. Gap for RaiSE to fill.

---

### 6.2 Approval Workflows for Agent Actions

**Pattern**: Multi-stage approval for high-risk actions.

**Example** (software deployment):
```yaml
# Approval workflow policy
action: deploy_to_production
risk_level: high

approval_chain:
  - stage: peer_review
    approvers: [team_members]
    required_approvals: 1
    timeout: 24h

  - stage: tech_lead_review
    approvers: [tech_leads]
    required_approvals: 1
    timeout: 48h

  - stage: security_review
    approvers: [security_team]
    required_approvals: 1
    timeout: 72h
    criteria:
      - no_secrets_in_code: true
      - security_scan_passed: true

automation:
  auto_approve_if:
    - all_tests_passed: true
    - no_high_severity_vulnerabilities: true
    - code_coverage: ">= 80%"

  escalate_if:
    - approval_timeout_exceeded: true
    - high_risk_changes_detected: true
```

**Applicability to RaiSE**:
- **Low**: RaiSE agents generate docs, not deploy code. Risk is low.
- **Possible use case**: Approval workflow for governance policy changes (new rules require team vote)

---

### 6.3 Audit Trails and Compliance Requirements

**Regulatory Requirements** (examples):
- **SOC 2**: Log all system access, changes to configuration
- **ISO 27001**: Access control, change management, audit logs
- **GDPR**: Data processing logs, consent tracking, deletion records
- **HIPAA**: Patient data access logs, PHI modification tracking

**Audit Trail Pattern** (for RaiSE Kata Executor):
```json
{
  "event_id": "evt_abc123",
  "timestamp": "2026-01-29T10:30:00Z",
  "event_type": "kata_execution",
  "kata_id": "flujo-01-discovery",
  "user_id_hash": "sha256(user_email)",
  "policy_version": "discovery-policy-v2.0.0",
  "preconditions_result": {
    "passed": true,
    "checks": [
      {"id": "PRE-001", "status": "PASS"}
    ]
  },
  "execution_result": {
    "started_at": "2026-01-29T10:30:05Z",
    "completed_at": "2026-01-29T10:35:20Z",
    "duration_seconds": 315,
    "tokens_consumed": 4567,
    "steps_completed": 5
  },
  "gate_result": {
    "gate_id": "gate-discovery",
    "status": "PASS",
    "validations": [
      {"id": "VAL-001", "status": "PASS"},
      {"id": "VAL-002", "status": "PASS", "value": 7, "threshold": 5},
      {"id": "VAL-003", "status": "PASS"}
    ]
  },
  "artifacts_generated": [
    "specs/main/project_requirements.md"
  ]
}
```

**Storage**: PostgreSQL (time-series optimized), retention policy 2 years.

**Querying**:
```sql
-- Find all failed gate executions in last 30 days
SELECT event_id, kata_id, gate_result->>'status', timestamp
FROM audit_log
WHERE event_type = 'kata_execution'
  AND gate_result->>'status' = 'FAIL'
  AND timestamp > NOW() - INTERVAL '30 days';
```

**Compliance Report**:
```
Kata Execution Compliance Report (2026-01-01 to 2026-01-29)

Total Executions: 1,247
Passed Gates: 1,189 (95.3%)
Failed Gates: 58 (4.7%)

Failed Gate Breakdown:
- gate-discovery: 12 failures (2.1% of discovery runs)
- gate-design: 31 failures (7.8% of design runs)
- gate-backlog: 15 failures (3.2% of backlog runs)

Top Failure Reasons:
1. VR-002: Insufficient functional requirements (18 occurrences)
2. VR-005: Missing architecture diagram (14 occurrences)
3. VR-007: No error handling specification (12 occurrences)

Policy Violations: 0 (no unauthorized policy overrides)
```

---

## 7. Specific Questions Answered

### 7.1 Can We Enforce "STOP" (Jidoka) Through Policy?

**Answer**: **YES**, with caveats.

**Mechanism**:
1. **Pre-execution gate stops execution before kata starts** (deterministic)
2. **Mid-execution monitoring detects violations and stops** (requires instrumentation)
3. **Post-execution gate stops handoff to next kata** (current RaiSE gates, but needs automation)

**Example** (pre-execution gate enforcing Jidoka):
```yaml
# Pre-execution policy
gate_id: PRE-TECH-DESIGN-001
gate_type: pre_execution
applies_to: flujo-03-tech-design

preconditions:
  - check_id: CHK-001
    name: Solution Vision exists
    validator: file_exists
    params:
      path: specs/main/solution_vision.md
    severity: error
    on_fail:
      action: stop_execution  # JIDOKA: Stop deterministically
      message: "Solution Vision not found. Tech Design cannot proceed without it."
      recovery_guidance:
        - "Run /raise.2.vision to create Solution Vision"
        - "Ensure gate-vision passes"
        - "Re-run /raise.4.tech-design"
```

**Execution**:
```
User: /raise.4.tech-design

Kata Executor: Running pre-execution gate PRE-TECH-DESIGN-001...
Kata Executor: Checking CHK-001: Solution Vision exists...
Kata Executor: ❌ FAILED

🛑 JIDOKA: Execution stopped.

Solution Vision not found. Tech Design cannot proceed without it.

📋 Recovery:
  1. Run /raise.2.vision to create Solution Vision
  2. Ensure gate-vision passes
  3. Re-run /raise.4.tech-design

Execution halted. No tokens consumed on Tech Design.
```

**Caveat**: Mid-execution monitoring (agent deviating during kata) requires runtime instrumentation, which is Phase 2 complexity.

---

### 7.2 Trade-Off: Strict Enforcement vs Agent Flexibility

**Spectrum**:
```
100% Strict                  Sweet Spot                     100% Flexible
│                                │                                │
│                                │                                │
▼                                ▼                                ▼
No LLM autonomy            70% rules / 30% heuristic        LLM does anything
Deterministic              Pre/post gates + guidelines       No enforcement
Low adaptability           Balanced: safety + creativity      High risk
```

**RaiSE Position**: **70-80% Strict, 20-30% Flexible**

**Strict (Enforced via Policy)**:
- File existence checks (deterministic)
- Schema validation (frontmatter, section structure)
- Dependency checks (kata prerequisites)
- Artifact completeness (min requirements met)
- Terminology compliance (use canonical terms from glossary)

**Flexible (Heuristic Guidelines)**:
- Writing style (agent chooses phrasing)
- Example selection (agent picks relevant examples)
- Diagram style (agent decides Mermaid vs PlantUML)
- Organization (agent reorders sections if clearer)

**Implementation**:
```yaml
# Policy defines strict rules
validations:
  - rule_id: VR-001
    enforcement: strict  # Deterministic check
    check:
      type: count
      threshold: 5

  - rule_id: VR-009
    enforcement: heuristic  # LLM interprets
    guidance: "Ensure Tech Design is understandable to junior developers"
    validation_method: llm_evaluation
    severity: info
```

**Why This Balance?**:
- **Strict rules** prevent catastrophic failures (missing files, invalid structure)
- **Heuristic guidelines** allow agent to adapt to context (Shu-Ha-Ri progression)
- **70/30 ratio** empirically effective (based on RaiSE's Constitution §7: Lean, eliminate waste but don't over-constrain)

---

### 7.3 How to Handle Policy Violations Gracefully?

**Design Principle**: Violations should be **informative, actionable, non-punitive**.

**Poor UX** (current state - LLM interpretation):
```
Orquestador: /raise.4.tech-design

Claude: I cannot proceed because the Solution Vision is missing. Please run /raise.2.vision first.

[User confused: Why did it fail? What exactly is missing? How do I fix it?]
```

**Good UX** (with policy-driven errors):
```
Orquestador: /raise.4.tech-design

Kata Executor: Running pre-execution gate PRE-TECH-DESIGN-001...
Kata Executor: ❌ Validation failed: CHK-001 (Solution Vision exists)

🛑 JIDOKA: Execution stopped due to failed precondition.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Problem:
   Solution Vision not found at: specs/main/solution_vision.md

🔍 Why this matters:
   Tech Design requires Solution Vision as input to define architecture.
   Without it, the design will lack strategic context.

🛠️  How to fix:
   1. Run: /raise.2.vision
   2. Ensure gate-vision passes (checklist in docs/gates/gate-vision.md)
   3. Re-run: /raise.4.tech-design

📖 Reference:
   Kata: docs/katas/flujo-02-solution-vision.md
   Gate: docs/gates/gate-vision.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execution halted. Fix the issue above and retry.
```

**Violation Handling Strategies**:

| Severity | User Action Required | Example |
|----------|---------------------|---------|
| **error** | MUST fix before continuing | Missing required file |
| **warning** | SHOULD fix, but can override | Low test coverage (45% vs 70% target) |
| **info** | Awareness only, no action needed | Suggestion to add examples |

**Override Mechanism** (for warnings):
```
Kata Executor: ⚠️  Warning: VR-008 failed (Test coverage 45%, expected 70%)

Continue anyway? [y/N] y

Kata Executor: Override recorded. Continuing execution...
[Logged to audit trail: user overrode warning VR-008]
```

**Escalation** (for repeated overrides):
```
Kata Executor: ⚠️  Warning: VR-008 failed (Test coverage 45%, expected 70%)
Kata Executor: Note: You've overridden this warning 3 times in the last week.
Kata Executor: Consider addressing test coverage to avoid future warnings.

Continue anyway? [y/N]
```

---

## 8. Recommendations for RaiSE Kata Harness

### 8.1 Adopt Three-Layer Architecture

**Proposed Structure**:
```
.raise/
├── katas/               # Layer 1: Process knowledge (Markdown)
│   ├── flujo-01-discovery.md
│   ├── flujo-02-solution-vision.md
│   └── flujo-03-tech-design.md
├── policies/            # Layer 2: Governance rules (YAML)
│   ├── discovery-policy.yaml
│   ├── vision-policy.yaml
│   └── tech-design-policy.yaml
├── templates/           # Artifact templates
│   └── solution/
│       └── project_requirements.md
├── gates/               # Validation gate definitions (YAML, not Markdown)
│   ├── gate-discovery.yaml
│   ├── gate-vision.yaml
│   └── gate-design.yaml
└── harness/             # Layer 3: Execution engine (to be built)
    ├── kata_executor.py
    ├── policy_engine.py
    └── gate_runner.py
```

**Migration Path**:
1. **Phase 0** (current): Katas in Markdown, gates in Markdown (interpretive)
2. **Phase 1** (MVP): Add policies (YAML), gates still Markdown, harness partially enforces policies
3. **Phase 2** (mature): Gates migrate to YAML (fully executable), harness fully automated
4. **Phase 3** (advanced): Runtime monitoring, advanced policy types

---

### 8.2 Policy DSL Specification (Initial)

**Five Core Policy Types** (MVP):

1. **precondition_check**: Validate before kata starts
2. **artifact_schema**: Validate output structure
3. **validation_gate**: Post-execution quality checks
4. **handoff_gate**: Validate before next kata
5. **jidoka_trigger**: Auto-stop conditions

**Schema** (JSON Schema for policy YAML):
```yaml
# .raise/policies/policy-schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RaiSE Policy Schema",
  "type": "object",
  "required": ["policy_id", "policy_version", "policy_type", "applies_to"],
  "properties": {
    "policy_id": {"type": "string"},
    "policy_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "policy_type": {"enum": ["precondition_check", "artifact_schema", "validation_gate", "handoff_gate", "jidoka_trigger"]},
    "applies_to": {
      "type": "object",
      "properties": {
        "katas": {"type": "array", "items": {"type": "string"}},
        "artifacts": {"type": "array", "items": {"type": "string"}}
      }
    },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["check_id", "description", "validator", "severity", "on_fail"],
        "properties": {
          "check_id": {"type": "string"},
          "description": {"type": "string"},
          "validator": {"type": "string"},
          "params": {"type": "object"},
          "severity": {"enum": ["error", "warning", "info"]},
          "on_fail": {
            "type": "object",
            "required": ["action", "message"],
            "properties": {
              "action": {"enum": ["stop_execution", "log_warning", "log_info"]},
              "message": {"type": "string"},
              "recovery_guidance": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  }
}
```

**Validators Library** (built-in validators):
- `file_exists`
- `file_exists_any`
- `frontmatter_valid`
- `section_present`
- `count` (list items, headings, etc.)
- `pattern_match`
- `pattern_match_all`
- `schema_validation` (JSON Schema for YAML/JSON artifacts)

**Extensibility**: Allow custom validators (Python plugins):
```python
# .raise/policies/custom_validators/has_acceptance_criteria.py
from raise.policy_engine import Validator

class HasAcceptanceCriteria(Validator):
    validator_name = "has_acceptance_criteria"

    def validate(self, artifact, params):
        content = artifact.read()
        if "**Criterios de Aceptación:**" not in content:
            return ValidationResult(
                passed=False,
                message="Missing acceptance criteria section in requirement"
            )
        return ValidationResult(passed=True)
```

---

### 8.3 Implement Pre-Execution Gates

**Current Gap**: RaiSE has no pre-execution validation. Katas start, consume tokens, then fail at the end.

**Proposed**:
```yaml
# .raise/policies/pre-discovery-policy.yaml
policy_id: pre-discovery-policy
policy_type: precondition_check
applies_to:
  katas: [flujo-01-discovery]

preconditions:
  - check_id: PRE-001
    description: "Context documents available"
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
        - "Or provide context in command arguments: /raise.1.discovery --context 'Project ABC aims to...'"

  - check_id: PRE-002
    description: "User has write access to specs/main/"
    validator: directory_writable
    params:
      path: specs/main/
    severity: error
    on_fail:
      action: stop_execution
      message: "Cannot write to specs/main/. Check permissions."
      recovery_guidance:
        - "Run: chmod u+w specs/main/"
        - "Or run kata with sudo (not recommended)"
```

**Execution Flow**:
```
User: /raise.1.discovery --context "E-commerce platform for selling widgets"

Kata Executor: Loading kata flujo-01-discovery...
Kata Executor: Running pre-execution checks (pre-discovery-policy)...
Kata Executor:   [⚠️  WARN] PRE-001: Context documents available → No files found
Kata Executor:   [✅ PASS] PRE-002: Write access to specs/main/

⚠️  Warning: No context documents found. PRD will be based solely on user input.
   Suggestion: If context exists, add to docs/ directory

Continue? [Y/n] Y

Kata Executor: Starting kata execution...
[... kata runs ...]
```

---

### 8.4 Add Runtime Monitoring (Phase 2)

**Goal**: Detect mid-execution violations (agent deviating from expected behavior).

**Monitors** (conceptual - requires instrumentation):
1. **File Modification Monitor**: Track which files agent touches
2. **API Call Monitor**: Log external API calls (if any)
3. **Token Usage Monitor**: Alert if kata consuming excessive tokens
4. **Time Limit Monitor**: Warn if kata taking too long

**Example**:
```yaml
# .raise/policies/discovery-runtime-monitoring.yaml
policy_id: discovery-runtime-monitoring
policy_type: runtime_monitoring
applies_to:
  katas: [flujo-01-discovery]

monitors:
  - monitor_id: MON-001
    name: "File modification scope"
    type: file_watcher
    allowed_paths:
      - specs/main/project_requirements.md
      - specs/main/*.md
    forbidden_paths:
      - src/**
      - .raise/**
    violation_action: alert_and_continue
    violation_message: "Warning: Agent modifying files outside Discovery scope"

  - monitor_id: MON-002
    name: "Token budget"
    type: token_counter
    threshold: 10000  # Max tokens for Discovery kata
    violation_action: stop_execution
    violation_message: "Token budget exceeded. Possible infinite loop or overly complex PRD."
```

**Implementation**: Requires instrumenting Kata Executor to intercept:
- File system calls (wrap `open()`, `write()`)
- Network calls (wrap `requests`, `urllib`)
- LLM API calls (wrap `openai.ChatCompletion.create()`)

**Complexity**: HIGH. Recommend Phase 2 (post-MVP).

---

### 8.5 Use Policy DSL for Gates

**Current State**: Gates are Markdown checklists (`.raise/gates/gate-discovery.md`).

**Problem**: Not executable. Relies on human or LLM interpretation.

**Proposed**: Migrate gates to YAML (executable).

**Example Migration**:

**Before** (Markdown):
```markdown
# Gate-Discovery: Validación del PRD

## Criterios Obligatorios
- [ ] 1. Título del proyecto claro
- [ ] 2. >= 5 requisitos funcionales
- [ ] 3. Cada requisito con criterios de aceptación
```

**After** (YAML):
```yaml
# .raise/gates/gate-discovery.yaml
gate_id: gate-discovery
gate_version: 2.0.0
applies_to: flujo-01-discovery
artifact: specs/main/project_requirements.md

validations:
  - validation_id: VAL-001
    criterion: "Título del proyecto claro"
    description: "Frontmatter must have 'titulo' field with non-empty value"
    check:
      type: frontmatter_field_exists
      field: titulo
    automated: true
    severity: error

  - validation_id: VAL-002
    criterion: ">= 5 requisitos funcionales"
    description: "Section 'Requisitos Funcionales' must have >= 5 list items starting with FR-"
    check:
      type: count
      selector: "## Requisitos Funcionales > list items[starts-with='FR-']"
      operator: ">="
      threshold: 5
    automated: true
    severity: error

  - validation_id: VAL-003
    criterion: "Cada requisito con criterios de aceptación"
    description: "Each FR-* section must have subsection 'Criterios de Aceptación'"
    check:
      type: pattern_match_all
      selector: "### FR-* > subsection[heading='Criterios de Aceptación']"
      match_all: true
    automated: true
    severity: error
```

**Gate Executor** (CLI):
```bash
$ raise gate run gate-discovery

Running gate: gate-discovery (v2.0.0)
Artifact: specs/main/project_requirements.md

Validating...
  [✅ PASS] VAL-001: Título del proyecto claro
  [✅ PASS] VAL-002: >= 5 requisitos funcionales (found: 7)
  [❌ FAIL] VAL-003: Cada requisito con criterios de aceptación
    → FR-003 missing 'Criterios de Aceptación' subsection
    → FR-006 missing 'Criterios de Aceptación' subsection

Gate Result: FAIL (2 errors)

🛑 JIDOKA: Fix validation errors before proceeding to next phase.

Fix:
  1. Add 'Criterios de Aceptación' to FR-003
  2. Add 'Criterios de Aceptación' to FR-006
  3. Re-run: raise gate run gate-discovery
```

---

### 8.6 Separate Jidoka from LLM Instructions

**Current Approach** (embedded in kata Markdown):
```markdown
### Paso 2: Identificar Requisitos

- Extraer requisitos del contexto
- **Verificación**: >= 5 requisitos documentados
- > **Si no puedes continuar**: Menos de 5 requisitos → **JIDOKA**: Preguntar al usuario por más contexto
```

**Problem**: Relies on LLM to interpret "Si no puedes continuar" and stop. Not deterministic.

**Proposed Approach** (policy-enforced):

**Kata** (pure process, no enforcement logic):
```markdown
### Paso 2: Identificar Requisitos

Extraer requisitos funcionales del contexto. Documentar cada requisito con:
- ID único (FR-XXX)
- Descripción clara
- Prioridad (P0/P1/P2)
- Criterios de Aceptación

**Output**: Lista de requisitos funcionales documentados.
```

**Policy** (enforcement logic):
```yaml
# .raise/policies/discovery-policy.yaml
step_policies:
  - step_id: step-2-identify-requirements
    post_step_validation:
      - rule_id: VR-002
        description: ">= 5 requisitos funcionales"
        check:
          type: count
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
          jidoka_trigger: true  # Explicit Jidoka enforcement
```

**Execution** (harness enforces):
```
Kata Executor: Executing Step 2: Identificar Requisitos...

[LLM generates output]

Kata Executor: Validating Step 2 output (discovery-policy → step-2-identify-requirements)...
Kata Executor:   [❌ FAIL] VR-002: >= 5 requisitos funcionales (found: 3, expected: >= 5)

🛑 JIDOKA: Execution stopped due to validation failure.

Insufficient functional requirements (found: 3, expected: >= 5)

🛠️  Recovery:
  1. Review context documents for more requirements
  2. Ask user for additional scope
  3. Break down existing requirements into smaller units

Retry Step 2? [y/N]
```

**Benefits**:
- **Deterministic**: Harness detects violation, not LLM interpretation
- **Separation of concerns**: Kata is pure process, policy is enforcement
- **Testable**: Policy can be unit-tested independently

---

## 9. Implementation Roadmap

### Phase 1: MVP (Weeks 1-4)

**Goal**: Prove concept with basic policy enforcement.

**Deliverables**:
1. **Policy DSL Specification** (YAML schema, 5 core policy types)
2. **Policy Engine** (Python CLI: `raise policy validate <policy.yaml>`)
3. **Pre-execution Gates** (3 policies: discovery, vision, tech-design)
4. **Gate Migration** (convert 3 Markdown gates to YAML)
5. **Basic Kata Executor** (load kata + policy, run preconditions, execute, run gate)

**Success Criteria**:
- User runs `/raise.1.discovery`
- Pre-execution gate runs, checks preconditions
- Kata executes (via LLM)
- Post-execution gate runs (YAML-based), deterministic pass/fail
- If fail: display actionable error with recovery guidance (no ambiguity)

---

### Phase 2: Observability (Weeks 5-8)

**Goal**: Add telemetry and gate reporting.

**Deliverables**:
1. **Audit Logging** (log all kata executions, gate results to PostgreSQL)
2. **Gate Dashboard** (CLI: `raise gate report` shows pass/fail trends)
3. **Policy Versioning** (support SemVer for policies, migration warnings)
4. **Custom Validators** (plugin system for project-specific checks)

**Success Criteria**:
- Team runs 20 katas over 2 weeks
- Dashboard shows: 18 passed, 2 failed (gate-design)
- Failure analysis identifies root cause (missing architecture diagrams)
- Policy updated to clarify requirement

---

### Phase 3: Runtime Monitoring (Weeks 9-12)

**Goal**: Add mid-execution monitoring (optional, advanced).

**Deliverables**:
1. **File Watcher** (monitor file modifications during kata)
2. **Token Budget Monitor** (alert if kata exceeds expected token usage)
3. **Time Limit Monitor** (alert if kata taking too long)
4. **Deviation Alerts** (notify user if agent violating policy, but don't stop)

**Success Criteria**:
- User runs kata that modifies file outside scope
- Runtime monitor detects, displays warning
- User confirms intentional, execution continues (logged to audit trail)

---

### Phase 4: Advanced Features (Weeks 13-16)

**Goal**: Mature governance capabilities.

**Deliverables**:
1. **Approval Workflows** (multi-stage approval for policy changes)
2. **Policy Testing Framework** (`raise policy test <policy.yaml> --scenario <test.json>`)
3. **Visual Policy Editor** (low-code UI for non-technical users)
4. **Integration with External Tools** (Semgrep, ESLint for code validation)

**Success Criteria**:
- Non-developer (PM) can create new validation rule via UI
- Policy tested before deployment
- Policy change goes through approval workflow (team vote)

---

## 10. Conclusion

### Summary of Key Findings

1. **Policy-Mechanism Separation Feasible**: OPA, Guardrails AI, NeMo prove pattern works. RaiSE should adopt.

2. **Custom DSL Recommended**: YAML-based DSL lowers learning curve, aligns with RaiSE philosophy (Heutagogy).

3. **Three-Layer Architecture**: Kata (process), Policy (governance), Harness (execution). Current commands conflate these.

4. **Pre-Execution Gates Missing**: Major gap. Add precondition checks to fail fast.

5. **Executable Gates Needed**: Current Markdown gates not deterministic. Migrate to YAML.

6. **Jidoka Enforceable**: Yes, via policy (not LLM interpretation). Harness detects violations, stops automatically.

7. **Trade-off: 70% Strict, 30% Flexible**: Balance enforcement with adaptability. Strict for structure, flexible for content.

8. **Graceful Violation Handling**: Informative errors, actionable recovery guidance, non-punitive.

### Recommendations Recap

1. **Adopt Three-Layer Architecture** (Kata | Policy | Harness)
2. **Implement Pre-Execution Gates** (fail fast on preconditions)
3. **Add Runtime Monitoring** (Phase 2 - detect deviations mid-execution)
4. **Use Policy DSL for Gates** (migrate Markdown → YAML)
5. **Separate Jidoka from LLM Instructions** (policy-enforced, not prompt-based)

### Next Steps

1. **Review this research** with Emilio and RaiSE team
2. **Decide on Phase 1 scope** (MVP features)
3. **Design Policy DSL schema** (finalize YAML structure)
4. **Prototype Policy Engine** (CLI for policy validation)
5. **Convert 1 gate to YAML** (gate-discovery as proof of concept)
6. **Build Basic Kata Executor** (load kata, run policy, execute, validate)
7. **Test with 3 katas** (discovery, vision, tech-design)
8. **Iterate based on feedback**

---

## References

### Industry Standards & Tools

- **OPA (Open Policy Agent)**: https://www.openpolicyagent.org/
- **Cedar (AWS)**: https://www.cedarpolicy.com/
- **Guardrails AI**: https://www.guardrailsai.com/, https://github.com/guardrails-ai/guardrails
- **NeMo Guardrails (NVIDIA)**: https://github.com/NVIDIA/NeMo-Guardrails
- **Semgrep**: https://semgrep.dev/docs/writing-rules/rule-syntax
- **SARIF**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- **LlamaGuard**: https://github.com/meta-llama/PurpleLlama

### RaiSE Framework Documents

- **Constitution**: `docs/framework/v2.1/model/00-constitution-v2.md`
- **Glossary**: `docs/framework/v2.1/model/20-glossary-v2.1.md`
- **ADR-007 (Guardrails)**: `.private/decisions/adr-007-guardrails.md`
- **Governance Bridge Spec**: `specs/main/research/bmad-brownfield-analysis/governance-bridge-spec.md`
- **Kata Discrepancy Analysis**: `specs/main/research/outputs/kata-command-discrepancy-analysis.md`
- **Observable Gates Feature**: `specs/main/research/speckit-critiques/stories/feature-003-observable-gates.md`
- **Semantic Density Research**: `specs/main/research/sar-component/semantic-density/semantic-density-research-report.md`

### Academic & Industry Papers

- **"Does Prompt Formatting Have Any Impact on LLM Performance?"** (arXiv:2411.10541) - Format comprehension research
- **Prompt Engineering Guide** (https://www.promptingguide.ai/) - Few-shot examples, best practices
- **Constitutional AI** (Anthropic) - RLAIF, self-critique, principle-based training

---

**End of Research Report**

**Confidence**: HIGH (synthesis of established patterns, RaiSE-specific analysis, actionable recommendations)

**Ready for**: Validation by RaiSE team, prototype development, iterative refinement

**Questions for Follow-up**:
1. Should RaiSE build custom policy engine or adopt OPA/Guardrails?
2. What's the priority: pre-execution gates (Phase 1) or runtime monitoring (Phase 2)?
3. Should policy DSL use YAML or explore Cedar-like syntax?
4. How to handle policy versioning and migration (breaking changes)?
