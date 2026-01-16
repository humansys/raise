# Normalization Report: patron/02-analisis-agnostico-codigo-fuente.md

**Processed**: 2026-01-12
**Coherence**: aligned
**Orquestador Approval**: pending

## Semantic Coherence Check

**Level**: patron
**Guiding Question**: ¿Qué forma?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the PATTERN for analyzing source code to generate essential documentation. It defines a reusable 4-phase template (API Surface Discovery, Dependencies Analysis, Business Logic & Resilience, Synthesis) that can be applied to any codebase regardless of technology stack. This is a structural pattern kata correctly placed in `patron/`.

## Jidoka Inline Changes

This kata has 10 steps (across 4 phases) that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 1.1 | Identificar Puntos de Entrada | ✅ Yes | ✅ Yes |
| 1.2 | Definir Contratos de Datos | ✅ Yes | ✅ Yes |
| 2.1 | Mapear Dependencias Salientes | ✅ Yes | ✅ Yes |
| 2.2 | Identificar Dependencias de Infraestructura | ✅ Yes | ✅ Yes |
| 3.1 | Extraer Conceptos del Dominio | ✅ Yes | ✅ Yes |
| 3.2 | Detectar Patrones de Resiliencia | ✅ Yes | ✅ Yes |
| 3.3 | Mapear Casos de Uso de Negocio | ✅ Yes | ✅ Yes |
| 4.1 | Ensamblar service-overview.md | ✅ Yes | ✅ Yes |
| 4.2 | Formalizar y Versionar Artefactos | ✅ Yes | ✅ Yes |
| 4.3 | Crear README para Documentación | ✅ Yes | ✅ Yes |

**Total Steps**: 10
**Steps Modified**: 10

### Jidoka Content Added

**Paso 1.1 - Endpoints:**
- **Verificación:** Existe una lista de endpoints con tipo, ruta y operaciones para cada punto de entrada del servicio.
- **Si no puedes continuar:** No se encuentran puntos de entrada → Verificar que el servicio tiene API pública; si es un worker/job, documentar los triggers en lugar de endpoints.

**Paso 1.2 - Contracts:**
- **Verificación:** Existe `contracts.md` o `contracts.yaml` con la estructura de request/response para cada endpoint identificado en 1.1.
- **Si no puedes continuar:** Contratos incompletos → Revisar endpoints sin documentar y completar la definición de sus modelos de datos.

**Paso 2.1 - Egress Dependencies:**
- **Verificación:** Existe `dependencies.yaml` con lista de servicios externos, tipo de comunicación, propósito y criticidad.
- **Si no puedes continuar:** Dependencias no detectadas → Revisar imports/using statements y archivos de configuración para identificar clientes de servicios externos.

**Paso 2.2 - Infrastructure:**
- **Verificación:** `dependencies.yaml` incluye sección de infraestructura con bases de datos, caché, brokers y su propósito.
- **Si no puedes continuar:** Infraestructura no documentada → Revisar archivos de configuración (docker-compose, appsettings, .env) para identificar servicios de infraestructura.

**Paso 3.1 - Domain Concepts:**
- **Verificación:** Existe `domain-model.md` con entidades, agregados, objetos de valor e invariantes de negocio.
- **Si no puedes continuar:** Dominio no claro → Buscar carpetas Domain/Models/Entities o equivalentes; si es CRUD simple, documentar las entidades de persistencia como modelo de dominio.

**Paso 3.2 - Resilience Patterns:**
- **Verificación:** Existe `resilience-guide.md` con patrones implementados (retry, circuit breaker, timeouts) y anti-patrones detectados.
- **Si no puedes continuar:** No se detectan patrones → Documentar explícitamente "Sin patrones de resiliencia detectados" como hallazgo crítico para plan de mejora.

**Paso 3.3 - Use Cases:**
- **Verificación:** Existe `use-cases.md` con descripción de negocio para cada endpoint y trazabilidad endpoint→dominio.
- **Si no puedes continuar:** Casos de uso no claros → Consultar con stakeholder de negocio o inferir propósito del nombre del endpoint y sus operaciones.

**Paso 4.1 - Service Overview:**
- **Verificación:** Existe `service-overview.md` que permite entender el servicio en <5 minutos (propósito, bounded context, dependencias, dominio).
- **Si no puedes continuar:** Overview incompleto → Revisar artefactos de fases anteriores para consolidar información faltante.

**Paso 4.2 - Formalize Artifacts:**
- **Verificación:** Todos los artefactos (`contracts.md`, `dependencies.yaml`, `domain-model.md`, `resilience-guide.md`, `use-cases.md`) existen con metadatos de fecha y commit.
- **Si no puedes continuar:** Artefactos incompletos → Revisar la fase correspondiente (1-3) para generar los artefactos faltantes antes de versionar.

**Paso 4.3 - README:**
- **Verificación:** Existe `README.md` en la carpeta de documentación con tabla de contenidos y enlaces a cada artefacto generado.
- **Si no puedes continuar:** README sin enlaces → Verificar que todos los artefactos de 4.2 existen antes de enlazarlos en el README.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Frontmatter id | `L2-02-Analisis-Agnostico...` | `patron-02-analisis-agnostico-codigo-fuente` | ID format |
| Frontmatter nivel | `nivel: 2` | `nivel: patron` | Level naming |
| Metadatos Id | `L2-02-Analisis-Agnostico...` | `patron-02-analisis-agnostico-codigo-fuente` | ID format |
| Metadatos Nivel | `Nivel 2 (Componente Genérico)` | `Patrón` | Level naming |
| Contexto | `flujo-08 o flujo-09` | `flujo-08 o flujo-09` | Already correct |
| Notas | `Al igual que en L1-07` | (removed reference) | Deleted kata |

**Total Replacements**: 5 terminology changes

## Notes

1. **Full Jidoka coverage**: All 10 steps now have explicit verification criteria. Each step defines the specific artifact that should exist and provides recovery guidance.

2. **Artifact-focused Jidoka**: The verifications are tailored to the documentation artifacts produced by this pattern kata (contracts.md, dependencies.yaml, domain-model.md, etc.).

3. **L1-07 reference removed**: The original kata referenced `L1-07` (Generacion-Documentacion-Esencial-SAR) which was a project-specific kata that has been deleted. The principle of minimalist documentation was preserved without the broken reference.

4. **Already had strong structure**: This kata already had well-defined "Criterios de Aceptación" at each step. Jidoka Inline complements these with explicit verification checkpoints and correction paths.

5. **Preserved Audiencia**: "Arquitecto de Software, Líder Técnico, Desarrollador Senior" was preserved as these are job titles, not the deprecated "Developer" role term.

6. **No deprecated terminology found**: This kata did not use Practicante, Developer, DoD, or Reglas in a deprecated context.

7. **Pattern structure validated**: The 4-phase structure (Discovery → Dependencies → Business Logic → Synthesis) is a reusable pattern that answers "¿Qué forma?" for source code analysis.

---

**Report Generated**: 2026-01-12T01:15:00
