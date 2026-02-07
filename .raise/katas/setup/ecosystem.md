---
id: ecosystem
titulo: "Ecosystem: Dependency Mapping"
work_cycle: setup
frequency: once-brownfield
fase_metodologia: 0

prerequisites:
  greenfield: []
  brownfield: [setup/analyze]
template: null
gate: null
next_kata: project/discovery

adaptable: true
shuhari:
  shu: "Mapear todas las integraciones sistemáticamente"
  ha: "Enfocarse en integraciones críticas"
  ri: "Crear kata de Ecosystem para dominios específicos"

version: 1.0.0
---

# Ecosystem: Dependency Mapping

## Propósito

Mapear el ecosistema de integraciones, dependencias externas, y sistemas relacionados para entender el contexto operacional del proyecto.

> **Note:** This kata is primarily for **brownfield** projects where you need to understand existing integrations. For greenfield projects, proceed directly to `project/discovery` after `setup/rules`.

## Contexto

**Cuándo usar:**
- Después de analizar el codebase
- Cuando se necesita entender integraciones
- Antes de diseñar nuevas funcionalidades

**Inputs requeridos:**
- Codebase analizado
- Acceso a documentación de APIs

**Output:**
- Mapa de ecosistema documentado

## Pasos

### Paso 1: Identificar Integraciones

Listar sistemas externos:
- APIs consumidas
- Bases de datos
- Servicios cloud
- Third-party services

**Verificación:** Lista de integraciones completa.

> **Si no puedes continuar:** Integraciones ocultas → Buscar en configuración y secrets.

### Paso 2: Documentar Contratos

Para cada integración:
- Endpoints/métodos usados
- Formatos de datos
- Autenticación requerida

**Verificación:** Contratos documentados.

> **Si no puedes continuar:** Documentación faltante → Inferir de código y verificar.

### Paso 3: Identificar Dependencias Críticas

Clasificar por criticidad:
- Core (sistema no funciona sin ella)
- Important (degrada funcionalidad)
- Nice-to-have (mejora experiencia)

**Verificación:** Clasificación completada.

> **Si no puedes continuar:** Criticidad no clara → Preguntar "¿qué pasa si esto falla?".

### Paso 4: Mapear Flujos de Datos

Documentar cómo fluyen los datos:
- Entrada → Procesamiento → Salida
- Transformaciones
- Puntos de persistencia

**Verificación:** Flujos documentados.

> **Si no puedes continuar:** Flujos complejos → Dividir en sub-flujos.

### Paso 5: Crear Diagrama de Ecosistema

Visualizar el ecosistema:
- Sistema central
- Integraciones
- Flujos de datos

**Verificación:** Diagrama creado.

> **Si no puedes continuar:** Herramienta no disponible → Usar ASCII o Mermaid.

## Output

- **Artefacto:** Mapa de ecosistema
- **Ubicación:** `governance/ecosystem.md`
- **Gate:** N/A
- **Siguiente kata:** `project/discovery`

## Referencias

- Kata previa: `setup/analyze`
