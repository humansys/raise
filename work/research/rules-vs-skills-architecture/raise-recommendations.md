# RaiSE Framework: Rules vs. Skills Implementation Recommendations

**Research ID**: RES-ARCH-COMPARE-RULES-SKILLS-001
**Part**: RaiSE Recommendations (D3)
**Date**: 2026-01-23
**Version**: 1.0.0

---

## Executive Summary

Based on comprehensive research into Rules (Context) vs. Skills (Tools) architectures for agentic code generation, this document provides **actionable recommendations** for the RaiSE framework.

**Core Recommendation**: RaiSE should support **BOTH** paradigms through a hybrid architecture:
1. **Rules** for communicating philosophy, patterns, and stylistic guidance
2. **Skills** for deterministic enforcement, validation, and external data access
3. **Hybrid Artifacts** that pair rules (explain why) with skills (enforce what)

**Strategic Goal**: Enable RaiSE to build agents that **know the guidelines** (via rules) and **can enforce them** (via skills) agentically.

**Timeline**:
- **Phase 1** (Current): Rules foundation (`raise.rules.generate`)
- **Phase 2** (3 months): Skills scaffolding (`raise.skills.generate`)
- **Phase 3** (6 months): Hybrid integration (`raise.hybrid.generate`)
- **Phase 4** (12 months): Dynamic optimization (RAG-for-Rules, Tool Search integration)

---

## 1. Current State Analysis

### 1.1 What RaiSE Has Today

**Implemented**:
- ✅ `raise.rules.generate`: Automated rule extraction from brownfield code
- ✅ Dual traceability: Rules + Analysis documents + Governance registry
- ✅ Evidence-based generation: Requires 3-5 examples + 2 counter-examples
- ✅ Governance registry (`specs/main/ai-rules-reasoning.md`)
- ✅ Integration with Cursor (`.cursor/rules/*.mdc`)

**Architecture**:
```
Brownfield Code
    ↓
raise.rules.generate
    ↓
.cursor/rules/[ID]-[name].mdc (Rules)
specs/main/analysis/rules/analysis-for-[name].md (Rationale)
specs/main/ai-rules-reasoning.md (Registry)
```

**Strengths**:
- Excellent for **pattern mining** (extracting implicit knowledge)
- Strong **traceability** (every rule has documented rationale)
- **Team-shareable** (Git-versioned)
- Low **authoring friction** (markdown files)

### 1.2 What's Missing

**Gaps**:
- ❌ **Enforcement**: Rules suggest, but don't enforce
- ❌ **Validation**: No automated validation of rule compliance
- ❌ **External Data**: Cannot fetch live docs, API schemas, etc.
- ❌ **Scaffolding**: No code generation from templates
- ❌ **Dynamic Loading**: All rules loaded always (token overhead)
- ❌ **Skills Infrastructure**: No MCP server generation or tool scaffolding

**Opportunities**:
1. **Add enforcement layer** via validation scripts/tools
2. **Generate MCP servers** for external integrations
3. **Pair rules with tools** for hybrid artifacts
4. **Optimize token usage** via dynamic rule loading

---

## 2. Recommended Architecture

### 2.1 The Hybrid Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    USER / ORCHESTRATOR                       │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  RULES (Context)    │         │  SKILLS (Tools)     │
│  - Philosophy       │         │  - Enforcement      │
│  - Examples         │         │  - Validation       │
│  - Patterns         │         │  - Data Fetching    │
│  - Principles       │         │  - Scaffolding      │
└─────────────────────┘         └─────────────────────┘
            │                               │
            │        ┌─────────────┐        │
            └───────▶│   HYBRID    │◀───────┘
                     │  - Rules    │
                     │  - Tools    │
                     │  - Aligned  │
                     └─────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  GENERATED CODE       │
                │  (Guided + Validated) │
                └───────────────────────┘
