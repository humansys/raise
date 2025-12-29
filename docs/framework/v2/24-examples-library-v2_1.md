# RaiSE Examples Library
## Ejemplos PrÃ¡cticos de Uso

**VersiÃ³n:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**PropÃ³sito:** Biblioteca de ejemplos concretos para aprender RaiSE.

> **Nota de versiÃ³n 2.0:** Ejemplos actualizados con Validation Gates, Observable Workflow, y MCP. TerminologÃ­a alineada con ontologÃ­a v2.0.

---

## Ejemplo 1: Feature Nueva con Validation Gates

### Contexto
- **Proyecto:** API REST existente en Python
- **Feature:** Agregar endpoint de bÃºsqueda con filtros
- **Estimado:** 2-3 dÃ­as

### Proceso Paso a Paso

#### 1. InicializaciÃ³n (si no existe)
```bash
raise init --agent cursor
raise mcp start  # [v2.0] Iniciar MCP server
```

#### 2. EspecificaciÃ³n
```
/raise.specify Agregar endpoint de bÃºsqueda de productos con filtros por categorÃ­a, precio y disponibilidad
```

**Resultado:** Spec generada en `.raise/specs/FEAT-001-busqueda-productos.md`

#### 3. Validar Gate-Discovery [NUEVO v2.0]
```bash
raise gate check --gate Gate-Discovery --artifact .raise/specs/FEAT-001-busqueda-productos.md
```

**Output:**
```
âœ… Gate-Discovery PASSED
   â”œâ”€ Stakeholders definidos: âœ“
   â”œâ”€ Requisitos funcionales claros: âœ“
   â”œâ”€ NFRs especificados: âœ“
   â””â”€ Criterios de Ã©xito medibles: âœ“
```

#### 4. DiseÃ±o TÃ©cnico
```
/raise.plan @.raise/specs/FEAT-001-busqueda-productos.md
```

**Resultado:** Plan tÃ©cnico con:
- DiseÃ±o de endpoint
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

#### 7. ImplementaciÃ³n con Tracing [NUEVO v2.0]
```
/raise.implement @.raise/tasks/TASK-001.md
```

Cada acciÃ³n se registra automÃ¡ticamente en Observable Workflow.

#### 8. AuditorÃ­a Final [NUEVO v2.0]
```bash
raise audit --session today
```

### Artefactos Generados
```
.raise/
â”œâ”€â”€ memory/
â”‚   â”œâ”€â”€ constitution.md
â”‚   â””â”€â”€ guardrails.json          # [v2.0]
â”œâ”€â”€ traces/
â”‚   â””â”€â”€ 2025-12-28.jsonl         # [v2.0] Observable Workflow
â”œâ”€â”€ specs/
â”‚   â””â”€â”€ FEAT-001-busqueda-productos.md
â”œâ”€â”€ plans/
â”‚   â””â”€â”€ FEAT-001-plan.md
â””â”€â”€ tasks/
    â”œâ”€â”€ TASK-001-modelo-filtros.md
    â”œâ”€â”€ TASK-002-query-builder.md
    â””â”€â”€ ...
```

### Lecciones Aprendidas
- Especificar filtros **antes** de diseÃ±ar evita retrabajos
- Gate-Design detectÃ³ falta de paginaciÃ³n temprano
- Observable Workflow permitiÃ³ ver dÃ³nde se gastaron mÃ¡s tokens

---

## Ejemplo 2: Proyecto Greenfield con MCP

### Contexto
- **Proyecto:** Microservicio desde cero
- **Stack:** Python + FastAPI + PostgreSQL
- **Estimado:** 2 semanas

### Proceso Paso a Paso

