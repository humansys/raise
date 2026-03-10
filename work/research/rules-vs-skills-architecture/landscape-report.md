# Rules vs. Skills: Architecture Guide 2026

**Research ID**: RES-ARCH-COMPARE-RULES-SKILLS-001
**Date**: 2026-01-23
**Author**: RaiSE Research Team
**Version**: 1.0.0

---

## Executive Summary

The landscape of agentic code generation in 2026 is characterized by a critical architectural choice: **Rules (Context)** vs **Skills (Tools)**. This research reveals that these are not competing approaches but complementary mechanisms that serve distinct purposes in the AI engineering stack.

**Key Findings:**

1. **The Shift**: The industry is moving from "context stuffing" (injecting all knowledge into prompts) to "tool execution" (enabling AI to call external functions), but context remains essential for nuance and style.

2. **The Hybrid Reality**: 97M+ monthly MCP SDK downloads and 85% of enterprises implementing AI agents by 2025 signal that the future is **hybrid architecture** - combining rules for "soft" constraints with tools for "hard" enforcement.

3. **The Economics**: Context windows incur a "silent tax" - every token costs money and increases latency. At $0.19-$0.49 per 1M tokens, a 10M token query costs $2-$5. Tools reduce token overhead by 85% through dynamic loading but add round-trip latency.

4. **The Pattern**: "Rules define philosophy; Tools enforce correctness." Rules excel at communicating architectural principles, naming conventions, and stylistic preferences. Tools excel at deterministic validation, external data access, and executable verification.

5. **For RaiSE**: The framework should generate **both** - Rules (`.mdc` files) for guiding AI behavior AND Skills (MCP servers, validation scripts) for enforcing quality gates. The choice depends on whether the requirement is suggestive or mandatory.

---

## 1. The Rules (Context) Paradigm

### 1.1 What Are Rules?

Rules are **passive context injections** - text-based guidelines that augment the AI's system prompt to shape its behavior. In Cursor, they're `.mdc` files in `.cursor/rules/`. In Claude Code, they're CLAUDE.md files or custom instructions. In Copilot, they're workspace instructions.

**Mechanism:**
```
User Query → AI Model loads relevant rules → Rules injected into context → Model generates response considering rules
```

Rules work by increasing the **attention** the model pays to certain patterns or constraints. They rely on the model's ability to:
- Parse natural language instructions
- Understand implicit context
- Apply judgment about when rules apply
- Balance conflicting guidance

### 1.2 Strengths: Where Rules Excel

#### Nuance and Style
Rules can communicate **soft constraints** that don't have binary enforcement:
- "Prefer functional programming over imperative when possible"
- "Use descriptive variable names that explain intent"
- "Follow the repository pattern for database access"
- "Maintain a conversational tone in API documentation"

These are judgment calls that an AI can learn to apply contextually, but a linter cannot enforce.

#### Architectural Philosophy
Rules excel at conveying the **"why"** behind decisions:
```markdown
## Architecture Principle: Dependency Injection

We use FastAPI's `Depends()` for shared services (database sessions,
authentication) instead of global variables.

**Rationale**: This enables:
- Easy testing (mock dependencies)
- Clear contracts (function signatures declare needs)
- Lifecycle management (sessions auto-close)

**Example:**
```python
@router.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```
```

The AI doesn't just learn the pattern - it learns the reasoning, enabling it to apply the principle to new situations.

#### Rapid Iteration
Creating a rule is as simple as writing markdown:
1. Create `.cursor/rules/fastapi.mdc`
2. Write guidelines in plain language
3. Commit to Git
4. Team instantly benefits

No schema definitions, no handler code, no testing infrastructure. **Authoring friction: minimal.**

#### Domain-Specific Guidance
Rules can reference project-specific context:
- "Use the `OrderProcessor` class for all e-commerce transactions"
- "Follow the naming convention established in `src/core/models/`"
- "Refer to `@docs/ARCHITECTURE.md` for system design"

The AI can pull in these references dynamically when needed.

### 1.3 Weaknesses: Where Rules Break Down