```

### 2.2 Three-Tier Command Structure

**Tier 1: Rules Generation** (Existing, Enhanced)
```
raise.rules.generate
→ Input: Brownfield code OR architectural decision
→ Output: .mdc rule file + analysis document
→ Use Case: Communicating patterns, philosophy, examples
```

**Tier 2: Skills Generation** (NEW)
```
raise.skills.generate
→ Input: Skill specification (JSON/YAML)
→ Output: MCP server OR validation script
→ Use Case: Enforcement, validation, data fetching, scaffolding
```

**Tier 3: Hybrid Generation** (NEW)
```
raise.hybrid.generate
→ Input: Architectural pattern + validation requirements
→ Output: Rule file (.mdc) + Tool (script or MCP server)
→ Use Case: Philosophy + enforcement pairs
```

---

## 3. Phase 1: Enhance raise.rules.generate (Immediate - 1 month)

### 3.1 Add Validation Option

**Enhancement**: `--with-validation` flag

**Behavior**:
```bash
raise.rules.generate --pattern "repository-pattern" --with-validation
```

**Output**:
1. `.cursor/rules/pattern-100-repository.mdc` (Rule)
2. `.specify/scripts/validate-repository-pattern.sh` (Validation script)
3. `specs/main/analysis/rules/analysis-for-repository-pattern.md` (Analysis)

**Rule Template** (Enhanced):
```markdown
---
id: pattern-100-repository
category: pattern
priority: P0
validation_script: .specify/scripts/validate-repository-pattern.sh
---

# Repository Pattern

**Purpose**: Isolate data access logic from business logic.

## Specification

Use repository classes for database access:

**Do This**:
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()
```

**Don't Do This**:
```python
# Direct DB access in business logic
def process_user(user_id: int):
    db = SessionLocal()  # Bad: direct DB access
    user = db.query(User).filter(User.id == user_id).first()
```

## Verification

Run validation script:
```bash
.specify/scripts/validate-repository-pattern.sh src/
```

This checks that:
- Database queries are encapsulated in repository classes
- Business logic doesn't directly import SQLAlchemy models
```

**Validation Script Template**:
```bash
#!/bin/bash
# validate-repository-pattern.sh
# Validates repository pattern usage

DIR="${1:-.}"

echo "Validating repository pattern in $DIR..."

# Check for direct DB access in business logic
violations=$(grep -r "db.query" "$DIR/domain/" 2>/dev/null)

if [ -n "$violations" ]; then
  echo "❌ FAIL: Direct database queries in business logic:"
  echo "$violations"
  exit 1
fi

# Check for repository classes in data layer
repos=$(find "$DIR/data/" -name "*repository.py" 2>/dev/null)

if [ -z "$repos" ]; then
  echo "⚠️  WARNING: No repository classes found in data layer"
  exit 2
fi

echo "✅ PASS: Repository pattern correctly implemented"
exit 0
```

### 3.2 Integration with Existing Workflow

**Modified Outline** for `raise.rules.generate`:
```markdown
3. **Iterative Extraction & Generation**:
   FOR EACH pattern:
     a. Collect evidence
     b. Create analysis document
     c. Design rule (YAML + content)
     d. IF --with-validation:
          i. Generate validation script
          ii. Reference script in rule
     e. Write rule file (.mdc)
     f. IF --with-validation:
          i. Write validation script to .specify/scripts/
          ii. Test script with sample code
```

### 3.3 Governance Updates

**Enhanced Registry** (`specs/main/ai-rules-reasoning.md`):
```markdown
| ID | Rule | Date | Objective | Analysis | Validation |
|----|------|------|-----------|----------|------------|
| 100 | Repository Pattern | 2026-01-20 | Isolate data access | [Analysis](./analysis/rules/...) | [Script](../../.specify/scripts/validate-repository-pattern.sh) |
```

---

## 4. Phase 2: Create raise.skills.generate (3 months)

### 4.1 Command Specification

**Purpose**: Generate MCP servers, validation scripts, and tool definitions

**Usage**:
```bash
raise.skills.generate --spec skill-spec.yaml
```

