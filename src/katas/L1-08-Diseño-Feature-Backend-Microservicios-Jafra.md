# RaiSE Kata: Diseño de Feature Backend para Microservicios Jafra (L1-08)

**ID**: L1-08
**Nombre**: Diseño de Feature Backend para Infraestructura de Microservicios Jafra
**Descripción**: Guía el proceso completo de diseño de un nuevo feature backend que maximiza el reuso de servicios existentes, minimiza cambios en la infraestructura, y aplica principios KISS, DRY, YAGNI con análisis sistemático del ecosistema.
**Objetivo**:
    *   Diseñar features backend que aprovechen al máximo la infraestructura existente
    *   Aplicar sistemáticamente principios KISS, DRY, YAGNI en el diseño arquitectónico
    *   Minimizar el impacto en servicios existentes (modificaciones mínimas viables)
    *   Generar un diseño técnico detallado con estrategia de implementación clara
    *   Establecer contratos API-first que preserven compatibilidad backward
**Dependencias**:
    *   `L0-03: Meta-Kata del Protocolo de Ejecución y Colaboración`
    *   `L1-07: Generación de Documentación Esencial desde Código Fuente` (documentación esencial disponible)
    *   Feature requirements definidos (épica, HUs, criterios de aceptación)
    *   Acceso a workspace con múltiples repositorios de microservicios
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas de Clean Architecture y CQRS
    *   Reglas de diseño de contratos gRPC/REST

---

## Contexto y Principios Fundamentales

Esta kata implementa un **proceso híbrido** que combina:
- **Marco Teórico**: DDD, Clean Architecture, CQRS, API-First Design
- **Proceso Práctico**: Service Discovery, Impact Analysis, Contract-First Implementation
- **Principios de Diseño**: KISS (Keep It Simple), DRY (Don't Repeat Yourself), YAGNI (You Aren't Gonna Need It)

**Filosofía Central**: **"Maximizar Reuso, Minimizar Cambio, Preservar Simplicidad"**

### **Principios Rectores**
1. **KISS**: Preferir soluciones simples que extienden capacidades existentes
2. **DRY**: Reutilizar servicios y endpoints antes que duplicar funcionalidad  
3. **YAGNI**: Implementar solo lo estrictamente necesario para el feature actual
4. **Minimal Viable Changes**: Cambios mínimos que cumplan requerimientos
5. **Contract Preservation**: Mantener compatibilidad de contratos existentes

---

## Pasos del Kata

### **Paso 0: Preparación y Tracking de Sesión**

**Instrucción (Orquestador):** 
```
"Ejecuta el diseño del feature '[FEATURE_NAME]' según los requerimientos en '[REQUIREMENTS_PATH]'. 
Crea el documento de tracking en '.raise/docs/kata-sessions/YYYY-MM-DD_L1-08-Execution-[FEATURE_NAME].md'"
```

**Acción (Agente IA):**
1. **Crear documento de tracking** con secciones:
   - Plan de Implementación (checklist)
   - Análisis de Requerimientos
   - Mapeo de Servicios Existentes
   - Decisiones de Diseño
   - Estrategia de Implementación
2. **Leer y resumir requerimientos** del feature
3. **Presentar plan detallado** para aprobación del Orquestador

---

## **FASE 1: ECOSYSTEM DISCOVERY & REQUIREMENTS ANALYSIS**

### **Paso 1: Bounded Context Analysis (DDD)**

**Instrucción (Orquestador):** 
```
"Identifica el bounded context del feature y mapea servicios existentes relevantes."
```

**Acción (Agente IA):**
- **Analizar documentación esencial**: Leer `docs/essential/*/services-map.yaml`
- **Identificar bounded contexts**:
  ```yaml
  feature_context:
    domain: "[Domain Area - ej: User Management, Financial Operations]"
    primary_concepts: ["[Concept1]", "[Concept2]"]
    related_contexts: ["[Context1]", "[Context2]"]
    
  existing_services:
    direct_match: ["[Service que maneja concepto directamente]"]
    partial_match: ["[Service con capacidades relacionadas]"]
    supporting: ["[Services de soporte/infraestructura]"]
  ```

### **Paso 2: Capability Mapping & Overlap Analysis**

**Instrucción (Orquestador):** 
```
"Mapea capacidades existentes que pueden ser reutilizadas para el feature."
```