#### Context Window Saturation
Every rule consumes tokens. Loading 58 tools as text consumes ~55k tokens. For large projects:
- 100+ rules = context window overflow
- Critical rules might get truncated
- Token costs multiply: $2-$5 per 10M token query

**Solution from industry**: Dynamic loading (Tool Search) reduces overhead by 85%, but this isn't available for pure text rules.

#### "I Forgot" Hallucinations
The AI model doesn't have perfect attention. Even with rules in context:
- The model might overlook a rule if it's buried in 50 others
- Contradictory rules create confusion
- Vague rules ("use best practices") are ignored

Anthropic's research shows that **clarity and specificity** matter more than quantity.

#### Non-Deterministic Adherence
Rules are **suggestions**, not guarantees. The model can:
- Misinterpret a rule
- Apply a rule incorrectly
- Ignore a rule if it conflicts with the user's explicit request

For **hard requirements** (security, compliance), rules alone are insufficient.

#### Conflicting Instructions
When rules contradict:
```markdown
# Rule 1: "Never use `eval()`"
# Rule 2: "For dynamic expressions, use `eval()` with sanitization"
```

The AI must make a judgment call, potentially choosing wrong. Traditional linters would flag this conflict deterministically.

### 1.4 Best Practices for Rules

From community analysis (Cursor forums, Anthropic best practices):

1. **Keep rules focused**: One theme per file (FastAPI, Pydantic, Testing)
2. **Use globs precisely**: Target specific files, not `**/*.py`
3. **Provide examples**: Show "Do This" and "Don't Do This" code
4. **State rationale**: Explain the "why" in 1-2 sentences
5. **Reference, don't duplicate**: Use `@filename.md` to pull in docs
6. **Prioritize rules**: Mark critical rules with `alwaysApply: true`
7. **Version control**: Treat rules as code - review changes in PRs

**Token budget discipline**: If rules exceed 20% of context window, refactor or split.

---

## 2. The Skills (Tools/MCP) Paradigm

### 2.1 What Are Skills/Tools?

Skills are **active executable functions** that the AI can invoke to perform actions or retrieve data. In Model Context Protocol (MCP), skills manifest as:
- **Tools**: Functions the AI can call (write files, query APIs, run linters)
- **Resources**: Data sources the AI can read (database schemas, docs)
- **Prompts**: Reusable templates for common tasks

**Mechanism:**
```
User Query → AI determines tool needed → AI calls tool with arguments → Tool executes → Result returned to AI → AI incorporates result into response
```

Tools work through **function calling** - the AI doesn't just suggest code, it *executes* code.

### 2.2 Strengths: Where Tools Excel

#### Deterministic Actions
Tools provide **guaranteed execution**:
- A linter tool *will* catch syntax errors (no probabilistic failure)
- A database query *will* return actual data (no hallucination)
- A file write *will* persist the file (no "I forgot")

**Example**: Instead of asking the AI to "check if this follows the repository pattern," a tool *runs* the validation and returns pass/fail.

#### Accessing External Data
The AI cannot hallucinate data it doesn't have. Tools bridge this gap:
- Fetch live documentation from APIs
- Query database schemas
- Retrieve Jira tickets for context
- Pull latest library versions from npm/pip

**Sourcegraph Cody** leverages this via OpenCtx - connecting to Jira, Linear, Notion to fetch context the AI can't fabricate.

#### Rigorous Testing and Verification
Tools enable **test-driven constraints**:
```python
# MCP Tool: validate_fastapi_endpoint
def validate_endpoint(code: str) -> ValidationResult:
    # Parse AST
    # Check for Pydantic models
    # Verify dependency injection
    # Ensure async/await usage
    return ValidationResult(passed=True, violations=[])
```

The AI can call this tool after generating code to verify correctness.

#### Scaffolding and Code Generation
Tools can generate boilerplate deterministically:
- "Create FastAPI endpoint with CRUD operations"
- Tool scaffolds: router file, Pydantic models, database models, tests

Unlike the AI guessing the structure, the tool applies a **proven template**.

### 2.3 Weaknesses: Where Tools Break Down