**Input Specification** (`skill-spec.yaml`):
```yaml
name: validate_fastapi_endpoints
type: validation  # validation | data-fetcher | scaffold
language: python  # python | typescript | bash
description: Validates FastAPI endpoints follow best practices

checks:
  - name: uses_pydantic_models
    description: Ensure request/response use Pydantic models
    failure_message: "Endpoint missing Pydantic models"

  - name: has_dependency_injection
    description: Check for Depends(get_db) in signature
    failure_message: "Endpoint not using dependency injection"

  - name: has_error_handling
    description: Verify HTTPException used for errors
    failure_message: "Endpoint missing error handling"

inputs:
  - name: file_path
    type: string
    required: true
    description: Path to Python file to validate

outputs:
  - name: result
    type: ValidationResult
    schema:
      passed: boolean
      violations: array<string>
      warnings: array<string>
```

**Output**:
1. **MCP Server** (if type != bash):
   - `/.specify/mcp-servers/validate-fastapi/server.py`
   - `/.specify/mcp-servers/validate-fastapi/tool_definition.json`
2. **Validation Script** (if type == validation):
   - `.specify/scripts/validate-fastapi-endpoints.sh`
3. **Documentation**:
   - `.specify/mcp-servers/validate-fastapi/README.md`
4. **Tests**:
   - `.specify/mcp-servers/validate-fastapi/tests/test_validation.py`

### 4.2 Tool Templates by Type

#### Type 1: Validation Tool

**Generated MCP Server** (`validate-fastapi/server.py`):
```python
import ast
from mcp import MCPServer, Tool, ValidationResult

server = MCPServer(name="validate-fastapi")

@server.tool(
    name="validate_fastapi_endpoint",
    description="Validates FastAPI endpoints follow best practices"
)
def validate_endpoint(file_path: str) -> ValidationResult:
    """Validate FastAPI endpoint implementation"""

    with open(file_path, 'r') as f:
        code = f.read()

    tree = ast.parse(code)
    violations = []
    warnings = []

    # Check 1: Uses Pydantic models
    has_pydantic = "pydantic" in code.lower()
    if not has_pydantic:
        violations.append("Endpoint missing Pydantic models")

    # Check 2: Has dependency injection
    has_depends = "Depends(" in code
    if not has_depends:
        violations.append("Endpoint not using dependency injection")

    # Check 3: Has error handling
    has_http_exception = "HTTPException" in code
    if not has_http_exception:
        warnings.append("Consider adding HTTPException for errors")

    return ValidationResult(
        passed=len(violations) == 0,
        violations=violations,
        warnings=warnings
    )

if __name__ == "__main__":
    server.run()
```

**Generated Script** (`.specify/scripts/validate-fastapi-endpoints.sh`):
```bash
#!/bin/bash
# validate-fastapi-endpoints.sh
# Validates FastAPI endpoints

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "ERROR: File not found: $FILE"
  exit 1
fi

# Call MCP server (or run inline checks)
python .specify/mcp-servers/validate-fastapi/server.py validate_endpoint "$FILE"
```

#### Type 2: Data Fetcher Tool

**Spec Example** (`fetch-library-versions.yaml`):
```yaml
name: fetch_npm_versions
type: data-fetcher
language: typescript
description: Fetches latest versions of npm packages

inputs:
  - name: package_name
    type: string
    required: true

outputs:
  - name: version_info
    type: object
    schema:
      current: string
      latest: string
      outdated: boolean
```

**Generated MCP Server** (`fetch-npm-versions/server.ts`):
```typescript
import { MCPServer, Tool } from "@modelcontextprotocol/sdk";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const server = new MCPServer({ name: "fetch-npm-versions" });

server.addTool({
  name: "fetch_npm_version",
  description: "Fetches latest versions of npm packages",
  inputSchema: {
    type: "object",
    properties: {
      package_name: { type: "string" }
    },
    required: ["package_name"]
  },
  async handler({ package_name }) {
    const { stdout } = await execAsync(
      `npm view ${package_name} version --json`
    );
    const latest = JSON.parse(stdout);

    // Get current version from package.json
    const packageJson = require("./package.json");
    const current = packageJson.dependencies[package_name] || "not installed";

    return {
      current,
      latest,
      outdated: current !== latest
    };
  }
});

server.start();
```

