---
id: patron-03-tech-design-stack-aware
nivel: patron
titulo: "Tech Design Consciente del Stack"
audience: intermediate
template_asociado: tech_design.md
validation_gate: gate-design
prerequisites:
  - principios-00-meta-kata
  - patron-01-code-analysis
tags: [tech-design, brownfield, stack, arquitectura, patron]
version: 1.0.0
---

# Tech Design Consciente del Stack

## Propósito

Guiar el diseño técnico en contextos brownfield donde ya existe un stack tecnológico establecido. Este patrón responde a: **¿Qué forma debe tener un diseño técnico que respete y extienda lo existente?**

## Cuándo Aplicar

- Antes de implementar features en proyectos existentes
- Cuando se necesita extender arquitectura establecida
- Para evaluar compatibilidad de nuevas tecnologías
- Al diseñar integraciones con sistemas legacy

## Pre-condiciones

- Análisis de código completado (`patron-01-code-analysis`)
- Ecosistema mapeado (`patron-02-ecosystem-discovery`)
- Requisitos funcionales claros (PRD o equivalente)

---

## Estructura del Diseño

### Paso 1: Inventariar Stack Actual

Documentar las tecnologías en uso:
- Lenguajes y versiones
- Frameworks principales
- Bases de datos y storage
- Infraestructura (cloud, on-prem, híbrida)
- Herramientas de CI/CD

**Verificación:** Lista exhaustiva de tecnologías con versiones específicas.

> **Si no puedes continuar:** Stack no documentado → Extraer de package.json, Gemfile, requirements.txt, pom.xml, o equivalente. El código no miente.

---

### Paso 2: Identificar Patrones Establecidos

Documentar los patrones arquitectónicos en uso:
- Estructura de capas (MVC, Clean Architecture, etc.)
- Patrones de comunicación (REST, eventos, etc.)
- Patrones de datos (Repository, Active Record, etc.)
- Convenciones de naming y organización

**Verificación:** Puedes explicar "así es como se hacen las cosas aquí" con ejemplos concretos.

> **Si no puedes continuar:** Patrones inconsistentes en el código → Identificar el patrón dominante (>60% del código). Las excepciones se documentan como deuda técnica.

---

### Paso 3: Evaluar Constraints del Stack

Identificar limitaciones impuestas por el stack:
- Versiones de lenguaje/framework que limitan features
- Dependencias que no se pueden actualizar
- Decisiones arquitectónicas irreversibles
- Limitaciones de infraestructura

**Verificación:** Lista de constraints con impacto en el diseño actual.

> **Si no puedes continuar:** Constraints no claros → Preguntar: "¿Qué NO podemos cambiar?" a los stakeholders técnicos. Los constraints definen el espacio de solución.

---

### Paso 4: Diseñar Dentro del Stack

Crear el diseño técnico respetando lo existente:
- Usar los patrones establecidos
- Extender sin contradecir
- Minimizar nuevas dependencias
- Mantener consistencia con el código existente

**Verificación:** El diseño se ve como "más de lo mismo" para alguien que conoce el proyecto.

> **Si no puedes continuar:** El diseño requiere romper patrones existentes → Documentar explícitamente el porqué. Si es necesario divergir, debe ser una decisión consciente (ADR).

---

### Paso 5: Identificar Extensiones Necesarias

Si el diseño requiere capacidades nuevas:
- Nuevas librerías o dependencias
- Nuevos patrones o abstracciones
- Cambios en infraestructura
- Actualizaciones de versiones

**Verificación:** Lista de extensiones con justificación de cada una.

> **Si no puedes continuar:** Extensión contradice constraints → Reevaluar el diseño. Si la extensión es inevitable, escalar la decisión al owner técnico.

---

### Paso 6: Planificar Migración Incremental

Si hay deuda técnica que pagar o patrones a mejorar:
- Definir estado objetivo
- Crear path incremental
- Identificar puntos de no retorno
- Estimar esfuerzo por fase

**Verificación:** Plan que permite entregar valor mientras se mejora el código.

> **Si no puedes continuar:** Migración todo-o-nada → Buscar seams (costuras) en el código donde se pueda migrar por partes. Si no hay seams, crearlos primero.

---

### Paso 7: Documentar Decisiones

Crear documentación del diseño:
- Diagrama de componentes afectados
- Decisiones técnicas con rationale
- Trade-offs considerados
- Plan de implementación

**Verificación:** Otro desarrollador puede implementar el diseño sin preguntas adicionales.

> **Si no puedes continuar:** Diseño requiere conocimiento implícito → Hacer explícito ese conocimiento en la documentación. Si tú lo necesitas, otros también.

---

## Output de Este Patrón

Al completar este patrón, el Orquestador tiene:
- Inventario del stack actual
- Patrones establecidos documentados
- Constraints identificados
- Diseño técnico compatible con el stack
- Lista de extensiones necesarias (si las hay)
- Plan de migración (si aplica)
- Documentación compartible

---

## Principios del Diseño Stack-Aware

### 1. Consistencia sobre Perfección
Es mejor seguir un patrón imperfecto consistentemente que introducir el "patrón perfecto" que nadie más usa.

### 2. Evolución sobre Revolución
Cambios incrementales que entregan valor son preferibles a reescrituras masivas.

### 3. Explícito sobre Implícito
Toda desviación del patrón establecido debe documentarse con su razón.

### 4. Reversible sobre Óptimo
Preferir decisiones que se puedan deshacer a decisiones "óptimas" irreversibles.

---

## Anti-Patrones

| Anti-Patrón | Problema | Solución |
|-------------|----------|----------|
| "Greenfield en Brownfield" | Ignorar lo existente | Estudiar y respetar patrones actuales |
| Dependencia nueva por feature | Explosión de dependencias | Evaluar si lo existente resuelve el problema |
| Arquitectura astronaut | Sobre-diseño para flexibilidad futura | YAGNI - diseñar para el problema actual |
| Copy-paste de otro proyecto | Patrones incompatibles | Adaptar al contexto específico |

---

## Relación con Otras Katas

| Kata | Relación |
|------|----------|
| `flujo-03-tech-design` | Este patrón complementa al flujo añadiendo consciencia del stack |
| `patron-01-code-analysis` | Pre-requisito para entender el código existente |
| `patron-02-ecosystem-discovery` | Pre-requisito para entender integraciones |

---

## Referencias

- Template: [`tech_design.md`](../../templates/tech/tech_design.md)
- Gate: [`gate-design`](../../gates/gate-design.md)
- Meta-Kata: [`principios-00-meta-kata`](../principios/00-meta-kata.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md)
