---
id: flujo-02-solution-vision
nivel: flujo
titulo: "Solution Vision: De PRD a Visión de Solución"
audience: intermediate
template_asociado: templates/solution/solution-vision-template.md
validation_gate: gates/gate-vision.md
prerequisites:
  - flujo-01-discovery
fase_metodologia: 2
tags: [vision, arquitectura, alineamiento, fase-2]
version: 1.0.0
---

# Solution Vision: De PRD a Visión de Solución

## Propósito

Transformar el PRD validado en una Visión de Solución de alto nivel que alinee los objetivos de negocio con las decisiones técnicas fundamentales. Este documento sirve como puente entre "qué queremos" (PRD) y "cómo lo construiremos" (Tech Design).

Esta kata responde a la pregunta: **¿Cómo fluye la traducción de requisitos de negocio a una visión técnica alineada?**

## Contexto

**Cuándo usar:**
- Después de que Gate-Discovery ha sido aprobado
- Antes de iniciar el diseño técnico detallado
- Cuando se necesita alineación entre stakeholders de negocio y técnicos

**Inputs requeridos:**
- PRD aprobado (output de `flujo-01-discovery`)
- Acceso al equipo técnico para validación de factibilidad
- Contexto de restricciones técnicas existentes

**Output:** Solution Vision Document siguiendo `templates/solution/solution-vision-template.md`

## Pre-condiciones

- [ ] Gate-Discovery aprobado
- [ ] PRD disponible en `.raise/specs/{proyecto}-prd.md`
- [ ] Arquitecto o Tech Lead disponible para consulta
- [ ] Stakeholders de negocio disponibles para validación de alineamiento

---

## Pasos

### Paso 1: Cargar PRD y Contexto Técnico

Cargar el PRD aprobado y recopilar información sobre el contexto técnico:
- Stack tecnológico existente (si es brownfield)
- Restricciones de infraestructura
- Capacidades del equipo
- Integraciones requeridas

**Verificación:** El PRD está cargado y existe un resumen de 1 página del contexto técnico (stack, restricciones, integraciones conocidas).

> **Si no puedes continuar:** Contexto técnico desconocido → Ejecutar `patron-01-code-analysis` para brownfield, o documentar decisiones de stack para greenfield antes de continuar.

---

### Paso 2: Instanciar Template Solution Vision

Crear una copia del template de Solution Vision para el proyecto.

```bash
cp templates/solution/solution-vision-template.md .raise/specs/{proyecto}-vision.md
```

**Verificación:** Existe archivo `{proyecto}-vision.md` con todas las secciones del template presentes.

> **Si no puedes continuar:** Template no encontrado → Verificar ruta `templates/solution/solution-vision-template.md`. Si no existe, usar la versión del repositorio raise-config.

---

### Paso 3: Sintetizar Problem Statement

Extraer del PRD y reformular el problema en términos que conecten negocio con solución técnica:
- ¿Quién está afectado? → ¿Qué usuarios/sistemas interactúan?
- ¿Cuál es el impacto? → ¿Qué capacidad técnica falta?
- ¿Por qué ahora? → ¿Qué habilitador técnico lo hace posible?

**Verificación:** El Problem Statement en la Vision es más conciso que en el PRD y añade perspectiva técnica sin perder el enfoque de negocio.

> **Si no puedes continuar:** Problem Statement técnicamente vago → Revisar con Arquitecto para identificar el "dolor técnico" que subyace al problema de negocio.

---

### Paso 4: Definir Visión de Alto Nivel

Articular la solución propuesta en 2-3 párrafos:
- **Core value proposition**: ¿Qué valor único entrega?
- **Key differentiators**: ¿Qué lo hace diferente de alternativas?
- **Target outcomes**: ¿Qué estado futuro habilitamos?

**Verificación:** Un stakeholder de negocio y uno técnico pueden leer la visión y ambos entienden qué se construirá y por qué.

> **Si no puedes continuar:** Visión demasiado técnica o demasiado abstracta → Aplicar la prueba del "elevator pitch": ¿puedes explicarlo en 30 segundos a alguien no técnico?

---

### Paso 5: Mapear Alineamiento Estratégico

Conectar explícitamente los goals del PRD con la solución propuesta:

| Business Goal (del PRD) | Cómo la Solución lo Habilita |
|------------------------|------------------------------|
| Goal 1 | Mecanismo técnico que lo logra |
| Goal 2 | Mecanismo técnico que lo logra |

**Verificación:** Cada goal del PRD tiene al menos un mecanismo técnico asociado en la tabla de alineamiento.

> **Si no puedes continuar:** Goals sin mecanismo claro → Identificar gap: ¿falta requisito en PRD o falta capacidad técnica? Escalar a Product Owner o Arquitecto según corresponda.

---

