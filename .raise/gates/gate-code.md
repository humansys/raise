---
id: gate-code
fase: 6
titulo: "Gate-Code: Validación del Código Implementado"
blocking: true
version: 1.0.0
---

# Gate-Code: Validación del Código Implementado

## Propósito

Verificar que el código implementado cumple los criterios de calidad, pasa todas las validaciones, y está listo para merge. Este gate implementa validación multinivel: funcional, estructural, arquitectónica y semántica.

## Cuándo Aplicar

- Después de completar `flujo-06-development`
- Antes de crear Pull Request
- Como pre-merge checklist

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Tests pasan** | `npm test` (o equivalente) exitoso |
| 2 | **Build exitoso** | `npm run build` sin errores |
| 3 | **Linting limpio** | Sin errores de linting |
| 4 | **AC cubiertos** | Cada criterio de aceptación implementado |
| 5 | **Guardrails cumplidos** | Código sigue guardrails del proyecto |
| 6 | **Revisión humana** | Orquestador ha revisado el código |
| 7 | **Commits limpios** | Mensajes siguen convención |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | Cobertura de tests | ≥80% en código nuevo |
| 9 | Documentación | Funciones públicas documentadas |
| 10 | No regresiones | Tests existentes siguen pasando |
| 11 | Performance | No degradación significativa |

---

## Validación Multinivel

### Nivel 1: Funcional
¿El código hace lo que debe?
- [ ] Criterios de aceptación cubiertos
- [ ] Happy path funciona
- [ ] Error cases manejados

### Nivel 2: Estructural
¿El código está bien escrito?
- [ ] Sigue convenciones del proyecto
- [ ] Naming claro y consistente
- [ ] Sin código duplicado
- [ ] Complejidad manejable

### Nivel 3: Arquitectónico
¿El código encaja en el sistema?
- [ ] Alineado con Tech Design
- [ ] Dependencias correctas
- [ ] Capas respetadas
- [ ] No acoplamientos indebidos

### Nivel 4: Semántico
¿El código refleja el negocio?
- [ ] Nombrado refleja dominio
- [ ] Reglas de negocio correctas
- [ ] Edge cases del dominio cubiertos

---

## Checklist Rápido

```markdown
## Gate-Code Checklist

**User Story:** {US-ID}
**Branch:** {branch-name}
**Fecha:** YYYY-MM-DD

### Automatizados
- [ ] 1. Tests pasan: `npm test` ✓
- [ ] 2. Build: `npm run build` ✓
- [ ] 3. Lint: `npm run lint` ✓

### Funcionales
- [ ] 4. AC 1: [descripción] implementado
- [ ] 4. AC 2: [descripción] implementado
- [ ] 4. AC N: ...

### Guardrails
- [ ] 5. guard-001: ✓
- [ ] 5. guard-002: ✓
- [ ] 5. [lista de guardrails aplicables]

### Review
- [ ] 6. Orquestador ha revisado código
- [ ] 6. Feedback incorporado

### Commits
- [ ] 7. Mensajes siguen convención
- [ ] 7. Commits atómicos y descriptivos

### Recomendados
- [ ] 8. Cobertura ≥80% en código nuevo
- [ ] 9. Funciones públicas documentadas
- [ ] 10. No hay tests rotos preexistentes
- [ ] 11. Performance verificada

### Resultado
- [ ] **PASS** - Listo para PR/merge
- [ ] **FAIL** - Issues pendientes: _______________

**Revisado por:** _______________
**Fecha:** _______________
```

---

## Proceso de Validación

### Pre-PR
1. Ejecutar validaciones automatizadas
2. Auto-review del código
3. Verificar contra checklist

### PR Creation
```bash
# Verificar todo antes de PR
npm run test && npm run build && npm run lint

# Crear PR si pasa
git push origin feature-branch
# Crear PR en plataforma
```

### Post-PR
1. Code review por peer
2. CI/CD pipeline
3. Merge si todo pasa

---

## Escalation Triggers

| Condición | Acción |
|-----------|--------|
| Tests fallan sin causa clara | Debug antes de continuar |
| Guardrail imposible de cumplir | Escalar a Arquitecto |
| Código incomprensible para Orquestador | Refactor antes de merge |
| Performance degradada | Profiling antes de merge |

---

## Referencias

- Kata asociada: `.raise/katas/story/implement.md`
- Gate previo: `gate-plan.md`
- Siguiente: UAT & Deploy (Gate-Deploy)
- Work Cycles: `framework/reference/work-cycles.md`
