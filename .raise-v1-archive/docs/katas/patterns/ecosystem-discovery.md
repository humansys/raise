---
id: patron-02-ecosystem-discovery
nivel: patron
titulo: "Descubrimiento de Ecosistema"
audience: intermediate
template_asociado: null
validation_gate: null
prerequisites:
  - principios-00-meta-kata
  - patron-01-code-analysis
tags: [ecosistema, discovery, integraciones, patron]
version: 1.0.0
---

# Descubrimiento de Ecosistema

## Propósito

Mapear el ecosistema completo en el que opera un sistema: servicios, integraciones, dependencias externas y flujos de datos. Este patrón responde a: **¿Qué forma tiene el ecosistema que rodea a este sistema?**

## Cuándo Aplicar

- Al iniciar trabajo en un sistema que interactúa con otros
- Antes de diseñar nuevas integraciones
- Para entender impacto de cambios cross-system
- Durante auditorías de arquitectura

---

## Estructura del Descubrimiento

### Paso 1: Identificar Sistemas Conectados

Listar todos los sistemas con los que interactúa el sistema objetivo:
- Sistemas upstream (proveen datos/servicios)
- Sistemas downstream (consumen datos/servicios)
- Sistemas peer (colaboran en el mismo nivel)

**Verificación:** Diagrama con todos los sistemas identificados y dirección de las flechas (quién llama a quién).

> **Si no puedes continuar:** No hay documentación de integraciones → Revisar configuración (URLs, credentials), logs de red, o código de clientes HTTP/mensajería.

---

### Paso 2: Mapear Protocolos de Comunicación

Para cada conexión identificada, documentar:
- Protocolo (REST, GraphQL, gRPC, mensajería)
- Formato de datos (JSON, XML, Protobuf)
- Autenticación requerida
- SLAs o timeouts esperados

**Verificación:** Tabla completa protocolo/formato/auth para cada integración.

> **Si no puedes continuar:** Protocolos no documentados → Capturar tráfico real o revisar código de integración. Los clientes HTTP revelan los contratos.

---

### Paso 3: Documentar Flujos de Datos

Trazar cómo fluyen los datos a través del ecosistema:
- Datos que entran al sistema (fuentes)
- Transformaciones que ocurren
- Datos que salen del sistema (destinos)
- Datos que se persisten localmente

**Verificación:** Diagrama de flujo de datos mostrando entradas, transformaciones y salidas.

> **Si no puedes continuar:** Flujos complejos con múltiples caminos → Enfocarse primero en el "happy path" principal. Los edge cases se documentan después.

---

### Paso 4: Identificar Dependencias Críticas

Clasificar las dependencias por criticidad:
- **Críticas**: Sistema no funciona sin ellas
- **Importantes**: Degradación significativa sin ellas
- **Opcionales**: Funcionalidad reducida pero operativa

**Verificación:** Matriz de dependencias con clasificación y justificación.

> **Si no puedes continuar:** No hay claridad sobre criticidad → Preguntar: "¿Qué pasa si este servicio no responde?" La respuesta revela la criticidad.

---

### Paso 5: Evaluar Riesgos de Integración

Para cada integración crítica o importante:
- ¿Hay fallback si falla?
- ¿Hay rate limits?
- ¿Quién es el owner del otro sistema?
- ¿Hay SLA documentado?

**Verificación:** Registro de riesgos con mitigaciones identificadas (aunque no implementadas).

> **Si no puedes continuar:** Riesgos desconocidos → Asumir el peor caso y documentar. Mejor sobre-estimar riesgo que subestimar.

---

### Paso 6: Crear Mapa del Ecosistema

Consolidar todo en un artefacto visual y textual:
- Diagrama de arquitectura del ecosistema
- Tabla de integraciones con metadata
- Flujos de datos principales
- Matriz de riesgos

**Verificación:** El mapa puede ser entendido por alguien nuevo en el proyecto en <15 minutos.

> **Si no puedes continuar:** Ecosistema demasiado complejo para un solo diagrama → Crear vistas por dominio o por tipo de integración. Múltiples vistas > un diagrama ilegible.

---

## Output de Este Patrón

Al completar este patrón, el Orquestador tiene:
- Lista completa de sistemas conectados
- Documentación de protocolos y formatos
- Diagramas de flujo de datos
- Clasificación de dependencias por criticidad
- Registro de riesgos de integración
- Mapa visual del ecosistema

---

## Niveles de Profundidad

### Nivel Básico (2-4 horas)
- Identificar sistemas conectados
- Documentar protocolos principales
- Clasificar criticidad

### Nivel Completo (1-2 días)
- Todos los pasos del patrón
- Diagramas detallados
- Validación con owners de otros sistemas

### Nivel Exhaustivo (1 semana+)
- Auditoría de seguridad de integraciones
- Testing de fallbacks
- Documentación de contratos formales

---

## Herramientas Útiles

| Propósito | Herramientas |
|-----------|-------------|
| Diagramas | Draw.io, Mermaid, PlantUML |
| Captura de tráfico | Wireshark, Charles, mitmproxy |
| Documentación API | Swagger/OpenAPI, Postman |
| Monitoreo | Grafana, Datadog, New Relic |

---

## Anti-Patrones

| Anti-Patrón | Problema | Solución |
|-------------|----------|----------|
| Mapear solo lo documentado | Perder integraciones "shadow" | Verificar contra código y logs reales |
| Ignorar sistemas legacy | Dependencias ocultas | Incluir todo, aunque sea "viejo" |
| Asumir SLAs | Sorpresas en producción | Verificar SLAs explícitamente |
| Diagrama estático | Se desactualiza rápido | Automatizar generación si es posible |

---

## Referencias

- Meta-Kata: [`principios-00-meta-kata`](../principios/00-meta-kata.md)
- Patrón previo: [`patron-01-code-analysis`](./01-code-analysis.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md)
