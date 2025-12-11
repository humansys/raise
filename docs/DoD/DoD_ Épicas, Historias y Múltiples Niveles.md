# **Arquitectura Estratégica de la Calidad en el Desarrollo Ágil: Implementación Jerárquica de la Definition of Done (DoD) para Épicas e Historias de Usuario**

## **1\. Introducción: La Paradoja de la Finalización en la Ingeniería de Software Moderna**

En el ecosistema contemporáneo del desarrollo de software y la gestión de productos digitales, la noción de "terminado" se ha transformado desde un estado binario simple hacia un concepto multidimensional y estratificado. La pregunta fundamental que enfrentan las organizaciones que buscan escalar sus prácticas ágiles no es simplemente "¿cuándo está listo el código?", sino "¿cuándo se ha realizado el valor?". Esta distinción es crucial para entender la aplicación correcta de la **Definition of Done (DoD)**. La consulta que motiva este informe —sobre la mejor forma de utilizar la DoD a nivel de Épicas frente a Historias de Usuario, y si la coexistencia de múltiples DoDs es un estándar en la industria— toca la fibra sensible de la madurez organizacional. La respuesta corta, respaldada por la literatura más reciente y los marcos de trabajo de escalado como SAFe (Scaled Agile Framework), es que la estratificación de la DoD no solo es estándar, sino indispensable para evitar la acumulación de deuda técnica y garantizar la alineación estratégica.1

La "Definition of Done" actúa como el mecanismo principal de transparencia en Scrum y otras metodologías empíricas. Sin una definición compartida y rigurosa, la inspección y adaptación se vuelven imposibles, ya que los interesados (stakeholders) y los desarrolladores operan bajo suposiciones divergentes sobre el estado real del producto.3 En entornos complejos, donde múltiples equipos contribuyen a un único producto, o donde el trabajo se descompone en jerarquías de Iniciativas, Épicas e Historias, aplicar una única definición monolítica resulta insuficiente. Una Historia de Usuario puede estar perfectamente codificada y probada (micro-calidad), pero la Épica a la que pertenece podría carecer de validación legal, integración de sistemas o material de marketing (macro-calidad), impidiendo su lanzamiento real al mercado.5

Este informe exhaustivo desglosa la arquitectura de la calidad en entornos ágiles, proponiendo un modelo jerárquico para la DoD. Se explorará en profundidad cómo configurar estos criterios para maximizar la entrega de valor, minimizar el riesgo de "Undone Work" (trabajo no hecho) y alinear los esfuerzos técnicos con los objetivos de negocio. A través de un análisis detallado de marcos teóricos, prácticas de ingeniería y dinámicas organizacionales, se demostrará que la gestión de múltiples niveles de "Done" es el sello distintivo de una agilidad empresarial robusta y escalable.

## ---

**2\. Ontología del "Done": Fundamentos Teóricos y Necesidad de Escalado**

Para abordar la implementación práctica, es imperativo primero deconstruir el propósito ontológico de la Definition of Done. En su esencia, la DoD es un acuerdo formal que define la calidad institucional. No es simplemente una lista de comprobación técnica; es una aserción de que no se ha incurrido en deuda técnica involuntaria y de que el incremento producido es utilizable.3

### **2.1 La Transparencia como Imperativo de Gestión de Riesgos**

La transparencia es uno de los pilares del empirismo. En el contexto del desarrollo de productos, la transparencia significa que cuando un miembro del equipo dice que algo está "hecho", todos los demás entienden exactamente qué significa eso en términos de calidad, pruebas y documentación. Si la DoD es débil o ambigua, la transparencia colapsa. Los líderes pueden tomar decisiones de lanzamiento basadas en software que parece funcional en una demostración pero que carece de pruebas de carga o seguridad, introduciendo riesgos existenciales para la organización.1

A nivel de **Historia de Usuario**, la falta de transparencia se manifiesta como errores (bugs) que escapan a QA y ralentizan la velocidad futura. A nivel de **Épica**, la falta de transparencia es más insidiosa: puede resultar en el desarrollo de grandes bloques de funcionalidad que son técnicamente sólidos pero estratégicamente inútiles por falta de alineación con operaciones, ventas o cumplimiento normativo.8

### **2.2 La Evolución hacia Múltiples Niveles de "Done"**

La Guía Scrum original enfatiza una DoD para el Incremento. Sin embargo, a medida que las organizaciones adoptan Agile a escala, la realidad operativa impone una estructura más compleja. Marcos como SAFe, Nexus y Scrum@Scale han normalizado el uso de múltiples definiciones de hecho para abordar diferentes granularidades de trabajo.1

El argumento para estandarizar múltiples DoDs se basa en la distinción entre **Producción (Output)** y **Resultado (Outcome)**.

