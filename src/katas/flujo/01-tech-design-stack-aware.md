# RaiSE Kata: Diseño Técnico Stack-Aware y Ecosystem-Driven (L1-11)

**ID**: L1-11
**Nombre**: Diseño Técnico Stack-Aware para Zambezi Concierge Ecosystem
**Descripción**: Elabora diseños técnicos detallados aplicando las mejores prácticas del stack tecnológico específico (FastAPI/Laravel/PostgreSQL), maximizando reutilización del ecosistema existente y garantizando coherencia arquitectónica.
**Objetivo**:
    *   Generar diseños técnicos completos y precisos basados en el stack del proyecto
    *   Aplicar patrones arquitectónicos probados (Clean Architecture, Hexagonal, DDD)
    *   Maximizar reutilización de componentes existentes del ecosistema
    *   Garantizar backward compatibility y cero breaking changes no justificados
    *   Producir especificaciones técnicas implementables directamente
**Dependencias**:
    *   `L1-09: Ecosystem Discovery & Zero-Duplication Feature Design` (análisis del ecosistema)
    *   `L1-04: Generación de Plan de Implementación desde HU` (historias de usuario definidas)
    *   Acceso a capability-matrix.yaml y overlap-analysis.yaml del ecosistema
    *   Template de diseño técnico en `.raise/templates/tech/tech_design.md`
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas específicas del stack (virtualenv, security, testing)
    *   Patrones arquitectónicos del proyecto

---

## **META-PRINCIPIO FUNDAMENTAL**

**"STACK-AWARE & ECOSYSTEM-DRIVEN DESIGN"**: Todo diseño técnico debe aprovechar las capacidades específicas del stack tecnológico del proyecto y maximizar la reutilización de componentes existentes, aplicando patrones arquitectónicos consistentes con el ecosistema.

### **Principios de Diseño Técnico**
1. **Stack Mastery**: Conocimiento profundo de FastAPI, Laravel, PostgreSQL y patrones del ecosistema
2. **Reuse-First Architecture**: Diseñar extensiones sobre servicios existentes antes que crear nuevos
3. **Clean Boundaries**: Separación clara de responsabilidades (Presentation, Business, Data)
4. **Contract Stability**: Backward compatibility mandatoria - solo extensiones aditivas
5. **Implementation-Ready**: Especificaciones suficientemente detalladas para implementación directa
6. **Test-Driven Design**: Estrategia de testing integrada desde el diseño

---

## **FASE 0: ANÁLISIS DE CONTEXTO TÉCNICO**

### **Paso 0.1: Stack Technology Assessment**

**Instrucción (Orquestador):** 
```
"Analiza el stack tecnológico específico del proyecto y las capacidades técnicas disponibles para el feature '[FEATURE_NAME]'. 
Genera stack-assessment.yaml identificando componentes reutilizables."
```

**Acción (Agente IA):**
1. **Identificar stack components relevantes**:
   ```yaml
   stack_assessment:
     backend_python:
       framework: "FastAPI 0.115.12"
       database: "PostgreSQL (via SQLAlchemy)"
       testing: "pytest"
       migrations: "Alembic 1.15.2"
       security: "HTTPBearer (centralized in security.py)"
       available_patterns:
         - "Dependency Injection (FastAPI Depends)"
         - "Pydantic models para validation"
         - "Async/await patterns"
         
     admin_laravel:
       framework: "Laravel 11.x"
       admin_panel: "Filament 3.x"
       database: "PostgreSQL 17"
       testing: "PHPUnit/Pest"
       development: "DDEV"
       available_patterns:
         - "Eloquent ORM"
         - "Filament Resources y Forms"
         - "Artisan Commands"
         
     shared_infrastructure:
       database: "PostgreSQL"
       deployment: "DDEV (dev), Docker (prod)"
       version_control: "Git"
       ci_cd: "GitLab CI"
   ```

