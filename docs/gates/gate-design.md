---
id: gate-design
fase: 3
titulo: "Gate-Design: Validación del Tech Design"
blocking: true
version: 1.0.0
---

# Gate-Design: Validación del Tech Design

## Propósito

Verificar que el Technical Design está completo, es técnicamente sólido, y proporciona guía suficiente para implementación. Este gate asegura que el equipo puede comenzar a desarrollar sin ambigüedades arquitectónicas.

## Cuándo Aplicar

- Después de completar `flujo-03-tech-design`
- Antes de iniciar `flujo-05-backlog-creation`
- El documento debe existir en `.raise/specs/{proyecto}-tech-design.md`

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Arquitectura documentada** | Diagrama de componentes con relaciones claras |
| 2 | **Flujos de datos completos** | Cada input tiene camino trazable hasta output/persistencia |
| 3 | **Contratos de API definidos** | Endpoints con request/response documentados |
| 4 | **Modelo de datos especificado** | Entidades, campos, relaciones, índices |
| 5 | **Seguridad considerada** | AuthN/AuthZ definidos para cada endpoint |
| 6 | **Errores estandarizados** | Catálogo de códigos de error con formato |
| 7 | **Aprobación técnica** | Sign-off de Arquitecto o Tech Lead |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | Alternativas documentadas | ≥2 alternativas por decisión arquitectónica principal |
| 9 | Estrategia de testing | Tipos de tests y cobertura esperada definidos |
| 10 | Riesgos con mitigación | Cada riesgo tiene owner y plan |
| 11 | Preguntas resueltas | No hay preguntas abiertas bloqueantes |

---

## Proceso de Validación

### Paso 1: Verificar completitud de secciones

Revisar que todas las secciones del template estén completadas:

| Sección | ¿Completa? |
|---------|------------|
| Visión General | [ ] |
| Solución Propuesta | [ ] |
| Arquitectura de Componentes | [ ] |
| Flujo de Datos | [ ] |
| Contratos de API | [ ] |
| Modelo de Datos | [ ] |
| Seguridad | [ ] |
| Manejo de Errores | [ ] |
| Alternativas | [ ] |
| Riesgos | [ ] |
| Testing | [ ] |

**Verificación:** Todas las secciones tienen contenido sustancial (no placeholders).

> **Si falla:** Identificar secciones incompletas y regresar a kata para completar.

### Paso 2: Validar coherencia arquitectónica

Verificar que el diseño es internamente consistente:
- Componentes mencionados en diagrama aparecen en descripción
- Flujos de datos usan los componentes definidos
- APIs exponen las operaciones necesarias para los flujos
- Modelo de datos soporta las APIs definidas

**Verificación:** No hay componentes, flujos o APIs "huérfanos".

> **Si falla:** Trazar cada flujo end-to-end y verificar que todos los elementos están conectados.

### Paso 3: Validar trazabilidad con Vision

Confirmar que el diseño implementa la Solution Vision:
- Cada componente de alto nivel de la Vision tiene correspondencia
- Los mecanismos técnicos prometidos están diseñados
- El MVP scope está cubierto por el diseño

**Verificación:** No hay gaps entre Vision y Tech Design.

> **Si falla:** Identificar gaps. Si hay scope nuevo en Tech Design, validar con Product Owner.

### Paso 4: Revisión técnica de peers

Obtener revisión de al menos un desarrollador que no sea el autor:
- ¿El diseño es comprensible?
- ¿Hay decisiones cuestionables?
- ¿Faltan consideraciones?

**Verificación:** Feedback de peer review incorporado o documentado como "no action".

> **Si falla:** Agendar sesión de peer review antes de continuar.

### Paso 5: Aprobación de Arquitecto/Tech Lead

Obtener sign-off formal del responsable técnico.

**Verificación:** Evidencia de aprobación (email, comentario, firma).

> **Si falla:** Agendar sesión de revisión con Arquitecto/Tech Lead.

---

## Checklist Rápido

```markdown
## Gate-Design Checklist

**Tech Design:** {nombre del archivo}
**Vision Referencia:** {nombre de la vision}
**Fecha:** YYYY-MM-DD

### Obligatorios
- [ ] 1. Diagrama de arquitectura presente y claro
- [ ] 2. Flujos de datos trazables end-to-end
- [ ] 3. Contratos de API con request/response
- [ ] 4. Modelo de datos con entidades y relaciones
- [ ] 5. Seguridad (AuthN/AuthZ) por endpoint
- [ ] 6. Catálogo de errores estandarizado
- [ ] 7. Aprobación de Arquitecto/Tech Lead

### Recomendados
- [ ] 8. ≥2 alternativas por decisión principal
- [ ] 9. Estrategia de testing definida
- [ ] 10. Riesgos con owner y mitigación
- [ ] 11. Sin preguntas abiertas bloqueantes

### Coherencia
- [ ] Componentes del diagrama = componentes descritos
- [ ] Flujos usan componentes definidos
- [ ] APIs soportan los flujos
- [ ] Modelo de datos soporta las APIs

### Trazabilidad con Vision
- [ ] MVP scope cubierto
- [ ] Mecanismos técnicos implementados
- [ ] Sin scope creep

### Resultado
- [ ] **PASS** - Todos los obligatorios cumplidos
- [ ] **FAIL** - Criterios fallidos: _______________

**Peer Review por:** _______________ Fecha: ___
**Aprobación Técnica:** _______________ Fecha: ___
**Validado por:** _______________
```

---

## Escalation Triggers

| Condición | Acción |
|-----------|--------|
| Diseño imposible de implementar con recursos | Escalar a PM para re-scope |
| Desacuerdo arquitectónico no resuelto | Escalar a Arquitecto senior |
| Riesgos técnicos altos sin mitigación | Spike/POC antes de continuar |

---

## Referencias

- Kata asociada: [`flujo-03-tech-design`](../katas-v2.1/flujo/03-tech-design.md)
- Template: [`tech_design.md`](../templates/tech/tech_design.md)
- Gate previo: [`gate-vision`](./gate-vision.md)
- Siguiente gate: [`gate-backlog`](./gate-backlog.md)
