# RaiSE Kata: Extracción de Backlog desde Imágenes para Jafra+ (L1-10)

**ID**: L1-10
**Nombre**: Extracción y Estructuración de Backlog desde Imágenes para Proyectos Jafra+
**Descripción**: Sistematiza el proceso de conversión de backlogs presentados en formato de imagen (tablas, matrices, especificaciones visuales) a una estructura organizada de directorios y archivos de historias de usuario siguiendo las convenciones establecidas del proyecto.
**Objetivo**:
    *   Estandarizar la extracción de información de backlog desde imágenes
    *   Crear estructura consistente de directorios por historia de usuario
    *   Generar documentos de user story usando el template establecido
    *   Asegurar nomenclatura correcta y consistente en toda la estructura
    *   Facilitar la transición de especificaciones visuales a documentación técnica estructurada
**Dependencias**:
    *   `L0-03: Meta-Kata del Protocolo de Ejecución y Colaboración`
    *   Template de user story disponible en `.raise/templates/backlog/user_story.md`
    *   Imagen(es) del backlog con especificaciones de historias de usuario
    *   Estructura de feature definida (ej: F01-Admin-Lider)
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas de documentación y estructuración de proyectos

---

## Contexto y Principios

Esta kata formaliza el proceso observado en la sesión donde se extrajo exitosamente información de una imagen de backlog y se convirtió en estructura organizada. El proceso debe ser:

**Principios Fundamentales:**
*   **Extracción Sistemática**: Análisis metódico de cada historia visible en la imagen
*   **Nomenclatura Consistente**: Aplicación uniforme de convenciones de naming
*   **Template Adherence**: Uso estricto del template establecido para user stories
*   **Iteración Controlada**: Procesamiento de una historia a la vez con validación
*   **Trazabilidad Completa**: Mapping claro desde imagen hasta estructura final

---

## Pre-condiciones

- Se tiene acceso a imagen(es) del backlog con historias de usuario claramente identificables
- El template de user story está disponible y validado
- La estructura de feature objetivo está definida (ej: `docs/backlog/modulo-pedidos/F01-Admin-Lider/`)
- El Orquestador Humano puede validar la interpretación de cada historia extraída

---

## Fases del Protocolo de Ejecución

### **Fase 1: Planificación y Mapeo Inicial**

#### **Paso 1.1: Análisis de Imagen y Extracción de Historias**

**Instrucción (Orquestador):** 
```
"Analiza la imagen del backlog '[IMAGEN_PATH]' y extrae todas las historias de usuario identificables. 
Crea el documento de tracking en '.raise/docs/kata-sessions/YYYY-MM-DD_L1-10-Execution-[FEATURE_NAME].md'"
```

**Acción (Agente IA):**
1. **Crear documento de tracking** con estructura:
   ```markdown
   # Kata L1-10: Extracción de Backlog desde Imágenes
   ## Feature: [FEATURE_NAME]
   ## Fecha: [YYYY-MM-DD]
   
   ### Plan de Implementación
   - [ ] Análisis inicial de imagen
   - [ ] Extracción de historias individuales
   - [ ] Validación de interpretación
   - [ ] Creación de estructura de directorios
   - [ ] Generación de documentos user story
   - [ ] Validación final y cierre
   
   ### Historias Identificadas
   [Lista a completar en Paso 1.2]
   
   ### Decisiones de Nomenclatura
   [Decisiones a documentar durante ejecución]
   ```

2. **Analizar imagen sistemáticamente**:
   - Identificar columnas/campos de la tabla (ID, Requerimiento, Módulo, Cómo, Quiero, Para, etc.)
   - Extraer cada fila como una historia de usuario individual
   - Crear tabla de mapeo inicial

#### **Paso 1.2: Mapeo de Historias y Nomenclatura**

**Instrucción (Orquestador):** 
```
"Para cada historia identificada, genera la nomenclatura de directorio siguiendo el patrón: 
HU-[ID]-[Descripcion-Kebab-Case] y lista todas para validación."
```

**Acción (Agente IA):**
1. **Crear tabla de mapeo**:
   ```yaml
   historias_extraidas:
     - id: "HU-036"
       requisito: "R024"
       modulo: "Captura de Pedido"
       actor: "Líder JAFRA"
       quiero: "Recibir una alerta cuando un Veliz no pueda ingresar un pedido"
       para: "Identificar los siguientes pasos de apoyo al Consultor"
       directorio_propuesto: "HU-036-Recibir-Alerta-Veliz-No-Puede-Ingresar-Pedido"
       archivo_propuesto: "HU-036-Recibir-Alerta-Cuando-Veliz-No-Puede-Ingresar-Pedido.md"
   ```

2. **Actualizar documento de tracking** con lista completa
3. **Presentar para validación** del Orquestador Humano

