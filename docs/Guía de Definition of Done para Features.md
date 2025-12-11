# **Informe Exhaustivo: Guía de Implementación, Gestión y Evolución de la "Definition of Done" (DoD) a Nivel de Feature en Entornos Ágiles**

## **1\. Introducción: La Crisis de la Terminación y la Filosofía del "Hecho"**

En la industria del desarrollo de software moderno y la gestión de productos digitales, la ambigüedad en torno a la finalización de tareas representa uno de los riesgos más insidiosos y costosos para las organizaciones. La pregunta aparentemente inocua "¿Está terminada esta funcionalidad?" a menudo desencadena una cascada de interpretaciones subjetivas que varían drásticamente entre desarrolladores, especialistas en aseguramiento de calidad (QA), Product Owners y stakeholders ejecutivos. Para un desarrollador, "hecho" puede significar simplemente que el código ha sido escrito y compila en su máquina local. Para un QA, puede implicar que los casos de prueba han sido ejecutados. Para Operaciones, significa que está desplegado y monitoreado en producción. Para el negocio, "hecho" es sinónimo de valor entregado y monetizable en manos del cliente final. Esta disonancia cognitiva y operativa es el caldo de cultivo para la deuda técnica, los defectos de escape a producción y la erosión de la confianza entre los equipos técnicos y el negocio.1

La "Definition of Done" (DoD), o Definición de Hecho, surge en este contexto no como una simple lista de verificación administrativa, sino como un artefacto fundamental de gobernanza y transparencia en los marcos de trabajo ágiles como Scrum, Kanban y SAFe. Representa un acuerdo formal, un contrato social explícito y compartido que establece los estándares de calidad innegociables que debe cumplir cualquier incremento de producto para ser considerado completo y potencialmente desplegable.4 Sin embargo, la aplicación de este concepto se vuelve exponencialmente más compleja cuando elevamos la granularidad del trabajo desde la simple Historia de Usuario (User Story) hasta la Feature (Funcionalidad o Característica).

Una Feature, al ser una agrupación lógica de valor que a menudo abarca múltiples historias de usuario y, en ocasiones, múltiples sprints, requiere una arquitectura de calidad sistémica. Implementar una DoD a nivel de Feature no es simplemente agregar más casillas de verificación; implica una reingeniería del flujo de valor para asegurar que la integración, la validación de extremo a extremo (E2E), el cumplimiento normativo y la preparación operativa se realicen de manera continua y rigurosa. Este informe disecciona la anatomía, el proceso de creación y la gestión operativa de la DoD para Features, proporcionando una guía definitiva para equipos que buscan trascender el "casi hecho" y alcanzar la excelencia en la entrega.6

### **1.1. El Costo Económico del "Undone Work"**

El concepto de "Undone Work" (Trabajo No Hecho) es central para entender la necesidad de una DoD robusta. Cuando un equipo marca una Feature como "completada" pero omite tareas críticas como la actualización de la documentación, las pruebas de regresión automatizadas o la revisión de seguridad, crea una deuda invisible. Este trabajo no desaparece; se acumula como un pasivo oculto que deberá pagarse con intereses en el futuro, a menudo en forma de parches de emergencia (hotfixes), refactorización costosa o incidentes de seguridad. Una DoD estricta actúa como un mecanismo de contención de costos, forzando al equipo a internalizar el esfuerzo real de desarrollo dentro del ciclo de vida de la Feature, en lugar de externalizarlo hacia el futuro o hacia otros departamentos.8

## **2\. Taxonomía del Trabajo Ágil: Epic, Feature y User Story**

Para aplicar correctamente una Definition of Done, es imperativo establecer una taxonomía clara del trabajo. La confusión entre niveles jerárquicos conduce a la aplicación de criterios de calidad incorrectos: criterios demasiado laxos para funcionalidades críticas o burocracia excesiva para tareas menores. La estructura jerárquica estándar en herramientas como Jira y marcos como SAFe distingue tres niveles principales, cada uno con sus propias expectativas de "Hecho".10

### **2.1. Epic (Épica): La Visión Estratégica**

En la cúspide de la jerarquía se encuentra la Épica. Una Épica representa una iniciativa estratégica de gran envergadura, a menudo alineada con los objetivos trimestrales o anuales de la empresa (OKRs). Por su naturaleza, una Épica es demasiado grande para ser entregada en un solo sprint y suele abarcar múltiples Features.

* **Naturaleza:** Estratégica, de largo plazo.
* **DoD de Épica:** Se centra en la validación de hipótesis de negocio, el cumplimiento de KPIs macroeconómicos, la finalización de todas las Features hijas y la validación de la arquitectura empresarial. "Hecho" aquí significa que la iniciativa ha entregado el ROI esperado o ha completado su ciclo de vida de inversión.6

### **2.2. Feature (Característica): La Unidad de Valor Entregable**

La Feature es el nivel crítico donde la estrategia se encuentra con la ejecución. Se define como una funcionalidad distintiva que satisface una necesidad del usuario o resuelve un problema específico, y que es lo suficientemente sustancial como para justificar un anuncio de lanzamiento o una nota en el registro de cambios (changelog), pero lo suficientemente pequeña para ser completada dentro de un Program Increment (PI) o una serie de sprints consecutivos.

