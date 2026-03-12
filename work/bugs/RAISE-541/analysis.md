# RAISE-541: Analysis

## Root Cause

SonarQube detecta violaciones de 8 reglas que ruff/pyright no cubren.
No hubo análisis estático con Sonar en el ciclo local durante el desarrollo inicial.

## Causal Chain (5 Whys)

Problem → Sonar reporta ~60 violaciones en 8 reglas
Why1   → ruff/pyright no cubren S1192/S1172/S5713/S6019/S125/S7503/S5754/S7632
Why2   → SonarQube no estaba en el ciclo local (solo en CI/SonarCloud)
Why3   → SOP de sonarqube-local se escribió durante el ciclo pre-launch (SES-076)
Root cause → Gap de tooling local cubierto ahora; las violaciones son deuda acumulada

## Fix Approach

Fixes en orden de riesgo ascendente (sin cambio de comportamiento primero):

1. S125  — eliminar código comentado (0 riesgo)
2. S7632 — corregir syntax de # type: ignore (0 riesgo)
3. S5713 — eliminar exception redundante en except tuple (0 riesgo, misma semántica)
4. S7503 — quitar `async` sin `await` (riesgo bajo — requiere verificar callers)
5. S1172 — prefixar parámetros no usados con `_` (riesgo bajo — sin cambio de firma)
6. S6019 — corregir reluctant quantifiers en regex (riesgo medio — cambio de regex)
7. S1192 — extraer constantes de literales duplicados (riesgo bajo — refactor mecánico)
8. S5754 — reraise exception silenciada (riesgo medio — cambia comportamiento en error path)

## Not a root cause

"Human error" — las reglas no eran visibles localmente. Fix sistémico: SOP ya existe.
