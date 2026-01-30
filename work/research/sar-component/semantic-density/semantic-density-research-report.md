# Research Report: Modelo de Representacion de Reglas Semanticamente Densas

**Research ID**: RES-SAR-REPR-001
**Fecha**: 2026-01-28
**Investigador**: Claude Opus 4.5 (asistido)
**Solicitante**: Emilio (RaiSE Framework)
**Version**: 1.0.0

---

## Executive Summary

Este research investiga el prior art para definir el formato optimo de representacion de reglas extraidas por SAR (Static Analysis for Rules) que sean semanticamente densas, validables, y consumibles por agentes LLM via RAG.

### Hallazgos Clave

1. **No existe formato universal optimo**: La efectividad del formato depende del modelo LLM y la tarea. YAML y Markdown emergen como los formatos con mejor balance densidad/comprension.

2. **Campos universales identificados**: Analisis de 8+ formatos revela convergencia en campos core: `id`, `severity`, `message/description`, `pattern`, `examples`, `metadata`.

3. **Chunk size optimo para reglas**: 256-512 tokens para contenido tecnico, con 10-20% overlap. Las reglas deben ser self-contained.

4. **Ejecutabilidad es diferenciador clave**: Formatos como Semgrep y ast-grep que incluyen queries ejecutables superan a formatos puramente descriptivos.

5. **Metadatos para RAG filtering son criticos**: `category`, `tags`, `applies_to`, `language` son esenciales para precision en retrieval.

---

## Prior Art Analysis por Dominio

### Dominio 1: Formatos de Representacion de Conocimiento para LLMs (P0)

#### 1.1 Instruction Tuning Formats

**Alpaca Format**
- **Descripcion**: Formato flat JSON para pares instruction-response
- **Campos**: `instruction`, `input`, `output`, `text`
- **Fortalezas**: Simple, ampliamente adoptado, bueno para single-turn
- **Debilidades**: No soporta multi-turn, sin estructura para ejemplos
- **Adopcion**: Stanford Alpaca, miles de fine-tunes derivados
- **Aplicabilidad a SAR**: BAJA - demasiado simple para reglas complejas

**ShareGPT Format**
- **Descripcion**: Formato nested para conversaciones multi-turn
- **Campos**: `conversations[]` con `from`/`value`, soporta `function_call`, `tools`
- **Fortalezas**: Multi-turn, function calling, flexible
- **Debilidades**: Mas complejo de parsear, overhead en tokens
- **Adopcion**: OpenAI, Hugging Face defaults, LlamaFactory
- **Aplicabilidad a SAR**: MEDIA - util para reglas con contexto conversacional

**OpenAI Function Calling Schema**
- **Descripcion**: JSON Schema para definir herramientas/funciones
- **Campos**: `name`, `description`, `parameters` (JSON Schema)
- **Fortalezas**: Structured outputs, validation built-in
- **Debilidades**: Verboso, no optimizado para reglas estaticas
- **Adopcion**: OpenAI API, Anthropic tool_use, industry standard
- **Aplicabilidad a SAR**: MEDIA - modelo util para especificar contratos

**Confidence**: HIGH (Tier 1-2 sources: official documentation, peer-reviewed papers)

#### 1.2 Format Comprehension Research

| Formato | GPT-3.5 Performance | GPT-4 Performance | Token Efficiency | Best For |
|---------|---------------------|-------------------|------------------|----------|
| JSON | 59.7% accuracy | 73.9% accuracy | Baseline | Structured data |
| Markdown | 50.0% accuracy | 81.2% accuracy | -15% vs JSON | Readable docs |
| YAML | Variable | Best overall | -10% vs JSON | Config, rules |
| XML | Lower | Comparable | +80% vs Markdown | Legacy systems |

**Key Finding**: Larger models are more format-robust. YAML recomendado como default para accuracy; Markdown si cost es prioridad.