#### Type 3: Scaffold Tool

**Spec Example** (`scaffold-fastapi-endpoint.yaml`):
```yaml
name: scaffold_fastapi_endpoint
type: scaffold
language: python
description: Generates FastAPI endpoint with standard structure

inputs:
  - name: resource_name
    type: string
    required: true
    description: Name of resource (e.g., "user", "order")

  - name: methods
    type: array<string>
    required: false
    default: ["GET", "POST", "PUT", "DELETE"]

template_file: templates/fastapi-endpoint.py.jinja
output_path: src/api/routers/{{resource_name}}.py
```

**Generated MCP Tool**:
```python
from jinja2 import Template

@server.tool(name="scaffold_fastapi_endpoint")
def scaffold_endpoint(resource_name: str, methods: list = None):
    """Generate FastAPI endpoint from template"""

    if methods is None:
        methods = ["GET", "POST", "PUT", "DELETE"]

    with open(".specify/templates/fastapi-endpoint.py.jinja") as f:
        template = Template(f.read())

    code = template.render(
        resource=resource_name,
        Resource=resource_name.capitalize(),
        methods=methods
    )

    output_path = f"src/api/routers/{resource_name}.py"
    with open(output_path, 'w') as f:
        f.write(code)

    return {"created": output_path}
```

### 4.3 Integration with raise.rules.generate

**Companion Rules for Tools**:

When a tool is generated, optionally generate a companion rule that references it:

```bash
raise.skills.generate --spec validate-fastapi.yaml --with-rule
```

**Generated Rule** (`.cursor/rules/tool-fastapi-validation.mdc`):
```markdown
---
description: FastAPI endpoint validation (use after generating endpoints)
tool: validate_fastapi_endpoint
---

# FastAPI Endpoint Validation

After generating or modifying FastAPI endpoints, validate them:

**Tool**: `validate_fastapi_endpoint`

**Usage**:
```python
# AI can call this tool automatically
result = validate_fastapi_endpoint(file_path="src/api/routers/user.py")
```

**Checks**:
- ✅ Uses Pydantic models for request/response
- ✅ Uses dependency injection (Depends)
- ✅ Includes error handling (HTTPException)

**Fix violations** by following pattern in [FastAPI rule](./fastapi.mdc).
```

---

## 5. Phase 3: Hybrid Generation (6 months)

### 5.1 Command Specification

**Purpose**: Generate aligned rule + tool pairs

**Usage**:
```bash
raise.hybrid.generate --pattern repository-pattern --analysis specs/main/analysis/patterns/repository.md
```

**Workflow**:
1. **Parse Analysis Document**: Extract pattern definition, examples, validation criteria
2. **Generate Rule**: Philosophy, examples, rationale (`.mdc`)
3. **Generate Tool**: Validation logic based on criteria (script or MCP)
4. **Link Them**: Rule references tool, tool references rule
5. **Update Registry**: Single entry for hybrid artifact

### 5.2 Hybrid Artifact Structure

**Example**: Repository Pattern

**Files Generated**:
```
.cursor/rules/hybrid-repository-pattern.mdc
.specify/scripts/validate-repository-pattern.sh
.specify/mcp-servers/repository-analyzer/server.py
specs/main/analysis/patterns/repository.md
```