* **Nivel Historia (Output):** Se centra en la producción correcta de una pieza de software. ¿Cumple con las especificaciones? ¿Está libre de defectos?  
* **Nivel Épica (Outcome):** Se centra en la capacidad de esa colección de software para generar un resultado de negocio. ¿Es vendible? ¿Es operable? ¿Cumple con la regulación?

Ignorar esta distinción lleva al anti-patrón donde los equipos celebran una alta "velocidad" de historias completadas, mientras que el negocio sufre una sequía de lanzamientos reales porque las Épicas nunca alcanzan un estado de despliegue.10 Por lo tanto, establecer DoDs diferenciados es el estándar necesario para cerrar la brecha entre TI y Negocio.

## ---

**3\. Definition of Done a Nivel de Historia de Usuario (User Story)**

La Historia de Usuario es la unidad atómica de entrega en Agile. La DoD a este nivel es la primera línea de defensa contra la entropía del software. Su objetivo primordial es asegurar la **Excelencia Técnica** y la mantenibilidad del código. Si la DoD de la Historia es laxa, ninguna cantidad de gestión a nivel de Épica podrá salvar el producto de la inestabilidad.

### **3.1 Componentes Críticos de la DoD de Historia**

Una DoD robusta para historias de usuario debe trascender la simple funcionalidad. Debe garantizar que el nuevo código sea un ciudadano de primera clase en la base de código existente. Basándonos en las mejores prácticas de ingeniería y los datos analizados 5, los componentes esenciales se dividen en calidad interna y externa.

#### **Excelencia Técnica y Calidad del Código**

La base de la DoD es el código mismo. No es suficiente que el código "funcione"; debe estar bien escrito.

* **Pruebas Unitarias:** La historia no está hecha hasta que las pruebas unitarias estén escritas y pasando. Esto no es negociable. Las pruebas deben cubrir no solo el "camino feliz", sino también casos de borde y manejo de errores. La cobertura de código (code coverage) a menudo se estipula aquí (ej. mínimo 80%), aunque la calidad de la aserción es más importante que el porcentaje bruto.5  
* **Revisión de Código (Peer Review):** El código debe ser revisado por al menos otro ingeniero. Esta práctica no solo detecta errores lógicos que las máquinas no ven, sino que es vital para la propiedad colectiva del código y la difusión del conocimiento dentro del equipo. Una historia con código "privado" o no revisado es un riesgo de bus factor.12  
* **Análisis Estático y Estándares:** El código debe cumplir con las guías de estilo del equipo (linting) y pasar análisis estáticos de seguridad (SAST) sin vulnerabilidades críticas. Esto automatiza la burocracia de la calidad.15

#### **Validación Funcional y QA**

* **Criterios de Aceptación (AC) Cumplidos:** Mientras que la DoD es genérica, la validación funcional es específica. La historia debe cumplir rigurosamente con los AC definidos durante el refinamiento.  
* **Pruebas en Entorno de Desarrollo/QA:** La funcionalidad debe ser verificable en un entorno compartido, no solo en la máquina del desarrollador ("works on my machine" no es aceptable).  
* **Ausencia de Defectos Conocidos:** No se debe cerrar una historia si se han identificado bugs durante el sprint asociados a ella. La filosofía es "Zero Bugs" al cierre de la historia.14

#### **Documentación y Mantenibilidad**

* **Documentación Técnica:** Si la historia implicó cambios en la arquitectura, APIs o modelos de datos, la documentación técnica (ej. Swagger, diagramas en Confluence) debe actualizarse.  
* **Refactorización:** La DoD debe incluir tiempo para refactorizar el código tocado, dejando el campamento más limpio de lo que se encontró ("Boy Scout Rule").12

### **3.2 Tabla de Referencia: Checklist de DoD para Historias de Usuario**

La siguiente tabla resume un estándar de industria para la DoD a nivel de Historia, diseñado para ser implementado en herramientas como Jira o Azure DevOps.

| Categoría | Ítem de Verificación (Checklist) | Razón de Ser (Why) |
| :---- | :---- | :---- |
| **Construcción** | Código commiteado en rama correcta y compilación (Build) exitosa. | Asegura la integración continua y evita romper el repositorio compartido. |
| **Calidad Código** | Pruebas Unitarias ejecutadas y pasando (Cobertura \> X%). | Garantiza que la lógica interna es sólida y protege contra regresiones futuras. |
| **Calidad Código** | Code Review completado y aprobado por pares. | Mantiene estándares de ingeniería, seguridad y comparte conocimiento. |
| **Funcionalidad** | Criterios de Aceptación (AC) verificados por QA/Tester. | Confirma que se construyó lo que el Product Owner pidió. |
| **Integridad** | Análisis estático de código (SonarQube) sin alertas críticas. | Previene deuda técnica invisible y vulnerabilidades de seguridad básicas. |
| **Aceptación** | Demostración al Product Owner (PO) y aprobación. | Validación final de negocio antes de considerar el trabajo terminado. |

