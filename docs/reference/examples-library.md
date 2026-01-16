# RaiSE Examples Library
## Ejemplos Prácticos de Uso

**Versión:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**Propósito:** Biblioteca de ejemplos concretos para aprender RaiSE.

> **Nota de versión 2.0:** Ejemplos actualizados con Validation Gates, Observable Workflow, y MCP. Terminología alineada con ontología v2.0.

---

## Ejemplo 1: Feature Nueva con Validation Gates

### Contexto
- **Proyecto:** API REST existente en Python
- **Feature:** Agregar endpoint de búsqueda con filtros
- **Estimado:** 2-3 días

### Proceso Paso a Paso

#### 1. Inicialización (si no existe)
```bash
raise init --agent cursor
raise mcp start  # [v2.0] Iniciar MCP server
```

#### 2. Especificación
```
/raise.specify Agregar endpoint de búsqueda de productos con filtros por categoría, precio y disponibilidad
```

**Resultado:** Spec generada en `.raise/specs/FEAT-001-busqueda-productos.md`

#### 3. Validar Gate-Discovery [NUEVO v2.0]
```bash
raise gate check --gate Gate-Discovery --artifact .raise/specs/FEAT-001-busqueda-productos.md
```

**Output:**
```
✅ Gate-Discovery PASSED
   ├─ Stakeholders definidos: ✓
   ├─ Requisitos funcionales claros: ✓
   ├─ NFRs especificados: ✓
   └─ Criterios de éxito medibles: ✓
```

#### 4. Diseño Técnico
```
/raise.plan @.raise/specs/FEAT-001-busqueda-productos.md
```

**Resultado:** Plan técnico con:
- Diseño de endpoint
- Query parameters
- Modelo de response
- Consideraciones de performance

#### 5. Validar Gate-Design [NUEVO v2.0]
```
/raise.gate Gate-Design
```

#### 6. Tareas
```
/raise.tasks @.raise/plans/FEAT-001-plan.md
```

**Resultado:**
1. Crear modelo de filtros
2. Implementar query builder
3. Crear endpoint controller
4. Agregar tests
5. Documentar API

#### 7. Implementación con Tracing [NUEVO v2.0]
```
/raise.implement @.raise/tasks/TASK-001.md
```

Cada acción se registra automáticamente en Observable Workflow.

#### 8. Auditoría Final [NUEVO v2.0]
```bash
raise audit --session today
```

### Artefactos Generados
```
.raise/
├── memory/
│   ├── constitution.md
│   └── guardrails.json          # [v2.0]
├── traces/
│   └── 2025-12-28.jsonl         # [v2.0] Observable Workflow
├── specs/
│   └── FEAT-001-busqueda-productos.md
├── plans/
│   └── FEAT-001-plan.md
└── tasks/
    ├── TASK-001-modelo-filtros.md
    ├── TASK-002-query-builder.md
    └── ...
```

### Lecciones Aprendidas
- Especificar filtros **antes** de diseñar evita retrabajos
- Gate-Design detectó falta de paginación temprano
- Observable Workflow permitió ver dónde se gastaron más tokens

---

## Ejemplo 2: Proyecto Greenfield con MCP

### Contexto
- **Proyecto:** Microservicio desde cero
- **Stack:** Python + FastAPI + PostgreSQL
- **Estimado:** 2 semanas

### Proceso Paso a Paso

#### Fase 0: Inicialización con MCP
```bash
mkdir my-service && cd my-service
raise init --template microservice
raise mcp start --daemon  # MCP server en background
```

**Verificar recursos MCP:**
```bash
raise mcp resources
```

**Output:**
```
╭──────────────────────────────────────────────────────╮
│ raise://constitution      Principios del proyecto    │
│ raise://guardrails        Guardrails activos         │
│ raise://specs/*           (vacío)                    │
╰──────────────────────────────────────────────────────╯
```

#### Fase 1: Constitution
```
/raise.constitution
```

**Resultado:** Constitution personalizada basada en:
- Stack elegido
- Patrones del equipo
- Restricciones de la organización

#### Fase 2: PRD
Usar template `project_requirements.md`:
- Definir problema y objetivos
- Identificar stakeholders
- Establecer NFRs

**Validar:**
```bash
raise gate check --gate Gate-Context
```

#### Fase 3: Solution Vision
```
/raise.specify --template solution-vision
```

**Validar:**
```bash
raise gate check --gate Gate-Vision
```

#### Fase 4: Tech Design
```
/raise.plan --template tech-design
```

**Validar:**
```bash
raise gate check --gate Gate-Design
```

#### Fase 5+: Iteración con Observable Workflow
Para cada feature del MVP:
1. `/raise.specify`
2. `raise gate check --gate Gate-Discovery`
3. `/raise.plan`
4. `raise gate check --gate Gate-Design`
5. `/raise.tasks`
6. `/raise.implement`
7. `raise gate check --gate Gate-Code`

**Auditoría semanal:**
```bash
raise audit --period week --format md --output weekly-report.md
```

