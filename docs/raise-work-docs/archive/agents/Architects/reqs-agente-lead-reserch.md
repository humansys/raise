# Especificación de Requerimiento para el Agente de IA Generativa

## Título del Proyecto
Desarrollo de un Agente de IA Generativa para la Prospección de Leads en humansys

## Objetivo
Implementar un agente de IA generativa en la plataforma dify.ai que procese leads recibidos por correo electrónico, investigue información relevante sobre los leads y genere un reporte y un mensaje inicial pre-llenado en Gmail para el vendedor asignado. Además, se requiere que tanto el reporte como los datos del lead se guarden en JIRA.

## Alcance
El agente deberá realizar las siguientes funciones:
1. **Recepción de Correo Electrónico**: Detectar nuevos correos electrónicos en Gmail que contengan información sobre leads.
2. **Extracción de Información**: Extraer datos relevantes del correo electrónico, incluyendo nombre del solicitante, empresa, descripción de la oportunidad, y datos de contacto.
3. **Investigación**: Realizar una búsqueda en internet para obtener información adicional sobre la empresa y el solicitante.
4. **Generación de Reporte**: Crear un reporte que incluya información sobre la empresa, el rol del solicitante y posibles necesidades.
5. **Generación de Mensaje Inicial**: Crear un borrador de correo electrónico pre-llenado en Gmail para el vendedor asignado.
6. **Integración con JIRA**: Guardar el reporte y los datos del lead en JIRA para su seguimiento.

## Requerimientos Funcionales

### 1. Recepción de Correo Electrónico
- **Descripción**: El agente debe integrarse con Gmail para detectar nuevos correos electrónicos que contengan leads.
- **Herramienta**: Make (Integromat) para la integración con Gmail.

### 2. Extracción de Información
- **Descripción**: Extraer datos relevantes del correo electrónico.
- **Datos a Extraer**:
  - Nombre del solicitante
  - Empresa
  - Descripción de la oportunidad
  - Email
  - Teléfono

### 3. Investigación
- **Descripción**: Realizar una búsqueda en internet para obtener información adicional sobre la empresa y el solicitante.
- **Herramientas**:
  - Scraping Web (Beautiful Soup, Scrapy)
  - LinkedIn API para obtener información sobre el solicitante.

### 4. Generación de Reporte
- **Descripción**: Crear un reporte que incluya:
  - Información de la empresa
  - Rol del solicitante
  - Posibles necesidades identificadas

### 5. Generación de Mensaje Inicial
- **Descripción**: Crear un borrador de correo electrónico pre-llenado en Gmail.
- **Formato del Mensaje**:
  ```text
  Asunto: Oportunidad de colaboración con [Nombre de la Empresa]

  Estimado [Nombre del Solicitante],

  Espero que estés bien. He recibido tu consulta sobre [Descripción de la Oportunidad] y me gustaría discutir cómo podemos ayudarte a optimizar tus procesos con nuestras soluciones de Atlassian.

  ¿Te gustaría agendar una llamada para hablar más al respecto?

  Saludos,
  [Tu Nombre]
  [Tu Puesto]
  humansys
  ```

### 6. Integración con JIRA
- **Descripción**: Guardar el reporte y los datos del lead en JIRA.
- **Herramienta**: JIRA API para crear tickets o almacenar información relevante.

## Requerimientos No Funcionales
- **Seguridad**: Asegurar que toda la información recopilada y almacenada cumpla con las políticas de privacidad y normativas de protección de datos.
- **Escalabilidad**: El sistema debe ser capaz de manejar múltiples leads simultáneamente sin degradar el rendimiento.
- **Usabilidad**: La interfaz de usuario debe ser intuitiva para que los vendedores puedan acceder fácilmente a los borradores de correos y reportes.

## Viabilidad Técnica
### Capacidades de las Herramientas
1. **dify.ai**: Plataforma de agentes que permite la creación de agentes de IA generativa. Soporta integraciones con APIs y puede manejar flujos de trabajo complejos.
2. **Gmail API**: Permite la integración con Gmail para enviar, recibir y gestionar correos electrónicos. Soporta la creación de borradores pre-llenados.
3. **JIRA API**: Permite la creación y gestión de tickets en JIRA, lo que facilita el seguimiento de leads y la documentación de interacciones.

### Conclusión de Viabilidad
La implementación de este flujo de trabajo es viable utilizando las herramientas mencionadas. La integración entre dify.ai, Gmail y JIRA es factible y permitirá automatizar el proceso de prospección de leads de manera eficiente.

## Próximos Pasos
1. Validar esta especificación con el Product Owner.
2. Asignar recursos para el desarrollo del agente.
3. Establecer un cronograma para la implementación y pruebas.

---

**Fecha de Creación**: [Fecha]
**Creado por**: [Tu Nombre]


ATATT3xFfGF0A0pIvDNKkucEfMx_kZRdVlt8ORexOHV1UUYMY0vldNkqZtVDhT_CoIUgClKkzDFxP6rLp0YZCl9HswLEM_x2jxejnNljjgvpiWfGellEeZDhh-AfHn5Sl1tgVcsjpvpreWfnJG3DIO9LW8sc-ILrk_krHkcWWTLgyXUObp-CxiY=73146BBA
