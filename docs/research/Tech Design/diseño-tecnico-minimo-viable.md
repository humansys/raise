
El Proceso del Arquitecto Excepcional: Un Framework Metódico para el Diseño Técnico en Sistemas Brownfield


Resumen Ejecutivo

Este informe responde a la pregunta de investigación sobre el proceso de diseño técnico óptimo para introducir nuevas características en repositorios de software existentes (brownfield). La "mejor práctica" moderna no es un único "framework" estático, sino un proceso dinámico centrado en la Arquitectura Evolutiva.1 Este paradigma acepta el cambio como una constante y se aleja del diseño predictivo.1
El proceso óptimo que ejecutan los diseñadores excepcionales es un ciclo de retroalimentación continuo que consta de cinco fases:
Fase 1: Interrogación (El "Por Qué"): Deconstruir el requisito del producto para definir el problema real 3, separándolo de la solución propuesta.5
Fase 2: Análisis (El "Dónde"): Evaluar el impacto del cambio mediante un análisis profundo del repositorio, yendo más allá del análisis estático 6 para incluir el Análisis de Acoplamiento de Cambio (Change Coupling Analysis) 7 y la visualización de dependencias.9
Fase 3: Armonización (El "Cuándo"): Tomar la decisión económica central de refactorizar (armonizar) o no, utilizando la heurística "Tidy First?" de Kent Beck 10, que equilibra los principios de DRY 12 y YAGNI.13
Fase 4: Implementación (El "Cómo"): Ejecutar el cambio utilizando los principios de Mínima Arquitectura Viable (MVA) 14 y Mínimo Cambio Viable (MVC) 15, favoreciendo la refactorización incremental sobre la reescritura.16
Fase 5: Gobernanza (La "Garantía"): "Asegurar" la armonía futura mediante la gobernanza automatizada. Esto incluye Funciones de Aptitud Arquitectónica 17 como ArchUnit 19 para la coerción de patrones internos, y Pruebas de Contrato (Pact) 20 para proteger las fronteras externas entre servicios (aplicado al stack Svelte/Python/Laravel).
El entregable final de este proceso es una Documentación Mínima Viable (MVD) 22, cuyo artefacto principal es el Registro de Decisiones de Arquitectura (ADR) 23, que captura el "por qué" de la decisión para la evolución futura del sistema.

Parte 1: El Framework Conceptual: Del Eslógan al Diseño Evolutivo


1.1. Fundamentos: Reinterpretando KISS, DRY, YAGNI para Sistemas Brownfield

El desafío central de la consulta se sitúa en el desarrollo brownfield, definido como la necesidad de desarrollar y desplegar nuevos sistemas de software en la presencia inmediata de aplicaciones de software (legadas) existentes.25 A diferencia de los proyectos greenfield (hoja en blanco) 27, el trabajo brownfield no es de creación pura, sino de integración, coexistencia y evolución.16
Los principios de diseño ágil como KISS (Keep It Simple, Stupid), DRY (Don't Repeat Yourself) y YAGNI (You Aren't Gonna Need It) son fundamentales para gestionar esta complejidad.13 KISS aboga por la solución más sencilla.29 YAGNI advierte contra la implementación de características "que creemos que podríamos necesitar en el futuro", enfocándose en el valor inmediato.13 DRY promueve la modularización para evitar la redundancia.30
Sin embargo, la "mejor práctica" no consiste en aplicar estos principios dogmáticamente, sino en saber equilibrarlos.29 Específicamente, en un sistema brownfield, los principios de DRY y YAGNI entran en una tensión económica directa. Si un desarrollador observa dos piezas de lógica "similares" y las refactoriza en una abstracción común para satisfacer DRY, pero esa abstracción nunca se vuelve a usar o diverge en el futuro, ha violado YAGNI al construir una "generalización innecesaria". Inversamente, si aplica YAGNI de forma estricta y se niega a abstraer, terminará con lógica duplicada y violará DRY. El trabajo del diseñador excepcional no es seguir estos principios, sino arbitrar la tensión entre ellos.
Una reinterpretación de alto nivel de DRY es crucial aquí. La definición común se centra en la duplicación de código.30 Sin embargo, una definición más poderosa y relevante es: "DRY no se trata de la duplicación de código, sino de la duplicación de conocimiento".12 La definición canónica establece: "Cada pieza de conocimiento debe tener una representación única, inequívoca y autorizada dentro de un sistema".12
Esto es fundamental para el ejemplo del usuario (Laravel y Python). El "conocimiento" de "qué es un cliente" o "cuáles son las reglas de permiso" probablemente existe en ambos sistemas. Un desarrollador estándar no vería una violación de DRY porque el código (PHP en Laravel, Python en el backend de RAG) no está copiado. Un diseñador excepcional sí ve esto como una violación crítica de DRY. El conocimiento está duplicado y puede (y lo hará) desincronizarse. Esta perspectiva redefine el análisis del repositorio: el objetivo no es buscar código duplicado, sino conocimiento duplicado, cuya solución suele ser arquitectónica (p.ej., un servicio de autoridad único o una base de datos compartida).31

1.2. El Paradigma Moderno: La Arquitectura Evolutiva (La "Mejor Práctica")

El diseño de software tradicional (predictivo) falló porque asumía requisitos fijos, intentando emular a la ingeniería civil donde la arquitectura se completa antes de la construcción.1 Este modelo es incompatible con el negocio moderno, donde "los cambios regulares en los requisitos son una necesidad empresarial".1 Los proyectos que intentaban construir toda la infraestructura por adelantado a menudo eran cancelados sin entregar ningún valor empresarial.32
La "mejor práctica" que ha surgido en respuesta es el Diseño Evolutivo (ED). Este es el "camino intermedio" entre el sobre-diseño (violar YAGNI) y el sub-diseño (código espagueti).33 El proceso de ED es simple:
Construir la implementación más simple posible de los requisitos actuales.33
Cuando llega un nuevo requisito, reorganizar (refactorizar) el código para que sea la implementación más simple posible del nuevo requisito más el antiguo.33
A nivel macro, esto se conoce como Arquitectura Evolutiva (EA). Es un enfoque para construir sistemas que soportan el "cambio incremental guiado como un principio de primer orden".2 Permite a las empresas experimentar con nuevas tecnologías con un costo y riesgo mínimos 2 y evita los costosos ciclos de reescritura.37
Este paradigma redefine la consulta del usuario. El "framework conceptual" que define al diseñador excepcional no es un diagrama de arquitectura estático, sino su dominio de un proceso que gestiona el cambio. La arquitectura se convierte en un verbo ("evolucionar") en lugar de un sustantivo ("el diagrama"). El resto de este informe detalla las cinco fases de ese proceso.

