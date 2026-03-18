# RAISE-570 — Analysis

## Root Cause (XS — 5 Whys)

1. Tests fallan con FileNotFoundError: 'git'
2. porque el ejecutable `git` no existe en el contenedor
3. porque `python:3.12-slim` no incluye git
4. porque `before_script` solo instala `libatomic1` (y uv)
5. **Root cause:** `git` nunca fue agregado al `apt-get install` del job `test`

## Fix Approach

`.gitlab-ci.yml` línea 21:

```diff
- apt-get update -qq && apt-get install -y -qq libatomic1
+ apt-get update -qq && apt-get install -y -qq libatomic1 git
```

Una palabra. No hay regression test que escribir en RED-first — el test ya existe
(`test_git_integration.py`). El "RED" es el pipeline CI actual fallando.
El "GREEN" es el pipeline pasando después del fix.

## Validation

Push branch → MR → verificar que pipeline pasa (los 4 tests verdes).
No reproducible localmente (dev tiene git instalado).