* **Naturaleza:** Táctica-Operativa, orientada al usuario final.
* **Relación:** Una Feature se descompone en múltiples User Stories.
* **DoD de Feature:** Este es el foco de nuestro informe. Implica que todas las historias componentes están terminadas, integradas, probadas como un flujo completo, documentadas y listas para su despliegue en producción. La Feature DoD asegura la integridad sistémica.14

### **2.3. User Story (Historia de Usuario): La Unidad de Trabajo Atómico**

La Historia de Usuario es la unidad indivisible de trabajo planificable en un sprint. Describe una necesidad vertical muy específica.

* **Naturaleza:** Ejecución inmediata, sprint individual.
* **DoD de Historia:** Se enfoca en la calidad del código, pruebas unitarias y cumplimiento de los criterios de aceptación específicos de esa pequeña rebanada de funcionalidad. Es importante notar que una historia puede estar "Hecha" técnicamente, pero la Feature a la que pertenece puede no estar "Hecha" hasta que todas las demás historias se integren.11

### **2.4. Tabla de Diferenciación Jerárquica**

La siguiente tabla sintetiza las diferencias estructurales y de calidad esperada entre estos tres niveles, ayudando a clarificar dónde debe aplicarse cada lista de verificación.

| Dimensión                      | User Story (Historia)                        | Feature (Característica)                        | Epic (Épica)                                             |
| :------------------------------ | :------------------------------------------- | :----------------------------------------------- | :-------------------------------------------------------- |
| **Duración Típica**     | 1 Sprint (o menos)                           | 1-5 Sprints (o 1 Program Increment)              | Múltiples Sprints / Trimestres                           |
| **Enfoque de Valor**      | Valor incremental / micro-funcionalidad      | Valor completo / Solución de problema           | Iniciativa Estratégica / Nuevo Mercado                   |
| **Responsable Principal** | Equipo de Desarrollo                         | Product Owner / Product Manager                  | Product Manager / Portfolio Manager                       |
| **Enfoque de la DoD**     | Calidad del Código y Funcionalidad Unitaria | Integración, Flujo E2E, No-Funcionales          | Impacto de Negocio, ROI, Arquitectura                     |
| **Ejemplo de Criterio**   | "Tests unitarios pasan", "Code Review OK"    | "Tests de regresión pasan", "Docs actualizados" | "Análisis de mercado completo", "Go-to-Market ejecutado" |
| **Herramienta (Jira)**    | Issue Type: Story/Task                       | Issue Type: Feature/Epic (según config.)        | Issue Type: Epic/Initiative                               |

Fuente: Síntesis basada en el análisis comparativo de.6

## **3\. Marco Conceptual: La Tríada de la Calidad (DoD, AC, DoR)**

Para navegar el proceso de definición de hecho, es crucial distinguir la DoD de otros dos conceptos adyacentes con los que frecuentemente se confunde: los Criterios de Aceptación (AC) y la Definición de Preparado (DoR). Estos tres elementos forman una "Tríada de Calidad" que protege el flujo de trabajo ágil tanto a la entrada como a la salida.1

### **3.1. Definition of Done (DoD) vs. Criterios de Aceptación (AC)**

La distinción más crítica reside en el alcance y la universalidad. Mientras que la DoD es un estándar global, los AC son locales y específicos.

* **Definition of Done (DoD):** Es universal. Aplica a *todas* las Features por igual (o a todas las historias). Responde a la pregunta: "¿Cumple este trabajo con los estándares de ingeniería y calidad de nuestra organización?". Incluye elementos como revisiones de código, cobertura de pruebas, estándares de documentación y cumplimiento de seguridad. Es un acuerdo estático (aunque evoluciona lentamente).19
* **Criterios de Aceptación (AC):** Son específicos. Aplican únicamente a *una* Feature o Historia en particular. Definen el comportamiento funcional esperado. Responden a la pregunta: "¿Hace el software lo que el usuario pidió en este caso específico?". Por ejemplo, para una Feature de "Login", los AC incluirían "El usuario debe ser bloqueado tras 3 intentos fallidos". Los AC cambian con cada nuevo ítem del backlog.4

**Insight de Segundo Orden:** Existe una relación de contención lógica. Una Feature no puede cumplir su DoD si no ha cumplido sus AC. La verificación de los AC es, de hecho, a menudo uno de los ítems dentro de la lista de verificación de la DoD (ej. "Ítem de DoD: Todos los Criterios de Aceptación han sido verificados y aprobados por el PO").22

### **3.2. Definition of Done (DoD) vs. Definition of Ready (DoR)**

Esta relación es temporal y direccional. La DoR protege la entrada del sprint; la DoD protege la salida.

* **Definition of Ready (DoR):** Establece los requisitos previos que una Feature debe cumplir *antes* de que el equipo acepte trabajar en ella. ¿Está clara la descripción? ¿Se han identificado las dependencias? ¿Están listos los diseños de UX? ¿Se ha estimado el esfuerzo? Si una Feature no cumple la DoR, se considera que tiene un alto riesgo de bloqueo y no debe entrar en planificación.18
* **Definition of Done (DoD):** Establece las condiciones para *finalizar* el trabajo. Si no se cumple, el trabajo no se libera.

