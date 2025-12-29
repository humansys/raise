# RaiSE Commands Reference
## Referencia de Comandos CLI y Slash Commands

**Versión:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Documentar comandos disponibles para usuarios y agentes.

> **Nota de versión 2.0:** Esta versión añade comandos para Validation Gates, Observable Workflow, y MCP. Terminología actualizada: guardrails, gates.

---

## CLI Commands (raise-kit)

### Comandos Core

| Comando | Propósito | Estado |
|---------|-----------|--------|
| `raise init` | Inicializar proyecto | ✅ v1.0 |
| `raise hydrate` | Sincronizar guardrails | ✅ v1.0 |
| `raise check` | Validar proyecto | ✅ v1.0 |
| `raise validate` | Ejecutar katas | ✅ v1.0 |
| `raise generate` | Generar artefactos | ✅ v1.0 |
| **`raise gate`** | Validar Validation Gates | ✅ v2.0 |
| **`raise mcp`** | Gestionar MCP server | ✅ v2.0 |
| **`raise audit`** | Observable Workflow | ✅ v2.0 |
| **`raise guardrail`** | Gestionar guardrails | ✅ v2.0 |

---

### raise init

Inicializa un proyecto con estructura RaiSE.

**Sintaxis:**
```bash
raise init [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--agent <nombre>` | Agente objetivo | auto-detect |
| `--template <nombre>` | Template de proyecto | standard |
| `--config <url>` | URL de raise-config | default repo |
| `--skip-hydrate` | No sincronizar guardrails | false |
| **`--mcp`** | Inicializar MCP server | true [v2.0] |

**Ejemplos:**
```bash
# Inicialización básica
raise init

# Con agente específico
raise init --agent cursor

# Con template enterprise
raise init --agent copilot --template enterprise

# Sin MCP server (legacy mode)
raise init --no-mcp
```

**Resultado:**
```
.raise/
├── memory/
│   ├── constitution.md
│   └── guardrails.json         # [v2.0] antes: raise-rules.json
├── traces/                      # [v2.0] Observable Workflow
├── raise.yaml
├── mcp-config.json              # [v2.0] MCP server config
└── README.md
```

---

### raise hydrate

Sincroniza guardrails desde el repositorio central.

**Sintaxis:**
```bash
raise hydrate [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--config <url>` | URL de raise-config | desde raise.yaml |
| `--branch <nombre>` | Branch a sincronizar | main |
| `--force` | Sobrescribir cambios locales | false |
| **`--guardrails-only`** | Solo sincronizar guardrails | false [v2.0] |

**Ejemplos:**
```bash
# Sincronizar desde config default
raise hydrate

# Desde branch específico
raise hydrate --branch develop

# Solo guardrails (rápido)
raise hydrate --guardrails-only
```

**Resultado:**
- Actualiza `.raise/memory/guardrails.json`
- Sincroniza katas
- Actualiza templates
- Regenera MCP resources [v2.0]

---

### raise check

Valida el proyecto contra los guardrails activos.

**Sintaxis:**
```bash
raise check [ruta] [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--guardrails <ids>` | Solo validar guardrails específicos | todos |
| `--fix` | Intentar corrección automática | false |
| `--format <fmt>` | Formato de salida (text/json) | text |
| `--strict` | Fallar en warnings | false |
| **`--trace`** | Registrar en Observable Workflow | true [v2.0] |

**Ejemplos:**
```bash
# Validar proyecto completo
raise check

# Validar archivo específico
raise check src/main.py

# Solo ciertos guardrails
raise check --guardrails GR-001,GR-002

# Output JSON para CI, sin traces
raise check --format json --strict --no-trace
```

**Exit codes:**
| Código | Significado |
|--------|-------------|
| 0 | Sin errores |
| 1 | Errores encontrados |
| 2 | Warnings (con --strict) |

---

### raise gate [NUEVO v2.0]

Valida Validation Gates del flujo de trabajo.

**Sintaxis:**
```bash
raise gate <subcommand> [opciones]
```

**Subcomandos:**
| Subcommand | Descripción |
|------------|-------------|
| `check` | Validar un gate específico |
| `list` | Listar gates disponibles |
| `status` | Estado de gates del proyecto |
| `pass` | Marcar gate como pasado (manual) |

