A continuación, encontrarás una **guía más específica y técnica** sobre cómo escribir las reglas (Cursor Rules), qué sintaxis emplean, qué tipo de archivos se utilizan y de qué forma se integran con el IDE de Cursor. Esta guía se basa en la documentación oficial y experiencias de la comunidad de usuarios de Cursor.

---

## 1. Estructura y ubicación de las reglas

### 1.1. Directorio de reglas: `.cursor/rules/`
Para que Cursor IDE reconozca y aplique las reglas en un proyecto, deberás crear (o utilizar) el directorio especial:

```
.cursor/rules/
```

Dentro de esta carpeta, se pueden colocar múltiples **archivos de reglas** (generalmente con extensión `.md`, `.mdc` o similar). Cada archivo describe uno o varios conjuntos de reglas que se cargarán y aplicarán según el *scope* (alcance) definido.

> **Nota**: Existen también “Reglas globales” que puedes configurar a nivel de la aplicación Cursor (en *Settings > Rules for AI*). Dichas reglas se aplican a todos tus proyectos. Sin embargo, lo más habitual es que cada repositorio contenga sus propias reglas locales dentro de `.cursor/rules/`, pues suelen estar muy ligadas al estilo y configuración de cada proyecto.

### 1.2. Archivos de reglas por ámbito o temática
No estás limitado a un único archivo de reglas. Una práctica recomendable es **dividir tus reglas** en varios ficheros, agrupando las directivas por tema o por tecnología. Por ejemplo:

- `general.mdc`: reglas generales de estilo y convenciones globales.  
- `backend.mdc`: reglas específicas para el código de backend (p. ej. Node, Python, etc.).  
- `frontend.mdc`: reglas específicas para el frontend (React, Vue, etc.).  
- `database.mdc`: reglas dedicadas a la integración con la base de datos, migraciones, etc.

