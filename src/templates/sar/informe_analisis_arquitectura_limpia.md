# Informe de Análisis de Arquitectura Limpia: [Nombre del Repositorio]

**ID Documento:** `[SAR-CLNARC]-[CODIGOPROYECTO]-[SEQ]`
**Documento Padre:** `[resumen_repositorio.md#ID]`
**Versión:** `1.0`
**Fecha:** `[AAAA-MM-DD]`

## 1. Evaluación General de Adherencia a Arquitectura Limpia

*[Evaluación general de cómo el sistema se alinea con los principios de Arquitectura Limpia (según Robert C. Martin). ¿Existe una clara separación de incumbencias? ¿Se respeta la regla de dependencia?]*

*   **Nivel de Adherencia Estimado:** `[ej., Alto, Medio-Alto, Medio, Medio-Bajo, Bajo]`
*   **Comentarios Generales:** `[Resumen del alineamiento con Arquitectura Limpia.]`

## 2. Identificación y Separación de Capas (Entidades, Casos de Uso, Adaptadores, Frameworks)

*   **Capa de Entidades (Dominio/Core):**
    *   **Identificación:** `[Proyectos/Namespaces que contienen las entidades de negocio puras y la lógica de dominio más fundamental.]`
    *   **Evaluación:** `[ej., Bien definida y aislada, Contiene referencias a frameworks, Lógica de dominio mezclada con lógica de aplicación.]`
*   **Capa de Casos de Uso (Aplicación):**
    *   **Identificación:** `[Proyectos/Namespaces que orquestan los flujos de la aplicación, implementan los casos de uso y contienen interfaces para la infraestructura.]`
    *   **Evaluación:** `[ej., Clara separación de la lógica de aplicación, Dependencias correctas hacia el dominio, Acoplamiento con detalles de infraestructura.]`
*   **Capa de Adaptadores de Interfaz (Infraestructura/Presentación - parte adaptadora):**
    *   **Identificación:** `[Proyectos/Namespaces que implementan los adaptadores para la infraestructura (ej., repositorios EF Core, clientes HTTP a servicios externos) y para la UI/API (ej., controladores, presentadores).]`
    *   **Evaluación:** `[ej., Implementaciones de interfaces de aplicación/dominio residen aquí, Referencias directas desde la aplicación a clases concretas de infraestructura.]`
*   **Capa de Frameworks y Drivers (Infraestructura/Presentación - parte externa):**
    *   **Identificación:** `[Se refiere a los frameworks mismos (ASP.NET Core, EF Core), drivers de BBDD, y la UI o API como mecanismo de entrega.]`
    *   **Evaluación:** `[ej., El núcleo de la aplicación es independiente de estos detalles, Fuerte acoplamiento del dominio con EF Core.]`

## 3. Adherencia a la Regla de Dependencia

*[Analizar si las dependencias fluyen hacia adentro (Presentación -> Aplicación -> Dominio; Infraestructura -> Aplicación/Dominio vía interfaces).]*

*   **Evaluación General:** `[ej., Mayormente respetada, Se observan violaciones significativas, Algunas dependencias incorrectas entre proyectos.]`
*   **Diagrama de Dependencias de Proyectos (Conceptual o Enlace):**
    *   `[Si es posible, incluir un diagrama simple o referenciar `informe_mapa_dependencias.md`]`
*   **Violaciones Específicas Identificadas:**
    *   **Violación 1:**
        *   **Descripción:** `[ej., Proyecto de Dominio (`Proyecto.Core`) tiene una referencia directa a `Proyecto.Infrastructure.Data`.]`
        *   **Impacto:** `[Acopla el dominio a detalles de implementación de base de datos, dificulta el cambio de ORM o BBDD, viola la independencia del dominio.]`
        *   **Ubicación del Problema:** `[Referencia en .csproj o `using` statement en archivo específico.]`
        *   **Sugerencia:** `[Invertir la dependencia usando una interfaz de repositorio en Dominio, implementada en Infraestructura.]`
    *   **Violación 2:**
        *   **Descripción:** `[ej., La capa de Aplicación (`Proyecto.Application`) usa clases concretas de un servicio externo definido en `Proyecto.Infrastructure.ExternalServices` en lugar de una abstracción.]`
        *   **Impacto:** `[Dificulta pruebas unitarias de la capa de aplicación, acoplamiento fuerte a una implementación específica del servicio externo.]`
        *   **Ubicación del Problema:** `[Clase/Método específico en Aplicación.]`
        *   **Sugerencia:** `[Definir una interfaz para el servicio externo en Aplicación, implementarla en Infraestructura.]`
