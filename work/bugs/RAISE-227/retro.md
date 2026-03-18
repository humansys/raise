# Retrospective: RAISE-227

## Summary
- Root cause: `constructor_declaration` no visitado en el C# walker; `Symbol` sin campo `depends_on`
- Fix approach: helper `_extract_csharp_constructor_deps`, campo en `Symbol`, pass-through en `build_hierarchy`

## Heutagogical Checkpoint
1. Learned: Symbol es un modelo de transporte — sin `depends_on` no hay canal del scanner al analyzer. Toda la pipeline (scanner → model → hierarchy → analyzed component) debía tocar.
2. Process change: ninguno — TDD funcionó limpio, 3 commits atómicos claros.
3. Framework improvement: ninguno.
4. Capability gained: patrón para añadir extracción semántica a scanners de otros lenguajes.

## Patterns
- Added: none (patrón ya capturado en lógica del código)
- Reinforced: none evaluated