2. **Mapear requerimientos a capacidades del stack**:
   ```yaml
   feature_to_stack_mapping:
     api_authentication:
       component: "backend/api/security.py"
       pattern: "HTTPBearer with get_current_site dependency"
       reuse_level: "100% - usar dependency existente"
       
     database_entities:
       component: "backend/alembic/versions/"
       pattern: "SQLAlchemy models + Alembic migrations"
       reuse_level: "80% - extender modelos existentes"
       
     admin_interface:
       component: "admin/app/Filament/Resources/"
       pattern: "Filament Resource with Forms"
       reuse_level: "60% - crear nuevo resource basado en pattern"
   ```

**Entregable Crítico**: `stack-assessment.yaml` con mapping feature → stack capabilities

### **Paso 0.2: Ecosystem Component Discovery**

**Instrucción (Orquestador):** 
```
"Basándote en capability-matrix.yaml de L1-09, identifica componentes existentes que se reutilizarán 
y componentes que requerirán extensión para este diseño técnico."
```

**Acción (Agente IA):**
1. **Clasificar componentes por nivel de impacto**:
   ```yaml
   component_impact_analysis:
     zero_impact_reuse:
       - "backend/api/security.py::get_current_site"
       - "backend/api/security.py::raise_auth_error"
       - "admin DatabaseSeeder patterns"
       justification: "Reutilización directa sin modificaciones"
       
     extension_required:
       - component: "backend/api/models.py::SiteConfiguration"
         extension: "Add new fields for emprendedor config"
         backward_compatible: true
         migration_required: true
         
       - component: "admin/app/Filament/Resources/SiteResource.php"
         extension: "Add emprendedor kit form fields"
         backward_compatible: true
         migration_required: false
         
     new_components:
       - "backend/api/routers/emprendedor.py (new router)"
       - "admin/app/Filament/Resources/EmprendedorResource.php (new resource)"
       justification: "No existe componente equivalente - nueva funcionalidad"
   ```

**Entregable Crítico**: `component-impact.yaml` con clasificación de componentes

### **Paso 0.3: Architecture Pattern Selection**

**Instrucción (Orquestador):** 
```
"Define los patrones arquitectónicos específicos a aplicar, validando coherencia con la arquitectura 
existente del proyecto."
```

**Acción (Agente IA):**
1. **Seleccionar patrones por capa**:
   ```yaml
   architecture_patterns:
     backend_api:
       pattern: "Clean Architecture + Dependency Injection"
       layers:
         presentation: "FastAPI routers en api/routers/"
         business_logic: "Service layer (a crear si es complejo)"
         data_access: "SQLAlchemy models en api/models.py"
       validation: "Pydantic schemas para request/response"
       
     admin_panel:
       pattern: "MVC + Repository Pattern (Laravel)"
       layers:
         presentation: "Filament Resources (Forms + Tables)"
         business_logic: "Eloquent Models + Custom Actions"
         data_access: "Eloquent ORM"
       
     database_design:
       pattern: "Normalized relational design"
       migrations: "Alembic (backend) + Laravel migrations (admin)"
       indexes: "Strategy for query optimization"
       
     security:
       pattern: "Centralized authentication via HTTPBearer"
       implementation: "Reuse backend/api/security.py utilities"
       
     testing:
       backend: "pytest with fixtures"
       admin: "PHPUnit/Pest feature tests"
       e2e: "Manual testing guide approach"
   ```

**Entregable Crítico**: `architecture-patterns.yaml` con decisiones de diseño justificadas

---

## **FASE 1: DISEÑO DE COMPONENTES TÉCNICOS**

### **Paso 1.1: Backend API Design (FastAPI)**

**Instrucción (Orquestador):** 
```
"Diseña los componentes del backend siguiendo patrones FastAPI, incluyendo routers, dependencies, 
models, schemas y migraciones Alembic."
```