Parte 2: El Proceso Óptimo de Diseño Técnico (El "Cómo" del Diseñador Excepcional)


2.1. Fase 1: Interrogación del Requisito (El "Por Qué" y el "Qué")

Antes de escribir código o dibujar diagramas, el primer deber del diseñador excepcional es asegurar que el problema esté bien definido.38 No aceptan "listas de deseos" o especificaciones ambiguas.4
Los diseñadores excepcionales deconstruyen la solución propuesta por el negocio para encontrar el problema real. Y Combinator advierte contra las "Soluciones en Busca de un Problema (SISP)".5 Una solicitud de característica ("Queremos un 'Uber para plomeros'") es una solución.5 El diseñador excepcional pregunta: "¿Cuál es el problema?" (p.ej., "Es difícil encontrar plomeros disponibles").5 En un contexto brownfield, esto significa preguntar: "¿Cómo hacen los usuarios esto ahora?".3 A menudo, la solicitud es una traducción literal de un proceso manual existente. El trabajo del diseñador es entender ese proceso y luego diseñar una solución nativa del sistema, no una imitación del flujo de trabajo manual.3
El diseñador excepcional utiliza su conocimiento técnico como una herramienta para refinar y validar el requisito del producto. Un caso de estudio ilustra esto perfectamente: a un equipo se le pidió "construir encuestas de COVID por SMS".4 En lugar de aceptar el requisito, el diseñador comenzó a hacer preguntas de diseño técnico: "¿Cómo manejaremos las respuestas entrantes? ¿Qué pasa si una respuesta no coincide con las opciones dadas?".4 Al hacer estas preguntas, el diseñador expuso una falla fundamental en el concepto del producto. El equipo se dio cuenta de que la solución era inviable antes de que se escribiera una sola línea de código.4
La primera fase del diseño técnico no es técnica. Es una interrogación del producto para llegar a un requisito singular e inequívoco.40 Esto evita la violación más costosa de YAGNI: construir perfectamente la característica equivocada. El entregable de esta fase son requisitos claros, a menudo en forma de Historias de Usuario 41 y Criterios de Aceptación.22

2.2. Fase 2: Análisis del Repositorio (El "Dónde" y el "Con Qué")

Una vez que el "qué" está claro, el diseñador debe "considerar todos los aspectos técnicos necesarios... del repo de software existente".

2.2.1. Evaluación Rápida y Análisis de Código

El proceso comienza con una investigación de fondo.38
Análisis Estático (SAST): Inspecciona el código sin ejecutarlo.6 Es fundamental para entender la estructura, la sintaxis, las vulnerabilidades 6 y, críticamente, la adherencia a los principios arquitectónicos.43
Análisis Dinámico (DAST): Ejecuta la aplicación para observar el comportamiento en tiempo de ejecución.6 Es esencial para encontrar cuellos de botella de rendimiento y fugas de memoria 44, que son problemas comunes en sistemas brownfield.

2.2.2. Identificación de Patrones y Dependencias Existentes

El diseñador debe identificar los patrones existentes para "armonizar" con ellos.
Manual: El primer paso es simplemente "conocer" los patrones.45 Un desarrollador senior identificará patrones por heurística: nombres de clases (Factory, Adapter, Service), estructura de directorios, etc. Se evalúa el estado actual, buscando "puntos de dolor" y componentes fuertemente acoplados.46
Automatizado (Práctica Moderna): Se utilizan herramientas especializadas. Herramientas como SciTools Understand pueden crear grafos de dependencia y calcular métricas.47 Los asistentes de codificación basados en IA (Inteligencia Artificial) que son conscientes del repositorio 49, como Documatic 48, permiten usar lenguaje natural para consultar la base de código (p.ej., "Muéstrame dónde nos conectamos a la base de datos").48 La GenAI puede acelerar drásticamente las tareas de comprensión del código y refactorización.50

2.2.3. La Técnica del Diseñador Excepcional: Análisis de Acoplamiento de Cambio

Esta es la técnica más avanzada para el análisis de brownfield. Un grafo de dependencia estático le dice lo que podría romperse. El Análisis de Acoplamiento de Cambio (o Acoplamiento Temporal) le dice lo que históricamente ha roto.
Esta técnica identifica módulos que cambian juntos en los commits de Git.8 Revela dependencias lógicas y ocultas que el análisis estático no puede ver. Herramientas como CodeScene pueden ejecutar este análisis a través de múltiples repositorios Git.8 Esto es esencial para el ejemplo del usuario (Svelte/Laravel/Python). Revelaría si un cambio en el composer.json de Laravel (Repo A) está temporalmente acoplado a un cambio en el package.json de Svelte (Repo B). Esto expone el costo de coordinación real entre equipos y los verdaderos "puntos calientes" del sistema.7
Una técnica poderosa para visualizar esto es el uso de Bases de Datos de Grafos (Neo4j).9 Un diseñador puede cargar el código, las dependencias SQL y las relaciones del repositorio como nodos y relaciones.9 Luego, puede ejecutar consultas Cypher recursivas (p.ej., MATCH path = (t:Table)-->(:File)) para "rastrear" el impacto de un cambio en una tabla de pgvector hasta el componente de Svelte que finalmente consume esos datos.9
Un diseñador estándar analiza el código. Un diseñador excepcional analiza el historial de cambios. Este análisis es la forma más precisa de predecir el "efecto dominó" y el costo real de la nueva característica.

2.3. Fase 3: La Decisión de Armonización: ¿"Tidy First?" (La Heurística Central)