#### High Build Cost
Creating a tool requires:
1. **Schema definition** (JSON for MCP)
2. **Handler implementation** (Python, TypeScript, etc.)
3. **Error handling** (what if arguments are invalid?)
4. **Testing** (unit tests, integration tests)
5. **Documentation** (how to use the tool)

**Authoring friction: high.** Simple rules (30 lines of markdown) become 200 lines of code.

#### Token Overhead
Ironically, tools consume significant tokens via their **definitions**:
- 58 tools = ~55k tokens of definitions
- Must load definitions into context so AI knows they exist

**Solution**: Dynamic tool loading (Tool Search) reduces this by 85%, but adds complexity.

#### Latency and Round-Trips
Every tool call is a **round-trip**:
```
AI generates response → Identifies tool needed → Calls tool → Waits for result → Continues generating
```

Multiple tool calls compound latency. Anthropic notes that batching 32 requests reduces cost by 85% but increases latency by 20%.

#### "Black Box" Opacity
When the AI calls a tool, the user might not understand why:
- "Claude ran `validate_schema` but I don't know what that checked"
- Debugging requires understanding both the AI's reasoning AND the tool's logic

**Rules are transparent** - a developer can read `.mdc` files. Tools require code inspection.

#### Reliability Issues
As Armin Ronacher notes: "MCP servers themselves are sometimes not super reliable and they are an extra thing that can go wrong."

Tools depend on:
- External APIs (can be down)
- Network connectivity (can fail)
- Execution environments (can crash)

### 2.4 Best Practices for Tools

From Anthropic's Claude Code best practices and community insights:

1. **Tools must be fast**: <5 seconds ideal. Hangs are worse than crashes.
2. **Clear error messages**: "Invalid argument: X must be a string" not "Error 500"
3. **Sandboxing**: Prevent AI from dangerous actions (deleting files, network access)
4. **Rate limiting**: Avoid infinite loops (AI calling same tool 100x)
5. **Fallback behavior**: If tool fails, AI should gracefully continue
6. **Only MCP when necessary**: Regular shell scripts work fine for many cases
7. **Dynamic loading**: Use Tool Search for 30+ tools to avoid context bloat

**Token budget for tools**: Keep definitions under 10% of context window via dynamic loading.

---

## 3. Comparative Matrix

| Feature | Rules (.mdc, CLAUDE.md) | Skills (MCP Tools) |
|---------|-------------------------|---------------------|
| **Enforcement** | Probabilistic (Suggestion) | Deterministic (Execution) |
| **Token Cost** | High (Always in context) | Medium (Definitions + Results) |
| **Authoring Cost** | Low (Markdown) | High (Code + Schema + Tests) |
| **Latency** | Low (Zero-shot generation) | Medium (Round-trips per tool call) |
| **Reliability** | Non-deterministic (model attention) | Deterministic (but tools can fail) |
| **External Data** | Cannot access (hallucination risk) | Can fetch live data |
| **Complexity** | Low (text files) | High (code infrastructure) |
| **Transparency** | High (readable markdown) | Medium (requires code inspection) |
| **Maintenance** | Low (edit text) | Medium (code updates, version deps) |
| **Security** | Safe (passive) | Risk (active execution) |
| **Versioning** | Git (simple) | Git + dependency management |
| **Best For** | Philosophy, style, nuance, examples | Validation, data fetching, scaffolding |
| **Failure Mode** | AI ignores rule | Tool crashes or returns error |
| **Scale** | 100+ rules = context issues | 30+ tools = need dynamic loading |

---

## 4. Case Studies: Industry Implementations

### 4.1 Cursor: Hybrid Rules + MCP

**Rules Implementation:**
- `.cursor/rules/*.mdc` files with YAML frontmatter
- Globs for file targeting (e.g., `globs: ["src/api/**/*.py"]`)
- Four attachment modes: Always, Auto-Attached, Agent-Requested, Manual
- Community shares 879+ rule files via GitHub

**MCP Integration:**
- Cursor connects to MCP servers via `~/.cursor/mcp.json`
- Tools available to Composer Agent if "relevant" (AI decides)
- Resources NOT yet supported (tools only)
- OAuth for authenticated MCP servers