**Acción (Agente IA):**
1. **API Contract Design**:
   ```yaml
   api_design:
     router: "backend/api/routers/emprendedor.py"
     
     endpoints:
       - method: POST
         path: "/api/v1/emprendedor/register"
         auth: "Depends(get_current_site)"
         request_schema: "EmprendedorRegistrationRequest"
         response_schema: "EmprendedorRegistrationResponse"
         business_logic:
           - "Validate CURP via existing profile validation"
           - "Create user via authentication service"
           - "Associate emprendedor kit"
         error_handling:
           - "401: Invalid or missing API Key (via raise_auth_error)"
           - "400: Validation errors (Pydantic)"
           - "409: CURP already registered"
   ```

2. **Data Model Extensions**:
   ```python
   # backend/api/models.py - Extension design
   class EmprendedorProfile(Base):
       __tablename__ = 'emprendedor_profiles'
       
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey('users.id'))  # Reuse existing users table
       curp = Column(String(18), unique=True, nullable=False, index=True)
       kit_type = Column(String(50), nullable=False)
       registration_date = Column(DateTime, default=datetime.utcnow)
       
       # Relationships
       user = relationship("User", back_populates="emprendedor_profile")
   ```

3. **Alembic Migration Design**:
   ```yaml
   migration_spec:
     revision: "add_emprendedor_profiles"
     dependencies: ["users table (existing)"]
     operations:
       - "CREATE TABLE emprendedor_profiles"
       - "CREATE INDEX idx_emprendedor_curp ON emprendedor_profiles(curp)"
       - "ADD FOREIGN KEY emprendedor_profiles.user_id → users.id"
     rollback: "DROP TABLE emprendedor_profiles"
     backward_compatible: true
     breaking_changes: false
   ```

4. **Security Integration**:
   ```python
   # Diseño de integración con security.py
   from backend.api.security import security, get_current_site, raise_auth_error
   
   @router.post("/emprendedor/register")
   async def register_emprendedor(
       request: EmprendedorRegistrationRequest,
       site: SiteConfiguration = Depends(get_current_site)  # Reuse existing
   ):
       # Implementation uses centralized auth
       pass
   ```

**Entregable Crítico**: `backend-design.yaml` con especificaciones completas

### **Paso 1.2: Admin Panel Design (Laravel/Filament)**

**Instrucción (Orquestador):** 
```
"Diseña los componentes del admin panel usando Filament patterns, incluyendo Resources, Forms, 
Tables y Actions."
```

**Acción (Agente IA):**
1. **Filament Resource Design**:
   ```php
   // admin/app/Filament/Resources/EmprendedorResource.php - Design spec
   
   class EmprendedorResource extends Resource
   {
       protected static ?string $model = EmprendedorProfile::class;
       
       public static function form(Form $form): Form
       {
           return $form->schema([
               TextInput::make('curp')
                   ->required()
                   ->length(18)
                   ->unique(ignoreRecord: true),
               Select::make('kit_type')
                   ->options([
                       'basic' => 'Kit Básico',
                       'premium' => 'Kit Premium',
                   ])
                   ->required(),
               // ... more fields
           ]);
       }
       
       public static function table(Table $table): Table
       {
           return $table->columns([
               TextColumn::make('curp')->searchable(),
               TextColumn::make('kit_type'),
               TextColumn::make('registration_date')->dateTime(),
           ]);
       }
   }
   ```

2. **Eloquent Model Design**:
   ```php
   // admin/app/Models/EmprendedorProfile.php
   
   class EmprendedorProfile extends Model
   {
       protected $fillable = ['user_id', 'curp', 'kit_type'];
       
       public function user(): BelongsTo
       {
           return $this->belongsTo(User::class);  // Reuse existing User model
       }
   }
   ```

