# Kata: Refinamiento Ontológico (KRO)
## Proceso para Extraer Mejoras de Conversaciones

**Nivel:** Flujo  
**Pregunta Guía:** ¿Cómo fluye el conocimiento desde conversaciones hacia mejoras ontológicas?  
**Audiencia:** Orquestador (Emilio), Agente (Claude)

---

## Propósito

Cada conversación donde se explica RaiSE es un **experimento heutagógico**: al articular conceptos para otros, se prueban contra la realidad. Esta Kata estructura el proceso de extraer valor de esas conversaciones.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO KRO                                    │
│                                                                 │
│   TRANSCRIPT ──► EXTRACCIÓN ──► CLASIFICACIÓN ──► BACKLOG      │
│        │              │               │               │         │
│        ▼              ▼               ▼               ▼         │
│   [Conversación]  [Conceptos]    [Tipo de       [Priorizado    │
│                   [Fricciones]    cambio]        por impacto]  │
│                   [Metáforas]                                   │
│                                                                 │
│   ◄─────────────── VALIDACIÓN ◄─────────────── IMPLEMENTACIÓN  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisitos

- [ ] Transcript de conversación (Google Doc, texto plano, o similar)
- [ ] Acceso al corpus RaiSE (project knowledge)
- [ ] Archivo `35-ontology-backlog-v2.md` existente

---

## Paso 1: Contextualizar el Transcript

**Acción:** Identificar metadata de la conversación.

Extraer:
- **Interlocutor:** Nombre, rol, empresa, relación con Emilio
- **Objetivo:** Qué intentaba lograr Emilio (pitch, colaboración, onboarding, etc.)
- **Perfil técnico:** ¿Developer activo? ¿Manager? ¿Ejecutivo? ¿Técnico pero no dev?
- **Duración:** Aproximada en minutos
- **Tipo:** Pitch fundacional / Discusión técnica / Exploración de negocio / Onboarding

**Verificación:** ¿Tengo suficiente contexto para interpretar las fricciones?

> **Si no puedes continuar:** Buscar información adicional sobre el interlocutor o preguntar a Emilio por contexto.

---

## Paso 2: Extraer Conceptos Articulados

**Acción:** Identificar términos y frases que Emilio usa para explicar RaiSE.

Buscar:
| Categoría | Qué buscar | Señales |
|-----------|------------|---------|
| **Definiciones espontáneas** | Cuando Emilio define algo en sus palabras | "Lo que quiero decir es...", "Eso significa que..." |
| **Metáforas nuevas** | Comparaciones que ayudan a explicar | "Es como...", "Piensa en..." |
| **Frases que resuenan** | El interlocutor dice "Ah, ya entendí" | Confirmaciones verbales, cambio de tono |
| **Refinamientos en vivo** | Emilio mejora una explicación al decirla | Reformulaciones, "mejor dicho..." |

**Output:** Tabla de conceptos con cita textual.

**Verificación:** ¿Cada concepto tiene cita textual que lo respalde?

> **Si no puedes continuar:** Re-leer el transcript buscando momentos de explicación, no solo afirmaciones.

---

## Paso 3: Detectar Fricciones

**Acción:** Identificar momentos donde el interlocutor no entendió o malinterpretó.

Señales de fricción:
- Preguntas que revelan confusión ("¿Pero entonces...?")
- Silencios seguidos de cambio de tema
- Interpretaciones incorrectas que Emilio corrige
- Preguntas que Emilio no pudo responder completamente

**Output:** Tabla de fricciones con causa probable y acción sugerida.

**Verificación:** ¿Identifiqué al menos las fricciones obvias?

> **Si no puedes continuar:** Comparar lo que dijo Emilio con lo que el interlocutor entendió. La brecha es la fricción.

---

## Paso 4: Catalogar Metáforas Efectivas

**Acción:** Identificar explicaciones que funcionaron especialmente bien.

Criterios de "efectividad":
- El interlocutor confirmó entendimiento inmediato
- Emilio la usó múltiples veces en la conversación
- Simplifica un concepto complejo elegantemente
- Es memorable y repetible

**Output:** Tabla de metáforas con contexto de uso sugerido.

**Verificación:** ¿Las metáforas son específicas de RaiSE o genéricas?

> **Si no puedes continuar:** Priorizar metáforas que solo funcionan para RaiSE, no analogías genéricas de software.

---

## Paso 5: Clasificar Hallazgos

**Acción:** Asignar tipo de cambio ontológico a cada hallazgo.

