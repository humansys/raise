# RaiSE Context - Solution Vision

**Document ID**: VIS-CTX-001
**Version**: 1.0.0
**Date**: 2026-01-28
**Author**: Emilio + Claude Opus 4.5
**Status**: Borrador
**Related Docs**:
  - [SAR Solution Vision](./solution-vision.md) - Componente de extraccion
  - [SAR Solution Roadmap](./solution-roadmap.md) - Roadmap tactico

---

## Contexto de Arquitectura

`raise.ctx` es el componente que entrega el Minimum-Viable Context (MVC) a agentes LLM, consumiendo los datos generados por SAR:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAISE GOVERNANCE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐                                                │
│  │        SAR          │  Batch: cuando codebase cambia                 │
│  │   (Extracción)      │  Ver: solution-vision.md                       │
│  └──────────┬──────────┘                                                │
│             │ genera                                                     │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │    Data Store       │  .raise/                                       │
│  │                     │  ├── rules/*.yaml                              │
│  │                     │  ├── graph.yaml                                │
│  │                     │  └── project-profile.yaml                      │
│  └──────────┬──────────┘                                                │
│             │ consume                                                    │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │    raise.ctx        │  On-demand: cada task del agente    ◀── ESTE  │
│  │  (Entrega de MVC)   │  CLI: raise ctx get                  DOCUMENTO│
│  ├─────────────────────┤  Slash: /raise.ctx                             │
│  │ • Lee rules + graph │                                                │
│  │ • Traversal determ. │                                                │
│  │ • Filtra por task   │                                                │
│  │ • Entrega MVC       │                                                │
│  └──────────┬──────────┘                                                │
│             │ entrega                                                    │
│             ▼                                                            │
│  ┌─────────────────────┐                                                │
│  │   Agente LLM        │  Recibe MVC en context window                  │
│  │  (Claude Code)      │                                                │
│  └─────────────────────┘                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**SAR** genera los datos (batch, cuando el codebase cambia).
**raise.ctx** entrega el contexto (on-demand, cada vez que un agente necesita reglas).

---

## Contexto de Negocio

### Declaracion del Problema

Los agentes LLM necesitan contexto de gobernanza en el momento justo, con la cantidad justa de informacion. Demasiado contexto desperdicia tokens; muy poco contexto produce codigo inconsistente.

- **Quien se ve afectado?** Agentes LLM ejecutando tareas de desarrollo
- **Cual es el impacto?** Sin MVC, agentes ignoran convenciones del proyecto
- **Cuando ocurre?** Cada vez que un agente genera o modifica codigo
- **Por que es importante?** El contexto correcto = codigo que pasa code review en primer intento

### Vision de la Solucion

**raise.ctx** (RaiSE Context) es el componente que:

1. **Lee** los datos de gobernanza generados por SAR (rules, graph)
2. **Procesa** queries del agente (task + scope)
3. **Traversa** el grafo de forma determinista para encontrar reglas relevantes
4. **Entrega** el Minimum-Viable Context optimizado para context window

**Propuesta de valor**: Dado un task y scope, entregar exactamente las reglas necesarias — ni mas, ni menos.

**Caracteristica clave**: **Determinista** — mismo input siempre produce mismo output.

### CLI

```bash
# Obtener MVC para una tarea especifica
raise ctx get --task "implement user authentication" --scope "src/services/"

# Obtener MVC para un archivo especifico
raise ctx get --file "src/services/AuthService.ts"

# Listar todas las reglas disponibles
raise ctx list

# Ver detalle de una regla
raise ctx show ts-repository-suffix

# Slash command en Claude Code (infiere task del contexto)
/raise.ctx
```

---

## Principio Core: Retrieval Determinista

`raise.ctx` NO es un RAG tradicional basado en embeddings. Es un **sistema de retrieval determinista** basado en:

1. **Matching estructurado** por scope (file patterns, directories)
2. **Traversal de grafo** para reglas relacionadas
3. **Filtering por confidence** threshold

### Por que Determinista?

| RAG Tradicional | raise.ctx |
|-----------------|-----------|
| Embeddings + similarity | Graph traversal + pattern matching |
| Resultados variables | Mismo input = mismo output |
| "Parece relevante" | "Es relevante por scope/relacion" |
| Black box | Auditable y explicable |
| Requiere fine-tuning | Funciona out-of-the-box |

**Beneficio**: Gobernanza verificable. Si una regla se incluye en el MVC, hay una razon explicita (scope match, relacion en grafo, confidence threshold).

---

## Arquitectura: Flujo de Retrieval

### Pipeline de Query

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      raise.ctx PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  INPUT: --task "implement auth service" --scope "src/services/"         │
│                                                                          │
│  STEP 1: SCOPE MATCHING                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Match reglas por:                                                │   │
│  │  - pattern.scope matches "src/services/**"                       │   │
│  │  - tags contienen "services" o "authentication"                  │   │
│  │  - category relevante al task                                     │   │
│  │                                                                   │   │
│  │  Result: primary_rules[] (directly applicable)                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  STEP 2: GRAPH TRAVERSAL                                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Para cada primary_rule, traversar grafo:                        │   │
│  │  - Follow "requires" edges (dependencias)                        │   │
│  │  - Follow "related_to" edges (1 nivel)                          │   │
│  │  - Check "conflicts_with" (warnings)                            │   │
│  │  - Check "supersedes" (deprecations)                            │   │
│  │                                                                   │   │
│  │  Result: context_rules[] (related rules)                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  STEP 3: CONFIDENCE FILTERING                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Apply --min-confidence threshold (default: 0.80)                │   │
│  │  - Filter out rules below threshold                              │   │
│  │  - Keep low-confidence rules in warnings (if advisory)          │   │
│  │                                                                   │   │
│  │  Result: filtered primary_rules[] + context_rules[]             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  STEP 4: MVC ASSEMBLY                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Assemble Minimum-Viable Context:                                │   │
│  │  - primary_rules: full content                                   │   │
│  │  - context_rules: summary + relation                            │   │
│  │  - warnings: conflicts, deprecations, low-confidence            │   │
│  │  - graph_context: relevant subgraph                             │   │
│  │                                                                   │   │
│  │  Apply token budget (default: <4K tokens)                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              ▼                                           │
│  OUTPUT: MVC (YAML/JSON)                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Algoritmo de Graph Traversal

```
function getMVC(task, scope, minConfidence):
    // Step 1: Find primary rules
    primaryRules = rules.filter(r =>
        matchesScope(r.pattern.scope, scope) &&
        r.confidence >= minConfidence
    )

    // Step 2: Traverse graph for context
    contextRules = []
    warnings = []

    for rule in primaryRules:
        // Get required rules (recursive, depth-limited)
        required = graph.traverse(rule.id, "requires", maxDepth=3)
        contextRules.addAll(required)

        // Get related rules (1 level only)
        related = graph.traverse(rule.id, "related_to", maxDepth=1)
        contextRules.addAll(related)

        // Check conflicts
        conflicts = graph.traverse(rule.id, "conflicts_with", maxDepth=1)
        for conflict in conflicts:
            if conflict in primaryRules:
                warnings.add("CONFLICT: {rule.id} conflicts with {conflict.id}")

        // Check deprecations
        superseded = graph.getIncoming(rule.id, "supersedes")
        if superseded:
            warnings.add("DEPRECATED: {rule.id} supersedes {superseded.id}")

    // Step 3: Deduplicate and apply confidence filter
    contextRules = unique(contextRules).filter(r => r.confidence >= minConfidence)

    // Step 4: Assemble MVC
    return MVC(
        task: task,
        scope: scope,
        primary_rules: primaryRules.map(fullContent),
        context_rules: contextRules.map(summary),
        warnings: warnings,
        graph_context: buildSubgraph(primaryRules + contextRules)
    )
```

---

## Output: Minimum-Viable Context (MVC)

### Estructura del MVC

```yaml
# Response from: raise ctx get --task "implement auth" --scope "src/services/"
version: "1.0"
generated_at: "2026-01-28T10:30:00Z"
deterministic: true  # mismo input siempre produce este output

query:
  task: "implement user authentication service"
  scope: "src/services/"
  min_confidence: 0.80

primary_rules:
  - id: ts-service-suffix
    confidence: 0.92
    enforcement: strong
    title: "Service classes must end with 'Service' suffix"
    description: |
      All classes in src/services/ must follow naming pattern: {Name}Service.
    examples:
      positive:
        - code: "export class AuthService { ... }"
      negative:
        - code: "export class AuthHandler { ... }"
          fix: "Rename to AuthService"
    # ... full rule content

  - id: ts-async-error-handling
    confidence: 0.87
    enforcement: moderate
    title: "Async functions must use try-catch with custom errors"
    # ... full rule content

context_rules:
  - id: ts-repository-suffix
    confidence: 0.95
    relation: "ts-service-suffix typically uses repositories"
    summary: "Repository classes end with 'Repository' suffix"
    # summary only, not full content (token efficiency)

  - id: ts-custom-error-classes
    confidence: 0.91
    relation: "ts-async-error-handling requires custom errors"
    summary: "Define AuthError, ValidationError for domain errors"

warnings:
  - type: low_confidence
    rule_id: ts-jwt-pattern
    confidence: 0.72
    message: "JWT pattern has 72% adoption. Consider but don't enforce."

  - type: deprecation
    old_rule: ts-old-auth-pattern
    new_rule: ts-jwt-pattern
    message: "ts-old-auth-pattern is deprecated. Use ts-jwt-pattern."

graph_context:
  nodes:
    - { id: ts-service-suffix, category: naming }
    - { id: ts-async-error-handling, category: patterns }
    - { id: ts-repository-suffix, category: naming }
    - { id: ts-custom-error-classes, category: patterns }
  edges:
    - { from: ts-service-suffix, to: ts-repository-suffix, type: related_to }
    - { from: ts-async-error-handling, to: ts-custom-error-classes, type: requires }

metadata:
  total_rules_evaluated: 47
  primary_rules_returned: 2
  context_rules_returned: 2
  estimated_tokens: 1847
```

### Token Budget Management

El MVC tiene un budget de tokens configurable (default: 4K):

| Seccion | Budget Allocation |
|---------|-------------------|
| primary_rules | 60% (full content) |
| context_rules | 25% (summaries only) |
| warnings | 10% |
| graph_context | 5% |

Si el MVC excede el budget:
1. Reducir context_rules (menos related, keep required)
2. Truncar descriptions de primary_rules
3. Simplificar graph_context

---

## CLI Interface

### Comandos

```bash
# Obtener MVC para task + scope
raise ctx get --task "..." --scope "..."

# Opciones de filtering
raise ctx get --task "..." --min-confidence 0.60  # incluir advisory
raise ctx get --task "..." --include-all          # todo, sin filtrar

# Opciones de output
raise ctx get --task "..." --format yaml          # default
raise ctx get --task "..." --format json
raise ctx get --task "..." --format markdown      # human-readable

# Token budget
raise ctx get --task "..." --max-tokens 2000      # limitar output

# Listar reglas
raise ctx list                                     # todas
raise ctx list --category naming                   # por categoria
raise ctx list --confidence 0.90                   # high confidence only

# Ver regla especifica
raise ctx show ts-repository-suffix
raise ctx show ts-repository-suffix --with-graph   # incluir relaciones
```

### Slash Command (Claude Code)

```
/raise.ctx                           # infiere task del contexto de conversacion
/raise.ctx --scope src/services/     # especificar scope
/raise.ctx --file AuthService.ts     # scope a archivo especifico
```

---

## Integracion con Agentes

### Flujo Tipico

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENTE LLM (Claude Code)                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Usuario pide: "implement user authentication"               │
│                                                                 │
│  2. Agente invoca: /raise.ctx --scope src/services/            │
│                                                                 │
│  3. raise.ctx retorna MVC con reglas relevantes                │
│                                                                 │
│  4. Agente incluye MVC en su contexto                          │
│                                                                 │
│  5. Agente genera codigo siguiendo las reglas                  │
│                                                                 │
│  6. Codigo generado:                                            │
│     - Sigue naming convention (AuthService)                    │
│     - Usa error handling pattern                               │
│     - Inyecta Repository correctamente                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ejemplo de Uso en Prompt

```markdown
## Governance Context (from raise.ctx)

The following rules apply to code in `src/services/`:

### Primary Rules

**ts-service-suffix** (confidence: 92%, enforcement: strong)
Service classes must end with 'Service' suffix.

✅ `export class AuthService { ... }`
❌ `export class AuthHandler { ... }` → Rename to AuthService

**ts-async-error-handling** (confidence: 87%, enforcement: moderate)
Async functions must use try-catch with custom errors.

### Context Rules

- **ts-repository-suffix**: Services typically inject Repositories
- **ts-custom-error-classes**: Define AuthError for domain errors

### Warnings

⚠️ JWT pattern has 72% adoption - consider but don't enforce
```

---

## Metricas de Exito

### Metricas de Retrieval

| Metrica | Target | Descripcion |
|---------|--------|-------------|
| Precision | >95% | Reglas devueltas son relevantes |
| Recall | >90% | No se omiten reglas criticas |
| Latencia | <200ms | Tiempo de respuesta |
| Determinismo | 100% | Mismo input = mismo output |

### Metricas de Impacto

| Metrica | Target | Descripcion |
|---------|--------|-------------|
| Code review pass rate | >80% | Codigo generado con MVC pasa review |
| Token efficiency | <4K | MVC cabe en context window |
| Agent adoption | 100% | Todos los comandos raise.* usan ctx |

---

## Restricciones y Supuestos

### Restricciones Tecnicas

1. **Determinismo**: Mismo query siempre produce mismo MVC
2. **Token Budget**: MVC debe caber en context window razonable
3. **Latencia**: Respuesta en <200ms para no bloquear al agente
4. **Offline**: Debe funcionar sin conexion a internet

### Restricciones de Negocio

1. **No embeddings**: Retrieval estructurado, no semantic search
2. **Explicabilidad**: Cada regla incluida tiene razon explicita
3. **KISS**: Algoritmo de traversal simple y auditable

### Supuestos

1. SAR ha generado datos validos en `.raise/`
2. El grafo tiene relaciones significativas
3. Los agentes pueden procesar MVC en formato YAML

---

## Glosario

| Termino | Definicion |
|---------|------------|
| **raise.ctx** | Componente de entrega de contexto de gobernanza |
| **MVC** | Minimum-Viable Context - conjunto minimo de reglas para una tarea |
| **Retrieval Determinista** | Busqueda basada en reglas, no embeddings |
| **Graph Traversal** | Navegacion del grafo de relaciones entre reglas |
| **Token Budget** | Limite de tokens para el MVC |
| **Primary Rules** | Reglas directamente aplicables al scope |
| **Context Rules** | Reglas relacionadas necesarias para entender las primarias |

---

## Roadmap

### Fase 1: MVP (junto con SAR A3)

- [ ] CLI basico: `raise ctx get --task --scope`
- [ ] Scope matching por file patterns
- [ ] Confidence filtering
- [ ] Output YAML/JSON

### Fase 2: Graph Traversal

- [ ] Implementar traversal de `requires` edges
- [ ] Implementar traversal de `related_to` (1 nivel)
- [ ] Deteccion de conflicts y deprecations
- [ ] Warnings en MVC

### Fase 3: Integracion

- [ ] Slash command `/raise.ctx`
- [ ] Integracion con otros comandos raise.*
- [ ] Token budget management
- [ ] Output markdown para humanos

### Fase 4: Optimizacion

- [ ] Cache de queries frecuentes
- [ ] Indexing para latencia <100ms
- [ ] Metricas de uso

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Documento inicial |

---

*raise.ctx entrega el contexto. Para la generacion de datos, ver [SAR](./solution-vision.md).*
