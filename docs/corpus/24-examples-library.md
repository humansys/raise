# RaiSE Examples Library
## Ejemplos Prácticos de Uso

**Versión:** 1.0.0  
**Fecha:** 27 de Diciembre, 2025  
**Propósito:** Biblioteca de ejemplos concretos para aprender RaiSE.

---

## Ejemplo 1: Feature Nueva en Proyecto Existente

### Contexto
- **Proyecto:** API REST existente en Python
- **Feature:** Agregar endpoint de búsqueda con filtros
- **Estimado:** 2-3 días

### Proceso Paso a Paso

#### 1. Inicialización (si no existe)
```bash
raise init --agent cursor
```

#### 2. Especificación
```
/raise.specify Agregar endpoint de búsqueda de productos con filtros por categoría, precio y disponibilidad
```

**Resultado:** Spec generada en `.raise/specs/FEAT-001-busqueda-productos.md`

#### 3. Diseño Técnico
```
/raise.plan @.raise/specs/FEAT-001-busqueda-productos.md
```

**Resultado:** Plan técnico con:
- Diseño de endpoint
- Query parameters
- Modelo de response
- Consideraciones de performance

#### 4. Tareas
```
/raise.tasks @.raise/plans/FEAT-001-plan.md
```

**Resultado:**
1. Crear modelo de filtros
2. Implementar query builder
3. Crear endpoint controller
4. Agregar tests
5. Documentar API

#### 5. Implementación
```
/raise.implement @.raise/tasks/TASK-001.md
```

### Artefactos Generados
```
.raise/
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
- El DoD de diseño detectó falta de paginación temprano

---

## Ejemplo 2: Proyecto Greenfield Completo

### Contexto
- **Proyecto:** Microservicio desde cero
- **Stack:** Python + FastAPI + PostgreSQL
- **Estimado:** 2 semanas

### Proceso Paso a Paso

#### Fase 0: Inicialización
```bash
mkdir my-service && cd my-service
raise init --template microservice
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

#### Fase 3: Solution Vision
```
/raise.specify --template solution-vision
```

#### Fase 4: Tech Design
```
/raise.plan --template tech-design
```

#### Fase 5+: Iteración
Para cada feature del MVP:
1. `/raise.specify`
2. `/raise.plan`
3. `/raise.tasks`
4. `/raise.implement`
5. `/raise.validate dod-code`

### Estructura Final
```
my-service/
├── .raise/
│   ├── memory/
│   │   └── constitution.md
│   ├── specs/
│   ├── plans/
│   └── tasks/
├── src/
├── tests/
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

#### 3. Reglas desde Patrones
Extraer reglas de patrones detectados:
- Naming conventions existentes
- Estructura de directorios
- Patrones de código

#### 4. Adopción Gradual
Para cada nueva feature:
1. Crear spec siguiendo RaiSE
2. Implementar con validación
3. Legacy no tocado

### Lecciones Aprendidas
- **No forzar** cambios en código existente
- Documentar "deuda técnica conocida"
- Migrar patrones gradualmente

---

## Ejemplo 4: Governance Multi-Proyecto

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

Estructura:
```
org-raise-config/
├── rules/
│   ├── 001-naming.mdc
│   ├── 002-security.mdc
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
```

#### 3. Sincronización
```bash
raise hydrate
```

#### 4. CI/CD Enforcement
```yaml
# .github/workflows/raise.yml
- run: raise hydrate
- run: raise check --strict
```

### Beneficios
- Una fuente de verdad
- Updates sin tocar repos
- Compliance automático

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

---

### Anti-Ejemplo 2: Saltar Fases

❌ **Malo:**
```
/raise.implement Crear sistema de autenticación
```

✅ **Bueno:**
```
/raise.specify Sistema de autenticación con SSO
[... después de validar spec ...]
/raise.plan @spec.md
[... después de validar plan ...]
/raise.implement @task-001.md
```

**Por qué falla:** Sin spec/plan, el código carece de contexto y el agente toma decisiones arbitrarias.

---

### Anti-Ejemplo 3: Ignorar DoD

❌ **Malo:**
Completar feature sin ejecutar validación.

✅ **Bueno:**
```
/raise.validate dod-code @feature.md
```

**Por qué falla:** Los problemas se detectan tarde (o nunca).

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

## Patrones Recomendados

### Patrón: Explicabilidad Primero
```
Antes de implementar X, explícame:
1. Tu enfoque propuesto
2. Alternativas consideradas
3. Trade-offs
```

### Patrón: Validación Continua
Después de cada fase:
```
/raise.validate dod-{fase} @artefacto.md
```

### Patrón: Iteración con Contexto
```
Dado el feedback anterior, ajusta el diseño para [cambio específico].
```

---

*Esta biblioteca crece con cada nuevo patrón aprendido.*
