# Deep Research Prompt: Modelo de Representación de Reglas Semánticamente Densas

 **Research ID** : RES-SAR-REPR-001
 **Fecha** : 2026-01-28
 **Solicitante** : Emilio (RaiSE Framework)
 **Objetivo** : Investigar prior art para definir el formato óptimo de representación de reglas extraídas por SAR que sean semánticamente densas, validables, y consumibles por agentes LLM vía RAG.

---

## Contexto del Problema

SAR (Static Analysis for Rules) extrae patrones de código brownfield y los convierte en  **reglas gobernables** . Estas reglas deben:

1. **Ser semánticamente densas** : Contener suficiente contexto para que un LLM entienda cuándo y cómo aplicarlas sin ambigüedad
2. **Ser validables** : Incluir especificaciones ejecutables que permitan verificar cumplimiento
3. **Ser consumibles por RAG** : Optimizadas para retrieval semántico y injection en context window
4. **Ser deterministas** : La misma regla produce el mismo comportamiento de enforcement
5. **Ser evolucionables** : Soportar versionado, deprecación, y refinamiento

 **La pregunta central** : ¿Qué estructura de datos representa óptimamente una "regla de código" para consumo por agentes LLM en un flujo RAG?

---

## Dominios de Investigación

### Dominio 1: Formatos de Representación de Conocimiento para LLMs (P0)

<scope>
- Structured prompting formats (YAML, JSON, XML, Markdown)
- Knowledge graph serializations consumibles por LLMs
- Instruction tuning data formats (Alpaca, ShareGPT, OpenAI function schemas)
- Tool/function calling schemas y su semántica
- DSLs para expresar constraints y reglas
</scope>
<key_questions>

1. ¿Qué formatos de representación tienen mejor "instruction following" cuando se inyectan en context?
2. ¿Cómo balancear densidad semántica vs. token efficiency?
3. ¿Qué campos son necesarios vs. opcionales para que un LLM aplique una regla correctamente?
4. ¿Cómo representar ejemplos positivos/negativos de forma que el LLM generalice correctamente?
5. ¿Qué rol juegan los metadatos (severity, scope, rationale) en la aplicación de reglas?
   </key_questions>

<search_queries>

* "LLM instruction format best practices"
* "structured knowledge injection context window"
* "YAML vs JSON vs Markdown LLM comprehension"
* "few-shot examples format LLM"
* "rule representation knowledge graphs LLM"
* "semantic density prompt engineering"
  </search_queries>

<expected_sources>

* Papers de instruction tuning (FLAN, Alpaca, Vicuna)
* OpenAI/Anthropic documentation sobre structured outputs
* Research sobre prompt formatting impact (arXiv)
* Knowledge graph + LLM integration papers
  </expected_sources>

---

### Dominio 2: Formatos de Reglas en Static Analysis Tools (P0)

<scope>
- Semgrep rule schema (YAML)
- CodeQL query structure
- ESLint/PMD rule definitions
- SonarQube rule format
- ast-grep YAML rules
- SARIF (Static Analysis Results Interchange Format)
</scope>
<key_questions>

1. ¿Qué campos son universales en todas las herramientas de SA?
2. ¿Cómo expresan estas herramientas el "pattern" vs. el "anti-pattern"?
3. ¿Cómo manejan severity, confidence, y false positive rates?
4. ¿Qué metadatos de trazabilidad incluyen (CWE, OWASP, custom tags)?
5. ¿Cómo expresan fix suggestions o autofix?
   </key_questions>

<search_queries>

* "Semgrep rule schema specification"
* "SARIF format static analysis"
* "CodeQL query structure documentation"
* "ESLint rule metadata schema"
* "static analysis rule interchange format"
* "code pattern rule DSL comparison"
  </search_queries>

<expected_sources>

* Semgrep docs (semgrep.dev/docs/writing-rules)
* SARIF spec (OASIS standard)
* CodeQL documentation
* ESLint custom rules guide
* PMD rule designer documentation
  </expected_sources>

