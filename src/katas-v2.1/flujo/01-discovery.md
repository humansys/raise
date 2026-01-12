---
id: flujo-01-discovery
nivel: flujo
titulo: "Discovery: Creación del PRD"
audience: beginner
template_asociado: templates/solution/project_requirements.md
validation_gate: gates/gate-discovery.md
prerequisites: []
fase_metodologia: 1
tags: [discovery, prd, requisitos, fase-1]
version: 1.0.0
---

# Discovery: Creación del PRD

## Propósito

Transformar las notas de reuniones de discovery y el contexto inicial del proyecto en un PRD (Product Requirements Document) estructurado que sirva como contrato entre stakeholders y el equipo técnico.

Esta kata responde a la pregunta: **¿Cómo fluye la información desde el discovery inicial hacia un PRD validado?**

## Contexto

**Cuándo usar:**
- Al iniciar un nuevo proyecto
- Al comenzar una nueva épica o feature significativo
- Después de las reuniones iniciales con stakeholders

**Inputs requeridos:**
- Notas de reuniones de discovery
- Contexto del proyecto (Fase 0 completada)
- Acceso a stakeholders para clarificaciones

**Output:** PRD completado siguiendo `templates/solution/project_requirements.md`

## Pre-condiciones

- [ ] Fase 0 (Contexto) completada: stakeholders identificados, tecnologías definidas, restricciones documentadas
- [ ] Al menos una reunión de discovery realizada
- [ ] Product Owner o stakeholder clave disponible para validación

---

## Pasos

### Paso 1: Cargar Contexto Inicial

Recopilar todas las notas de reuniones, correos y documentos previos que capturen la visión inicial del proyecto. Consolidar en un único lugar accesible.

**Verificación:** Existe un documento o carpeta con todo el contexto inicial consolidado. El Orquestador confirma que no falta información crítica.

> **Si no puedes continuar:** Contexto disperso o incompleto → Solicitar al Orquestador que consolide las notas de reuniones en un único documento antes de continuar.

---

### Paso 2: Instanciar Template PRD

Crear una copia del template `templates/solution/project_requirements.md` con el nombre del proyecto.

```bash
cp templates/solution/project_requirements.md .raise/specs/{proyecto}-prd.md
```

**Verificación:** Existe archivo `{proyecto}-prd.md` con todas las secciones del template vacías pero presentes.

> **Si no puedes continuar:** Template no encontrado → Verificar que `templates/solution/project_requirements.md` existe en el repositorio. Si no existe, crear desde el template base de RaiSE.

---

### Paso 3: Articular el Problema de Negocio

Completar la sección "Problem Statement" del PRD, respondiendo:
- ¿Quién tiene el problema? (usuarios afectados)
- ¿Cuál es el impacto del problema? (costo, tiempo, frustración)
- ¿Por qué es importante resolverlo ahora? (urgencia, oportunidad)

**Verificación:** La sección Problem Statement está completa y un stakeholder no técnico puede entenderla sin explicación adicional.

> **Si no puedes continuar:** Problema no claro → Agendar sesión de 30 minutos con Product Owner para clarificar el problema central. Usar la técnica de los "5 Por Qués" si es necesario.

---

### Paso 4: Definir Metas y Métricas de Éxito

Completar la sección "Goals & Success Metrics" con:
- Metas de negocio cuantificables (qué queremos lograr)
- Métricas que indicarán éxito (cómo lo mediremos)
- Targets específicos (qué número es "suficiente")

**Verificación:** Cada meta tiene al menos una métrica asociada con target numérico. Ejemplo: "Reducir tiempo de procesamiento de 5 minutos a 30 segundos".

> **Si no puedes continuar:** Métricas vagas ("mejorar la experiencia") → Preguntar "¿Cómo sabremos que tuvimos éxito?" hasta obtener números concretos. Si el stakeholder no puede dar números, proponer rangos y pedir validación.

---

### Paso 5: Documentar Alcance (In/Out)

Completar la sección "Scope" especificando explícitamente:
- **In-Scope:** Lo que SÍ está incluido en este proyecto
- **Out-of-Scope:** Lo que NO está incluido (y por qué se excluye)

**Verificación:** Las listas In-Scope y Out-of-Scope son mutuamente excluyentes y cubren las áreas de ambigüedad común del dominio.

