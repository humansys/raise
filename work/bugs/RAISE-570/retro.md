# Retrospective: RAISE-570

## Summary
- Root cause: `python:3.12-slim` no incluye `git`; `compliance/extractors/git.py` llama `subprocess.run(['git', ...])` → `FileNotFoundError` en 4 tests de integración
- Fix approach: agregar `git` al `apt-get install` en `.gitlab-ci.yml` job `test` (1 palabra)

## Heutagogical Checkpoint

1. **Learned:** El CI fallaba en tests antes de llegar a pyright — RAISE-570 "desbloqueó" el pipeline y expuso un defecto latente de tipo en `DefaultAgentPlugin`. Un fix puede revelar bugs ocultos que el pipeline nunca alcanzaba.

2. **Process change:** Antes de cerrar un bugfix de CI, correr pytest + ruff + pyright localmente para detectar lo que el CI hubiera encontrado después del fix. No asumir que "tests pasan = CI pasa".

3. **Framework improvement:** pyright ya está en CLAUDE.md gates pero no se ejecutó antes del primer push. Candidato a pre-commit hook o checklist explícito en rai-bugfix Step 4.

4. **Capability gained:** Ishikawa aplicado a fallo de CI — distinguir causa raíz (git ausente en imagen) de factor contribuyente (CI nunca llegaba a pyright porque fallaba antes en tests).

## Patterns
- Added: none
- Reinforced: none evaluated
