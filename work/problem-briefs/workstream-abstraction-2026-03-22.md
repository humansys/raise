# Problem Brief: Workstream Abstraction

> **Date:** 2026-03-22
> **Stakeholder:** Equipo de desarrollo
> **Domain:** Calidad / retrabajo
> **Next:** `/rai-epic-design` (includes grounding research on parallel workstream patterns)

---

## 1. Apuesta

Calidad / retrabajo — commits en ramas equivocadas, caos de branches por sesiones paralelas sin aislamiento.

## 2. Para quién

Equipo de desarrollo (el developer que trabaja con Rai en múltiples líneas de trabajo en paralelo).

## 3. Estado actual (Gap)

El desarrollador no puede trabajar en múltiples líneas de trabajo en paralelo de forma segura porque no existe una abstracción que agrupe sesiones en un workstream con aislamiento de branches, y las sesiones paralelas producen commits en ramas equivocadas generando caos.

## 4. Raíz (3 Whys)

1. **¿Por qué las sesiones paralelas producen commits en ramas equivocadas?** Claude Code por repo parece mantener una rama seleccionada — dos sesiones en el mismo repo compiten por el mismo estado de branch. (Requiere grounding research)
2. **¿Por qué abres dos sesiones sin worktree?** Porque quiere trabajar en diferentes cosas al mismo tiempo — cada cosa en paralelo es un "workstream".
3. **¿Por qué RaiSE no ofrece aislamiento por workstream?** No se diseñó ni se consideró. Se asumió trabajo secuencial (una cosa a la vez).

**Raíz:** RaiSE se diseñó asumiendo trabajo secuencial (una cosa a la vez), pero la práctica real es paralela — múltiples líneas de trabajo épica-level simultáneas que necesitan aislamiento de branches, sesiones agrupadas, y merge controlado. Conforme el agente gane autonomía, esto será el default, no la excepción. (Hipótesis — requiere grounding research en epic design)

## 5. Early Signal (4 semanas)

Queja que deja de escucharse: "Me hizo commit en la rama equivocada / tengo que hacer cherry-pick porque mezclé trabajo de dos cosas distintas."

## 6. Hipótesis

**Si** creamos una abstracción de workstream que agrupe sesiones con aislamiento de branches (worktrees) y merge controlado al cerrar, **entonces** desaparecerá la queja de "commit en rama equivocada / cherry-pick por trabajo mezclado" **para** el equipo de desarrollo, **medido por** cero incidentes de commits en ramas equivocadas y cero cherry-picks correctivos en 4 semanas.

## Relaciones

- **Depende de:** Session Identity Fix (Problem Brief 1) — workstream integra sesiones, necesita que la identidad de sesión sea confiable
- **Informa:** ADR-013v2 (Domain Cartridge Architecture) — workstream merge = merge de domain data across branches
- **Milestone:** v2.3+
- **Research needed:** Grounding on parallel workstream patterns, Claude Code branch behavior, worktree integration patterns
