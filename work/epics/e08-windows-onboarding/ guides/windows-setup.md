# Setup en Windows — Antes de empezar

> **Vigencia:** Este documento es un workaround temporal.
> Aplica mientras el bug E4 (cp1252) no esté resuelto en una release de RaiSE.
> Si ya tienes una versión que incluye el fix, puedes ignorarlo.

---

## Paso obligatorio antes de instalar RaiSE

En Windows, Python usa por defecto la codificación `cp1252` para la consola.
RaiSE imprime caracteres Unicode (`✓`, `▶`, `⚠`) que no existen en `cp1252`,
lo que provoca un crash en varios comandos — incluso cuando la operación terminó bien.

**El síntoma:** corres `rai graph build` y ves algo como esto al final:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**El fix:** una variable de entorno que le dice a Python que use UTF-8.

### Cómo configurarlo

Abre una terminal (cmd o PowerShell) y corre:

```cmd
setx PYTHONUTF8 1
```

Deberías ver:

```
SUCCESS: Specified value was saved.
```

**Importante:** cierra la terminal y abre una nueva. La variable solo toma efecto en sesiones nuevas.

### Cómo verificar que está activo

En una terminal nueva:

```cmd
echo %PYTHONUTF8%
```

Debe mostrar `1`. Si muestra `%PYTHONUTF8%` (sin sustituir), la terminal es vieja — ciérrala y abre otra.

### Preguntas frecuentes

**¿Necesito permisos de administrador?**
No. `setx` sin flags escribe en tu usuario (`HKCU`), no en el sistema.

**¿`setx` viene instalado?**
Sí, es nativo de Windows Vista en adelante. No hay que instalar nada.

**¿Es permanente?**
Sí, hasta que lo quites manualmente. No hay que repetirlo en cada sesión.

**¿Afecta otras aplicaciones?**
Solo a procesos Python. No cambia el locale del sistema ni afecta otras apps.

### Cómo quitarlo (si necesitas)

En PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable('PYTHONUTF8', [NullString]::Value, 'User')
```

Abre una terminal nueva para que tome efecto.

---

*Verificado en: Windows 11 + Python 3.13 — 2026-03-25*
*Bug de referencia: RAISE E4 (cp1252 encoding)*
