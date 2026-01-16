---
id: principios-01-execution-protocol
nivel: principios
titulo: "Protocolo de Ejecución: Cómo Ejecutar Cualquier Kata"
audience: beginner
template_asociado: null
validation_gate: null
prerequisites:
  - principios-00-meta-kata
tags: [protocolo, ejecucion, proceso, principios]
version: 1.0.0
---

# Protocolo de Ejecución: Cómo Ejecutar Cualquier Kata

## Propósito

Establecer el protocolo estándar para ejecutar cualquier kata del sistema RaiSE. Este principio asegura consistencia y calidad en la aplicación de todas las katas.

Esta kata responde a: **¿Por qué seguir un protocolo?** y **¿Cuándo aplicar cada paso?**

---

## El Protocolo de 7 Pasos

### Paso 1: Identificar el Contexto

Antes de seleccionar una kata, clarificar:
- ¿Qué fase de la metodología es esto?
- ¿Qué artefacto necesito producir?
- ¿Qué inputs tengo disponibles?
- ¿Quién validará el output?

**Verificación:** Puedes responder las cuatro preguntas con claridad.

> **Si no puedes continuar:** Contexto no claro → Hablar con Product Owner o Tech Lead para clarificar antes de comenzar.

---

### Paso 2: Seleccionar la Kata Correcta

Usar la pregunta guía del nivel:
- **¿Por qué?/¿Cuándo?** → Buscar en `principios/`
- **¿Cómo fluye?** → Buscar en `flujo/`
- **¿Qué forma?** → Buscar en `patron/`
- **¿Cómo hacer?** → Buscar en `tecnica/`

**Verificación:** La kata seleccionada produce el artefacto que necesitas.

> **Si no puedes continuar:** No hay kata para tu necesidad → Puede ser tarea trivial (no requiere kata) o gap en el sistema (documentar para futura kata).

---

### Paso 3: Verificar Pre-condiciones

Revisar la sección "Pre-condiciones" de la kata:
- ¿Tengo todos los inputs requeridos?
- ¿Los gates previos están aprobados?
- ¿Las personas necesarias están disponibles?

**Verificación:** Todas las pre-condiciones marcadas como cumplidas.

> **Si no puedes continuar:** Pre-condición no cumplida → Completar el paso previo antes de iniciar esta kata. No comenzar sobre base incompleta.

---

### Paso 4: Cargar el Contexto Necesario

Preparar el ambiente de trabajo:
- Abrir documentos de referencia (PRD, Vision, Tech Design)
- Identificar template asociado
- Cargar guardrails aplicables
- Tener gate checklist visible

**Verificación:** Todos los documentos necesarios están accesibles sin búsqueda adicional.

> **Si no puedes continuar:** Documento faltante → Localizar antes de continuar. Si no existe, puede indicar que falta un paso previo.

---

### Paso 5: Ejecutar Paso a Paso

Para cada paso de la kata:

1. **Leer** el paso completo (acción + verificación + corrección)
2. **Ejecutar** la acción descrita
3. **Verificar** usando el criterio indicado
4. **Si falla**, aplicar la resolución sugerida
5. **Solo continuar** cuando la verificación pasa

**Principio Jidoka:** Si un paso falla, PARAR. No acumular problemas.

**Verificación:** Cada paso está marcado como completado antes de pasar al siguiente.

> **Si no puedes continuar:** Paso falló sin resolución clara → Escalar al rol indicado en la kata o documentar el bloqueo para retrospectiva.

---

### Paso 6: Validar el Output

Una vez completados todos los pasos:
1. Revisar el artefacto producido
2. Verificar contra el template (si aplica)
3. Ejecutar el Validation Gate asociado
4. Obtener aprobación del stakeholder relevante

**Verificación:** Gate pasado y aprobación obtenida.

> **Si no puedes continuar:** Gate falló → Revisar criterios fallidos. Volver al paso correspondiente de la kata para corregir.

---

### Paso 7: Documentar y Transicionar

Finalizar el trabajo:
1. Guardar artefacto en ubicación correcta
2. Actualizar estado en herramienta de tracking
3. Comunicar completitud a stakeholders
4. Identificar siguiente kata en el flujo

**Verificación:** Artefacto guardado, estado actualizado, siguiente paso claro.

> **Si no puedes continuar:** Siguiente paso no claro → Revisar la sección "Siguiente paso" de la kata completada.

---

## Principios del Protocolo

### 1. Secuencialidad
Ejecutar pasos en orden. No saltar pasos aunque parezcan obvios.

**Por qué:** Los pasos están ordenados por dependencia. Saltar puede causar retrabajos.

### 2. Verificación Explícita
Cada paso debe verificarse antes de continuar. No asumir que "probablemente está bien".

**Por qué:** Detectar problemas temprano es más barato que detectarlos tarde.

### 3. Parar en Anomalías (Jidoka)
Si algo falla, parar inmediatamente. No acumular errores esperando que se resuelvan solos.

**Por qué:** Un error no corregido genera errores en cascada.

### 4. Transparencia
Mantener al Orquestador (y stakeholders) informados del progreso y bloqueos.

**Por qué:** La colaboración humano-IA requiere visibilidad mutua.

### 5. Trazabilidad
Documentar decisiones, especialmente cuando se adapta una kata (fase Ha de ShuHaRi).

**Por qué:** Facilita retrospectivas y mejora continua del sistema.

---

## Adaptación del Protocolo (ShuHaRi)

### Fase Shu (Principiante)
- Seguir el protocolo exactamente
- No omitir pasos
- Pedir ayuda ante cualquier duda

### Fase Ha (Intermedio)
- Adaptar pasos al contexto específico
- Combinar pasos cuando tiene sentido
- Documentar adaptaciones

### Fase Ri (Avanzado)
- Protocolo internalizado, fluye naturalmente
- Crear variantes para contextos específicos
- Contribuir mejoras al protocolo base

**Verificación:** Identificas en qué fase estás y actúas acorde.

> **Si no puedes continuar:** No estás seguro de tu nivel → Cuando dudes, usa Shu. Es mejor ser riguroso que tomar atajos prematuros.

---

## Anti-Patrones a Evitar

| Anti-Patrón | Por qué es Problema | Qué Hacer |
|-------------|---------------------|-----------|
| Saltar pre-condiciones | Base incompleta | Completar pre-condiciones primero |
| Ignorar verificaciones | Errores acumulados | Verificar cada paso |
| Continuar tras fallo | Problemas en cascada | PARAR y resolver |
| No documentar | Retrabajos futuros | Documentar decisiones |
| Adaptar prematuramente | Pérdida de rigor | Dominar antes de adaptar |

---

## Output de Esta Kata

Al completar esta kata, el Orquestador:
- Conoce el protocolo de 7 pasos
- Entiende los principios subyacentes
- Sabe cómo adaptar según su nivel ShuHaRi
- Puede identificar y evitar anti-patrones

---

## Referencias

- Meta-Kata: [`principios-00-meta-kata`](./00-meta-kata.md)
- Glosario Jidoka: [`20-glossary-v2.1.md`](../../../docs/framework/v2.1/model/20-glossary-v2.1.md)
- ADR-009 ShuHaRi: [`adr-009-shuhari-hybrid.md`](../../../docs/framework/v2.1/adrs/adr-009-shuhari-hybrid.md)
