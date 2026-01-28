# Guía de Configuración de Raise Kit

Este kit permite transformar un proyecto estándar de `specify` en un proyecto **compatible con Raise**, inyectando comandos especializados, gates, scripts y plantillas.

## Prerrequisitos

1. **Specify CLI**: Instala la herramienta usando `uv` (Ver [repositorio oficial](https://github.com/github/spec-kit/tree/main)):
   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ``` 
2. **Entorno de Ejecución**:
   *   **Bash**: Para Linux, macOS o Windows (Git Bash/WSL).
   *   **PowerShell**: Para Windows.
3. **Raise Kit**: Este repositorio/carpeta debe estar presente.

## Flujo de Trabajo

Sigue estos pasos para crear un nuevo proyecto y configurarlo con Raise Kit.

### 1. Inicializar un nuevo proyecto Specify

Ejecuta el comando de inicialización estándar. Puedes usar cualquier nombre para la carpeta de tu proyecto.

```bash
specify init <nombre-proyecto>
```

*Ejemplo:*

```bash
specify init mi-app
```

### 2. Inyectar Recursos de Raise

#### Opción A: Bash (Linux/macOS/Git Bash)

Ejecuta el script de transformación en Bash. Este script copiará los scripts complementarios de Bash (excluyendo PowerShell) a tu proyecto.

```bash
bash .raise-kit/scripts/bash/raise/transform-commands.sh <nombre-proyecto>
```

*Ejemplo:*
```bash
bash .raise-kit/scripts/bash/raise/transform-commands.sh mi-app
```

#### Opción B: PowerShell (Windows)

Ejecuta el script de transformación en PowerShell. Este script copiará los scripts complementarios de PowerShell (excluyendo Bash) a tu proyecto.

```powershell
powershell -ExecutionPolicy Bypass -File .raise-kit/scripts/powershell/raise/transform-commands.ps1 -ProjectName <nombre-proyecto>
```

*Ejemplo:*
```powershell
powershell -ExecutionPolicy Bypass -File .raise-kit/scripts/powershell/raise/transform-commands.ps1 -ProjectName mi-app
```

## ¿Qué sucede?

La carpeta de tu proyecto (`<nombre-proyecto>/.specify`) se poblará con:

* **Comandos**: Renombrados y parcheados (ej. `/speckit.specify` -> `/speckit.1.specify`).
* **Gates**: Gates de validación desde `.raise-kit/gates`.
* **Scripts**: Scripts de ayuda desde `.raise-kit/scripts`.
* **Plantillas**: Plantillas de documentación desde `.raise-kit/templates`.

Tu proyecto está ahora listo para usar con la metodología completa de Raise.