**Acción (Agente IA):**
- **Extraer capacidades** de `inter-service-contracts.yaml`:
  ```yaml
  capability_analysis:
    required_for_feature:
      - capability: "[Required Capability]"
        existing_service: "[Service]"
        coverage: "[0-100%]"
        gap: "[What's missing]"
        reuse_strategy: "[extend|compose|new]"
        
    functional_overlaps:
      - overlap: "[Overlapping functionality]"
        services: ["[Service1]", "[Service2]"]
        risk: "[CRITICAL|HIGH|MEDIUM|LOW]"
        resolution: "[Strategy to avoid duplication]"
  ```

### **Paso 3: KISS/DRY/YAGNI Constraints Identification**

**Instrucción (Orquestador):** 
```
"Identifica constraints de simplicidad y oportunidades de reutilización."
```

**Acción (Agente IA):**
- **Aplicar filtros de simplicidad**:
  ```yaml
  design_constraints:
    kiss_principle:
      - "Prefer extending [ExistingService] over creating new service"
      - "Use existing [DataModel] instead of new entity"
      
    dry_principle:
      - "Reuse [ExistingEndpoint] for [Functionality]"
      - "Leverage [SharedLibrary] for [CommonOperation]"
      
    yagni_principle:
      - "Implement only [CoreRequirement], defer [FutureFeature]"
      - "Use simple [Pattern] over complex [AlternativePattern]"
  ```

---

## **FASE 2: DESIGN OPTIONS & DECISION MAKING**

### **Paso 4: Generate Design Options (Minimum 3)**

**Instrucción (Orquestador):** 
```
"Genera 3 opciones de diseño priorizando reuso y simplicidad."
```

**Acción (Agente IA):**
- **Opción A - Maximum Reuse**: Extender servicios existentes
- **Opción B - Minimal New Service**: Nuevo servicio mínimo + orquestación  
- **Opción C - Hybrid Approach**: Combinación estratégica

Para cada opción:
```yaml
option_a_maximum_reuse:
  approach: "Extend [ExistingService] with new operations"
  changes:
    - service: "[ServiceName]"
      modification: "[Specific change]"
      risk: "[LOW|MEDIUM|HIGH]"
      effort: "[1-5]"
  
  kiss_score: "[1-10] - Simplicity assessment"
  dry_score: "[1-10] - Reuse level"
  yagni_score: "[1-10] - Minimalism"
  
  pros:
    - "Leverages existing [Capability]"
    - "Minimal infrastructure changes"
  cons:
    - "Increases complexity of [ExistingService]"
    - "Potential coupling with [ExistingFeature]"
```

### **Paso 5: Service Interaction Design (Clean Architecture)**

**Instrucción (Orquestador):** 
```
"Para la opción seleccionada, diseña las interacciones siguiendo Clean Architecture."
```

**Acción (Agente IA):**
- **Mapear capas de Clean Architecture**:
  ```mermaid
  graph TB
      A[Presentation Layer] --> B[Application Layer]
      B --> C[Domain Layer] 
      B --> D[Infrastructure Layer]
      
      subgraph "New Feature"
          E[FeatureController] --> F[FeatureUseCase]
          F --> G[FeatureEntity]
          F --> H[ExistingServiceClient]
      end
  ```

- **Definir responsabilidades por capa**:
  ```yaml
  layer_design:
    presentation:
      new_components: ["[FeatureController]"]
      modifications: ["Extend [ExistingController]"]
      
    application:
      new_use_cases: ["[CreateFeatureUseCase]"]
      reused_services: ["[ExistingApplicationService]"]
      
    domain:
      new_entities: ["[FeatureEntity]"] 
      extended_entities: ["[ExistingEntity with new properties]"]
      
    infrastructure:
      new_repositories: ["[FeatureRepository]"]
      reused_clients: ["[ExistingServiceClient]"]
  ```

### **Paso 6: Contract-First API Design**

**Instrucción (Orquestador):** 
```
"Diseña los contratos API preservando compatibilidad con servicios existentes."
```

**Acción (Agente IA):**
- **Diseñar contratos nuevos**:
  ```protobuf
  // NEW CONTRACTS
  service FeatureService {
    // New operations
    rpc CreateFeature(CreateFeatureRequest) returns (CreateFeatureResponse);
    rpc GetFeatureStatus(GetFeatureStatusRequest) returns (GetFeatureStatusResponse);
  }
  
  message CreateFeatureRequest {
    string feature_id = 1;
    FeatureDetails details = 2;
    // Reuse existing types where possible
    UserInfo user = 3; // From existing UserService contracts
  }
  ```

