---
id: L1-16-DoD-Historias-Usuario-kata
nivel: 1
tags: [dod, historias-usuario, proceso, calidad, raiSE, agentes-ia]
---

## L1-16: Definición y Uso del DoD para Historias de Usuario en Proyectos RaiSE

## Metadatos
- **Id**: L1-16-DoD-Historias-Usuario-kata
- **Nivel**: 1
- **Título**: Definición y Uso del DoD para Historias de Usuario en Proyectos RaiSE
- **Propósito**: Establecer un proceso repetible para definir, adaptar y aplicar una Definition of Done (DoD) coherente y verificable a nivel de Historia de Usuario (HU) en proyectos desarrollados con agentes de IA orquestados por un humano RaiSE.
- **Contexto**: Proyectos donde el desarrollo es realizado principalmente por agentes de IA (coder, TL, QA, arquitecto, etc.) bajo la orquestación de un humano, y donde las HUs son la unidad principal de planificación, ejecución y verificación de valor entregado. Esta kata se aplica cuando el proyecto ya cuenta con los artefactos esenciales de requisitos y diseño (PRD, visión de solución, diseño técnico general o por feature, HUs definidas y un plan de implementación por HU, o artefactos equivalentes según el proceso del proyecto).
- **Audiencia**: RaiSE Dev (humano orquestador), Product Owner, Tech Lead (humano o agente), QA (humano o agente), y cualquier agente de IA involucrado en la planificación, diseño, implementación, pruebas y documentación de HUs.

## Pre-condiciones
- Existe un **proyecto** definido con objetivos de negocio y técnicos claros.
- El proyecto ya cuenta con los artefactos esenciales de requisitos y diseño, al menos:
  - PRD creado.
  - Visión de Solución.
  - Diseño Técnico General y, cuando aplique, diseño técnico por feature.
  - Historias de Usuario documentadas individualmente.
  - Plan de Implementación por Historia de Usuario para la HU que se va a trabajar.
- Existe al menos una **Historia de Usuario candidata** (nueva o en refinamiento) con:
  - Un título claro.
  - Una descripción funcional preliminar.
  - Al menos un borrador de criterios de aceptación funcionales.
- El RaiSE Dev (humano orquestador) tiene acceso a:
  - Las políticas generales de calidad de la organización.
  - Las guías RaiSE relevantes (katas L0/L1 que apliquen al proyecto).
- Se ha decidido que el trabajo se ejecutará **con agentes de IA** (p.ej. RaiSE Coder, Tech Lead, Arquitecto, QA) y que el humano actuará como orquestador responsable de la calidad final.

## Pasos de la Kata

### Paso 1: Alinear el contexto de la HU y del proyecto
- **Acción**: 
  - Revisar la HU candidata para entender su objetivo de negocio, alcance funcional y dependencias.
  - Identificar el tipo de HU (p.ej. funcional, técnica, deuda, mejora de UX, tarea de infraestructura) y el nivel de riesgo (bajo, medio, alto) en términos de impacto y complejidad.
  - Asegurar que el contexto del proyecto (dominio, restricciones técnicas, prioridades de calidad) está claro para el RaiSE Dev y para los agentes que participarán.
- **Criterios de Aceptación**:
  - El tipo de HU y su nivel de riesgo están explícitamente documentados en la HU.
  - Se han registrado las principales dependencias (otros servicios, módulos, integraciones) asociadas a la HU.
  - El RaiSE Dev puede explicar en 1–2 frases el objetivo de la HU y por qué es importante.

### Paso 2: Identificar fuentes de criterios de calidad para el DoD
- **Acción**:
  - Recopilar las fuentes que condicionan la calidad de la HU, incluyendo:
    - Políticas de calidad organizacionales (seguridad, cumplimiento, rendimiento, observabilidad, accesibilidad, etc.).
    - Estándares de proyecto (naming, arquitectura, testing, documentación).
    - Requisitos no funcionales relevantes para el dominio de la HU.
  - Explicitar qué fuentes serán obligatorias para todas las HUs del proyecto y cuáles son opcionales o contextuales.
- **Criterios de Aceptación**:
  - Existe una lista clara de fuentes de calidad referenciadas para la HU (o, idealmente, para todas las HUs del proyecto).
  - Cada fuente está etiquetada como **obligatoria** u **opcional/contextual**.
  - Los agentes de IA pueden acceder (vía contexto) a esta lista para consultarla al generar o verificar el DoD.