**Hybrid Pattern:**
```
User opens FastAPI file
→ Cursor loads fastapi.mdc rule (context)
→ User asks "Create endpoint"
→ AI generates code following rule
→ User asks "Validate this"
→ AI calls MCP validation tool
→ Tool returns pass/fail
→ AI suggests fixes based on tool output
```

**Insight**: Cursor uses **rules for generation guidance** and **tools for verification**.

### 4.2 Claude Code: Tools-First, Context-Aware

**Tools Implementation:**
- Native tool use via function calling
- MCP servers for external integrations
- Dynamic tool loading (Tool Search) reduces overhead 85%
- Experimental MCP CLI mode

**Context Implementation:**
- CLAUDE.md files for project instructions
- `@filename` references to pull in docs on-demand
- `/clear` command to reset context when bloated

**Hybrid Pattern:**
```
Claude reads CLAUDE.md (rules for project)
→ User asks "Add feature X"
→ Claude calls grep tool (find related code)
→ Claude calls read tool (load files)
→ Claude generates code following CLAUDE.md principles
→ Claude calls linter tool (validate)
→ Claude reports results
```

**Insight**: Claude Code uses **rules for context** and **tools for capabilities**.

### 4.3 Replit Agent: Limited Context, Strong Tools

**Context Limitations:**
- Limited context window tied to Agent capacity
- Struggles with large existing codebases
- Works best for new projects with common patterns

**Tools Implementation:**
- MCP for connecting to code repositories and documentation
- Tools for code generation, debugging, environment management

**Hybrid Pattern:**
```
User: "Create Python web app"
→ Replit generates scaffold (tool)
→ User: "Add database"
→ Replit infers pattern (limited context) + uses database tool
```

**Insight**: Replit compensates for limited context with **strong tool execution**.

### 4.4 Sourcegraph Cody: Context as Competitive Edge

**Context Strength:**
- Deep codebase understanding via Sourcegraph's search engine
- Extends beyond immediate files to project-wide context
- OpenCtx for non-code sources (Jira, Linear, Notion, Google Docs)

**Tools Implementation:**
- Custom and pre-built commands (generate tests, fix code, optimize)
- Integration with external systems via OpenCtx

**Hybrid Pattern:**
```
User in file X
→ Cody understands X's role in project architecture (context)
→ User asks "Generate test"
→ Cody uses test generation command (tool)
→ Test reflects project patterns (context-aware tool)
```

**Insight**: Cody's advantage is **context breadth** - tools are context-informed.

### 4.5 Emerging Pattern: Agentic RAG

**Traditional RAG** (Retrieval-Augmented Generation):
- Query → Retrieve documents → Generate answer
- Static, one-shot retrieval

**Agentic RAG** (2026 trend):
- Query → Agent decides which retrieval tool to use → Retrieves → Evaluates → Iteratively refines
- Dynamic, multi-step retrieval

**Rules vs Tools in Agentic RAG:**
- **Rules**: Define which knowledge sources are authoritative
- **Tools**: Retrieve from those sources dynamically

**Example**:
```
Rule: "For architecture decisions, reference docs/adrs/"
Tool: rag_retrieve(source="docs/adrs/", query="authentication")
→ AI reads ADR-005-oauth2-implementation.md
→ AI generates code following that decision
```

**Insight**: Agentic RAG treats **retrieval as a tool** and **source priority as a rule**.

---

## 5. The Hybrid Future: Convergence Patterns

### 5.1 Jit (Just-in-Time) Context

**Problem**: Loading all rules consumes tokens. Loading all tools costs latency.

**Solution**: Retrieve context/tools **only when needed**.

**Implementation (Rules)**:
```markdown
# Rule: Architecture Overview
Do not load this rule always. Load on-demand when user asks:
- "What's the system architecture?"
- "How do services communicate?"
```

The AI uses the rule's description to decide when to fetch it.

**Implementation (Tools)**:
```python
# MCP Tool Definition
{
  "name": "validate_repository_pattern",
  "defer_loading": true  # Don't load definition until called
}
```

