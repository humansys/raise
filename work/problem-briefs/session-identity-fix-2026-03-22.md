# Problem Brief: Session Identity Fix

> **Date:** 2026-03-22
> **Stakeholder:** Equipo de desarrollo
> **Domain:** Visibilidad / control
> **Next:** `/rai-epic-design`

---

## 1. Apuesta

Visibilidad y control — el developer no puede ver ni gestionar su trabajo de forma coherente a través de múltiples sesiones y environments.

## 2. Para quién

Equipo de desarrollo (el developer que trabaja con Rai en múltiples sesiones, environments y channels).

## 3. Estado actual (Gap)

El desarrollador no puede gestionar trabajo multi-sesión de forma coherente porque las sesiones están acopladas al environment (no al dev+repo), hay leakage cross-repo, y la numeración diverge entre environments del mismo developer.

## 4. Raíz (3 Whys)

1. **¿Por qué las sesiones están acopladas al environment?** Error de diseño — implementamos lo primero que se nos ocurrió.
2. **¿Por qué no se pensó bien?** Había sesgo hacia la privacidad de la sesión, que se ha ido disminuyendo con la práctica.
3. **¿Por qué se priorizó privacidad sobre trazabilidad?** Se asumió que la data de sesión era "íntima del dev", pero en realidad si usas RaiSE en un repo, tienes compromiso con la mejora continua — la telemetría personal es relevante a nivel repo, incluyendo tracking de sesiones per dev independientemente del channel.

**Raíz:** La sesión se diseñó como concepto privado del developer (fuera de git), cuando en realidad es un artefacto de trabajo del repo. La telemetría, el historial y la continuidad de sesiones son valor compartido que debe vivir en git, aislado por dev+repo, no por environment.

## 5. Early Signal (4 semanas)

Queja que deja de escucharse: "Abrí sesión y me salió contexto de otro repo / otra numeración / no encontró mi sesión anterior."

## 6. Hipótesis

**Si** movemos la data de sesión a git (aislada por dev+repo, independiente del environment/channel), **entonces** desaparecerá la queja de "contexto equivocado / sesión perdida / numeración rota" **para** el equipo de desarrollo, **medido por** cero incidentes de leakage cross-repo y continuidad de sesión entre environments en 4 semanas.

## Relaciones

- **Independiente de:** Workstream abstraction (segundo Problem Brief)
- **Habilita:** Workstream puede integrar sesiones correctamente solo si la identidad de sesión es confiable
- **Informa:** ADR-013v2 (Domain Cartridge Architecture) — session data como domain con sus propias reglas de merge
