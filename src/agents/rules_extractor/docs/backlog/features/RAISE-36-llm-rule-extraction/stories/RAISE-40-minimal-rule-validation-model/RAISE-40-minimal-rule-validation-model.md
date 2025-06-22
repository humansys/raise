# [RAISE-40] Minimal Rule Validation Model

## Historia de Usuario
**Como** desarrollador del MVP,  
**Necesito** un modelo Pydantic mínimo llamado `BusinessRule`,  
**Para que** el JSON devuelto por el LLM sea validado automáticamente.

## Descripción
Esta historia implementa un modelo de validación Pydantic para las reglas de negocio extraídas del código legado AS/400. El modelo debe definir la estructura básica de una regla de negocio y proporcionar validación automática para asegurar que los datos devueltos por el LLM cumplan con los requisitos mínimos.

## Criterios de Aceptación (BDD)

### Escenario 1: Validación de campos obligatorios
**Dado** que el LLM ha generado un objeto JSON de regla de negocio  
**Cuando** el objeto carece de algún campo obligatorio (`id`, `description`, `type`, `source_reference`, `confidence`)  
**Entonces** el sistema debe lanzar una excepción de validación  
**Y** proporcionar información clara sobre qué campo está faltando

### Escenario 2: Validación de formato de campos
**Dado** que el LLM ha generado un objeto JSON de regla de negocio con todos los campos obligatorios  
**Cuando** algún campo tiene un formato incorrecto (ej. `confidence` no es un número entre 0-1)  
**Entonces** el sistema debe lanzar una excepción de validación  
**Y** proporcionar información clara sobre el error de formato

### Escenario 3: Descomponer reglas complejas
**Dado** que el LLM ha generado reglas de diferentes tipos (validación, decisión, cálculo, flujo de trabajo)  
**Cuando** el sistema procesa estos diferentes tipos de reglas  
**Entonces** cada tipo debe validarse según su estructura específica  
**Y** mantener los campos comunes definidos en `BaseRule`

### Escenario 4: Prueba de validación exitosa
**Dado** que hay un ejemplo de JSON válido para una regla de negocio  
**Cuando** se valida con el modelo Pydantic  
**Entonces** la validación debe ser exitosa  
**Y** convertir el JSON a un objeto de Python totalmente tipado

## Guía de Implementación

### Contexto
El modelo `BusinessRule` ya ha sido implementado en `./rules_extractor/models/business_rule.py`. Este archivo contiene una implementación completa y extensible del modelo de reglas de negocio que incluye no solo los campos básicos requeridos sino también estructuras adicionales para diferentes tipos de reglas.

### Estado Actual
El modelo existente implementa:
- Una clase base `BaseRule` con campos comunes
- Clases específicas para diferentes tipos de reglas (`ValidationRule`, `DecisionRule`, `CalculationRule`, `WorkflowRule`)
- Enumeraciones para tipos controlados
- Validadores para asegurar la integridad de los datos
- Funciones auxiliares para la carga de reglas desde diccionarios

### Tareas de Implementación
Dado que la implementación del modelo ya existe y cumple con los requisitos de la historia, las tareas restantes son:

1. **Documentación del modelo**:
   - Crear documentación sobre cómo utilizar el modelo existente
   - Proporcionar ejemplos de uso para diferentes tipos de reglas

2. **Pruebas unitarias**:
   - Implementar pruebas para validar que el modelo funciona correctamente con diferentes entradas
   - Verificar que las validaciones funcionan como se espera
   - Comprobar la carga desde diccionarios

3. **Integración**:
   - Asegurar que el modelo está correctamente importado y utilizado en los módulos de extracción de reglas
   - Verificar que las excepciones se manejan adecuadamente

### Directrices Técnicas
- **KISS**: El modelo ya implementa una solución que cumple con los requisitos de la historia.
- **DRY**: Reutiliza las estructuras existentes para diferentes tipos de reglas a través de la herencia.
- **YAGNI**: El modelo incluye características que podrían considerarse más allá del MVP, pero están diseñadas de manera que no interfieren con el uso básico.

### Consideraciones de Arquitectura
- El modelo utiliza Pydantic para validación automática
- La jerarquía de clases permite extensibilidad
- Los validadores personalizados garantizan la integridad de los datos
- Las uniones tipadas (`Union`) permiten tratar diferentes tipos de reglas de manera homogénea

## Métricas de Éxito
- El modelo puede validar correctamente ejemplos de JSON generados por LLMs
- Las excepciones de validación son informativas y ayudan a diagnosticar problemas
- Las pruebas unitarias pasan exitosamente
- El modelo se integra correctamente con el resto del sistema de extracción de reglas

## Implementado por
[Nombre del implementador]

## Fecha de implementación
[Fecha] 