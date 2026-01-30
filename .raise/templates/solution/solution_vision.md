# Solution Vision: [Nombre del Sistema]

> **Estado**: Draft | En Revisión | Aprobado
> **Fecha**: [YYYY-MM-DD]
> **Autor**: [Nombre]
> **Versión**: 1.0.0

---

## 1. Identidad del Sistema

### 1.1 Descripción

> "[Nombre] es un [tipo de sistema] que permite a [usuarios] [capacidad principal] para [beneficio]."

### 1.2 Tipo de Sistema

- [ ] Product (B2C)
- [ ] Product (B2B)
- [ ] Platform (Internal)
- [ ] Platform (External)
- [ ] Service (API/Backend)
- [ ] Tool (Internal/Developer)

### 1.3 Misión

[¿Cuál es la razón de existir de este sistema? 1-2 oraciones]

---

## 2. Alcance

### 2.1 In Scope

**Capacidades que el sistema DEBE tener:**
- [ ] [Capacidad 1]
- [ ] [Capacidad 2]
- [ ] [Capacidad 3]

**Usuarios que DEBE servir:**
- [Usuario/Persona 1]
- [Usuario/Persona 2]

**Problemas que DEBE resolver:**
- [Problema 1 - ref: Business Case]
- [Problema 2]

### 2.2 Out of Scope

**Explícitamente EXCLUIDO:**
- ❌ [Capacidad excluida 1]
- ❌ [Capacidad excluida 2]

**Usuarios que NO servirá:**
- ❌ [Usuario excluido]

**Problemas que NO resolverá:**
- ❌ [Problema fuera de scope]

### 2.3 Boundaries

**Dónde termina este sistema:**

| Responsabilidad | Este Sistema | Otro Sistema |
|-----------------|--------------|--------------|
| [Ej: Autenticación] | Consume tokens | Identity Provider los genera |
| [Ej: Pagos] | Inicia transacción | Payment Gateway la procesa |

---

## 3. Capacidades Core

| ID | Capacidad | Descripción | Prioridad | Usuarios |
|----|-----------|-------------|-----------|----------|
| C1 | [Nombre] | [Qué permite hacer] | Must | [Quién] |
| C2 | [Nombre] | [Qué permite hacer] | Must | [Quién] |
| C3 | [Nombre] | [Qué permite hacer] | Should | [Quién] |
| C4 | [Nombre] | [Qué permite hacer] | Could | [Quién] |

**Leyenda de prioridad:**
- **Must**: Sin esta capacidad, el sistema no tiene sentido
- **Should**: Importante, pero sistema funciona sin ella
- **Could**: Nice-to-have, mejora la experiencia

---

## 4. Dirección Técnica

### 4.1 Stack Tecnológico

| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| **Frontend** | [Ej: React] | [18.x] | [Por qué] |
| **Backend** | [Ej: Node.js] | [20.x] | [Por qué] |
| **Database** | [Ej: PostgreSQL] | [15.x] | [Por qué] |
| **Cache** | [Ej: Redis] | [7.x] | [Por qué] |
| **Queue** | [Ej: RabbitMQ] | [3.x] | [Por qué] |
| **Infrastructure** | [Ej: AWS] | - | [Por qué] |

### 4.2 Patrones Arquitectónicos

**Arquitectura General:**
- [ ] Monolith
- [ ] Modular Monolith
- [ ] Microservices
- [ ] Serverless
- [ ] Hybrid

**Patrón de Diseño:**
- [ ] Clean Architecture
- [ ] Hexagonal Architecture
- [ ] Layered Architecture
- [ ] Event-Driven Architecture
- [ ] CQRS

**Patrón de Comunicación:**
- [ ] REST
- [ ] GraphQL
- [ ] gRPC
- [ ] Events/Messages
- [ ] Hybrid

**Justificación:**
[Por qué estos patrones para este sistema]

### 4.3 Decisiones Fundamentales

| ID | Decisión | Opciones Consideradas | Elección | Razón | ADR |
|----|----------|----------------------|----------|-------|-----|
| D1 | [Qué decidir] | [A, B, C] | [B] | [Por qué B] | [Link] |
| D2 | [Qué decidir] | [X, Y] | [X] | [Por qué X] | [Link] |

