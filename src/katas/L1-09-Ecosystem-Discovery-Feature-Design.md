# RaiSE Kata: Ecosystem Discovery & Zero-Duplication Feature Design (L1-09)

**ID**: L1-09
**Nombre**: Ecosystem Discovery & Zero-Duplication Feature Design for Microservices
**Descripción**: Realiza análisis exhaustivo del ecosistema de microservicios existente para prevenir duplicación funcional y maximizar reutilización al diseñar nuevos features.
**Objetivo**:
    *   Mapear comprehensivamente el ecosistema de servicios existente antes de cualquier diseño
    *   Detectar automáticamente overlaps funcionales para prevenir duplicación
    *   Generar análisis de impacto granular por servicio con estimaciones precisas
    *   Garantizar coherencia arquitectónica y patrones consistentes en el ecosistema
    *   Producir documentación de diseño que demuestre 0% duplicación funcional
**Dependencias**:
    *   `L1-07: Generación de Documentación Esencial desde Código Fuente` (documentación esencial debe existir)
    *   `L0-03: Meta-Kata del Protocolo de Ejecución y Colaboración`
    *   Feature requirements definidos con historias de usuario
    *   Acceso a documentación esencial de todos los microservicios del ecosistema
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas de DRY, KISS, YAGNI enforcement
    *   Reglas de zero-duplication validation

---

## **META-PRINCIPIO FUNDAMENTAL**

**"ECOSYSTEM-FIRST DESIGN"**: Antes de diseñar CUALQUIER feature nuevo, se debe demostrar comprensión completa del ecosistema existente y justificar por qué no se puede implementar mediante extensión/reutilización de servicios existentes.

### **Principios de Zero-Duplication**
1. **Comprehensive Discovery**: Mapear 100% de servicios relevantes antes de diseñar
2. **Overlap Detection**: Identificar automáticamente duplicación funcional ≥50%
3. **Reuse Mandate**: La Opción A siempre debe ser máxima reutilización (≥80%)
4. **Architecture Continuity**: Validar que cambios mantengan patrones existentes
5. **Evidence-Based Design**: Cada decisión respaldada por análisis del ecosistema

---

## **FASE 0: COMPREHENSIVE ECOSYSTEM DISCOVERY**

### **Paso 0.1: Exhaustive Service Inventory**

**Instrucción (Orquestador):** 
```
"Realiza inventario exhaustivo de TODOS los microservicios del ecosistema analizando su documentación esencial. 
Para el feature '[FEATURE_NAME]', genera capability-matrix.yaml que mapee capacidades existentes vs requerimientos."
```

**Acción (Agente IA):**
1. **Escanear documentación esencial completa**:
   - Leer TODOS los `docs/essential/*/service-overview.md` disponibles
   - Extraer entidades del dominio, operaciones gRPC, endpoints REST
   - Identificar bounded contexts y capacidades de negocio de cada servicio

2. **Mapear requerimientos a capacidades existentes**:
   ```yaml
   capability_matrix:
     user_registration:
       existing_services: ["registrations:95%", "authentication:100%"]
       gap: "Emprendedor-specific workflow (5%)"
       recommendation: "EXTEND registrations service"
       
     curp_validation:
       existing_services: ["profile:100%"]
       gap: "None"
       recommendation: "REUSE profile service - NO CHANGES"
   ```

**Entregable Crítico**: `capability-matrix.yaml` con cobertura 100% del ecosistema

### **Paso 0.2: Zero-Duplication Overlap Analysis**

**Instrucción (Orquestador):** 
```
"Detecta overlaps funcionales críticos (≥50%) y genera overlap-analysis.yaml con recomendaciones específicas para evitar duplicación."
```

**Acción (Agente IA):**
1. **Calcular semantic similarity entre requerimientos y capacidades existentes**
2. **Clasificar risk levels automáticamente**:
   - CRITICAL: ≥90% overlap → "REUSE - Do not create new"
   - HIGH: ≥70% overlap → "EXTEND - Modify existing" 
   - MEDIUM: ≥50% overlap → "EVALUATE - Consider options"

3. **Generar recomendaciones anti-duplication**:
   ```yaml
   recommendations:
     primary_action: "EXTEND existing services - do not create new"
     services_to_modify: ["registrations", "product"]
     services_zero_impact: ["profile", "authentication", "address-book", ...]
   ```

**Entregable Crítico**: `overlap-analysis.yaml` con validación de zero-duplication

### **Paso 0.3: Architecture Continuity Validation**

**Instrucción (Orquestador):** 
```
"Valida que cualquier cambio propuesto mantenga coherencia arquitectónica del ecosistema. 
Genera architecture-validation.yaml confirmando continuity."
```

