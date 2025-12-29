# RaiSE Commands Reference
## Referencia de Comandos CLI y Slash Commands

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Documentar comandos disponibles para usuarios y agentes.

---

## CLI Commands (raise-kit)

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
| `--skip-hydrate` | No sincronizar reglas | false |

**Ejemplos:**
```bash
# Inicialización básica
raise init

# Con agente específico
raise init --agent cursor

# Con template enterprise
raise init --agent copilot --template enterprise

# Con config personalizado
raise init --config https://github.com/org/raise-config.git
```

**Resultado:**
```
.raise/
├── memory/
│   └── constitution.md
├── raise.yaml
└── README.md
```

---

### raise hydrate

Sincroniza reglas desde el repositorio central.

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

**Ejemplos:**
```bash
# Sincronizar desde config default
raise hydrate

# Desde branch específico
raise hydrate --branch develop

# Forzar actualización
raise hydrate --force
```

**Resultado:**
- Actualiza `.raise/memory/raise-rules.json`
- Sincroniza katas
- Actualiza templates

---

### raise check

Valida el proyecto contra las reglas activas.

**Sintaxis:**
```bash
raise check [ruta] [opciones]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| `--rules <ids>` | Solo validar reglas específicas | todas |
| `--fix` | Intentar corrección automática | false |
| `--format <fmt>` | Formato de salida (text/json) | text |
| `--strict` | Fallar en warnings | false |

**Ejemplos:**
```bash
# Validar proyecto completo
raise check

# Validar archivo específico
raise check src/main.py

# Solo ciertas reglas
raise check --rules 001,002,003

# Output JSON para CI
raise check --format json --strict
```

**Exit codes:**
| Código | Significado |
|--------|-------------|
| 0 | Sin errores |
| 1 | Errores encontrados |
| 2 | Warnings (con --strict) |

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
| `--dod <fase>` | Fase de DoD a validar | - |
| `--output <archivo>` | Guardar reporte | stdout |

**Ejemplos:**
```bash
# Ejecutar kata específica
raise validate L1-16 --input specs/US-123.md

# Validar DoD de fase
raise validate --dod design

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

**Ejemplos:**
```bash
# Generar spec
raise generate spec --jira PROJ-123

# Generar historia
raise generate story --parent PROJ-123

# Generar diseño técnico
raise generate design --feature FEAT-456
```

---

## Slash Commands (Para Agentes)

Comandos que los agentes reconocen dentro de conversaciones.

### /raise.constitution

Genera o actualiza la constitution del proyecto.

**Uso:**
```
/raise.constitution [opciones]
```

**Comportamiento:**
1. Lee contexto del proyecto
2. Analiza patrones existentes (brownfield)
3. Genera constitution respetando principios RaiSE
4. Presenta para validación humana

**Ejemplo:**
```
/raise.constitution --analyze-existing
```

---

### /raise.specify

Crea una especificación para una feature.

**Uso:**
```
/raise.specify [descripción]
```

**Comportamiento:**
1. Elicita requisitos mediante diálogo
2. Usa template de PRD o feature spec
3. Valida contra DoD-Discovery
4. Genera documento estructurado

**Ejemplo:**
```
/raise.specify Implementar autenticación con SSO
```

---

### /raise.plan

Genera un plan técnico desde una spec.

**Uso:**
```
/raise.plan [spec-reference]
```

**Comportamiento:**
1. Lee especificación referenciada
2. Aplica kata L1-04 de planificación
3. Genera plan paso a paso
4. Valida contra DoD-Design

**Ejemplo:**
```
/raise.plan @specs/FEAT-123.md
```

---

### /raise.tasks

Desglosa un plan en tareas implementables.

**Uso:**
```
/raise.tasks [plan-reference]
```

**Comportamiento:**
1. Lee plan técnico
2. Atomiza en tareas
3. Identifica dependencias
4. Genera lista priorizada

**Ejemplo:**
```
/raise.tasks @plans/FEAT-123-plan.md
```

---

### /raise.implement

Ejecuta la implementación de tareas.

**Uso:**
```
/raise.implement [task-reference]
```

**Comportamiento:**
1. Lee tarea específica
2. Carga contexto relevante (reglas, design)
3. Genera código siguiendo reglas
4. Propone tests

**Ejemplo:**
```
/raise.implement @tasks/TASK-001.md
```

---

### /raise.validate

Ejecuta validación contra DoD o kata.

**Uso:**
```
/raise.validate [dod|kata] [target]
```

**Comportamiento:**
1. Identifica fase o kata
2. Lee artefacto target
3. Ejecuta validación
4. Reporta cumplimiento/gaps

**Ejemplos:**
```
/raise.validate dod-design @specs/FEAT-123.md
/raise.validate kata-L1-16 @stories/US-456.md
```

---

### /raise.explain

Explica razonamiento antes de generar.

**Uso:**
```
/raise.explain [acción]
```

**Comportamiento:**
1. Describe approach antes de ejecutar
2. Lista consideraciones
3. Presenta alternativas
4. Solicita confirmación

**Ejemplo:**
```
/raise.explain cómo implementarías la autenticación SSO
```

---

## Reglas Activas (.mdc)

Las reglas en `src/rules/` definen comportamiento de agentes:

| Regla | ID | Propósito |
|-------|-----|-----------|
| raise-methodology-overview | 010 | Visión general de metodología |
| raise-design-documentation-standards | 020 | Estándares de documentación |
| commit-guidelines | 310 | Guías de commits |
| workspace-session-protocol | 320 | Protocolo de sesiones |
| rule-management | 910 | Gestión de reglas |
| mermaid-diagram-standards | 920 | Estándares de diagramas |
| rule-precedence | 920 | Precedencia de reglas |

---

## Integración con CI/CD

### GitHub Actions

```yaml
name: RaiSE Check
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install raise-kit
      - run: raise check --format json --strict
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: raise-check
        name: RaiSE Check
        entry: raise check
        language: system
        pass_filenames: false
```

---

*Esta referencia se actualiza con cada nuevo comando añadido.*
