# RaiSE v2.1 Command Workflow Map

Este documento mapea la metodología conceptual (Katas/Fases) con los comandos específicos de SpecKit y RaiSE.

## 🗺️ El "Golden Path" (Flujo Principal)

Este es el orden lógico para llevar una idea desde el concepto hasta el código. Los pasos marcados como *(Opcional)* recomiendan su uso para mayor calidad.

| Fase | Meta Conceptual | Comando | Ubicación | Input (Entrada) | Output (Entregable) | Validation Gate |
|-------|-----------------|---------|-----------|-------|-------------------|-----------------|
| **0** | **Foundation** | `/speckit.2.constitution` | `01-onboarding/` | Principios del Proyecto | `.specify/memory/constitution.md` | - |
| **1** | **Discovery** | `/raise.1.discovery` | `02-projects/` | Notas crudas / Transcripciones | `specs/main/project_requirements.md` (PRD) | `gate-discovery` |
| **2** | **Solution Vision** | `/raise.2.vision` | `02-projects/` | PRD | `specs/main/solution_vision.md` | `gate-vision` |
| **3** | **Tech Design (Spec)** | `/speckit.1.specify` | `03-feature/` | Vision + Idea de la Feature | `specs/00N-feature/spec.md` | `gate-design` |
| **3b** | **Clarification** *(Opcional)* | `/speckit.2.clarify` | `03-feature/` | Spec incompleta | Spec refinada (sin ambigüedades) | - |
| **4** | **Implementation Plan** | `/speckit.3.plan` | `03-feature/` | Spec refinada | `specs/00N-feature/plan.md` | `gate-plan` |
| **5** | **Backlog/Tasks** | `/speckit.4.tasks` | `03-feature/` | Plan + Spec | `specs/00N-feature/tasks.md` | `gate-backlog` |
| **5b** | **Consistency Analysis** *(Opcional)* | `/speckit.5.analyze` | `03-feature/` | Tasks + Plan + Spec | Reporte de consistencia | - |
| **6** | **Implementation** | `/speckit.6.implement` | `03-feature/` | Tasks | Código Fuente | `gate-code` |

## 🛠️ Comandos de Soporte y Calidad

Herramientas transversales para mantener la calidad y consistencia.

| Comando | Carpeta | Categoría | Propósito | Cuándo usar |
|---------|---------|-----------|-----------|-------------|
| `/speckit.util.checklist` | `03-feature/` | Calidad | Genera listas de verificación personalizadas. | Durante la especificación o tareas. |
| `/speckit.util.issues` | `03-feature/` | Calidad | Convierte tareas a issues de GitLab. | Después de generar el backlog. |
| `/raise.1.analyze` | `01-onboarding/` | Análisis | Genera reporte SAR (Software Architecture Reconstruction). | Al inicio (Phase 0) o en proyectos brownfield. |
| `/raise.3.ecosystem` | `02-projects/` | Análisis | Visualiza servicios externos e integraciones. | Durante Phase 1 (Discovery) o Phase 4 (Planning). |
| `/raise.rules.generate` | `01-onboarding/` | Gobierno | Genera reglas base (`.cursorrules` / `.windsurf`). | Al configurar el repositorio (Phase 0). |
| `/raise.rules.edit` | `01-onboarding/` | Gobierno | Refina reglas de codificación existentes. | Cuando cambian los estándares del equipo. |

## 🛑 Principio Jidoka (Validación)

Cada comando verifica automáticamente sus dependencias. Si intentas ejecutar un paso avanzado sin el anterior:

1.  **STOP**: El agente te advertirá que faltan artefactos previos (ej: intentar `/speckit.3.plan` sin haber hecho `/speckit.1.specify`).
2.  **FIX**: Regresa a la fase faltante.
3.  **RESUME**: Continúa con el flujo una vez validado el input.
