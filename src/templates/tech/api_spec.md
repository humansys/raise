# Especificación de API: [Nombre del Endpoint o Propósito]

**Funcionalidad/Historia de Usuario/Diseño Técnico Relacionado:** [Enlace o ID]

## Endpoint: `[MÉTODO] /ruta/al/endpoint/{param}`

*(Ejemplo: `POST /api/v1/users/{userId}/profile`)*

**Descripción:**
*(Proporcione una descripción clara de lo que hace este endpoint.)*

**Solicitud:**

*   **Parámetros de Ruta:**
    *   `{nombre_param}`: (Tipo: `string`/`integer`/etc., Requerido: Sí/No) - Descripción.
    *   *(Agregar más si es necesario)*
*   **Parámetros de Consulta:**
    *   `param_consulta`: (Tipo: `string`/`integer`/etc., Requerido: Sí/No, Valor por defecto: `valor`) - Descripción.
    *   *(Agregar más si es necesario)*
*   **Encabezados:**
    *   `Nombre-Encabezado`: (Ejemplo: `Content-Type: application/json`) - Descripción/Propósito.
    *   *(Agregar más si es necesario)*
*   **Cuerpo de la Solicitud:**
    *   **Tipo de Contenido:** `application/json` (u otro)
    *   **Esquema/Estructura:**
        ```json
        {
          "clave": "tipo_valor (ej., string)",
          "anidado": {
            "otraClave": "boolean"
          },
          "claveArray": ["string"]
        }
        ```
    *   **Descripción:** *(Explicar el propósito de los campos)*
    *   **Reglas de Validación:** *(ej., el campo 'email' debe tener un formato de correo válido)*

**Respuestas:**

*   **Respuesta Exitosa (`200 OK` o `201 Created`, etc.):**
    *   **Tipo de Contenido:** `application/json` (u otro)
    *   **Esquema/Estructura del Cuerpo:**
        ```json
        {
          "id": "string",
          "estado": "string",
          "datos": { ... }
        }
        ```
    *   **Descripción:** *(Explicar los campos de la respuesta)*
*   **Respuesta de Error (`400 Bad Request`):**
    *   **Tipo de Contenido:** `application/json`
    *   **Esquema/Estructura del Cuerpo:**
        ```json
        {
          "error": "string (ej., ENTRADA_INVALIDA)",
          "mensaje": "string (Descripción del error legible)",
          "detalles": { ... } // Errores específicos de campo opcionales
        }
        ```
    *   **Causa:** *(Cuándo ocurre este error, ej., Campo requerido faltante)*
*   **Respuesta de Error (`404 Not Found`):**
    *   **Tipo de Contenido:** `application/json`
    *   **Esquema/Estructura del Cuerpo:** *(Similar al 400)*
    *   **Causa:** *(ej., El recurso con el ID especificado no existe)*
*   *(Agregar otros códigos de estado relevantes como 401, 403, 500 según sea necesario)*

**Autenticación y Autorización:**
*(Especificar método de autenticación requerido (ej., Token JWT Bearer) y requisitos de autorización (ej., El rol del usuario debe ser 'Admin').)*

**Ejemplo de Solicitud:**
```bash
curl -X POST \
  'https://tu-api.com/api/v1/users/123/profile' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "nombreMostrado": "Nuevo Nombre",
    "preferencias": { "tema": "oscuro" }
  }'
```

**Ejemplo de Respuesta Exitosa (`200 OK`):**
```json
{
  "id": "123",
  "estado": "actualizado",
  "datos": {
    "nombreMostrado": "Nuevo Nombre",
    "email": "usuario@ejemplo.com",
    "preferencias": {
      "tema": "oscuro"
    }
  }
}
```

**Notas:**
*(Cualquier contexto adicional, información sobre límites de tasa, consideraciones específicas.)* 