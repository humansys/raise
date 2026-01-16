# RaiSE Kata: Generación de Documentación Esencial desde Código Fuente (L1-07)

**ID**: L1-07
**Nombre**: Generación de Documentación Esencial desde Código Fuente
**Descripción**: Genera los 4 documentos esenciales de la "mínima información viable" para prevenir errores críticos en cualquier repositorio de Jafra, analizando directamente el código fuente (.NET + gRPC + Clean Architecture) sin depender de documentación SAR preexistente. Los documentos generados forman parte del corpus de RAG para generación de código.
**Objetivo**:
    *   Crear documentación ultra-compacta y crítica para cualquier repositorio de Jafra.
    *   Prevenir errores como "exception swallowing", pipelines silenciosos y violaciones de contratos.
    *   Generar información consumible en < 5 minutos por cualquier desarrollador.
    *   Establecer la base documental mínima para desarrollo seguro y mantenimiento.
    *   Crear corpus de conocimiento estructurado para RAG y generación automática de código.
**Dependencias**:
    *   `L0-03: Meta-Kata del Protocolo de Ejecución y Colaboración`
    *   Workspace con múltiples repositorios .NET (Clean Architecture + gRPC)
    *   Acceso al código fuente de repositorios en el workspace
**Reglas Cursor Relacionadas**:
    *   `010-raise-methodology-overview.mdc`
    *   Reglas de análisis de código C# y gRPC

---

## Contexto y Principios

Esta kata genera la **documentación esencial mínima** identificada como crítica para prevenir errores como los del war room de Jafra. Se enfoca en extraer información directamente del código fuente, sin requerir documentación previa.

**Principios Fundamentales:**
*   **Análisis Directo del Código**: Toda la información se extrae del análisis automático del código fuente
*   **Información Ultra-Compacta**: Máximo 50 líneas por documento, consultable en < 5 minutos
*   **Prevención de Errores Críticos**: Enfocado en casos reales identificados en war rooms
*   **Aplicabilidad Universal**: Funciona en cualquier repo de Jafra con stack estándar
*   **Corpus RAG**: Documentación estructurada para alimentar sistemas de generación de código
*   **Exactitud y Formalidad**: Información precisa y verificable directamente del código

---

## Estructura de Workspace y Organización

### **Workspace Multi-Repositorio**
Esta kata está diseñada para trabajar en un workspace que contiene múltiples repositorios de microservicios:

```
workspace/
├── raise-jf-ai-common/          # Repositorio de metodología y katas
│   └── docs/essential/          # Documentación esencial centralizada
│       ├── raise-jf-backend-files/
│       ├── raise-jf-backend-registrations/
│       ├── raise-jf-backend-address-book/
│       └── [repositorio-objetivo]/
├── raise-jf-backend-files/      # Repositorio de microservicio
├── raise-jf-backend-registrations/
├── raise-jf-backend-address-book/
└── [otros-repositorios]/
```

### **Estructura de Documentación Requerida**
Cada repositorio analizado debe tener su documentación en:
```
raise-jf-ai-common/docs/essential/[nombre-repositorio]/
├── services-map.yaml
├── inter-service-contracts.yaml
├── resilience-guide.md
├── deployment-checklist.md
├── README.md
└── [fecha]_L1-07-Execution-[nombre-repo].md
```

---

## Documentos Esenciales a Generar

### 1. **Mapa de Servicios y Dependencias** (`services-map.yaml`)
- Servicios gRPC y REST identificados con precisión técnica
- Reglas de comunicación permitidas/prohibidas basadas en análisis real
- Dependencias críticas entre microservicios con checksums de contratos
- Información estructurada para RAG: tipos de datos, endpoints, dependencias

### 2. **Contratos Inter-Servicios Críticos** (`inter-service-contracts.yaml`)
- Endpoints críticos con casos de idempotencia documentados formalmente
- Códigos de error esperados por operación con mapeo HTTP/gRPC
- Casos específicos de manejo de duplicados extraídos del código
- Timeouts, SLAs y políticas de retry documentadas

### 3. **Guía de Resiliencia** (`resilience-guide.md`)
- Patrones de idempotencia implementados con referencias específicas al código
- Anti-patrones detectados con ubicación exacta (archivo:línea)
- Reglas de manejo de errores extraídas de implementaciones reales
- Vulnerabilidades críticas con acciones correctivas específicas

