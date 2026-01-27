# Decision Framework: Rule or Skill?

**Research ID**: RES-ARCH-COMPARE-RULES-SKILLS-001
**Part**: Decision Framework (D2)
**Date**: 2026-01-23
**Version**: 1.0.0

---

## Purpose

This framework provides **practical, actionable guidance** for engineering teams to decide whether to implement a coding standard, constraint, or capability as:
- **Rule** (Context - passive guidance via .mdc, CLAUDE.md, instructions)
- **Skill/Tool** (Active execution via MCP, scripts, APIs)
- **Hybrid** (Both - rule explains, tool enforces)

---

## Quick Reference: The Decision Matrix

| Question | Rule | Tool | Hybrid |
|----------|------|------|--------|
| **Requires external data?** (API, DB, live docs) | ❌ | ✅ | Tool for fetch, Rule for usage |
| **Hard requirement?** (security, compliance, correctness) | ❌ | ✅ | Rule explains, Tool validates |
| **Deterministically validatable?** (linter, regex, AST) | ❌ | ✅ | ✅ |
| **Nuanced judgment?** (style, naming, architecture philosophy) | ✅ | ❌ | Rule guides, Tool optional |
| **Complex logic?** (100+ lines of conditional rules) | ❌ | ✅ | Tool clearer than prose |
| **Code template/scaffold?** (boilerplate generation) | ❌ | ✅ | Rule shows example, Tool scaffolds |
| **Philosophy or principle?** (explain "why") | ✅ | ❌ | Rule explains, Tool enforces |
| **Token budget available?** (< 20% of context window) | ✅ | N/A | Consider both |
| **Team already maintains it?** (linter, CI config) | N/A | ✅ | Align Rule with existing Tool |

---

## Decision Tree (Detailed)

```
START: You have a coding standard, constraint, or capability to implement.

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Does this require EXTERNAL DATA?                        │
│ (APIs, databases, live documentation, filesystem access)        │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   TOOL      Continue to Step 2
   (AI cannot
   access without
   tool)

           │
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Is this a HARD REQUIREMENT?                             │
│ (Security, compliance, legal, correctness - cannot be violated) │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   TOOL      Continue to Step 3
   (Cannot trust
   AI to always
   comply)

           │
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Can this be validated DETERMINISTICALLY?                │
│ (Linter, regex pattern, AST analysis, unit test)                │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   HYBRID    Continue to Step 4
   (Rule explains
   why, Tool
   validates)

           │
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Does this involve NUANCED JUDGMENT?                     │
│ (Style preferences, naming context, architectural philosophy)   │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   RULE      Continue to Step 5
   (AI excels at
   contextual
   judgment)

           │
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Is this COMPLEX BRANCHING LOGIC?                        │
│ (100+ lines of conditional rules, decision table)               │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   TOOL      Continue to Step 6
   (Code clearer
   than prose)

           │
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Is this a CODE TEMPLATE/SCAFFOLD?                       │
│ (Boilerplate generation, consistent file structures)            │
└─────────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────┐
     │ YES       │ NO
     ▼           ▼
   TOOL      RULE
   (Deterministic  (Default: guidance
   scaffold)       via context)
```

---

## Heuristic Rules (Quick Decision)

### Use RULE when:

1. ✅ **Explaining philosophical principles**
   - "We prefer functional programming for data transformations"
   - "Use immutable data structures where possible"
   - "Follow SOLID principles"

2. ✅ **Defining naming conventions**
   - "Use camelCase for JavaScript, snake_case for Python"
   - "Prefix private methods with underscore"
   - "Name test files with `.test.ts` suffix"

3. ✅ **Establishing code style preferences**
   - "Prefer async/await over Promise chains"
   - "Use destructuring for object parameters"
   - "Keep functions under 50 lines when possible"

4. ✅ **Providing examples and anti-patterns**
   - "Do This: `const user = await getUser(id);`"
   - "Don't Do This: `getUser(id).then(...)`"

5. ✅ **Communicating domain context**
   - "In this system, an Order transitions through: Draft → Pending → Confirmed → Shipped"
   - "The `UserService` handles authentication, `ProfileService` handles user data"

