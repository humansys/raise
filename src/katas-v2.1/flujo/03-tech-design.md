---
id: flujo-03-tech-design
nivel: flujo
titulo: "Tech Design: Arquitectura Detallada"
audience: intermediate
template_asociado: templates/tech/tech_design.md
validation_gate: gates/gate-design.md
prerequisites:
  - flujo-02-solution-vision
fase_metodologia: 3
tags: [arquitectura, diseño, tech-design, fase-3]
version: 1.0.0
---

# Tech Design: Arquitectura Detallada

## Propósito

Traducir la Solution Vision en un diseño técnico detallado que guíe la implementación. Este documento especifica la arquitectura de componentes, flujos de datos, contratos de API, y decisiones técnicas fundamentales.

Esta kata responde a la pregunta: **¿Cómo fluye la visión de alto nivel hacia un diseño técnico implementable?**

## Contexto

**Cuándo usar:**
- Después de que Gate-Vision ha sido aprobado
- Antes de crear el backlog de User Stories
- Cuando se requiere diseño técnico formal (proyectos > 2 semanas)

**Inputs requeridos:**
- Solution Vision aprobada (output de `flujo-02-solution-vision`)
- PRD como referencia de requisitos
- Documentación técnica existente (para brownfield)

**Output:** Technical Design Document siguiendo `templates/tech/tech_design.md`

## Pre-condiciones

- [ ] Gate-Vision aprobado
- [ ] Solution Vision disponible en `.raise/specs/{proyecto}-vision.md`
- [ ] Arquitecto o Tech Lead asignado para revisión
- [ ] Stack tecnológico definido

---

## Pasos

### Paso 1: Cargar Vision y Contexto Técnico

Cargar la Solution Vision y recopilar documentación técnica adicional:
- Solution Vision aprobada
- PRD para referencia de requisitos detallados
- Documentación de APIs existentes (si aplica)
- Schemas de datos existentes (si brownfield)

**Verificación:** Todos los documentos están accesibles y el contexto técnico del proyecto está claro.

> **Si no puedes continuar:** Documentación técnica faltante → Para brownfield, ejecutar `patron-01-code-analysis` primero. Para greenfield, documentar decisiones de stack pendientes.

---

### Paso 2: Instanciar Template Tech Design

Crear el documento de diseño técnico:

```bash
cp templates/tech/tech_design.md .raise/specs/{proyecto}-tech-design.md
```

**Verificación:** Existe archivo `{proyecto}-tech-design.md` con metadatos completados (project_name, version, date, related_docs).

> **Si no puedes continuar:** Template no encontrado → Verificar ruta del template o usar versión base de raise-config.

---

### Paso 3: Definir Visión General Técnica

Completar sección "Visión General y Objetivo":
- Resumir el objetivo desde perspectiva técnica
- Identificar el problema técnico central a resolver
- Conectar con los goals de la Solution Vision

**Verificación:** La visión técnica es comprensible para un desarrollador que no ha leído el PRD, pero está claramente alineada con los objetivos de negocio.

> **Si no puedes continuar:** Visión desconectada del negocio → Revisar Solution Vision y extraer los mecanismos técnicos identificados en el paso de alineamiento.

---

### Paso 4: Describir Solución Propuesta

Completar sección "Solución Propuesta":
- Enfoque técnico de alto nivel
- Principales piezas/componentes involucrados
- Decisiones arquitectónicas fundamentales (monolito vs microservicios, sync vs async, etc.)

**Verificación:** Un desarrollador senior puede entender el approach en 5 minutos de lectura.

> **Si no puedes continuar:** Múltiples approaches válidos sin decisión → Documentar alternativas en sección "Alternativas Consideradas" y escalar decisión a Arquitecto.

---

### Paso 5: Detallar Arquitectura de Componentes

Completar sección "Arquitectura y Desglose de Componentes":

**Componentes Nuevos:**
- Nombre, propósito, responsabilidades
- Lenguaje/framework
- Interfaces expuestas

**Componentes Modificados:**
- Qué cambia y por qué
- Impacto en componentes dependientes

**Servicios Externos:**
- Integraciones requeridas
- Contratos esperados

**Verificación:** Existe diagrama (Mermaid o similar) que muestra todos los componentes y sus relaciones. Cada componente tiene responsabilidad única (SRP).

> **Si no puedes continuar:** Componentes con responsabilidades mezcladas → Aplicar principio de responsabilidad única. Si un componente hace "X e Y", considerar separar.

---

### Paso 6: Documentar Flujos de Datos

Completar sección "Flujo de Datos":
- Origen de los datos
- Transformaciones aplicadas
- Destino de almacenamiento
- Flujos síncronos vs asíncronos

**Verificación:** Para cada input del sistema, se puede trazar el camino hasta su destino final.

> **Si no puedes continuar:** Flujos incompletos → Identificar cada "entrada" al sistema (API call, evento, cron) y documentar qué pasa con los datos hasta que se persisten o responden.

---

### Paso 7: Especificar Contratos de API

Completar sección "Contrato(s) de API":
- Endpoints (método, ruta)
- Request body/params
- Response body
- Códigos de error

**Verificación:** Cada endpoint tiene ejemplo de request y response. Los contratos son suficientes para que un consumidor pueda implementar sin preguntas.

