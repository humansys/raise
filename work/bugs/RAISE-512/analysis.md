# RAISE-512: Analysis

## Classification: S — single causal chain

## 5 Whys

| Step | Statement |
|------|-----------|
| Problem | El toggle de tema solo afecta bloques de código, no el resto de la página |
| Why 1 | Los colores de fondo, texto y navegación no cambian al alternar `data-theme` |
| Why 2 | Todos los colores oscuros están definidos en `:root` (aplica siempre, sin condición) |
| Why 3 | Starlight alterna temas cambiando `data-theme="dark/light"` en `<html>`, pero `:root` siempre tiene mayor o igual especificidad que `[data-theme='dark']` y no hay bloque `[data-theme='light']` |
| Why 4 | La customización CSS original fijó un tema oscuro permanente sin preservar el mecanismo de switching de Starlight |
| Root cause | Los colores del tema oscuro están en `:root` en lugar de `[data-theme='dark']`, impidiendo que Starlight pueda alternarlos. Los bloques de código usan variables `--ec-*` independientes con su propio sistema de theming, por eso sí responden. |

## Countermeasure

Reestructurar `starlight.css`:
1. Mover los colores oscuros (bg, text, grays) de `:root` a `[data-theme='dark']`
2. Añadir bloque `[data-theme='light']` con los equivalentes en claro de Starlight
3. Mantener en `:root` solo lo que debe ser constante: accent colors, fonts, line-heights

Esto restaura el mecanismo de switching de Starlight sin perder la personalización visual.