### **3.3 El Rol de la Automatización en la DoD de Historia**

Para que la DoD de Historia sea efectiva y no un cuello de botella administrativo, debe automatizarse tanto como sea posible dentro del pipeline de CI/CD (Integración Continua / Despliegue Continuo). Herramientas modernas pueden bloquear la fusión (merge) de código si no se cumplen ciertos criterios de la DoD, como la aprobación de la revisión de código o el paso de las pruebas unitarias. Esto convierte a la DoD en una "Quality Gate" automatizada, liberando al equipo de verificaciones manuales tediosas y permitiéndoles enfocarse en la resolución de problemas complejos.15

## ---

**4\. Definition of Done a Nivel de Épica (Epic/Feature)**

Si la Historia de Usuario se trata de construir la cosa *correctamente* (build the thing right), la Épica se trata de construir la *cosa correcta* y asegurar que sea viable para el negocio (build the right thing). La Épica suele representar un incremento de valor significativo, como una nueva característica comercializable o una mejora sustancial de la infraestructura.8

### **4.1 La Falacia de la Suma de las Partes**

Un error común en organizaciones inmaduras es asumir que una Épica está "Hecha" en el instante en que se cierra la última Historia de Usuario asociada.8 Esta visión mecanicista ignora la complejidad de la integración y los requisitos del mundo real.

* **Integración de Sistemas:** Diez historias pueden funcionar perfectamente de forma aislada (mockeando dependencias), pero fallar catastróficamente cuando se integran. La DoD de Épica debe exigir pruebas de integración end-to-end.5  
* **Coherencia de la Experiencia de Usuario (UX):** Las historias individuales pueden cumplir sus ACs, pero la Épica completa puede tener un flujo de usuario fragmentado o inconsistente. La DoD de Épica requiere una revisión holística de UX/UI.  
* **Requisitos No Funcionales (NFRs):** El rendimiento, la escalabilidad y la seguridad a menudo son propiedades emergentes del sistema completo, no de historias individuales. Una Épica no está hecha hasta que se valida que el sistema bajo carga soporta la nueva funcionalidad.18

### **4.2 Componentes Esenciales de la DoD de Épica**

La DoD a este nivel actúa como una compuerta de lanzamiento (Release Gate). Involucra a actores fuera del equipo de desarrollo inmediato, como Operaciones, Legal, Marketing y Ventas.

#### **Validación de Integración y Sistema**

* **Pruebas de Regresión Completas:** Se debe verificar que la nueva Épica no ha roto funcionalidades antiguas. Esto suele implicar la ejecución de suites de regresión automatizadas extensas que son demasiado costosas para correr por cada historia individual.5  
* **Pruebas de Rendimiento y Seguridad:** Escaneos de vulnerabilidades profundos (DAST), pruebas de penetración y pruebas de carga para asegurar que la infraestructura soporta la nueva característica.6  
* **Integración End-to-End (E2E):** Validación de flujos completos a través de todos los sistemas integrados (ej. desde el front-end web hasta el backend de SAP y el sistema de facturación).

#### **Habilitación Operativa y de Negocio**

* **Cumplimiento Legal y Normativo:** Verificación de que la funcionalidad cumple con leyes como GDPR, CCPA o regulaciones específicas de la industria (ej. HIPAA en salud). Esto es crítico para evitar riesgos legales masivos.20  
* **Material de Soporte y Usuario:** Actualización de la base de conocimiento de soporte, manuales de usuario, y guías de ayuda. El equipo de soporte al cliente debe estar capacitado *antes* del lanzamiento.5  
* **Preparación de Go-to-Market:** Notas de lanzamiento (Release Notes), documentación de APIs pública, y activos de marketing listos. La funcionalidad no sirve si nadie sabe que existe o cómo venderla.6

### **4.3 Tabla de Referencia: Checklist de DoD para Épicas**

Esta tabla proporciona una guía para Product Managers y Release Managers sobre qué verificar antes de marcar una Épica como concluida.

| Dominio | Ítem de Verificación (Checklist) | Impacto de Negocio |
| :---- | :---- | :---- |
| **Integridad del Sistema** | Todas las historias hijas en estado "Done". | Prerrequisito básico de completitud funcional. |
| **Calidad Global** | Pruebas de Regresión y E2E pasadas en entorno de Staging. | Protege la estabilidad del producto existente y la experiencia del usuario. |
| **NFRs** | Pruebas de Carga y Rendimiento dentro de umbrales (SLAs). | Asegura que el sistema no colapsará bajo el uso real de la nueva feature. |
| **Seguridad/Legal** | Auditoría de seguridad y revisión de cumplimiento (Legal/Compliance) aprobadas. | Mitiga riesgos legales, multas y daños a la reputación de marca. |
| **Operaciones** | Plan de despliegue, scripts de rollback y monitoreo configurados. | Garantiza un lanzamiento seguro y capacidad de respuesta ante incidentes. |
| **Usuario/Mercado** | Documentación de usuario, Release Notes y entrenamiento de soporte completados. | Maximiza la adopción del usuario y reduce la carga inicial sobre soporte técnico. |
| **Validación** | Demo de la solución completa aceptada por Stakeholders clave. | Confirmación final de que se ha entregado el valor esperado. |