**Criterios de Aceptación Fase 1:**
- Lista completa de historias extraídas de la imagen
- Nomenclatura consistente propuesta para cada historia
- Mapeo validado por el Orquestador Humano
- Plan detallado aprobado explícitamente

---

### **Fase 2: Ejecución Iterativa por Historia**

#### **Paso 2.1: Procesamiento Individual de Historia**

**Instrucción (Orquestador):** 
```
"Procesa la historia '[HU-ID]' creando su directorio y documento según el template. 
Procesa solo UNA historia a la vez y espera mi validación antes de continuar."
```

**Acción (Agente IA):**
1. **Crear directorio de la historia**:
   ```bash
   mkdir -p "[FEATURE_PATH]/[HU-XXX-Descripcion-Directorio]"
   ```

2. **Generar documento de user story** usando template:
   ```markdown
   # HU-XXX - [Título Descriptivo Completo]
   
   *ID JIRA:* HU-XXX
   *Funcionalidad Relacionada:* [F01-Admin-Lider]({{parent_Epic_link}})
   *Requerimiento Relacionado:* RXXX - [Nombre del Requerimiento]
   
   *Como* [Actor extraído de imagen]
   *Quiero* [Acción extraída de imagen]
   *Para* [Beneficio extraído de imagen]
   
   [Resto del template completado según contexto]
   ```

3. **Actualizar tracking** marcando historia como completada
4. **Notificar al Orquestador** para validación individual

#### **Paso 2.2: Validación Iterativa**

**Instrucción (Orquestador):** 
```
"Revisa el documento creado para HU-[ID]. Si está correcto, autoriza procesar la siguiente historia. 
Si requiere ajustes, especifica qué modificar antes de continuar."
```

**Criterios para Continuar:**
- Estructura de directorio correcta
- Nombre de archivo siguiendo convención establecida
- Template aplicado correctamente con información de la imagen
- Información técnica coherente y completa

#### **Paso 2.3: Bucle de Procesamiento**

**Proceso:** Repetir Paso 2.1 y 2.2 para cada historia hasta completar todas las historias identificadas en Fase 1.

**Condiciones de Pausa (según L0-03):**
1. **Error en procesamiento**: Si template no se aplica correctamente
2. **Ambigüedad en imagen**: Si información no es clara para una historia específica
3. **Validación fallida**: Si Orquestador requiere modificaciones

---

### **Fase 3: Validación Final y Cierre**

#### **Paso 3.1: Verificación de Completitud**

**Instrucción (Orquestador):** 
```
"Verifica que todas las historias identificadas han sido procesadas y genera el resumen final."
```

**Acción (Agente IA):**
1. **Verificar estructura completa**:
   ```bash
   # Listar estructura generada
   tree [FEATURE_PATH] -L 2
   ```

2. **Validar nomenclatura consistente**:
   - Todos los directorios siguen patrón HU-XXX-Descripcion-Kebab-Case
   - Todos los archivos siguen patrón HU-XXX-Descripcion-Completa.md
   - No hay duplicados o inconsistencias

3. **Generar métricas de completitud**:
   ```yaml
   metricas_finales:
     historias_en_imagen: [número]
     historias_procesadas: [número]
     porcentaje_completitud: "100%"
     directorios_creados: [número]
     archivos_generados: [número]
   ```

#### **Paso 3.2: Documentación de Lecciones Aprendidas**

**Acción (Agente IA):**
1. **Documentar en tracking**:
   ```markdown
   ## Lecciones Aprendidas
   - Patrones de nomenclatura aplicados
   - Ambigüedades resueltas durante el proceso
   - Convenciones establecidas para futuras extracciones
   
   ## Recomendaciones para Próximas Extracciones
   - [Recomendación específica basada en experiencia]
   ```

2. **Completar checklist del plan de implementación**

**Post-condiciones:**
- Estructura completa de directorios creada
- Todos los documentos de user story generados y validados
- Tracking completo con lecciones aprendidas
- 100% de historias de la imagen procesadas

---

## Especificaciones Técnicas Detalladas

### **Convenciones de Nomenclatura Establecidas**

#### **Directorios de Historia:**
```
Patrón: HU-[ID]-[Descripcion-Accion-Principal]
Ejemplo: HU-036-Recibir-Alerta-Veliz-No-Puede-Ingresar-Pedido
Reglas:
- Máximo 60 caracteres
- Kebab-case (guiones, no espacios)
- Descripción debe ser acción principal o objetivo core
- Sin artículos innecesarios (el, la, los, las)
```

#### **Archivos de User Story:**
```
Patrón: HU-[ID]-[Descripcion-Completa-Detallada].md
Ejemplo: HU-036-Recibir-Alerta-Cuando-Veliz-No-Puede-Ingresar-Pedido.md
Reglas:
- Puede ser más descriptivo que directorio
- Incluir contexto adicional si clarifica propósito
- Mantener coherencia con directorio padre
```