6. ✅ **Suggesting best practices**
   - "Document public API functions with JSDoc"
   - "Include error handling for all async operations"

7. ✅ **Token budget allows** (< 20% of context window)
   - You have 200K token window, rules consume < 40K tokens

### Use TOOL when:

1. ✅ **Fetching live documentation or data**
   - Latest library versions from npm/pip
   - Current database schema
   - Live API documentation
   - Jira ticket details for context

2. ✅ **Running linters or validators**
   - ESLint, Pylint, Black, Prettier
   - Type checkers (TypeScript, mypy)
   - Security scanners (Snyk, Bandit)

3. ✅ **Querying databases or APIs**
   - Fetch user records for testing
   - Query code search (Sourcegraph)
   - Retrieve configuration values

4. ✅ **Generating boilerplate from templates**
   - Scaffold FastAPI endpoints with standard structure
   - Create React components with default props
   - Generate test stubs

5. ✅ **Enforcing security or compliance rules**
   - "No API keys in code" → Scan for secrets
   - "All inputs must be sanitized" → Run SAST tool
   - "Dependencies must be up-to-date" → Check for CVEs

6. ✅ **Verifying correctness deterministically**
   - "All Pydantic models must have examples" → AST check
   - "Database migrations must have rollback" → File structure validation
   - "Tests must cover 80% of code" → Coverage tool

7. ✅ **Accessing external systems**
   - Read from filesystem (search codebase)
   - Call external APIs (fetch data)
   - Execute shell commands (run tests)

### Use HYBRID when:

1. ✅ **Rule explains the "why," tool enforces the "what"**
   - Rule: "Use repository pattern to isolate data access (enables testing, reduces coupling)"
   - Tool: AST validator checks for repository usage

2. ✅ **Philosophy + validation pairing**
   - Rule: "FastAPI endpoints must use dependency injection for database sessions"
   - Tool: Linter checks for `Depends(get_db)` in route signatures

3. ✅ **Template + verification**
   - Rule: Shows example of correct API endpoint structure
   - Tool: Scaffolds endpoint from template, validates against spec

4. ✅ **Best practice + enforcement**
   - Rule: "All public functions need docstrings (for maintainability)"
   - Tool: Linter warns if docstring missing

5. ✅ **Gradual migration strategy**
   - Start with Rule (guidance only)
   - Add Tool later when pattern stabilizes (enforcement)

---

## Real-World Scenarios (with Decisions)

### Scenario 1: "Never commit API keys"

**Analysis**:
- Hard requirement? ✅ YES (security)
- Deterministically validatable? ✅ YES (regex scan)
- External data? ❌ NO

**Decision**: **TOOL** (pre-commit hook scanning for secrets)

**Implementation**:
```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached | grep -E '(API_KEY|SECRET|PASSWORD)=\w+'; then
  echo "ERROR: Possible secret in commit"
  exit 1
fi
```

**Optional Rule** (explaining why):
```markdown
# Security: No Secrets in Code

Never commit API keys, passwords, or secrets.

**Why**: Secrets in version control can be exposed if repo becomes public.

**How**: Use environment variables or secret management (AWS Secrets Manager, etc.)

**Validation**: Pre-commit hook scans for patterns like `API_KEY=xxx`
```

**Result**: Hybrid (Rule explains philosophy, Tool enforces)

---

### Scenario 2: "Prefer descriptive variable names"

**Analysis**:
- Hard requirement? ❌ NO (style preference)
- Nuanced judgment? ✅ YES (context-dependent)
- Deterministically validatable? ❌ NO (what is "descriptive"?)

**Decision**: **RULE** (AI judges contextually)

**Implementation**:
```markdown
# Naming Conventions: Descriptive Variables

Use variable names that explain **intent**, not just **type**.

**Do This**:
```python
user_count = get_active_users()  # Clear: counting active users
max_retries = 3  # Clear: retry limit
```

**Don't Do This**:
```python
x = get_active_users()  # Unclear: what is x?
n = 3  # Unclear: what does n represent?
```

**Exception**: Loop indices (`i`, `j`) are acceptable for simple loops.
```

**Result**: Rule only (no tool needed)

---

### Scenario 3: "Use FastAPI dependency injection for database sessions"