*   **Buenas Prácticas Observadas:**
    *   `[ej., Uso de interfaces en la capa de Aplicación para definir contratos con la capa de Infraestructura (patrón Repositorio, etc.).]`

## 4. Independencia de Frameworks y UI

*   **Dominio/Core:**
    *   **Evaluación:** `[ej., Totalmente independiente (POCOs), Contiene atributos de EF Core o referencias a `System.Web`/`Microsoft.AspNetCore`.]`
    *   **Ejemplos de Acoplamiento (si existen):**
        *   `[Entidad `Product` en `Proyecto.Domain` decorada con `[Table("Products")]` de EF Core.]`
*   **Aplicación/Casos de Uso:**
    *   **Evaluación:** `[ej., Lógica de aplicación pura, Contiene referencias a `HttpContext` o clases de ASP.NET Core, Dependencia de tipos de datos de EF Core (ej. `DbSet`).]`
    *   **Ejemplos de Acoplamiento (si existen):**
        *   `[Servicio `OrderService` en `Proyecto.Application` accediendo directamente a `HttpContext.User`.]`

## 5. Integridad de los Límites Arquitectónicos

*   **Evaluación:** `[¿Cómo se protegen los límites entre capas? ¿Se usan DTOs entre Presentación y Aplicación? ¿Se exponen entidades de dominio directamente a la UI/API?]*
*   **Manejo de Datos entre Capas:**
    *   **Presentación <-> Aplicación:** `[ej., Uso de DTOs específicos, Mapeo con AutoMapper, Se exponen directamente entidades de dominio.]`
    *   **Aplicación <-> Dominio:** `[ej., Se operan directamente entidades de dominio, Se usan objetos de transferencia internos si es necesario.]`
    *   **Aplicación <-> Infraestructura:** `[ej., Comunicación a través de interfaces, Paso de entidades de dominio o DTOs específicos de infraestructura.]`

## 6. Testeabilidad

*   **Evaluación:** `[¿La arquitectura facilita las pruebas unitarias del dominio y la lógica de aplicación? ¿Es posible probar los casos de uso sin depender de la UI o la base de datos?]*
*   **Puntos Fuertes para la Testeabilidad:**
    *   `[ej., Uso de interfaces y DI permite mocking fácil de dependencias.]`
    *   `[ej., Lógica de dominio aislada en clases POCO.]`
*   **Desafíos para la Testeabilidad:**
    *   `[ej., Acoplamiento fuerte a clases concretas de infraestructura dificulta el aislamiento.]`
    *   `[ej., Lógica de negocio dentro de controladores de API o manejadores de eventos de UI.]`

## 7. Ejemplos Específicos de Conformidad o Desviación

*[Resaltar patrones o antipatrones específicos encontrados que ilustren la adherencia o desviación de los principios de Arquitectura Limpia.]*

*   **Conformidad: [ej., Implementación del Patrón Repositorio]**
    *   **Descripción:** `[La capa de Aplicación define interfaces `IRepository<T>` que son implementadas por la capa de Infraestructura usando EF Core, desacoplando la lógica de negocio de la persistencia.]`
    *   **Ubicación:** `[Interfaces en `Proyecto.Application.Interfaces`, Implementaciones en `Proyecto.Infrastructure.Data.Repositories`]`
*   **Desviación: [ej., Entidades de Dominio con Anotaciones de Framework]**
    *   **Descripción:** `[Las clases de entidad en el proyecto de Dominio están decoradas con atributos de `System.ComponentModel.DataAnnotations` o de EF Core, acoplando el dominio a detalles de UI/Framework y persistencia.]`
    *   **Ubicación:** `[Clase `User` en `Proyecto.Domain.Entities`]`
    *   **Impacto:** `[Reduce la independencia del dominio, introduce dependencias no deseadas.]`

## 8. Recomendaciones

*[Sugerencias para mejorar el alineamiento con Arquitectura Limpia. Pueden enlazar con `recomendaciones_refactorizacion.md`.]*

*   `[ej., Introducir DTOs para la comunicación entre la capa de Presentación/API y la capa de Aplicación para evitar exponer entidades de dominio.]`
*   `[ej., Refactorizar violaciones de la Regla de Dependencia moviendo interfaces al proyecto correcto e invirtiendo dependencias.]`
*   `[ej., Extraer lógica de negocio de los controladores de API hacia la capa de Aplicación.]`

## 9. Historial del Documento

| Versión | Fecha      | Autor(es)      | Cambios Realizados                                                  |
|---------|------------|----------------|---------------------------------------------------------------------|
| 1.0     | AAAA-MM-DD | [Nombre(s)]    | Versión inicial del informe de análisis de arquitectura limpia.      |
| ...     | ...        | ...            | ...                                                                 | 