---

### Dominio 3: RAG Chunk Design para Código y Reglas (P0)

<scope>
- Optimal chunk size para code-related content
- Metadata schemas para filtering en vector DBs
- Hybrid search (semantic + keyword) para reglas
- Context window packing strategies
- Re-ranking y relevance scoring para reglas
</scope>
<key_questions>

1. ¿Cuál es el tamaño óptimo de chunk para reglas de código en RAG?
2. ¿Qué metadata fields mejoran precision en retrieval?
3. ¿Cómo estructurar una regla para que sea "self-contained" en un chunk?
4. ¿Qué embedding models funcionan mejor para code rules vs. prose rules?
5. ¿Cómo manejar reglas con dependencias (requires, conflicts_with)?
   </search_queries>

<search_queries>

* "RAG chunk size optimization code"
* "vector database metadata filtering best practices"
* "code documentation RAG retrieval"
* "embedding models code vs text comparison"
* "hybrid search semantic keyword code"
* "context window packing strategies LLM"
  </search_queries>

<expected_sources>

* LangChain/LlamaIndex documentation sobre chunking
* Papers sobre code retrieval (CodeSearchNet, etc.)
* Pinecone/Weaviate/Chroma best practices
* Research sobre embedding models para código
  </expected_sources>

---

### Dominio 4: Ontologías y Taxonomías de Reglas de Software (P1)

<scope>
- Taxonomías de code smells y anti-patterns
- Ontologías de software engineering (SWEBOK)
- Classification schemes para coding standards
- Relationship types entre reglas (depends, conflicts, supersedes)
</scope>
<key_questions>

1. ¿Existen ontologías formales para reglas de código que podamos reusar?
2. ¿Qué taxonomías de categorización son estándar en la industria?
3. ¿Cómo modelar relaciones entre reglas (jerarquía, conflicto, dependencia)?
4. ¿Qué nivel de formalismo es útil vs. overhead?
   </key_questions>

<search_queries>

* "software engineering ontology OWL"
* "code smell taxonomy classification"
* "coding standards categorization scheme"
* "anti-pattern ontology software"
* "rule relationship modeling software constraints"
  </search_queries>

<expected_sources>

* SWEBOK (Software Engineering Body of Knowledge)
* Papers sobre code smell detection y taxonomías
* ISO/IEC standards para software quality
* Academic ontologies (OntoSoft, etc.)
  </expected_sources>

---

### Dominio 5: Specifications y Contracts en Software (P1)

<scope>
- Design by Contract (DbC) specifications
- API specification formats (OpenAPI, AsyncAPI)
- Type-level specifications (refinement types)
- Formal methods para especificar behavior
- Property-based testing specifications
</scope>
<key_questions>

1. ¿Cómo expresan los contratos formales las precondiciones/postcondiciones?
2. ¿Qué podemos aprender de OpenAPI sobre especificar "correct usage"?
3. ¿Cómo hacer una regla "ejecutable" (verificable programáticamente)?
4. ¿Qué balance entre formalismo y usabilidad es apropiado?
   </key_questions>

<search_queries>

* "design by contract specification format"
* "OpenAPI schema best practices"
* "executable specifications software"
* "property-based testing specification"
* "refinement types practical"
  </search_queries>

<expected_sources>

* Eiffel DbC documentation
* OpenAPI specification
* Papers sobre refinement types (Liquid Haskell, etc.)
* QuickCheck/Hypothesis documentation
  </expected_sources>

---

### Dominio 6: Cursor Rules, Claude Rules, y AI Coding Assistants (P1)

<scope>
- .cursorrules / rules.mdc format
- Claude CLAUDE.md conventions
- GitHub Copilot workspace rules
- Cline rules format
- Aider CONVENTIONS.md pattern
</scope>
<key_questions>

