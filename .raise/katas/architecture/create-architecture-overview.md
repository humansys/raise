---
id: "kata-arch-001"
title: "Kata: Create Architecture Overview"
category: "architecture"
output_template: ".raise/templates/architecture/architecture-overview.md"
output_gate: ".raise/gates/gate-architecture.md"
---

# Kata: Create Architecture Overview

## Cuándo Aplicar

Cuando el sistema tiene **>2 componentes** y necesitas documentar la arquitectura a nivel C4 (Context + Container). Prerequisito: Solution Vision aprobada.

---

## Pasos

### 1. Verificar prerequisitos

Confirmar que existen los inputs necesarios:
- Solution Vision aprobada
- Entendimiento de componentes principales
- Stakeholders técnicos identificados

**Output**: Checklist de prerequisitos ✓

**Verificación**: Solution Vision existe y tiene sección de "Solución Propuesta"

> ⚠️ **Si falla**: Ejecutar kata `create-solution-vision` primero

---

### 2. Identificar actores y sistemas externos

Mapear el contexto del sistema (C4 Level 1):
- ¿Quién usa el sistema? (usuarios, roles)
- ¿Con qué sistemas externos se integra?
- ¿Qué datos entran/salen?

**Output**: Lista de actores + sistemas externos con sus interacciones

**Verificación**: Cada actor tiene un verbo de interacción (usa, consume, envía)

> ⚠️ **Si falla**: Revisar Solution Vision sección de stakeholders y alcance

---

### 3. Definir containers

Identificar los containers principales (C4 Level 2):
- ¿Qué aplicaciones/servicios componen el sistema?
- ¿Qué tecnología usa cada uno?
- ¿Cómo se comunican entre sí?

**Output**: Tabla de containers con: nombre, responsabilidad, tecnología, tipo

**Verificación**: Cada container tiene responsabilidad única (single responsibility)

> ⚠️ **Si falla**: Si un container tiene múltiples responsabilidades, dividirlo

---

### 4. Diagramar arquitectura

Crear diagramas ASCII o Mermaid:
- System Context diagram (actores + sistema + externos)
- Container diagram (containers internos + comunicación)

**Output**: 2 diagramas en el documento

**Verificación**: Diagramas son legibles y muestran flujo de datos

> ⚠️ **Si falla**: Simplificar - si no cabe en ASCII simple, el sistema es muy complejo para un overview

---

### 5. Documentar decisiones clave

Extraer decisiones arquitectónicas significativas:
- ¿Por qué esta estructura y no otra?
- ¿Qué alternativas se descartaron?

**Output**: Tabla de decisiones con rationale + referencias a ADRs (si existen)

**Verificación**: Cada decisión tiene un "por qué", no solo un "qué"

> ⚠️ **Si falla**: Si no hay rationale, la decisión no está madura - documentar como "pendiente de validar"

---

### 6. Definir quality attributes

Especificar requisitos no funcionales clave:
- Performance (latencia, throughput)
- Scalability (usuarios, datos)
- Security (authn, authz, datos sensibles)
- Reliability (uptime, recovery)

**Output**: Tabla de NFRs con: atributo, requisito, cómo se logra

**Verificación**: Cada NFR es medible (tiene número o criterio objetivo)

> ⚠️ **Si falla**: NFRs vagos ("debe ser rápido") → convertir a específicos ("<200ms p95")

---

### 7. Compilar documento

Usar template y compilar todas las secciones:
1. Cargar template: `.raise/templates/architecture/architecture-overview.md`
2. Completar secciones requeridas (1-4)
3. Agregar secciones opcionales solo si aplican

**Output**: Archivo `architecture-overview.md` completo

**Verificación**: Documento tiene las 4 secciones requeridas completas

> ⚠️ **Si falla**: Revisar pasos anteriores - algún input está incompleto

---

### 8. Validar con gate

Ejecutar gate de validación:
1. Verificar estructura (secciones presentes)
2. Verificar contenido (no placeholders)
3. Verificar consistencia con Solution Vision

**Output**: Gate passed ✓

**Verificación**: Todos los criterios del gate cumplen

> ⚠️ **Si falla**: Corregir issues identificados por el gate y re-validar

---

## Output Final

- **Archivo**: `specs/main/[proyecto]/architecture-overview.md`
- **Template**: `.raise/templates/architecture/architecture-overview.md`
- **Gate**: `.raise/gates/gate-architecture.md`

---

## Checklist Rápido

```
[ ] Solution Vision existe
[ ] System Context diagram creado
[ ] Container diagram creado
[ ] Tabla de containers completa
[ ] Decisiones con rationale
[ ] NFRs medibles
[ ] Gate passed
```

---

## Referencias

- [C4 Model](https://c4model.com/) - Simon Brown
- Template: `.raise/templates/architecture/architecture-overview.md`
- Ejemplo: `specs/main/governance/architecture-overview.md`
