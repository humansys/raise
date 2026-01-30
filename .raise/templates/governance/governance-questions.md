# Governance Questions Catalog

> **Purpose**: Guía de preguntas para derivar guardrails durante la ejecución del kata `setup/governance`.

---

## Cómo Usar Este Catálogo

1. Recorrer cada categoría en orden
2. Para cada pregunta, determinar:
   - **Respuesta** (lo que aplica al proyecto)
   - **Nivel** (MUST/SHOULD/MAY)
   - **Fuente** (Vision, código existente, decisión de equipo)
3. Convertir respuestas en guardrails usando el template `.mdc`

---

## Categoría 1: Arquitectura

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| A1 | ¿Qué patrón de arquitectura se usa? | Clean, Hexagonal, Layered, Modular Monolith, Microservices | Clean Architecture |
| A2 | ¿Cómo se organizan los módulos/features? | Por feature, por capa, por dominio | Por feature |
| A3 | ¿Qué nivel de acoplamiento se permite entre módulos? | Ninguno, vía interfaces, vía eventos | Vía interfaces |
| A4 | ¿Se permite dependencia de frameworks en el dominio? | No (Clean), Sí (pragmático) | No |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| A5 | ¿Cómo se manejan las dependencias cross-cutting (logging, auth)? | Inyección de dependencias vs decoradores |
| A6 | ¿Existe un Domain Model separado de los DTOs? | Separación de concerns |
| A7 | ¿Cómo se comunican los bounded contexts? | Eventos, APIs, shared kernel |

### Guardrails Típicos

```
MUST-ARCH-001: Seguir Clean Architecture (capas: domain, application, infrastructure)
SHOULD-ARCH-002: Organizar código por features, no por capas técnicas
MAY-ARCH-003: Usar Domain Events para comunicación entre bounded contexts
```

---

## Categoría 2: Testing

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| T1 | ¿Qué cobertura mínima de tests se requiere? | 60%, 70%, 80%, 90% | 80% |
| T2 | ¿Qué tipos de tests son obligatorios? | Unit, Integration, E2E | Unit + Integration |
| T3 | ¿Se requiere TDD? | Siempre, para lógica crítica, nunca | Para lógica crítica |
| T4 | ¿Qué framework de testing se usa? | Jest, Vitest, Pytest, JUnit | Depende del stack |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| T5 | ¿Cómo se mockean dependencias externas? | Mocks, stubs, fakes, in-memory |
| T6 | ¿Se requieren tests de contrato para APIs? | Consumer-driven contracts |
| T7 | ¿Hay tests de performance/carga? | Baseline de performance |
| T8 | ¿Qué patrón de test se sigue? | AAA, Given-When-Then, describe/it |

### Guardrails Típicos

```
MUST-TEST-001: Cobertura de tests >= 80%
SHOULD-TEST-002: Todo código nuevo requiere tests correspondientes
SHOULD-TEST-003: Usar patrón AAA (Arrange-Act-Assert) en tests
MAY-TEST-004: Tests de integración para cada endpoint de API
```

---

## Categoría 3: Seguridad

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| S1 | ¿Qué mecanismo de autenticación se usa? | JWT, OAuth2, Session, API Keys | JWT + OAuth2 |
| S2 | ¿Cómo se maneja la autorización? | RBAC, ABAC, Claims-based | RBAC |
| S3 | ¿Cómo se manejan los secrets? | Env vars, Vault, AWS Secrets | Env vars (dev), Vault (prod) |
| S4 | ¿Se requiere HTTPS? | Siempre, solo producción | Siempre |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| S5 | ¿Cómo se validan inputs? | Schema validation, sanitization |
| S6 | ¿Hay auditoría de acciones sensibles? | Audit log |
| S7 | ¿Qué headers de seguridad se requieren? | CORS, CSP, HSTS |
| S8 | ¿Cómo se manejan datos sensibles (PII)? | Encryption at rest/transit |

### Guardrails Típicos

```
MUST-SEC-001: Autenticación JWT para todos los endpoints protegidos
MUST-SEC-002: Validación de input en todos los endpoints
SHOULD-SEC-003: Audit log para operaciones de escritura
MAY-SEC-004: Rate limiting en endpoints públicos
```

---

## Categoría 4: API

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| P1 | ¿Qué estilo de API se usa? | REST, GraphQL, gRPC, tRPC | REST |
| P2 | ¿Cómo se versiona la API? | URL (/v1/), Header, Query param | URL path |
| P3 | ¿Se requiere documentación OpenAPI/Swagger? | Sí, No | Sí |
| P4 | ¿Qué formato de respuesta estándar? | JSON:API, HAL, custom | Custom consistente |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| P5 | ¿Cómo se manejan errores en la API? | RFC 7807, custom format |
| P6 | ¿Se usa paginación? ¿Qué tipo? | Offset, cursor, keyset |
| P7 | ¿Hay rate limiting? | Por usuario, por IP, global |
| P8 | ¿Cómo se manejan operaciones asíncronas? | Polling, webhooks, SSE |

### Guardrails Típicos