**Opciones para `raise gate check`:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--gate <nombre>` | Gate a validar | requerido |
| `--artifact <ruta>` | Artefacto a validar | auto-detect |
| `--escalate` | Escalar a humano si falla | true |
| `--output <ruta>` | Guardar checklist | stdout |

**Ejemplos:**
```bash
# Validar Gate-Design
raise gate check --gate Gate-Design --artifact specs/FEAT-123-design.md

# Listar gates disponibles
raise gate list

# Ver estado de todos los gates
raise gate status

# Marcar gate como pasado manualmente
raise gate pass --gate Gate-Vision --reason "Aprobado en reunión"
```

**Output ejemplo:**
```
╭──────────────────────────────────────────────────────────────╮
│ Gate-Design Validation                                       │
├──────────────────────────────────────────────────────────────┤
│ ✅ Arquitectura de componentes definida                      │
│ ✅ Contratos de API especificados                           │
│ ❌ Modelo de datos incompleto (falta esquema de usuarios)   │
│ ⚠️ Consideraciones de seguridad pendientes                  │
├──────────────────────────────────────────────────────────────┤
│ Status: FAILED (2/4 criterios)                              │
│ Action: Escalation triggered → Orquestador notificado       │
╰──────────────────────────────────────────────────────────────╯
```

---

### raise mcp [NUEVO v2.0]

Gestiona el servidor MCP de RaiSE.

**Sintaxis:**
```bash
raise mcp <subcommand> [opciones]
```

**Subcomandos:**
| Subcommand | Descripción |
|------------|-------------|
| `start` | Iniciar MCP server |
| `stop` | Detener MCP server |
| `status` | Estado del server |
| `resources` | Listar resources disponibles |
| `tools` | Listar tools disponibles |
| `test` | Probar conexión con agente |

**Opciones para `raise mcp start`:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--port <número>` | Puerto del server | 3000 |
| `--transport <tipo>` | Transport (stdio/sse) | stdio |
| `--daemon` | Ejecutar en background | false |

**Ejemplos:**
```bash
# Iniciar MCP server
raise mcp start

# Iniciar en background con SSE
raise mcp start --transport sse --daemon

# Ver resources disponibles
raise mcp resources

# Probar conexión
raise mcp test --agent claude
```

**Output de `raise mcp resources`:**
```
╭────────────────────────────────────────────────────────────╮
│ Available MCP Resources                                    │
├────────────────────────────────────────────────────────────┤
│ raise://constitution      Constitution del proyecto        │
│ raise://guardrails        Guardrails activos (JSON)        │
│ raise://specs/*           Especificaciones del proyecto    │
│ raise://gates/Gate-Design Definición de Gate-Design        │
╰────────────────────────────────────────────────────────────╯
```

**Output de `raise mcp tools`:**
```
╭────────────────────────────────────────────────────────────╮
│ Available MCP Tools                                        │
├────────────────────────────────────────────────────────────┤
│ validate_gate     Valida un Validation Gate                │
│ check_guardrail   Valida contra un guardrail específico    │
│ escalate          Escala decisión a Orquestador            │
│ log_trace         Registra evento en Observable Workflow   │
╰────────────────────────────────────────────────────────────╯
```

---

### raise audit [NUEVO v2.0]

Audita y reporta Observable Workflow.

**Sintaxis:**
```bash
raise audit [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--session <id>` | Session específica | última |
| `--period <range>` | Período (today/week/month) | today |
| `--format <fmt>` | Formato (text/json/md/csv) | text |
| `--output <ruta>` | Guardar reporte | stdout |
| `--metrics` | Incluir métricas agregadas | true |

**Ejemplos:**
```bash
# Auditoría de hoy
raise audit

# Última semana en Markdown
raise audit --period week --format md --output report.md

# Métricas de sesión específica
raise audit --session sess_abc123 --metrics

# Export para análisis externo
raise audit --period month --format csv --output traces.csv
```

