# Data Model: Glosario Mínimo (Seed) para Stage 0

**Feature**: 002-glossary-seed
**Date**: 2026-01-11
**Phase**: 1 (Design)

## Document Structure

### Entity: Concepto Semilla

Representa uno de los 5 conceptos esenciales que un Orquestador necesita conocer en Stage 0.

**Attributes**:
- `nombre`: String (término canónico del glosario v2.1)
- `interfaz_simple`: String (<10 palabras, frase accesible)
- `detalle_minimo`: String (1-2 oraciones de contexto)
- `ejemplo_concreto`: String (caso de uso del framework)

**Constraints**:
- Total por concepto: ≤100 palabras
- `nombre` DEBE coincidir exactamente con glosario v2.1
- `ejemplo_concreto` DEBE referenciar flujo spec-kit cuando sea posible

**Instances** (5 conceptos):
1. Orquestador
2. Spec
3. Agent
4. Validation Gate
5. Constitution

---

### Entity: Glosario Seed Document

Representa el artefacto markdown completo.

**Attributes**:
- `titulo`: String ("Glosario Esencial de RaiSE")
- `introduccion`: String (~50 palabras)
- `conceptos`: Array[5] of Concepto Semilla
- `cierre`: String (~50 palabras, con enlace a glosario v2.1)

**Constraints**:
- Longitud total: 400-600 palabras
- Formato: Markdown
- Ubicación: `docs/framework/v2.1/model/20a-glossary-seed.md`

---

## Markdown Template Structure

```markdown
# Glosario Esencial de RaiSE

[Introducción: 2-3 líneas sobre por qué existe este glosario mínimo]

---

## Orquestador

[Interfaz simple]

[Detalle mínimo: 1-2 oraciones]

**Ejemplo**: [Caso de uso concreto]

---

## Spec

[Interfaz simple]

[Detalle mínimo: 1-2 oraciones]

**Ejemplo**: [Caso de uso concreto]

---

## Agent

[Interfaz simple]

[Detalle mínimo: 1-2 oraciones]

**Ejemplo**: [Caso de uso concreto]

---

## Validation Gate

[Interfaz simple]

[Detalle mínimo: 1-2 oraciones]

**Ejemplo**: [Caso de uso concreto]

---

## Constitution

[Interfaz simple]

[Detalle mínimo: 1-2 oraciones]

**Ejemplo**: [Caso de uso concreto]

---

*Para el glosario completo con ~35 términos, consulta [20-glossary-v2.1.md](./20-glossary-v2.1.md)*
```

---

## Validation Schema

### Gate-Terminología

| Verification | Method |
|--------------|--------|
| Términos canónicos usados | Comparar `nombre` de cada concepto con glosario v2.1 |
| Sin términos nuevos no definidos | Revisar `detalle_minimo` y `ejemplo_concreto` |

### Gate-Coherencia

| Verification | Method |
|--------------|--------|
| Sin contradicciones con glosario v2.1 | Comparar definiciones completas |
| Sin contradicciones con Constitution | Verificar principios mencionados |

### Success Criteria Validation

| Criterion | Method |
|-----------|--------|
| SC-001: 5 secciones | Contar headers `##` en markdown |
| SC-002: 400-600 palabras | `wc -w 20a-glossary-seed.md` |
| SC-003: Ejemplos presentes | Regex search `\*\*Ejemplo\*\*:` (5 matches) |

---

*Data model completado. Proceder a quickstart.md.*
