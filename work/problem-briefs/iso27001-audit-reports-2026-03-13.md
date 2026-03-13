# Problem Brief: ISO 27001 Audit Report Generator

**Date:** 2026-03-13
**Stakeholder:** Vic (Konesh), Emilio
**Project:** raise-commons

---

## 1. Dominio

Visibilidad / control

## 2. Stakeholder primario

Equipo de desarrollo

## 3. Estado actual (gap)

El equipo de desarrollo no puede demostrar cumplimiento ISO 27001 porque la evidencia está dispersa en git, Jira y documentos sueltos.

## 4. Causa raíz (3 Whys)

1. **¿Por qué la evidencia está dispersa?** — Diversidad de herramientas y no ha habido inversión en automatización.
2. **¿Por qué no ha habido inversión en automatización?** — Presupuesto limitado.
3. **¿Por qué no se ha justificado esa inversión?** — Otros proyectos más estratégicos han tenido prioridad.

**Raíz:** La recolección de evidencia ISO no ha competido en prioridad contra proyectos de negocio porque no se ha demostrado que puede automatizarse a bajo costo.

## 5. Early signal (4 semanas)

Desaparece el proceso de preparación manual de auditoría.

## 6. Hipótesis

Si automatizamos la generación de reportes de evidencia ISO 27001 desde artefactos existentes (git, gates, sessions), entonces desaparece la preparación manual de auditoría para el equipo de desarrollo, medido por tiempo de preparación de evidencia pre-auditoría reducido >80% en 4 semanas.

---

**Siguiente paso:** `/rai-epic-design`