## ---

**5\. El Estándar de la Industria: Múltiples DoDs en Marcos Escalados (SAFe, LeSS, Nexus)**

Respondiendo directamente a la consulta sobre si es estándar tener más de un DoD: **Sí, es el estándar predominante en entornos empresariales escalados.** La complejidad de los sistemas modernos hace imposible capturar todas las dimensiones de calidad en una sola lista plana aplicada al final de un sprint de dos semanas.9

### **5.1 El Modelo de Scaled Agile Framework (SAFe)**

SAFe es quizás el marco más explícito en esta estratificación, definiendo claramente distintos niveles de DoD que corresponden a su jerarquía de trabajo (Team, Program, Solution).1

* **Team DoD (Nivel Historia):** Enfocado en la calidad del código, pruebas unitarias y aceptación local. Es responsabilidad del equipo ágil.  
* **System DoD (Nivel Feature/Épica):** Enfocado en la integración continua a nivel de tren (Agile Release Train \- ART). Aquí es donde se valida que las historias de múltiples equipos funcionan juntas. Incluye la aceptación en la "System Demo".  
* **Solution DoD (Nivel Capability):** Para sistemas grandes y ciberfísicos, esto incluye validaciones de cumplimiento regulatorio, pruebas en hardware real y validaciones de proveedores externos.

Esta estructura permite que los equipos mantengan la velocidad (velocity) en sus historias mientras el tren (ART) asegura la coherencia del sistema.

### **5.2 Comparativa con LeSS y Nexus**

Otros marcos como LeSS (Large-Scale Scrum) y Nexus adoptan un enfoque ligeramente diferente pero compatible filosóficamente.

* **LeSS** aboga por una "DoD Perfecta". Reconocen que a menudo hay una brecha entre lo que el equipo puede hacer en un sprint ("Done" actual) y lo que se necesita para enviar el producto ("Potentially Shippable"). A este delta lo llaman "Undone Work". El objetivo en LeSS es expandir continuamente la DoD del equipo para reducir el "Undone Work" a cero, eliminando la necesidad de departamentos separados de pruebas o integración.4  
* **Nexus** requiere una "DoD Integrada". Dado que múltiples equipos trabajan en un solo backlog, la DoD debe centrarse en el incremento integrado. No importa si la historia del Equipo A está bien; si rompe la compilación del Equipo B, no está "Done".23

### **5.3 Tabla Comparativa de Enfoques de DoD en Marcos Ágiles**

| Marco de Trabajo | Enfoque de DoD | Manejo de Épicas/Features | Filosofía Subyacente |
| :---- | :---- | :---- | :---- |
| **Scrum (Puro)** | Una única DoD para el Incremento. | No prescribe explícitamente sobre Épicas, foco en el Incremento de Sprint. | Simplicidad y transparencia radical; evita esconder "Undone Work". |
| **SAFe** | Jerárquico: Team DoD, System DoD, Solution DoD. | DoD explícita a nivel de Sistema para Features/Épicas. | Calidad construida a escala; reconoce la especialización y capas de integración. |
| **LeSS** | Una DoD compartida para todos los equipos. | Minimiza la jerarquía; enfoca en reducir la brecha entre "Dev Done" y "Shippable". | Desescalado organizacional; todo el equipo es responsable del producto entero. |
| **Nexus** | DoD del Incremento Integrado. | Prioriza la integración continua sobre la finalización individual de tareas. | La integración es el riesgo principal en el escalado. |

## ---

**6\. Distinciones Conceptuales Clave: DoD vs. Criterios de Aceptación vs. Definition of Ready**

Para implementar esto correctamente, es vital desambiguar términos que a menudo se confunden, llevando a fricciones en los equipos.25

### **6.1 DoD vs. Criterios de Aceptación (AC)**

Esta es la confusión más frecuente.

* **La DoD es Universal:** Aplica a *todas* las Historias de Usuario (o Épicas). Es un estándar de calidad. Ej: "Todo código debe tener 80% de cobertura de pruebas".  
* **Los AC son Específicos:** Aplican a *una* Historia de Usuario específica. Definen el alcance funcional. Ej: "El usuario debe poder pagar con tarjeta Visa".  
* **Relación:** Una historia no está terminada hasta que cumple *ambos*. La DoD asegura que está bien construida (calidad); los AC aseguran que hace lo que debe (funcionalidad).

