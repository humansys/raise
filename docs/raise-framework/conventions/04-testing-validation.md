# 04: Pruebas y Validación

## Alcance

*   Incluye pruebas unitarias, de integración, E2E (cuando aplique), análisis estático de código y validación semántica contra requisitos y diseño.

## Proceso y Convenciones

1.  **Pruebas Guiadas por Requisitos:** Las pruebas automatizadas (especialmente unitarias y de integración) **deben** verificar directamente los Criterios de Aceptación definidos (historias BDD) y las especificaciones (API, Componente).
2.  **Generación Asistida de Pruebas:** Utilizar la IA (y el agente QA si está configurado) para generar casos de prueba basados en las especificaciones. Proporcionar el archivo de especificación como contexto clave.
3.  **Validación Multinivel:** La validación en RaiSE va más allá de la ejecución de pruebas:
    *   **Funcional:** ¿El código hace lo que se supone que debe hacer según los AC?
    *   **Estructural:** ¿Cumple con las reglas de estilo (`.cursor/rules/`), linters y formateadores configurados?
    *   **Arquitectónica:** ¿Se alinea con los patrones y decisiones definidos en el Diseño Técnico?
    *   **Semántica:** ¿Refleja correctamente la lógica y las reglas de negocio del dominio?
4.  **Integración Continua (CI):** Todas las pruebas automatizadas y chequeos de calidad (linting, formato) **deben** ejecutarse como parte de la pipeline de CI/CD definida para el proyecto.
5.  **Revisión Humana:** Aunque la IA asiste en la generación de pruebas, la revisión humana es necesaria para asegurar la relevancia, cobertura adecuada y mantenibilidad de las pruebas. 