Dynamic tool loading via Tool Search: AI fetches tool definition when relevant.

**Result**: 85% token reduction, context stays focused.

### 5.2 Active Context (Executable Rules)

**Concept**: Rules that contain executable components.

**Example**:
```markdown
# Rule: Python Code Must Pass Black Formatter

**Verification Script**:
```bash
black --check $FILE || exit 1
```

**Enforcement**:
- Pre-commit hook runs script
- AI can call script as tool to verify generated code
```

**Pattern**:
- Rule = Philosophy ("Use Black for formatting")
- Tool = Enforcement (actual Black execution)
- They reference each other: Rule says "see tool X for validation"

### 5.3 RAG-for-Rules

**Problem**: 100+ rules in project. AI can't attend to all.

**Solution**: Treat rules as documents in a RAG system.

**Implementation**:
```
User asks: "How do I structure a FastAPI endpoint?"
→ AI queries rule index (vector DB of rule embeddings)
→ Retrieves: fastapi.mdc, pydantic.mdc, testing.mdc
→ Loads ONLY those 3 rules into context
→ Generates answer
```

**Result**: Context window stays lean, relevant rules always present.

### 5.4 Policy-to-Tests (P2T) Framework

**Concept**: Translate natural-language policies into executable rules.

**From research** (arXiv:2512.04408 - Executable Governance for AI):
- Pipeline reads policy documents
- Extracts rules using LLMs and deterministic checks
- Generates DSL-encoded rules (hazards, conditions, exceptions)
- Creates runtime guardrails (NeMo Guardrails, Guardrails AI)

**Application to RaiSE**:
```
Input: CLAUDE.md (natural language rules)
→ P2T pipeline extracts constraints
→ Generates:
  - .mdc files (AI guidance)
  - linter configs (ESLint, Pylint)
  - test cases (pytest, jest)
→ All enforce same policy
```

**Result**: **Single source of truth** (policy doc) generates both rules and tools.

### 5.5 Multi-Agent Architectures

**Trend (2026)**: Multiple agents collaborate, each with specialized tools/rules.

**Pattern**:
```
Agent 1: Code Generator
- Rules: Coding style, architecture patterns
- Tools: Scaffolding, template generation

Agent 2: Reviewer
- Rules: Code review checklist
- Tools: Linters, security scanners, test runners

Agent 3: Documenter
- Rules: Documentation standards
- Tools: Doc generators, diagram tools
```

**Coordination**:
- Agent 1 generates code → passes to Agent 2
- Agent 2 validates → returns feedback → Agent 1 refines
- Agent 3 documents final result

**Rules vs Tools**: Each agent has **local rules** (its specialty) and **shared tools** (common infrastructure).

---

## 6. Context Window Economics

### 6.1 The Token Budget Reality

**Cost Structure (2026 pricing)**:
- Claude Opus 4.5: ~$0.19-$0.49 per 1M tokens
- 10M token query: $2-$5 per request

**Context Window Sizes**:
- Claude 4: 200K tokens
- Gemini 2.5 Pro: 2M tokens
- Magic LTM-2-Mini: 100M tokens

**Trade-off**:
```
Wider context window = More capabilities
                      = More cost per query
                      = More latency (TTFT in minutes for 10M tokens)
```

### 6.2 Rules vs Tools: Token Math

**Scenario**: 50 coding rules, 30 validation tools

**Rules Approach (All in Context)**:
- 50 rules × 500 words average = 25,000 words
- ~33,000 tokens (1 token ≈ 0.75 words)
- Cost: $0.006-$0.016 per query
- Latency: Increased TTFT (more tokens to process)

**Tools Approach (Dynamic Loading)**:
- Tool definitions: 30 tools × 100 tokens = 3,000 tokens
- Actual tool calls: 5 calls × 200 tokens result = 1,000 tokens
- Total: 4,000 tokens
- Cost: $0.0008-$0.002 per query
- Latency: Round-trip per tool call (~200-500ms each)