**Analysis**:
- Hard requirement? ⚠️ MEDIUM (architecture decision)
- Deterministically validatable? ✅ YES (check for `Depends(get_db)`)
- Nuanced judgment? ✅ YES (why dependency injection is good)

**Decision**: **HYBRID** (Rule explains, Tool validates)

**Rule Implementation**:
```markdown
# FastAPI: Dependency Injection for Database

Use FastAPI's `Depends()` for database sessions, not global DB objects.

**Why**:
- **Testability**: Easy to mock `get_db` in tests
- **Lifecycle**: Session auto-closes after request
- **Clarity**: Function signature declares dependencies

**Example**:
```python
from fastapi import Depends
from sqlalchemy.orm import Session

@router.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Validation**: Run `.specify/scripts/validate-fastapi-di.sh`
```

**Tool Implementation** (`.specify/scripts/validate-fastapi-di.sh`):
```bash
#!/bin/bash
# Validate FastAPI routes use Depends for DB sessions

file="$1"

# Check for Session parameter without Depends
if grep -E '@router\.(get|post|put|delete)' "$file" | \
   grep 'Session' | \
   grep -v 'Depends(get_db)'; then
  echo "ERROR: FastAPI route uses Session without Depends(get_db)"
  exit 1
fi

echo "✓ All routes use Depends for DB sessions"
exit 0
```

**Result**: Hybrid (Rule explains philosophy + provides example, Tool validates compliance)

---

### Scenario 4: "Fetch latest library versions for dependency updates"

**Analysis**:
- Requires external data? ✅ YES (npm registry, PyPI)
- Hard requirement? ❌ NO (maintenance task)
- Deterministically validatable? N/A (fetching, not validating)

**Decision**: **TOOL** (AI cannot fetch without tool)

**Implementation** (MCP Tool):
```python
# MCP Tool: check_npm_updates
import subprocess
import json

def check_npm_updates() -> dict:
    """Fetch latest versions of npm packages in package.json"""
    result = subprocess.run(
        ["npm", "outdated", "--json"],
        capture_output=True,
        text=True
    )
    outdated = json.loads(result.stdout)
    return {
        "outdated_packages": len(outdated),
        "details": outdated
    }
```

**Result**: Tool only (Rule not needed - straightforward task)

---

### Scenario 5: "Follow clean architecture layers (presentation, business, data)"

**Analysis**:
- Hard requirement? ❌ NO (architectural philosophy)
- Nuanced judgment? ✅ YES (where to draw boundaries)
- Deterministically validatable? ⚠️ PARTIALLY (can check imports)

**Decision**: **HYBRID** (Rule explains, Tool checks import violations)

**Rule Implementation**:
```markdown
# Architecture: Clean Architecture Layers

This project follows clean architecture with 3 layers:

1. **Presentation** (`src/api/`): FastAPI routes, request/response models
2. **Business** (`src/domain/`): Business logic, domain models
3. **Data** (`src/data/`): Database access, repositories

**Dependency Rule**:
- Presentation → Business → Data (one direction only)
- Data should NOT import from Business or Presentation
- Business should NOT import from Presentation

**Why**: Prevents tight coupling, enables testing (mock data layer), business logic reusable.

**Example**:
```python
# ✅ Correct: Presentation imports Business
# src/api/users.py
from src.domain.user_service import UserService

# ❌ Incorrect: Data imports Presentation
# src/data/user_repository.py
from src.api.schemas import UserOut  # VIOLATION
```

**Validation**: Run `.specify/scripts/validate-clean-arch.sh`
```

**Tool Implementation**:
```bash
#!/bin/bash
# Check for clean architecture violations

# Data layer should not import from api/ or domain/
if grep -r "from src.api" src/data/ || \
   grep -r "from src.domain" src/data/; then
  echo "ERROR: Data layer imports from API or Domain (violation)"
  exit 1
fi

# Business layer should not import from api/
if grep -r "from src.api" src/domain/; then
  echo "ERROR: Domain layer imports from API (violation)"
  exit 1
fi