### **6.2 DoD vs. Definition of Ready (DoR)**

Mientras que la DoD es la compuerta de salida, la DoR es la compuerta de entrada.

* **DoR de Épica:** Una Épica no debe entrar en un Sprint de planificación (PI Planning en SAFe) si no cumple con la DoR: tener un caso de negocio, análisis de arquitectura preliminar y criterios de éxito definidos.  
* **Riesgo:** Una DoR demasiado estricta puede convertirse en un proceso de fase-puerta (Stage-Gate) encubierto, reintroduciendo el modelo de cascada (Waterfall). Se debe usar con precaución para asegurar fluidez, no para bloquear el trabajo.3

## ---

**7\. Estrategias de Implementación Técnica y Operativa**

La teoría debe traducirse en configuración de herramientas y rituales de equipo. A continuación, se detallan estrategias para implementar DoDs jerárquicas utilizando herramientas comunes como Jira.

### **7.1 Configuración en Jira: Automatización y Validadores**

Para **Historias de Usuario**, la DoD no debe ser un documento en una wiki que nadie lee. Debe estar integrada en el flujo de trabajo.

* **Checklists Interactivas:** Utilizar plugins (como "Issue Checklist" o "Definition of Done") para insertar una lista de verificación obligatoria en cada ticket de Jira.  
* **Validadores de Transición:** Configurar el workflow de Jira para que no permita mover una historia a la columna "Done" a menos que:  
  * El campo "Code Review" esté marcado.  
  * Haya un enlace a una Pull Request fusionada.  
  * No haya sub-tareas abiertas.  
  * El estado de la build en el CI/CD (ej. Jenkins/GitLab) sea "Success".16

Para **Épicas**, la automatización debe ser asistida, no ciega.

* **No cierre automático puro:** Aunque existen scripts para cerrar una Épica cuando se cierran sus historias hijas 17, esto es peligroso porque omite la validación de la DoD de Épica (NFRs, Legal, etc.).  
* **Flujo Recomendado:** Cuando todas las historias se cierran, una automatización debe mover la Épica a un estado "Pending Release" o "Validating". Esto notifica al Product Owner o Release Manager para que ejecute la checklist de la DoD de Épica antes de cerrarla manualmente.30

### **7.2 Visualización en Tableros**

La transparencia se logra visualizando el proceso.

* **Tablero de Equipo:** Columnas claras para desarrollo, revisión y pruebas. La columna "Done" debe tener explícitamente escrita la DoD en el encabezado del tablero (físico o digital) como recordatorio constante.31  
* **Tablero de Programa/Portafolio:** Un tablero Kanban para Épicas que visualice el flujo de valor más amplio. Columnas como "Implementing", "Validating" (donde ocurre la DoD de Épica) y "Done" ayudan a los stakeholders a ver qué iniciativas están realmente listas para el mercado versus cuáles están solo "codificadas".32

### **7.3 Gestión de "Undone Work"**

Si un equipo no puede cumplir con algún elemento de la DoD (ej. pruebas de carga) dentro del sprint, esto no debe ignorarse.

* **Excepción Explícita:** Se debe crear un ticket de "Deuda Técnica" o "Trabajo Restante" vinculado a la Épica. La Épica no puede pasar su DoD hasta que estos tickets se resuelvan.  
* **Transparencia Radical:** Marcar el ítem como "Done" sabiendo que falta algo es mentir al sistema. Es preferible declarar el sprint fallido o reducir el alcance que degradar la definición de "Done".11

## ---

**8\. Impacto Cultural y Organizacional**

La implementación de múltiples DoDs no es solo un cambio técnico; es un cambio cultural profundo. Afecta cómo los equipos perciben su responsabilidad y cómo el negocio percibe el progreso.

### **8.1 De "Control de Calidad" a "Calidad Integrada"**

Tradicionalmente, la calidad era responsabilidad de un departamento de QA separado al final del ciclo. La DoD a nivel de historia fuerza el concepto de **Built-in Quality** (Calidad Integrada). Los desarrolladores se vuelven responsables de la calidad porque no pueden mover su trabajo a "Done" sin pruebas. Esto puede causar resistencia inicial ya que la "velocidad" aparente bajará, pero la velocidad real (entrega de valor sin retrabajo) aumentará.1

### **8.2 Negociación y Acuerdo**

La DoD no debe ser impuesta por la gerencia. Debe ser un acuerdo colaborativo.