3. **Laravel Migration Design**:
   ```php
   // admin/database/migrations/YYYY_MM_DD_create_emprendedor_profiles_table.php
   
   Schema::create('emprendedor_profiles', function (Blueprint $table) {
       $table->id();
       $table->foreignId('user_id')->constrained()->onDelete('cascade');
       $table->string('curp', 18)->unique();
       $table->string('kit_type', 50);
       $table->timestamps();
       
       $table->index('curp');
   });
   ```

**Entregable Crítico**: `admin-design.yaml` con especificaciones Filament

### **Paso 1.3: Database Design & Migration Strategy**

**Instrucción (Orquestador):** 
```
"Diseña el esquema de base de datos completo, estrategia de migración dual (Alembic + Laravel), 
y plan de rollback."
```

**Acción (Agente IA):**
1. **Database Schema Design**:
   ```yaml
   database_schema:
     new_tables:
       emprendedor_profiles:
         columns:
           - "id SERIAL PRIMARY KEY"
           - "user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"
           - "curp VARCHAR(18) UNIQUE NOT NULL"
           - "kit_type VARCHAR(50) NOT NULL"
           - "registration_date TIMESTAMP DEFAULT NOW()"
           - "created_at TIMESTAMP"
           - "updated_at TIMESTAMP"
         indexes:
           - "CREATE INDEX idx_emprendedor_curp ON emprendedor_profiles(curp)"
           - "CREATE INDEX idx_emprendedor_user_id ON emprendedor_profiles(user_id)"
           
     modified_tables:
       sites:
         new_columns:
           - "emprendedor_enabled BOOLEAN DEFAULT FALSE"
           - "emprendedor_config JSONB"
         backward_compatible: true
   ```

2. **Dual Migration Strategy**:
   ```yaml
   migration_strategy:
     backend_alembic:
       file: "backend/alembic/versions/XXXX_add_emprendedor_profiles.py"
       execution: "alembic upgrade head"
       test_command: "cd backend && pytest tests/test_migrations.py"
       
     admin_laravel:
       file: "admin/database/migrations/YYYY_MM_DD_add_emprendedor_profiles.php"
       execution: "ddev artisan migrate"
       test_command: "ddev artisan migrate:status"
       
     synchronization:
       approach: "Backend migrations run first (source of truth)"
       validation: "Admin migrations match backend schema exactly"
       
     rollback_plan:
       - "admin: ddev artisan migrate:rollback --step=1"
       - "backend: alembic downgrade -1"
       - "verify: check no orphaned data"
   ```

**Entregable Crítico**: `database-design.yaml` con estrategia de migración completa

### **Paso 1.4: Integration & Data Flow Design**

**Instrucción (Orquestador):** 
```
"Diseña los flujos de integración entre componentes, incluyendo secuencias de llamadas, 
manejo de transacciones y patrones de comunicación."
```

**Acción (Agente IA):**
1. **Sequence Diagrams**:
   ```mermaid
   sequenceDiagram
       participant Client as External Client
       participant API as FastAPI Backend
       participant Auth as Security Module (REUSED)
       participant DB as PostgreSQL
       participant Admin as Filament Admin
       
       Client->>API: POST /api/v1/emprendedor/register
       API->>Auth: get_current_site(credentials)
       
       alt Invalid/Missing API Key
           Auth-->>API: raise_auth_error()
           API-->>Client: 401 Invalid or missing API Key
       end
       
       Auth-->>API: SiteConfiguration
       API->>DB: Validate CURP uniqueness
       
       alt CURP exists
           DB-->>API: Conflict
           API-->>Client: 409 CURP already registered
       end
       
       API->>DB: BEGIN TRANSACTION
       API->>DB: INSERT INTO emprendedor_profiles
       API->>DB: COMMIT
       API-->>Client: 201 Registration successful
       
       Admin->>DB: Query emprendedor_profiles (Eloquent)
       DB-->>Admin: Results
       Admin-->>Admin: Render Filament Table
   ```

