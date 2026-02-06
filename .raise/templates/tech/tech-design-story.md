---
id: "[TEC]-[CODE]-[FEAT-ID]"
title: "Tech Design: [Feature Name]"
version: "1.0"
date: "[YYYY-MM-DD]"
status: "[Draft|Approved]"
feature_ref: "[F1.1]"
backlog_ref: "[BCK-XXX-001]"
template: "lean-spec-v1"
---

# Tech Design: [Feature Name]

> **Feature**: [F1.1] - [Nombre del Feature]
> **Epic**: [E1] - [Nombre del Epic]

## 1. Approach

**Qué hace este feature**:
[1-2 oraciones]

**Cómo lo implementamos**:
[1-2 oraciones con approach técnico]

**Componentes afectados**:
- [Componente 1]: [cambio]
- [Componente 2]: [cambio]

---

## 2. Interfaz / Contrato

```yaml
# API, CLI args, o schema principal
[definición del contrato]
```

**Ejemplo de uso**:
```bash
# o código de ejemplo
[ejemplo concreto]
```

---

## 3. Consideraciones

| Aspecto | Decisión | Rationale |
|---------|----------|-----------|
| [Aspecto 1] | [qué hacemos] | [por qué] |
| [Aspecto 2] | [qué hacemos] | [por qué] |

**Riesgos identificados**:
- [ ] [Riesgo 1]
- [ ] [Riesgo 2]

---

<details>
<summary><h2>Algoritmo / Lógica (si aplica)</h2></summary>

```
[Pseudocódigo o descripción de lógica compleja]
```

</details>

<details>
<summary><h2>Testing Approach (si aplica)</h2></summary>

| Tipo | Qué cubre |
|------|-----------|
| Unit | [qué] |
| Integration | [qué] |

</details>
