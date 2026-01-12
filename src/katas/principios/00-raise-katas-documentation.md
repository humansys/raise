# Documentación del Sistema de Katas RaiSE: Guía para el Desarrollo Confiable

## Introducción

Este documento describe el sistema de "Katas" del proyecto, una serie de ejercicios y guías prácticas diseñadas bajo el marco RaiSE (Reliable AI Software Engineering). Los katas son fundamentales para alinear tanto a los desarrolladores humanos como a los flujos de desarrollo asistidos por IA (agentes) con las convenciones, patrones y la "cultura de ingeniería" de este repositorio. Su objetivo principal es asegurar la **confiabilidad**, consistencia y calidad del software que construimos.

## ¿Qué son los Katas y Cuál es su Propósito?

En nuestro contexto, un kata es un documento estructurado que encapsula un estándar, un proceso, un patrón de diseño o una decisión arquitectónica específica del proyecto. Sirven para:

1.  **Internalizar la "Cultura del Repositorio":** Los katas codifican las prácticas probadas y las decisiones de diseño que definen cómo construimos software de manera confiable. Son la materialización de nuestra "cultura de ingeniería".
2.  **Guiar el Desarrollo Asistido por IA:** Cuando se genera un plan de implementación (por ejemplo, para una historia de usuario), los agentes de IA consultan estos katas. Los katas de niveles más profundos y con mayor detalle técnico sirven como referencia directa para la generación de código, asegurando que las soluciones propuestas por la IA se adhieran a nuestros estándares.
3.  **Capacitación y Onboarding:** Facilitan el aprendizaje y la adopción de nuestras metodologías y patrones por parte de los desarrolladores, promoviendo la uniformidad y reduciendo la curva de aprendizaje.
4.  **Fomentar la Confiabilidad (Reliability):** Al estandarizar enfoques para problemas comunes y promover patrones robustos, los katas son una herramienta clave para alcanzar los objetivos de confiabilidad de RaiSE.

## Estructura Jerárquica de los Katas

Los katas están organizados en una jerarquía de niveles, desde conceptos generales hasta detalles técnicos específicos. Esta estructura permite una comprensión progresiva y una aplicación contextual adecuada.

### Nivel L0: Meta-Katas (Fundamentos y Filosofía)
*   **Propósito:** Establecen los principios filosóficos y los conceptos fundamentales que rigen todo el ciclo de vida del desarrollo y mantenimiento dentro del proyecto.
*   **Ejemplos:** `L0-01-meta-kata-desarrollo.md`, `L0-02-meta-kata-mantenimiento.md`.
*   **Uso:** Proporcionan el "porqué" detrás de nuestras prácticas generales. Son la base conceptual sobre la que se construyen los demás niveles.

### Nivel L1: Katas de Proceso (Metodología y Flujos de Trabajo)
*   **Propósito:** Definen los procesos y metodologías clave que seguimos, especialmente en la planificación y ejecución de tareas de desarrollo.
*   **Ejemplos:** `L1-04-generacion-plan-implementacion-hu.md`, `L1-06-generacion-plan-hu-mobile.md`.
*   **Uso:** Guían cómo abordamos la descomposición de problemas, la planificación de la implementación de historias de usuario y otros flujos de trabajo esenciales. Informan a los agentes de IA sobre los pasos esperados en estos procesos.

### Nivel L2: Katas de Componentes y Patrones Arquitectónicos
*   **Propósito:** Describen en detalle los patrones de diseño, las estructuras de componentes y las implementaciones técnicas específicas para las diferentes partes de nuestra arquitectura.
*   **Ejemplos:** `L2-01-interfaces-dominio-kata.md`, `L2-03-casos-uso-kata.md`, `L2-05-repositorio-kata.md`, `L2-06-redux-estado-global.md`, `L2-07-viewmodel-kata.md`.
*   **Uso:** Estos son katas cruciales para la generación de código por IA. Cuando un plan de implementación requiere, por ejemplo, un nuevo repositorio o un componente ViewModel, el agente de IA consultará el kata L2 correspondiente para entender la estructura, las convenciones de nombrado, las dependencias típicas y los fragmentos de código ejemplares.

### Nivel L3: Katas Técnicos Avanzados y Especializados
*   **Propósito:** Profundizan en aspectos técnicos más complejos o especializados, a menudo construyendo sobre los patrones definidos en L2.
*   **Ejemplos:** `L3-01-modelado-datos-kata.md`, `L3-03-patrones-async-kata.md`, `L3-05-testing-estrategico.md`.
*   **Uso:** Proporcionan guía detallada para tareas que requieren un conocimiento técnico más profundo, como el diseño de modelos de datos complejos, la implementación de patrones asíncronos avanzados o la definición de estrategias de testing específicas. Los agentes de IA los utilizan para refinar implementaciones y abordar requisitos no triviales.

## ¿Cómo Guían los Katas a los Flujos Agénticos (IA)?

1.  **Referencia durante la Planificación:** Al generar un plan de implementación para una historia de usuario, los katas L1 (y L0 subyacentes) ayudan a estructurar el plan de acuerdo con nuestros procesos.
2.  **Consulta para Generación de Código:** Cuando el plan de implementación se traduce en tareas de codificación, los agentes de IA se refieren a los katas L2 y L3 relevantes. Por ejemplo:
    *   Si una tarea implica crear una nueva entidad de dominio, el agente consultará `L2-02-entidades-dominio.md` (o similar).
    *   Si se necesita implementar un nuevo caso de uso, se basará en `L2-03-casos-uso-kata.md`.
3.  **Adherencia a Patrones:** Los ejemplos de "código bueno" y las directrices en los katas aseguran que el código generado por la IA siga los patrones establecidos, utilice las convenciones de nombrado correctas y se integre adecuadamente con el resto del sistema.
4.  **Consistencia y Reducción de Errores:** Al tener una fuente de verdad clara sobre cómo implementar ciertas funcionalidades o componentes, se reduce la variabilidad y la probabilidad de introducir errores o anti-patrones.

## Relación con RaiSE y la Confiabilidad

El sistema de Katas es una manifestación directa de varios principios de RaiSE:

*   **Reglas Explícitas y Consistentes:** Los katas hacen explícitas nuestras reglas de diseño e implementación.
*   **Confiabilidad como Prioridad:** Están diseñados para promover patrones que llevan a software más robusto, mantenible y predecible.
*   **Orquestación Humana:** Si bien guían a la IA, también sirven como material de aprendizaje y referencia para los desarrolladores, quienes siguen siendo los orquestadores finales del proceso.
*   **Conocimiento Documentado y Compartido:** Centralizan el conocimiento técnico y las mejores prácticas del proyecto, haciéndolos accesibles a todo el equipo y a los sistemas de IA.

## Conclusión

El sistema de Katas es una inversión estratégica en la calidad y confiabilidad de nuestro software. Al definir y mantener estos katas, no solo mejoramos la eficiencia y consistencia del desarrollo asistido por IA, sino que también fortalecemos el conocimiento colectivo del equipo y aseguramos que el proyecto evolucione de manera coherente y robusta.

Se espera que todos los desarrolladores se familiaricen con los katas relevantes para su trabajo y contribuyan a su mejora continua a medida que el proyecto evoluciona. 