### Estructura Final
```
my-service/
├── .raise/
│   ├── memory/
│   │   ├── constitution.md
│   │   └── guardrails.json
│   ├── traces/
│   │   └── *.jsonl
│   ├── specs/
│   ├── plans/
│   └── tasks/
├── src/
├── tests/
├── mcp-config.json           # [v2.0]
└── pyproject.toml
```

---

## Ejemplo 3: Migración de Proyecto Legacy

### Contexto
- **Proyecto:** Monolito PHP de 5 años
- **Objetivo:** Adoptar RaiSE sin rewrite
- **Restricción:** No romper funcionalidad existente

### Proceso Paso a Paso

#### 1. Análisis SAR
```bash
raise init --skip-constitution
```

Usar katas SAR:
- `L2-02-Analisis-Agnostico-Codigo-Fuente.md`
- `L2-03-Ecosystem-Discovery.md`

**Resultado:** Documentación de arquitectura existente

#### 2. Constitution Basada en Legado
```
/raise.constitution --analyze-existing
```

**Importante:** La constitution **respeta** patrones existentes, no impone nuevos.

#### 3. Guardrails desde Patrones [ACTUALIZADO v2.0]
Extraer guardrails de patrones detectados:
```bash
raise guardrail add --file custom/php-naming.mdc
raise guardrail add --file custom/directory-structure.mdc
```

**Ejemplo de guardrail extraído:**
```markdown
---
id: "GR-PHP-001"
scope: code
severity: warning
---

# Naming Convention: Controllers

## Regla
Los controllers deben terminar en `Controller.php` y usar PascalCase.

## Ejemplo Correcto
```php
class ProductController extends BaseController
```
```

#### 4. Adopción Gradual con Gates
Para cada nueva feature:
1. Crear spec siguiendo RaiSE → `raise gate check --gate Gate-Discovery`
2. Implementar con validación → `raise gate check --gate Gate-Code`
3. Legacy no tocado

**Observable Workflow para tracking:**
```bash
raise audit --period month --format csv --output adoption-metrics.csv
```

### Lecciones Aprendidas
- **No forzar** cambios en código existente
- Documentar "deuda técnica conocida" como guardrails deshabilitados
- Migrar patrones gradualmente

---

## Ejemplo 4: Governance Multi-Proyecto con MCP

### Contexto
- **Organización:** 10 equipos, 50+ repos
- **Objetivo:** Governance centralizada
- **Rol:** Platform team

### Proceso Paso a Paso

#### 1. Crear raise-config Central
```bash
mkdir org-raise-config && cd org-raise-config
raise init --template config-repo
```

Estructura [ACTUALIZADO v2.0]:
```
org-raise-config/
├── guardrails/                # [v2.0] Antes: rules/
│   ├── GR-001-naming.mdc
│   ├── GR-002-security.mdc
│   └── ...
├── gates/                     # [v2.0]
│   ├── Gate-Discovery.md
│   ├── Gate-Design.md
│   └── ...
├── katas/
├── templates/
└── raise.yaml
```

#### 2. Configurar Repos
En cada repo:
```yaml
# raise.yaml
config:
  repo: https://github.com/org/org-raise-config.git
  branch: main
mcp:
  enabled: true                # [v2.0]
observable:
  enabled: true                # [v2.0]
  retention_days: 30
```

#### 3. Sincronización
```bash
raise pull
raise mcp start  # Iniciar MCP con config centralizado
```

#### 4. CI/CD Enforcement [ACTUALIZADO v2.0]
```yaml
# .github/workflows/raise.yml
name: RaiSE Governance
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install raise-kit
      
      - name: Hydrate Guardrails
        run: raise pull
      
      - name: Check Guardrails
        run: raise check --format json --strict
      
      - name: Validate Required Gates
        run: |
          raise gate check --gate Gate-Discovery || true
          raise gate check --gate Gate-Design || true
          raise gate check --gate Gate-Code
      
      - name: Export Audit
        if: always()
        run: raise audit --format json --output audit.json
      
      - uses: actions/upload-artifact@v4
        with:
          name: raise-audit
          path: audit.json
```

### Beneficios
- Una fuente de verdad para guardrails y gates
- Updates sin tocar repos
- Compliance automático
- **Métricas agregadas via Observable Workflow** [v2.0]

---

## Ejemplo 5: Escalation en Acción [NUEVO v2.0]

### Contexto
Agente encuentra situación ambigua durante implementación.

### Flujo de Escalation

#### 1. Agente Detecta Problema
```json
{
  "tool": "validate_gate",
  "parameters": {
    "gate": "Gate-Design",
    "artifact": "spec.md"
  }
}
```

**Respuesta:**
```json
{
  "status": "failed",
  "criteria": [
    {"name": "Security considerations", "passed": false, "gap": "No authentication strategy defined"}
  ],
  "escalation_required": true
}
```

#### 2. Agente Escala
```json
{
  "tool": "escalate",
  "parameters": {
    "reason": "Gate-Design failed: Missing authentication strategy",
    "context": "Spec defines API endpoints but no auth mechanism",
    "options": [
      "Add JWT authentication section",
      "Use existing session-based auth",
      "Mark as internal-only API (no auth required)"
    ]
  }
}
```

