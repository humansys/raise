# RaiSE Kata: Feature YAML Extraction from Backlog Images (L1-11)

**ID**: L1-11
**Nombre**: Feature YAML Extraction from Backlog Images
**Descripción**: Extrae sistemáticamente información de backlogs presentados en imágenes y la estructura en formato YAML rico, separando datos extraídos de propuestas técnicas que requieren validación posterior.
**Objetivo**:
    *   Convertir backlogs visuales a formato YAML estructurado y parseable
    *   Separar claramente información extraída vs. propuestas técnicas draft
    *   Generar artifact rico en metadatos para alimentar katas de diseño posteriores
    *   Marcar explícitamente elementos que requieren validación vs. ecosistema existente
    *   Crear base sólida para análisis de ecosistema y diseño técnico
**Dependencias**:
    *   `L0-03: Meta-Kata del Protocolo de Ejecución y Colaboración`
    *   Imagen(es) del backlog con especificaciones de historias de usuario
    *   Feature identificado para extracción (ej: F01-Producto)
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas de documentación y estructuración de proyectos

---

## Contexto y Principios

Esta kata se enfoca EXCLUSIVAMENTE en la extracción y estructuración de información, SIN tomar decisiones técnicas definitivas. Actúa como el primer paso en un pipeline de análisis que posteriormente puede alimentar katas de diseño como L1-09.

**Principios Fundamentales:**
*   **Extraction-Only Focus**: Solo extraer información visible en la imagen
*   **Explicit Separation**: Distinguir claramente entre datos extraídos y campos desconocidos
*   **Rich Metadata**: Generar YAML con contexto suficiente para análisis posterior
*   **Unknown Markers**: Dejar vacíos o marcar como "UNKNOWN" elementos que no se pueden extraer
*   **Ecosystem Agnostic**: No hacer asunciones sobre servicios o arquitectura existente

---

## Pre-condiciones

- Se tiene acceso a imagen(s) del backlog con historias de usuario claramente identificables
- El feature objetivo está identificado (ej: F01-Producto, F02-Pedidos, etc.)
- El directorio de destino está definido (ej: `docs/backlog/extracted/`)

---

## Fases del Protocolo de Ejecución

### **Fase 1: Análisis Sistemático de Imagen**

#### **Paso 1.1: Identificación de Estructura y Metadatos**

**Instrucción (Orquestador):** 
```
"Analiza la imagen del backlog '[IMAGEN_PATH]' para el feature '[FEATURE_ID]' y crea el documento de tracking inicial en '.raise/docs/kata-sessions/YYYY-MM-DD_L1-11-Extraction-[FEATURE_ID].md'"
```

**Acción (Agente IA):**
1. **Crear documento de tracking** con estructura:
   ```markdown
   # Kata L1-11: Feature YAML Extraction from Images
   ## Feature: [FEATURE_ID]
   ## Fecha: [YYYY-MM-DD]
   
   ### Plan de Implementación
   - [ ] Análisis de estructura de imagen
   - [ ] Extracción sistemática de historias
   - [ ] Generación de YAML estructurado
   - [ ] Validación de completitud
   - [ ] Documentación de gaps identificados
   
   ### Metadatos de Extracción
   - **Imagen fuente**: [IMAGEN_PATH]
   - **Feature objetivo**: [FEATURE_ID]
   - **Estructura identificada**: [A completar]
   - **Historias extraídas**: [Contador]
   
   ### Decisiones de Estructuración
   [Decisiones tomadas durante la extracción]
   ```

2. **Analizar estructura de la imagen**:
   - Identificar columnas/campos disponibles (ID, Requerimiento, Módulo, Actor, etc.)
   - Detectar nivel de detalle en reglas de negocio
   - Evaluar calidad y completitud de información visible

#### **Paso 1.2: Extracción Sistemática de Historias**

**Instrucción (Orquestador):** 
```
"Extrae sistemáticamente TODAS las historias visibles en la imagen para el feature especificado, organizando la información en estructura preliminar."
```

**Acción (Agente IA):**
1. **Extraer información fila por fila**:
   - Mapear cada columna a campos estructurados
   - Preservar texto exacto de la imagen (no interpretar)
   - Identificar información faltante o ambigua

2. **Crear estructura preliminar**:
   ```yaml
   preliminary_extraction:
     - id: "HU-XXX"
       raw_data:
         requirement: "[Extraído exacto]"
         module: "[Extraído exacto]"
         actor: "[Extraído exacto]"
         action: "[Extraído exacto]"
         benefit: "[Extraído exacto]"
         business_rules: "[Extraído exacto]"
       gaps_identified:
         - "Falta información de prioridad"
         - "Criterios de aceptación no especificados"
   ```

**Criterios de Aceptación Fase 1:**
- Lista completa de historias del feature extraídas
- Información preservada exactamente como aparece en imagen
- Gaps y ambigüedades identificados explícitamente
- Estructura preliminar validada

---

### **Fase 2: Estructuración YAML Rica**

#### **Paso 2.1: Generación de YAML Base con Metadatos**