```
MUST-API-001: Documentación OpenAPI para todos los endpoints
MUST-API-002: Versionado de API en URL path (/v1/, /v2/)
SHOULD-API-003: Formato de error consistente con RFC 7807
MAY-API-004: Paginación cursor-based para colecciones
```

---

## Categoría 5: Código

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| C1 | ¿Qué estilo de código se sigue? | Guía del lenguaje, Airbnb, Google | Guía estándar del lenguaje |
| C2 | ¿Se usa linting? ¿Qué reglas? | ESLint, Prettier, Biome | ESLint + Prettier |
| C3 | ¿Se usan tipos estrictos? | TypeScript strict, MyPy strict | Sí |
| C4 | ¿Convención de naming? | camelCase, snake_case, kebab | Por lenguaje |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| C5 | ¿Longitud máxima de funciones? | Lines of code limit |
| C6 | ¿Complejidad ciclomática máxima? | Cognitive complexity limit |
| C7 | ¿Se prohíben ciertos patrones? | any, eval, magic numbers |
| C8 | ¿Se requieren comentarios de documentación? | JSDoc, docstrings |

### Guardrails Típicos

```
MUST-CODE-001: TypeScript strict mode habilitado
SHOULD-CODE-002: ESLint sin warnings en código nuevo
SHOULD-CODE-003: Funciones <= 50 líneas
MAY-CODE-004: JSDoc para funciones públicas
```

---

## Categoría 6: Manejo de Errores

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| E1 | ¿Cómo se estructuran los errores? | Error classes, error codes, Result type | Error classes |
| E2 | ¿Qué se loggea en errores? | Stack trace, context, user info | Context sin PII |
| E3 | ¿Cómo se propagan errores? | Throw, Result/Either, callbacks | Throw + boundaries |
| E4 | ¿Hay error boundaries? | Por layer, por feature, global | Por feature |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| E5 | ¿Cómo se manejan errores de terceros? | Wrap, rethrow, transform |
| E6 | ¿Hay retry logic? ¿Para qué operaciones? | Transient failures |
| E7 | ¿Cómo se alertan errores críticos? | Logging, alerting, on-call |
| E8 | ¿Hay graceful degradation? | Fallbacks, circuit breakers |

### Guardrails Típicos

```
MUST-ERR-001: Error boundaries en cada feature/módulo
SHOULD-ERR-002: Errores loggeados con correlation ID
SHOULD-ERR-003: No exponer stack traces en producción
MAY-ERR-004: Circuit breaker para llamadas a servicios externos
```

---

## Categoría 7: Documentación

### Preguntas Core

| # | Pregunta | Opciones Comunes | Default Sugerido |
|---|----------|------------------|------------------|
| D1 | ¿Qué decisiones se documentan con ADR? | Arquitectónicas, todas, ninguna | Arquitectónicas |
| D2 | ¿Dónde vive la documentación? | docs/, wiki, Confluence | docs/ en repo |
| D3 | ¿Se requiere README por módulo? | Sí, no, solo complejos | Solo complejos |
| D4 | ¿Se documentan APIs? | OpenAPI, manual, auto-generated | OpenAPI auto |

### Preguntas de Profundidad

| # | Pregunta | Impacto |
|---|----------|---------|
| D5 | ¿Hay diagrams as code? | Mermaid, PlantUML, C4 |
| D6 | ¿Se mantiene un changelog? | CHANGELOG.md, releases |
| D7 | ¿Documentación en código o externa? | Inline, separate docs |
| D8 | ¿Se documenta el onboarding? | Getting started guide |

### Guardrails Típicos

```
SHOULD-DOC-001: ADR para decisiones arquitectónicas significativas
SHOULD-DOC-002: Diagramas C4 para arquitectura de alto nivel
MAY-DOC-003: README.md en módulos con lógica compleja
MAY-DOC-004: CHANGELOG.md actualizado con cada release
```

---

## Proceso de Derivación

### 1. Recorrer Preguntas

Para cada categoría:
```
Pregunta → Respuesta → ¿Nivel? → ¿Excepción? → Guardrail
```

### 2. Priorizar

Orden de implementación:
1. **MUST** de Seguridad (S1-S4)
2. **MUST** de Arquitectura (A1-A4)
3. **MUST** de Testing (T1-T2)
4. **SHOULD** por categoría
5. **MAY** según necesidad

### 3. Validar Consistencia

Verificar que:
- No hay contradicciones entre guardrails
- Los niveles reflejan el impacto real
- Las excepciones están documentadas

---

## Adaptación por Dominio

### Fintech
Agregar preguntas sobre:
- Compliance (PCI-DSS, SOX)
- Auditoría transaccional
- Idempotencia en operaciones

### Healthcare
Agregar preguntas sobre:
- HIPAA compliance
- Encryption de PHI
- Access control granular

### E-commerce
Agregar preguntas sobre:
- PCI compliance para pagos
- Manejo de inventario
- Consistencia eventual vs fuerte

---

*Template version: 1.0.0*
*Based on: ADR-009 Continuous Governance Model*