#### Fase 0: InicializaciÃ³n con MCP
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
â•­â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•®
â”‚ raise://constitution      Principios del proyecto â”‚
â”‚ raise://guardrails        Guardrails activos       â”‚
â”‚ raise://specs/*           (vacÃ­o)                  â”‚
â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•¯
```

#### Fase 1: Constitution
```
/raise.constitution
```

**Resultado:** Constitution personalizada basada en:
- Stack elegido
- Patrones del equipo
- Restricciones de la organizaciÃ³n

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

#### Fase 5+: IteraciÃ³n con Observable Workflow
Para cada feature del MVP:
1. `/raise.specify`
2. `raise gate check --gate Gate-Discovery`
3. `/raise.plan`
4. `raise gate check --gate Gate-Design`
5. `/raise.tasks`
6. `/raise.implement`
7. `raise gate check --gate Gate-Code`

**AuditorÃ­a semanal:**
```bash
raise audit --period week --format md --output weekly-report.md
```

### Estructura Final
```
my-service/
â”œâ”€â”€ .raise/
â”‚   â”œâ”€â”€ memory/
â”‚   â”‚   â”œâ”€â”€ constitution.md
â”‚   â”‚   â””â”€â”€ guardrails.json
â”‚   â”œâ”€â”€ traces/
â”‚   â”‚   â””â”€â”€ *.jsonl
â”‚   â”œâ”€â”€ specs/
â”‚   â”œâ”€â”€ plans/
â”‚   â””â”€â”€ tasks/
â”œâ”€â”€ src/
â”œâ”€â”€ tests/
â”œâ”€â”€ mcp-config.json           # [v2.0]
â””â”€â”€ pyproject.toml
```

---

## Ejemplo 3: MigraciÃ³n de Proyecto Legacy

### Contexto
- **Proyecto:** Monolito PHP de 5 aÃ±os
- **Objetivo:** Adoptar RaiSE sin rewrite
- **RestricciÃ³n:** No romper funcionalidad existente

### Proceso Paso a Paso

#### 1. AnÃ¡lisis SAR
```bash
raise init --skip-constitution
```

Usar katas SAR:
- `L2-02-Analisis-Agnostico-Codigo-Fuente.md`
- `L2-03-Ecosystem-Discovery.md`

**Resultado:** DocumentaciÃ³n de arquitectura existente

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

**Ejemplo de guardrail extraÃ­do:**
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

#### 4. AdopciÃ³n Gradual con Gates
Para cada nueva feature:
1. Crear spec siguiendo RaiSE â†’ `raise gate check --gate Gate-Discovery`
2. Implementar con validaciÃ³n â†’ `raise gate check --gate Gate-Code`
3. Legacy no tocado

**Observable Workflow para tracking:**
```bash
raise audit --period month --format csv --output adoption-metrics.csv
```

### Lecciones Aprendidas
- **No forzar** cambios en cÃ³digo existente
- Documentar "deuda tÃ©cnica conocida" como guardrails deshabilitados
- Migrar patrones gradualmente

---

## Ejemplo 4: Governance Multi-Proyecto con MCP

### Contexto
- **OrganizaciÃ³n:** 10 equipos, 50+ repos
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
â”œâ”€â”€ guardrails/                # [v2.0] Antes: rules/
â”‚   â”œâ”€â”€ GR-001-naming.mdc
â”‚   â”œâ”€â”€ GR-002-security.mdc
â”‚   â””â”€â”€ ...
â”œâ”€â”€ gates/                     # [v2.0]
â”‚   â”œâ”€â”€ Gate-Discovery.md
â”‚   â”œâ”€â”€ Gate-Design.md
â”‚   â””â”€â”€ ...
â”œâ”€â”€ katas/
â”œâ”€â”€ templates/
â””â”€â”€ raise.yaml
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

#### 3. SincronizaciÃ³n
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
- Compliance automÃ¡tico
- **MÃ©tricas agregadas via Observable Workflow** [v2.0]

---

## Ejemplo 5: Escalation en AcciÃ³n [NUEVO v2.0]

### Contexto
Agente encuentra situaciÃ³n ambigua durante implementaciÃ³n.

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

#### 3. Orquestador Recibe NotificaciÃ³n
```
â•­â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•®
â”‚ âš ï¸ ESCALATION: Gate-Design Failed                          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Reason: Missing authentication strategy                     â”‚
â”‚ Context: Spec defines API endpoints but no auth mechanism   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Options:                                                    â”‚
â”‚ [1] Add JWT authentication section                          â”‚
â”‚ [2] Use existing session-based auth                         â”‚
â”‚ [3] Mark as internal-only API (no auth required)           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Select option (1-3): _                                      â”‚
â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•¯
```

#### 4. DecisiÃ³n Registrada en Observable Workflow
```jsonl
{"timestamp":"...","action":"escalation","gate":"Gate-Design","reason":"Missing auth","decision":"option_1","decided_by":"human"}
```

---

## Anti-Ejemplos: QuÃ© NO Hacer

### Anti-Ejemplo 1: Spec Demasiado Vaga

âŒ **Malo:**
```markdown
# Feature: Mejorar bÃºsqueda
La bÃºsqueda debe ser mejor y mÃ¡s rÃ¡pida.
```

âœ… **Bueno:**
```markdown
# Feature: BÃºsqueda con filtros
## Requisitos Funcionales
- Filtrar por categorÃ­a (lista predefinida)
- Filtrar por rango de precio (min/max)
- Filtrar por disponibilidad (boolean)
## NFRs
- Response time < 200ms para 10k productos
- Soporte de paginaciÃ³n (20 items default)
```

**Por quÃ© falla:** Sin criterios especÃ­ficos, el agente "inventa" y el resultado no cumple expectativas.

**Gate que lo detecta:** Gate-Discovery âŒ

---

### Anti-Ejemplo 2: Saltar Validation Gates [ACTUALIZADO v2.0]

âŒ **Malo:**
```
/raise.implement Crear sistema de autenticaciÃ³n
```

âœ… **Bueno:**
```
/raise.specify Sistema de autenticaciÃ³n con SSO
raise gate check --gate Gate-Discovery
/raise.plan @spec.md
raise gate check --gate Gate-Design
/raise.implement @task-001.md
raise gate check --gate Gate-Code
```

**Por quÃ© falla:** Sin spec/plan, el cÃ³digo carece de contexto y el agente toma decisiones arbitrarias.

---

### Anti-Ejemplo 3: Ignorar Escalations [NUEVO v2.0]

âŒ **Malo:**
Configurar `--no-escalate` para "ir mÃ¡s rÃ¡pido".

âœ… **Bueno:**
Responder a escalations cuando ocurren.

**Por quÃ© falla:** Las decisiones no-documentadas crean deuda tÃ©cnica invisible.

---

### Anti-Ejemplo 4: Aceptar CÃ³digo Sin Revisar

âŒ **Malo:**
Aceptar todo output del agente sin leer.

âœ… **Bueno:**
1. Pedir explicaciÃ³n primero: `/raise.explain`
2. Revisar cÃ³digo generado
3. Solicitar cambios si necesario

**Por quÃ© falla:** Viola principio de HeutagogÃ­a. El humano pierde ownership.

---

### Anti-Ejemplo 5: No Auditar [NUEVO v2.0]

âŒ **Malo:**
Nunca ejecutar `raise audit`.

âœ… **Bueno:**
```bash
# AuditorÃ­a semanal
raise audit --period week --format md > weekly-review.md
```

**Por quÃ© falla:** Sin mÃ©tricas, no hay mejora continua (Kaizen).

---

## Patrones Recomendados

### PatrÃ³n: Explicabilidad Primero
```
Antes de implementar X, explÃ­came:
1. Tu enfoque propuesto
2. Alternativas consideradas
3. Trade-offs
```

### PatrÃ³n: Gate-Driven Development [NUEVO v2.0]
```bash
# Antes de cada transiciÃ³n de fase
raise gate check --gate Gate-{fase_actual}
```

### PatrÃ³n: Observable Sessions [NUEVO v2.0]
```bash
# Al inicio de sesiÃ³n de trabajo
raise mcp start

