---
id: design
titulo: "Design: Technical Architecture"
work_cycle: project
frequency: once-per-epic
fase_metodologia: 3

prerequisites:
  - project/vision
template: templates/tech/tech_design.md
gate: gates/gate-architecture.md
next_kata: project/backlog

adaptable: true
shuhari:
  shu: "Seguir todos los pasos del diseño C4"
  ha: "Adaptar nivel de detalle según complejidad del proyecto"
  ri: "Crear kata de Design para arquitecturas específicas (microservices, serverless)"

version: 1.1.0
---

# Design: Technical Architecture

## Propósito

Traducir la Project Vision en una arquitectura técnica detallada siguiendo el modelo C4 (Context, Container, Component). Este documento guía la implementación y sirve como referencia para decisiones técnicas.

## Contexto

**Cuándo usar:**
- Después de tener una Project Vision aprobada
- Antes de crear el backlog de implementación
- Cuando se necesita definir la arquitectura del sistema

**Inputs requeridos:**
- Project Vision aprobada (`governance/vision.md`)
- Contexto técnico del ecosistema

**Output:**
- `governance/design.md` - Technical Design estructurado

## Pasos

### Paso 1: Cargar Vision y Contexto

Cargar la Project Vision y recopilar información del contexto técnico actual.

**Verificación:** La Project Vision existe y el contexto técnico está claro.

> **Si no puedes continuar:** Vision no encontrada → Ejecutar `project/vision` primero.

### Paso 2: Definir System Context (C4 Level 1)

Documentar el sistema en su contexto:
- Actores externos (usuarios, sistemas)
- Sistemas externos que interactúan
- Límites del sistema

**Verificación:** Diagrama de contexto tiene ≥1 actor externo y ≥1 sistema externo (o justificación de standalone).

> **Si no puedes continuar:** Contexto no claro → Listar todos los sistemas que consumen o proveen datos.

### Paso 3: Definir Container Diagram (C4 Level 2)

Documentar los contenedores del sistema:
- Aplicaciones, servicios, bases de datos
- Tecnología de cada contenedor
- Comunicación entre contenedores

**Verificación:** Diagrama tiene ≥2 containers, cada uno con nombre, responsabilidad y tecnología.

> **Si no puedes continuar:** Arquitectura monolítica → Documentar como un container con componentes internos claros.

### Paso 4: Documentar Flujos de Datos

Para cada flujo principal:
- Input → Procesamiento → Output
- Transformaciones de datos
- Puntos de persistencia

**Verificación:** Cada input tiene un camino trazable hasta output o persistencia.

> **Si no puedes continuar:** Flujos complejos → Dividir en sub-flujos y documentar cada uno.

### Paso 5: Especificar Contratos de API

Para cada API:
- Endpoints con métodos HTTP
- Request/Response schemas
- Códigos de error

**Verificación:** Endpoints tienen request/response documentados.

> **Si no puedes continuar:** APIs no claras → Comenzar con los 3-5 endpoints más críticos.

### Paso 6: Definir Modelo de Datos

Documentar entidades principales:
- Entidades y atributos
- Relaciones entre entidades
- Índices y constraints

**Verificación:** Entidades tienen campos, relaciones e índices documentados.

> **Si no puedes continuar:** Modelo complejo → Comenzar con las 5 entidades core.

### Paso 7: Documentar Seguridad

Para cada endpoint y componente:
- Autenticación (AuthN)
- Autorización (AuthZ)
- Compliance requirements

**Verificación:** AuthN/AuthZ definidos para cada endpoint.

> **Si no puedes continuar:** Seguridad no clara → Definir roles básicos (admin, user, guest) y permisos.

### Paso 8: Estandarizar Manejo de Errores

Documentar catálogo de errores:
- Códigos de error
- Formato de respuesta
- Estrategias de retry

**Verificación:** Catálogo de errores estandarizado existe.

> **Si no puedes continuar:** Errores ad-hoc → Definir formato estándar y migrar errores existentes.

### Paso 9: Documentar Decisiones Arquitectónicas

Para cada decisión clave:
- Contexto y problema
- Opciones consideradas
- Decisión y rationale

**Verificación:** Cada decisión tiene rationale (no solo "qué", también "por qué").

> **Si no puedes continuar:** Decisiones sin justificar → Revisar con equipo y documentar trade-offs.

### Paso 10: Validar con Equipo Técnico

Revisar diseño con peers:
- ¿Es comprensible?
- ¿Hay decisiones cuestionables?
- ¿Faltan consideraciones?

**Verificación:** Feedback de peer review incorporado.

> **Si no puedes continuar:** Sin peer review → Agendar sesión antes de continuar.

## Output

- **Artefacto:** Technical Design
- **Ubicación:** `governance/design.md`
- **Gate:** `gates/gate-architecture.md`
- **Siguiente kata:** `project/backlog`

## Referencias

- Gate de validación: `gates/gate-architecture.md`
- Template: `templates/tech/tech_design.md`
- C4 Model: https://c4model.com