2. **Transaction Management**:
   ```yaml
   transaction_design:
     backend_transactions:
       pattern: "SQLAlchemy session management"
       scope: "Per API request (FastAPI dependency)"
       rollback_triggers:
         - "Database constraint violations"
         - "Business logic validation failures"
         - "Unhandled exceptions"
         
     admin_transactions:
       pattern: "Laravel DB::transaction()"
       scope: "Filament Actions and Form submissions"
       rollback_triggers:
         - "Eloquent validation errors"
         - "Custom Action failures"
   ```

**Entregable Crítico**: `integration-flows.yaml` con diagramas y especificaciones

---

## **FASE 2: DISEÑO DE TESTING & VALIDACIÓN**

### **Paso 2.1: Backend Testing Strategy (pytest)**

**Instrucción (Orquestador):** 
```
"Diseña la estrategia de testing para el backend usando pytest, incluyendo fixtures, 
test cases y validación de authentication guard."
```

**Acción (Agente IA):**
1. **Test Structure Design**:
   ```yaml
   backend_testing:
     test_files:
       - "backend/tests/test_emprendedor_api.py"
       - "backend/tests/test_emprendedor_models.py"
       - "backend/tests/test_migrations_emprendedor.py"
       
     pytest_fixtures:
       - "test_db_session (existing - reuse)"
       - "authenticated_client (existing - reuse)"
       - "emprendedor_factory (new - create test data)"
       
     test_coverage:
       unit_tests:
         - "Test EmprendedorProfile model validations"
         - "Test CURP uniqueness constraint"
         - "Test kit_type enum validation"
         
       integration_tests:
         - "Test POST /emprendedor/register with valid data"
         - "Test 401 response without API key"
         - "Test 409 response with duplicate CURP"
         - "Test GET /emprendedor/{id} retrieval"
         
       auth_guard_tests:
         - "Run pytest --auth-check to validate HTTPBearer centralization"
         - "Verify no new HTTPBearer() instances outside security.py"
   ```

2. **Test Implementation Examples**:
   ```python
   # backend/tests/test_emprendedor_api.py - Design spec
   
   def test_register_emprendedor_success(authenticated_client, test_db):
       """Test successful emprendedor registration."""
       response = authenticated_client.post("/api/v1/emprendedor/register", json={
           "curp": "ABCD850101HDFLRN09",
           "kit_type": "basic",
           "email": "test@example.com"
       })
       assert response.status_code == 201
       assert response.json()["curp"] == "ABCD850101HDFLRN09"
   
   def test_register_emprendedor_missing_auth(client):
       """Test 401 response without API key."""
       response = client.post("/api/v1/emprendedor/register", json={...})
       assert response.status_code == 401
       assert response.json()["detail"] == "Invalid or missing API Key"
   
   def test_register_emprendedor_duplicate_curp(authenticated_client, emprendedor_factory):
       """Test 409 response with duplicate CURP."""
       existing = emprendedor_factory(curp="ABCD850101HDFLRN09")
       response = authenticated_client.post("/api/v1/emprendedor/register", json={
           "curp": "ABCD850101HDFLRN09",
           ...
       })
       assert response.status_code == 409
   ```

**Entregable Crítico**: `backend-testing.yaml` con estrategia completa

### **Paso 2.2: Admin Testing Strategy (PHPUnit/Pest)**

**Instrucción (Orquestador):** 
```
"Diseña la estrategia de testing para el admin panel usando PHPUnit/Pest, 
incluyendo Feature tests y Filament component tests."
```

**Acción (Agente IA):**
1. **Laravel Test Structure**:
   ```yaml
   admin_testing:
     test_files:
       - "admin/tests/Feature/EmprendedorResourceTest.php"
       - "admin/tests/Unit/EmprendedorProfileTest.php"
       
     test_database:
       strategy: "RefreshDatabase trait"
       seeders: "Use DatabaseSeeder for test data"
       
     test_coverage:
       feature_tests:
         - "Test Filament Resource can list emprendedores"
         - "Test Filament Form can create emprendedor"
         - "Test Filament Form validates CURP format"
         - "Test Filament Table search functionality"
         
       unit_tests:
         - "Test EmprendedorProfile model relationships"
         - "Test EmprendedorProfile accessors/mutators"
   ```

