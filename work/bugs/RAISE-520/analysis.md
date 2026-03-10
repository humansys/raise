# RAISE-520 Analysis — Path injection via --memory-dir flag

## Classification: XS — cause evident

## Root Cause

`memory_dir` recibido vía CLI flag se usa directamente sin canonicalizar.
`pathlib.Path` preserva secuencias `../` hasta que se resuelven en disco,
permitiendo que un valor como `../../../../tmp/evil` apunte fuera del proyecto.

## Causal Chain (5 Whys collapsed for XS)

Problem → `--memory-dir ../../../../tmp/evil` escribe fuera del proyecto
Why → path no se canonicaliza antes de usarlo
Why → no se llama `.resolve()` al recibirlo del CLI
Root cause → el flag fue agregado como override de poder sin sanitización defensiva

## Fix Approach

Aplicar `.resolve()` en los 3 puntos donde `memory_dir` se asigna a `mem_dir`:
- `pattern.py:110` (reinforce)
- `pattern.py:211` (add)
- `pattern.py:282` (sync)

`.resolve()` convierte el path a absoluto canónico, eliminando `../` components.
Comportamiento legítimo preservado — paths válidos resuelven igual.