**Hybrid Approach (Jit Context + Dynamic Tools)**:
- Load 5 relevant rules: 5 × 500 tokens = 2,500 tokens
- Load 3 relevant tools: 3 × 100 = 300 tokens
- Tool results: 3 × 200 = 600 tokens
- Total: 3,400 tokens
- Cost: $0.0006-$0.0017 per query

**Winner**: Hybrid approach - **83% cheaper** than all-rules, **comparable latency** to tools-only.

### 6.3 Batching Economics

**From Anthropic research**:
- Batching 32 requests: 85% cost reduction, 20% latency increase

**Application**:
- Batch-validate 32 files with tool calls: Cost drops dramatically
- Trade-off: User waits 20% longer for results

**When to batch**:
- Nightly CI runs (latency acceptable)
- Large refactorings (processing many files)

**When not to batch**:
- Interactive coding (latency critical)
- Single-file edits (no batch opportunity)

---

## 7. Decision Framework: Rule or Tool?

### 7.1 The Fundamental Question

**"Is this a preference or a requirement?"**

- **Preference** → Rule (suggestive)
- **Requirement** → Tool (enforced)

### 7.2 Decision Tree

```
┌─ Does this require external data? (API, DB, filesystem)
│  └─ YES → Tool (AI cannot access without it)
│  └─ NO → Continue
│
├─ Is this a hard requirement? (security, compliance, correctness)
│  └─ YES → Tool (cannot trust AI to always comply)
│  └─ NO → Continue
│
├─ Can this be validated via deterministic logic? (linter, regex, AST)
│  └─ YES → Hybrid (Rule explains why, Tool validates)
│  └─ NO → Continue
│
├─ Is this complex branching logic? (100+ lines of rules)
│  └─ YES → Tool (code is clearer than prose)
│  └─ NO → Continue
│
├─ Is this nuanced judgment? (style, naming, architecture philosophy)
│  └─ YES → Rule (AI excels at contextual judgment)
│  └─ NO → Continue
│
└─ Is this a code template? (scaffolding, boilerplate)
   └─ YES → Tool (consistent scaffold)
   └─ NO → Rule (guidance is sufficient)
```

### 7.3 Heuristics

**Use Rules When:**
- Explaining architectural principles
- Defining naming conventions
- Establishing code style preferences
- Providing examples and anti-patterns
- Communicating domain context
- Suggesting best practices
- Token budget allows (< 20% of window)

**Use Tools When:**
- Fetching live documentation or data
- Running linters or validators
- Querying databases or APIs
- Generating boilerplate from templates
- Enforcing security or compliance rules
- Verifying correctness deterministically
- Accessing external systems

**Use Hybrid When:**
- Rule explains the "why" (philosophy)
- Tool enforces the "what" (validation)
- Example: "Use repository pattern (rule) → validate with tool"

### 7.4 Examples

| Scenario | Approach | Rationale |
|----------|----------|-----------|
| "Never commit API keys" | **Tool** | Security requirement → linter scans for keys |
| "Prefer descriptive variable names" | **Rule** | Style preference → AI judges contextually |
| "Use FastAPI dependency injection" | **Hybrid** | Rule explains pattern, tool validates usage |
| "Fetch latest library versions" | **Tool** | Requires external data (npm, pip) |
| "Follow clean architecture layers" | **Rule** | Architectural philosophy, not binary |
| "Run tests before committing" | **Tool** | Hard requirement → pre-commit hook |
| "Write docstrings for public functions" | **Rule** | Best practice, not enforced strictly |
| "Scaffold new API endpoint" | **Tool** | Template generation (deterministic) |
| "Avoid tight coupling" | **Rule** | Design principle (nuanced judgment) |
| "Validate Pydantic models exist" | **Tool** | AST analysis (deterministic check) |

---

## 8. Recommendations for RaiSE Framework

### 8.1 Core Principle

**Generate BOTH rules and tools, choosing based on requirement type.**

### 8.2 Proposed Architecture

```
raise.rules.generate → Creates .mdc files (AI guidance)
raise.skills.generate → Creates MCP servers + validation scripts (enforcement)
raise.hybrid.generate → Creates rule + tool pair (philosophy + validation)
```

### 8.3 When to Generate What