2. **Test Implementation Examples**:
   ```php
   // admin/tests/Feature/EmprendedorResourceTest.php - Design spec
   
   use Illuminate\Foundation\Testing\RefreshDatabase;
   
   test('can list emprendedor profiles', function () {
       $emprendedor = EmprendedorProfile::factory()->create();
       
       livewire(ListEmprendedores::class)
           ->assertCanSeeTableRecords([$emprendedor])
           ->assertCanRenderTableColumn('curp');
   });
   
   test('can create emprendedor profile', function () {
       livewire(CreateEmprendedor::class)
           ->fillForm([
               'curp' => 'ABCD850101HDFLRN09',
               'kit_type' => 'basic',
           ])
           ->call('create')
           ->assertHasNoFormErrors();
       
       $this->assertDatabaseHas('emprendedor_profiles', [
           'curp' => 'ABCD850101HDFLRN09',
       ]);
   });
   ```

**Entregable Crítico**: `admin-testing.yaml` con estrategia PHPUnit/Pest

### **Paso 2.3: E2E & Manual Testing Guide**

**Instrucción (Orquestador):** 
```
"Diseña la guía de testing manual para validación E2E, siguiendo el formato 
de docs/MANUAL_TESTING_GUIDE.md."
```

**Acción (Agente IA):**
1. **Manual Testing Structure**:
   ```yaml
   manual_testing_guide:
     location: "docs/MANUAL_TESTING_EMPRENDEDOR.md"
     
     sections:
       prerequisites:
         - "DDEV environment running"
         - "Backend venv activated"
         - "Test database seeded"
         - "API key configured"
         
       test_scenarios:
         backend_api:
           - scenario: "Register new emprendedor via API"
             steps:
               - "curl POST /api/v1/emprendedor/register with valid data"
               - "Verify 201 response with registration details"
               - "Check database for new record"
             expected_results:
               - "HTTP 201 Created"
               - "Response contains CURP and kit_type"
               - "Database has emprendedor_profiles record"
               
           - scenario: "Reject duplicate CURP registration"
             steps:
               - "Register emprendedor with CURP X"
               - "Attempt to register again with same CURP"
             expected_results:
               - "First registration: 201 Created"
               - "Second registration: 409 Conflict"
               
         admin_panel:
           - scenario: "View emprendedores in Filament"
             steps:
               - "Navigate to /admin/emprendedores"
               - "Verify table displays records"
               - "Test search by CURP"
             expected_results:
               - "Table shows all emprendedor profiles"
               - "Search filters correctly"
               
       troubleshooting:
         - issue: "401 errors on API calls"
           solution: "Check API key in .env matches site configuration"
         - issue: "Migration fails"
           solution: "Run ddev restart and re-run migrations"
   ```

**Entregable Crítico**: `manual-testing-guide.md` diseñado

---

## **FASE 3: DOCUMENTACIÓN TÉCNICA & ENTREGABLES**

### **Paso 3.1: Technical Design Document Generation**

**Instrucción (Orquestador):** 
```
"Genera el documento de diseño técnico completo usando el template 
.raise/templates/tech/tech_design.md, poblando todas las secciones con las especificaciones diseñadas."
```