# Al final de sesiÃ³n
raise audit --session today
```

### PatrÃ³n: IteraciÃ³n con Contexto
```
Dado el feedback anterior, ajusta el diseÃ±o para [cambio especÃ­fico].
```

### PatrÃ³n: Escalation-Conscious [NUEVO v2.0]
```
Si encuentras ambigÃ¼edad en la spec, escala con:
1. El problema especÃ­fico
2. Opciones que has considerado
3. Tu recomendaciÃ³n (si tienes una)
```

---

## Changelog

### v2.1.0 (2025-12-28)
- **ACTUALIZADO**: Ejemplo 1 con Validation Gates
- **ACTUALIZADO**: Ejemplo 2 con MCP server
- **ACTUALIZADO**: Ejemplo 3 con guardrails
- **ACTUALIZADO**: Ejemplo 4 con CI/CD gates y audit
- **NUEVO**: Ejemplo 5 (Escalation en AcciÃ³n)
- **ACTUALIZADO**: Anti-ejemplos con Gates y Observable Workflow
- **NUEVO**: Patrones Gate-Driven y Observable Sessions

### v1.0.0 (2025-12-27)
- Release inicial

---

*Esta biblioteca crece con cada nuevo patrÃ³n aprendido. Ver [23-commands-reference-v2.md](./23-commands-reference-v2.md) para comandos.*
