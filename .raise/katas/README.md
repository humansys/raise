# Katas

> **Workflows lean** para crear entregables de forma consistente

---

## Qué es una Kata

Una kata es un workflow paso a paso que guía la creación de un entregable.

| Componente | Propósito |
|------------|-----------|
| **Cuándo Aplicar** | Trigger para usar la kata |
| **Pasos** | Acciones con verificación Jidoka |
| **Output** | Entregable + template + gate |

## Estructura Lean

```markdown
# Kata: [Nombre]

## Cuándo Aplicar
[1-2 oraciones]

## Pasos
### 1. [Acción]
[Descripción]
**Output**: [qué produce]
**Verificación**: [criterio]
> ⚠️ **Si falla**: [acción]

## Output Final
- Archivo: [path]
- Gate: [validación]
```

## Patrón Jidoka Inline

Cada paso incluye verificación y acción correctiva:

```markdown
**Verificación**: [cómo saber que está bien]
> ⚠️ **Si falla**: [qué hacer]
```

Esto permite **parar en defectos** y corregir antes de continuar.

---

## Katas Disponibles

| Kata | Categoría | Output |
|------|-----------|--------|
| `architecture/create-architecture-overview.md` | architecture | Architecture Overview |
| *(más por crear)* | | |

---

## Crear Nueva Kata

1. Usar template: `.raise/templates/kata.md`
2. Ubicar en categoría: `.raise/katas/[categoria]/`
3. Nombrar: `[verbo]-[sustantivo].md` (ej: `create-architecture-overview.md`)

---

*Template: `.raise/templates/kata.md`*