### Paso 6: Documentar Impacto por Stakeholder

Para cada tipo de usuario/stakeholder identificado en el PRD:
- Current pain points (del PRD)
- Expected benefits (cómo la solución los resuelve)

**Verificación:** La tabla de User Impact cubre todos los stakeholders del PRD y cada uno tiene beneficios concretos, no genéricos.

> **Si no puedes continuar:** Beneficios genéricos ("mejor experiencia") → Reformular en términos de acciones: "El usuario podrá [acción] en [tiempo] en lugar de [situación actual]".

---

### Paso 7: Definir MVP Scope

Traducir el alcance del PRD a términos de entrega:
- **Must Have**: Funcionalidades sin las cuales no hay valor (MVP)
- **Nice to Have**: Funcionalidades que mejoran pero no son esenciales
- **Out of Scope**: Explícitamente excluido (heredado del PRD)

**Verificación:** Must Have contiene máximo 3-5 items. Si hay más, no es un MVP.

> **Si no puedes continuar:** MVP demasiado grande → Aplicar la pregunta: "¿Si solo pudiéramos entregar UNA cosa, cuál sería?" Iterar hasta tener un MVP enfocado.

---

### Paso 8: Establecer Métricas de Éxito Técnicas

Traducir las métricas de negocio del PRD a métricas técnicas observables:

| Business Metric (PRD) | Technical Metric | Target |
|----------------------|------------------|--------|
| "Reducir tiempo de proceso" | Response time P95 | < 500ms |
| "Soportar crecimiento" | Concurrent users | 10,000 |

**Verificación:** Cada métrica de negocio tiene al menos una métrica técnica asociada que es medible sin intervención manual.

> **Si no puedes continuar:** Métricas no medibles automáticamente → Definir cómo se instrumentará la métrica (logs, APM, analytics) antes de continuar.

---

### Paso 9: Documentar Constraints y Assumptions

Consolidar restricciones técnicas y supuestos:
- **Business Constraints**: Presupuesto, timeline, regulaciones
- **Technical Constraints**: Stack obligatorio, integraciones legacy, seguridad
- **Assumptions**: Lo que asumimos sin verificar formalmente

**Verificación:** Las constraints técnicas son específicas (no "debe ser seguro" sino "debe cumplir SOC2 Type II").

> **Si no puedes continuar:** Constraints vagas → Para cada constraint genérica, preguntar: "¿Qué pasaría específicamente si no se cumple?"

---

### Paso 10: Identificar Componentes de Alto Nivel

Esbozar los componentes principales de la solución (sin diseño detallado):
- Servicios/módulos principales
- Integraciones externas
- Flujos de datos de alto nivel

**Verificación:** Existe un diagrama o lista de 3-7 componentes principales. Si hay más de 7, el nivel de abstracción es muy bajo.

> **Si no puedes continuar:** Demasiado detalle → Este paso es "boxes and arrows", no diseño. Abstraer hasta tener máximo 7 componentes. El detalle va en Tech Design.

---

### Paso 11: Validar con Stakeholders

Presentar la Solution Vision para validación dual:
1. **Stakeholders de negocio**: ¿La visión refleja sus necesidades?
2. **Stakeholders técnicos**: ¿La visión es técnicamente factible?

**Verificación:** Hay aprobación explícita de al menos un representante de negocio Y uno técnico.

> **Si no puedes continuar:** Desacuerdo entre negocio y técnico → Facilitar sesión conjunta para resolver. Documentar trade-offs y decisiones tomadas.

---

## Output

**Artefacto producido:** Solution Vision Document

**Ubicación:** `.raise/specs/{proyecto}-vision.md`

**Siguiente paso:**
1. Ejecutar `gates/gate-vision.md` para validar
2. Si pasa el gate, proceder a `flujo-03-tech-design`

---

## Escalation Gate

Durante esta kata, escalar si:

| Condición | Escalar a |
|-----------|-----------|
| Goals de negocio técnicamente imposibles | Product Owner + Arquitecto |
| Restricciones técnicas bloquean MVP | Sponsor del proyecto |
| Desacuerdo negocio vs técnico no resuelto | Project Manager |

---

## Notas

### Diferencia con Tech Design
- **Solution Vision**: QUÉ construiremos y POR QUÉ (alineamiento)
- **Tech Design**: CÓMO lo construiremos (arquitectura detallada)

### Para Proyectos Pequeños
Si el proyecto es < 2 semanas, Solution Vision y Tech Design pueden combinarse en un único documento.

---

## Referencias

- Template: [`templates/solution/solution-vision-template.md`](../../templates/solution/solution-vision-template.md)
- Prerequisito: [`flujo-01-discovery`](./01-discovery.md)
- Siguiente kata: [`flujo-03-tech-design`](./03-tech-design.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 2