**Rule Content** (`.cursor/rules/hybrid-repository-pattern.mdc`):
```markdown
---
id: hybrid-repository-pattern
category: architecture
priority: P0
validation_tool: validate_repository_pattern
mcp_server: repository-analyzer
---

# Repository Pattern (Hybrid)

**Philosophy**: Isolate data access logic from business logic to enable testability and reduce coupling.

## Pattern Specification

[... examples, do this / don't do this ...]

## Verification

### Automated Validation

**Script**: `.specify/scripts/validate-repository-pattern.sh`
```bash
.specify/scripts/validate-repository-pattern.sh src/
```

**MCP Tool**: `validate_repository_pattern`
- AI can call this automatically after generating code
- Checks: Repository classes exist, no direct DB access in business layer

### Manual Review

- Repository classes in `src/data/repositories/`
- Business logic in `src/domain/` doesn't import SQLAlchemy
- Dependency injection used to provide repositories

## Rationale

[Link to analysis document: specs/main/analysis/patterns/repository.md]

**Benefits**:
- **Testability**: Mock repositories in unit tests
- **Decoupling**: Business logic unaware of DB implementation
- **Flexibility**: Swap DB without changing business logic
```

**Tool Script**:
```bash
#!/bin/bash
# .specify/scripts/validate-repository-pattern.sh
# [... validation logic as shown in Phase 1 ...]
```

**MCP Server** (optional, for advanced analysis):
```python
# .specify/mcp-servers/repository-analyzer/server.py

@server.tool(name="analyze_repository_usage")
def analyze_repositories(directory: str):
    """Analyze repository pattern usage in codebase"""
    # - Find all repository classes
    # - Check for direct DB access violations
    # - Return detailed report
```

### 5.3 Governance for Hybrid Artifacts

**Enhanced Registry**:
```markdown
| ID | Artifact | Type | Date | Rule | Tool | Analysis |
|----|----------|------|------|------|------|----------|
| H01 | Repository Pattern | Hybrid | 2026-01-23 | [.mdc](../.cursor/rules/hybrid-repository-pattern.mdc) | [script](../../.specify/scripts/validate-repository-pattern.sh) | [Doc](./analysis/patterns/repository.md) |
```

---

## 6. Phase 4: Dynamic Optimization (12 months)

### 6.1 RAG-for-Rules Implementation

**Problem**: 100+ rules consume 50K+ tokens (25% of 200K window)

**Solution**: Index rules in vector DB, retrieve only relevant ones

**Architecture**:
```
┌─────────────────┐
│  User Query     │
│ "Create FastAPI │
│  endpoint"      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic Search │
│ (Vector DB)     │
│ - 100+ rules    │
│   indexed       │
└────────┬────────┘
         │
         ▼ (Top 5 relevant)
┌─────────────────┐
│ - fastapi.mdc   │
│ - pydantic.mdc  │
│ - testing.mdc   │
│ - security.mdc  │
│ - routing.mdc   │
└────────┬────────┘
         │
         ▼ (Load into context)
┌─────────────────┐
│ AI generates    │
│ endpoint code   │
│ following 5     │
│ loaded rules    │
└─────────────────┘
```

**Implementation**:

1. **Indexing Script** (`.specify/scripts/index-rules.py`):
```python
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.create_collection("rules")

# Index all .mdc files
for rule_file in Path(".cursor/rules").rglob("*.mdc"):
    with open(rule_file) as f:
        content = f.read()

    embedding = model.encode(content)
    collection.add(
        documents=[content],
        embeddings=[embedding],
        metadatas=[{"file": str(rule_file)}],
        ids=[rule_file.stem]
    )
```

2. **Retrieval Integration** (in AI workflow):
```python
def get_relevant_rules(query: str, top_k: int = 5) -> list:
    """Retrieve top-k relevant rules for query"""
    query_embedding = model.encode(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return [r['metadata']['file'] for r in results]

# Usage:
user_query = "Create FastAPI endpoint for users"
relevant_rules = get_relevant_rules(user_query)
# Load only these 5 rules into context
```

**Benefits**:
- **Token Savings**: 90% reduction (50K → 5K tokens)
- **Cost Savings**: $0.01/query → $0.001/query
- **Latency**: Faster TTFT (fewer tokens to process)
- **Scalability**: Can maintain 1000+ rules without context bloat

### 6.2 Dynamic Tool Loading (Tool Search Integration)

**Current State**: All tool definitions loaded (30 tools × 100 tokens = 3K tokens)

**Anthropic's Tool Search**: Load tools on-demand

