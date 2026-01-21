---
description: Generate a Technical Design document from an approved Solution Vision, following the 15 steps of kata flujo-03-tech-design.
handoffs:
  - label: Create Project Backlog
    agent: raise.5.backlog
    prompt: Create the project backlog from this Tech Design
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Populate the Tech Design template (`.specify/templates/raise/tech/tech_design.md`) with content derived from the Solution Vision, producing `specs/main/tech_design.md`.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load the template from `.specify/templates/raise/tech/tech_design.md`.
   - Prepare output file at `specs/main/tech_design.md`.

2. **Paso 1: Cargar Vision y Contexto Técnico**:
   - Cargar `specs/main/solution_vision.md` como input principal.
   - Cargar `specs/main/project_requirements.md` (PRD) como referencia de requisitos.
   - Recopilar documentación técnica adicional si existe (APIs, schemas, etc.).
   - **Verificación**: La Solution Vision existe y el contexto técnico del proyecto está claro.
   - > **Si no puedes continuar**: Solution Vision no encontrada → **JIDOKA**: Ejecutar `/raise.2.vision` primero. PRD faltante → Ejecutar `/raise.1.discovery` primero. Contexto técnico desconocido → Para brownfield, ejecutar `/raise.1.analyze`.

3. **Paso 2: Instanciar Template Tech Design**:
   - Copiar template a `specs/main/tech_design.md`.
   - Completar metadatos del frontmatter YAML: document_id, title, project_name, client, version, date, author.
   - Agregar `related_docs` referenciando la Solution Vision y PRD.
   - Establecer status como "Draft".
   - **Verificación**: El archivo existe con todos los metadatos completados (no placeholders).
   - > **Si no puedes continuar**: Template no encontrado → Verificar ruta `.specify/templates/raise/tech/tech_design.md`.

4. **Paso 3: Definir Visión General Técnica**:
   - Completar sección "1. Visión General y Objetivo".
   - Resumir el objetivo desde perspectiva técnica.
   - Identificar el problema técnico central a resolver.
   - Conectar con los goals de la Solution Vision.
   - **Verificación**: La visión técnica es comprensible para un desarrollador que no ha leído el PRD, pero está claramente alineada con los objetivos de negocio.
   - > **Si no puedes continuar**: Visión desconectada del negocio → Revisar Solution Vision y extraer los mecanismos técnicos identificados en el paso de alineamiento estratégico.

5. **Paso 4: Describir Solución Propuesta**:
   - Completar sección "2. Solución Propuesta".
   - Describir el enfoque técnico de alto nivel.
   - Listar las principales piezas/componentes involucrados.
   - Documentar decisiones arquitectónicas fundamentales (monolito vs microservicios, sync vs async, etc.).
   - **Verificación**: Un desarrollador senior puede entender el approach en 5 minutos de lectura.
   - > **Si no puedes continuar**: Múltiples approaches válidos sin decisión → Documentar alternativas en sección "10. Alternativas Consideradas" y marcar con [NEEDS CLARIFICATION] para escalar a Arquitecto.

6. **Paso 5: Detallar Arquitectura de Componentes**:
   - Completar sección "3. Arquitectura y Desglose de Componentes".
   - Documentar **Componentes Nuevos**: nombre, propósito, responsabilidades, lenguaje/framework.
   - Documentar **Componentes Modificados**: qué cambia y por qué, impacto en dependientes.
   - Documentar **Servicios Externos**: integraciones requeridas, endpoints específicos.
   - Crear diagrama Mermaid mostrando componentes y relaciones.
   - **Verificación**: Existe diagrama que muestra todos los componentes y sus relaciones. Cada componente tiene responsabilidad única (SRP).
   - > **Si no puedes continuar**: Componentes con responsabilidades mezcladas → Aplicar principio de responsabilidad única. Si un componente hace "X e Y", considerar separar.

7. **Paso 6: Documentar Flujos de Datos**:
   - Completar sección "4. Flujo de Datos".
   - Documentar origen de los datos.
   - Describir transformaciones aplicadas.
   - Indicar destino de almacenamiento.
   - Distinguir flujos síncronos vs asíncronos.
   - **Verificación**: Para cada input del sistema, se puede trazar el camino hasta su destino final.
   - > **Si no puedes continuar**: Flujos incompletos → Identificar cada "entrada" al sistema (API call, evento, cron) y documentar qué pasa con los datos hasta que se persisten o responden.

