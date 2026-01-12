# Quickstart: Usando el Documento de Ciclos de Trabajo

**Feature**: 004-operation-layers
**Audiencia**: Orquestadores RaiSE

---

## ¿Qué es el documento de Ciclos de Trabajo?

Es una guía rápida para saber **qué herramientas y katas usar** según el tipo de trabajo que estás haciendo.

---

## Flujo de Decisión Rápido

```
¿Qué estás haciendo?
│
├─► "Configurando un repo nuevo" ────► Ciclo de Onboarding
│   └─► Usa katas: L0-01, L2-01, L2-02
│
├─► "Planificando una épica" ────────► Ciclo de Proyecto
│   └─► Usa: PRD, Vision, Design (sin herramienta formal)
│
├─► "Implementando un feature" ──────► Ciclo de Feature
│   └─► Usa spec-kit: /speckit.specify → plan → tasks → implement
│
└─► "Reflexionando post-trabajo" ────► Ciclo de Mejora
    └─► Usa: /speckit.analyze, retrospectiva, checkpoint heutagógico
```

---

## Tabla de Referencia Rápida

| Estoy... | Ciclo | Herramienta |
|----------|-------|-------------|
| Analizando un repo existente | Onboarding | Katas L2-01, L2-02 |
| Estableciendo reglas/guardrails | Onboarding | Katas L2-04 a L2-06 |
| Escribiendo un PRD | Proyecto | (manual, plantillas) |
| Definiendo arquitectura de alto nivel | Proyecto | (manual, plantillas) |
| Especificando un feature | Feature | `/speckit.specify` |
| Creando plan de implementación | Feature | `/speckit.plan` |
| Generando tareas | Feature | `/speckit.tasks` |
| Codificando | Feature | `/speckit.implement` |
| Validando coherencia | Mejora | `/speckit.analyze` |
| Actualizando constitution | Mejora | `/speckit.constitution` |

---

## Preguntas Frecuentes

### ¿Puedo usar spec-kit para configurar un repo nuevo?
**No.** spec-kit opera en el Ciclo de Feature. Para onboarding, usa las katas L0-01/L2-*.

### ¿Qué pasa si salto el Ciclo de Proyecto?
**Es válido.** Proyectos pequeños pueden ir de Onboarding directo a Feature. Solo pierdes la documentación de alto nivel (PRD, Vision).

### ¿Dónde encaja raise-kit (futuro)?
raise-kit extenderá spec-kit para cubrir los ciclos que hoy no tienen herramienta formal (Onboarding, Proyecto, Mejora completa).

---

## Ubicación del Documento

El documento completo está en:
```
docs/framework/v2.1/model/26-work-cycles-v2.1.md
```

Definiciones formales en el glosario:
```
docs/framework/v2.1/model/20-glossary-v2.1.md → "Work Cycle"
```
