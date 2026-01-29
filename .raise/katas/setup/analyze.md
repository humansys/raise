---
id: analyze
titulo: "Analyze: Codebase Analysis"
work_cycle: setup
frequency: once-brownfield
fase_metodologia: 0

prerequisites: []
template: null
gate: null
next_kata: setup/ecosystem

adaptable: true
shuhari:
  shu: "Analizar sistemáticamente todas las convenciones"
  ha: "Enfocarse en las convenciones más impactantes"
  ri: "Crear kata de Analyze para stacks específicos"

version: 1.0.0
---

# Analyze: Codebase Analysis

## Propósito

Analizar un codebase existente (brownfield) para extraer convenciones, patrones, y reglas implícitas que deben formalizarse como guardrails del proyecto.

## Contexto

**Cuándo usar:**
- Al entrar a un repositorio existente por primera vez
- Cuando se quiere formalizar convenciones implícitas
- Antes de comenzar desarrollo en un proyecto brownfield

**Inputs requeridos:**
- Acceso al repositorio
- Documentación existente (si hay)

**Output:**
- Reglas extraídas en `.cursor/rules/`
- Documento de convenciones

## Pasos

### Paso 1: Explorar Estructura

Analizar estructura de directorios:
- Organización de código
- Patrones de naming
- Separación de concerns

**Verificación:** Estructura documentada.

> **Si no puedes continuar:** Estructura caótica → Documentar el caos como punto de partida.

### Paso 2: Identificar Stack Tecnológico

Detectar tecnologías usadas:
- Lenguajes y versiones
- Frameworks
- Dependencias principales

**Verificación:** Stack documentado.

> **Si no puedes continuar:** Stack mixto → Documentar cada tecnología por separado.

### Paso 3: Extraer Patrones de Código

Analizar código para detectar:
- Patrones de arquitectura (MVC, Clean, etc.)
- Convenciones de naming
- Manejo de errores
- Testing patterns

**Verificación:** Patrones identificados con ejemplos.

> **Si no puedes continuar:** Sin patrones claros → Documentar como "convenciones pendientes de definir".

### Paso 4: Detectar Anti-Patrones

Identificar código que viola convenciones:
- Inconsistencias
- Code smells
- Deuda técnica

**Verificación:** Anti-patrones documentados.

> **Si no puedes continuar:** N/A (anti-patrones son opcionales de documentar).

### Paso 5: Formalizar Reglas

Crear archivos `.mdc` para cada convención:
- Nombre descriptivo
- Globs aplicables
- Instrucciones claras

**Verificación:** Reglas creadas en `.cursor/rules/`.

> **Si no puedes continuar:** Formato incorrecto → Verificar schema de reglas.

## Output

- **Artefacto:** Reglas del proyecto
- **Ubicación:** `.cursor/rules/*.mdc`
- **Gate:** N/A
- **Siguiente kata:** `setup/ecosystem`

## Referencias

- Skill relacionado: `skills/generate-rules.yaml`