Esta fase aborda directamente la tensión central de la consulta: "promover los minimos cambios viables" versus "harmonizado con los patrones diseño existente".
La heurística que nombra este dilema es "Tidy First?" (¿Ordenar Primero?) de Kent Beck.11 El dilema es: "Tengo que cambiar este código, está desordenado, ¿ordeno (refactorizo) primero?".11 Beck redefine "refactorización" (un término que se ha inflado para significar grandes proyectos de deuda técnica) a "tidyings" (ordenamientos): "los pequeños y adorables refactorings que nadie podría odiar".10 Estos son cambios estructurales que duran de minutos a una hora.54

2.3.1. La Regla de Oro: Separar Cambios Estructurales (S) y de Comportamiento (B)

La regla operativa central de Kent Beck es separar los tipos de cambio 55:
Un Cambio de Comportamiento (B) añade nueva funcionalidad (la característica solicitada).
Un Cambio Estructural (S) es un "tidying" o refactorización que "armoniza" el código.
La regla clave es: "estar siempre haciendo un tipo de cambio o el otro, pero nunca ambos al mismo tiempo".55 Hacer ambos simultáneamente (p.ej., añadir una característica Y al mismo tiempo refactorizar una función no relacionada) es la principal fuente de riesgo y errores. El diseñador excepcional elige secuenciar estos cambios (S y B) de la manera más rentable.55

2.3.2. El Modelo Económico del "Tidy First?" (El "Cuándo")

La decisión de "ordenar primero" no es una decisión de "limpieza" dogmática 56, sino una decisión económica.11
La fórmula es 58: Un diseñador excepcional ordena (armoniza) primero si y solo si:
$costo(ordenar) + costo(cambio\_B \text{ después}) < costo(cambio\_B \text{ sin ordenar})$
En otras palabras: ¿Es el costo de limpiar el desorden ahora 54 menor que el costo adicional que se pagará por implementar la característica dentro del desorden?.58 Si la respuesta es sí, se ordena primero.
Esto se basa en una visión profunda del valor del software. Como señala Kent Beck, "Pensé que me pagaban por lo que había hecho. No era así. Me pagaban principalmente por lo que podía hacer después".56 El valor del software no son solo sus características actuales (flujo de caja), sino su capacidad de cambiar en el futuro. En finanzas, esto se llama "opcionalidad".56 Un código desordenado y acoplado tiene baja opcionalidad. "Ordenar" (armonizar) es el acto de gastar dinero ahora (tiempo de desarrollador) para comprar opcionalidad futura (hacer que los cambios futuros sean más baratos).54
La siguiente tabla traduce este modelo económico en una guía de decisión táctica.
Tabla 1: Matriz de Decisión Táctica: ¿"Tidy First?"

Escenario (Análisis del Desorden)
Heurística de Secuenciación (S/B)
Justificación Económica (Por Qué)
El desorden (alto acoplamiento) hace que el cambio de Comportamiento (B) sea arriesgado o significativamente más caro.
Ordenar Primero (Primero S)
$costo(S) < (costo(B \text{ sin } S) - costo(B \text{ con } S))$.58 El ahorro en B paga el costo de S.
El desorden es feo, pero no está relacionado con la ruta del código del cambio B.
Comportamiento Primero (Primero B)
Ordenar ahora (S) no tiene ROI inmediato 54 y viola YAGNI (es una generalización innecesaria).13
El desorden está relacionado, pero no está claro cuál es la abstracción correcta (S) todavía.
Comportamiento Primero (Primero B)
Implementar B (incluso de forma desordenada) aclarará los patrones de abstracción correctos.55 Refactorizar prematuramente es arriesgado.
Se implementó B, pero ahora el desorden es obvio y esta área del código se volverá a tocar pronto.
Ordenar Después (Después S)
Se paga la "deuda" 58 inmediatamente después de la característica, para amortizar el costo en futuros cambios.


2.4. Fase 4: Diseño de la Solución (El "Cómo" Mínimo Viable)


2.4.1. Mínima Arquitectura Viable (MVA) y Mínimo Cambio Viable (MVC)

Esta es la estrategia de implementación que cumple con KISS/YAGNI. La arquitectura tradicional es un cuello de botella porque busca crear una arquitectura "casi perfecta" que escale a todas las necesidades futuras.14 Esto es una violación fundamental de YAGNI.
La solución es la Mínima Arquitectura Viable (MVA).14 MVA no es "sin arquitectura". Es la arquitectura suficiente para el lanzamiento inicial, que sirve como un "trampolín" (stepping stone) hacia la visión a largo plazo.14 Reduce el tiempo de comercialización y el desperdicio de recursos.14 Esto se alinea con el Mínimo Cambio Viable (MVC) 15 y el Mínimo Reemplazo Viable (MVR) 59, que prioriza mejoras incrementales sobre un "big bang".59

2.4.2. La Heurística del Brownfield: "No Reescribir, Refactorizar"

La tentación en un sistema brownfield 25 es declarar la bancarrota técnica y "reescribir desde cero".16 El diseñador excepcional se resiste a esto, armado con el argumento clave de Joel Spolsky: "No hay absolutamente ninguna razón para creer que harás un mejor trabajo la segunda vez".16 ¿Por qué? Porque el equipo original (que ya no está) al menos tenía el contexto. El nuevo equipo "simplemente cometerá la mayoría de los viejos errores de nuevo, e introducirá algunos problemas nuevos".16 El diseñador excepcional respeta el código legado y aplica la refactorización incremental.46

2.4.3. Diseño Evolutivo de Bases de Datos (EvoDB)

Esto es crítico para el stack del usuario (Postgres/pgvector). El diseño ágil a menudo se rompe en la base de datos.61 El Diseño Evolutivo de BD 61 trata los cambios de BD como refactorizaciones.
Proceso: (1) Todos los artefactos de la BD (esquema, datos) están bajo control de versiones con el código de la aplicación.61 (2) Todos los cambios (DDL, DML) son migraciones.61 (3) Estas migraciones son pequeñas, automatizadas y se ejecutan como parte del pipeline de CI (Integración Continua).61 (4) Una Refactorización de BD es el cambio acoplado de (esquema + migración de datos + código de acceso a la BD).61