* **Nivel Historia:** El equipo de desarrollo define su DoD basándose en su madurez técnica, con input del Product Owner.  
* **Nivel Épica:** Product Management, Arquitectura y Stakeholders definen la DoD de Épica para asegurar que se cumplan los objetivos de negocio.  
* **Fricción Saludable:** Es normal que haya tensión. El equipo puede querer una DoD menos estricta para ir más rápido; el negocio puede querer más controles. La DoD es el tratado de paz que equilibra estas fuerzas.1

### **8.3 El Costo de la Calidad**

Adoptar una DoD rigurosa a nivel de Épica hará visible el verdadero costo de lanzar software. Actividades como "Revisión Legal" o "Actualización de Manuales", que antes eran invisibles o se hacían con prisa al final, ahora son requisitos explícitos. Esto permite a la organización planificar mejor y asignar recursos adecuados a estas tareas no-codificadas.10

## ---

**9\. Escenarios y Casos de Estudio**

Para ilustrar la aplicación práctica, consideremos dos escenarios comunes.

### **Escenario A: La Trampa del "Water-Scrum-Fall"**

Una organización financiera tiene equipos Scrum que completan historias cada dos semanas. Tienen una DoD de Historia que incluye pruebas unitarias. Sin embargo, no tienen DoD de Épica.

* **Resultado:** Los equipos "terminan" sus historias. Seis meses después, intentan integrar todo para un lanzamiento mayor. Descubren problemas masivos de rendimiento y el departamento legal rechaza el flujo de datos de usuarios. El lanzamiento se retrasa 3 meses.  
* **Diagnóstico:** Aunque tenían agilidad a nivel micro (Historia), operaban en cascada a nivel macro. Una DoD de Épica habría forzado validaciones legales y de rendimiento incrementales.

### **Escenario B: Organización DevOps Madura**

Una empresa de SaaS utiliza SAFe.

* **Práctica:** Tienen una DoD de Equipo automatizada en su pipeline. Tienen una DoD de Sistema que exige que cada Feature nueva se despliegue automáticamente en un entorno de "Staging" y pase pruebas de regresión visuales.  
* **Resultado:** Las Épicas se consideran "Done" solo cuando están activas en producción tras un despliegue progresivo (Canary Release) y las métricas de negocio confirman la adopción.  
* **Diagnóstico:** La DoD jerárquica permite fluidez. La calidad técnica está automatizada a nivel bajo, permitiendo que la gestión de nivel alto se enfoque en métricas de éxito del producto real.

## ---

**10\. Conclusiones y Recomendaciones Ejecutivas**

La respuesta a la necesidad de saber la mejor forma de usar la DoD a nivel de Épicas e Historias es inequívoca: **se debe adoptar un modelo jerárquico y anidado de calidad.** La estandarización de múltiples DoDs no es una burocracia innecesaria, sino la estructura de soporte necesaria para escalar la agilidad sin sacrificar la estabilidad.

### **Recomendaciones Clave para la Implementación**

1. **Formalice la Distinción:** Cree dos artefactos separados y visibles: "DoD de Equipo" (Técnico/Micro) y "DoD de Épica/Programa" (Negocio/Macro). No intente mezclar todo en una sola lista gigante.  
2. **Automatice la Base:** Invierta fuertemente en automatizar la DoD de Historia (Unit Tests, Linting, SonarQube). Si es manual, será ignorada bajo presión.  
3. **No Automatice el Juicio de Valor:** Mantenga la verificación humana para la DoD de Épica. La decisión de si una funcionalidad es "vendible" o "legal" requiere juicio, no solo un script.  
4. **Integre NFRs en la Épica:** Asegúrese de que la DoD de Épica incluya explícitamente requisitos no funcionales como seguridad, rendimiento y cumplimiento. Estos son los asesinos silenciosos de los lanzamientos.  
5. **Cultura de "Stop the Line":** Empodere a los equipos para detener el trabajo en nuevas funcionalidades si no pueden cumplir la DoD actual. Es preferible reducir el alcance que reducir la calidad (la definición de "Done").  
6. **Revisión Periódica:** Programe revisiones trimestrales de las DoDs. A medida que el equipo madura y la automatización mejora, la DoD debe volverse más estricta ("Raise the bar"), no más laja.

En última instancia, la Definition of Done es la única medida real de progreso en un proyecto ágil. Un producto con el 100% de las historias "codificadas" pero con una DoD de Épica incompleta está, en términos reales de negocio, 0% hecho. Implementar esta jerarquía es el paso crítico para alinear la ilusión del progreso con la realidad de la entrega de valor.

#### **Obras citadas**