La interacción entre DoR y DoD crea un sistema de "esclusas" de calidad. Un equipo que ignora la DoR (aceptando trabajo vago) inevitablemente fallará en cumplir la DoD (entregando trabajo defectuoso o incompleto) debido a la falta de claridad inicial. Por ende, una DoD fuerte requiere una DoR fuerte.18

## **4\. El Proceso de Creación de la DoD para una Feature**

Crear una Definition of Done efectiva no es una tarea administrativa de copiar y pegar una plantilla genérica. Debe ser un ejercicio colaborativo y reflexivo que involucre a todo el Equipo Scrum y stakeholders clave para asegurar el compromiso y la viabilidad técnica.24 A continuación, se detalla un proceso de taller estructurado para definir la DoD.

### **4.1. Preparación y Participantes**

El taller debe ser facilitado por el Scrum Master. Los asistentes obligatorios son el Equipo de Desarrollo (quienes ejecutan el trabajo) y el Product Owner (quien valida el valor). Para una DoD a nivel de Feature, es altamente recomendable invitar a representantes de Arquitectura, Seguridad, Operaciones (DevOps) y Soporte, ya que las Features impactan estas áreas más que las historias individuales.25

### **4.2. Dinámica del Taller (Paso a Paso)**

#### **Paso 1: Lluvia de Ideas (Divergencia)**

El facilitador pide al equipo que imagine que están a punto de lanzar una Feature crítica a producción. La pregunta detonante es: "¿Qué debe haber sucedido para que podamos irnos a dormir tranquilos sabiendo que esto no fallará y que el usuario estará satisfecho?".
Cada participante escribe actividades en notas adhesivas (ej. "Tests pasados", "Código revisado", "UX validada", "Marketing notificado").27

#### **Paso 2: Agrupación y Consolidación (Convergencia)**

El equipo agrupa las notas en categorías lógicas (Calidad, Documentación, Procesos, Seguridad). Se eliminan duplicados y se clarifican términos ambiguos (ej. cambiar "Probado" por "Pruebas de regresión automatizadas pasadas").24

#### **Paso 3: Filtrado de Realidad (Lo Posible vs. Lo Ideal)**

Esta es la fase crítica donde se evita la frustración futura. Se dibuja una línea divisoria en el tablero:

* **DoD Actual (Compromiso):** Actividades que el equipo puede realizar *hoy* con las herramientas y habilidades actuales para *cada* Feature.
* **DoD Futura/Ideal (Aspiracional):** Actividades que el equipo sabe que *debería* hacer (ej. "Tests de carga automatizados", "Análisis de seguridad estático"), pero que actualmente no puede realizar por falta de infraestructura o tiempo. Estos ítems se convierten en impedimentos organizacionales que deben resolverse con el tiempo para "madurar" la DoD.8

#### **Paso 4: Definición de Criterios Claros y Testeables**

Cada ítem seleccionado para la DoD Actual debe ser binario (Sí/No). Evitar términos subjetivos como "Código bueno" o "Documentación suficiente". Usar en su lugar "Código cumple con guía de estilo linter" o "Documentación de API actualizada en Swagger".5

#### **Paso 5: Publicación y Acuerdo**

La lista final se formaliza en un "Acuerdo de Trabajo" o "Team Charter". Debe ser visible en el espacio de trabajo (físico o digital, como un Dashboard de Jira o Confluence) y todos los miembros deben comprometerse explícitamente a respetarla. No es una imposición de la gerencia, es un estándar autoimpuesto por el equipo.3

## **5\. Componentes Detallados de una DoD para Features**

Una DoD robusta para una Feature debe ser multidimensional. A continuación, se desglosa una lista exhaustiva de criterios, organizados por dimensiones de calidad, explicando el *por qué* de cada uno. Esta sección sirve como menú para que los equipos seleccionen sus criterios.

### **5.1. Dimensión de Calidad del Código e Integración**

A nivel de Feature, la preocupación principal es la integridad estructural y la fusión limpia del código.

* **Control de Versiones:** Todo el código de las historias constituyentes debe estar fusionado (merged) en la rama objetivo (ej. develop, main o release branch) sin conflictos de fusión pendientes.
* **Limpieza de Ramas:** Las ramas de características (feature branches) temporales deben ser eliminadas tras la fusión para mantener la higiene del repositorio.
* **Análisis Estático:** El código debe pasar por herramientas de análisis estático (ej. SonarQube) cumpliendo los umbrales de calidad definidos (ej. 0 vulnerabilidades críticas, deuda técnica \< 5%).20
* **Revisión de Pares (Peer Review):** No solo revisión de código, sino revisión de la lógica de la Feature completa. ¿Se han seguido los patrones de diseño arquitectónico acordados?.5

### **5.2. Dimensión de Aseguramiento de Calidad (QA) y Pruebas**

Aquí es donde la DoD de Feature difiere más de la de Historia. Se requiere una visión holística.