### 4. **Checklist de Despliegue** (`deployment-checklist.md`)
- Verificaciones críticas pre-despliegue basadas en análisis de riesgos
- Tests de contratos inter-servicios con comandos ejecutables
- Validaciones de idempotencia específicas del repositorio
- Triggers de rollback basados en anti-patrones detectados

---

## Pasos del Kata

### **Paso 0: Identificación del Repositorio Objetivo**

**Instrucción (Orquestador):** 
```
"Ejecuta la Kata L1-07 para el repositorio [NOMBRE_REPOSITORIO_EXACTO]. 
Genera la documentación esencial en la estructura requerida."
```

**Acción (Agente IA):**
1. **Verificar workspace**: Listar repositorios disponibles en workspace
2. **Confirmar repositorio objetivo**: Validar que existe `[NOMBRE_REPOSITORIO_EXACTO]`
3. **Crear estructura de directorios**: 
   ```bash
   mkdir -p raise-jf-ai-common/docs/essential/[NOMBRE_REPOSITORIO_EXACTO]
   ```
4. **Crear documento de tracking**: `YYYY-MM-DD_L1-07-Execution-[NOMBRE_REPO].md`
5. **Presentar plan específico** para el repositorio identificado

### **Paso 1: Navegación y Análisis de Repositorio Objetivo**

**Instrucción (Orquestador):** 
```
"Cambia al repositorio objetivo y analiza su estructura completa."
```

**Acción (Agente IA):**
- **Cambiar directorio**: `cd ../[NOMBRE_REPOSITORIO_EXACTO]`
- **Mapear estructura**: Ejecutar `list_dir` recursivo para identificar arquitectura
- **Identificar proyectos**: Buscar patrones Clean Architecture (*.Domain, *.Application, etc.)
- **Localizar contratos**: Encontrar archivos .proto, controllers, y configuraciones
- **Verificar stack tecnológico**: Identificar versions .NET, frameworks, dependencias

---

### **Fase 1: Análisis Exhaustivo del Código Fuente**

### **Paso 2: Extracción de Servicios y Contratos**

**Instrucción (Orquestador):** 
```
"Extrae todos los servicios gRPC y REST con precisión técnica para corpus RAG."
```

**Acción (Agente IA):**
- **Servicios gRPC**: 
  ```bash
  grep_search query="service " include_pattern="*.proto"
  ```
- **Controladores REST**: 
  ```bash
  grep_search query="Controller|ControllerBase" include_pattern="*.cs"
  ```
- **Métodos y endpoints**: Extraer signatures completas, parámetros, tipos de retorno
- **Checksums de contratos**: Calcular hash de archivos .proto para versionado
- **Documentar con precisión**: Tipos exactos, namespaces, versiones

### **Paso 3: Mapeo de Dependencias Inter-Servicios**

**Instrucción (Orquestador):** 
```
"Mapea todas las dependencias inter-servicios con información técnica precisa."
```

**Acción (Agente IA):**
- **Clientes gRPC**: 
  ```bash
  grep_search query="\.proto|GrpcChannel|CallInvoker" include_pattern="*.cs"
  ```
- **Clientes HTTP**: 
  ```bash
  grep_search query="HttpClient|RestClient|IHttpClientFactory" include_pattern="*.cs"
  ```
- **Configuraciones**: Analizar appsettings.json, Program.cs, Startup.cs
- **Inyección de dependencias**: Mapear servicios registrados
- **URLs y endpoints**: Extraer configuraciones de servicios externos

### **Paso 4: Detección de Patrones Críticos y Anti-Patrones**

**Instrucción (Orquestador):** 
```
"Detecta anti-patrones y vulnerabilidades con ubicación exacta en el código."
```

**Acción (Agente IA):**
- **Exception swallowing**: 
  ```bash
  grep_search query="catch.*\{[\s\n]*return|catch.*\{[\s\n]*\}" include_pattern="*.cs"
  ```
- **Manejo de duplicados**: 
  ```bash
  grep_search query="Duplicate|AlreadyExists|Conflict|Idempotent" include_pattern="*.cs"
  ```
- **Timeouts y configuraciones**: Buscar valores hardcodeados vs configurables
- **Logging y observabilidad**: Verificar patrones de logging estructurado
- **Documentar ubicaciones exactas**: archivo:línea para cada anti-patrón

### **Paso 5: Análisis de Códigos de Error y Manejo**

**Instrucción (Orquestador):** 
```
"Mapea todos los códigos de error con precisión para documentación RAG."
```

