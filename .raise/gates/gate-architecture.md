# Gate: Architecture Overview

## Criterios de Validación

### Estructura (Requerido)

| Criterio | Check |
|----------|-------|
| Tiene sección "System Context" | [ ] |
| Tiene sección "Container Diagram" | [ ] |
| Tiene sección "Decisiones Clave" | [ ] |
| Tiene sección "Quality Attributes" | [ ] |

### Contenido (Requerido)

| Criterio | Check |
|----------|-------|
| System Context tiene ≥1 actor externo | [ ] |
| System Context tiene ≥1 sistema externo O justificación de standalone | [ ] |
| Container diagram tiene ≥2 containers | [ ] |
| Cada container tiene: nombre, responsabilidad, tecnología | [ ] |
| Cada decisión tiene rationale (no solo "qué", también "por qué") | [ ] |
| NFRs son medibles (tienen números o criterios objetivos) | [ ] |

### Consistencia (Requerido)

| Criterio | Check |
|----------|-------|
| Componentes mencionados existen en Solution Vision | [ ] |
| No hay contradicciones con Solution Vision | [ ] |
| Tecnologías son consistentes con restricciones técnicas | [ ] |

### Calidad (Recomendado)

| Criterio | Check |
|----------|-------|
| Diagramas son legibles (no sobrecargados) | [ ] |
| No hay secciones con placeholders `[TODO]` | [ ] |
| Decisiones referencian ADRs si existen | [ ] |

---

## Resultado

| Estado | Criterio |
|--------|----------|
| ✅ **PASS** | Todos los criterios Requeridos cumplen |
| ⚠️ **PASS con observaciones** | Requeridos cumplen, algunos Recomendados no |
| ❌ **FAIL** | Algún criterio Requerido no cumple |

---

## Acciones si FAIL

1. Identificar criterios que no cumplen
2. Volver al paso correspondiente de la kata
3. Corregir y re-ejecutar gate