* **Pruebas de Regresión:** Verificación obligatoria de que la nueva Feature no ha roto funcionalidades existentes en otras partes del sistema. Esto es crítico porque las Features a menudo tocan código compartido.6
* **Pruebas de Integración E2E:** Ejecución de escenarios de prueba que atraviesan todo el flujo de la Feature, incluyendo interacciones con bases de datos, APIs externas y microservicios.
* **Cobertura de Código:** Cumplimiento del porcentaje acordado (ej. \>80%) no solo en unitarios, sino en la cobertura funcional de la Feature.
* **Defectos:** Política de cero defectos críticos/mayores conocidos. Los defectos menores pueden ser aceptados si se documentan y priorizan como deuda técnica, pero esto debe ser una decisión consciente.3

### **5.3. Dimensión Operativa y Despliegue (DevOps)**

Una Feature no sirve si no se puede operar o desplegar de manera fiable.

* **Configuración:** Los scripts de configuración, variables de entorno y secretos necesarios para la Feature deben estar actualizados en los sistemas de gestión de configuración (ej. Kubernetes ConfigMaps).
* **Base de Datos:** Scripts de migración de base de datos probados (incluyendo scripts de rollback en caso de fallo).33
* **Monitoreo:** Se han implementado logs adecuados y métricas de negocio/técnicas para monitorear la salud y el uso de la Feature en producción (Observabilidad).33
* **Entorno:** Desplegado y verificado exitosamente en un entorno de Staging/Pre-producción que sea un espejo fiel de Producción.1

### **5.4. Dimensión de Documentación y Cumplimiento**

* **Documentación Técnica:** Diagramas de arquitectura actualizados, documentación de API (Swagger/OpenAPI) generada.
* **Documentación de Usuario:** Guías de usuario, FAQs y materiales de ayuda actualizados para reflejar la nueva funcionalidad.5
* **Notas de Lanzamiento (Release Notes):** Texto descriptivo listo para ser incluido en la comunicación a clientes o stakeholders internos.
* **Cumplimiento Legal/Seguridad:** Aprobación de auditoría de seguridad (si aplica), cumplimiento de GDPR (ej. si la Feature recolecta nuevos datos personales), y validación de accesibilidad (WCAG).33

### **5.5. Dimensión de Negocio (Product Ownership)**

* **Aceptación del PO:** El Product Owner ha revisado la Feature funcionando en el entorno de Staging y ha confirmado que cumple con la visión y los Criterios de Aceptación agregados.6
* **Demo a Stakeholders:** La Feature ha sido demostrada a los interesados clave (ej. equipo de ventas, soporte) y se ha capturado su feedback inicial (aunque la aprobación formal suele ser del PO).37

## **6\. Ejemplos de Listas de Verificación (Checklists) por Industria**

La DoD no es "talla única". Dependiendo de la industria y la criticidad del software, la DoD variará en rigor. A continuación, se presentan ejemplos adaptados a tres sectores distintos basados en la investigación.33

### **6.1. Ejemplo 1: Industria SaaS (Software as a Service) \- Enfoque en Velocidad**

En un entorno SaaS B2B o B2C, la velocidad de despliegue y la experiencia de usuario (UX) son primordiales.

| Categoría           | Criterio DoD                                                         |
| :------------------- | :------------------------------------------------------------------- |
| **Calidad**    | Code Review aprobado por 1 par. Coverage\> 80%.                      |
| **Pruebas**    | Pruebas automatizadas de UI (Cypress/Selenium) para el "Happy Path". |
| **Despliegue** | Feature Flag creado y apagado por defecto (Dark Launch).             |
| **UX/UI**      | Revisión visual contra Figma/Sketch aprobada por el Diseñador.     |
| **Negocio**    | Analytics (Mixpanel/GA) implementados para trackear uso.             |

### **6.2. Ejemplo 2: Industria Financiera/Bancaria (Fintech) \- Enfoque en Seguridad**

Aquí la tolerancia al riesgo es cero. La DoD es pesada en cumplimiento y seguridad.

| Categoría           | Criterio DoD                                                                                     |
| :------------------- | :----------------------------------------------------------------------------------------------- |
| **Calidad**    | Code Review aprobado por 2 pares (incluyendo 1 senior). Coverage\> 90%.                          |
| **Seguridad**  | Análisis estático de seguridad (SAST) limpio. Scan de dependencias (OWASP) limpio.             |
| **Pruebas**    | Pruebas de penetración (PenTest) ejecutadas en el módulo. Pruebas de integridad transaccional. |
| **Compliance** | Auditoría de PCI-DSS verificada. Logs de auditoría implementados inmutables.                   |
| **Ops**        | Plan de Rollback documentado y probado en simulacro.                                             |

### **6.3. Ejemplo 3: Salud (HealthTech/HIPAA) \- Enfoque en Privacidad**

El foco está en la protección de datos del paciente y la trazabilidad.

| Categoría               | Criterio DoD                                                                   |
| :----------------------- | :----------------------------------------------------------------------------- |
| **Privacidad**     | Validación de encriptación de datos en reposo y tránsito (PHI).             |
| **Accesos**        | Controles de acceso (RBAC) verificados estrictamente.                          |
| **Trazabilidad**   | Cada línea de código trazable a un requisito (User Story) y un Test Case.    |
| **Documentación** | Evaluación de impacto en privacidad actualizada. Manual clínico actualizado. |
| **Aprobación**    | Firma digital del Oficial de Cumplimiento (Compliance Officer).                |