**Acción (Agente IA):**
- **Constantes de error**: 
  ```bash
  grep_search query="ErrorsConst|StatusCode|HttpStatusCode" include_pattern="*.cs"
  ```
- **Excepciones personalizadas**: Mapear jerarquía de excepciones del dominio
- **Transformaciones entre capas**: Documentar mapeo de errores gRPC ↔ HTTP
- **Códigos de negocio**: Extraer enums y constantes específicas del dominio

---

### **Fase 2: Generación de Documentación Formal**

### **Paso 6: Generar Mapa de Servicios (services-map.yaml)**

**Instrucción (Orquestador):** 
```
"Genera services-map.yaml con información técnica precisa para corpus RAG."
```

**Acción (Agente IA):**
- **Estructura YAML formal** con servicios identificados
- **Checksums de contratos** para versionado automático
- **Dependencias críticas** con niveles de criticidad (HIGH/MEDIUM/LOW)
- **Tipos de comunicación** (gRPC/REST/SOAP) con endpoints específicos
- **Información para RAG**: tipos de datos, namespaces, versiones exactas
- **Máximo 50 líneas**, ultra-compacto pero técnicamente preciso

### **Paso 7: Generar Contratos Inter-Servicios (inter-service-contracts.yaml)**

**Instrucción (Orquestador):** 
```
"Genera inter-service-contracts.yaml con casos críticos y códigos de error exactos."
```

**Acción (Agente IA):**
- **Endpoints críticos** con signatures completas
- **Casos de idempotencia** extraídos del código real
- **Mapeo de códigos de error** HTTP ↔ gRPC con referencias exactas
- **Timeouts y SLAs** documentados desde configuraciones
- **Políticas de retry** identificadas en el código
- **Información estructurada** para generación automática de código

### **Paso 8: Generar Guía de Resiliencia (resilience-guide.md)**

**Instrucción (Orquestador):** 
```
"Genera resilience-guide.md con patrones específicos y ubicaciones exactas."
```

**Acción (Agente IA):**
- **Patrones implementados** con referencias al código (archivo:línea)
- **Anti-patrones detectados** con ubicación específica y riesgo
- **Vulnerabilidades críticas** con acciones correctivas técnicas
- **Código de ejemplo** extraído del repositorio real
- **Métricas de monitorización** específicas para el servicio
- **Acciones inmediatas** priorizadas por criticidad

### **Paso 9: Generar Checklist de Despliegue (deployment-checklist.md)**

**Instrucción (Orquestador):** 
```
"Genera deployment-checklist.md ejecutable con verificaciones específicas."
```

**Acción (Agente IA):**
- **Verificaciones pre-despliegue** basadas en análisis de riesgos específicos
- **Comandos ejecutables** para validación de contratos
- **Tests específicos** para anti-patrones detectados
- **Triggers de rollback** basados en vulnerabilidades identificadas
- **Scripts de validación** con timeouts y criterios de éxito
- **Contactos de emergencia** y escalación

### **Paso 10: Generar README y Documentación de Mantenimiento**

**Instrucción (Orquestador):** 
```
"Finaliza con README.md y documentación de mantenimiento automático."
```

**Acción (Agente IA):**
- **README.md** explicando propósito y uso específico del repositorio
- **Comandos de regeneración** automática cuando cambie el código
- **Integración con CI/CD** para actualización automática
- **Métricas de calidad** de la documentación generada
- **Enlaces a corpus RAG** y uso en generación de código

---

## Plantillas Formales para Corpus RAG