echo "✓ Clean architecture dependencies respected"
exit 0
```

**Result**: Hybrid (Rule explains layering philosophy, Tool catches violations)

---

### Scenario 6: "Scaffold new FastAPI endpoint with standard structure"

**Analysis**:
- Code template? ✅ YES (boilerplate generation)
- Deterministic? ✅ YES (template is fixed)
- Nuanced judgment? ❌ NO (template is standard)

**Decision**: **TOOL** (scaffold generator)

**Implementation** (MCP Tool or Script):
```python
# scaffold_fastapi_endpoint.py
import os

def scaffold_endpoint(name: str, path: str, methods: list):
    """Generate FastAPI endpoint with standard structure"""

    template = f'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.data.database import get_db
from src.domain.{name}_service import {name.capitalize()}Service
from src.api.schemas.{name} import {name.capitalize()}In, {name.capitalize()}Out

router = APIRouter(prefix="/{name}s", tags=["{name}s"])

@router.post("/", response_model={name.capitalize()}Out)
async def create_{name}(
    {name}_in: {name.capitalize()}In,
    db: Session = Depends(get_db)
):
    """Create new {name}"""
    service = {name.capitalize()}Service(db)
    return service.create({name}_in)

@router.get("/{{id}}", response_model={name.capitalize()}Out)
async def get_{name}(id: int, db: Session = Depends(get_db)):
    """Get {name} by ID"""
    service = {name.capitalize()}Service(db)
    {name} = service.get(id)
    if not {name}:
        raise HTTPException(status_code=404, detail="{name.capitalize()} not found")
    return {name}
