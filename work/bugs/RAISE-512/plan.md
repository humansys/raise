# RAISE-512: Fix Plan

## Tasks

### Task 1 — Reestructurar starlight.css
Mover colores de tema de `:root` a bloques `[data-theme='dark']` y `[data-theme='light']`.
Mantener en `:root`: accent colors, fonts, line-heights, link colors.

Estructura objetivo:
```css
:root {
  /* Constantes: accent, fonts, line-heights */
}

[data-theme='dark'] {
  /* Todos los colores oscuros actuales */
}

[data-theme='light'] {
  /* Equivalentes en claro (defaults de Starlight o valores propios) */
}
```

Verification: inspección visual manual — toggle cambia toda la página en ambas direcciones
Commit: `fix(RAISE-512): restore full-page theme switching in docs site`

## Final verification
- Light mode: fondo blanco/claro, texto oscuro, sidebar claro, código claro
- Dark mode: fondo negro, texto claro, sidebar oscuro, código oscuro
- Accent color (copper) se mantiene en ambos modos
