# ADR-009: ShuHaRi Hybrid Implementation

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-29  
**Autores:** Emilio (HumanSys.ai), Claude (RaiSE Ontology Architect)

---

## Contexto

El sistema de Katas de RaiSE requiere una forma de clasificar la audiencia y nivel de práctica deliberada esperado del Orquestador. El schema v2.0 define solo una dimensión:

```yaml
kata:
  level: enum [L0, L1, L2, L3]  # Qué enseña (dominio)
```

Esta estructura captura **qué** enseña la Kata, pero no **a quién** está dirigida ni el nivel de maestría esperado.

### Problema Identificado

| Problema | Manifestación | Desperdicio Lean |
|----------|---------------|------------------|
| Desalineación Kata-Orquestador | Aprendiz usa kata experta → frustración | Muri (sobrecarga) |
| Sin progresión clara | Orquestador no sabe qué practicar next | Mura (irregularidad) |
| Heutagogía no operacionalizada | Principio §5 queda declarativo | Muda (potencial no realizado) |

### Propuesta Original: ShuHaRi Explícito

El documento `kata-shuhari-schema-v2_1.md` propone añadir ShuHaRi (守破離) como dimensión explícita:

```yaml
kata:
  domain: L2      # Qué enseña
  band: ha        # A quién (requiere entender 守破離)
```

**Preocupación:** Esto añade carga cognitiva significativa. El usuario debe aprender terminología japonesa adicional (ya tenemos Kata, Jidoka, Kaizen, Kanban).

---

## Decisión

Adoptar un **enfoque híbrido**:

1. **ShuHaRi como filosofía de diseño interno** — guía cómo RaiSE crea y organiza Katas
2. **Interfaz de usuario con términos universales** — el usuario ve `audience: beginner/intermediate/advanced`
3. **Mapeo documentado para mantenedores** — preserva la riqueza filosófica

### Schema Adoptado

```yaml
# Lo que VE el usuario
kata:
  id: kata-spec-writing
  domain: L2                    # Qué enseña
  audience: intermediate        # A quién (término universal)
  prerequisites: [kata-prd-review]

# Mapeo INTERNO (para mantenedores)
# beginner    ← Shu (守) - Proteger la forma
# intermediate ← Ha (破) - Romper/adaptar la forma
# advanced    ← Ri (離) - Trascender la forma
```

### Principios de Implementación

| Principio | Aplicación |
|-----------|------------|
| **Progressive Disclosure** | Filosofía ShuHaRi disponible en docs avanzados, no requerida para uso |
| **Familiar Interface** | Términos `beginner/intermediate/advanced` son universales en software |
| **Rich Foundation** | Diseño de Katas sigue progresión ShuHaRi internamente |
| **Marketing Differentiation** | ShuHaRi es historia para talks, blog posts, diferenciación |

### Criterios por Nivel

| Audience | ShuHaRi | Características de la Kata |
|----------|---------|---------------------------|
| `beginner` | 守 Shu | Pasos exactos, sin variación, copiar la forma |
| `intermediate` | 破 Ha | Adaptación al contexto, entender el "por qué" |
| `advanced` | 離 Ri | Crear variaciones propias, fluir sin forma |

---

## Consecuencias

### Positivas

- **Onboarding simple**: Usuario entiende `audience: intermediate` inmediatamente
- **Filosofía preservada**: ShuHaRi guía diseño sin exponerse al usuario
- **Diferenciación en marketing**: Podemos hablar de ShuHaRi en contenido externo
- **Coherencia cultural**: Mantiene conexión con Kata, TPS, artes marciales japonesas
- **Heutagogía operacionalizada**: Progresión clara beginner → intermediate → advanced
- **Carga cognitiva mínima**: No añade términos japoneses a aprender

### Negativas

- **Indirección**: Mantenedores deben conocer el mapeo interno
- **Posible pérdida de riqueza**: Usuario promedio no aprende filosofía ShuHaRi
- **Documentación dual**: Docs públicos vs. docs internos de diseño

### Neutras

- **Términos japoneses existentes no afectados**: Kata, Jidoka, Kaizen permanecen (son diferenciadores establecidos)
- **Compatible con schema v2.0**: Solo añade campo `audience`, no rompe nada

---

## Alternativas Consideradas

### 1. ShuHaRi Explícito (Propuesta Original)

```yaml
kata:
  band: ha  # Usuario debe aprender 守破離
```

**Rechazado porque:**
- Añade carga cognitiva significativa
- Curva de onboarding más empinada
- CTOs enterprise pueden percibirlo como "exótico"

### 2. Sin Clasificación de Audiencia

Mantener solo `level: L0-L3`.

**Rechazado porque:**
- No resuelve el problema de desalineación Kata-Orquestador
- Principio de Heutagogía queda sin operacionalizar
- Desperdicio Muri no eliminado

### 3. Términos Numéricos

```yaml
kata:
  mastery_level: 1  # 1-3
```

**Rechazado porque:**
- Menos expresivo que beginner/intermediate/advanced
- Números arbitrarios sin semántica clara
- Pierde conexión con filosofía subyacente

---

## Implementación

### Cambios Requeridos

| Componente | Cambio |
|------------|--------|
| `11-data-architecture-v2.md` | Añadir campo `audience` a schema Kata |
| `20-glossary-v2.md` | Añadir entrada para `audience` con nota sobre ShuHaRi |
| `05-learning-philosophy-v2.md` | Documentar mapeo ShuHaRi (sección avanzada) |
| Katas existentes | Añadir campo `audience` a cada una |

### Migración

1. Añadir `audience` a schema de Kata
2. Clasificar las 22 Katas existentes
3. Actualizar CLI para filtrar por `audience`
4. Documentar mapeo interno para contribuidores

---

## Referencias

- [kata-shuhari-schema-v2_1.md](../kata-shuhari-schema-v2_1.md) — Propuesta original
- [05-learning-philosophy-v2.md](../05-learning-philosophy-v2.md) — Principios de Heutagogía
- [11-data-architecture-v2.md](../11-data-architecture-v2.md) — Schema de Kata
- Martin Fowler, "Shu Ha Ri" — https://martinfowler.com/bliki/ShuHaRi.html
- Alistair Cockburn, "Shu Ha Ri" — https://alistair.cockburn.us/shu-ha-ri/

---

*Este ADR formaliza la decisión de adoptar ShuHaRi como filosofía de diseño interno mientras se expone una interfaz simple al usuario.*
