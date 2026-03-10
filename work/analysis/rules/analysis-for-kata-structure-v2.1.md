# Análisis para Regla: Estructura de Katas v2.1

## Contexto y Objetivo
El framework RaiSE v2.1 define una estructura rigurosa para las "Katas", que son guías de proceso estandarizadas. El objetivo es formalizar esta estructura mediante una regla automática que garantice consistencia en `src/katas-v2.1/`.

## Patrones Identificados

### 1. Naming Convention y Ubicación
- **Ubicación**: `src/katas-v2.1/{nivel}/` donde nivel es `flujo`, `patron`, `principios` o `tecnica`.
- **Nombre de archivo**: `\d{2}-[\w-]+\.md` (ej: `01-discovery.md`).

### 2. Frontmatter Obligatorio
Todos los archivos deben iniciar con YAML frontmatter conteniendo:
- `id`: Formato `{nivel}-{numero}-{nombre}`
- `nivel`: Uno de [flujo, patron, principios, tecnica]
- `titulo`: String entre comillas
- `audience`: [beginner, intermediate, advanced]
- `template_asociado`: Path relativo o null
- `validation_gate`: Path relativo o null
- `prerequisites`: Lista de IDs
- `tags`: Lista de strings
- `version`: Semver

### 3. Estructura del Contenido (Markdown)
El documento debe seguir este orden de secciones (H2):
1. **Propósito**: Qué logra y qué pregunta responde.
2. **Contexto** / **Cuándo Aplicar**: Inputs, triggers.
3. **Pasos** (para Flujo) o **Estructura** (para Patrón): El cuerpo principal.
4. **Output**: Artefacto resultante.
5. **Validation Gate** (si aplica).
6. **Referencias**.

### 4. Patrón "Jidoka Inline" (Crítico)
Dentro de los pasos, se exige el siguiente micro-formato para habilitar la corrección temprana:

```markdown
### Paso N: [Nombre]
[Descripción]

**Verificación:** [Criterio de éxito]

> **Si no puedes continuar:** [Causa] → [Resolución]
```

## Evidencia

### Ejemplo Correcto (src/katas-v2.1/flujo/01-discovery.md)
- Frontmatter completo.
- Estructura H2 estándar.
- Pasos con bloque `> **Si no puedes continuar:**`.

### Ejemplo Correcto (src/katas-v2.1/patron/01-code-analysis.md)
- Estructura adaptada a patrón pero manteniendo Jidoka Inline.

## Anti-patrones a Evitar
1. **Falta de Jidoka**: Pasos que son solo instrucciones sin verificación ni cláusula de escape.
2. **Frontmatter Incompleto**: Omitir `template_asociado` o `validation_gate` (deben ser null si no existen).
3. **IDs Inconsistentes**: El ID en frontmatter no coincide con el nombre de archivo/carpeta.

## Recomendación de Regla
Crear una regla `100-kata-structure-v2.1` que valide:
1. Existencia y esquema del frontmatter.
2. Presencia de secciones obligatorias.
3. Uso del patrón Jidoka Inline en secciones de pasos.