8. **Paso 7: Especificar Contratos de API**:
   - Completar sección "5. Contrato(s) de API".
   - Documentar cada endpoint: método, ruta, descripción.
   - Especificar request body/params con tipos.
   - Especificar response body con tipos.
   - Listar códigos de error posibles.
   - **Verificación**: Cada endpoint tiene ejemplo de request y response. Los contratos son suficientes para que un consumidor pueda implementar sin preguntas.
   - > **Si no puedes continuar**: Contratos ambiguos → Para cada campo, definir tipo, requerido/opcional, y validaciones. Si es enum, listar valores posibles.

9. **Paso 8: Diseñar Modelo de Datos**:
   - Completar sección "6. Cambios en el Modelo de Datos".
   - Documentar nuevas tablas/colecciones.
   - Documentar campos nuevos en tablas existentes.
   - Especificar índices requeridos.
   - Describir estrategia de migración.
   - **Verificación**: El modelo soporta todos los requisitos funcionales del PRD. Las relaciones están normalizadas apropiadamente.
   - > **Si no puedes continuar**: Requisitos no mapeados a modelo → Revisar cada requisito funcional y verificar qué datos necesita persistir. Añadir entidades/campos faltantes.

10. **Paso 9: Documentar Algoritmos Clave**:
    - Completar sección "7. Algoritmos / Lógica Clave".
    - Documentar lógica de negocio no obvia.
    - Describir algoritmos de procesamiento complejos.
    - Explicar reglas de validación complejas.
    - **Verificación**: La lógica compleja está documentada con pseudocódigo o descripción paso a paso.
    - > **Si no puedes continuar**: Lógica no clara → Marcar con [NEEDS CLARIFICATION] y preguntar: "¿Qué pasa cuando [caso edge]?" hasta cubrir los escenarios no obvios.

11. **Paso 10: Especificar Consideraciones de Seguridad**:
    - Completar sección "8. Consideraciones de Seguridad".
    - Documentar autenticación (quién puede acceder).
    - Documentar autorización (qué puede hacer cada rol).
    - Identificar datos sensibles y cómo se protegen.
    - Listar vulnerabilidades mitigadas.
    - **Verificación**: Cada endpoint tiene definido quién puede invocarlo. Los datos sensibles tienen estrategia de protección.
    - > **Si no puedes continuar**: Requisitos de seguridad no claros → Revisar NFRs del PRD. Si no hay, asumir mínimo: autenticación requerida, datos PII encriptados. Documentar estos defaults.

12. **Paso 11: Definir Estrategia de Errores**:
    - Completar sección "9. Estrategia de Manejo de Errores".
    - Clasificar tipos de errores esperados.
    - Definir formato de respuesta de error.
    - Establecer estrategia de logging.
    - Documentar políticas de recuperación/retry.
    - **Verificación**: Existe catálogo de códigos de error con mensaje y acción sugerida para el cliente.
    - > **Si no puedes continuar**: Sin estrategia de errores → Definir al menos: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (internal error) con formato consistente.

13. **Paso 12: Documentar Alternativas Consideradas**:
    - Completar sección "10. Alternativas Consideradas".
    - Documentar opciones técnicas evaluadas.
    - Explicar razón de rechazo de cada alternativa.
    - Describir trade-offs de la decisión tomada.
    - **Verificación**: Al menos 2 alternativas documentadas para las decisiones arquitectónicas principales.
    - > **Si no puedes continuar**: No hubo alternativas → Siempre hay alternativas. Documentar al menos: "hacer nada" y "approach opuesto" (ej: monolito vs microservicios) con razones de rechazo.

14. **Paso 13: Listar Preguntas y Riesgos**:
    - Completar sección "11. Preguntas Abiertas y Riesgos".
    - Documentar preguntas técnicas sin resolver.
    - Listar riesgos de implementación.
    - Identificar dependencias externas críticas.
    - **Verificación**: Cada pregunta tiene owner asignado. Cada riesgo tiene mitigación propuesta.
    - > **Si no puedes continuar**: Preguntas sin owner → Asignar cada pregunta al rol más apropiado (Arquitecto, Tech Lead, Product Owner) con fecha límite de respuesta.