**Integration**:
```json
{
  "tools": [
    {
      "name": "validate_fastapi_endpoint",
      "defer_loading": true,
      "description": "Use for validating FastAPI endpoint code"
    }
  ]
}
```

**Behavior**:
- Tool definition NOT loaded initially
- When AI determines validation needed → fetches definition dynamically
- **Token Savings**: 85% (Anthropic's benchmark)

**Implementation** (Claude Code integration):
```bash
export ENABLE_TOOL_SEARCH=true
export ENABLE_EXPERIMENTAL_MCP_CLI=false
```

### 6.3 Hybrid Retrieval (Rules + Tools)

**Advanced Pattern**: Combine RAG-for-Rules with Dynamic Tool Loading

**Workflow**:
```
User: "Create and validate FastAPI endpoint"
  ↓
Semantic Search:
  - Retrieves: fastapi.mdc, validation.mdc (2 rules)
  ↓
AI reads rules, generates code
  ↓
AI determines validation needed
  ↓
Tool Search:
  - Fetches: validate_fastapi_endpoint definition
  ↓
AI calls tool → validates code → reports results
```

**Result**: Minimal token usage, maximum capability

---

## 7. Integration with Existing RaiSE Commands

### 7.1 raise.1.analyze.code

**Enhancement**: After analyzing brownfield code, suggest rules AND tools

**Modified Output**:
```markdown
## Recommendations

### Patterns Identified (Generate Rules)
1. Repository Pattern (12 occurrences)
   - Command: `raise.rules.generate --pattern repository`
   - Or: `raise.hybrid.generate --pattern repository` (with validation)

2. Service Layer Pattern (8 occurrences)
   - Command: `raise.rules.generate --pattern service-layer`

### Architecture Violations (Generate Tools)
1. Direct DB access in business logic (5 files)
   - Command: `raise.skills.generate --spec validate-clean-arch.yaml`

2. Missing error handling (10 endpoints)
   - Command: `raise.skills.generate --spec validate-error-handling.yaml`
```

### 7.2 raise.2.vision

**Enhancement**: Vision documents reference both rules and tools

**Vision Template Update**:
```markdown
## Architecture Decision: Repository Pattern

**Philosophy**: Isolate data access...

**Artifacts**:
- **Rule**: `.cursor/rules/repository-pattern.mdc` (guides AI)
- **Tool**: `.specify/scripts/validate-repository-pattern.sh` (enforces)

**Generation**:
```bash
raise.hybrid.generate --pattern repository-pattern --analysis specs/main/adrs/ADR-005-repository.md
```
```

### 7.3 raise.4.tech-design

**Enhancement**: Tech Design includes Guardrails section

**Tech Design Template Update**:
```markdown
## Guardrails

### Rules (AI Guidance)
- Architecture: Repository pattern, service layer
- Security: No secrets in code, input validation
- Testing: Test-first development

### Tools (Enforcement)
- Linters: ESLint, Pylint, mypy
- Security: Bandit, Snyk
- Validation: Custom scripts for architecture boundaries

### Hybrid Artifacts
- Repository Pattern: Rule + AST validator
- API Security: Rule + secret scanner

**Generation**:
```bash
# Generate all guardrails
raise.hybrid.generate --from-tech-design specs/main/tech_design.md
```
```

---

## 8. Development Roadmap

### Month 1: Foundation Enhancement

**Week 1-2**: Enhance `raise.rules.generate`
- [ ] Add `--with-validation` flag
- [ ] Generate validation script templates
- [ ] Update rule template to reference scripts
- [ ] Update governance registry schema

**Week 3-4**: Create validation script library
- [ ] Template: Pattern validation (AST-based)
- [ ] Template: Security check (regex-based)
- [ ] Template: Architecture boundary check
- [ ] Documentation: How to write validation scripts

**Deliverable**: `raise.rules.generate --with-validation` working

---

### Months 2-4: Skills Generation

**Month 2**: Spec and Templates
- [ ] Design skill specification format (YAML)
- [ ] Create MCP server templates (Python, TypeScript)
- [ ] Create validation script templates (Bash)
- [ ] Create test templates (pytest, jest)

**Month 3**: Command Implementation
- [ ] Implement `raise.skills.generate` command
- [ ] Parser for spec files
- [ ] Code generators for each template type
- [ ] Integration tests

**Month 4**: Integration and Documentation
- [ ] Integrate with existing commands (`raise.1.analyze.code`)
- [ ] Documentation: Spec format, examples
- [ ] Sample specs for common scenarios
- [ ] Tutorial: Creating first skill

**Deliverable**: `raise.skills.generate` working, with 10+ example specs

---

### Months 5-7: Hybrid Generation

**Month 5**: Analysis-to-Hybrid Pipeline
- [ ] Parser for analysis documents (extract validation criteria)
- [ ] Generator: Rule from analysis (existing, enhance)
- [ ] Generator: Tool from validation criteria (new)
- [ ] Linker: Reference tool in rule, rule in tool

**Month 6**: Command Implementation
- [ ] Implement `raise.hybrid.generate` command
- [ ] Workflow orchestration (rule + tool generation)
- [ ] Governance registry updates for hybrid artifacts
- [ ] Quality gates for generated pairs

**Month 7**: Real-World Testing
- [ ] Generate hybrid artifacts for 10 common patterns
- [ ] Test with real projects
- [ ] Refine based on feedback
- [ ] Documentation and examples

**Deliverable**: `raise.hybrid.generate` working, validated on real patterns

---

### Months 8-12: Dynamic Optimization

**Month 8-9**: RAG-for-Rules
- [ ] Implement rule indexing (vector embeddings)
- [ ] Implement semantic search (ChromaDB/Pinecone)
- [ ] Integrate with rule loading (fetch top-k)
- [ ] Benchmark token savings

**Month 10-11**: Tool Search Integration
- [ ] Research Anthropic's Tool Search API
- [ ] Implement defer_loading for generated tools
- [ ] Integrate with MCP server generation
- [ ] Benchmark token/latency savings

**Month 12**: Hybrid Retrieval
- [ ] Combine RAG-for-Rules + Tool Search
- [ ] Optimize retrieval strategy
- [ ] Performance testing
- [ ] Documentation and best practices

**Deliverable**: Optimized token usage (80%+ reduction), maintained capability

---

## 9. Success Metrics

### Phase 1 (Rules Enhanced)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Rules with validation scripts | 80% | Count rules with `validation_script` field |
| Validation script pass rate | > 90% | Run scripts on codebase, check pass rate |
| False positive rate | < 10% | Developer feedback on incorrect violations |
| Developer satisfaction | ≥ 4/5 | Survey after 1 month usage |

### Phase 2 (Skills Generated)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Skills generated per week | 5+ | Track command usage |
| Tool reliability | > 95% | Monitor tool execution failures |
| Token overhead | < 10% | Measure tool definitions token usage |
| Latency per tool call | < 2 seconds | Monitor tool execution time |

### Phase 3 (Hybrid Artifacts)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hybrid artifacts generated | 20+ | Count rule+tool pairs |
| Alignment score | > 90% | Rule and tool check same criteria |
| Developer preference | > 70% choose hybrid | Survey: Prefer hybrid vs rule-only |
| Code quality improvement | Measurable | Bug rate, maintainability index |

### Phase 4 (Optimized)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Token usage reduction | 80% | Before/after RAG-for-Rules |
| Query cost reduction | 80% | Cost per query before/after |
| Latency improvement | 50% faster TTFT | Time to first token |
| Rule base scalability | 500+ rules | Maintain performance with large rule sets |

---

## 10. Risk Assessment and Mitigation

### Risk 1: Complexity Overhead

**Risk**: Adding tools increases system complexity, maintenance burden

**Mitigation**:
- Start with **simple tools** (bash scripts) before MCP servers
- Provide **templates** to reduce authoring friction
- Clear **documentation** and examples
- **Incremental adoption**: Rules → Scripts → MCP servers

**Fallback**: If tools too complex, stay with rules + manual validation

---

### Risk 2: Tool Reliability

**Risk**: Tools can fail (bugs, dependencies, external APIs down)

**Mitigation**:
- **Error handling**: Graceful failures, clear error messages
- **Testing**: Unit tests for all generated tools
- **Sandboxing**: Limit tool capabilities (no destructive actions)
- **Monitoring**: Track tool failure rates

**Fallback**: Tools fail soft - AI continues without enforcement

---

### Risk 3: Token Economics Change

**Risk**: MCP/Tool pricing changes, RAG-for-Rules becomes more expensive

**Mitigation**:
- **Monitor costs**: Track token usage and costs monthly
- **Configurable**: Allow disabling dynamic loading if costs spike
- **Alternatives**: Support multiple retrieval strategies

**Fallback**: Revert to static rule loading if dynamic costs exceed benefit

---

### Risk 4: MCP Adoption Uncertainty

**Risk**: MCP doesn't become standard, investment wasted

**Mitigation**:
- **Multi-protocol**: Support MCP + Cursor rules + GitHub Copilot instructions
- **Abstraction layer**: Generate tools that work across platforms
- **Validation scripts**: Work anywhere (bash/Python universal)

**Fallback**: Validation scripts are portable, MCP servers can be abandoned

---

## 11. Quick Start Guide (For RaiSE Developers)

### Step 1: Generate Your First Rule with Validation (Phase 1)

```bash
# Analyze brownfield code
raise.1.analyze.code

# Generate rule with validation
raise.rules.generate --pattern repository-pattern --with-validation

# Output:
# - .cursor/rules/pattern-100-repository.mdc
# - .specify/scripts/validate-repository-pattern.sh
# - specs/main/analysis/rules/analysis-for-repository.md
```

### Step 2: Create Your First Skill (Phase 2)

```bash
# Write spec
cat > validate-fastapi.yaml <<EOF
name: validate_fastapi_endpoints
type: validation
language: python
description: Validates FastAPI endpoint best practices
# ... (full spec)
EOF

# Generate skill
raise.skills.generate --spec validate-fastapi.yaml

# Output:
# - .specify/mcp-servers/validate-fastapi/server.py
# - .specify/scripts/validate-fastapi-endpoints.sh
```

### Step 3: Generate Hybrid Artifact (Phase 3)

```bash
# Generate rule + tool pair
raise.hybrid.generate --pattern repository-pattern

# Output:
# - .cursor/rules/hybrid-repository-pattern.mdc (Rule)
# - .specify/scripts/validate-repository-pattern.sh (Tool)
# - specs/main/analysis/patterns/repository.md (Analysis)
```

### Step 4: Optimize with RAG (Phase 4)

```bash
# Index all rules for semantic search
.specify/scripts/index-rules.py

# Enable dynamic loading in Claude Code
export ENABLE_TOOL_SEARCH=true

# Rules and tools now loaded on-demand
# Token usage drops 80%+
```

---

## 12. Conclusion

**Strategic Imperative**: RaiSE must support **both Rules and Skills** to build complete agentic systems.

**Phased Approach**:
1. **Enhance** existing rules generation (add validation scripts)
2. **Build** new skills generation (MCP servers, tools)
3. **Integrate** into hybrid artifacts (aligned philosophy + enforcement)
4. **Optimize** with dynamic loading (RAG-for-Rules, Tool Search)

**Expected Outcomes**:
- **For Developers**: AI that knows your standards AND enforces them
- **For Teams**: Consistent code quality across all AI-generated code
- **For RaiSE**: Industry-leading agentic framework with hybrid architecture

**Timeline**: 12 months to full hybrid architecture with optimization

**Next Steps**:
1. Review and approve this recommendation
2. Create detailed design docs for Phase 1 (Month 1)
3. Begin implementation of `raise.rules.generate --with-validation`
4. Establish success metrics and monitoring

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-23
**Maintained By**: RaiSE Research Team
**Status**: Proposed - Awaiting Approval
