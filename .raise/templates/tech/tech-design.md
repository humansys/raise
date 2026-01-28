---
id: "[TEC]-[CODE]-[SEQ]"
title: "Tech Design: [Nombre Feature]"
version: "1.0"
date: "[YYYY-MM-DD]"
status: "[Draft|Approved]"
related_docs:
  - "[VIS-XXX-001]"
  - "[PRD-XXX-001]"
template: "lean-spec-v1"
---

# Tech Design: [Nombre Feature]

## 1. Objetivo y Solución

**Problema técnico**:
[1-2 oraciones: qué problema técnico resolvemos]

**Solución propuesta**:
[1-2 oraciones: cómo lo resolvemos]

**Componentes involucrados**:
- [Componente 1]: [rol]
- [Componente 2]: [rol]

---

## 2. Arquitectura

```
[Diagrama ASCII o Mermaid mostrando componentes y flujo]
```

| Componente | Responsabilidad | Tipo |
|------------|-----------------|------|
| [Nombre] | [Qué hace] | nuevo / modificado / externo |

---

## 3. Contratos de Datos

### Interfaces / APIs

```yaml
# Endpoint o Interface principal
nombre: [nombre]
input:
  - campo: tipo
output:
  - campo: tipo
```

### Schemas Clave

```yaml
# Schema principal (inline o referencia a archivo)
[NombreSchema]:
  campo_requerido: tipo
  campo_opcional?: tipo
```

---

## 4. Decisiones y Riesgos

### Decisiones Clave

| Decisión | Rationale |
|----------|-----------|
| [Qué decidimos] | [Por qué] |

### Alternativas Descartadas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| [Opción no elegida] | [Por qué no] |

### Open Questions / Riesgos

- [ ] [Pregunta o riesgo pendiente 1]
- [ ] [Pregunta o riesgo pendiente 2]

---

<!-- Secciones opcionales: expandir solo si aplica -->

<details>
<summary><h2>Flujo de Datos (Opcional)</h2></summary>

```
[Diagrama de flujo de datos si es complejo]
```

[Descripción del flujo: origen → transformación → destino]

</details>

<details>
<summary><h2>Algoritmos Clave (Opcional)</h2></summary>

### [Nombre del Algoritmo]

**Input**: [qué recibe]
**Output**: [qué produce]
**Complejidad**: [O(n), O(log n), etc.]

```
[Pseudocódigo o descripción paso a paso]
```

</details>

<details>
<summary><h2>Seguridad (Opcional)</h2></summary>

| Aspecto | Medida |
|---------|--------|
| Autenticación | [mecanismo] |
| Autorización | [mecanismo] |
| Datos sensibles | [cómo se protegen] |

</details>

<details>
<summary><h2>Estrategia de Pruebas (Opcional)</h2></summary>

| Tipo | Cobertura | Herramienta |
|------|-----------|-------------|
| Unit | [qué cubren] | [herramienta] |
| Integration | [qué cubren] | [herramienta] |
| E2E | [qué cubren] | [herramienta] |

</details>