**Acción (Agente IA):**
1. **Validar pattern consistency across services**
2. **Verificar contract compatibility (backward compatible extensions only)**
3. **Evaluar complexity impact (prefer minimal changes)**

**Entregable Crítico**: `architecture-validation.yaml` con score de continuity

---

## **FASE 1: GRANULAR IMPACT ASSESSMENT**

### **Paso 1.1: Service-Specific Impact Matrix Generation**

**Instrucción (Orquestador):** 
```
"Genera matriz detallada de impacto por cada servicio del ecosistema, incluyendo estimaciones precisas de esfuerzo y riesgo."
```

**Acción (Agente IA):**
1. **Analizar impacto granular por servicio**:
   ```yaml
   # Para cada uno de los 13 servicios:
   service_impact_matrix:
     registrations:
       impact_level: "HIGH"
       specific_changes:
         - "Add EmprendedorRegistrationWorkflow"
         - "Extend CreateApplicant with emprendedor type"
       effort_estimate: "3 weeks"
       risk_level: "MEDIUM"
       breaking_changes: false
       
     product:
       impact_level: "MEDIUM"  
       specific_changes:
         - "Add emprendedor kit configurations"
         - "Add GetEmprendedorKits operation"
       effort_estimate: "1 week"
       risk_level: "LOW"
       breaking_changes: false
       
     profile:
       impact_level: "ZERO"
       specific_changes: []
       effort_estimate: "0 weeks"
       justification: "CURP validation already complete"
   ```

2. **Generar executive summary**:
   ```yaml
   impact_summary:
     total_services_analyzed: 13
     high_impact_services: 1
     medium_impact_services: 1
     zero_impact_services: 11
     total_effort_estimate: "4 weeks"
     reuse_percentage: "85%"
   ```

**Entregable Crítico**: `impact-matrix.yaml` con assessment completo del ecosistema

### **Paso 1.2: Reuse-First Design Options Generation**

**Instrucción (Orquestador):** 
```
"Genera opciones de diseño priorizando máxima reutilización. La Opción A DEBE ser >80% reuse."
```

**Acción (Agente IA):**
1. **Opción A - Maximum Reuse (MANDATORIA)**:
   ```yaml
   option_a_maximum_reuse:
     approach: "Extend registrations + product services"
     reuse_percentage: 95%
     services_modified: 2
     services_new: 0
     development_time: "4 weeks"
     architecture_impact: "MINIMAL"
     
     justification:
       - "registrations service already handles 95% of registration workflow"
       - "product service already manages kit configurations"
       - "All other services (profile, authentication, etc.) require 0 changes"
   ```

2. **Opción B - New Service (DISCOURAGED)**:
   ```yaml
   option_b_new_service:
     approach: "Create new emprendedores service"
     reuse_percentage: 30%
     problems:
       - "95% functional duplication with registrations"
       - "Violates DRY principle severely"
       - "Creates maintenance burden"
     recommendation: "REJECT - Violates zero-duplication principle"
   ```

**Entregable Crítico**: Design options con Option A >= 80% reuse mandatorio

---

## **FASE 2: ZERO-DUPLICATION TECHNICAL DESIGN**

### **Paso 2.1: Minimal Viable Changes Design**

**Instrucción (Orquestador):** 
```
"Diseña cambios mínimos viables que cumplan requerimientos aprovechando máximamente la infraestructura existente."
```

**Acción (Agente IA):**
1. **Definir extension points específicos**:
   ```yaml
   minimal_changes:
     registrations_service:
       new_entities: ["EmprendedorApplication extends Applicant"]
       new_commands: ["CreateEmprendedorApplicationCommand"]
       new_workflows: ["EmprendedorRegistrationWorkflow"]
       reused_components: 
         - "Existing CURP validation (ProfileService)"
         - "Existing document upload (FilesService)"
         - "Existing payment processing (CreditService)"
   ```

2. **Mapear integration flows**:
   ```mermaid
   sequenceDiagram
       participant UI as Frontend
       participant REG as Registrations Service
       participant PROF as Profile Service (REUSED)
       participant ADDR as AddressBook Service (REUSED)
       participant FILES as Files Service (REUSED)
       participant CREDIT as Credit Service (REUSED)
       
       UI->>REG: CreateEmprendedorApplication (NEW)
       REG->>PROF: ValidateCURP (EXISTING)
       REG->>ADDR: ValidateAddress (EXISTING)
       REG->>FILES: CreateDocumentPlaceholders (EXISTING)
       REG->>CREDIT: SetupPaymentMethod (EXISTING)
   ```

### **Paso 2.2: Contract Extensions Design**

**Instrucción (Orquestador):** 
```
"Diseña extensiones de contratos que sean 100% backward compatible."
```