1. ¿Qué formato usan los AI coding assistants actuales para reglas?
2. ¿Qué campos han demostrado ser efectivos en la práctica?
3. ¿Cómo manejan scope (file, directory, project)?
4. ¿Cómo expresan prioridad y condiciones de aplicación?
5. ¿Qué limitaciones tienen los formatos actuales?
   </key_questions>

<search_queries>

* "cursor rules format specification"
* "cursorrules best practices examples"
* "claude.md project instructions format"
* "AI coding assistant custom rules"
* "cline rules configuration"
* "aider conventions documentation"
  </search_queries>

<expected_sources>

* Cursor documentation oficial
* awesome-cursorrules repository
* Anthropic Claude documentation
* Cline documentation
* Community best practices posts
  </expected_sources>

---

### Dominio 7: Knowledge Representation for Software Engineering (P2)

<scope>
- Architecture Decision Records (ADRs)
- Request for Comments (RFCs) internal
- Technical Design Documents formats
- Runbooks y playbooks structures
</scope>
<key_questions>

1. ¿Qué podemos aprender de ADRs sobre capturar "decisions"?
2. ¿Cómo estructuran las empresas su conocimiento técnico interno?
3. ¿Qué formatos han demostrado longevidad y mantenibilidad?
   </key_questions>

<search_queries>

* "architecture decision record format template"
* "technical documentation knowledge management"
* "RFC template software engineering"
* "runbook structure best practices"
  </search_queries>

---

## Framework de Evaluación

Para cada formato/estructura encontrada, evaluar:

| Criterio                      | Peso | Descripción                                |
| ----------------------------- | ---- | ------------------------------------------- |
| **Densidad Semántica** | 25%  | ¿Cuánto contexto útil por token?         |
| **LLM Comprehension**   | 25%  | ¿El LLM interpreta correctamente la regla? |
| **Ejecutabilidad**      | 20%  | ¿Se puede verificar automáticamente?      |
| **RAG Friendliness**    | 15%  | ¿Funciona bien como chunk en retrieval?    |
| **Human Readability**   | 10%  | ¿Un humano puede entender y editar?        |
| **Evolvability**        | 5%   | ¿Soporta versionado y cambios?             |

---

## Hipótesis de Trabajo

Basado en el research previo de SAR, la hipótesis inicial es que el formato óptimo tendrá:

```yaml
# HIPÓTESIS: Estructura de Regla SAR
---
# === IDENTITY ===
id: string                    # Único, slugified
version: semver               # Para evolución
status: draft|active|deprecated

# === CLASSIFICATION ===
category: naming|structure|error_handling|async|security|...
priority: P0|P1|P2
tags: [string]                # Para filtering en RAG

# === SEMANTIC CORE ===
title: string                 # Human-readable, <80 chars
intent: string                # El "por qué" en una oración
description: markdown         # Explicación completa

# === SPECIFICATION (Ejecutable) ===
pattern:
  type: ast-grep|regex|structural
  query: string               # La query ejecutable
  language: [typescript, javascript, ...]
  
anti_pattern:
  query: string               # Qué NO hacer (opcional)

# === EVIDENCE (Para validación) ===
examples:
  positive:                   # DO this
    - code: |
        ...
      explanation: string
  negative:                   # DON'T do this
    - code: |
        ...
      explanation: string
      fix: |                  # Cómo corregir
        ...

# === RELATIONSHIPS (Para grafo) ===
requires: [rule_id]           # Dependencias
conflicts_with: [rule_id]     # Mutually exclusive
supersedes: [rule_id]         # Depreca otra regla
related_to: [rule_id]         # Informational

# === CONTEXT (Para RAG filtering) ===
applies_to:
  phases: [design, implement, review]
  file_patterns: ["*.ts", "src/**/*"]
  modules: [domain, infrastructure]
  
# === PROVENANCE (Trazabilidad) ===
extracted_from:
  source: SAR|manual|imported
  evidence_count: number
  confidence: HIGH|MEDIUM|LOW
  extraction_date: ISO8601

# === METADATA ===
metadata:
  cwe: [CWE-xxx]              # Si aplica
  owasp: [A01:2021]           # Si aplica
  references: [url]
---

# {title}

{description expandida en Markdown}

## Rationale

{Por qué esta regla existe - el conocimiento tribal capturado}

## Examples

### ✅ Correct Usage

```{language}
{positive_example}
```

### ❌ Incorrect Usage

```{language}
{negative_example}
```

 **Fix** : {cómo corregir}

## Verification

Esta regla puede verificarse ejecutando:

```bash
sg --pattern '{pattern.query}' --lang {language}
```

## Related Rules

* [{related_rule.id}](https://claude.ai/chat/%7Blink%7D): {brief description}

```