**Output ejemplo:**
```
╭──────────────────────────────────────────────────────────────╮
│ Observable Workflow Audit - 2025-12-28                       │
├──────────────────────────────────────────────────────────────┤
│ Sessions: 3                                                  │
│ Total Actions: 47                                            │
│ Gates Validated: 8 (passed: 6, failed: 2)                   │
│ Escalations: 2 (4.2%)                                       │
├──────────────────────────────────────────────────────────────┤
│ Metrics                                                      │
│ ├─ Re-prompting Rate: 2.1 (target: <3) ✅                   │
│ ├─ Token Usage: 45,230                                      │
│ ├─ Avg Gate Validation: 1.8s                                │
│ └─ Escalation Rate: 4.2% (target: 10-15%) ⚠️ bajo           │
├──────────────────────────────────────────────────────────────┤
│ Top Guardrails Triggered                                     │
│ ├─ GR-005 Max File Length: 12 times                         │
│ ├─ GR-002 Documentation Required: 8 times                   │
│ └─ GR-011 Test Coverage: 5 times                            │
╰──────────────────────────────────────────────────────────────╯
```

---

### raise guardrail [NUEVO v2.0]

Gestiona guardrails del proyecto.

> **Nota:** `raise rule` permanece como alias para compatibilidad.

**Sintaxis:**
```bash
raise guardrail <subcommand> [opciones]
```

**Subcomandos:**
| Subcommand | Descripción |
|------------|-------------|
| `list` | Listar guardrails activos |
| `show` | Mostrar detalle de guardrail |
| `add` | Añadir guardrail local |
| `disable` | Deshabilitar guardrail |
| `enable` | Habilitar guardrail |

**Ejemplos:**
```bash
# Listar guardrails
raise guardrail list

# Ver detalle
raise guardrail show GR-005

# Deshabilitar temporalmente
raise guardrail disable GR-005 --reason "Refactoring en progreso"

# Añadir guardrail local
raise guardrail add --file custom-guardrail.mdc
```

---

### raise validate

Ejecuta katas de validación.

**Sintaxis:**
```bash
raise validate <kata> [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--input <archivo>` | Archivo a validar | - |
| `--gate <nombre>` | Validation Gate a validar | - |
| `--output <archivo>` | Guardar reporte | stdout |

**Ejemplos:**
```bash
# Ejecutar kata específica
raise validate L1-16 --input specs/US-123.md

# Validar Validation Gate
raise validate --gate Gate-Design

# Guardar reporte
raise validate L1-04 --output report.md
```

---

### raise generate

Genera artefactos desde templates.

**Sintaxis:**
```bash
raise generate <tipo> [opciones]
```

**Tipos disponibles:**
| Tipo | Genera |
|------|--------|
| `spec` | Especificación de feature |
| `story` | Historia de usuario |
| `design` | Diseño técnico |
| `plan` | Plan de implementación |
| **`guardrail`** | Guardrail desde template [v2.0] |
| **`gate`** | Definición de gate [v2.0] |

**Ejemplos:**
```bash
# Generar spec
raise generate spec --jira PROJ-123

# Generar guardrail personalizado
raise generate guardrail --scope code --name "Custom Rule"

# Generar definición de gate
raise generate gate --name Gate-Custom
```

---

## Slash Commands (Para Agentes)

Comandos que los agentes reconocen dentro de conversaciones.

### Comandos Actualizados v2.0

| Comando | Propósito | Gate Asociado |
|---------|-----------|---------------|
| `/raise.constitution` | Generar constitution | — |
| `/raise.specify` | Crear especificación | Gate-Discovery |
| `/raise.plan` | Generar plan técnico | Gate-Design |
| `/raise.tasks` | Desglosar en tareas | Gate-Backlog |
| `/raise.implement` | Implementar tarea | Gate-Code |
| **`/raise.gate`** | Validar gate actual | Variable |
| `/raise.validate` | Ejecutar validación | Variable |
| `/raise.explain` | Explicar razonamiento | — |

### /raise.gate [NUEVO v2.0]

Valida el Validation Gate actual del flujo.

**Uso:**
```
/raise.gate [gate-name]
```

**Comportamiento:**
1. Identifica gate actual (o especificado)
2. Recopila artefactos relevantes
3. Ejecuta validación
4. Reporta status
5. Escala si falla