| Tipo | Código | Descripción | Ejemplo |
|------|--------|-------------|---------|
| **Adición** | `ADD` | Concepto nuevo no documentado | "Presupuesto de inferencia" |
| **Refinamiento** | `REF` | Mejora de definición existente | "Dueño del contexto" para Orquestador |
| **Alias** | `ALI` | Nueva forma de nombrar algo existente | "Pastorear IAs" = Orquestar |
| **Corrección** | `COR` | Inconsistencia a resolver | "prácticas" vs "técnica" |
| **Arquitectura** | `ARQ` | Cambio en estructura técnica | Transpilación MD→Cedar |
| **Scope** | `SCP` | Clarificación de qué está dentro/fuera | "SAR no es MVP" |
| **Comunicación** | `COM` | Metáfora/frase para docs externos | "Coches para Verstappens" |

**Verificación:** ¿Cada hallazgo tiene exactamente un tipo asignado?

> **Si no puedes continuar:** Si un hallazgo tiene múltiples tipos, dividirlo en items separados.

---

## Paso 6: Priorizar Items

**Acción:** Asignar prioridad basada en impacto.

Criterios de priorización:

| Criterio | Peso | Pregunta |
|----------|------|----------|
| **Frecuencia** | 3x | ¿Apareció en múltiples transcripts? |
| **Fricción** | 2x | ¿Causó confusión al interlocutor? |
| **Coherencia** | 2x | ¿Es contradicción con corpus actual? |
| **Impacto** | 1x | ¿Cuántos documentos afecta? |

**Escala resultante:**
- **P0**: Contradicciones que causan confusión repetida
- **P1**: Refinamientos que mejoran comunicación significativamente
- **P2**: Adiciones que completan la ontología
- **P3**: Nice-to-have (metáforas, aliases)

**Verificación:** ¿Los P0 son realmente críticos? ¿Los P3 son realmente opcionales?

> **Si no puedes continuar:** Comparar con items existentes en backlog. Si el nuevo es más urgente, ajustar prioridades relativas.

---

## Paso 7: Actualizar Backlog

**Acción:** Añadir items al archivo `35-ontology-backlog-v2.md`.

Para cada item nuevo:
1. Asignar ID secuencial (ONT-XXX)
2. Completar todos los campos de la tabla
3. Añadir al historial de transcripts procesados
4. Actualizar métricas de resumen
5. Si hay patrones cross-transcript, documentar en sección correspondiente

**Verificación:** ¿El backlog sigue siendo coherente después de los cambios?

> **Si no puedes continuar:** Verificar que no hay IDs duplicados y que las referencias a documentos son correctas.

---

## Paso 8: Generar Reporte de Análisis

**Acción:** Producir documento de análisis siguiendo el template.

El reporte debe incluir:
1. Resumen ejecutivo (3-5 oraciones)
2. Contexto de la conversación
3. Tablas de hallazgos (conceptos, fricciones, metáforas)
4. Items propuestos para backlog
5. Observaciones meta (insights sobre cómo mejorar explicaciones)

**Verificación:** ¿El reporte es autosuficiente para alguien que no leyó el transcript?

> **Si no puedes continuar:** Añadir contexto faltante. El reporte debe ser útil incluso meses después.

---

## Output Esperado

1. **Análisis del transcript** (en conversación o archivo separado)
2. **Backlog actualizado** (`35-ontology-backlog-v2.md`)
3. **Decisiones pendientes** para validación con Emilio (si hay P0)

---

## Conexión con Otros Procesos

- **Input:** Transcripts de conversaciones (Google Docs, Tactiq, etc.)
- **Output:** Items en backlog → Implementación en corpus
- **Relacionado:** ADR para cambios estructurales, Kata de Validación Ontológica para verificar coherencia post-implementación

---

## Notas de Implementación

### Para el Agente (Claude)

Al procesar un transcript:
1. Siempre buscar primero en project_knowledge la ontología actual
2. Comparar conceptos del transcript contra definiciones existentes
3. Ser conservador con P0 — solo si hay contradicción clara
4. Priorizar metáforas que son únicas de RaiSE

### Para el Orquestador (Emilio)

- Validar items P0 antes de siguiente transcript
- Marcar items implementados en backlog
- Aportar contexto sobre interlocutores cuando sea relevante

---

## Changelog

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-01-06 | Creación inicial |

---

*Esta Kata implementa Kaizen aplicado a la propia ontología de RaiSE.*