**Acción (Agente IA):**
1. **Populate Template**:
   ```yaml
   tech_design_document:
     location: "docs/technical-designs/TEC-ZAM-XXX-emprendedor-registration.md"
     
     sections_populated:
       1_vision_general:
         content: "Descripción del objetivo técnico y problema a resolver"
         source: "From stack-assessment.yaml + feature requirements"
         
       2_solucion_propuesta:
         content: "Resumen de alto nivel del approach (extend registrations service)"
         source: "From component-impact.yaml"
         
       3_arquitectura:
         content: "Componentes nuevos, modificados, servicios externos"
         diagrams: "Mermaid diagrams from integration-flows.yaml"
         source: "From backend-design.yaml + admin-design.yaml"
         
       4_flujo_datos:
         content: "Sequence diagrams y descripción de data movement"
         source: "From integration-flows.yaml"
         
       5_contratos_api:
         content: "Especificación completa de endpoints FastAPI"
         source: "From backend-design.yaml::api_design"
         
       6_modelo_datos:
         content: "Esquema de base de datos y migraciones"
         source: "From database-design.yaml"
         
       7_algoritmos:
         content: "Lógica de negocio y validaciones complejas"
         
       8_seguridad:
         content: "Uso de security.py, autenticación, autorización"
         source: "From architecture-patterns.yaml::security"
         
       9_manejo_errores:
         content: "Estrategia de error handling (raise_auth_error, Pydantic validation)"
         
       10_alternativas:
         content: "Opción A (extend) vs Opción B (new service) - justificación"
         source: "From L1-09 capability-matrix.yaml"
         
       11_preguntas_riesgos:
         content: "Open questions y risk mitigation"
         
       12_estimacion:
         content: "Complejidad, incertidumbres, dependencias"
         
       13_estrategia_testing:
         content: "pytest strategy + PHPUnit strategy + manual testing"
         source: "From backend-testing.yaml + admin-testing.yaml"
   ```

**Entregable Crítico**: `TEC-ZAM-XXX-[feature-name].md` completamente poblado

### **Paso 3.2: Implementation Checklist Generation**

**Instrucción (Orquestador):** 
```
"Genera checklist de implementación secuencial con comandos específicos de verificación 
para cada stack."
```

**Acción (Agente IA):**
1. **Checklist Structure**:
   ```yaml
   implementation_checklist:
     phase_1_database:
       - task: "Create Alembic migration"
         file: "backend/alembic/versions/XXXX_add_emprendedor_profiles.py"
         verify: "alembic upgrade head"
         test: "cd backend && pytest tests/test_migrations_emprendedor.py"
         
       - task: "Create Laravel migration"
         file: "admin/database/migrations/YYYY_MM_DD_add_emprendedor_profiles.php"
         verify: "ddev artisan migrate"
         test: "ddev artisan migrate:status"
         
     phase_2_backend_api:
       - task: "Create Pydantic schemas"
         file: "backend/api/schemas/emprendedor.py"
         verify: "python -c 'from backend.api.schemas.emprendedor import *'"
         
       - task: "Create SQLAlchemy model"
         file: "backend/api/models.py::EmprendedorProfile"
         verify: "python -c 'from backend.api.models import EmprendedorProfile'"
         
       - task: "Create FastAPI router"
         file: "backend/api/routers/emprendedor.py"
         verify: "curl http://localhost:8000/api/v1/emprendedor/register (expect 401)"
         test: "cd backend && pytest tests/test_emprendedor_api.py"
         
       - task: "Run auth guard validation"
         verify: "cd backend && pytest --auth-check"
         
     phase_3_admin_panel:
       - task: "Create Eloquent model"
         file: "admin/app/Models/EmprendedorProfile.php"
         verify: "ddev artisan tinker --execute='EmprendedorProfile::count()'"
         
       - task: "Create Filament Resource"
         file: "admin/app/Filament/Resources/EmprendedorResource.php"
         verify: "Navigate to /admin/emprendedores in browser"
         test: "ddev artisan test --filter=EmprendedorResourceTest"
         
     phase_4_integration:
       - task: "E2E manual testing"
         guide: "docs/MANUAL_TESTING_EMPRENDEDOR.md"
         verify: "Complete all test scenarios in guide"
   ```