**Instrucción (Orquestador):** 
```
"Genera el archivo YAML base con toda la información extraída y metadatos de trazabilidad. Archivo destino: 'docs/backlog/extracted/[FEATURE_ID].yaml'"
```

**Acción (Agente IA):**
1. **Crear estructura YAML completa**:
   ```yaml
   # Metadatos de extracción
   extraction_metadata:
     source_image: "[IMAGEN_PATH]"
     extraction_date: "[YYYY-MM-DD]"
     extraction_kata: "L1-11"
     extractor_version: "1.0"
     status: "EXTRACTED"
     
   # Información del feature
   feature:
     id: "[FEATURE_ID]"
     name: ""  # Dejar vacío si no está explícito en la imagen
     module: "[Extraído de imagen]"
     description: ""  # Dejar vacío si no está explícito en la imagen
     validation_needed:
       - "Definir nombre oficial del feature"
       - "Definir descripción basada en especificaciones completas"
   
   # Historias extraídas
   user_stories:
     - id: "[HU-XXX]"
       title: "[Título basado en acción principal]"
       
       # Datos directamente extraídos de imagen
       extracted_data:
         requirement_id: "[Extraído exacto]"
         module: "[Extraído exacto]"
         actor: "[Extraído exacto]"
         action: "[Extraído exacto]"
         benefit: "[Extraído exacto]"
         business_rules: |
           [Texto exacto de reglas/requisitos de la imagen]
         
       # Información técnica (dejar vacío lo que no se puede extraer)
       technical_info:
         acceptance_criteria: []  # Dejar vacío - no disponible en imagen típica
         
         components: []  # Dejar vacío - requiere análisis técnico
         
         api_endpoints: []  # Dejar vacío - requiere diseño de API
         
         data_model:
           entities: []  # Dejar vacío - requiere análisis de dominio
         
         estimation:
           story_points: "UNKNOWN"
           complexity_factors: []
         
         dependencies:
           internal_dependencies: []
           external_dependencies: []
   ```

#### **Paso 2.2: Enriquecimiento con Propuestas Draft**

**Instrucción (Orquestador):** 
```
"Para cada historia extraída, genera propuestas técnicas preliminares marcadas como DRAFT, basándote únicamente en la información disponible."
```

**Acción (Agente IA):**
1. **Dejar campos técnicos vacíos**:
   - No inferir criterios de aceptación (dejar array vacío)
   - No proponer componentes técnicos específicos
   - No sugerir arquitectura o endpoints

2. **Enfocar en información extraíble**:
   - Solo completar lo que está explícitamente visible en la imagen
   - Preservar reglas de negocio tal como aparecen
   - Mantener estructura del template pero con campos vacíos para lo desconocido

3. **Documentar limitaciones**:
   - Identificar qué información falta para completar el diseño
   - Listar áreas que requieren análisis técnico posterior
   - Mantener trazabilidad de qué se extrajo vs. qué falta

#### **Paso 2.3: Identificación de Gaps y Validaciones Necesarias**

**Instrucción (Orquestador):** 
```
"Identifica y documenta explícitamente todos los gaps de información y validaciones que se requerirán en fases posteriores."
```

**Acción (Agente IA):**
1. **Documentar gaps de información**:
   ```yaml
   extraction_gaps:
     missing_information:
       - "Criterios de aceptación específicos no definidos en imagen"
       - "Prioridades de historias no especificadas"
       - "Dependencias entre historias no clarificadas"
       
     ambiguous_information:
       - "Regla 'Confirmar con JAFRA' requiere clarificación"
       - "Término 'Veliz' necesita definición del dominio"
       
     validation_required:
       - "Validar propuestas técnicas vs. servicios existentes (L1-09)"
       - "Confirmar estimaciones con equipo técnico"
       - "Validar criterios de aceptación con stakeholders"
   ```

**Criterios de Aceptación Fase 2:**
- YAML completo generado con estructura rica
- Separación clara entre datos extraídos y campos vacíos/UNKNOWN
- Información técnica no extraíble dejada vacía explícitamente
- Gaps y áreas técnicas pendientes documentadas

---

### **Fase 3: Validación y Finalización**

#### **Paso 3.1: Verificación de Completitud**

**Instrucción (Orquestador):** 
```
"Verifica que todas las historias de la imagen han sido procesadas y que el YAML generado es completo y consistente."
```

**Acción (Agente IA):**
1. **Verificar completitud de extracción**:
   - Contar historias en imagen vs. historias en YAML
   - Verificar que no se perdió información visible
   - Confirmar consistencia en nomenclatura

2. **Validar estructura YAML**:
   ```bash
   # Verificar que el YAML es válido
   yaml-lint docs/backlog/extracted/[FEATURE_ID].yaml
   ```

3. **Generar métricas de extracción**:
   ```yaml
   extraction_metrics:
     total_stories_in_image: "[número]"
     stories_extracted: "[número]"
     completeness_percentage: "100%"
     draft_elements_count: "[número]"
     validation_items_count: "[número]"
   ```

#### **Paso 3.2: Documentación de Próximos Pasos**