- **Extensiones de contratos existentes**:
  ```protobuf
  // EXTENSIONS TO EXISTING CONTRACTS
  service ExistingService {
    // Existing operations (unchanged)
    rpc ExistingOperation(ExistingRequest) returns (ExistingResponse);
    
    // New operations (backward compatible)
    rpc FeatureRelatedOperation(FeatureRequest) returns (FeatureResponse);
  }
  ```

---

## **FASE 3: DETAILED TECHNICAL DESIGN**

### **Paso 7: CQRS Command/Query Design**

**Instrucción (Orquestador):** 
```
"Diseña los commands y queries siguiendo CQRS, reutilizando handlers existentes donde sea posible."
```

**Acción (Agente IA):**
- **Commands (acciones de escritura)**:
  ```csharp
  // NEW COMMANDS
  public class CreateFeatureCommand : IRequest<CreateFeatureResponse>
  {
      public string FeatureId { get; set; }
      public FeatureDetails Details { get; set; }
      // Reuse existing value objects
      public UserId CreatedBy { get; set; } // From existing User domain
  }
  
  // REUSE EXISTING
  // Leverage existing UpdateUserCommand for user-related changes
  ```

- **Queries (acciones de lectura)**:
  ```csharp
  // NEW QUERIES  
  public class GetFeatureStatusQuery : IRequest<FeatureStatusResponse>
  {
      public string FeatureId { get; set; }
  }
  
  // COMPOSE EXISTING
  // Combine results from existing GetUserQuery + GetSettingsQuery
  ```

### **Paso 8: Event-Driven Integration Design**

**Instrucción (Orquestador):** 
```
"Diseña la integración entre servicios usando eventos, minimizando acoplamiento."
```

**Acción (Agente IA):**
- **Eventos de dominio**:
  ```yaml
  domain_events:
    new_events:
      - event: "FeatureCreated"
        payload: 
          feature_id: "string"
          created_by: "UserId"
          created_at: "timestamp"
        subscribers: ["NotificationService", "AuditService"]
        
    reused_events:
      - event: "UserUpdated" # Existing event
        new_subscriber: "FeatureService" # New subscriber
        purpose: "Update feature permissions on user changes"
  ```

### **Paso 9: Data Model & Persistence Strategy**

**Instrucción (Orquestador):** 
```
"Diseña el modelo de datos minimizando nuevas entidades y aprovechando estructuras existentes."
```

**Acción (Agente IA):**
- **Estrategia de persistencia**:
  ```yaml
  data_strategy:
    new_entities:
      - entity: "Feature"
        properties: ["Id", "Name", "Status", "CreatedBy", "CreatedAt"]
        persistence: "New table in [ExistingDatabase]"
        
    extended_entities:
      - entity: "User" # Existing entity
        new_properties: ["PreferredFeatures", "FeaturePermissions"]
        migration_strategy: "Add columns to existing User table"
        
    shared_entities:
      - entity: "Address" # Reuse existing
        usage: "Reference existing Address entity for feature locations"
  ```

---

## **FASE 4: IMPLEMENTATION STRATEGY & VALIDATION**

### **Paso 10: Minimal Viable Changes Plan**

**Instrucción (Orquestador):** 
```
"Genera el plan de cambios mínimos viables priorizados por impacto."
```

**Acción (Agente IA):**
- **Categorizar cambios por impacto**:
  ```yaml
  implementation_plan:
    zero_impact: # No breaking changes
      - "Add new FeatureController endpoints"
      - "Create new FeatureService with own database table"
      - "Add new event handlers for FeatureCreated"
      
    low_impact: # Additive changes
      - "Extend UserService with feature-related queries"
      - "Add new columns to User table"
      - "Subscribe FeatureService to existing UserUpdated events"
      
    medium_impact: # Require coordination
      - "Update AuthenticationService to include feature permissions"
      - "Modify existing user creation flow to initialize feature preferences"
      
    high_impact: # Require careful migration
      - "Update existing API contracts with new optional fields"
      - "Modify core user authentication to check feature access"
  ```

### **Paso 11: Testing Strategy for Reused Components**

**Instrucción (Orquestador):** 
```
"Diseña estrategia de testing que valide tanto funcionalidad nueva como preservación de existente."
```