#### 3. Orquestador Recibe Notificación
```
╭───────────────────────────────────────────────────────╮
│ ⚠️ ESCALATION: Gate-Design Failed                     │
├───────────────────────────────────────────────────────┤
│ Reason: Missing authentication strategy               │
│ Context: Spec defines API endpoints but no auth...    │
├───────────────────────────────────────────────────────┤
│ Options:                                              │
│ [1] Add JWT authentication section                    │
│ [2] Use existing session-based auth                   │
│ [3] Mark as internal-only API (no auth required)     │
├───────────────────────────────────────────────────────┤
│ Select option (1-3): _                                │
╰───────────────────────────────────────────────────────╯
```

#### 4. Decisión Registrada en Observable Workflow
```jsonl
{"timestamp":"...","action":"escalation","gate":"Gate-Design","reason":"Missing auth","decision":"option_1","decided_by":"human"}
```

---

## Anti-Ejemplos: Qué NO Hacer

### Anti-Ejemplo 1: Spec Demasiado Vaga

❌ **Malo:**
```markdown
# Feature: Mejorar búsqueda
La búsqueda debe ser mejor y más rápida.
```

✅ **Bueno:**
```markdown
# Feature: Búsqueda con filtros
## Requisitos Funcionales
- Filtrar por categoría (lista predefinida)
- Filtrar por rango de precio (min/max)
- Filtrar por disponibilidad (boolean)
## NFRs
- Response time < 200ms para 10k productos
- Soporte de paginación (20 items default)
```

**Por qué falla:** Sin criterios específicos, el agente "inventa" y el resultado no cumple expectativas.

**Gate que lo detecta:** Gate-Discovery ❌

---

### Anti-Ejemplo 2: Saltar Validation Gates [ACTUALIZADO v2.0]

❌ **Malo:**
```
/raise.implement Crear sistema de autenticación
```

✅ **Bueno:**
```
/raise.specify Sistema de autenticación con SSO
raise gate check --gate Gate-Discovery
/raise.plan @spec.md
raise gate check --gate Gate-Design
/raise.implement @task-001.md
raise gate check --gate Gate-Code
```

**Por qué falla:** Sin spec/plan, el código carece de contexto y el agente toma decisiones arbitrarias.

---

### Anti-Ejemplo 3: Ignorar Escalations [NUEVO v2.0]

❌ **Malo:**
Configurar `--no-escalate` para "ir más rápido".

✅ **Bueno:**
Responder a escalations cuando ocurren.

**Por qué falla:** Las decisiones no-documentadas crean deuda técnica invisible.

---

### Anti-Ejemplo 4: Aceptar Código Sin Revisar

❌ **Malo:**
Aceptar todo output del agente sin leer.

✅ **Bueno:**
1. Pedir explicación primero: `/raise.explain`
2. Revisar código generado
3. Solicitar cambios si necesario

**Por qué falla:** Viola principio de Heutagogía. El humano pierde ownership.

---

### Anti-Ejemplo 5: No Auditar [NUEVO v2.0]

❌ **Malo:**
Nunca ejecutar `raise audit`.

✅ **Bueno:**
```bash
# Auditoría semanal
raise audit --period week --format md > weekly-review.md
```

**Por qué falla:** Sin métricas, no hay mejora continua (Kaizen).

---

## Patrones Recomendados

### Patrón: Explicabilidad Primero
```
Antes de implementar X, explícame:
1. Tu enfoque propuesto
2. Alternativas consideradas
3. Trade-offs
```

### Patrón: Gate-Driven Development [NUEVO v2.0]
```bash
# Antes de cada transición de fase
raise gate check --gate Gate-{fase_actual}
```

### Patrón: Observable Sessions [NUEVO v2.0]
```bash
# Al inicio de sesión de trabajo
raise mcp start

# Al final de sesión
raise audit --session today
```

### Patrón: Iteración con Contexto
```
Dado el feedback anterior, ajusta el diseño para [cambio específico].
```

### Patrón: Escalation-Conscious [NUEVO v2.0]
```
Si encuentras ambigüedad en la spec, escala con:
1. El problema específico
2. Opciones que has considerado
3. Tu recomendación (si tienes una)
```

---

## Changelog

### v2.1.0 (2025-12-28)
- **ACTUALIZADO**: Ejemplo 1 con Validation Gates
- **ACTUALIZADO**: Ejemplo 2 con MCP server
- **ACTUALIZADO**: Ejemplo 3 con guardrails
- **ACTUALIZADO**: Ejemplo 4 con CI/CD gates y audit
- **NUEVO**: Ejemplo 5 (Escalation en Acción)
- **ACTUALIZADO**: Anti-ejemplos con Gates y Observable Workflow
- **NUEVO**: Patrones Gate-Driven y Observable Sessions

### v1.0.0 (2025-12-27)
- Release inicial

---

*Esta biblioteca crece con cada nuevo patrón aprendido. Ver [23-commands-reference-v2.md](./23-commands-reference-v2.md) para comandos.*
