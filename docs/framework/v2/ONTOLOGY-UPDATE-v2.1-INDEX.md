# RaiSE Ontology Update v2.1
## Resumen de Cambios Introducidos

**Fecha:** 28 de Diciembre, 2025  
**Sesión:** Kata Schema con Niveles Semánticos y Jidoka Inline

---

## Cambios Consolidados

### 1. Niveles de Kata: Nombres Semánticos

| Antes | Después | Pregunta Guía |
|-------|---------|---------------|
| `L0` (Meta) | **Principios** | ¿Por qué? ¿Cuándo aplica? |
| `L1` (Proceso) | **Flujo** | ¿Cómo fluye el trabajo? |
| `L2` (Componente) | **Patrón** | ¿Qué estructura usar? |
| `L3` (Técnico) | **Técnica** | ¿Cómo ejecutar esto? |

**Justificación:** "Principios" demanda interpretación activa—alineado con filosofía Lean centrada en principios y con §5 Heutagogía de la Constitution.

### 2. ShuHaRi: Lente, No Clasificación

| Concepto | Es... | No es... |
|----------|-------|----------|
| ShuHaRi | Lente del Orquestador | Dimensión de clasificación |
| Kata | Un archivo por concepto | Tres variantes por concepto |

**Justificación:** Reduce complejidad (4 niveles vs 12 combinaciones) sin perder profundidad. El Orquestador elige cómo relacionarse con cada Kata.

### 3. Jidoka Inline

**Antes:** Sección separada "micro-kaizen" al final de la Kata.

**Después:** Ciclo Jidoka embebido en cada paso:

```markdown
### Paso N: [Acción]
[Instrucciones]
**Verificación:** [Cómo saber si funcionó]
> **Si no puedes continuar:** [Causa → Resolución]
```

**Justificación:** El problema y su resolución están en contexto. Flujo de lectura natural. Ciclo Jidoka (Detectar→Parar→Corregir→Continuar) explícito.

---

## Archivos Generados

| Archivo | Propósito |
|---------|-----------|
| `kata-shuhari-schema-v2_1.md` | Schema completo de Kata v2.1 |
| `patches/patch-11-data-architecture.md` | Cambios a entidad Kata |
| `patches/patch-20-glossary.md` | Cambios a definiciones y jerarquías |
| `patches/patch-05-learning-philosophy.md` | Nueva sección ShuHaRi |
| `patches/patch-21-methodology.md` | Referencias actualizadas |

---

## Documentos del Corpus Afectados

| Documento | Tipo de Cambio |
|-----------|----------------|
| `11-data-architecture-v2.md` | Modificar entidad Kata |
| `20-glossary-v2.md` | Modificar definición Kata, añadir ShuHaRi, actualizar jerarquía |
| `05-learning-philosophy-v2.md` | Añadir sección ShuHaRi como lente |
| `21-methodology-v2.md` | Actualizar referencias a niveles, añadir Jidoka inline |

---

## Estructura de Directorios Actualizada

```
raise-config/
└── katas/
    ├── principios/              # ¿Por qué? ¿Cuándo?
    │   ├── 01-rol-orquestador.md
    │   ├── 02-heutagogia.md
    │   └── 03-jidoka.md
    ├── flujo/                   # ¿Cómo fluye?
    │   ├── 01-discovery.md
    │   ├── 02-planning.md
    │   └── 04-generacion-plan.md
    ├── patron/                  # ¿Qué forma?
    │   ├── 01-tech-design.md
    │   └── 02-analisis-codigo.md
    └── tecnica/                 # ¿Cómo hacer?
        ├── 01-modelado-datos.md
        └── 02-api-rest.md
```

---

## Comandos de Migración

```bash
# Migrar nombres de archivos
raise migrate katas --to-semantic

# Verificar estructura de pasos (Jidoka inline)
raise lint katas --check-jidoka-inline

# Generar reporte de migración
raise audit katas --migration-status
```

---

## ADRs Introducidos

### ADR-011: Niveles Semánticos de Kata
- **Estado:** Accepted
- **Decisión:** L0→Principios, L1→Flujo, L2→Patrón, L3→Técnica
- **Razón:** Coherencia Lean, pregunta guía implícita, reducción de carga cognitiva

### ADR-012: Jidoka Inline
- **Estado:** Accepted
- **Decisión:** Embeber ciclo de corrección en cada paso
- **Razón:** Contexto inmediato, flujo natural, ciclo Jidoka explícito

---

## Coherencia Filosófica Preservada

| Concepto | Origen | Rol en RaiSE |
|----------|--------|--------------|
| **Kata** | Artes marciales | Práctica deliberada |
| **ShuHaRi** | Artes marciales | Progresión del Orquestador |
| **Jidoka** | Toyota/TPS | Calidad construida |
| **Kaizen** | Toyota/TPS | Mejora continua |
| **Principios** | Lean | Base de decisiones |

> Toda la terminología mantiene coherencia con orígenes japoneses de Lean/TPS.

---

## Instrucciones de Aplicación

1. **Revisar** el schema completo en `kata-shuhari-schema-v2_1.md`
2. **Aplicar** los patches a cada documento del corpus
3. **Migrar** archivos de katas existentes con `raise migrate katas --to-semantic`
4. **Validar** coherencia con `raise lint katas --check-jidoka-inline`
5. **Actualizar** referencias en documentación adicional

---

*Este documento resume los cambios ontológicos de la sesión 2025-12-28.*