**Esta hipótesis debe ser validada o refinada por la investigación.**

---

## Output Esperado

El research debe producir:

### 1. Prior Art Analysis (por dominio)
Para cada formato/esquema encontrado:
- Descripción del formato
- Campos que incluye
- Fortalezas y debilidades
- Evidencia de uso (adopción, herramientas que lo usan)
- Aplicabilidad a SAR

### 2. Comparative Matrix
Tabla comparando todos los formatos encontrados contra los criterios de evaluación.

### 3. Synthesis: Recommended Schema
Propuesta de schema para SAR rules basada en:
- Campos universales (presentes en múltiples formatos)
- Campos únicos valiosos (de formatos específicos)
- Campos necesarios para RAG (metadata para filtering)
- Campos necesarios para ejecutabilidad (pattern queries)

### 4. RAG Integration Design
- Estrategia de chunking para reglas
- Metadata fields para vector DB
- Query patterns para retrieval
- Re-ranking considerations

### 5. Open Questions
Preguntas que el research no pudo resolver y requieren experimentación.

---

## Restricciones de Investigación

### Fuentes Válidas (por tier)

**Tier 1 (Gold)**: 
- Especificaciones oficiales (SARIF, OpenAPI, JSON Schema)
- Papers peer-reviewed sobre knowledge representation
- Documentación oficial de herramientas establecidas

**Tier 2 (Silver)**:
- Documentación de Cursor, Semgrep, CodeQL
- Blog posts de autores de herramientas
- arXiv preprints con evaluación empírica

**Tier 3 (Bronze)**:
- Community repositories (awesome-cursorrules)
- Stack Overflow discussions con evidencia
- GitHub issues/discussions relevantes

**Tier 4 (Copper)** - Solo para señales, no evidencia:
- Reddit/HN discussions
- Twitter threads de practitioners

### Reglas Epistémicas

1. **No inventar formatos** — Solo reportar lo que existe
2. **Citar fuentes verificables** — URL o paper reference
3. **Distinguir "usado en producción" vs "propuesto en paper"**
4. **Declarar gaps** — Si un dominio no tiene prior art, decirlo
5. **Confidence levels** — HIGH/MEDIUM/LOW para cada finding

---

## Criterio de Completitud

El research está completo cuando:

- [ ] Cada dominio tiene al menos 3 fuentes tier 1-2
- [ ] La comparative matrix tiene al menos 8 formatos evaluados
- [ ] El recommended schema tiene justificación para cada campo
- [ ] Los open questions son específicos y accionables
- [ ] El documento es self-contained (no requiere leer otros docs para entender)

---

## Notas para el Investigador

1. **Prioriza formatos usados en producción** sobre propuestas académicas
2. **Busca convergencia** — campos que aparecen en múltiples formatos son señal fuerte
3. **Considera el consumidor** — el output es para LLMs, no solo humanos
4. **Piensa en RAG** — la regla debe funcionar como chunk autónomo
5. **Ejecutabilidad es clave** — si no se puede verificar, no es gobernanza

---

**Tiempo estimado de investigación**: 4-6 horas
**Formato de entrega**: Markdown document siguiendo la estructura de output esperado
**Audiencia**: Technical lead de RaiSE (asume conocimiento de LLMs, RAG, y static analysis)
```