'''

    os.makedirs(f"src/api/routers", exist_ok=True)
    with open(f"src/api/routers/{name}.py", "w") as f:
        f.write(template)

    print(f"✓ Created endpoint: src/api/routers/{name}.py")
```

**Optional Rule** (showing standard structure):
```markdown
# FastAPI Endpoint Structure

Standard endpoint structure:

1. Import dependencies
2. Create router with prefix and tags
3. Define endpoints using `@router` decorators
4. Use Pydantic models for request/response
5. Use dependency injection for DB session
6. Include error handling (HTTPException)

**Example**: See `src/api/routers/user.py`

**Scaffold**: Use `/scaffold-endpoint <name>` to generate template
```

**Result**: Tool for scaffolding, Rule for documentation (optional)

---

### Scenario 7: "All API endpoints must have rate limiting"

**Analysis**:
- Hard requirement? ✅ YES (security/performance)
- Deterministically validatable? ✅ YES (check for rate limit decorator)
- Nuanced judgment? ⚠️ SOME (rate limit value varies by endpoint)

**Decision**: **HYBRID** (Rule explains strategy, Tool validates presence)

**Rule Implementation**:
```markdown
# Security: Rate Limiting

All API endpoints MUST have rate limiting to prevent abuse.

**Strategy**:
- Public endpoints: 100 requests/minute/IP
- Authenticated endpoints: 1000 requests/minute/user
- Admin endpoints: No limit (trusted)

**Implementation**: Use `slowapi` library
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/public")
@limiter.limit("100/minute")
async def public_endpoint():
    ...
```

**Validation**: Run `.specify/scripts/validate-rate-limits.sh`
```

**Tool Implementation**:
```bash
#!/bin/bash
# Check all FastAPI routes have rate limiting

routes=$(grep -r '@router\.' src/api/routers/ | grep -v '@limiter.limit')

if [ -n "$routes" ]; then
  echo "ERROR: Routes without rate limiting:"
  echo "$routes"
  exit 1
fi

echo "✓ All routes have rate limiting"
exit 0
```

**Result**: Hybrid (Rule explains rate limit strategy, Tool ensures no route is missing decorator)

---

## Token Budget Considerations

### Calculating Token Impact

**Rule Token Cost**:
```
1 rule file = ~500 words average
             = ~667 tokens (0.75 words/token)

50 rule files = 33,350 tokens
```

**Tool Token Cost**:
```
1 tool definition = ~100 tokens
30 tools = 3,000 tokens (definitions only)

Tool execution results = ~200 tokens per call
5 tool calls = 1,000 tokens (results)

Total: 4,000 tokens
```

**Comparison**:
- 50 Rules: 33K tokens (always in context)
- 30 Tools: 4K tokens (definitions + results)
- **Tools save 88% of tokens**

### Dynamic Loading Strategy

**Problem**: 50 rules × 667 tokens = 33K tokens (16.5% of 200K window)

**Solution**: RAG-for-Rules (Just-in-Time loading)

**Implementation**:
1. Index all rules in vector DB (embeddings)
2. User asks question
3. Retrieve 5 most relevant rules (semantic search)
4. Load only those 5 into context (3,335 tokens)
5. **Savings**: 90% reduction (33K → 3.3K tokens)

**When to use**:
- Large rule sets (50+ rules)
- Limited context window (<200K tokens)
- Dynamic query patterns (can't predict which rules needed)

---

## Validation and Testing Matrix

| Type | Validation Method | Test Approach |
|------|-------------------|---------------|
| **Rule** | Manual review (AI behavior observation) | Ask AI questions, verify answers follow rule |
| **Tool** | Automated tests (unit, integration) | Test with known inputs, verify expected outputs |
| **Hybrid** | Both (rule review + tool tests) | Verify AI cites rule, then tool validates code |

### Testing Rules

**Challenge**: Rules are non-deterministic (AI might ignore)

**Approach**:
1. **Smoke Test**: Ask AI a question where rule applies
2. **Verify**: Check if response follows rule
3. **Iterate**: If AI ignores rule, make rule more explicit

**Example**:
```
Rule: "Use async/await for FastAPI endpoints"

Test:
User: "Create a GET endpoint for /users"
AI Response: ...should include `async def get_users(...)`...

✅ Pass: AI used async
❌ Fail: AI used sync → Revise rule
```

### Testing Tools

**Challenge**: Tools can fail (crashes, errors)

**Approach**:
1. **Unit Tests**: Test tool logic in isolation
2. **Integration Tests**: Test tool in context of AI workflow
3. **Error Handling Tests**: Verify graceful failure

**Example**:
```python
# test_validate_fastapi_di.py
def test_valid_endpoint():
    code = '''
    @router.get("/users/")
    async def get_users(db: Session = Depends(get_db)):
        ...
    '''
    result = validate_fastapi_di(code)
    assert result.passed == True

def test_missing_depends():
    code = '''
    @router.get("/users/")
    async def get_users(db: Session):  # Missing Depends
        ...
    '''
    result = validate_fastapi_di(code)
    assert result.passed == False
    assert "Missing Depends" in result.message
```

---

## Migration Strategy: Adding Rules/Tools to Existing Projects

### Phase 1: Inventory (Week 1)

1. **List all constraints**:
   - Coding standards (from style guides, wikis)
   - Architecture decisions (from ADRs)
   - Security requirements (from compliance docs)

2. **Categorize** each constraint:
   - Hard (security, compliance) → Tool candidates
   - Soft (style, naming) → Rule candidates
   - Medium (architecture) → Hybrid candidates

### Phase 2: Prioritize (Week 1)

**Criteria**:
- **Impact**: How often is this violated? (High impact = prioritize)
- **Cost**: How hard to implement? (Low cost = quick wins)
- **Risk**: What's the danger if ignored? (High risk = prioritize)

**Framework**:
```
Priority = (Impact × Risk) / Cost

High Priority: P ≥ 10
Medium Priority: 5 ≤ P < 10
Low Priority: P < 5
```

### Phase 3: Implement Quick Wins (Week 2-3)

**Quick Wins**: High Priority + Low Cost
- Example: "No API keys in code" → Secret scanner (tool) - 1 hour to implement

**Start with Rules**:
- Rules are faster to create (markdown files)
- Establish "AI personality" for project

**Then Add Tools**:
- For hard requirements identified in Phase 1

### Phase 4: Measure and Iterate (Ongoing)

**Metrics**:
- **Adherence Rate**: % of code following rule/passing tool
- **Detection Rate**: % of violations caught in review
- **False Positive Rate**: % of tool flags that are incorrect

**Iterate**:
- Rules with low adherence (< 60%) → Make more explicit or add tool
- Tools with high false positives (> 10%) → Refine validation logic

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Over-Reliance on Rules for Hard Requirements

**Problem**:
```markdown
# Rule: Never use eval()

Do not use `eval()` - it's insecure.
```

**Why It Fails**: AI might still suggest `eval()` under pressure or if user explicitly asks.

**Fix**: Add Tool (linter) to enforce:
```bash
if grep -r 'eval(' src/; then
  echo "ERROR: eval() found (security violation)"
  exit 1
fi
```

### ❌ Anti-Pattern 2: Verbose Rules That Should Be Tools

**Problem**:
```markdown
# Rule: Validate Pydantic Models

For every Pydantic model, ensure:
1. All fields have type annotations
2. At least one field has an example
3. The model has a Config class with orm_mode if ORM is used
4. If the model is for API response, it should have response_model_exclude_none
5. ... (50 more lines of conditionals)
```

**Why It Fails**: Too complex for AI to reliably follow. Better as deterministic code.

**Fix**: Create validation tool:
```python
def validate_pydantic_model(code: str) -> ValidationResult:
    # Parse AST
    # Check field annotations
    # Check examples
    # Check Config
    # Return structured result
```

### ❌ Anti-Pattern 3: Redundant Rules and Tools (Inconsistency)

**Problem**:
```
Rule: "Use camelCase for JavaScript"
ESLint Config: enforces snake_case
```

**Why It Fails**: Conflicting guidance confuses AI and developers.

**Fix**: **Align** rule with tool:
```markdown
# Rule: JavaScript Naming (Enforced by ESLint)

Use camelCase for variables and functions.

**Validation**: ESLint rule `camelcase` enforces this.
```

### ❌ Anti-Pattern 4: Tool Without Documentation (Black Box)

**Problem**: Tool exists, but no one knows when/why to use it.

**Fix**: Create companion rule:
```markdown
# Validation: Clean Architecture

To check architecture boundaries:
```bash
.specify/scripts/validate-clean-arch.sh
```

This ensures Data layer doesn't import from Presentation.
```

### ❌ Anti-Pattern 5: Context Bloat (Loading All Rules Always)

**Problem**: 100 rules loaded into every query, consuming 50K tokens.

**Why It Fails**: Costs $0.01/query, slows down inference.

**Fix**: Use dynamic loading (RAG-for-Rules) or globs to target specific files.

---

## Checklist: Before Implementing

Before creating a rule or tool, ask:

### Rules Checklist

- [ ] Is this guidance (not enforcement)?
- [ ] Can I explain this in < 500 words?
- [ ] Does this require contextual judgment (not binary check)?
- [ ] Will this help AI generate better code (not just lint it)?
- [ ] Is the token budget available (< 20% of window)?
- [ ] Have I provided examples (Do This / Don't Do This)?
- [ ] Is this stored in version control (team shares it)?

### Tools Checklist

- [ ] Does this require external data OR deterministic validation?
- [ ] Is this a hard requirement (cannot be violated)?
- [ ] Can I write a test for this tool?
- [ ] Will this tool fail gracefully (clear error messages)?
- [ ] Is the latency acceptable (< 5 seconds)?
- [ ] Have I documented when/how to use this tool?
- [ ] Is this sandboxed (no dangerous side effects)?

### Hybrid Checklist

- [ ] Is the rule explaining "why" (philosophy)?
- [ ] Is the tool enforcing "what" (validation)?
- [ ] Do they reference each other (rule mentions tool, tool links to rule)?
- [ ] Is this a pattern (not a one-off constraint)?
- [ ] Will this reduce manual code review burden?

---

## Conclusion

**The Golden Rule**:
> "If you can't enforce it, make it a Rule. If you must enforce it, make it a Tool. If you should explain AND enforce it, make it Hybrid."

**Decision Flow**:
1. Start with the Decision Tree (Step 1-6)
2. Apply Heuristic Rules for quick judgment
3. Validate with Token Budget considerations
4. Test the decision with Real-World Scenarios
5. Avoid Anti-Patterns
6. Use Checklists before implementation

**For RaiSE Framework**:
- Build both `raise.rules.generate` (for Rules) and `raise.skills.generate` (for Tools)
- Default to **Hybrid** for architectural patterns (philosophy + validation)
- Optimize with **dynamic loading** to manage token budgets

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-23
**Maintained By**: RaiSE Research Team