## **7\. Integración Operativa: La DoD en el Ciclo de Vida del Sprint**

La DoD debe ser una herramienta viva, integrada en cada evento de Scrum, no un documento que se consulta solo al final.35

### **7.1. Sprint Planning (Planificación)**

Durante la planificación, el equipo debe consultar la DoD al estimar las Features. Una Feature que parece simple de codificar puede tener una estimación alta si la DoD exige pruebas de carga y documentación extensa.

* **Acción:** El equipo pregunta: "¿El esfuerzo estimado incluye la creación de los tests de regresión y la actualización de la Wiki como exige nuestra DoD?". Esto evita subestimaciones crónicas.2

### **7.2. Daily Scrum (Reunión Diaria)**

Los miembros del equipo deben reportar progreso en función de la DoD.

* **Anti-patrón:** "Ya terminé la codificación, así que estoy listo."
* **Patrón Correcto:** "Terminé la codificación, pero aún me falta actualizar la documentación y pasar el análisis de seguridad según la DoD, así que aún no está Done.".5

### **7.3. Sprint Review (Revisión)**

Este es el momento de la verdad. Solo se presentan las Features que cumplen el 100% de la DoD.

* **Regla de Hierro:** Si una Feature funciona perfectamente pero falta la documentación (y es parte de la DoD), **no se demuestra**. Se declara como "No Hecha". Esto visibiliza la importancia de la calidad ante los stakeholders. Presentar trabajo incompleto como "terminado" crea una falsa sensación de progreso.33
* **Agenda:** La revisión debe comenzar recordando la DoD vigente para establecer el contexto de calidad de lo que se va a mostrar.40

### **7.4. Sprint Retrospective (Retrospectiva)**

El equipo inspecciona la DoD misma. ¿Fue realista? ¿Hubo algún criterio que causó cuello de botella? ¿Se escapó algún bug que sugiere que necesitamos agregar un nuevo criterio a la DoD? Aquí es donde la DoD evoluciona.25

## **8\. Gestión Técnica en Herramientas (Jira y Automatización)**

Para que la DoD se cumpla, debe estar integrada en las herramientas de trabajo diario. Depender de la memoria humana es una estrategia fallida.

### **8.1. Implementación en Jira**

Existen varias estrategias para materializar la DoD en Jira 31:

1. **Checklist Explícito (Plugin):** Usar apps como "Smart Checklist" que insertan la lista de DoD en cada ticket de tipo Feature. Se puede configurar para que sea obligatorio marcar todos los items antes de transicionar el estado.
2. **Validadores de Workflow:** Configurar el flujo de trabajo de Jira para bloquear la transición a "Done" si ciertos campos no están completos o si el estado del build vinculado (Bitbucket/GitLab) no es "Exitoso".31
3. **Sub-tareas:** Algunos equipos crean sub-tareas automáticas para ítems grandes de la DoD (ej. "Crear Documentación"), aunque esto puede generar ruido en el backlog.

### **8.2. Integración con CI/CD (Automatización)**

La forma más efectiva de "policía" de la DoD es el pipeline de CI/CD.

* **Quality Gates:** Configurar SonarQube u herramientas similares para que el pipeline falle si la cobertura de código es \<80% o si hay vulnerabilidades críticas. Esto hace que el cumplimiento de la DoD técnica sea automático e ineludible.32
* **Despliegue Automático:** Si la DoD requiere despliegue en Staging, el pipeline debe encargarse de esto automáticamente tras el merge, eliminando el paso manual.

## **9\. Gestión de Excepciones y Trabajo No Terminado (Undone Work)**

¿Qué sucede cuando termina el Sprint y una Feature está "casi lista"? Este es uno de los escenarios más comunes y difíciles.

### **9.1. El Principio del Binario (Done vs. Not Done)**

En Scrum, no existe el "99% hecho". Si falta un solo criterio de la DoD, la Feature no está hecha.

* **Manejo del Rollover:** No se debe mover automáticamente la Feature al siguiente sprint. Debe volver al Product Backlog y ser re-priorizada. Esto es doloroso pero necesario para mantener la honestidad empírica de la velocidad del equipo.9
* **Impacto en Métricas:** La Feature cuenta como 0 puntos de velocidad en el sprint actual. Esto fuerza al equipo a dividir el trabajo en trozos más pequeños en el futuro para asegurar la finalización.

### **9.2. Manejo de Excepciones (Emergencia)**

Si el negocio decide imperativamente lanzar una Feature que no cumple toda la DoD (ej. falta documentación menor), esto debe tratarse como una **excepción formal**:

1. **Registro de Deuda:** Se crea inmediatamente un ticket de "Deuda Técnica" en el backlog para completar el faltante.
2. **Transparencia:** Se comunica explícitamente a los stakeholders el riesgo asumido.
3. **Retrospectiva:** Se analiza por qué ocurrió para evitar que la excepción se convierta en la norma.33

## **10\. Escalamiento y Contexto Avanzado (Dual Track, SAFe)**