### Paso 3: Definir la estructura estándar del DoD a nivel de HU
- **Acción**:
  - Definir una **plantilla estándar de DoD-HU** en formato de checklist, que pueda reutilizarse en todas las HUs del proyecto.
  - Incluir, como mínimo, las siguientes categorías:
    - **Funcionalidad** (cumplimiento de criterios de aceptación).
    - **Calidad técnica** (arquitectura, patrones, manejo de errores, seguridad básica, rendimiento esperado).
    - **Testing** (unitario, integración, e2e, pruebas asistidas por IA según aplique).
    - **Documentación** (técnica, de usuario, SAR, notas de cambio, diagramas si aplica).
    - **Operaciones y observabilidad** (logs, métricas, alertas, feature flags, rollback seguro).
    - **Experiencia de usuario y accesibilidad** (cuando aplique).
  - Definir un formato consistente, por ejemplo:
    - `[ ] Categoría: ítem concreto verificable`.
- **Criterios de Aceptación**:
  - Existe una plantilla de DoD-HU documentada y versionada en el repositorio del proyecto.
  - Cada categoría tiene al menos 2–3 ítems genéricos que se puedan especializar por HU.
  - El formato de la plantilla es fácilmente consumible por agentes de IA (markdown claro y estructurado).

### Paso 4: Derivar los ítems funcionales específicos de la HU
- **Acción**:
  - Tomar los criterios de aceptación de la HU (o derivarlos si aún son vagos) y convertirlos en ítems de DoD concretos y verificables.
  - Asegurar que cada criterio de aceptación tiene al menos un ítem de DoD que exprese cómo se validará (por ejemplo, vía test automatizado, escenario de prueba manual, demo funcional).
  - En caso de ambigüedad, el RaiSE Dev coordina (con PO/agentes) la clarificación necesaria antes de cerrar el DoD funcional.
- **Criterios de Aceptación**:
  - No existe ningún criterio de aceptación sin un ítem de DoD asociado.
  - Cada ítem funcional de DoD está redactado en términos observables (input, comportamiento esperado, resultado).
  - Las pruebas (manuales o automatizadas) necesarias para validar cada ítem funcional están identificadas.

### Paso 5: Derivar los ítems de calidad técnica, testing y seguridad
- **Acción**:
  - A partir de las fuentes de calidad y la plantilla estándar, instanciar los ítems técnicos que apliquen a esta HU, por ejemplo:
    - Patrón arquitectónico correcto aplicado (según katas L2/L3 relevantes).
    - Manejo de errores y fallos con degradación controlada.
    - Validaciones de entrada y sanitización de datos.
    - Pruebas unitarias mínimas por componente/función modificada.
    - Pruebas de integración en puntos críticos.
    - Consideraciones de seguridad (autenticación, autorización, gestión de secretos, protección de datos).
  - Ajustar el nivel de exigencia según el riesgo de la HU (mayor riesgo ⇒ DoD técnico más estricto).
- **Criterios de Aceptación**:
  - El DoD incluye ítems explícitos sobre:
    - Patrón arquitectónico y convenciones técnicas.
    - Testing (tipos de pruebas y cobertura mínima esperada).
    - Seguridad y manejo de errores relevantes al contexto.
  - Para cada ítem técnico se indica cómo se verificará (revisión de código, ejecución de suite de tests, revisión de logs, etc.).

### Paso 6: Incluir ítems de documentación y conocimiento
- **Acción**:
  - Definir qué documentación debe quedar actualizada o creada cuando la HU se marque como Done, por ejemplo:
    - Actualización de SAR o documentación arquitectónica impactada.
    - Documentación de API (contratos, ejemplos de uso, cambios de versiones).
    - Notas de despliegue y cambios relevantes para otros equipos.
    - Manuales de usuario o ayuda contextual si aplica.
  - Asegurar que la documentación es accesible tanto para humanos como para agentes de IA en futuras iteraciones.
- **Criterios de Aceptación**:
  - El DoD contiene al menos un ítem de documentación asociado a cada artefacto relevante que pueda verse afectado.
  - Se especifica la ubicación donde deberá residir la documentación (ruta de archivo, sección de wiki, etc.).
  - La HU no puede cerrarse sin que estos ítems estén marcados como completados.

### Paso 7: Mapear ítems de DoD a roles y agentes de IA
- **Acción**:
  - Para cada ítem del DoD, asignar explícitamente:
    - El **responsable primario** (puede ser un agente de IA en un rol específico: Coder, TL, QA, Arquitecto).
    - El **responsable de validación** (si difiere del responsable primario; habitualmente el RaiSE Dev humano o un agente de QA/TL).
  - Documentar este mapeo en la HU o en el plan de implementación para que los agentes lo usen como guía de ejecución y verificación.