15. **Paso 14: Definir Consideraciones para Estimación**:
    - Completar sección "13. Consideraciones para Estimación".
    - Listar factores de complejidad clave.
    - Documentar incertidumbres conocidas.
    - Identificar posibles optimizaciones/simplificaciones.
    - Documentar dependencias críticas que afectan esfuerzo.
    - Identificar oportunidades de reutilización.
    - **Verificación**: La sección proporciona información suficiente para el proceso de estimación.
    - > **Si no puedes continuar**: Sin información de estimación → Revisar decisiones arquitectónicas y extraer factores de complejidad de cada una.

16. **Paso 15: Definir Estrategia de Testing**:
    - Completar sección "14. Estrategia de Pruebas".
    - Definir tipos de pruebas necesarias (unit, integration, e2e).
    - Especificar cobertura esperada.
    - Documentar ambientes de prueba requeridos.
    - **Verificación**: La estrategia cubre el camino crítico del sistema (happy path + principales error cases).
    - > **Si no puedes continuar**: Sin estrategia clara → Mínimo: unit tests para lógica de negocio, integration tests para APIs, e2e para flujos críticos de usuario.

17. **Paso 16: Validar con Equipo Técnico**:
    - Indicar que el Tech Design debe presentarse para revisión técnica.
    - Recomendar walkthrough con Tech Lead/Arquitecto.
    - Sugerir revisión de peers (otros desarrolladores).
    - **Verificación**: Tech Design listo para aprobación por Arquitecto o Tech Lead.
    - > **Si no puedes continuar**: Feedback no resuelto → Priorizar feedback por impacto. Resolver blockers antes de continuar. Documentar decisiones de "no action" con justificación.

18. **Finalize & Validate**:
    - Confirm file existence with `check_file "specs/main/tech_design.md" "Tech Design Generation"`.
    - Ejecutar validación usando `.specify/gates/raise/gate-design.md`.
    - Run `.specify/scripts/bash/update-agent-context.sh`.
    - Verificar que el Tech Design cumple los criterios del gate:
      - [ ] Diagrama de arquitectura presente y claro
      - [ ] Flujos de datos trazables end-to-end
      - [ ] Contratos de API con request/response
      - [ ] Modelo de datos con entidades y relaciones
      - [ ] Seguridad (AuthN/AuthZ) por endpoint
      - [ ] Catálogo de errores estandarizado
      - [ ] Aprobación de Arquitecto/Tech Lead
    - Mostrar resumen:
      - "✓ Tech Design generado en specs/main/tech_design.md"
      - Para secciones vacías: "⚠ Sección '[nombre]' está vacía - revisar manualmente"
    - Mostrar handoff: "→ Siguiente paso: `/raise.5.backlog`"

## Notas

### Para Proyectos Brownfield
Antes de ejecutar este flujo, considerar ejecutar:
- `/raise.1.analyze` para análisis de código existente
- Mapeo de dependencias del ecosistema

### Nivel de Detalle por Tipo de Proyecto
- **Greenfield**: Más detalle en decisiones fundamentales (stack, patterns, infraestructura)
- **Brownfield**: Enfocarse en cambios y cómo integran con lo existente
- **Spike/POC**: Versión ligera enfocada en riesgos técnicos a validar

### Documentos Separados
Si el diseño es muy extenso, considerar documentos separados:
- `{proyecto}-api-spec.md` para contratos detallados
- `{proyecto}-data-model.md` para ERD completo
- `{proyecto}-security.md` para análisis de seguridad

## High-Signaling Guidelines

- **Output**: A single Markdown document (`specs/main/tech_design.md`) populated from the template.
- **Focus**: Technical architecture and "HOW", derived from the "WHAT" in Vision.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Stop and ask if Solution Vision is missing. For non-critical missing info, use [NEEDS CLARIFICATION] markers and continue with reasonable defaults.
- **LIMIT**: Maximum 5 [NEEDS CLARIFICATION] markers total. If more uncertainty, stop and clarify with stakeholders.

## AI Guidance

When executing this workflow:
1. **Role**: You are a Technical Architect populating a template—your output is the Tech Design document, not code.
2. **Be proactive**: Propose standard patterns (REST, GraphQL, event-driven) if not specified. Use industry defaults for security, error handling.
3. **Follow Katas**: Ensure every step and Jidoka block from `flujo-03-tech-design` is respected.
4. **Traceability**: Every technical decision should link back to a requirement in the PRD or a goal in the Vision.
5. **Gates**: Always run the reference gate at the end.
6. **Diagrams**: Use Mermaid syntax for architecture diagrams to ensure they render in Markdown viewers.
7. **Consistency**: Follow the structure pattern of `raise.1.discovery` and `raise.2.vision` commands.
