# Quickstart: Transform Commands Script

## Uso Básico

```bash
# Desde la raíz del repositorio template
./template/.specify/scripts/bash/raise/transform-commands.sh
```

## Prerequisitos

- Bash 4.0+ (verificar con `bash --version`)
- Git Bash en Windows (MINGW64) es compatible
- Permisos de escritura en carpeta destino

## Estructura de Carpetas

**Origen:**
```
template/.claude/commands/
├── speckit.specify.md
├── speckit.clarify.md
├── speckit.plan.md
├── speckit.tasks.md
├── speckit.analyze.md
├── speckit.implement.md
├── speckit.checklist.md
├── speckit.taskstoissues.md
└── speckit.constitution.md
```

**Destino:**
```
.specify-raise/commands/
├── 01-onboarding/
│   └── speckit.2.constitution.md
└── 03-feature/
    ├── speckit.1.specify.md
    ├── speckit.2.clarify.md
    ├── speckit.3.plan.md
    ├── speckit.4.tasks.md
    ├── speckit.5.analyze.md
    ├── speckit.6.implement.md
    ├── speckit.util.checklist.md
    └── speckit.util.issues.md
```

## Verificación Post-ejecución

```bash
# Verificar que no quedan referencias antiguas
grep -r "agent: speckit\." .specify-raise/commands/ | grep -v "speckit\.[0-9]" | grep -v "speckit\.util"

# Debería retornar vacío si la transformación fue exitosa
```

## Escenarios de Test

### Test 1: Transformación Completa
```bash
# 1. Ejecutar script
./transform-commands.sh

# 2. Verificar conteo de archivos
ls -1 .specify-raise/commands/**/*.md | wc -l
# Esperado: 9
```

### Test 2: Carpeta Origen No Existe
```bash
# Mover carpeta origen temporalmente
mv template/.claude/commands template/.claude/commands.bak

# Ejecutar script
./transform-commands.sh
# Esperado: ERROR y exit code 1

# Restaurar
mv template/.claude/commands.bak template/.claude/commands
```

### Test 3: Archivo Destino Ya Existe
```bash
# Crear archivo conflictivo
touch .specify-raise/commands/03-feature/speckit.1.specify.md

# Ejecutar script
./transform-commands.sh
# Esperado: WARNING para ese archivo, continúa con el resto
```