**Entregable Crítico**: `IMPLEMENTATION_CHECKLIST.md` con verificaciones por stack

### **Paso 3.3: Architecture Decision Records (ADRs)**

**Instrucción (Orquestador):** 
```
"Documenta las decisiones arquitectónicas clave en formato ADR para referencia futura."
```

**Acción (Agente IA):**
1. **ADR Generation**:
   ```markdown
   # ADR-XXX: Use Centralized HTTPBearer for Emprendedor API
   
   ## Status
   Accepted
   
   ## Context
   New emprendedor registration API requires authentication. Existing 
   backend/api/security.py provides centralized HTTPBearer with standardized 
   401 responses.
   
   ## Decision
   Reuse existing `get_current_site` dependency instead of creating new 
   authentication logic.
   
   ## Consequences
   - **Positive**: Consistent auth behavior, passes pytest --auth-check guard
   - **Positive**: Zero duplication of security logic
   - **Negative**: None
   
   ## Alternatives Considered
   - Create new HTTPBearer instance → Rejected (violates centralization rule)
   - Use JWT tokens → Rejected (incompatible with existing API key system)
   ```

**Entregable Crítico**: `docs/adr/ADR-XXX-[decision-title].md` files

---

## **VALIDATION GATES MANDATORIOS**

### **Gate 1: Stack Alignment Validated**
- **Criterio**: Diseño usa patterns nativos de FastAPI/Laravel/PostgreSQL
- **Validación**: Revisión de code snippets contra best practices del stack
- **Fallo**: Si usa patterns incompatibles → STOP, revisar stack-assessment

### **Gate 2: Ecosystem Reuse Maximized**  
- **Criterio**: ≥80% de componentes reutilizados o extendidos (no nuevos)
- **Validación**: component-impact.yaml muestra ratio reuse/extension/new
- **Fallo**: Si reuse <80% → STOP, revisar capability-matrix from L1-09

### **Gate 3: Backward Compatibility Confirmed**
- **Criterio**: Zero breaking changes, todas las extensiones son aditivas
- **Validación**: Revisión de migrations y API contracts
- **Fallo**: Si breaking changes sin justificación → STOP, rediseñar

### **Gate 4: Testing Strategy Complete**
- **Criterio**: pytest, PHPUnit y manual testing guides diseñados
- **Validación**: Cada componente tiene test coverage plan
- **Fallo**: Si gaps en testing → STOP, completar strategy

### **Gate 5: Implementation-Ready Specifications**
- **Criterio**: Technical design document tiene detalle suficiente para implementar
- **Validación**: Desarrollador puede seguir specs sin ambigüedad
- **Fallo**: Si specs incompletas → STOP, detallar design

---

## **Resultados Esperados**

Al completar esta kata:
- **Technical Design Document**: Documento completo en `.raise/templates/tech/tech_design.md` format
- **Stack-Specific Specs**: Diseños detallados para FastAPI, Laravel, PostgreSQL
- **Implementation Checklist**: Secuencia de tareas con comandos de verificación
- **Testing Strategy**: pytest, PHPUnit y manual testing guides
- **ADRs**: Documentación de decisiones arquitectónicas clave
- **Zero-Duplication Evidence**: Demostración de máxima reutilización del ecosistema

## **Principios RaiSE Reforzados**

*   **Stack Mastery**: Aprovechamiento profundo de capabilities del stack tecnológico
*   **Ecosystem-Driven Design**: Extensión de servicios existentes antes que creación
*   **Clean Architecture**: Separación de responsabilidades y boundaries claros
*   **Backward Compatibility**: Preservación de contratos existentes
*   **Test-Driven Design**: Testing strategy integrada desde el diseño
*   **Implementation-Ready Specs**: Documentación suficientemente detallada para ejecución directa

**Esta kata TRANSFORMA el diseño técnico de conceptual a implementable, garantizando alineación con el stack y máxima reutilización del ecosistema existente.**