**Acción (Agente IA):**
- **Testing por categoría de cambio**:
  ```yaml
  testing_strategy:
    new_functionality:
      - "Unit tests for new FeatureService operations"
      - "Integration tests for FeatureController endpoints"
      - "Contract tests for new gRPC operations"
      
    extended_functionality:
      - "Regression tests for existing UserService operations"
      - "Integration tests for UserService + FeatureService interactions"
      - "Performance tests to ensure no degradation"
      
    preserved_functionality:
      - "Run existing test suites on modified services"
      - "Contract compatibility tests for extended APIs"
      - "End-to-end tests for existing user flows"
  ```

### **Paso 12: Deployment & Rollback Strategy**

**Instrucción (Orquestador):** 
```
"Diseña estrategia de deployment que minimice riesgos en servicios existentes."
```

**Acción (Agente IA):**
- **Fases de deployment**:
  ```yaml
  deployment_phases:
    phase_1_foundation:
      - "Deploy FeatureService (isolated, no external dependencies)"
      - "Deploy database schema changes"
      - "Verify basic functionality"
      
    phase_2_integration:
      - "Deploy UserService extensions (backward compatible)"
      - "Enable event subscription from FeatureService"
      - "Validate integration without user impact"
      
    phase_3_activation:
      - "Deploy frontend changes"
      - "Enable feature for limited user group"
      - "Monitor system health and performance"
      
    rollback_triggers:
      - "Error rate in any existing service > 1%"
      - "Response time degradation > 10% in core operations"
      - "Database connection pool exhaustion"
  ```

---

## **FASE 5: DOCUMENTATION & HANDOFF**

### **Paso 13: Technical Design Document Generation**

**Instrucción (Orquestador):** 
```
"Genera el documento de diseño técnico completo para implementación."
```

**Acción (Agente IA):**
- **Estructura del documento**:
  ```markdown
  # Technical Design: [FEATURE_NAME]
  
  ## 1. Executive Summary
  - Feature purpose and business value
  - Selected design option and rationale
  - KISS/DRY/YAGNI compliance summary
  
  ## 2. Architecture Overview
  - Service interaction diagram
  - Clean Architecture layer mappings
  - Integration points with existing services
  
  ## 3. Implementation Details
  - New components specification
  - Extended components changes
  - API contracts and gRPC definitions
  
  ## 4. Data Design
  - Entity models and relationships
  - Database schema changes
  - Migration strategy
  
  ## 5. Implementation Plan
  - Phased deployment strategy
  - Testing approach
  - Rollback procedures
  
  ## 6. Appendices
  - Service capability matrix
  - Impact assessment
  - Performance considerations
  ```

### **Paso 14: Code Generation Guidelines**

**Instrucción (Orquestador):** 
```
"Genera guidelines específicas para la implementación que preserven los principios aplicados."
```

**Acción (Agente IA):**
- **Guidelines para desarrolladores**:
  ```yaml
  implementation_guidelines:
    reuse_patterns:
      - "Always inject existing [IUserService] instead of creating new user operations"
      - "Use existing [AddressDto] for location-related data"
      - "Leverage [CommonValidationLibrary] for input validation"
      
    kiss_patterns:
      - "Prefer simple JSON responses over complex nested objects"
      - "Use existing enum types instead of creating new ones"
      - "Implement straightforward CRUD operations before optimization"
      
    dry_patterns:
      - "Extract common feature logic to [FeatureHelpers] utility class"
      - "Reuse existing [ResponseWrapper] for consistent API responses"
      - "Share [FeatureConstants] across all feature-related components"
      
    yagni_patterns:
      - "Implement only required feature status states: [Active, Inactive]"
      - "Skip advanced search functionality until requested"
      - "Use simple database relationships without performance optimization"
  ```

---

## **Resultados Esperados**

Al completar esta kata:
- **Diseño técnico optimizado** que maximiza reuso de infraestructura existente
- **Plan de implementación pragmático** con minimal viable changes
- **Contratos API-first** que preservan compatibility
- **Estrategia de testing** que valida nuevo y existente functionality
- **Documentation completa** para guiar implementation y maintenance
- **Adherencia comprobada** a principios KISS, DRY, YAGNI

## **Principios RaiSE Reforzados**

*   **Design First & Documentation First**: Diseño técnico precede implementación
*   **Minimalism & Pragmatism**: Solo lo necesario, del modo más simple posible
*   **Reuse & Composition**: Leveraging existing infrastructure over creation
*   **Clean Architecture**: Proper layering and dependency management
*   **Contract-First Development**: API design antes que implementation
*   **Human-AI Collaboration**: Orquestador guía strategy, Agente ejecuta analysis
*   **Incremental & Safe Changes**: Phased deployment with rollback capabilities