---

## 5. Quality Attributes

### 5.1 Requisitos No Funcionales

| Attribute | Requisito | Métrica | Target | Prioridad |
|-----------|-----------|---------|--------|-----------|
| **Performance** | Response time | p95 latency | < 200ms | Must |
| **Performance** | Throughput | Requests/sec | > 1000 | Should |
| **Availability** | Uptime | Monthly | 99.9% | Must |
| **Scalability** | Concurrent users | Peak | 10,000 | Should |
| **Scalability** | Data growth | Annual | 10x | Should |
| **Maintainability** | Code coverage | Percentage | > 80% | Should |
| **Maintainability** | Deploy frequency | Per week | > 5 | Could |

### 5.2 Security Level

**Nivel seleccionado:**
- [ ] **Low**: Internal tool, no sensitive data
- [ ] **Medium**: User data, standard authentication
- [ ] **High**: PII, financial data, compliance required
- [ ] **Critical**: Regulated industry (healthcare, finance)

**Justificación:**
[Por qué este nivel de seguridad]

**Requisitos de seguridad derivados:**

| Requisito | Aplica | Detalle |
|-----------|--------|---------|
| Encryption at rest | Sí/No | [Detalle] |
| Encryption in transit | Sí/No | [Detalle] |
| Authentication | Sí/No | [Método] |
| Authorization | Sí/No | [Modelo: RBAC/ABAC] |
| Audit logging | Sí/No | [Qué se loggea] |
| Compliance | Sí/No | [GDPR/SOC2/HIPAA/etc] |

---

## 6. Integraciones

### 6.1 Sistemas Upstream (Consume)

| Sistema | Tipo | Datos | Criticidad | Owner |
|---------|------|-------|------------|-------|
| [Nombre] | API/DB/Event | [Qué datos] | Core/Supporting | [Equipo] |
| [Nombre] | API/DB/Event | [Qué datos] | Core/Supporting | [Equipo] |

### 6.2 Sistemas Downstream (Expone)

| Sistema | Tipo | Datos | SLA | Contrato |
|---------|------|-------|-----|----------|
| [Nombre] | API/Event | [Qué datos] | [Garantías] | [Link] |
| [Nombre] | API/Event | [Qué datos] | [Garantías] | [Link] |

### 6.3 Contratos

**Estándares de API:**
- [ ] OpenAPI/Swagger para REST
- [ ] GraphQL Schema
- [ ] AsyncAPI para eventos
- [ ] Protobuf para gRPC

**Versionado:**
- [ ] URL path (/v1/, /v2/)
- [ ] Header
- [ ] Query parameter

---

## 7. Evolución

### 7.1 Roadmap de Alto Nivel

| Fase | Timeframe | Capacidades | Milestone |
|------|-----------|-------------|-----------|
| MVP | [Q1 2024] | [C1, C2] | [Qué se puede hacer] |
| V1 | [Q2 2024] | [C3, C4] | [Qué se puede hacer] |
| V2 | [Q4 2024] | [C5, C6] | [Qué se puede hacer] |

### 7.2 Principios de Evolución

**Cómo evolucionará este sistema:**
1. [Principio 1: Ej: "Backward compatibility siempre"]
2. [Principio 2: Ej: "Feature flags para rollout gradual"]
3. [Principio 3: Ej: "Deprecation con 6 meses de aviso"]

---

## 8. Trazabilidad

| Fuente | Artefacto | Relación |
|--------|-----------|----------|
| Business Case | `governance/solution/business_case.md` | Justifica este sistema |
| Governance | `governance/solution/` | Deriva de esta vision |
| ADRs | `dev/decisions/framework/` | Decisiones técnicas |

---

## 9. Aprobaciones

| Rol | Nombre | Fecha | Status |
|-----|--------|-------|--------|
| Technical Lead | [Nombre] | [Fecha] | Aprobado/Pendiente |
| Architect | [Nombre] | [Fecha] | Aprobado/Pendiente |
| Product Owner | [Nombre] | [Fecha] | Aprobado/Pendiente |

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | [Fecha] | [Autor] | Versión inicial |

---

*Generado por: `solution/vision` kata*
*Template version: 1.0.0*