**Sources**:
- [arXiv:2411.10541 - Does Prompt Formatting Have Any Impact on LLM Performance?](https://arxiv.org/html/2411.10541v1)
- [Improving Agents - Best Nested Data Format](https://www.improvingagents.com/blog/best-nested-data-format/)

**Confidence**: HIGH (empirical studies with quantified results)

#### 1.3 Few-Shot Examples Best Practices

- **Minimo**: 2 ejemplos, maximo util ~5
- **Balance**: Usar BOTH positive AND negative examples
- **Formato consistente**: Mantener estructura identica entre ejemplos
- **Bias awareness**: Majority label bias, recency bias afectan resultados
- **Recomendacion**: Alternar positive/negative para evitar sesgos

**Sources**: [Prompt Engineering Guide](https://www.promptingguide.ai/techniques/fewshot), [IBM Few-Shot Prompting](https://www.ibm.com/think/topics/few-shot-prompting)

**Confidence**: HIGH (widely replicated findings)

---

### Dominio 2: Formatos de Reglas en Static Analysis Tools (P0)

#### 2.1 Semgrep Rule Schema

**Schema Version**: v1 (YAML)

**Campos Requeridos**:
```yaml
id: string              # Unique identifier, e.g., "no-unused-variable"
message: string         # Why Semgrep matched, how to fix
severity: enum          # LOW | MEDIUM | HIGH | CRITICAL
languages: [string]     # Target languages
pattern: string         # OR patterns, pattern-either, pattern-regex
```

**Campos Opcionales**:
```yaml
options: object         # Matching feature toggles
fix: object             # Autofix search-and-replace
metadata: object        # CWE, OWASP, custom tags (no behavior impact)
paths: object           # Include/exclude file paths
category: string        # best-practice | correctness | security
min-version: string     # Minimum Semgrep version
max-version: string     # Maximum compatible version
```

**Pattern Operators**:
- Positive: `pattern`, `patterns`, `pattern-either`, `pattern-regex`, `pattern-inside`
- Negative: `pattern-not`, `pattern-not-inside`, `pattern-not-regex`
- Conditionals: `metavariable-regex`, `metavariable-pattern`, `metavariable-comparison`

**Fortalezas**: Ejecutable, bien documentado, JSON Schema disponible, amplia adopcion
**Debilidades**: Limitado a lenguajes soportados, no captura rationale extenso

**Sources**:
- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)
- [Semgrep JSON Schema](https://json.schemastore.org/semgrep.json)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.2 SARIF (Static Analysis Results Interchange Format)

**Version**: 2.1.0 (OASIS Standard, August 2023)

**Object Model Hierarchy**:
```
sarifLog
  └── runs[]
        ├── tool
        ├── results[]
        │     ├── ruleId
        │     ├── ruleIndex
        │     ├── message
        │     ├── level: note | warning | error
        │     ├── kind
        │     └── locations[]
        │           ├── physicalLocation (file, region)
        │           └── logicalLocation (class, method)
        └── rules[] (reportingDescriptor)
              ├── id
              ├── name
              ├── shortDescription
              ├── fullDescription
              ├── messageStrings
              └── defaultConfiguration
```

**Fortalezas**: OASIS standard, tool-agnostic, rich location info, GitHub integration
**Debilidades**: Verboso, focused on results not rule definition, JSON only

**Sources**: [OASIS SARIF v2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)

**Confidence**: HIGH (Tier 1: OASIS international standard)

#### 2.3 ast-grep Rule Format

**Campos Core**:
```yaml
id: string              # Unique identifier
language: enum          # Bash|C|Cpp|CSharp|Go|Java|JavaScript|Python|Rust|TypeScript|...
rule: object            # AST matching specification
severity: enum          # hint | info | warning | error | off
```

**Rule Object Types**:
```yaml
# Atomic Rules
pattern: string | Pattern    # Code pattern to match
kind: string                 # AST node kind
regex: string                # Regex pattern

# Relational Rules
inside: RuleObject           # Target must be inside matching node
has: RuleObject              # Target must have child matching
follows: RuleObject          # Target follows matching node
precedes: RuleObject         # Target precedes matching node

# Composite Rules
all: [RuleObject]            # AND logic
any: [RuleObject]            # OR logic
not: RuleObject              # Negation
matches: string              # Named rule reference
```

**Campos Adicionales**:
```yaml
constraints: object     # Meta-variable filters
transform: object       # Meta-variable transformations
fix: string | FixConfig # Autofix pattern
```

**Meta-Variables**:
- `$VAR`: Match single AST node (named)
- `$$$ARGS`: Match zero or more nodes
- `$_VAR`: Non-capturing match
- `$$VAR`: Capture unnamed nodes

**Fortalezas**: Powerful AST matching, fix support, multiple languages, composable rules
**Debilidades**: Learning curve, less adoption than Semgrep

**Sources**: [ast-grep Configuration Reference](https://ast-grep.github.io/reference/yaml.html), [Rule Object Reference](https://ast-grep.github.io/reference/rule.html)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.4 ESLint Rule Schema

**Rule Export Structure**:
```javascript
module.exports = {
  meta: {
    type: "problem" | "suggestion" | "layout",
    docs: {
      description: string,    // Short description
      category: string,       // Rule category heading
      recommended: boolean,   // In eslint:recommended?
      url: string             // Documentation URL
    },
    fixable: "code" | "whitespace" | null,
    hasSuggestions: boolean,
    schema: [JSONSchema],     // Options validation (Draft-04)
    deprecated: boolean,
    replacedBy: [string],
    messages: {
      [messageId]: string     // Message templates
    }
  },
  create(context) {
    // Returns AST visitor object
    return {
      Identifier(node) { ... }
    };
  }
};
```

**Fortalezas**: Mature ecosystem, extensible, good schema validation
**Debilidades**: JavaScript-specific, programmatic (not declarative), complex setup

**Sources**: [ESLint Custom Rules](https://eslint.org/docs/latest/extend/custom-rules)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.5 CodeQL Query Structure

**Query File Structure**:
```ql
/**
 * @name Query name
 * @description Query description
 * @kind problem | path-problem | metric | diagnostic
 * @id language/query-id
 * @precision very-high | high | medium | low
 * @severity error | warning | recommendation
 * @tags correctness security maintainability
 * @problem.severity error | warning | recommendation
 */

import language

from /* variable declarations */
where /* logical formula */
select /* result expressions */
```

**Metadata Annotations**:
- `@name`: Human-readable name
- `@description`: Detailed explanation
- `@kind`: Result interpretation (problem, path-problem, metric)
- `@id`: Unique identifier (language/category/name)
- `@precision`: Confidence in results
- `@severity`: Issue severity
- `@tags`: Categorization tags

**Fortalezas**: Powerful Datalog-based queries, deep semantic analysis, GitHub integration
**Debilidades**: Steep learning curve, requires database building, proprietary aspects

**Sources**: [CodeQL Query Documentation](https://codeql.github.com/docs/writing-codeql-queries/about-codeql-queries/), [QL Language Reference](https://codeql.github.com/docs/ql-language-reference/)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.6 PMD XPath Rule Format

**XML Rule Structure**:
```xml
<?xml version="1.0"?>
<ruleset name="Custom Rules"
         xmlns="http://pmd.sourceforge.net/ruleset/2.0.0">
  <rule name="RuleName"
        language="java"
        message="Violation message"
        class="net.sourceforge.pmd.lang.rule.XPathRule">
    <description>Rule description</description>
    <priority>3</priority>
    <properties>
      <property name="xpath">
        <value><![CDATA[
          //FieldDeclaration[@Private='true']
        ]]></value>
      </property>
    </properties>
    <example><![CDATA[
      // Example violating code
    ]]></example>
  </rule>
</ruleset>
```

**Priority Levels**: 1 (highest) to 5 (lowest)

**Fortalezas**: XPath-based (familiar), XML standard, Designer tool available
**Debilidades**: Verbose XML, limited to PMD-supported languages, XPath learning curve

**Sources**: [PMD Writing XPath Rules](https://docs.pmd-code.org/latest/pmd_userdocs_extending_writing_xpath_rules.html)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.7 SonarQube Rule Definition

**Custom Rule Methods**:
1. **Java Plugin**: Full API access, most powerful
2. **XPath Rules**: Via web interface, simpler
3. **Generic Import**: External tool results in standard format

**Rule Metadata Guidelines** (Sonar internal):
```
Title: <action verb> <subject>
Description: HTML with sections
- What is the issue?
- How does it work?
- Pitfalls (optional)
- Exceptions (optional)
- More info (optional)

Message: Concise finding description
Severity: BLOCKER | CRITICAL | MAJOR | MINOR | INFO
Type: BUG | VULNERABILITY | CODE_SMELL | SECURITY_HOTSPOT
Tags: CWE, OWASP, custom
```

**Fortalezas**: Enterprise-grade, 5000+ rules, 30 languages, quality profiles
**Debilidades**: Plugin complexity, less portable than SARIF

**Sources**: [SonarQube Adding Coding Rules](https://docs.sonarsource.com/sonarqube-server/extension-guide/adding-coding-rules)

**Confidence**: HIGH (Tier 1: official documentation)

#### 2.8 Universal Fields Across SA Tools

| Field | Semgrep | SARIF | ast-grep | ESLint | CodeQL | PMD | SonarQube |
|-------|---------|-------|----------|--------|--------|-----|-----------|
| id/name | `id` | `ruleId` | `id` | `meta.docs` | `@id` | `name` | Rule Key |
| message | `message` | `message` | - | `messages` | `@description` | `message` | Message |
| severity | `severity` | `level` | `severity` | `meta.type` | `@severity` | `priority` | Severity |
| description | `metadata` | `fullDescription` | - | `meta.docs.description` | `@description` | `description` | Description |
| pattern | `pattern*` | - | `rule` | `create()` | `where` | `xpath` | Java API |
| fix | `fix` | `fix` | `fix` | `fixable` | - | - | quickfix |
| category | `category` | - | - | `meta.docs.category` | `@tags` | - | Type |
| tags/refs | `metadata` | `tags` | - | - | `@tags` | - | Tags |

**Convergencia Observada**:
- **Universales**: id, message/description, severity, pattern mechanism
- **Comunes**: fix/autofix, category, tags, language
- **Especificos**: precision (CodeQL), priority (PMD), paths (Semgrep)

---

### Dominio 3: RAG Chunk Design para Codigo y Reglas (P0)

#### 3.1 Optimal Chunk Size

| Content Type | Recommended Size | Overlap | Rationale |
|--------------|------------------|---------|-----------|
| Technical docs | 400-500 tokens | 15-20% | Capture full API descriptions |
| Fact-based queries | 128-256 tokens | 10% | Precise keyword matching |
| Conceptual content | 256-512 tokens | 15% | Broader context needed |
| Code rules | 256-512 tokens | 10-15% | Self-contained rule chunks |

**Starting Point**: 256 tokens, optimize based on retrieval metrics.

**Research Findings**:
- Smaller chunks (64-128) optimal for fact-based answers
- Larger chunks (512-1024) improve retrieval requiring broader context
- NVIDIA: Page-level chunking achieved highest accuracy in benchmarks
- 15% overlap performed best with 1024-token chunks

**Sources**:
- [LlamaIndex Chunk Size Evaluation](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5)
- [Firecrawl Chunking Strategies 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [NVIDIA Chunking Strategy Blog](https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/)

**Confidence**: HIGH (multiple empirical studies)

#### 3.2 Metadata Fields for Vector DB Filtering

**Essential Metadata**:
```yaml
# Identity
rule_id: string           # Unique identifier
version: semver           # Rule version

# Classification
category: enum            # security | reliability | performance | style
severity: enum            # critical | high | medium | low
language: [string]        # Programming languages

# Scope
applies_to:
  file_patterns: [glob]   # e.g., "*.ts", "src/**/*"
  phases: [enum]          # design | implement | review
  modules: [string]       # domain | infrastructure

# Discovery
tags: [string]            # Freeform tags for search
keywords: [string]        # Extracted keywords for BM25
```

**Filtering Best Practices**:
- Pre-filtering: Narrow by metadata BEFORE vector search (faster, more precise)
- Post-filtering: Filter AFTER vector search (more results, then refine)
- Hybrid: Combine semantic + keyword (BM25) search

**Sources**: [Pinecone Vector Database](https://www.pinecone.io/learn/vector-database/), [Neo4j Graph Metadata Filtering](https://neo4j.com/blog/developer/graph-metadata-filtering-vector-search-rag/)

**Confidence**: HIGH (production best practices)

#### 3.3 Code Embedding Models Performance

| Model | MRR | Recall@1 | Cost | Recommendation |
|-------|-----|----------|------|----------------|
| Voyage Code-3 | 97.3% | 95% | $$ | Best accuracy |
| OpenAI 3-small | 95.0% | 91% | $0.02/1M | Best cost/accuracy |
| Cohere v3 | 92.8% | 87% | $$ | Good alternative |
| MiniLM-L6 | 80.1% | 69% | Free | Budget option |
| GraphCodeBERT | 50.9% | 39% | Free | Not recommended |
| CodeBERT | 11.7% | 6.5% | Free | Obsolete |

**Key Insight**: General-purpose models (OpenAI, Voyage) significantly outperform older code-specific models (CodeBERT, GraphCodeBERT) on code search tasks.

**Hybrid Approach Recommended**: Combine code-specific embedding with BM25 keyword matching for best results.

**Sources**: [Modal Code Embedding Comparison](https://modal.com/blog/6-best-code-embedding-models-compared), [Code-Embed Paper](https://arxiv.org/html/2411.12644v2)

**Confidence**: HIGH (benchmark data from 2025)

#### 3.4 Self-Contained Chunk Design for Rules

Para que una regla funcione como chunk autonomo en RAG:

**Must Include**:
1. **Rule identity**: id, title, version
2. **Problem statement**: What and why
3. **Pattern specification**: How to detect
4. **At least one example**: Positive and/or negative
5. **Severity/priority**: For triage

**Optional but Valuable**:
- Rationale (the "why" - tribal knowledge)
- Fix suggestion
- Related rules (references, not full content)
- Verification method

**Anti-patterns**:
- Rules that reference external content without inclusion
- Rules split across multiple chunks
- Rules without examples
- Rules with only negative examples (no positive guidance)

---

### Dominio 4: Ontologias y Taxonomias de Reglas de Software (P1)

#### 4.1 Code Smell Taxonomy

**Mantyla Taxonomy** (widely cited):
1. **Bloaters**: Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps
2. **Object-Orientation Abusers**: Switch Statements, Parallel Inheritance Hierarchies, Refused Bequest, Alternative Classes with Different Interfaces
3. **Change Preventers**: Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies
4. **Dispensables**: Lazy Class, Data Class, Duplicate Code, Dead Code, Speculative Generality
5. **Couplers**: Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man

**Research Findings**:
- 56 Code Smells identified in comprehensive catalog
- Taxonomy provides better understanding than flat lists
- Anti-patterns sometimes used synonymously, sometimes distinguished

**Sources**: [Tusharma Code Smell Taxonomy](https://tusharma.in/smells/smellDefs.html), [Bad Code Smells Taxonomy](https://mmantyla.github.io/BadCodeSmellsTaxonomy)

**Confidence**: MEDIUM (academic consensus, some variation)

#### 4.2 Industry Classification Schemes

**CWE (Common Weakness Enumeration)**:
- Hierarchical taxonomy for security weaknesses
- CWE Top 25 Most Dangerous
- Machine-readable, widely adopted
- Example: CWE-79 (XSS), CWE-89 (SQL Injection)

**OWASP**:
- Top 10 Web Application Security Risks
- Updated periodically (2021 latest)
- Example: A01:2021 (Broken Access Control)

**CERT**:
- Secure Coding Standards by language
- Rules and recommendations
- Example: ERR00-J (Do not suppress or ignore checked exceptions)

**Aplicabilidad a SAR**: Use CWE/OWASP as metadata tags for security rules; Mantyla taxonomy for maintainability classification.

---

### Dominio 5: Specifications y Contracts en Software (P1)

#### 5.1 Design by Contract (Eiffel)

**Contract Elements**:
```eiffel
put (x: ELEMENT; key: STRING)
    require                          -- Precondition (client obligation)
        count <= capacity
        not key.empty
    do
        -- Implementation
    ensure                           -- Postcondition (supplier guarantee)
        has (x)
        item (key) = x
        count = old count + 1
    end
```

**Key Concepts**:
- **Precondition** (`require`): What client MUST satisfy
- **Postcondition** (`ensure`): What supplier MUST deliver
- **Invariant** (`invariant`): Must hold for all instances
- **old notation**: Reference to pre-execution state

**Inheritance Rules**:
- Subclasses may WEAKEN preconditions (not strengthen)
- Subclasses may STRENGTHEN postconditions (not weaken)

**Aplicabilidad a SAR**: Model rules as contracts. Pattern = precondition that must be satisfied. Violation = precondition failure.

**Sources**: [Eiffel Design by Contract](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_(tm),_Assertions_and_Exceptions)

**Confidence**: HIGH (foundational concept, well-documented)

#### 5.2 OpenAPI Specification

**Schema Structure**:
```yaml
openapi: "3.1.0"
info:
  title: API Name
  version: "1.0.0"
paths:
  /resource:
    get:
      operationId: getResource
      parameters: [...]
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
components:
  schemas:
    Resource:
      type: object
      required: [id, name]
      properties:
        id: { type: string }
        name: { type: string }
```

**Best Practices**:
- Be explicit with types and formats
- Use `required` array for mandatory fields
- Avoid `additionalProperties: true` unless necessary
- Unique, descriptive `operationId` for each operation
- Validate with Spectral or similar tools

**Aplicabilidad a SAR**: OpenAPI schema structure as model for rule specifications. JSON Schema for validation.

**Sources**: [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html), [OpenAPI v3.2.0 Spec](https://spec.openapis.org/oas/v3.2.0.html)

**Confidence**: HIGH (Tier 1: official specification)

#### 5.3 JSON Schema (2020-12)

**Core Validation Keywords**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "message", "severity"],
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "severity": { "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "uniqueItems": true
    }
  },
  "additionalProperties": false
}
```

**Key Features**:
- `prefixItems`/`items` for array validation (changed in 2020-12)
- `format` vocabulary (annotation vs assertion)
- `$ref` for schema reuse
- Rich validation: minLength, maxLength, pattern, enum, etc.

**Aplicabilidad a SAR**: Use JSON Schema for rule schema validation. Enables tooling, IDE support.

**Sources**: [JSON Schema 2020-12](https://json-schema.org/draft/2020-12)

**Confidence**: HIGH (Tier 1: official specification)

---

### Dominio 6: Cursor Rules, Claude Rules, y AI Coding Assistants (P1)

#### 6.1 Cursor Rules (.mdc format)

**Current Format** (2025):
```markdown
---
description: RPC Service boilerplate
globs:
  - src/services/**/*.ts
alwaysApply: false
---

# Rule content in Markdown

## When to Apply
- Creating new RPC services
- Modifying existing service interfaces

## Pattern
Always use the following structure...

## Examples
### Good
```typescript
// Correct implementation
```

### Bad
```typescript
// Incorrect implementation
```
```

**Key Features**:
- Frontmatter with `description`, `globs`, `alwaysApply`
- Stored in `.cursor/rules/` directory
- Markdown body with free-form content
- Glob-based scoping
- Composable (multiple .mdc files)

**Best Practices**:
- Keep rules under 500 lines
- Use concrete examples with tick/cross markers
- Focus on one concern per rule
- Include both positive and negative examples

**Limitation**: Context window forgets rules over long conversations - periodic reinforcement needed.

**Sources**: [Cursor Rules Documentation](https://cursor.com/docs/context/rules), [Tautorn Cursor Best Practices](https://www.tautorn.com.br/blog/cursor-rules)

**Confidence**: HIGH (Tier 2: official and community documentation)

#### 6.2 Claude CLAUDE.md

**Format**: Free-form Markdown with no required structure.

**Common Sections**:
```markdown
# Project Name

## Overview
Brief description of the project.

## Architecture
Key architectural patterns and decisions.

## Coding Standards
- Naming conventions
- File organization
- Error handling patterns

## Forbidden Patterns
Things Claude should NOT do.

## Preferred Patterns
Things Claude SHOULD do.

## Examples
Concrete code examples.
```

**Locations**:
- Project root: `CLAUDE.md`
- Directory-specific: `path/to/dir/CLAUDE.md`
- Personal: `~/.claude/CLAUDE.md`

**Best Practices**:
- Commit to source control
- Use `/init` to bootstrap
- Add learnings: "Add to CLAUDE.md an instruction to avoid this in future"
- Review and refine periodically

**Sources**: [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices), [Claude Code Manual](https://clune.org/posts/claude-code-manual/)

**Confidence**: HIGH (Tier 1-2: Anthropic documentation)

#### 6.3 Cline Rules (.clinerules/)

**Structure**:
```
project/
├── .clinerules/
│   ├── typescript-style.md
│   ├── testing-standards.md
│   └── code-review-checklist.md
└── src/
```

**Format**: Plain Markdown files with conventions:
```markdown
# TypeScript Style Guidelines

## Naming Conventions
- Use PascalCase for components
- Use camelCase for functions

## Examples

### Good
```typescript
function getUserById(id: string): User { ... }
```

### Bad
```typescript
function get_user_by_id(id: string): User { ... }
```
```

**Cross-Platform**: Works with Cursor, Cline, RooCode, Windsurf.

**Sources**: [Cline Rules Documentation](https://docs.cline.bot/enterprise-solutions/configuration/infrastructure-configuration/rules)

**Confidence**: HIGH (Tier 2: official documentation)

#### 6.4 Aider CONVENTIONS.md

**Usage**:
```bash
aider --read CONVENTIONS.md
# Or in .aider.conf.yml:
read: CONVENTIONS.md
```

**Format**: Free-form Markdown describing coding conventions.

**Example**:
```markdown
# Project Conventions

## HTTP Client
- Prefer httpx over requests
- Always use async client for IO operations

## Type Hints
- Use types everywhere possible
- Prefer Protocol over ABC for interfaces
```

**Sources**: [Aider Conventions Documentation](https://aider.chat/docs/usage/conventions.html)

**Confidence**: HIGH (Tier 2: official documentation)

#### 6.5 Emerging Standard: AGENTS.md

Proposal for unified agent rules across tools:
- Single file in project root
- Natural language rules
- Tool-agnostic format
- Reduces setup time across multiple agents

**Status**: Proposal, not widely adopted yet.

---

### Dominio 7: Knowledge Representation for Software Engineering (P2)

#### 7.1 ADR (Architecture Decision Record)

**MADR Template** (Markdown Any Decision Records):

```markdown
# Use Plain JUnit5 for advanced test assertions

## Status
Accepted | Deprecated | Superseded by [ADR-0123](0123-example.md)

## Context and Problem Statement
How to write readable test assertions?

## Decision Drivers
* Readability
* Maintainability
* Learning curve

## Considered Options
* Plain JUnit5
* Hamcrest
* AssertJ

## Decision Outcome
Chosen option: "Plain JUnit5", because...

### Consequences
* Good, because...
* Bad, because...

## Validation
How to verify the decision was correct?

## More Information
Links, related decisions, etc.
```

**Core Sections**: Context, Decision, Consequences
**Supplemental**: Status, Decision Drivers, Options, Validation

**Aplicabilidad a SAR**: ADR structure as model for rule rationale documentation. Decision drivers = evidence for rule.

**Sources**: [MADR Documentation](https://adr.github.io/madr/), [ADR Templates](https://adr.github.io/adr-templates/)

**Confidence**: HIGH (Tier 1: widely adopted standard)

---

## Comparative Matrix

### Format Comparison Against Evaluation Criteria

| Format | Semantic Density | LLM Comprehension | Executability | RAG Friendliness | Human Readability | Evolvability | Overall |
|--------|------------------|-------------------|---------------|------------------|-------------------|--------------|---------|
| **Semgrep YAML** | 85% | 80% | 100% | 75% | 85% | 90% | **86%** |
| **ast-grep YAML** | 80% | 75% | 100% | 70% | 80% | 85% | **81%** |
| **SARIF JSON** | 70% | 70% | 60% | 80% | 60% | 95% | **71%** |
| **CodeQL** | 90% | 60% | 100% | 50% | 50% | 85% | **71%** |
| **ESLint JS** | 75% | 65% | 100% | 40% | 70% | 80% | **70%** |
| **PMD XML** | 65% | 60% | 90% | 50% | 55% | 75% | **64%** |
| **Cursor .mdc** | 70% | 90% | 20% | 80% | 95% | 70% | **68%** |
| **CLAUDE.md** | 65% | 95% | 10% | 75% | 100% | 60% | **65%** |
| **Alpaca JSON** | 50% | 80% | 0% | 70% | 70% | 50% | **52%** |
| **MADR** | 80% | 85% | 0% | 85% | 95% | 90% | **69%** |

**Weights Applied**: Densidad 25%, LLM 25%, Ejecutabilidad 20%, RAG 15%, Human 10%, Evolvability 5%

**Key Observations**:
1. **Semgrep** leads overall due to balance of executability and readability
2. **Cursor/Claude** excel at LLM comprehension but lack executability
3. **CodeQL** most semantically dense but poor RAG fit (Datalog not easily chunked)
4. **SARIF** best for tool interoperability but verbose for human editing

---

## Synthesis: Recommended Schema for SAR Rules

Basado en el analisis de prior art, propongo el siguiente schema que combina:
- Campos universales de SA tools (Semgrep, ast-grep, SARIF)
- Estructura optimizada para RAG (self-contained chunks)
- Formato YAML para balance densidad/comprension
- Elementos de ejecutabilidad (pattern queries)
- Metadata para governance (provenance, evidence)

### Schema SAR Rule v1.0

```yaml
# ═══════════════════════════════════════════════════════════════════
# SAR RULE SCHEMA v1.0
# Semantically Dense Rule Representation for LLM Consumption via RAG
# ═══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# SECTION 1: IDENTITY (Required)
# Campos para identificacion unica y versionado
# ─────────────────────────────────────────────────────────────────────
id: string                    # Unique, slugified (e.g., "ts-async-error-handling")
version: semver               # Semantic version (e.g., "1.0.0")
status: enum                  # draft | active | deprecated | archived

# ─────────────────────────────────────────────────────────────────────
# SECTION 2: CLASSIFICATION (Required)
# Campos para filtering en RAG y priorizacion
# ─────────────────────────────────────────────────────────────────────
category: enum                # security | reliability | performance |
                              # maintainability | style | architecture
severity: enum                # critical | high | medium | low | info
priority: enum                # P0 | P1 | P2 | P3
tags: [string]                # Freeform tags for discovery
                              # e.g., ["async", "error-handling", "typescript"]

# ─────────────────────────────────────────────────────────────────────
# SECTION 3: SEMANTIC CORE (Required)
# El contenido principal que el LLM necesita entender
# ─────────────────────────────────────────────────────────────────────
title: string                 # Human-readable, <80 chars
                              # e.g., "Always wrap async operations in try-catch"

intent: string                # The "why" in ONE sentence
                              # e.g., "Prevent unhandled promise rejections that crash the process"

description: |                # Extended explanation in Markdown
  Full description of the rule including:
  - What the rule enforces
  - Why it matters
  - When to apply it

  This section should be self-contained - an LLM should understand
  the rule fully from this description alone.

rationale: |                  # The tribal knowledge - why this pattern exists HERE
  Captured organizational context:
  - Historical incidents that motivated this rule
  - Team discussions and decisions
  - Links to ADRs or RFCs if applicable

# ─────────────────────────────────────────────────────────────────────
# SECTION 4: SPECIFICATION (Required for executable rules)
# Queries ejecutables para deteccion automatica
# ─────────────────────────────────────────────────────────────────────
languages: [string]           # Target languages: [typescript, javascript]

pattern:                      # What code SHOULD look like (positive pattern)
  type: enum                  # ast-grep | semgrep | regex | structural
  query: |                    # The executable query
    try {
      await $ASYNC_CALL
    } catch ($ERR) {
      $HANDLER
    }
  explanation: string         # Plain language explanation of the pattern

anti_pattern:                 # What code should NOT look like (optional)
  type: enum
  query: |
    await $ASYNC_CALL
  explanation: string

fix:                          # Autofix template (optional)
  template: |
    try {
      await $ASYNC_CALL
    } catch (error) {
      logger.error('Operation failed', { error });
      throw error;
    }
  description: string         # Explanation of the fix

# ─────────────────────────────────────────────────────────────────────
# SECTION 5: EVIDENCE (Required - minimum 3 positive, 2 negative)
# Ejemplos concretos para few-shot learning
# ─────────────────────────────────────────────────────────────────────
examples:
  positive:                   # DO this (minimum 3)
    - code: |
        async function fetchUser(id: string): Promise<User> {
          try {
            const response = await api.get(`/users/${id}`);
            return response.data;
          } catch (error) {
            logger.error('Failed to fetch user', { id, error });
            throw new UserFetchError(id, error);
          }
        }
      explanation: |
        Proper error handling with logging and typed error.
      source:                 # Provenance (optional but recommended)
        file: src/services/user-service.ts
        commit: abc123

  negative:                   # DON'T do this (minimum 2)
    - code: |
        async function fetchUser(id: string): Promise<User> {
          const response = await api.get(`/users/${id}`);
          return response.data;
        }
      explanation: |
        Missing error handling - unhandled rejection will crash process.
      fix: |                  # How to correct this specific violation
        Wrap the await call in try-catch, log the error, and rethrow
        with appropriate context.

# ─────────────────────────────────────────────────────────────────────
# SECTION 6: RELATIONSHIPS (Optional)
# Conexiones con otras reglas para navegacion en grafo
# ─────────────────────────────────────────────────────────────────────
relationships:
  requires: [rule_id]         # Must be satisfied first
  conflicts_with: [rule_id]   # Mutually exclusive
  supersedes: [rule_id]       # Deprecates older rules
  related_to: [rule_id]       # Informational links
  parent: rule_id             # Hierarchical relationship

# ─────────────────────────────────────────────────────────────────────
# SECTION 7: SCOPE (Required)
# Contexto de aplicabilidad para RAG filtering
# ─────────────────────────────────────────────────────────────────────
applies_to:
  phases: [enum]              # design | implement | review | deploy
  file_patterns: [glob]       # ["*.ts", "src/services/**/*"]
  modules: [string]           # [domain, application, infrastructure]
  contexts: [string]          # [api, cli, worker, test]

excludes:                     # Where rule does NOT apply
  file_patterns: [glob]       # ["**/*.test.ts", "**/*.spec.ts"]
  contexts: [string]          # [test, mock]

# ─────────────────────────────────────────────────────────────────────
# SECTION 8: PROVENANCE (Required for governance)
# Trazabilidad y auditoria
# ─────────────────────────────────────────────────────────────────────
provenance:
  source: enum                # sar-extracted | manual | imported | hybrid
  extraction:                 # If SAR-extracted
    tool_version: string      # SAR version used
    config_hash: string       # Configuration hash
    timestamp: ISO8601        # When extracted
    evidence_count: number    # Number of occurrences found
    confidence: enum          # high | medium | low

  validation:                 # Human validation status
    reviewed_by: string       # Reviewer ID
    reviewed_at: ISO8601
    approved: boolean
    comments: string

# ─────────────────────────────────────────────────────────────────────
# SECTION 9: METADATA (Optional)
# Campos adicionales para integracion
# ─────────────────────────────────────────────────────────────────────
metadata:
  cwe: [string]               # ["CWE-248", "CWE-755"]
  owasp: [string]             # ["A01:2021"]
  cert: [string]              # ["ERR00-J"]
  references: [url]           # External documentation

  # Custom fields for organization-specific needs
  custom: object
```

### Schema Justificacion por Campo

| Campo | Fuente Principal | Justificacion |
|-------|------------------|---------------|
| `id` | Universal (todos los SA tools) | Identificacion unica, referencia estable |
| `version` | SARIF, OpenAPI | Evolucion controlada, deprecation |
| `status` | SARIF, MADR | Lifecycle management |
| `category` | Semgrep, SonarQube | RAG filtering, priorization |
| `severity` | Universal | Triage, alerting |
| `priority` | SAR scoring research | Ordenamiento en backlog |
| `tags` | Semgrep metadata, CodeQL | Keyword search, classification |
| `title` | Universal | Human readability |
| `intent` | MADR decision outcome | Quick understanding of "why" |
| `description` | Universal | Full context for LLM |
| `rationale` | MADR, ADRs | Tribal knowledge capture |
| `languages` | Semgrep, ast-grep | Applicability filtering |
| `pattern.type` | ast-grep, Semgrep | Tool-agnostic execution |
| `pattern.query` | ast-grep, Semgrep | Executable specification |
| `anti_pattern` | Few-shot research | Boundary definition |
| `fix` | Semgrep, ast-grep | Autofix capability |
| `examples.positive` | Few-shot research | DO this (min 3) |
| `examples.negative` | Few-shot research | DON'T do this (min 2) |
| `relationships` | SARIF, ontology research | Graph navigation |
| `applies_to` | Semgrep paths, Cursor globs | Scope definition |
| `excludes` | Semgrep paths | Exception handling |
| `provenance.source` | SAR extraction research | Audit trail |
| `provenance.extraction` | SLSA, reproducibility | Reproducibility |
| `provenance.validation` | Governance requirements | Human oversight |
| `metadata.cwe/owasp` | Semgrep, SonarQube | Standard references |

---

## RAG Integration Design

### Chunking Strategy

**Recommendation**: Single-chunk rules (no splitting)

Cada regla SAR debe caber en un chunk de 256-512 tokens. Si una regla excede este limite:
1. Reducir descripcion/rationale
2. Mover ejemplos adicionales a documento separado referenciado
3. Mantener ejemplos minimos inline (1 positive, 1 negative)

**Chunk Structure**:
```
[HEADER: id, title, severity, category, tags]
[INTENT: one-sentence why]
[DESCRIPTION: core explanation]
[PATTERN: detection query]
[EXAMPLE_POSITIVE: one DO example]
[EXAMPLE_NEGATIVE: one DON'T example]
```

**Estimacion Token Budget** (GPT-4 tokenizer):
- Header: ~30 tokens
- Intent: ~20 tokens
- Description: ~150 tokens (target)
- Pattern: ~50 tokens
- Examples: ~150 tokens (2 examples)
- **Total**: ~400 tokens (within 256-512 target)

### Metadata Fields para Vector DB

**Indexed Fields** (for filtering):
```yaml
rule_id: string          # Exact match
category: string         # Enum filter
severity: string         # Enum filter
languages: [string]      # Array contains
tags: [string]           # Array contains
status: string           # Enum filter
applies_to.phases: [string]  # Array contains
applies_to.modules: [string] # Array contains
```

**Embedding Fields** (for semantic search):
```yaml
# Concatenate for embedding generation:
embedding_text: |
  {title}
  {intent}
  {description}
  {rationale}
  Tags: {tags.join(', ')}
```

### Query Patterns

**Pattern 1: Category + Severity Filter**
```
Query: "How should I handle errors in async functions?"
Pre-filter: category = "reliability" AND languages contains "typescript"
Semantic: "error handling async functions"
```

**Pattern 2: Tag-Based Discovery**
```
Query: "Security rules for authentication"
Pre-filter: category = "security" AND tags contains "authentication"
Semantic: "authentication security vulnerabilities"
```

**Pattern 3: Phase-Scoped Rules**
```
Query: "What to check during code review?"
Pre-filter: applies_to.phases contains "review"
Semantic: "code review checklist patterns"
```

### Re-Ranking Considerations

Despues de retrieval inicial, re-rank por:
1. **Severity alignment**: Critical rules first for security queries
2. **Specificity**: Prefer rules with matching `applies_to` context
3. **Freshness**: Prefer recently validated rules
4. **Evidence strength**: Prefer rules with high provenance.confidence

---

## Open Questions

Las siguientes preguntas no fueron resueltas por este research y requieren experimentacion:

### Q1: Optimal Description Length
**Pregunta**: Cual es la longitud optima de `description` para balance entre completitud y token efficiency?

**Hipotesis**: 100-200 tokens es suficiente si `intent`, `examples`, y `pattern` son buenos.

**Experimento Propuesto**: A/B test con descripciones de 50, 100, 200, 400 tokens midiendo retrieval precision y LLM task completion.

### Q2: Example Count vs Quality
**Pregunta**: Es mejor tener mas ejemplos (5+) o menos ejemplos (2-3) de mayor calidad?

**Research Suggests**: 2-5 es el rango optimo, pero no hay data especifica para reglas de codigo.

**Experimento Propuesto**: Variar numero de ejemplos (1, 2, 3, 5, 10) y medir LLM adherencia a regla.

### Q3: Pattern Query Format Preference
**Pregunta**: Que formato de pattern query (ast-grep vs Semgrep vs regex) es mejor comprendido por LLMs?

**Hipotesis**: LLMs comprenden mejor patterns que se parecen a codigo real (ast-grep) que DSLs abstractos.

**Experimento Propuesto**: Presentar misma regla con diferentes formatos de query, medir comprension.

### Q4: Negative Example Impact
**Pregunta**: Los ejemplos negativos mejoran o confunden al LLM?

**Research Suggests**: Mejoran, pero hay riesgo de que el LLM imite el patron negativo.

**Experimento Propuesto**: Comparar reglas con/sin ejemplos negativos en tareas de generacion.

### Q5: Cross-Language Rule Generalization
**Pregunta**: Puede un LLM generalizar una regla de TypeScript a Python basandose en el `intent`?

**Hipotesis**: Si el `intent` es suficientemente claro, si.

**Experimento Propuesto**: Entrenar con reglas TS, evaluar aplicacion en Python.

### Q6: Chunk Boundary Effects
**Pregunta**: Como afecta el truncado de reglas largas a la comprension?

**Hipotesis**: Rules truncadas en mitad de un ejemplo son peores que truncadas despues del intent.

**Experimento Propuesto**: Truncar reglas en diferentes puntos, medir comprension.

### Q7: Embedding Model Selection for Rules
**Pregunta**: Los modelos generales (OpenAI) superan a modelos code-specific para reglas que son mayormente texto?

**Hipotesis**: Para reglas semanticamente densas (mas texto que codigo), modelos generales funcionan bien.

**Experimento Propuesto**: Benchmark Voyage-code vs OpenAI-3 vs Cohere en retrieval de reglas SAR.

---

## Validacion de Hipotesis Original

El prompt incluia una hipotesis de estructura. Evaluacion:

| Campo Hipotetico | Validacion | Ajuste |
|------------------|------------|--------|
| `id`, `version`, `status` | VALIDADO | Sin cambios |
| `category`, `priority`, `tags` | VALIDADO | Sin cambios |
| `title`, `intent`, `description` | VALIDADO | Sin cambios |
| `pattern.type`, `pattern.query` | VALIDADO | Agregar `explanation` |
| `anti_pattern` | VALIDADO | Hacerlo opcional |
| `examples.positive/negative` | VALIDADO | Agregar `source` para provenance |
| `requires`, `conflicts_with`, `supersedes` | VALIDADO | Agrupar en `relationships` |
| `applies_to.phases/file_patterns/modules` | VALIDADO | Agregar `excludes` |
| `extracted_from` | REFINADO | Renombrar a `provenance`, expandir |
| `metadata.cwe/owasp/references` | VALIDADO | Sin cambios |

**Conclusion**: La hipotesis original era solida. El schema propuesto es una evolucion refinada con:
1. Mejor organizacion en secciones
2. Campo `explanation` para patterns
3. Seccion `provenance` expandida para auditoria
4. Seccion `excludes` para excepciones explicitas
5. Campo `source` en ejemplos para trazabilidad

---

## Conclusiones

Este research establece que:

1. **YAML es el formato recomendado** para reglas SAR, balanceando densidad semantica, comprension LLM, y legibilidad humana.

2. **La estructura propuesta converge** con formatos probados en produccion (Semgrep, ast-grep, SARIF) mientras agrega elementos especificos para RAG y gobernanza.

3. **Self-contained chunks** de 256-512 tokens son viables si se priorizan campos esenciales y se externalizan ejemplos adicionales.

4. **La ejecutabilidad diferencia** reglas de gobernanza de meras convenciones. El campo `pattern.query` es critico.

5. **Provenance es no-negociable** para reglas extraidas automaticamente. Sin trazabilidad, no hay confianza.

6. **Few-shot examples** (3 positive, 2 negative minimo) son esenciales para que LLMs apliquen reglas correctamente.

El schema propuesto esta listo para implementacion piloto, con los open questions como areas de experimentacion futura.

---

## Referencias

### Tier 1 (Gold) - Especificaciones Oficiales
- [OASIS SARIF v2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/v3.2.0.html)
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12)
- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)
- [ast-grep Configuration Reference](https://ast-grep.github.io/reference/yaml.html)
- [ESLint Custom Rules](https://eslint.org/docs/latest/extend/custom-rules)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [PMD Writing XPath Rules](https://docs.pmd-code.org/latest/pmd_userdocs_extending_writing_xpath_rules.html)

### Tier 2 (Silver) - Documentacion de Herramientas
- [Cursor Rules Documentation](https://cursor.com/docs/context/rules)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Cline Rules Documentation](https://docs.cline.bot/enterprise-solutions/configuration/infrastructure-configuration/rules)
- [Aider Conventions](https://aider.chat/docs/usage/conventions.html)
- [SonarQube Adding Coding Rules](https://docs.sonarsource.com/sonarqube-server/extension-guide/adding-coding-rules)
- [MADR Documentation](https://adr.github.io/madr/)
- [Eiffel Design by Contract](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_(tm),_Assertions_and_Exceptions)

### Tier 2 (Silver) - Research Papers & Benchmarks
- [arXiv:2411.10541 - Prompt Formatting Impact on LLM Performance](https://arxiv.org/html/2411.10541v1)
- [Improving Agents - Best Nested Data Format for LLMs](https://www.improvingagents.com/blog/best-nested-data-format/)
- [LlamaIndex Chunk Size Evaluation](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5)
- [NVIDIA Chunking Strategy](https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/)
- [Modal Code Embedding Comparison](https://modal.com/blog/6-best-code-embedding-models-compared)
- [Code-Embed Paper](https://arxiv.org/html/2411.12644v2)

### Tier 3 (Bronze) - Community Resources
- [awesome-cursorrules Repository](https://github.com/PatrickJS/awesome-cursorrules)
- [Prompt Engineering Guide - Few-Shot](https://www.promptingguide.ai/techniques/fewshot)
- [Tusharma Code Smell Taxonomy](https://tusharma.in/smells/smellDefs.html)
- [Mantyla Bad Code Smells Taxonomy](https://mmantyla.github.io/BadCodeSmellsTaxonomy)

### Internal References
- [RaiSE Deterministic Extraction Patterns](../deterministic-rule-extraction/deterministic-extraction-patterns.md)
- [SAR Templates README](/.raise-kit/templates/raise/sar/README.md)

---

*Documento generado como parte del research de RaiSE para reliable AI software engineering.*
*Research ID: RES-SAR-REPR-001 | Version: 1.0.0 | Fecha: 2026-01-28*
