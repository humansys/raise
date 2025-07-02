*ID JIRA:* {{jira_id}}
*Funcionalidad Relacionada:* [{{parent_Epic}}]({{parent_Epic_link}})

*Como* {{user_type}}
*Quiero* {{action}}
*Para* {{benefit}}

*Criterios de Aceptación*
```gherkin
# language: es
@historia-{{jira_id}}

Escenario: {{scenario_1_name}}
  @escenario-1
  Dado que {{initial_context}}
  Cuando {{action}}
  Entonces {{expected_result}}
  # Si se necesita, añadir más 'Y' o 'Pero'
  # Y {{additional_result}}

Escenario: {{scenario_2_name}}
  @escenario-2
  Dado que {{initial_context_2}}
  Cuando {{action_2}}
  # Si se necesita, añadir más 'Y' o 'Pero'
  # Entonces {{expected_result_2}}

# (Añadir más escenarios según sea necesario aquí dentro)
# Escenario: {{scenario_3_name}}
#   @escenario-3
#   Dado que ...
#   Cuando ...
#   Entonces ...
```

*Detalles Técnicos*

*Componentes Clave*
```yaml
componentes:
  - nombre: "{{component_name}}"
    descripción: "{{component_description}}"
    responsabilidad: "{{component_responsibility}}"
```

*Endpoints de API*
```yaml
api:
  - método: "GET"
    ruta: "/api/{{resource}}"
    propósito: "{{purpose}}"
  - método: "POST"
    ruta: "/api/{{resource}}"
    payload:
      campo1: "tipo_dato"
      campo2: "tipo_dato"
```

*Cambios en el Modelo de Datos*
```sql
-- Nuevos campos o tablas requeridas
ALTER TABLE {{table_name}}
ADD COLUMN {{column_name}} {{data_type}};
```

*Consideraciones UI/UX*
- [ ] {{ui_consideration_1}}
- [ ] {{ui_consideration_2}}

*Mockups / Diseños*

![{{mockup_description}}]({{mockup_url}})

*Pruebas Requeridas*

- [ ] *Pruebas Unitarias*
  ```typescript
  describe('{{component_name}}', () => {
    it('should {{test_description}}', () => {
      // Test case
    });
  });
  ```
- [ ] *Pruebas de Integración*
- [ ] *Pruebas de UI*
- [ ] *Pruebas de Rendimiento*
- [ ] *Pruebas de Seguridad*
- [ ] *Pruebas de Accesibilidad*

*Dependencias*

| ID | Tipo | Descripción | Estado |
|----|------|-------------|--------|
| {{dependency_id}} | {{type}} | {{description}} | {{status}} |

*Estimación*

| Métrica | Valor |
|---------|-------|
| Puntos de Historia | {{story_points}} |
| Tiempo Estimado | {{estimated_time}} |

*Notas Adicionales*

*Consideraciones Especiales*
- {{special_consideration_1}}
- {{special_consideration_2}}

*Referencias*
- [{{reference_name}}]({{reference_url}}) 