### **Template: services-map.yaml**
```yaml
# 📊 MAPA DE SERVICIOS Y DEPENDENCIAS - [RepositoryName]
# Generado: [YYYY-MM-DD] | Kata: L1-07 | Versión: [X.Y]
# ⚠️  ULTRA-COMPACTO: 50 líneas máximo | CORPUS RAG: Información técnica precisa

service:
  name: "[Namespace.ExactoDelServicio]"
  type: "microservice|monolith|library"
  architecture: "clean-architecture|layered|other"
  runtime: "[.NET Version]"
  ports:
    - grpc: "[service.v1.ServiceName]"
    - rest: "[/api/route/**]"

# 🗄️ DEPENDENCIAS CRÍTICAS CON CHECKSUMS
dependencies:
  databases:
    - name: "[DatabaseName]"
      type: "[sql-server|postgresql|mongodb]"
      host: "[host:port]"
      criticality: "[HIGH|MEDIUM|LOW]"
      
  storage:
    - name: "[StorageProvider]"
      type: "[gcs|s3|azure-blob]"
      operations: ["[operation1]", "[operation2]"]
      criticality: "[HIGH|MEDIUM|LOW]"
      
  external_services:
    - name: "[ServiceName]"
      type: "[grpc|rest|soap]"
      contract_checksum: "[sha256-hash]"
      endpoint: "[url-or-namespace]"
      criticality: "[HIGH|MEDIUM|LOW]"

# 🚨 VULNERABILIDADES CRÍTICAS DETECTADAS
critical_issues:
  - "⚠️  [Descripción específica con ubicación archivo:línea]"
  - "🔐 [Problema de seguridad específico]"
  - "♻️  [Anti-patrón detectado con riesgo específico]"

# 📡 COMUNICACIÓN INTER-SERVICIOS
inter_service_calls:
  - target: "[ServiceName]"
    method: "[MethodName]"
    criticality: "[HIGH|MEDIUM|LOW]"
    timeout_ms: [valor]

# 🔄 CARACTERÍSTICAS DE IDEMPOTENCIA
idempotency:
  [operation_name]: "[método de detección específico]"
  [otra_operacion]: "[patrón implementado]"
```

### **Template: inter-service-contracts.yaml**
```yaml
# 📋 CONTRATOS INTER-SERVICIOS CRÍTICOS - [RepositoryName]
# Generado: [YYYY-MM-DD] | Kata: L1-07 | Versión: [X.Y]
# ⚠️  ULTRA-COMPACTO: 50 líneas máximo | CORPUS RAG: Contratos técnicos precisos

# 🎯 CONTRATOS gRPC ([archivo.proto])
grpc_contracts:
  service: "[namespace.ServiceName]"
  contract_checksum: "[sha256-hash]"
  
  critical_methods:
    - name: "[MethodName]"
      input: "[RequestType] ([campos principales])"
      output: "[ResponseType] ([campos principales])"
      risk: "[HIGH|MEDIUM|LOW] - [descripción específica]"
      timeout_ms: [valor]
      idempotent: [true|false]
      
# 🌐 CONTRATOS REST ([/api/route])
rest_contracts:
  critical_endpoints:
    - method: "[HTTP_METHOD] [/exact/route]"
      purpose: "[Descripción técnica específica]"
      auth: "[Tipo de autenticación o DISABLED]"
      risk: "[CRITICAL|HIGH|MEDIUM] - [riesgo específico]"
      max_size: "[límite si aplica]"
      timeout_ms: [valor]

# 🚨 RIESGOS CRÍTICOS IDENTIFICADOS
security_risks:
  - "🔐 [Riesgo específico con ubicación]"
  - "👤 [Problema de autenticación/autorización]"
  - "📏 [Inconsistencia de configuración]"
  
# 📊 CÓDIGOS DE ERROR ESTÁNDAR
error_codes:
  [categoria]: "[código_específico]"
  [otra_categoria]: "[otro_código]"
  
# 🔄 POLÍTICAS DE RETRY Y TIMEOUTS
retry_policies:
  [operation]: 
    max_retries: [número]
    backoff_ms: [valor]
    circuit_breaker: [true|false]
```

### **Template: resilience-guide.md**
```markdown
# 🛡️ GUÍA DE RESILIENCIA - [RepositoryName]
**Generado:** [YYYY-MM-DD] | **Kata:** L1-07 | **Versión:** [X.Y]  
**⚠️ ULTRA-COMPACTO:** 50 líneas máximo | **CORPUS RAG:** Patrones técnicos verificables

## 🚨 VULNERABILIDADES CRÍTICAS DETECTADAS

### 1. **[Nombre de Vulnerabilidad]**
- **Problema**: [Descripción técnica específica]
- **Ubicación**: `[archivo.cs:línea]`
- **Impacto**: [Consecuencia técnica específica]
- **Acción**: [Solución técnica específica]

### 2. **[Otra Vulnerabilidad]**
- **Problema**: [Descripción con código específico]
- **Impacto**: [Riesgo cuantificado]
- **Acción**: [Implementación técnica requerida]

## 🔄 PATRONES DE RECUPERACIÓN

### **[Tipo de Fallo - ej: Database Failures]**
```yaml
Strategy: "[estrategia específica del código]"
Implementation: "[ubicación en código]"
Max_Retries: [valor del código]
Timeout_ms: [valor configurado]
Circuit_Breaker: "[implementado|missing]"
```

### **[Otro Tipo de Fallo]**
```csharp
// PATRÓN IMPLEMENTADO: [descripción]
// Ubicación: [archivo.cs:línea]
[código específico extraído del repositorio]
```

## ⚡ MONITORIZACIÓN ESENCIAL

### **Métricas Críticas Específicas**
1. **[Métrica específica]** → [Indicador de qué problema]
2. **[Otra métrica]** → [Problema que detecta]

### **Logs Críticos del Código**
- `[ErrorConstant]` → [Significado específico]
- `[OtroError]` → [Contexto del código]

## 🚀 ACCIONES INMEDIATAS REQUERIDAS
1. [Acción técnica específica con prioridad]
2. [Otra acción con implementación concreta]
```