Parte 3: Aplicación al Ecosistema Heterogéneo (Análisis del Ejemplo del Usuario)

El stack específico del usuario (Svelte, Python, Laravel) no es un monolito; es un sistema distribuido.63 Un diseñador estándar ve tres proyectos separados.31 Un arquitecto excepcional ve un único sistema distribuido. La complejidad no está en los nodos (Laravel, Python), sino en las aristas (las llamadas de red y los contratos de datos entre ellos).65

3.1. Desafío 1: Gestión de Dependencias (El "Efecto Dominó" Multi-Repo)


3.1.1. Patrón de Aislamiento del Frontend: Backends-for-Frontends (BFF)

Problema: El widget de Svelte 66 necesita datos de ambos backends (RAG de Python, Admin de Laravel). Esto acopla fuertemente al cliente a dos APIs dispares, creando una sobrecarga de integración y múltiples llamadas de red en el cliente.67
Solución (Mejor Práctica): Introducir un Backend-for-Frontend (BFF).67 Este es un nuevo servicio (p.ej., un simple Node.js o incluso un BFF dedicado de Laravel/Python) que es propiedad del equipo de Svelte.
Funcionamiento: (1) El widget de Svelte hace una sola llamada a su BFF (p.ej., $GET /widget-data$). (2) El BFF orquesta las llamadas: llama al servicio de Python-RAG y al servicio de Laravel-Admin. (3) El BFF agrega y transforma las dos respuestas en una sola carga útil optimizada para la vista de Svelte.67
Valor: Desacopla radicalmente el frontend. Permite al equipo de Svelte evolucionar de forma autónoma 67 y evita tener un backend de propósito general que intente servir a múltiples clientes.67

3.1.2. Patrones de Integración Backend-a-Backend (Python-Laravel)

¿Cómo se comunica el backend de RAG (Python) y el backend de Admin (Laravel)? (p.ej., cuando se crea un nuevo "cliente" en Laravel, el sistema de RAG necesita saberlo). La elección del patrón de integración es una decisión de diseño fundamental.
Tabla 2: Patrones de Integración para el Stack Python-Laravel

Patrón de Integración
Caso de Uso (Ejemplo)
Ventajas
Desventajas (Riesgo de Acoplamiento)
API Síncrona (REST/RPC)
Python llama a un endpoint de Laravel para validar un cliente en tiempo real.
Simple, respuesta inmediata.
Alto acoplamiento temporal. Si Laravel está caído, Python falla.
Base de Datos Compartida
Laravel escribe en la tabla clients; Python lee de la tabla clients.31
Muy simple de implementar.31
El peor acoplamiento. El esquema de la BD se convierte en un contrato rígido. Un cambio de migración en Laravel 69 rompe Python instantáneamente.61
Colas de Mensajes (Asíncrono)
Laravel publica un evento client.created en RabbitMQ.31 Python consume de esa cola.31
Desacoplamiento total. Resiliencia (si Python está caído, los mensajes esperan). Escalabilidad.
Mayor complejidad operativa (se necesita un broker de mensajes).


3.1.3. Análisis de Impacto de Cambio (CIA) en Microservicios

En este sistema distribuido, ¿cómo "considerar todos los aspectos" del "efecto dominó" (ripple effect) de un cambio?.70 El ISAR (Incremental Software Architecture Reconstruction) es un framework conceptual para esto.72 Es un proceso automatizado 74 que proporciona retroalimentación inmediata a los desarrolladores sobre el impacto de sus cambios.73
Proceso de ISAR 72:
Línea Base (IR): El sistema analiza continuamente los repositorios para construir una Representación Intermedia (IR) de toda la arquitectura del sistema.
Delta: Cuando un desarrollador hace un commit, el sistema extrae un "Delta" (el cambio).
Análisis de Impacto: Compara el Delta con el IR para "identificar el impacto directo e indirecto".72
Reglas: Aplica reglas personalizadas, como "Llamada Inválida" (una llamada a un endpoint REST que ya no existe) o "Método de Servicio Modificado" (un cambio en la firma que afectará a los consumidores).72

3.2. Desafío 2: Mantenimiento de la Armonía (Gobernanza Automatizada)

Esta es la "garantía" que solicita la consulta: "asegurar que" el diseño se mantenga armonizado. Un diseñador tradicional escribiría un documento wiki de "Guía de Estilo" y esperaría que todos lo leyeran. Esto falla inevitablemente.75 La gobernanza arquitectónica excepcional se logra por ejecución, no por documentación.

3.2.1. El Concepto: Funciones de Aptitud Arquitectónica (Architectural Fitness Functions)

Esta es la respuesta de la Arquitectura Evolutiva a la "degradación" del diseño.75
Definición: "Cualquier mecanismo que realiza una evaluación de integridad objetiva de alguna característica de la arquitectura".17
Traducción: Son pruebas automatizadas (unitarias, de pipeline) que verifican la arquitectura.18

3.2.2. Aplicación 1 (Gobernanza Interna): ArchUnit

Problema: ¿Cómo "armonizar con los patrones existentes" dentro de un repositorio (p.ej., el backend de Laravel o Python)?.19
Solución: ArchUnit.19 Es una biblioteca (de Java, pero los conceptos son universales y existen equivalentes como NetArchTest o dependency-cruiser 17) que permite escribir pruebas unitarias que obligan a cumplir las reglas de arquitectura.19
Ejemplo: Un diseñador excepcional no documenta el patrón de capas; lo prueba. El siguiente código conceptual (basado en ArchUnit 19) es una prueba unitaria que se ejecuta en el pipeline de CI:
Java
@ArchTest
private final ArchRule layered_architecture_is_respected =
        layeredArchitecture()
               .consideringAllDependencies()
               .layer("Controller").definedBy("..controller..")
               .layer("Service").definedBy("..service..")
               .layer("Repository").definedBy("..repository..")
                // Reglas de gobernanza
               .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
               .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller")
               .whereLayer("Repository").mayOnlyBeAccessedByLayers("Service");


Valor: Si un nuevo desarrollador intenta añadir un cambio que viola este patrón (p.ej., el Controlador llama directamente al Repositorio), el pipeline de CI falla. La "armonía" ya no es una sugerencia; es un requisito ejecutable.19