**For Brownfield Analysis**:
```
raise.1.analyze.code
→ Identifies patterns
→ For each pattern:
   • If soft (style, naming) → raise.rules.generate
   • If hard (architecture, security) → raise.hybrid.generate
```

**For Greenfield Setup**:
```
raise.2.vision
→ Defines architecture decisions
→ For each decision:
   • Philosophy → rule
   • Validation → tool
```

### 8.4 Specific Recommendations

**1. Extend raise.rules.generate**:
- Add option: `--with-validation` to generate tool alongside rule
- Template: Rule explains pattern, tool validates it
- Example: Repository pattern rule + AST validation script

**2. Create raise.skills.generate**:
- Input: Specification (JSON or YAML)
- Output:
  - MCP server (TypeScript or Python)
  - Handler implementations
  - JSON schema for tool definitions
  - Tests (pytest or jest)
  - Documentation

**3. Implement Hybrid Templates**:
```markdown
# Rule: Repository Pattern

**Purpose**: Isolate data access logic...

**Verification**: Run `.specify/scripts/validate-repository-pattern.sh`
```

Tool script:
```bash
#!/bin/bash
# validate-repository-pattern.sh
# Checks if repository pattern is correctly implemented
```

**4. Dynamic Context Loading**:
- Implement RAG-for-Rules: Index rules in vector DB
- Retrieve only relevant rules per query
- Reduces token overhead 70-85%

**5. Token Budget Guidelines**:
- Rules: < 20% of context window
- Tools: < 10% of context window (definitions only)
- Reserve 70% for actual code and conversation

### 8.5 Migration Path

**Phase 1: Rules Foundation** (Current State)
- `raise.rules.generate` creates .mdc files
- Focus: Patterns, conventions, examples

**Phase 2: Tools Introduction** (Next 3 months)
- `raise.skills.generate` scaffolds MCP servers
- Focus: Validation, data fetching, scaffolding

**Phase 3: Hybrid Integration** (Next 6 months)
- `raise.hybrid.generate` creates rule + tool pairs
- Focus: Aligned philosophy and enforcement

**Phase 4: Dynamic Optimization** (Next 12 months)
- RAG-for-Rules implementation
- Dynamic tool loading integration
- Token budget optimization

---

## 9. Industry Trends and Future Outlook

### 9.1 MCP Adoption Trajectory

**2024-2025**:
- MCP announced (Nov 2024)
- Downloads grew 100K → 8M (6 months)
- 5,800+ servers, 300+ clients

**2026 (Projected)**:
- 75% of API gateway vendors support MCP
- 50% of iPaaS vendors support MCP
- 40% of enterprise apps include AI agents
- $10.3B market size (34.6% CAGR)

**Takeaway**: MCP is becoming the **de facto standard** for agent-tool integration.

### 9.2 The Multi-Agent Future

By 2026, **multi-agent collaboration** becomes standard:
- Multiple specialized agents (code generator, reviewer, documenter)
- Each agent has local rules + shared tools
- Coordination via message passing (Agent-to-Agent protocol)

**Implication for RaiSE**: Design tools to be **agent-neutral** - any agent can use them.

### 9.3 The Death of RAG? Context Engineering

Article: "Is RAG Dead? The Rise of Context Engineering" (Towards Data Science)

**Thesis**: As context windows grow (100M+ tokens), retrieval becomes less critical. Just load everything.

**Counter-thesis**: Context window economics make this prohibitively expensive. RAG evolves into **Agentic RAG**.

**Outcome**: Hybrid approach wins - use retrieval to minimize context, but load more when justified.

### 9.4 Security and Compliance

**Challenge**: 85% of enterprises deploy agents, but regulatory frameworks lag.

**Prediction**: By 2026, 50%+ of enterprises use third-party services for AI guardrails.

**Tools for RaiSE**:
- Generate compliance validation tools
- Integrate with guardrail frameworks (NeMo, Guardrails AI)
- Policy-to-Tests pipeline for automated rule enforcement

### 9.5 The Context Window Wars