- **Criterios de Aceptación**:
  - No existe ningún ítem de DoD sin responsable primario claramente asignado.
  - Los ítems críticos (seguridad, cambios arquitectónicos, impactos en otros sistemas) tienen responsable de validación explícito.
  - Los agentes de IA pueden inferir, a partir de la HU, qué tareas deben ejecutar para cumplir cada ítem del DoD.

### Paso 8: Validar y congelar el DoD de la HU antes de la implementación
- **Acción**:
  - Revisar el DoD propuesto con los stakeholders relevantes (PO, TL, QA, Arquitecto; humanos o agentes) y realizar los ajustes necesarios.
  - Acordar qué partes del DoD son **obligatorias para considerar la HU como Done en este ciclo** y cuáles podrían postergarse explícitamente (con justificación).
  - Marcar el DoD como "congelado" para la ejecución, permitiendo solo ajustes controlados durante el sprint/ciclo.
- **Criterios de Aceptación**:
  - El DoD de la HU está revisado y aceptado por al menos el RaiSE Dev humano y un rol de negocio (p.ej. PO).
  - Los ítems del DoD están clasificados como:
    - Obligatorios en este ciclo.
    - Diferibles (con fecha/criterio claro para su abordaje futuro).
  - El estado del DoD (versión y fecha) está registrado junto a la HU.

### Paso 9: Integrar el DoD en los artefactos del flujo de trabajo
- **Acción**:
  - Incluir el DoD completo (o un enlace directo a él) en el artefacto donde vive la HU (p.ej. ticket de issue tracker, YAML de HU, documento de especificación).
  - Asegurar que el plan de implementación de la HU (definido según el proceso estándar del proyecto) referencia los ítems del DoD y, cuando sea útil, los descompone en tareas técnicas o sub-tareas asignables a agentes.
  - Configurar, si aplica, automatizaciones o checklists en la herramienta de gestión para que el DoD se vea y se marque durante la ejecución.
- **Criterios de Aceptación**:
  - Cualquier persona o agente que abra la HU puede ver de forma inmediata y clara el DoD asociado.
  - Existe una trazabilidad visible entre los ítems del DoD y las tareas/sub-tareas del plan de implementación.
  - Las herramientas de gestión utilizadas (issue tracker, CI/CD, etc.) reflejan el estado de cumplimiento de los ítems del DoD.

### Paso 10: Usar el DoD como checklist de verificación al cierre de la HU
- **Acción**:
  - Al finalizar la implementación, el RaiSE Dev lidera (junto con los agentes relevantes) una revisión de cierre usando el DoD como checklist:
    - Verificar cada ítem del DoD, marcándolo como cumplido o no cumplido.
    - Revisar evidencias: código, resultados de tests, documentación actualizada, métricas, etc.
  - Si hay ítems obligatorios no cumplidos, la HU **no** debe marcarse como Done; en su lugar:
    - Se ajusta el plan y se completan los ítems pendientes, o
    - Se renegocia el alcance con negocio y se registra explícitamente la excepción.
- **Criterios de Aceptación**:
  - No se marca ninguna HU como Done sin haber pasado por la verificación explícita contra su DoD.
  - Para cada ítem del DoD, existe evidencia razonable de cumplimiento (en código, tests, documentación o herramientas de observabilidad).
  - Cualquier excepción o ítem diferido queda documentado con su justificación y plan de seguimiento.

## Post-condiciones
- Cada HU relevante del proyecto dispone de un **DoD explícito, versionado y verificable**, asociado directamente a la HU.
- El DoD de la HU cubre de manera balanceada:
  - Funcionalidad.
  - Calidad técnica, seguridad y testing.
  - Documentación y conocimiento.
  - Operabilidad y observabilidad cuando aplique.
- Los agentes de IA utilizan el DoD de cada HU como guía para:
  - Ajustar y ejecutar el plan de implementación definido para esa HU.
  - Ejecutar la implementación y las pruebas.
  - Verificar el cumplimiento antes de marcar la HU como Done.
- El RaiSE Dev mantiene el control y la responsabilidad final sobre la calidad, usando el DoD como contrato explícito entre negocio, tecnología y agentes de IA.

## Notas Adicionales
- Esta Kata debe revisarse y ajustarse periódicamente conforme el proyecto madure y se obtenga experiencia práctica con el uso de DoD a nivel de HUs.
- Es recomendable mantener ejemplos de DoD reales (anonimizados si es necesario) como referencia para nuevos miembros del equipo y para calibrar a los agentes de IA.
- Cuando cambien las políticas de calidad de la organización o del proyecto, se debe revisar esta Kata y las plantillas de DoD para mantener la alineación.