3.2.3. Aplicación 2 (Gobernanza Externa): Pruebas de Contrato (Pact)

Problema: El sistema del usuario es distribuido (Parte 3). Las Funciones de Aptitud también deben gobernar las fronteras entre servicios (Svelte-BFF, BFF-Python, BFF-Laravel). Los microservicios fallan en sus puntos de integración.20
Solución: Consumer-Driven Contract Testing (CDCT) 20 usando una herramienta como Pact.21
Proceso Detallado:
Consumidor (p.ej., el BFF): En sus pruebas unitarias, el BFF (Consumidor) define su expectativa del servicio de Python (Proveedor). "Cuando hago $POST /rag-query$ con $\{ \text{"question": "..."} \}$, espero un $200 \text{ OK}$ con un JSON que contenga un campo $answer$".80
Pacto (Archivo): Al ejecutar esta prueba, Pact genera un archivo de contrato (JSON) que captura esta expectativa.81
Broker: El CI del Consumidor publica este "pacto" en un servidor central llamado Pact Broker.83
Proveedor (p.ej., Python-RAG): En su pipeline de CI, el servicio de Python descarga el "pacto" de su consumidor (el BFF) desde el Broker.85
Verificación: Pact reproduce la solicitud del contrato contra el servicio de Python real y verifica que la respuesta real coincida con la expectativa del contrato.85
Resultado: Si el equipo de Python renombra el campo $answer$ a $response\_text$, su propio pipeline de CI fallará.20 Se les impide fusionar un cambio que rompería al BFF 86, permitiendo a los equipos evolucionar de forma independiente pero segura.86

Parte 4: El Entregable: Documentación Mínima para un Impacto Máximo

La documentación tradicional es un cuello de botella y a menudo está desactualizada.88 En el diseño ágil y evolutivo, el código y las pruebas (como las Funciones de Aptitud) son la documentación principal.41

4.1. La Filosofía: Documentación Mínima Viable (MVD)

El objetivo no es la documentación "perfecta", sino la "suficiente".90 Se trata de "priorizar despiadadamente".90 MVD es la menor cantidad de documentación necesaria para facilitar la comunicación, capturar decisiones críticas y dar soporte al mantenimiento futuro.22 Los componentes esenciales de MVD incluyen la visión del producto, las historias de usuario y, fundamentalmente, las decisiones de arquitectura y diseño.22

4.2. El Estándar de Oro: Registros de Decisiones de Arquitectura (ADR)

Este es el entregable clave de la Fase 4 del proceso de diseño. Es el artefacto que responde al por qué.91
Definición: Un ADR (Architectural Decision Record) captura una única decisión de diseño arquitectónicamente significativa (ASR) y su justificación.23
Valor: En un sistema brownfield que evoluciona 93, el código le dice qué es el sistema, pero el ADR le dice por qué es así. Evita que los futuros desarrolladores cuestionen o reviertan decisiones cruciales porque no entendieron el contexto o los trade-offs.88
Almacenamiento: Los ADRs se almacenan como archivos de texto (Markdown) en el repositorio Git, junto al código que afectan.95

4.3. Herramientas y Plantillas de ADR

Existen herramientas CLI para gestionar el ciclo de vida de los ADRs (p.ej., adr-tools, pyadr).23 La plantilla más referenciada por su simplicidad y poder es la de Michael Nygard.24
Tabla 3: Plantilla de ADR Mínimo Viable (Basada en Michael Nygard)

Campo
Descripción
Ejemplo (Basado en el Stack del Usuario)
Título
Una breve descripción de la decisión, no del problema.24
ADR-003: Adopción del Patrón BFF para el Widget de Svelte
Estado
.24
Aceptado
Contexto
El problema, las fuerzas en juego, las limitaciones.24
El widget de Svelte necesita datos de RAG (Python) y Admin (Laravel). Esto crea un alto acoplamiento y múltiples llamadas de red desde el cliente, afectando el rendimiento y la autonomía del equipo de frontend.
Decisión
La solución elegida, de forma clara e inequívoca.24
Implementaremos un servicio BFF dedicado (en Node.js/Express) que será propiedad del equipo de Svelte. Este BFF actuará como el único gateway para el widget, orquestando y agregando las llamadas a los backends de Python y Laravel.
Consecuencias
Los trade-offs (positivos y negativos).24
+ Desacopla Svelte de los backends. Reduce las llamadas de red del cliente. Permite al equipo de frontend iterar de forma autónoma.67

+ El BFF puede implementar un caché específico para la UI.

- Introduce un nuevo componente en el stack 63 que debe ser mantenido, monitoreado y desplegado, aumentando la complejidad operativa.

- El BFF debe implementar Pruebas de Contrato (Pact) para gestionar su acoplamiento con los dos backends.


Parte 5: Conclusión: La Síntesis del Proceso del Diseñador Excepcional