1. What is the Definition of Done (DoD) in Agile? \- Atlassian, fecha de acceso: diciembre 11, 2025, [https://www.atlassian.com/agile/project-management/definition-of-done](https://www.atlassian.com/agile/project-management/definition-of-done)  
2. The SAFe Hierarchy and Levels, Explained in Depth \- Enov8, fecha de acceso: diciembre 11, 2025, [https://www.enov8.com/blog/the-hierarchy-of-safe-scaled-agile-framework-explained/](https://www.enov8.com/blog/the-hierarchy-of-safe-scaled-agile-framework-explained/)  
3. The Definition of Done in Scrum | Agile Academy, fecha de acceso: diciembre 11, 2025, [https://www.agile-academy.com/en/scrum-master/what-is-the-definition-of-done-dod-in-agile/](https://www.agile-academy.com/en/scrum-master/what-is-the-definition-of-done-dod-in-agile/)  
4. The 2020 Scrum Guide TM, fecha de acceso: diciembre 11, 2025, [https://scrumguides.org/scrum-guide.html](https://scrumguides.org/scrum-guide.html)  
5. What is the definition of done? Guide for agile teams with examples \- LogRocket Blog, fecha de acceso: diciembre 11, 2025, [https://blog.logrocket.com/product-management/what-is-definition-of-done-agile-examples/](https://blog.logrocket.com/product-management/what-is-definition-of-done-agile-examples/)  
6. The Definition of Done \- LiminalArc, fecha de acceso: diciembre 11, 2025, [https://www.leadingagile.com/2017/02/definition-of-done/](https://www.leadingagile.com/2017/02/definition-of-done/)  
7. Definition of 'Done': What It Is and How It Supports Scrum Events | by Lavaneesh Gautam \- Your Value Coach | Agile Insider | Medium, fecha de acceso: diciembre 11, 2025, [https://medium.com/agileinsider/definition-of-done-what-it-is-and-how-it-supports-scrum-events-6868d9d38a44](https://medium.com/agileinsider/definition-of-done-what-it-is-and-how-it-supports-scrum-events-6868d9d38a44)  
8. Epics, Stories, and Initiatives | Atlassian, fecha de acceso: diciembre 11, 2025, [https://www.atlassian.com/agile/project-management/epics-stories-themes](https://www.atlassian.com/agile/project-management/epics-stories-themes)  
9. What is the Definition of Done (DOD) in SAFe (Scaled Agile Framework)?, fecha de acceso: diciembre 11, 2025, [https://agilemania.com/definition-of-done-in-safe](https://agilemania.com/definition-of-done-in-safe)  
10. How many Definitions of Done does Scrum need?, fecha de acceso: diciembre 11, 2025, [https://www.scrum.org/forum/scrum-forum/97420/how-many-definitions-done-does-scrum-need](https://www.scrum.org/forum/scrum-forum/97420/how-many-definitions-done-does-scrum-need)  
11. Not Done, not Scrum\! Why you can't create value and manage risks without Done Increments., fecha de acceso: diciembre 11, 2025, [https://www.scrum.org/resources/blog/not-done-not-scrum-why-you-cant-create-value-and-manage-risks-without-done](https://www.scrum.org/resources/blog/not-done-not-scrum-why-you-cant-create-value-and-manage-risks-without-done)  
12. Definition of Done \- Checklist for User Story and for Sprint \- Brainhub, fecha de acceso: diciembre 11, 2025, [https://brainhub.eu/library/definition-of-done-user-story-checklist](https://brainhub.eu/library/definition-of-done-user-story-checklist)  
13. The Agile Definition of Done: What Product Managers Need to Know \- ProductPlan, fecha de acceso: diciembre 11, 2025, [https://www.productplan.com/learn/agile-definition-of-done/](https://www.productplan.com/learn/agile-definition-of-done/)  
14. Definition of Done vs. User Stories vs. Acceptance Criteria \- Agile Pain Relief, fecha de acceso: diciembre 11, 2025, [https://agilepainrelief.com/blog/definition-of-done-user-stories-acceptance-criteria/](https://agilepainrelief.com/blog/definition-of-done-user-stories-acceptance-criteria/)  
15. 10 Practical Definition of Done Examples to Enhance Your Agile Process \- ONES.com, fecha de acceso: diciembre 11, 2025, [https://ones.com/blog/10-practical-definition-of-done-examples-agile-process/](https://ones.com/blog/10-practical-definition-of-done-examples-agile-process/)  
16. Agile epics: definition, examples, and templates \- Atlassian, fecha de acceso: diciembre 11, 2025, [https://www.atlassian.com/agile/project-management/epics](https://www.atlassian.com/agile/project-management/epics)  
17. Automation for Jira \- How to automatically close an Epic once all its child issues are closed, fecha de acceso: diciembre 11, 2025, [https://support.atlassian.com/automation/kb/how-to-automatically-close-an-epic-once-all-its-child-issues-are-closed/](https://support.atlassian.com/automation/kb/how-to-automatically-close-an-epic-once-all-its-child-issues-are-closed/)  
18. non-functional requirements | Scrum.org, fecha de acceso: diciembre 11, 2025, [https://www.scrum.org/forum/scrum-forum/7314/non-functional-requirements](https://www.scrum.org/forum/scrum-forum/7314/non-functional-requirements)  
19. What are Non-Functional Requirements in SAFe? Definition, Approach, Effects, fecha de acceso: diciembre 11, 2025, [https://premieragile.com/what-are-safe-non-functional-requirements/](https://premieragile.com/what-are-safe-non-functional-requirements/)  
20. Definition of Done \- DoD \- The Ultimate Guide For Leaders \- ADAPT Methodology, fecha de acceso: diciembre 11, 2025, [https://adaptmethodology.com/blog/definition-of-done-checklist/](https://adaptmethodology.com/blog/definition-of-done-checklist/)  
21. 6 Powerful Definition of Done Examples for 2025 \- resolution Atlassian Apps, fecha de acceso: diciembre 11, 2025, [https://www.resolution.de/post/definition-of-done-examples/](https://www.resolution.de/post/definition-of-done-examples/)  
22. Multiple Levels of “Done” in Scrum \- Mountain Goat Software, fecha de acceso: diciembre 11, 2025, [https://www.mountaingoatsoftware.com/blog/multiple-levels-of-done](https://www.mountaingoatsoftware.com/blog/multiple-levels-of-done)  
23. A definition of "Done" in case of several Development Teams working on a same product, fecha de acceso: diciembre 11, 2025, [https://softwareengineering.stackexchange.com/questions/382441/a-definition-of-done-in-case-of-several-development-teams-working-on-a-same-pr](https://softwareengineering.stackexchange.com/questions/382441/a-definition-of-done-in-case-of-several-development-teams-working-on-a-same-pr)  
24. Definition of 'Done': Dysfunctions & Tips \- Scrum.org, fecha de acceso: diciembre 11, 2025, [https://www.scrum.org/resources/blog/definition-done-dysfunctions-tips](https://www.scrum.org/resources/blog/definition-done-dysfunctions-tips)  
25. Definition of Done vs. Acceptance Criteria: A Complete Guide \- Agilemania, fecha de acceso: diciembre 11, 2025, [https://agilemania.com/definition-of-done-vs-acceptance-criteria](https://agilemania.com/definition-of-done-vs-acceptance-criteria)  
26. Definition of Done vs. Acceptance Criteria: A complete guide \- Nulab, fecha de acceso: diciembre 11, 2025, [https://nulab.com/learn/software-development/definition-of-done-vs-acceptance-criteria/](https://nulab.com/learn/software-development/definition-of-done-vs-acceptance-criteria/)  
27. Definition of Done vs Acceptance Criteria \- Visual Paradigm, fecha de acceso: diciembre 11, 2025, [https://www.visual-paradigm.com/scrum/definition-of-done-vs-acceptance-criteria/](https://www.visual-paradigm.com/scrum/definition-of-done-vs-acceptance-criteria/)  
28. Definition of Done and Definition of Ready with Examples \- Program Strategy HQ, fecha de acceso: diciembre 11, 2025, [https://www.programstrategyhq.com/post/dor-and-dod-checklists](https://www.programstrategyhq.com/post/dor-and-dod-checklists)  
29. Close an Epic when all the Issues Under that Epic are Closed \- ScriptRunner, fecha de acceso: diciembre 11, 2025, [https://www.scriptrunnerhq.com/help/example-scripts/transition-epic-when-children-closed-onPrem](https://www.scriptrunnerhq.com/help/example-scripts/transition-epic-when-children-closed-onPrem)  
30. How do you prevent an Epic from closing until all Stories are closed? \- Atlassian Community, fecha de acceso: diciembre 11, 2025, [https://community.atlassian.com/forums/Jira-questions/How-do-you-prevent-an-Epic-from-closing-until-all-Stories-are/qaq-p/2448052](https://community.atlassian.com/forums/Jira-questions/How-do-you-prevent-an-Epic-from-closing-until-all-Stories-are/qaq-p/2448052)  
31. The Importance of Sharing the Same 'Definition of Done' | by Sevil Topal \- Medium, fecha de acceso: diciembre 11, 2025, [https://seviltopal.medium.com/the-importance-of-sharing-the-same-definition-of-done-bd9e5874fef](https://seviltopal.medium.com/the-importance-of-sharing-the-same-definition-of-done-bd9e5874fef)  
32. Agile epics: complete guide for 2026 \- Monday.com, fecha de acceso: diciembre 11, 2025, [https://monday.com/blog/rnd/agile-epics/](https://monday.com/blog/rnd/agile-epics/)  
33. Scaled Agile Framework (SAFe) Values & Principles \- Atlassian, fecha de acceso: diciembre 11, 2025, [https://www.atlassian.com/agile/agile-at-scale/what-is-safe](https://www.atlassian.com/agile/agile-at-scale/what-is-safe)