**Instrucción (Orquestador):** 
```
"Documenta los próximos pasos recomendados y cómo este YAML puede alimentar otras katas del ecosistema RaiSE."
```

**Acción (Agente IA):**
1. **Generar recomendaciones de flujo**:
   ```yaml
   recommended_next_steps:
     immediate:
       - action: "Ejecutar L1-09 Ecosystem Discovery"
         input: "docs/backlog/extracted/[FEATURE_ID].yaml"
         purpose: "Validar propuestas vs. servicios existentes"
         
       - action: "Stakeholder validation session"
         focus: "Criterios de aceptación y reglas de negocio"
         validation_items: "[Lista de items marcados para validación]"
     
     subsequent:
       - "Refinamiento técnico basado en análisis de ecosistema"
       - "Estimación definitiva post-validación"
       - "Planificación de implementación"
   ```

2. **Actualizar documento de tracking**:
   ```markdown
   ## Estado Final
   - ✅ Extracción completada al 100%
   - ✅ YAML estructurado generado
   - ✅ Gaps identificados y documentados
   - ✅ Próximos pasos definidos
   
   ## Entregables
   - `docs/backlog/extracted/[FEATURE_ID].yaml` - YAML completo del feature
   - Lista de validaciones requeridas
   - Recomendaciones para próximos pasos
   ```

**Post-condiciones:**
- YAML completo y estructurado generado
- Separación clara entre información extraída y campos vacíos/UNKNOWN
- Gaps y áreas técnicas pendientes documentadas para fases posteriores
- Base sólida para análisis de ecosistema y diseño técnico

---

## Especificaciones Técnicas Detalladas

### **Estructura YAML Mandatoria**

#### **Sección extraction_metadata:**
```yaml
extraction_metadata:
  source_image: "ruta/a/imagen.png"           # REQUERIDO
  extraction_date: "YYYY-MM-DD"              # REQUERIDO
  extraction_kata: "L1-11"                   # REQUERIDO
  extractor_version: "1.0"                   # REQUERIDO
  status: "EXTRACTED"                        # REQUERIDO: EXTRACTED|VALIDATED|DESIGNED
```

#### **Sección feature:**
```yaml
feature:
  id: "F0X-FeatureName"                      # REQUERIDO
  name: ""                                   # Vacío si no está en imagen
  module: "[Extraído de imagen]"             # REQUERIDO si disponible
  description: ""                            # Vacío si no está en imagen
  validation_needed: []                      # REQUERIDO: lista de validaciones
```

#### **Sección user_stories (por historia):**
```yaml
user_stories:
  - id: "HU-XXX"                            # REQUERIDO
    title: "[Título basado en acción]"      # REQUERIDO
    
    extracted_data:                         # REQUERIDO: datos directos de imagen
      requirement_id: "[ID exacto]"
      module: "[Módulo exacto]"
      actor: "[Actor exacto]"
      action: "[Acción exacta]"
      benefit: "[Beneficio exacto]"
      business_rules: "[Reglas exactas]"
      
    technical_info:                         # REQUERIDO: información técnica
      acceptance_criteria: []               # Vacío - no extraíble de imagen
      components: []                        # Vacío - requiere análisis técnico
      api_endpoints: []                     # Vacío - requiere diseño
      estimation:                           
        story_points: "UNKNOWN"             # UNKNOWN si no especificado
        complexity_factors: []
      
      # OPCIONAL:
      data_model:
        entities: []
      dependencies:
        internal_dependencies: []
        external_dependencies: []
```

### **Convenciones de Nomenclatura**

#### **Archivos de Salida:**
```
Patrón: docs/backlog/extracted/[FEATURE_ID].yaml
Ejemplo: docs/backlog/extracted/F01-Producto.yaml
Reglas:
- Un archivo por feature
- Nombre debe coincidir con feature.id
- Extensión .yaml (no .yml)
```

#### **Marcadores de Estado:**
```
- ""                        # Campo vacío para información no disponible
- "UNKNOWN"                 # Para valores que requieren definición posterior
- "[Extraído exacto]"       # Para contenido literal de imagen
- "validation_needed"       # Para items que requieren validación
```

---

## Resultados Esperados

Al completar esta kata:
- **YAML Estructurado**: Archivo rico y parseable con toda la información extraída
- **Separación Clara**: Distinción explícita entre datos extraídos y campos vacíos/UNKNOWN
- **Trazabilidad Completa**: Metadatos que permiten auditar la extracción
- **Base para Análisis**: Artifact listo para alimentar katas de diseño y validación
- **Gaps Identificados**: Lista clara de información faltante o que requiere definición

## Principios RaiSE Reforzados

*   **Extraction-First Approach**: Datos limpios antes que interpretación
*   **Explicit Separation**: Hechos vs. campos desconocidos claramente distinguidos  
*   **Rich Metadata**: Información suficiente para análisis posterior
*   **Clean Templates**: Estructura completa con campos vacíos para información no extraíble
*   **Pipeline Integration**: Artifact optimizado para alimentar otras katas 