El "proceso óptimo, mínimo viable, 'KISS DRY YAGNI'" para introducir un nuevo requisito en un repositorio existente no es una lista de verificación estática. Es la ejecución disciplinada de un ciclo de retroalimentación de diseño evolutivo.
El proceso sintetizado es el siguiente:
Un diseñador excepcional Interroga el requisito 4 para entender el problema (Fase 1).
Luego, Analiza el repositorio existente, centrándose en el Acoplamiento de Cambio 8 para entender el costo real (Fase 2).
Toma una decisión económica explícita sobre la armonización usando "Tidy First?" 58, separando los cambios Estructurales (S) de los de Comportamiento (B) 55 (Fase 3).
Implementa la solución usando una Mínima Arquitectura Viable (MVA) 14, favoreciendo la refactorización incremental 16 (Fase 4).
Asegura la armonía futura automáticamente con Funciones de Aptitud (ArchUnit, Pact) que convierten los patrones en pruebas ejecutables 19 (Fase 5).
Finalmente, Registra el "por qué" de la decisión en un ADR 24 que vive con el código, informando al próximo diseñador que comience el ciclo de nuevo.
Este proceso no es lineal (de 1 a 5); es un ciclo. Las Funciones de Aptitud y los ADRs (Fase 5) proporcionan la retroalimentación continua 18 y el contexto 93 que alimentan el Análisis (Fase 2) y la Interrogación (Fase 1) del próximo cambio. El diseñador de software verdaderamente excepcional no es alguien que produce el diseño "perfecto" de una sola vez. Es la persona que diseña, construye y acelera este ciclo de retroalimentación, permitiendo que el sistema y el equipo evolucionen de manera segura, armoniosa y con un propósito claro.
Fuentes citadas
Foreword to Building Evolutionary Architectures - Martin Fowler, acceso: noviembre 9, 2025, https://martinfowler.com/articles/evo-arch-forward.html
Evolutionary architecture | Thoughtworks United States, acceso: noviembre 9, 2025, https://www.thoughtworks.com/en-us/insights/decoder/e/evolutionary-architecture
Engineers who care about product outcomes - how do you deal with feature factory environments? : r/ExperiencedDevs - Reddit, acceso: noviembre 9, 2025, https://www.reddit.com/r/ExperiencedDevs/comments/1md3vrp/engineers_who_care_about_product_outcomes_how_do/
The hardest part of building software is not coding, it's requirements - Stack Overflow, acceso: noviembre 9, 2025, https://stackoverflow.blog/2023/12/29/the-hardest-part-of-building-software-is-not-coding-its-requirements/
How to get startup ideas : YC Startup Library | Y Combinator, acceso: noviembre 9, 2025, https://www.ycombinator.com/library/8g-how-to-get-startup-ideas
Static vs. Dynamic Code Analysis - Qt, acceso: noviembre 9, 2025, https://www.qt.io/quality-assurance/blog/static-vs-dynamic-code-analysis
Microservice Dependencies - Visualization - CodeScene, acceso: noviembre 9, 2025, https://codescene.com/blog/microservice-dependencies-visualization
Change Coupling: Visualize Logical Dependencies — CodeScene ..., acceso: noviembre 9, 2025, https://docs.enterprise.codescene.io/versions/5.1.0/guides/technical/change-coupling.html
Using GraphDbs to Visualize Code/SQL dependencies - DEV ..., acceso: noviembre 9, 2025, https://dev.to/dealeron/using-graphdbs-to-visualize-code-sql-dependencies-3370
acceso: noviembre 9, 2025, https://brianreich.dev/book-review/tidy-first-by-kent-beck/#:~:text=Refactoring%20and%20tidying%20have%20a,take%20time%20to%20do%20it.
Tidy First? Kent Beck on Refactoring - YouTube, acceso: noviembre 9, 2025, https://www.youtube.com/watch?v=XmsyvStDuqI
3 software development principles I wish I knew earlier in my career, and the power of YAGNI, KISS, and DRY : r/programming - Reddit, acceso: noviembre 9, 2025, https://www.reddit.com/r/programming/comments/1bmicj0/3_software_development_principles_i_wish_i_knew/
Clean Code Essentials: YAGNI, KISS, DRY - DEV Community, acceso: noviembre 9, 2025, https://dev.to/juniourrau/clean-code-essentials-yagni-kiss-and-dry-in-software-engineering-4i3j
Minimum Viable Architecture in Product Development | BCG, acceso: noviembre 9, 2025, https://www.bcg.com/x/the-multiplier/minimum-viable-architecture-in-product-development
The Minimum Viable Change - Scaling Biotech, acceso: noviembre 9, 2025, https://scalingbiotech.com/2022/06/15/the-minimum-viable-change/
Why Brownfield Development Works For Your App | Tarka Labs Blogs, acceso: noviembre 9, 2025, https://blog.tarkalabs.com/brownfield-development-f1d5fa0b39c8
The Up-and-Running Guide to Architectural Fitness Functions - Mikael Vesavuori, acceso: noviembre 9, 2025, https://mikaelvesavuori.se/blog/2023-08-20_The-Up-and-Running-Guide-to-Architectural-Fitness-Function
Fitness function-driven development | Thoughtworks United States, acceso: noviembre 9, 2025, https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development
Optimizing Software Architecture: Fitness Functions Using ArchUnit ..., acceso: noviembre 9, 2025, https://kamlesh-kumar.com/optimizing-software-architecture-fitness-functions-using-archunit/
What is contract testing? A Complete Guide for Beginners, acceso: noviembre 9, 2025, https://www.frugaltesting.com/blog/what-is-contract-testing-a-complete-guide-for-beginners
Pact Docs: Introduction, acceso: noviembre 9, 2025, https://docs.pact.io/
Minimum Viable Documentation for Agile Product Teams - Beyond the Backlog, acceso: noviembre 9, 2025, https://beyondthebacklog.com/2024/09/21/minimum-viable-documentation-2/
Architectural Decision Records, acceso: noviembre 9, 2025, https://adr.github.io/
Documenting architecture decisions - The GDS Way, acceso: noviembre 9, 2025, https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html
Brownfield (software development) - Wikipedia, acceso: noviembre 9, 2025, https://en.wikipedia.org/wiki/Brownfield_(software_development)
Turning Legacy to Leverage: Building Developer Platforms in Brownfield Environments, acceso: noviembre 9, 2025, https://www.syntasso.io/post/turning-legacy-to-leverage-building-developer-platforms-in-brownfield-environments
Greenfield vs Brownfield IT Projects: Key Differences, Costs and Risks - Naturaily, acceso: noviembre 9, 2025, https://naturaily.com/blog/greenfield-vs-brownfield-projects-in-it-differences-pros-cons-and-how-to-lead
The Beauty of Brownfield Development | by Matt Oey | Gusto Engineering, acceso: noviembre 9, 2025, https://engineering.gusto.com/the-beauty-of-brownfield-development-cea14c2053ae
KISS vs. DRY vs. YAGNI: Understanding Key Software Development Principles, acceso: noviembre 9, 2025, https://rrmartins.medium.com/kiss-vs-dry-vs-yagni-understanding-key-software-development-principles-e307b7419636
KISS, SOLID, YAGNI And Other Fun Acronyms | by Fernando Doglio | Bits and Pieces, acceso: noviembre 9, 2025, https://blog.bitsrc.io/kiss-solid-yagni-and-other-fun-acronyms-b5d207530335
Developer Guide: Integrating Laravel with Python | by Khouloud ..., acceso: noviembre 9, 2025, https://medium.com/@khouloud.haddad/developer-guide-integrating-laravel-with-python-fed560afd38e
Incremental Delivery Through Continuous Design | Microsoft Learn, acceso: noviembre 9, 2025, https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/brownfield/incremental-delivery-through-continuous-design
A Brief Summary of Evolutionary Design - CodingItWrong.com, acceso: noviembre 9, 2025, https://codingitwrong.com/2024/01/29/brief-summary-of-evolutionary-design.html
What is Evolutionary Design? - Mozaic Works, acceso: noviembre 9, 2025, https://mozaicworks.com/blog/what-is-evolutionary-design
Practice: Evolutionary Design, acceso: noviembre 9, 2025, https://www2.htw-dresden.de/~anke/openup/practice.tech.evolutionary_design.base/guidances/practices/evolutionary_design_DE27D8D9.html
Using Cloud Fitness Functions to Drive Evolutionary Architecture - Amazon AWS, acceso: noviembre 9, 2025, https://aws.amazon.com/blogs/architecture/using-cloud-fitness-functions-to-drive-evolutionary-architecture/
Microservices | Technology Radar | Thoughtworks United States, acceso: noviembre 9, 2025, https://www.thoughtworks.com/en-us/radar/techniques/microservices
Engineering Design Process - Science Buddies, acceso: noviembre 9, 2025, https://www.sciencebuddies.org/science-fair-projects/engineering-design-process/engineering-design-process-steps
Engineering Design Process - TeachEngineering, acceso: noviembre 9, 2025, https://www.teachengineering.org/populartopics/designprocess
The Importance of Quality Requirements in Software Development | TestEvolve, acceso: noviembre 9, 2025, https://www.testevolve.com/blog/the-importance-of-quality-requirements-in-software-development
Agile Documentation: Benefits and Best Practices - Swimm, acceso: noviembre 9, 2025, https://swimm.io/learn/code-documentation/documentation-in-agile-why-it-matters-and-tips-for-success
Writing "minimum viable" technical design documents - Cody Django Redmond, acceso: noviembre 9, 2025, https://codydjango.com/software-technical-design-documents/
A Developer's Guide to Static vs. Dynamic Testing - Kiuwan, acceso: noviembre 9, 2025, https://www.kiuwan.com/blog/static-vs-dynamic-testing-guide/
Static vs. dynamic code analysis: A comprehensive guide - vFunction, acceso: noviembre 9, 2025, https://vfunction.com/blog/static-vs-dynamic-code-analysis/
How do you identify a design pattern when reading source code? [closed] - Stack Overflow, acceso: noviembre 9, 2025, https://stackoverflow.com/questions/2376344/how-do-you-identify-a-design-pattern-when-reading-source-code
Best Practices for Implementing Design Patterns in Legacy Code - DEV Community, acceso: noviembre 9, 2025, https://dev.to/wallacefreitas/best-practices-for-implementing-design-patterns-in-legacy-code-4ko2
Understand: The Software Developer's Multi-Tool, acceso: noviembre 9, 2025, https://scitools.com/
Top 5 Tools to Understand Any Codebase Faster - SurajOnDev, acceso: noviembre 9, 2025, https://www.surajon.dev/top-5-tools-to-understand-any-codebase-faster
20 Best AI Coding Assistant Tools [Updated Aug 2025], acceso: noviembre 9, 2025, https://www.qodo.ai/blog/best-ai-coding-assistant-tools/
Unleash developer productivity with generative AI - McKinsey, acceso: noviembre 9, 2025, https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/unleashing-developer-productivity-with-generative-ai
Change coupling: visualize the cost of change - CodeScene, acceso: noviembre 9, 2025, https://codescene.com/blog/change-coupling-visualize-the-cost-of-change
Project Configuration — CodeScene 1 Documentation, acceso: noviembre 9, 2025, https://codescene.io/docs/configuration/project-config/index.html
Tidy First? by Kent Beck | Sandor Dargo's Blog, acceso: noviembre 9, 2025, https://www.sandordargo.com/blog/2024/03/16/tidy-first-by-kent-beck
"Tidy First" by Kent Beck - Asking the Right Questions About Software Change, acceso: noviembre 9, 2025, https://blog.planetargon.com/blog/entries/tidy-first-by-kent-beck-asking-the-right-questions-about-software-change
SB Changes. As I explain software design through… | by Kent Beck ..., acceso: noviembre 9, 2025, https://medium.com/@kentbeck_7670/bs-changes-e574bc396aaa
Tidy first? (book review) | kalabro.tech by Kate Marshalkina, acceso: noviembre 9, 2025, https://kalabro.tech/tidy-first/
Book Review: “Tidy First?” - Ham Vocke, acceso: noviembre 9, 2025, https://hamvocke.com/blog/tidy-first-review/
Lessons from “Tidy First?” - shahzad bhatti - Medium, acceso: noviembre 9, 2025, https://shahbhat.medium.com/lessons-from-tidy-first-a5d01083807b
The 6 Principles of Minimum Viable Replacement (MVR) | HatchWorks AI, acceso: noviembre 9, 2025, https://hatchworks.com/blog/software-development/the-6-principles-of-minimum-viable-replacement-mvr/
What is the most effective way to add functionality to unfamiliar, structurally unsound code?, acceso: noviembre 9, 2025, https://softwareengineering.stackexchange.com/questions/135311/what-is-the-most-effective-way-to-add-functionality-to-unfamiliar-structurally
Evolutionary Database Design - Martin Fowler, acceso: noviembre 9, 2025, https://martinfowler.com/articles/evodb.html
tagged by: evolutionary design - Martin Fowler, acceso: noviembre 9, 2025, https://martinfowler.com/tags/evolutionary%20design.html
Distributed computing - Wikipedia, acceso: noviembre 9, 2025, https://en.wikipedia.org/wiki/Distributed_computing
Benefits To Combine Laravel with Svelte - Acquaint Softtech, acceso: noviembre 9, 2025, https://acquaintsoft.com/answers/laravel-with-svelte
Microservices | Thoughtworks United States, acceso: noviembre 9, 2025, https://www.thoughtworks.com/en-us/insights/decoder/m/microservices
Looking for a personal (Svelte) stack - DEV Community, acceso: noviembre 9, 2025, https://dev.to/mandrasch/looking-for-a-personal-stack-dj7
Backends for Frontends Pattern - Azure Architecture Center ..., acceso: noviembre 9, 2025, https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends
A backend engineer's perspective on frontend design - Medium, acceso: noviembre 9, 2025, https://medium.com/@systemdesignwithsage/a-backend-engineers-perspective-on-frontend-design-39b7db1d0c68
Considering a new tech stack? Laravel could be the best choice | Bristol Creative Industries, acceso: noviembre 9, 2025, https://bristolcreativeindustries.com/considering-a-new-tech-stack-laravel-could-be-the-best-choice/
Towards Infrastructure For Change Impact Analysis in Microservices: Early Findings and Prototyping - arXiv, acceso: noviembre 9, 2025, https://arxiv.org/html/2501.11778v1
Assessing Evolution of Microservices Using Static Analysis - MDPI, acceso: noviembre 9, 2025, https://www.mdpi.com/2076-3417/14/22/10725
[Literature Review] Towards Change Impact Analysis in Microservices-based System Evolution - Moonlight, acceso: noviembre 9, 2025, https://www.themoonlight.io/en/review/towards-change-impact-analysis-in-microservices-based-system-evolution
Towards Change Impact Analysis in Microservices-based System Evolution, acceso: noviembre 9, 2025, https://www.computer.org/csdl/proceedings-article/saner/2025/351000a159/26TIt6ftNny
Towards Change Impact Analysis in Microservices-based System Evolution - ResearchGate, acceso: noviembre 9, 2025, https://www.researchgate.net/publication/388232369_Towards_Change_Impact_Analysis_in_Microservices-based_System_Evolution
Architectural Fitness Functions: An intro to building evolutionary architectures | by Dragos-Cornel Serban | Yonder TechBlog | Medium, acceso: noviembre 9, 2025, https://medium.com/yonder-techblog/architectural-fitness-functions-an-intro-to-building-evolutionary-architectures-dc529ac76351
Fitness Functions for Your Architecture - InfoQ, acceso: noviembre 9, 2025, https://www.infoq.com/articles/fitness-functions-architecture/
Examples of the live coding session "Fitness Functions for Your Architecture" - GitHub, acceso: noviembre 9, 2025, https://github.com/thmuch/architecture-fitness-functions
What is Contract Testing & How is it Used? - Pactflow, acceso: noviembre 9, 2025, https://pactflow.io/blog/what-is-contract-testing/
Contract Testing for Microservices: A Complete Guide - HyperTest, acceso: noviembre 9, 2025, https://www.hypertest.co/contract-testing/contract-testing-for-microservices
PACT Contract Testing - Because Not Everything Needs Full Integration Tests - ISE Developer Blog, acceso: noviembre 9, 2025, https://devblogs.microsoft.com/ise/pact-contract-testing-because-not-everything-needs-full-integration-tests/
Contract Testing with Pact - DoorDash, acceso: noviembre 9, 2025, https://careersatdoordash.com/blog/contract-testing-with-pact/
How to Perform PACT Contract Testing: A Step-by-Step Guide - HyperTest, acceso: noviembre 9, 2025, https://www.hypertest.co/contract-testing/pact-contract-testing
Contract Testing With Pact - by Adrika Roy - Medium, acceso: noviembre 9, 2025, https://medium.com/@adrikaroy/contract-testing-with-pact-aae5055bb0f8
Contract Testing for BFF (Backend for Frontend) Development - Paul Serban, acceso: noviembre 9, 2025, https://paulserban.eu/blog/post/contract-testing-for-bff-backend-for-frontend-development/
5 minute guide - Pact Docs, acceso: noviembre 9, 2025, https://docs.pact.io/5-minute-getting-started-guide
Breaking Free from End-to-End Testing: Why Contract Testing Is the Key to Microservices Success - Discover Technology, acceso: noviembre 9, 2025, https://technology.discover.com/posts/end-to-end-contract-testing
Contract Testing in Microservices: Fundamentals, Benefits, and Best Practices - Medium, acceso: noviembre 9, 2025, https://medium.com/@abo.saad.muaath/contract-testing-in-microservices-fundamentals-benefits-and-best-practices-f5928a12522e
Mastering design iterations: The power of documentation - DfE Digital, Data and Technology, acceso: noviembre 9, 2025, https://dfedigital.blog.gov.uk/2024/09/11/mastering-design-iterations-the-power-of-documentation/
Lightweight Architecture Decision Records | Technology Radar - Thoughtworks, acceso: noviembre 9, 2025, https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records
Minimum Viable Documentation – the art of documentation triage, acceso: noviembre 9, 2025, https://blog.knowledgeowl.com/blog/posts/minimum-viable-documentation/
A practical overview on Architecture Decision Records (ADR) - Claudio Taverna, acceso: noviembre 9, 2025, https://ctaverna.github.io/adr/
AWS Prescriptive Guidance: Using architectural decision records to streamline technical decision-making for a software development project - AWS Documentation, acceso: noviembre 9, 2025, https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf
Design Decision Log - Engineering Fundamentals Playbook - Microsoft Open Source, acceso: noviembre 9, 2025, https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/
Architecture decision record (ADR) examples for software planning, IT leadership, and template documentation - GitHub, acceso: noviembre 9, 2025, https://github.com/joelparkerhenderson/architecture-decision-record
Master architecture decision records (ADRs): Best practices for effective decision-making, acceso: noviembre 9, 2025, https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/
Architectural Decision Record (ADR) Templates in Markdown and Excel - Blog — Loqbooq, acceso: noviembre 9, 2025, https://loqbooq.app/blog/architectural-decision-record-templates
Decision Capturing Tools, acceso: noviembre 9, 2025, https://adr.github.io/adr-tooling/
ADR Templates - Architectural Decision Records, acceso: noviembre 9, 2025, https://adr.github.io/adr-templates/