> **Si no puedes continuar:** Alcance ambiguo → Listar 3-5 áreas grises ("¿incluye reportes?", "¿incluye móvil?") y pedir decisión explícita a stakeholders. Documentar el razonamiento detrás de cada decisión.

---

### Paso 6: Listar Requisitos Funcionales

Completar la sección "Functional Requirements":
- Cada requisito describe QUÉ debe hacer el sistema
- Usar formato: "El sistema debe [acción] cuando [condición]"
- Priorizar usando MoSCoW (Must/Should/Could/Won't)

**Verificación:** Cada requisito funcional es testeable — se puede escribir un criterio de aceptación en formato Dado/Cuando/Entonces para él.

> **Si no puedes continuar:** Requisitos vagos ("el sistema debe ser fácil de usar") → Reformular como comportamiento observable. Preguntar: "¿Qué acción específica realiza el usuario y qué resultado espera ver?"

---

### Paso 7: Listar Requisitos No-Funcionales

Completar la sección "Non-Functional Requirements":
- Rendimiento (tiempos de respuesta, throughput)
- Seguridad (autenticación, autorización, datos sensibles)
- Disponibilidad (uptime, SLA)
- Escalabilidad (usuarios concurrentes, crecimiento)

**Verificación:** Cada requisito no-funcional tiene un número o rango específico, no solo una aspiración.

> **Si no puedes continuar:** NFRs sin cuantificar → Para cada NFR vago, proponer un número basado en estándares de la industria y pedir validación. Ejemplo: "¿Es aceptable 99.9% de uptime (8.7 horas de downtime al año)?"

---

### Paso 8: Documentar Supuestos y Riesgos

Completar las secciones finales:
- **Supuestos:** Lo que asumimos verdadero sin haber verificado formalmente
- **Riesgos:** Lo que podría salir mal y estrategias de mitigación

**Verificación:** Hay al menos 3 supuestos y 3 riesgos documentados. Cada riesgo tiene una estrategia de mitigación asociada.

> **Si no puedes continuar:** No se identifican riesgos → Usar técnica de pre-mortem: "Imagina que el proyecto fracasó, ¿qué salió mal?" También preguntar: "¿Qué pasaría si [recurso/dependencia clave] no está disponible?"

---

### Paso 9: Validar PRD con Stakeholders

Presentar el PRD completo a los stakeholders para revisión y aprobación.

Acciones:
1. Enviar PRD con 24-48 horas de anticipación
2. Agendar sesión de revisión (30-60 min)
3. Capturar feedback y ajustar
4. Obtener aprobación explícita

**Verificación:** El PRD tiene aprobación explícita (email, comentario en documento, o acta de reunión) de al menos un stakeholder clave.

> **Si no puedes continuar:** Stakeholder no disponible → Documentar intento de validación (fecha, canal) y proceder con nota de "pendiente aprobación formal". Establecer deadline para aprobación antes de iniciar Fase 2.

---

## Output

**Artefacto producido:** PRD (Product Requirements Document)

**Ubicación:** `.raise/specs/{proyecto}-prd.md`

**Siguiente paso:**
1. Ejecutar `gates/gate-discovery.md` para validar que el PRD cumple los criterios
2. Si pasa el gate, proceder a `flujo-02-solution-vision`

---

## Validation Gate

Este kata produce el input para **Gate-Discovery**. Los criterios del gate son:

- [ ] Problema de negocio articulado claramente
- [ ] Metas y métricas de éxito definidas con números
- [ ] Alcance (in/out) explícito
- [ ] Requisitos funcionales testeables
- [ ] Requisitos no funcionales cuantificados
- [ ] Supuestos y riesgos documentados
- [ ] Aprobación de al menos un stakeholder

Ver: `gates/gate-discovery.md`

---

## Notas

### Para Proyectos Pequeños
Si es un feature menor (< 1 semana de trabajo), el PRD puede ser más ligero:
- Combinar Problem Statement y Goals en un párrafo
- Listar solo requisitos Must-Have
- Omitir sección de Riesgos si el impacto es bajo

### Para Proyectos Brownfield
Antes de este kata, considerar ejecutar:
- `patron-01-code-analysis` para entender el código existente
- `patron-02-ecosystem-discovery` para mapear dependencias

---

## Referencias

- Template: [`templates/solution/project_requirements.md`](../../templates/solution/project_requirements.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md) §Fase 1
- Siguiente kata: [`flujo-02-solution-vision`](./02-solution-vision.md)