**Acción (Agente IA):**
1. **Extend existing contracts (backward compatible)**:
   ```protobuf
   // Extension to registrations_v1.proto
   service RegistrationsService {
     // Existing operations (unchanged)
     rpc CreateApplicant(CreateApplicantRequest) returns (CreateApplicantResponse);
     
     // New operations (additive only)
     rpc CreateEmprendedorApplication(CreateEmprendedorRequest) returns (CreateEmprendedorResponse);
   }
   
   message CreateEmprendedorRequest {
     string curp = 1;
     string email = 2;
     EmprendedorKitSelection kit_selection = 3;
     // Reuse existing AddressInfo from address-book service
     AddressInfo address = 4;
   }
   ```

---

## **FASE 3: ECOSYSTEM VALIDATION & DOCUMENTATION**

### **Paso 3.1: Zero-Duplication Evidence Generation**

**Instrucción (Orquestador):** 
```
"Genera evidencia documentada de que el diseño logra 0% duplicación funcional y máxima reutilización."
```

**Acción (Agente IA):**
1. **Evidence matrix**:
   ```yaml
   zero_duplication_evidence:
     user_creation: "REUSES authentication.AddUser - NO DUPLICATION"
     curp_validation: "REUSES profile.GetActiveUserByCURP - NO DUPLICATION"  
     address_management: "REUSES address-book.CreateAddress - NO DUPLICATION"
     document_upload: "REUSES files.CreateFile - NO DUPLICATION"
     payment_processing: "REUSES credit.ProcessPayment - NO DUPLICATION"
     
     new_functionality_only:
       - "EmprendedorRegistrationWorkflow (orchestration only)"
       - "EmprendedorKit configuration (data only)"
   ```

2. **Reuse metrics**:
   ```yaml
   reuse_metrics:
     total_functionality_required: "100%"
     functionality_reused: "95%"
     functionality_new: "5%"
     services_modified: "2 of 13 (15%)"
     services_unchanged: "11 of 13 (85%)"
   ```

### **Paso 3.2: Implementation Roadmap with Validation Gates**

**Instrucción (Orquestador):** 
```
"Genera roadmap de implementación con gates de validación que aseguren preservación de principios."
```

**Acción (Agente IA):**
1. **Implementation phases con validation**:
   ```yaml
   implementation_roadmap:
     phase_1_registrations_extension:
       duration: "3 weeks"
       deliverables: ["EmprendedorRegistrationWorkflow", "Extended gRPC contracts"]
       validation_gate: "0% functional duplication confirmed"
       
     phase_2_product_configuration:
       duration: "1 week"  
       deliverables: ["EmprendedorKit configurations", "GetEmprendedorKits operation"]
       validation_gate: "Architecture continuity maintained"
       
     validation_criteria:
       - "No new services created"
       - "All contracts backward compatible"
       - "≥95% functionality reused"
       - "No breaking changes detected"
   ```

---

## **VALIDATION GATES MANDATORIOS**

### **Gate 1: Ecosystem Discovery Complete**
- **Criterio**: capability-matrix.yaml cubre ≥90% servicios del ecosistema
- **Fallo**: Si analysis incompleto → STOP, completar discovery

### **Gate 2: Zero-Duplication Validated**  
- **Criterio**: overlap-analysis.yaml demuestra estrategia anti-duplicación
- **Fallo**: Si duplicación no addressed → STOP, revisar strategy

### **Gate 3: Maximum Reuse Confirmed**
- **Criterio**: Opción A debe tener ≥80% reuse percentage
- **Fallo**: Si reuse <80% → STOP, revisar options

### **Gate 4: Architecture Continuity Maintained**
- **Criterio**: architecture-validation.yaml = "APPROVED"
- **Fallo**: Si architecture compromised → STOP, redesign

---

## **Resultados Esperados**

Al completar esta kata:
- **Ecosystem Understanding**: Comprensión 100% del ecosistema existente  
- **Zero-Duplication Evidence**: Documentación de 0% duplicación funcional
- **Maximum Reuse Design**: ≥80% reutilización de infraestructura existente
- **Architecture Continuity**: Preservación de patrones y coherencia
- **Implementation Roadmap**: Plan detallado con validation gates

## **Principios RaiSE Reforzados**

*   **Ecosystem-First Design**: Comprehensive understanding before creation
*   **Zero-Duplication Mandate**: Evidence-based prevention of functional overlap  
*   **Maximum Reuse Principle**: Leveraging existing infrastructure over creation
*   **Architecture Continuity**: Preserving ecosystem coherence and patterns
*   **Evidence-Based Decision Making**: All choices backed by ecosystem analysis

**Esta kata TRANSFORMA el diseño de feature de reactivo a proactivo, garantizando coherencia ecosistémica y eliminando duplicación funcional.** 