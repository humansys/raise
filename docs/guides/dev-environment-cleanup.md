# Dev Environment Cleanup

Guía para diagnosticar y limpiar instalaciones viejas de raise-cli antes de hacer un setup limpio.

**Si estás instalando desde cero** (máquina nueva, nunca tuviste rai), no necesitas esta guía. Ve directo a [Dev Environment Setup](dev-environment-setup.md).

## ¿Necesito limpiar?

Corre esto en tu terminal:

```bash
which -a rai
rai --version
```

| Ves esto | Significa | Qué hacer |
| --- | --- | --- |
| `which -a rai` no muestra nada | No tienes rai instalado | No necesitas limpiar. Ve a [Setup](dev-environment-setup.md) |
| Muestra **una** ruta y `rai --version` funciona | Tienes una instalación | Verifica de dónde viene (ver abajo) |
| Muestra **varias** rutas | Tienes instalaciones duplicadas | Necesitas limpiar |
| `rai --version` da error (`command not found`, `cannot execute`, `ModuleNotFoundError`) | La instalación está rota | Necesitas limpiar |

## ¿De dónde viene mi instalación?

```bash
# ¿Es un symlink? ¿A dónde apunta?
ls -la $(which rai)

# ¿Está en conda?
echo $PATH | tr ':' '\n' | grep conda

# ¿Está en pipx?
pipx list 2>/dev/null | grep rai

# ¿Está en uv tool?
uv tool list 2>/dev/null | grep raise-cli
```

| Viene de | Ruta típica | ¿Limpiar? |
| --- | --- | --- |
| uv tool | `~/.local/share/uv/tools/raise-cli/bin/rai` | No — ya está bien |
| pipx | `~/.local/pipx/venvs/raise-cli/bin/rai` | Opcional — funciona, pero puedes migrar a uv tool |
| conda | `~/miniconda3/bin/rai` o `~/anaconda3/bin/rai` | Sí |
| pip global | `/usr/lib/python3/...` o similar | Sí — contamina el Python del sistema |
| symlink roto | `~/.local/bin/rai -> (algo que no existe)` | Sí — borra el symlink |

Si todo apunta a uv tool y funciona, no hay nada que limpiar.

## Quitar conda

```bash
# 1. Ver si tienes conda
which conda
```

Si no tienes conda, salta a la siguiente sección.

### Opción A: No uso conda para nada más → desinstalar conda completa

Esto borra conda por completo. Después de esto, `conda` ya no existe como comando.

```bash
# 1. Borrar los bloques de "conda initialize" de tus shell configs
#    Abre cada archivo y borra TODO entre ">>> conda initialize >>>" y "<<< conda initialize <<<"
nano ~/.bashrc    # o el editor que uses
nano ~/.zshrc     # si usas zsh

# 2. Borrar el directorio de conda (esto ES desinstalar conda — todo vive ahí)
rm -rf ~/miniconda3    # o ~/anaconda3, depende de lo que instalaste

# 3. Abrir una terminal nueva para que el PATH se actualice
```

### Opción B: Uso conda para otros proyectos → solo quitar raise-cli de conda

Esto deja conda funcionando pero quita raise-cli y raise-pro de ahí.

```bash
# 1. Desinstalar raise-cli y raise-pro del entorno base de conda
conda activate base
pip uninstall raise-cli raise-pro -y

# 2. Verificar que ya no están
pip show raise-cli    # no debe mostrar nada
```

**¿Por qué limpiar conda aunque la sigas usando?** Si conda tiene raise-cli instalado, puede interferir con el `rai` de uv tool. Al quitarlo de conda, te aseguras de que `rai` siempre ejecuta la versión correcta.

## Quitar pipx

```bash
# 1. Desinstalar raise-cli de pipx
pipx uninstall rai-cli

# 2. (Opcional) Si no usas pipx para nada más
sudo apt remove pipx    # Linux
brew uninstall pipx      # macOS
```

## Quitar symlinks rotos

```bash
# Ver si ~/.local/bin/rai existe y a dónde apunta
ls -la ~/.local/bin/rai

# Si apunta a algo que ya no existe (conda, pipx viejo), bórralo
rm ~/.local/bin/rai
```

**¿Qué es un symlink?** Un atajo. `~/.local/bin/rai` es un archivo que dice "cuando me ejecuten, en realidad ejecuta ESTE OTRO archivo". Si ese otro archivo ya no existe, el symlink está "roto" y el comando falla.

## Verificar que quedó limpio

Abre una **terminal nueva** y corre:

```bash
which -a rai          # no debe mostrar nada (o solo uv tool si ya instalaste)
which conda           # debe decir "not found"
echo $PATH | tr ':' '\n' | grep conda    # no debe mostrar nada
```

Si todo sale limpio, ve a [Dev Environment Setup](dev-environment-setup.md) para instalar desde cero.
