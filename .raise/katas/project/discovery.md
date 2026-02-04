---
id: discovery
titulo: "Discovery: Creación del PRD"
work_cycle: project
frequency: once-per-epic
fase_metodologia: 1

prerequisites: []
template: templates/solution/project_requirements.md
gate: gates/gate-discovery.md
next_kata: project/vision

adaptable: true
shuhari:
  shu: "Seguir todos los pasos exactamente como se describen"
  ha: "Combinar pasos 4-5 si las métricas ya están claras desde el inicio"
  ri: "Crear kata de Discovery específica del dominio (ej: Discovery-SaaS, Discovery-API)"

version: 1.0.0
---

# Discovery: Creación del PRD

## Propósito

Transformar notas de reuniones de discovery y transcripciones en un Product Requirements Document (PRD) estructurado que capture el problema de negocio, metas, alcance, y requisitos de forma clara y testeable.

Esta kata es el punto de partida del ciclo de proyecto. Un PRD bien elaborado reduce ambigüedad, alinea stakeholders, y proporciona la base para la Project Vision.

## Contexto

**Cuándo usar:**
- Al iniciar un nuevo proyecto o épica
- Cuando hay notas de discovery dispersas que necesitan estructurarse
- Antes de comenzar cualquier trabajo de diseño técnico

**Inputs requeridos:**
- Notas de reuniones de discovery
- Acceso a stakeholders para clarificaciones
- Contexto del problema de negocio

**Output:**
- `governance/projects/{project}/prd.md` - PRD estructurado y validado

## Pasos

### Paso 1: Cargar Contexto Inicial

Recopilar todas las notas de reuniones y documentos previos disponibles. Consolidar información dispersa en una visión unificada del contexto.

**Verificación:** Existe contexto suficiente para articular el problema de negocio.

> **Si no puedes continuar:** Contexto disperso o incompleto → Solicitar al usuario que consolide las notas de reuniones antes de continuar.

### Paso 2: Instanciar Template PRD

Crear el archivo `governance/projects/{project}/prd.md` basado en el template de PRD.

**Verificación:** El archivo está listo para ser llenado con las secciones del template.

> **Si no puedes continuar:** Template no encontrado → Verificar que el template de PRD existe en la ubicación esperada.

### Paso 3: Articular el Problema de Negocio

Redactar sección "Problema de Negocio":
- Usuarios afectados y su contexto
- Impacto medible (costo, tiempo, oportunidad perdida)
- Urgencia y timing ("por qué ahora")

**Verificación:** Un stakeholder no técnico puede entender el problema sin explicación adicional.

> **Si no puedes continuar:** Problema no claro → Usar técnica de los "5 Por Qués" para clarificar el problema central. Iterar hasta llegar a la causa raíz.

### Paso 4: Definir Metas y Métricas de Éxito

Redactar secciones "Metas" y "Métricas de Éxito":
- Metas cuantificables alineadas con el problema
- Métricas con targets numéricos específicos
- Baseline actual vs. target esperado

**Verificación:** Cada meta tiene al menos una métrica asociada con target numérico.

> **Si no puedes continuar:** Métricas vagas → Preguntar "¿Cómo sabremos que tuvimos éxito?" hasta obtener números concretos. Si no hay datos, proponer rangos basados en industria.

### Paso 5: Documentar Alcance (In/Out)

Redactar sección "Alcance del Proyecto":
- In-Scope: qué SÍ está incluido (explícito)
- Out-of-Scope: qué NO está incluido (explícito)
- Áreas grises resueltas

**Verificación:** Las listas son mutuamente excluyentes y cubren las ambigüedades comunes.

> **Si no puedes continuar:** Alcance ambiguo → Listar 3-5 áreas grises (ej: "¿incluye móvil?", "¿incluye migración de datos?") y pedir decisión explícita.

### Paso 6: Listar Requisitos Funcionales

Redactar sección "Requisitos Funcionales":
- Formato: "El sistema DEBE [acción] cuando [condición]"
- Priorización MoSCoW (Must/Should/Could/Won't)
- Agrupación lógica por feature o dominio

**Verificación:** Cada requisito es testeable (puede expresarse como Given/When/Then).

> **Si no puedes continuar:** Requisitos vagos → Reformular como comportamiento observable. Preguntar: "¿Cuál es la acción específica y el resultado esperado?"

### Paso 7: Listar Requisitos No-Funcionales

Redactar sección "Requisitos No Funcionales":
- Rendimiento (tiempos de respuesta, throughput)
- Seguridad (autenticación, autorización, compliance)
- Disponibilidad (uptime, SLAs)
- Escalabilidad (usuarios concurrentes, volumen de datos)

**Verificación:** Cada requisito tiene un número o rango específico (no "debe ser rápido").

> **Si no puedes continuar:** NFRs sin cuantificar → Proponer números basados en estándares de la industria y pedir validación.

### Paso 8: Documentar Supuestos y Riesgos

Redactar secciones "Supuestos" y "Riesgos Identificados":
- Al menos 3 supuestos explícitos
- Al menos 3 riesgos con probabilidad, impacto, y mitigación

**Verificación:** Cada riesgo tiene una estrategia de mitigación asociada con owner.

> **Si no puedes continuar:** No se identifican riesgos → Usar técnica de pre-mortem: "Imagina que el proyecto fracasó en 6 meses, ¿qué salió mal?"

### Paso 9: Validar PRD con Stakeholders

Presentar el PRD para revisión y aprobación:
1. Enviar documento con 24-48 horas de anticipación
2. Agendar sesión de revisión (30-60 min)
3. Capturar feedback y ajustar
4. Obtener aprobación explícita (email, firma, o acta)

**Verificación:** El PRD tiene aprobación explícita de al menos un stakeholder clave.

> **Si no puedes continuar:** Stakeholder no disponible → Documentar intento de validación (fecha, canal) y proceder con nota de "pendiente aprobación formal". Establecer deadline antes de iniciar siguiente fase.

## Output

- **Artefacto:** Product Requirements Document (PRD)
- **Ubicación:** `governance/projects/{project}/prd.md`
- **Gate:** `gates/gate-discovery.md`
- **Siguiente kata:** `project/vision`

## Notas

### Para Proyectos Brownfield

Antes de ejecutar esta kata, considerar:
- Ejecutar `setup/analyze` para entender la base de código actual
- Ejecutar `setup/ecosystem` para mapear dependencias existentes
- Incluir sección de "Estado Actual" en el PRD

### Límite de Clarificaciones

Máximo 3 marcadores `[NEEDS CLARIFICATION]` en el documento final. Si hay más ambigüedades, escalar a sesión de clarificación con stakeholders.

## Referencias

- Gate de validación: `gates/gate-discovery.md`
- Template: `templates/solution/project_requirements.md`
- Técnica de los 5 Por Qués: Root cause analysis
- MoSCoW prioritization: Must/Should/Could/Won't
