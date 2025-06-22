*ID JIRA:* RAISE-119
*Funcionalidad Relacionada:* [RAISE-86 (Reglas)](https://humansys.atlassian.net/browse/RAISE-86)

*Como* Mantenedor de Reglas / Desarrollador
*Quiero* Refactorizar las reglas de cursor existentes para usar el formato YAML front matter estándar y añadir las cabeceras requeridas (`name`, `description`, `globs`)
*Para* Que Cursor IDE pueda descubrir, cargar y aplicar correctamente las reglas, mejorando la guía contextual para el desarrollo.

*Criterios de Aceptación*
```gherkin
# language: es
@historia-RAISE-119

Escenario: Verificar carga de regla refactorizada
  @escenario-1
  Dado que una regla de cursor ha sido refactorizada al formato YAML estándar con cabeceras `name`, `description`, y `globs`
  Cuando se abre un archivo que coincide con el `glob` de la regla refactorizada en Cursor IDE
  Entonces la regla refactorizada aparece como adjunta automáticamente y su contenido se incluye en el contexto del asistente IA

Escenario: Intentar usar regla con formato antiguo
  @escenario-2
  Dado que una regla de cursor aún utiliza el formato antiguo "Rule Name/Description" sin cabeceras YAML
  Cuando se abre un archivo que debería coincidir con el propósito de la regla antigua en Cursor IDE
  Entonces la regla antigua no se carga automáticamente y no está disponible en el contexto del asistente IA (o la IDE muestra una advertencia sobre el formato)

```

*Detalles Técnicos*

*Componentes Clave*
```yaml
componentes:
  - nombre: "Archivo de Regla (.mdc)"
    descripción: "Archivo Markdown con cabecera YAML para definir reglas de Cursor."
    responsabilidad: "Contener las directrices y metadatos (nombre, descripción, globs) para una regla específica."
```

*Endpoints de API*
```yaml
api: [] # No aplica
```

*Cambios en el Modelo de Datos*
```sql
-- No aplica
```

*Consideraciones UI/UX*
- [ ] No aplica

*Mockups / Diseños*

N/A

*Pruebas Requeridas*

- [X] *Pruebas Unitarias:* N/A (Se verifica manualmente o mediante la observacion del comportamiento del IDE).
- [ ] *Pruebas de Integración:* Verificar en Cursor IDE que las reglas refactorizadas se cargan correctamente según sus `globs`.
- [ ] *Pruebas de UI:* N/A
- [ ] *Pruebas de Rendimiento:* N/A
- [ ] *Pruebas de Seguridad:* N/A
- [ ] *Pruebas de Accesibilidad:* N/A

*Dependencias*

| ID | Tipo | Descripción | Estado |
|----|------|-------------|--------|
| N/A | N/A | No hay dependencias externas directas para este cambio de formato. | - |

*Estimación*

| Métrica | Valor |
|---------|-------|
| Puntos de Historia | 2 (Depende del número de reglas a refactorizar) |
| Tiempo Estimado | ~1-2h (Depende del número de reglas) |

*Notas Adicionales*

La refactorización debe seguir estrictamente las directrices definidas en `900-rule-authoring-guidelines.mdc`. Es crucial definir `globs` precisos para cada regla.

*Consideraciones Especiales*
- Asegurar que los campos `name`, `description`, y `globs` sean completados correctamente en la cabecera YAML de cada regla refactorizada.
- Validar el formato YAML después de la refactorización.

*Referencias*
- [.cursor/rules/900-rule-authoring-guidelines.mdc](<place_holder_for_actual_path_or_link>) 