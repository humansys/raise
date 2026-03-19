## Retrospective: RAISE-598

### Summary
- Root cause: CLI callback `doctor()` acumuló 3 concerns inline (JSON render, human render, fix application) sin extracción — cada feature adición incrementó nesting
- Fix approach: Extraer 3 sub-funciones privadas (`_render_json_output`, `_render_human_output`, `_apply_fixes`); callback queda como orquestador delgado

### Heutagogical Checkpoint

1. **Learned:** CLI callbacks son un punto ciego de complejidad acumulada. Cada `--flag` agrega un `if` inline que se siente pequeño solo, pero componen rápido. La función `doctor()` nunca tuvo un "bug" visible — simplemente se volvió difícil de razonar. El patrón de extracción es mecánico pero requiere disciplina de aplicarlo antes de que la complejidad llegue a 47.

2. **Process change:** Para CLI commands con múltiples output paths (--json, --verbose, etc.), extraer render functions desde el primer commit que agrega un segundo path — no esperar a que Sonar lo detecte.

3. **Framework improvement:** Podría añadir una guardrail: "CLI callbacks con más de 2 output paths deben extraer render functions." Por ahora no — esperemos a ver si el patrón aparece en otros callbacks antes de generalizar.

4. **Capability gained:** Confianza en el patrón refactor-sin-cambiar-tests: los tests de integración existentes son suficientes como regression harness para refactors estructurales. No necesito tests unitarios de las funciones privadas extraídas.

### Patterns
- Added: none — el insight de "CLI callbacks acumulan complejidad" no es nuevo, ya existe variante en el framework
- Reinforced: none evaluated
