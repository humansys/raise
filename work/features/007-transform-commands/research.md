# Research: Transform Commands Script

**Feature**: 007-transform-commands
**Date**: 2026-01-20

## Decisiones Técnicas

### 1. Lenguaje y Versión

**Decisión**: Bash 4.0+
**Rationale**:
- Requisito del PRD: script único sin dependencias externas
- Bash 4.0+ soporta arrays asociativos necesarios para mapeos
- Compatible con Git Bash en Windows (MINGW64)
**Alternativas consideradas**:
- Python: Descartado por requerir dependencia externa
- PowerShell: Descartado por no ser portable a Unix/Linux

### 2. Mecanismo de Reemplazo de Referencias

**Decisión**: `sed` con expresiones regulares
**Rationale**:
- Disponible en todos los entornos bash
- Permite reemplazo in-line eficiente
- Soporta patrones regex para matchear `agent: speckit.X`
**Alternativas consideradas**:
- `awk`: Más complejo para este caso de uso simple
- Bash string substitution: No soporta regex adecuadamente

### 3. Estructura de Mapeos

**Decisión**: Arrays asociativos declarativos al inicio del script
**Rationale**:
- Fácil de mantener y modificar
- Documentación implícita del mapeo
- Permite iteración simple con `for key in "${!array[@]}"`
**Estructura**:
```bash
declare -A FILE_MAP=(
    ["speckit.specify.md"]="03-feature/speckit.1.specify.md"
    ["speckit.clarify.md"]="03-feature/speckit.2.clarify.md"
    # ...
)

declare -A REF_MAP=(
    ["speckit.specify"]="speckit.1.specify"
    ["speckit.clarify"]="speckit.2.clarify"
    # ...
)
```

### 4. Manejo de Errores

**Decisión**: Exit codes estándar + mensajes descriptivos
**Rationale**:
- Exit 0: Éxito
- Exit 1: Error (carpeta no encontrada, permisos, etc.)
- Mensajes a stderr para errores, stdout para progreso
**Patrón**:
```bash
error() { echo "ERROR: $1" >&2; exit 1; }
warn() { echo "WARNING: $1" >&2; }
info() { echo "$1"; }
```

### 5. Comportamiento con Archivos Existentes

**Decisión**: No sobrescribir por defecto, advertir
**Rationale**:
- Comportamiento seguro que previene pérdida de datos
- El usuario puede eliminar manualmente y re-ejecutar si desea sobrescribir
- Alineado con principio de "least surprise"

## Patrones de Implementación

### Patrón de Transformación por Archivo

```bash
transform_file() {
    local src="$1"
    local dest="$2"
    local content

    # Leer contenido
    content=$(<"$src")

    # Aplicar reemplazos de referencias
    for old_ref in "${!REF_MAP[@]}"; do
        new_ref="${REF_MAP[$old_ref]}"
        content="${content//agent: $old_ref/agent: $new_ref}"
    done

    # Escribir a destino
    echo "$content" > "$dest"
}
```

### Validación Pre-ejecución

```bash
validate_environment() {
    [[ ! -d "$SRC_DIR" ]] && error "Carpeta origen no encontrada: $SRC_DIR"
    [[ ! -w "$(dirname "$DEST_DIR")" ]] && error "Sin permisos de escritura"
}
```

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Frontmatter malformado | Baja | Medio | Copiar sin modificar, advertir |
| Archivo destino existe | Media | Bajo | No sobrescribir, advertir |
| Permisos insuficientes | Baja | Alto | Validar antes de procesar |
| Encoding incorrecto | Baja | Medio | Asumir UTF-8, documentar |