### **10.1. Dual Track Agile (Discovery vs. Delivery)**

En equipos modernos que practican Dual Track (Descubrimiento y Entrega en paralelo), la DoD aplica principalmente al track de **Delivery**. Sin embargo, el track de **Discovery** puede tener su propia "Definition of Ready" o una "Definition of Done de Experimento" (ej. prototipo validado con 5 usuarios, hipótesis confirmada).42

### **10.2. Escalamiento (SAFe / LeSS)**

En entornos escalados con múltiples equipos trabajando en el mismo producto, la DoD no puede ser única de cada equipo. Debe haber una **DoD Sistémica** o compartida que asegure que el trabajo de todos los equipos se integra correctamente. Un equipo no puede declarar su Feature "Hecha" si rompe el build del tren de lanzamiento (Release Train).8

## **11\. Aspectos Culturales: Acuerdos de Trabajo y Psicología**

Finalmente, la DoD es un artefacto cultural. Su efectividad depende de la seguridad psicológica del equipo.

* **Empoderamiento:** La DoD otorga al equipo la autoridad de decir "No" a la presión de lanzar software de mala calidad. "No podemos lanzarlo porque violaríamos nuestra DoD" es un argumento profesional y objetivo, no una negativa personal.3
* **Cultura de Excelencia:** Una DoD respetada fomenta el orgullo profesional. El equipo sabe que lo que entregan es robusto. Por el contrario, violar constantemente la DoD desmoraliza al equipo y normaliza la mediocridad (la "normalización de la desviación").29

## **12\. Conclusión**

La implementación de una Definition of Done a nivel de Feature es una de las inversiones de mayor retorno que un equipo ágil puede realizar. Transforma la calidad de una variable subjetiva a una constante sistémica. Aunque su implementación inicial puede causar una caída aparente en la velocidad (al revelar el trabajo oculto del "Undone Work"), el resultado a medio plazo es una mayor predictibilidad, menor tasa de defectos y una alineación total entre las expectativas del negocio y la entrega técnica.

Para el líder de producto o ingeniería, el mandato es claro: co-crear la DoD con el equipo, integrarla en las herramientas, automatizar su verificación tanto como sea posible y, sobre todo, tener el coraje de respetarla cuando la presión por entregar aumente. Solo entonces "Hecho" significará verdaderamente "Hecho".

---

*Nota sobre las fuentes: Este informe ha sido elaborado sintetizando las mejores prácticas documentadas en la literatura ágil contemporánea, incluyendo guías de Scrum.org, Atlassian, y metodologías de escalado como SAFe y LeSS, referenciadas a lo largo del texto mediante los identificadores de los fragmentos de investigación proporcionados.*

#### **Obras citadas**