### **Template de User Story - Aplicación desde Imagen**

#### **Mapeo de Campos desde Imagen:**
```yaml
campo_imagen: "ID Req Jafra"
campo_template: "*Requerimiento Relacionado:*"
transformacion: "R[ID] - [Modulo]"

campo_imagen: "Cómo"
campo_template: "*Como*"
transformacion: "Extraer actor exacto"

campo_imagen: "Quiero"  
campo_template: "*Quiero*"
transformacion: "Extraer acción exacta"

campo_imagen: "Para"
campo_template: "*Para*"
transformacion: "Extraer beneficio exacto"

campo_imagen: "Reglas/Requisitos"
campo_template: "Secciones técnicas"
transformacion: "Interpretar y estructurar en criterios de aceptación"
```

#### **Enriquecimiento Técnico:**
Para cada historia extraída, el template debe incluir:
- **Criterios de Aceptación en Gherkin** basados en la columna "Reglas/Requisitos"
- **Componentes Técnicos** inferidos del contexto del módulo
- **Endpoints de API** apropiados para la funcionalidad
- **Dependencias** basadas en el requerimiento relacionado
- **Estimaciones** iniciales conservadoras

### **Manejo de Ambigüedades**

#### **Estrategias de Resolución:**
1. **Información Incompleta**: Usar placeholders claros para revisión posterior
2. **Terminología Ambigua**: Aplicar glosario del proyecto o escalation
3. **Dependencias Unclear**: Documentar asunciones para validación

#### **Escalation Triggers:**
- Imagen no legible en secciones críticas
- Terminología de negocio desconocida
- Conflictos entre requerimientos
- Información insuficiente para criterios de aceptación

---

## Validación de Calidad

### **Checklist de Calidad por Historia:**
```yaml
estructura:
  - [ ] Directorio creado con nomenclatura correcta
  - [ ] Archivo nombrado según convención
  - [ ] Template aplicado completamente

contenido:
  - [ ] Información extraída correctamente de imagen
  - [ ] Actor, acción y beneficio claros
  - [ ] Criterios de aceptación en Gherkin
  - [ ] Componentes técnicos relevantes
  - [ ] Estimaciones incluidas

consistencia:
  - [ ] Nomenclatura coherente con otras historias
  - [ ] Funcionalidad relacionada correcta
  - [ ] Requerimiento mapeado apropiadamente
```

### **Métricas de Éxito:**
- **Completitud**: 100% de historias procesadas
- **Consistencia**: 0% variaciones en nomenclatura
- **Calidad**: Template aplicado completamente en 100% casos
- **Trazabilidad**: Mapeo claro imagen → estructura en 100% casos

---

## Casos de Uso Específicos

### **Caso 1: Backlog Tabular Simple**
```
Imagen: Tabla con columnas ID, Módulo, Como, Quiero, Para
Procesamiento: Mapeo directo columna → campo template
Resultado: N historias con información completa
```

### **Caso 2: Backlog con Reglas Complejas**
```
Imagen: Incluye columna "Reglas/Requisitos" con especificaciones detalladas
Procesamiento: Interpretación en criterios Gherkin + componentes técnicos
Resultado: Historias enriquecidas técnicamente
```

### **Caso 3: Multiple Features en Una Imagen**
```
Imagen: Varias features/módulos en misma tabla
Procesamiento: Separación por feature + aplicación kata por feature
Resultado: Múltiples estructuras organizadas por feature
```

---

## Extensiones Futuras

### **Automatización Potencial:**
- OCR automático para extracción de texto
- Validación automática de nomenclatura
- Generación batch de múltiples features
- Integración con herramientas de gestión de backlog

### **Integraciones:**
- Sincronización con Jira/Azure DevOps
- Generación automática de épicas
- Validación de dependencias entre historias
- Estimación automática basada en patrones

---

## Resultados Esperados

Al completar esta kata:
- **Estructura organizada** de directorios por historia de usuario
- **Documentos consistentes** aplicando template establecido
- **Trazabilidad completa** desde imagen hasta documentación técnica
- **Nomenclatura unificada** siguiendo convenciones del proyecto
- **Base sólida** para fases posteriores de análisis e implementación

## Principios RaiSE Reforzados

*   **Documentation First**: Conversión sistemática de visual a documentación estructurada
*   **Consistent Standards**: Aplicación uniforme de convenciones y templates
*   **Human-AI Collaboration**: Orquestador valida interpretación, IA ejecuta procesamiento
*   **Iterative Refinement**: Procesamiento controlado con validación en cada historia
*   **Explicit Methodology**: Proceso replicable y sistemático para extracción de backlog 