**Current (2026)**:
- Average context: 500K tokens (10x from 2023)
- Leaders: Magic (100M), Gemini (2M), Claude (200K)

**Trend**: Context windows grow, but **costs don't scale linearly**.

**Economics**: Wider windows enable new use cases, but token discipline remains critical.

---

## 10. Conclusion

The Rules vs. Skills debate is a false dichotomy. The future is **convergence**:

1. **Rules for Philosophy**: Use markdown files to communicate principles, examples, and nuance. Perfect for style, architecture philosophy, and domain context.

2. **Tools for Enforcement**: Use executable functions for validation, data access, and scaffolding. Perfect for hard requirements and external integrations.

3. **Hybrid for Quality**: Pair rules (explain the "why") with tools (enforce the "what"). Example: Repository pattern rule + AST validation script.

4. **Dynamic Loading**: Use RAG-for-Rules and Tool Search to minimize token overhead while maximizing capability.

5. **Token Economics Matter**: At $2-$5 per 10M token query, context discipline is a competitive advantage. Hybrid approaches reduce costs 80%+ while maintaining capability.

**For RaiSE**, the path forward is clear:
- **Extend** `raise.rules.generate` for context creation
- **Create** `raise.skills.generate` for tool scaffolding
- **Integrate** both into `raise.hybrid.generate` for aligned philosophy + enforcement
- **Optimize** via dynamic loading and RAG-for-Rules

The goal: **Enable RaiSE to build agents that not only know the guidelines but can enforce them agentically.**

---

## Sources

### Official Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Anthropic MCP Introduction](https://www.anthropic.com/news/model-context-protocol)
- [Cursor MCP Documentation](https://cursor.com/docs/context/mcp)
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

### Research Papers
- [Executable Governance for AI (arXiv:2512.04408)](https://arxiv.org/abs/2512.04408)

### Industry Analysis
- [A Year of MCP - Pento](https://www.pento.ai/blog/a-year-of-mcp-2025-review)
- [Why Model Context Protocol Won - The New Stack](https://thenewstack.io/why-the-model-context-protocol-won/)
- [2026: Year for Enterprise MCP Adoption - CData](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- [MCP Adoption Statistics 2025 - MCP Manager](https://mcpmanager.ai/blog/mcp-adoption-statistics/)

### Technical Guides
- [MCP Resources vs Tools vs Prompts - Medium](https://medium.com/@laurentkubaski/mcp-resources-explained-and-how-they-differ-from-mcp-tools-096f9d15f767)
- [Agent Skills vs Rules vs Commands - Builder.io](https://www.builder.io/blog/agent-skills-rules-commands)
- [Agentic Coding Best Practices - Armin Ronacher](https://lucumr.pocoo.org/2025/6/12/agentic-coding/)
- [Traditional RAG vs Agentic RAG - NVIDIA](https://developer.nvidia.com/blog/traditional-rag-vs-agentic-rag-why-ai-agents-need-dynamic-knowledge-to-get-smarter/)

### Community Resources
- [Cursor Rules Deep Dive - Community Forum](https://forum.cursor.com/t/a-deep-dive-into-cursor-rules-0-45/60721)
- [How to Write Great Cursor Rules - Trigger.dev](https://trigger.dev/blog/cursor-rules)
- [Mastering Cursor Rules - DEV Community](https://dev.to/dpaluy/mastering-cursor-rules-a-developers-guide-to-smart-ai-integration-1k65)

### Cost and Economics
- [Hidden Costs of Context Windows - Brim Labs](https://brimlabs.ai/blog/the-hidden-costs-of-context-windows-optimizing-token-budgets-for-scalable-ai-products/)
- [LLM Pricing Comparison 2026](https://pricepertoken.com/)

### Architecture and Patterns
- [Agentic AI Architecture - Exabeam](https://www.exabeam.com/explainers/agentic-ai/agentic-ai-architecture-types-components-best-practices/)
- [Multi-Agent Architectures - Medium](https://medium.com/@iamanraghuvanshi/agentic-ai-7-multi-agent-architectures-explained-how-ai-agents-collaborate-141c23e9117f)

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-23
**Maintained By**: RaiSE Research Team