1. Acceptance Criteria vs Definition of Done: How to Keep Agile Teams Aligned \- AltexSoft, fecha de acceso: diciembre 9, 2025, [https://www.altexsoft.com/blog/acceptance-criteria-definition-of-done/](https://www.altexsoft.com/blog/acceptance-criteria-definition-of-done/)
2. 5 Steps to Find Your Definition of Done (With Examples and Workflows) \- Planio, fecha de acceso: diciembre 9, 2025, [https://plan.io/blog/definition-of-done/](https://plan.io/blog/definition-of-done/)
3. Scrum Explicit Contracts: The Definition of Done \- Motion Recruitment, fecha de acceso: diciembre 9, 2025, [https://motionrecruitment.com/blog/scrum-explicit-contracts-the-definition-of-done](https://motionrecruitment.com/blog/scrum-explicit-contracts-the-definition-of-done)
4. The definition of done and acceptance criteria: What's the difference? | Bigger Impact \- Boost, fecha de acceso: diciembre 9, 2025, [https://www.boost.co.nz/blog/2019/04/difference-definition-done-acceptance-criteria](https://www.boost.co.nz/blog/2019/04/difference-definition-done-acceptance-criteria)
5. Definition of done examples and tips | Bigger Impact \- Boost, fecha de acceso: diciembre 9, 2025, [https://www.boost.co.nz/blog/2019/05/definition-of-done-examples-and-tips](https://www.boost.co.nz/blog/2019/05/definition-of-done-examples-and-tips)
6. The Definition of Done \- LiminalArc, fecha de acceso: diciembre 9, 2025, [https://www.leadingagile.com/2017/02/definition-of-done/](https://www.leadingagile.com/2017/02/definition-of-done/)
7. What is the Definition of Done? | Scrum Alliance, fecha de acceso: diciembre 9, 2025, [https://resources.scrumalliance.org/Article/definition-dod](https://resources.scrumalliance.org/Article/definition-dod)
8. Definition of Done \- Large Scale Scrum (LeSS), fecha de acceso: diciembre 9, 2025, [https://less.works/less/framework/definition-of-done](https://less.works/less/framework/definition-of-done)
9. Handling Work Left at the End of an Agile Sprint \- Mountain Goat Software, fecha de acceso: diciembre 9, 2025, [https://www.mountaingoatsoftware.com/blog/handling-work-left-at-the-end-of-a-sprint](https://www.mountaingoatsoftware.com/blog/handling-work-left-at-the-end-of-a-sprint)
10. fecha de acceso: diciembre 9, 2025, [https://monday.com/blog/rnd/agile-epic-vs-feature/\#:\~:text=In%20SAFe%2C%20an%20epic%20is,tasks%20completed%20within%20a%20sprint.](https://monday.com/blog/rnd/agile-epic-vs-feature/#:~:text=In%20SAFe%2C%20an%20epic%20is,tasks%20completed%20within%20a%20sprint.)
11. Epic vs. Feature vs. User Story \- The Key Differences \- Agilemania, fecha de acceso: diciembre 9, 2025, [https://agilemania.com/epic-vs-feature-vs-user-story](https://agilemania.com/epic-vs-feature-vs-user-story)
12. Epics vs Features vs Stories \- Everything You Need To Know \- Visor, fecha de acceso: diciembre 9, 2025, [https://www.visor.us/blog/epics-vs-features-vs-stories/](https://www.visor.us/blog/epics-vs-features-vs-stories/)
13. The Key difference between Epic Vs Feature Vs User Story \- Simpliaxis, fecha de acceso: diciembre 9, 2025, [https://www.simpliaxis.com/resources/epic-vs-feature-vs-user-story](https://www.simpliaxis.com/resources/epic-vs-feature-vs-user-story)
14. What Is the Difference Between a Feature vs. a Story vs. Epics? Definition and Examples, fecha de acceso: diciembre 9, 2025, [https://airfocus.com/glossary/feature-story-epics/](https://airfocus.com/glossary/feature-story-epics/)
15. Epic Vs. Feature Vs. User Story \- Differences \- StarAgile, fecha de acceso: diciembre 9, 2025, [https://staragile.com/blog/epic-vs-feature-vs-user-story](https://staragile.com/blog/epic-vs-feature-vs-user-story)
16. Jira Story vs Task vs Feature: Understanding the Key Differences for Effective Project Planning \- ONES.com, fecha de acceso: diciembre 9, 2025, [https://ones.com/blog/jira-story-vs-task-vs-feature-differences/](https://ones.com/blog/jira-story-vs-task-vs-feature-differences/)
17. Jira Task vs Story: Which One to Choose for Optimal Workflow Management? \- ONES.com, fecha de acceso: diciembre 9, 2025, [https://ones.com/blog/jira-task-vs-story-optimal-workflow-management/](https://ones.com/blog/jira-task-vs-story-optimal-workflow-management/)
18. Ready vs Done: The Underrated Process That Keeps Work Clean \- Maxim Gorin \- Medium, fecha de acceso: diciembre 9, 2025, [https://maxim-gorin.medium.com/tired-of-tasks-starting-half-baked-or-closing-half-done-learn-how-dor-and-dod-keep-your-team-aligne-b912dfdf828c](https://maxim-gorin.medium.com/tired-of-tasks-starting-half-baked-or-closing-half-done-learn-how-dor-and-dod-keep-your-team-aligne-b912dfdf828c)
19. fecha de acceso: diciembre 9, 2025, [https://www.atlassian.com/work-management/project-management/acceptance-criteria\#:\~:text=DoD%20establishes%20a%20broader%20set,a%20team%20completes%20development%20work.](https://www.atlassian.com/work-management/project-management/acceptance-criteria#:~:text=DoD%20establishes%20a%20broader%20set,a%20team%20completes%20development%20work.)
20. What Is the Difference Between the Definition of Done and Acceptance Criteria? \- Scrum.org, fecha de acceso: diciembre 9, 2025, [https://www.scrum.org/resources/blog/what-difference-between-definition-done-and-acceptance-criteria](https://www.scrum.org/resources/blog/what-difference-between-definition-done-and-acceptance-criteria)
21. Definition of Done vs. Acceptance Criteria: A Complete Guide \- Agilemania, fecha de acceso: diciembre 9, 2025, [https://agilemania.com/definition-of-done-vs-acceptance-criteria](https://agilemania.com/definition-of-done-vs-acceptance-criteria)
22. Decoding Agile Concepts: Are Acceptance Criteria and Definition of Done the Same?, fecha de acceso: diciembre 9, 2025, [https://premieragile.com/decoding-agile-concepts-are-acceptance-criteria-and-definition-of-done-the-same/](https://premieragile.com/decoding-agile-concepts-are-acceptance-criteria-and-definition-of-done-the-same/)
23. Definition of Done vs Acceptance Criteria \- Visual Paradigm, fecha de acceso: diciembre 9, 2025, [https://www.visual-paradigm.com/scrum/definition-of-done-vs-acceptance-criteria/](https://www.visual-paradigm.com/scrum/definition-of-done-vs-acceptance-criteria/)
24. Creating Your Own Definition of Done \- Applied Frameworks, fecha de acceso: diciembre 9, 2025, [https://agile.appliedframeworks.com/applied-frameworks-agile-blog/creating-your-own-definition-of-done](https://agile.appliedframeworks.com/applied-frameworks-agile-blog/creating-your-own-definition-of-done)
25. Who Creates the Definition of Done and How to Create One? \- Agilemania, fecha de acceso: diciembre 9, 2025, [https://agilemania.com/who-creates-definition-of-done](https://agilemania.com/who-creates-definition-of-done)
26. What is the Definition of Done (DoD) in Agile? \- Atlassian, fecha de acceso: diciembre 9, 2025, [https://www.atlassian.com/agile/project-management/definition-of-done](https://www.atlassian.com/agile/project-management/definition-of-done)
27. Top 5 Tools and Techniques to Help Define the 'Definition of Done' in Agile Methodology, fecha de acceso: diciembre 9, 2025, [https://i3solutions.com/agile-development/top-5-tools-and-techniques-to-help-define-the-definition-of-done-in-agile-methodology/](https://i3solutions.com/agile-development/top-5-tools-and-techniques-to-help-define-the-definition-of-done-in-agile-methodology/)
28. Creating a Team Working Agreement \- Scrum.org, fecha de acceso: diciembre 9, 2025, [https://www.scrum.org/resources/creating-team-working-agreement](https://www.scrum.org/resources/creating-team-working-agreement)
29. Team Charter, Working Agreement, & Social Contract \- Template and Guide for Product and Engineering Teams | Easy Agile, fecha de acceso: diciembre 9, 2025, [https://www.easyagile.com/blog/team-charter-working-agreement-social-contract-template-guide](https://www.easyagile.com/blog/team-charter-working-agreement-social-contract-template-guide)
30. Team Working Agreement Template | Miroverse, fecha de acceso: diciembre 9, 2025, [https://miro.com/templates/team-working-agreement-template/](https://miro.com/templates/team-working-agreement-template/)
31. Definition of Done in Jira with Examples | TitanApps Blog, fecha de acceso: diciembre 9, 2025, [https://titanapps.io/blog/definition-of-done-in-jira/](https://titanapps.io/blog/definition-of-done-in-jira/)
32. Definition Of Done Checklist For Agile Project Success \- rosemet, fecha de acceso: diciembre 9, 2025, [https://www.rosemet.com/definition-of-done-checklist/](https://www.rosemet.com/definition-of-done-checklist/)
33. Definition of Done: The Complete Guide with Examples & Checklist ..., fecha de acceso: diciembre 9, 2025, [https://teachingagile.com/scrum/psm-1/scrum-implementation/definition-of-done](https://teachingagile.com/scrum/psm-1/scrum-implementation/definition-of-done)
34. The Agile Definition of Done: What Product Managers Need to Know, fecha de acceso: diciembre 9, 2025, [https://www.productplan.com/learn/agile-definition-of-done/](https://www.productplan.com/learn/agile-definition-of-done/)
35. Create an effective Agile definition of done \- Appfire, fecha de acceso: diciembre 9, 2025, [https://appfire.com/resources/blog/definition-of-done-in-agile](https://appfire.com/resources/blog/definition-of-done-in-agile)
36. Your Evolving Definition of Done | naked Agility with Martin Hinshelwood, fecha de acceso: diciembre 9, 2025, [https://nkdagility.com/resources/blog/your-evolving-definition-of-done/](https://nkdagility.com/resources/blog/your-evolving-definition-of-done/)
37. What is the definition of done? Guide for agile teams with examples \- LogRocket Blog, fecha de acceso: diciembre 9, 2025, [https://blog.logrocket.com/product-management/what-is-definition-of-done-agile-examples/](https://blog.logrocket.com/product-management/what-is-definition-of-done-agile-examples/)
38. What is a Sprint Review? \- Scrum.org, fecha de acceso: diciembre 9, 2025, [https://www.scrum.org/resources/what-is-a-sprint-review](https://www.scrum.org/resources/what-is-a-sprint-review)
39. The Sprint Review | Agile Academy, fecha de acceso: diciembre 9, 2025, [https://www.agile-academy.com/en/product-owner/sprint-review-dos-donts/](https://www.agile-academy.com/en/product-owner/sprint-review-dos-donts/)
40. Stop Having Sucky Sprint Reviews: Agenda That Works \- Agile Classrooms, fecha de acceso: diciembre 9, 2025, [https://learn.agileclassrooms.com/blog/sprint-review-agenda](https://learn.agileclassrooms.com/blog/sprint-review-agenda)
41. What do you do with incomplete items at the end of a sprint? : r/scrum \- Reddit, fecha de acceso: diciembre 9, 2025, [https://www.reddit.com/r/scrum/comments/dkitdl/what\_do\_you\_do\_with\_incomplete\_items\_at\_the\_end/](https://www.reddit.com/r/scrum/comments/dkitdl/what_do_you_do_with_incomplete_items_at_the_end/)
42. Dual Track Agile: the secret sauce to outcome-based development | by David Denham, fecha de acceso: diciembre 9, 2025, [https://medium.com/@daviddenham07/dual-track-agile-the-secret-sauce-to-outcome-based-development-601f6003ea73](https://medium.com/@daviddenham07/dual-track-agile-the-secret-sauce-to-outcome-based-development-601f6003ea73)
43. Working Agreements: 10 examples, samples & templates \- Echometer, fecha de acceso: diciembre 9, 2025, [https://echometerapp.com/en/working-agreement-agile-example-sample/](https://echometerapp.com/en/working-agreement-agile-example-sample/)