> **Si no puedes continuar:** Contratos ambiguos → Para cada campo, definir tipo, requerido/opcional, y validaciones. Si es enum, listar valores posibles.

---

### Paso 8: Diseñar Modelo de Datos

Completar sección "Cambios en el Modelo de Datos":
- Nuevas tablas/colecciones
- Campos nuevos en tablas existentes
- Índices requeridos
- Estrategia de migración

**Verificación:** El modelo soporta todos los requisitos funcionales del PRD. Las relaciones están normalizadas apropiadamente.

> **Si no puedes continuar:** Requisitos no mapeados a modelo → Revisar cada requisito funcional y verificar qué datos necesita persistir. Añadir entidades/campos faltantes.

---

### Paso 9: Documentar Algoritmos Clave

Completar sección "Algoritmos / Lógica Clave":
- Lógica de negocio no obvia
- Algoritmos de procesamiento
- Reglas de validación complejas

**Verificación:** La lógica compleja está documentada con pseudocódigo o descripción paso a paso.

> **Si no puedes continuar:** Lógica no clara → Preguntar al Product Owner: "¿Qué pasa cuando [caso edge]?" hasta cubrir los escenarios no obvios.

---

### Paso 10: Especificar Consideraciones de Seguridad

Completar sección "Consideraciones de Seguridad":
- Autenticación (quién puede acceder)
- Autorización (qué puede hacer cada rol)
- Datos sensibles (cómo se protegen)
- Vulnerabilidades mitigadas

**Verificación:** Cada endpoint tiene definido quién puede invocarlo. Los datos sensibles tienen estrategia de protección.

> **Si no puedes continuar:** Requisitos de seguridad no claros → Revisar NFRs del PRD. Si no hay, asumir mínimo: autenticación requerida, datos PII encriptados.

---

### Paso 11: Definir Estrategia de Errores

Completar sección "Estrategia de Manejo de Errores":
- Tipos de errores esperados
- Formato de respuesta de error
- Estrategia de logging
- Recuperación/retry

**Verificación:** Existe catálogo de códigos de error con mensaje y acción sugerida para el cliente.

> **Si no puedes continuar:** Sin estrategia de errores → Definir al menos: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (internal error) con formato consistente.

---

### Paso 12: Documentar Alternativas Consideradas

Completar sección "Alternativas Consideradas":
- Opciones evaluadas
- Razón de rechazo de cada una
- Trade-offs de la decisión tomada

**Verificación:** Al menos 2 alternativas documentadas para las decisiones arquitectónicas principales.

> **Si no puedes continuar:** No hubo alternativas → Siempre hay alternativas. Documentar al menos: "hacer nada" y "approach opuesto" con razones de rechazo.

---

### Paso 13: Listar Preguntas y Riesgos

Completar sección "Preguntas Abiertas y Riesgos":
- Preguntas técnicas sin resolver
- Riesgos de implementación
- Dependencias externas

**Verificación:** Cada pregunta tiene owner asignado. Cada riesgo tiene mitigación propuesta.

> **Si no puedes continuar:** Preguntas sin owner → Asignar cada pregunta al rol más apropiado (Arquitecto, Tech Lead, Product Owner) con fecha límite de respuesta.

---

### Paso 14: Definir Estrategia de Testing

Completar sección "Estrategia de Pruebas":
- Tipos de pruebas (unit, integration, e2e)
- Cobertura esperada
- Ambientes de prueba

**Verificación:** La estrategia cubre el camino crítico del sistema (happy path + principales error cases).

> **Si no puedes continuar:** Sin estrategia clara → Mínimo: unit tests para lógica de negocio, integration tests para APIs, e2e para flujos críticos de usuario.

---

### Paso 15: Validar con Equipo Técnico

Presentar el Tech Design para revisión técnica:
1. Walkthrough con Tech Lead/Arquitecto
2. Revisión de peers (otros desarrolladores)
3. Incorporar feedback
4. Obtener aprobación

**Verificación:** Tech Design aprobado por Arquitecto o Tech Lead. Comentarios de revisión resueltos.

> **Si no puedes continuar:** Feedback no resuelto → Priorizar feedback por impacto. Resolver blockers antes de continuar. Documentar decisiones de "no action" con justificación.

---

## Output

**Artefacto producido:** Technical Design Document

**Ubicación:** `.raise/specs/{proyecto}-tech-design.md`

**Siguiente paso:**
1. Ejecutar `gates/gate-design.md` para validar
2. Si pasa el gate, proceder a `flujo-05-backlog-creation`

---

## Notas

### Nivel de Detalle
- **Greenfield**: Más detalle en decisiones fundamentales
- **Brownfield**: Enfocarse en cambios y cómo integran con existente
- **Spike/POC**: Versión ligera enfocada en riesgos técnicos

### Documentos Relacionados
Si el diseño es muy extenso, considerar documentos separados:
- `{proyecto}-api-spec.md` para contratos detallados
- `{proyecto}-data-model.md` para ERD completo
- `{proyecto}-security.md` para análisis de seguridad

---

## Referencias

- Template: [`templates/tech/tech_design.md`](../../templates/tech/tech_design.md)
- Prerequisito: [`flujo-02-solution-vision`](./02-solution-vision.md)
- Siguiente kata: [`flujo-05-backlog-creation`](./05-backlog-creation.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 3