### **Template: deployment-checklist.md**
```markdown
# ✅ CHECKLIST DE DESPLIEGUE - [RepositoryName]
**Generado:** [YYYY-MM-DD] | **Kata:** L1-07 | **Versión:** [X.Y]  
**⚠️ ULTRA-COMPACTO:** 50 líneas máximo | **EJECUTABLE:** Comandos verificables

## 🚨 PRE-DESPLIEGUE (CRÍTICO - NO OMITIR)

### **Seguridad**
- [ ] **[Verificación específica]** - [Comando o acción específica]
- [ ] **[Otra verificación]** - [Implementación técnica]

### **Configuración**
- [ ] **[Config específica]** - [Valor exacto a verificar]
- [ ] **[Otra config]** - [Comando de validación]

### **Código**
- [ ] **[Anti-patrón específico]** - [Verificación en archivo:línea]

## ⚡ VERIFICACIÓN POST-DESPLIEGUE

### **Funcionalidad Core**
- [ ] **[Test específico]** → [Resultado esperado exacto]
- [ ] **[Otro test]** → [Criterio de éxito específico]

### **Comandos de Validación**
```bash
# [Descripción del comando]
[comando específico] || exit 1

# [Otra validación]
[otro comando con timeout específico]
```

## 🚨 ROLLBACK TRIGGERS (EJECUTAR ROLLBACK SI)
- ❌ [Condición específica con métrica]
- ❌ [Otra condición con valor umbral]

## 📞 CONTACTOS DE EMERGENCIA
- **[Equipo específico]**: `[contacto]`
- **[Otro equipo]**: `[escalación]`
```

---

## Criterios de Calidad para Corpus RAG

### **Exactitud Técnica**
- ✅ **Tipos de datos exactos**: Namespaces completos, versiones específicas
- ✅ **Ubicaciones precisas**: archivo:línea para cada referencia
- ✅ **Checksums verificables**: Hash de contratos para versionado
- ✅ **Comandos ejecutables**: Scripts validados y funcionales

### **Formalidad Estructurada**
- ✅ **YAML válido**: Sintaxis verificada y parseable
- ✅ **Markdown estructurado**: Headers consistentes, formato estándar
- ✅ **Información categorizada**: Criticidad, tipos, dependencias claramente definidas
- ✅ **Referencias cruzadas**: Enlaces entre documentos y código fuente

### **Completitud para RAG**
- ✅ **Información autosuficiente**: Cada documento contiene contexto necesario
- ✅ **Metadatos completos**: Fechas, versiones, checksums, ubicaciones
- ✅ **Casos de uso específicos**: Escenarios reales extraídos del código
- ✅ **Acciones ejecutables**: Comandos y verificaciones específicas

---

## Resultados Esperados

Al completar esta kata:
- **4 documentos esenciales** generados con precisión técnica del código
- **Información ultra-compacta** (máx. 50 líneas) pero técnicamente completa
- **Prevención de errores críticos** basada en análisis real y específico
- **Corpus RAG estructurado** para generación automática de código
- **Documentación verificable** con referencias exactas al código fuente
- **Base documental formal** para desarrollo seguro y mantenimiento

## Principios RaiSE Reforzados

*   **Análisis Automatizado**: Extracción directa y precisa del código fuente
*   **Prevención Proactiva**: Identificación específica de anti-patrones con ubicación
*   **Documentación Viva**: Documentos generados automáticamente, siempre actualizados
*   **Minimalismo Estratégico**: Información esencial pero técnicamente completa
*   **Colaboración Humano-IA**: Proceso guiado por humanos, ejecutado por IA con precisión
*   **Corpus de Conocimiento**: Información estructurada para RAG y generación de código 