Esta separación modular facilita el mantenimiento y la extensibilidad. Además, Cursor permite **incluir** o **omitir** un archivo de reglas según sus patrones de aplicación (ver detalles en la [Sección 3](#3-definir-el-scope-y-los-patrones-de-aplicación)).

---

## 2. Formato de las reglas: front matter YAML + contenido

Cada archivo de reglas **debe** incluir al inicio un bloque de *front matter* en sintaxis YAML. Posteriormente, viene el contenido propiamente dicho en Markdown. Cursor analiza esta sección YAML para entender *metadatos* como título, descripción y patrones de archivo.

Ejemplo mínimo de la estructura de un archivo de reglas en `.cursor/rules/`:

```yaml
---
title: "Reglas generales"
description: "Convenciones globales para el proyecto y lineamientos de estilo"
patterns:
  - "*"
---

# Reglas Generales

Este archivo describe las normas globales para el repositorio.
```

### 2.1. Campos comunes en el front matter

- **`title`**: Título descriptivo de las reglas.  
- **`description`**: Texto breve que explique la finalidad del archivo.  
- **`patterns`**: Lista (o cadena) de patrones (globs) de archivos a los que se aplicará esta regla. Por ejemplo:  
  - `*.js` para todos los archivos JavaScript.  
  - `src/**/*.py` para todos los `.py` dentro de `src/`.  
  - `*` si quieres aplicarlo a todo el repositorio, o `!test/*.js` para excluir carpetas específicas.  

Existe cierta flexibilidad en cómo se definen estos patrones. Normalmente se usa sintaxis de [globbing](https://en.wikipedia.org/wiki/Glob_(programming)) (*, **, etc.). Si no especificas `patterns`, la regla podría aplicarse de forma global en todo el proyecto, pero generalmente se recomienda ser explícito.

### 2.2. Contenido en Markdown
Tras el bloque de YAML, escribes tus reglas en **formato Markdown**. El cuerpo del archivo es donde colocas el “texto instructivo” que la IA usará como directrices. Puedes usar encabezados `#`, listas, tablas o cualquier sintaxis Markdown para estructurar tus reglas.

> **Importante**: Tanto el front matter YAML como el texto Markdown posterior se envían al modelo de IA como parte del *contexto* que Cursor inyecta en cada interacción (siempre y cuando se cumpla el patrón del archivo actual y no hayas excedido límites de token). Cuanto más claro y conciso sea tu contenido, mejor funcionará.

---

## 3. Definir el scope y los patrones de aplicación

En Cursor, cada archivo `.mdc` o `.md` dentro de `.cursor/rules/` puede incluir una clave `patterns` en el front matter para especificar a qué archivos se aplicará. Por ejemplo:

```yaml
---
title: "Reglas de JavaScript"
description: "Lineamientos para archivos .js y .jsx"
patterns:
  - "*.js"
  - "*.jsx"
---
```

Con esto, Cursor solo cargará estas reglas cuando estés editando o generando código en archivos `.js` o `.jsx`. Algunas variantes:

- **Aplicar a todo el proyecto**:  
  ```yaml
  patterns:
    - "*"
  ```
- **Exclusión de ciertas rutas** con `!`:  
  ```yaml
  patterns:
    - "**/*.py"
    - "!**/migrations/*"
  ```
  Aplica a todos los `.py` excepto los que estén en `migrations/`.

- **Múltiples directorios**:  
  ```yaml
  patterns:
    - "src/**/*.ts"
    - "lib/**/*.ts"
  ```

> **Consejo**: Usa el menor número posible de patrones *globales* para no saturar al modelo con reglas irrelevantes. Deja que cada archivo `.mdc` se aplique de forma selectiva a la parte del proyecto donde importa.

---

## 4. Sintaxis y estilo al redactar las reglas

Las reglas en el cuerpo Markdown funcionan como **instrucciones** o **constraints** que se inyectan al modelo. Aunque no hay una “sintaxis formal” rígida (como en un lenguaje de programación), sí se recomienda una estructura clara:

1. **Encabezados**: usar `##`, `###` etc. para agrupar secciones:
   - **Contexto del proyecto**  
   - **Lineamientos de estilo**  
   - **Buenas prácticas**  
   - **Errores comunes a evitar**  
   - **Uso de librerías**  

2. **Listas de viñetas o numeradas** para directrices puntuales, por ejemplo:
   ```markdown
   - Evitar variables globales.
   - Emplear `const` en lugar de `let` siempre que sea posible.
   - Cada componente React debe ser un Functional Component con Hooks.
   ```

3. **Directrices claras y directas**: en lugar de grandes párrafos, se sugiere usar oraciones concisas para que la IA no “pierda” la instrucción. Por ejemplo:
   ```markdown
   **Regla**: Para cada endpoint nuevo en FastAPI, usar un modelo Pydantic para la petición y otro para la respuesta.
   ```

4. **Resaltar palabras clave**: a veces, negrita o *itálicas* ayudan a enfatizar palabras concretas (p. ej. *“nunca”*, *“siempre”*, *“prohibir”*), lo que facilita que el modelo detecte la importancia. De todos modos, no abuses del formateo.

5. **Ejemplos de código**: en muchos casos, es útil incluir trozos de código con triple backtick (```), para ilustrar exactamente qué se espera. El modelo puede usar ese ejemplo como *patrón a seguir*.

   ```markdown
   ```js
   // Ejemplo de uso correcto de fetch con manejo de errores
   try {
     const resp = await fetch('/api/users');
     if (!resp.ok) {
       throw new Error('Error en la respuesta');
     }
     const data = await resp.json();
     ...
   } catch (err) {
     console.error(err);
   }
   ```
   ```

> **Tip**: Estas “muestras” de código sirven de referencia muy potente para la IA. No obstante, mantener las reglas *enfocadas* y no llenar de ejemplos irrelevantes o repetidos, pues cada snippet aumenta el número de tokens que consume.

---

## 5. Integración con Cursor IDE: cómo se aplican en la práctica

Una vez que tienes tus archivos de reglas en `.cursor/rules/`, Cursor IDE los procesará automáticamente:

1. **Indexación**: Al abrir el proyecto en Cursor, el IDE escanea la carpeta `.cursor/rules/` y lee cada archivo de reglas.  
2. **Contexto dinámico**: Cuando el usuario edita o solicita código en un archivo (por ejemplo, `app.js`), Cursor determina qué reglas son relevantes comparando la ruta y extensión del archivo con los `patterns` declarados.  
3. **Inyección**: Las reglas relevantes (o un subconjunto, si hay limitaciones de espacio de contexto) se inyectan en el prompt interno enviado al modelo de IA.  
4. **Generación**: El modelo produce sugerencias, autocompletado o respuestas de chat tomando en cuenta las instrucciones de las reglas.  
5. **Filtro o “auto-check”**: En la medida en que las reglas establezcan lineamientos de estilo, validaciones, etc., la IA intentará cumplirlos. Si hay conflictos o información contradictoria, la IA puede presentar un comportamiento inconsistente. Por eso la recomendación de mantener reglas claras y coherentes.

### 5.1. Verificación de qué reglas se están usando
Cursor a veces muestra (en sus paneles o en la interfaz) la lista de archivos de reglas que están activos en cierto momento. También puedes verificar en la configuración global si hay reglas del usuario que se apliquen a todos los proyectos. 

Si notas que el modelo ignora una regla, revisa:

- **¿Está el patrón `patterns` correcto?**  
- **¿No habrá otra regla que contradiga esa directriz?**  
- **¿Es demasiado largo el contexto?** (cuando se supera el límite de tokens, Cursor puede priorizar partes del contexto y dejar fuera otras).

---

## 6. Ejemplo completo de archivo de reglas

A continuación, un archivo de ejemplo (por ejemplo `backend.mdc`) que podrías colocar en `.cursor/rules/`:

```yaml
---
title: "Reglas para el backend Python con FastAPI"
description: "Instrucciones de estilo, estructura y mejores prácticas para el backend"
patterns:
  - "backend/**/*.py"
  - "!backend/**/migrations/*"
---

# Reglas de Backend (FastAPI + Python)

## Contexto
Este proyecto implementa una API REST en Python usando FastAPI, con SQLAlchemy para la base de datos y Pydantic para validaciones.

## Estándares de Código
- **Seguir PEP 8** para formato y nombres de variables.
- Utilizar `async def` para las rutas que interactúan con I/O (DB o red).
- Preferir `snake_case` en nombres de funciones y variables.

## Manejo de Rutas
- Definir un archivo `router_*.py` por cada módulo de negocio (ej. `router_users.py`).
- Cada endpoint debe retornar un modelo Pydantic de respuesta (evitar retornar dicts sueltos).
- Usar `HTTPException` para errores esperados (404, 400, etc.) con el código HTTP adecuado.

## Validaciones y Errores
- No usar `raise Exception` genérico, definir excepciones específicas o usar `HTTPException`.
- Manejar errores inesperados en middleware global, loguear la traza.

## Ejemplo de endpoint correcto
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserBase(BaseModel):
    email: str
    name: str

@router.get("/users/{user_id}", response_model=UserBase)
async def get_user(user_id: int):
    # Lógica para obtener user de la DB
    user = ... # Query
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserBase(**user.dict())
```

## Integración con la Base de Datos
- Usar SQLAlchemy con sesiones asíncronas (cuando sea posible).
- Centralizar la configuración de la sesión en `db.py`.

## Pruebas
- Escribir pruebas con `pytest` en el directorio `tests/`.
- Asegurar al menos un test de cada endpoint con `TestClient` de FastAPI.
```

En este ejemplo:

- Se define un **front matter** con `title`, `description` y `patterns`.  
- Se agrupan secciones con encabezados (`##`) y se listan reglas concretas.  
- Se incluyen **fragmentos de código** ilustrando el estándar deseado.

Cursor, al detectar que estás trabajando en archivos `.py` dentro de `backend/`, inyectará estas directrices al prompt, lo que guiará las sugerencias de IA.

---

## 7. Recomendaciones finales

1. **Mantener las reglas actualizadas**: cuando cambie la arquitectura, se añada una librería o cambien las directrices, actualiza tus archivos en `.cursor/rules/`.  
2. **Evitar duplicidad o contradicción**: si tienes varias reglas que aplican al mismo tipo de archivo, revisa que no entren en conflicto.  
3. **Ser conciso**: cada palabra de más en las reglas ocupa espacio en el prompt, así que prioriza claridad sin extenderte en exceso.  
4. **Iterar y perfeccionar**: observa el comportamiento de la IA en Cursor, y si notas que ignora cierto lineamiento, reformula la regla o verifica tus patrones.  
5. **Prueba con ejemplos**: tras añadir o modificar reglas, abre un archivo relevante y pide a Cursor un snippet de código (por ejemplo, “crea un endpoint X”) para comprobar que se ajusta a tus reglas.

---

### Resumen

- **Ubicación**: Las reglas se almacenan en `.cursor/rules/`.  
- **Formato**: Cada archivo usa un bloque YAML al inicio (`title`, `description`, `patterns`) seguido de texto en Markdown.  
- **Aplicación**: Cursor filtra las reglas según los patrones al editar archivos, inyectando su contenido como directrices para la IA.  
- **Mantenimiento**: Las reglas se versionan junto con el proyecto y deben ajustarse a medida que evoluciona el código.  

Con este enfoque, tendrás reglas **estructuradas y eficaces** que guíen la autocompletación y las sugerencias de Cursor IDE, alineadas con las necesidades y convenciones de tu repositorio. ¡Éxito en la implementación!