**Ejemplo:**
```
/raise.gate Gate-Design
```

---

### /raise.validate

Ejecuta validación contra Validation Gate o kata.

**Uso (actualizado v2.0):**
```
/raise.validate [gate|kata] [target]
```

**Ejemplos:**
```
/raise.validate Gate-Design @specs/FEAT-123.md
/raise.validate kata-L1-16 @stories/US-456.md
```

---

## MCP Tools (Para Agentes) [NUEVO v2.0]

Tools expuestos via MCP server para que agentes los invoquen.

### validate_gate

Valida un Validation Gate programáticamente.

**Schema:**
```json
{
  "name": "validate_gate",
  "parameters": {
    "gate": "Gate-Design",
    "artifact": "specs/FEAT-123-design.md"
  }
}
```

**Response:**
```json
{
  "status": "passed" | "failed",
  "criteria": [
    {"name": "...", "passed": true},
    {"name": "...", "passed": false, "gap": "..."}
  ],
  "escalation_required": false
}
```

---

### check_guardrail

Valida un guardrail específico.

**Schema:**
```json
{
  "name": "check_guardrail",
  "parameters": {
    "guardrail_id": "GR-005",
    "target": "src/main.py"
  }
}
```

---

### escalate

Escala decisión a Orquestador humano.

**Schema:**
```json
{
  "name": "escalate",
  "parameters": {
    "reason": "Gate-Design failed",
    "context": "Missing security considerations",
    "options": ["Proceed anyway", "Add security section", "Cancel task"]
  }
}
```

---

### log_trace

Registra evento en Observable Workflow.

**Schema:**
```json
{
  "name": "log_trace",
  "parameters": {
    "action": "custom_action",
    "details": {"key": "value"}
  }
}
```

---

## Guardrails Activos (.mdc)

Los guardrails en `.raise/memory/guardrails/` definen comportamiento de agentes:

| Guardrail | ID | Propósito |
|-----------|-----|-----------|
| raise-methodology-overview | GR-010 | Visión general de metodología |
| raise-design-documentation-standards | GR-020 | Estándares de documentación |
| commit-guidelines | GR-310 | Guías de commits |
| workspace-session-protocol | GR-320 | Protocolo de sesiones |
| guardrail-management | GR-910 | Gestión de guardrails |
| mermaid-diagram-standards | GR-920 | Estándares de diagramas |
| guardrail-precedence | GR-921 | Precedencia de guardrails |

---

## Integración con CI/CD

### GitHub Actions [ACTUALIZADO v2.0]

```yaml
name: RaiSE Validation
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
      - name: Check Guardrails
        run: raise check --format json --strict --no-trace
      - name: Validate Gates
        run: raise gate status --format json
      - name: Upload Traces
        if: always()
        run: raise audit --period today --format json --output traces.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: raise-traces
          path: traces.json
```

### Pre-commit Hook [ACTUALIZADO v2.0]

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: raise-check
        name: RaiSE Guardrails Check
        entry: raise check --no-trace
        language: system
        pass_filenames: false
      - id: raise-gate
        name: RaiSE Gate Validation
        entry: raise gate check --gate Gate-Code
        language: system
        pass_filenames: false
```

---

## Changelog

### v2.0.0 (2025-12-28)
- **NUEVO**: `raise gate` (check, list, status, pass)
- **NUEVO**: `raise mcp` (start, stop, status, resources, tools, test)
- **NUEVO**: `raise audit` (Observable Workflow)
- **NUEVO**: `raise guardrail` (list, show, add, disable, enable)
- **NUEVO**: MCP Tools documentados
- **RENOMBRADO**: `raise rule` → `raise guardrail` (alias mantenido)
- **ACTUALIZADO**: `raise init` con --mcp flag
- **ACTUALIZADO**: `raise check` con --trace flag
- **ACTUALIZADO**: CI/CD examples con gates y audit

### v1.0.0 (2025-12-27)
- Release inicial

---

*Esta referencia se actualiza con cada nuevo comando añadido. Ver [20-glossary-v2.md](./20-glossary-v2.md) para terminología.*
