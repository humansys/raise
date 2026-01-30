---
id: patron-01-code-analysis
nivel: patron
titulo: "Análisis de Código Existente (Brownfield)"
audience: intermediate
template_asociado: null
validation_gate: null
prerequisites:
  - principios-00-meta-kata
tags: [brownfield, analisis, codigo, patron]
version: 1.0.0
---

# Análisis de Código Existente (Brownfield)

## Propósito

Establecer un proceso estructurado para analizar codebases existentes antes de modificarlas o extenderlas. Este patrón responde a: **¿Qué forma tiene un análisis de código efectivo?**

## Cuándo Aplicar

- Antes de cualquier modificación en código existente
- Al iniciar trabajo en un proyecto brownfield
- Cuando se necesita entender deuda técnica
- Para planificar refactorizaciones

---

## Estructura del Análisis

### Paso 1: Mapear Estructura de Directorios

Obtener una visión general de la organización del código:
- Identificar carpetas principales y su propósito
- Detectar patrones de organización (por feature, por capa, híbrido)
- Localizar archivos de configuración clave

**Verificación:** Puedes describir la estructura en 2-3 oraciones y dibujar un diagrama mental de la organización.

> **Si no puedes continuar:** Estructura caótica sin patrón claro → Documentar la situación actual antes de proponer mejoras. El análisis de "lo que hay" precede al análisis de "lo que debería haber".

---

### Paso 2: Identificar Puntos de Entrada

Localizar cómo inicia la ejecución del sistema:
- Entry points de la aplicación (main, index, app)
- Handlers de eventos o requests
- Rutas o endpoints principales

**Verificación:** Puedes trazar el flujo desde que un usuario/sistema hace una petición hasta que obtiene respuesta.

> **Si no puedes continuar:** Múltiples entry points sin documentación → Usar herramientas de tracing o logs para descubrir flujos reales. El código ejecutado es la verdad.

---

### Paso 3: Analizar Dependencias

Mapear las dependencias internas y externas:
- Librerías y frameworks utilizados
- Servicios externos consumidos
- Dependencias entre módulos internos

**Verificación:** Lista completa de dependencias con versiones y propósito de cada una.

> **Si no puedes continuar:** Dependencias no declaradas (imports dinámicos, inyección) → Ejecutar el sistema y observar conexiones reales. Complementar con análisis estático.

---

### Paso 4: Evaluar Calidad de Código

Revisar indicadores de salud del código:
- Cobertura de tests existente
- Complejidad ciclomática
- Código duplicado
- Convenciones seguidas/violadas

**Verificación:** Tienes métricas concretas (números) sobre el estado actual.

> **Si no puedes continuar:** Sin herramientas de análisis → Usar herramientas gratuitas (SonarQube, ESLint, etc.) para obtener baseline. Sin métricas, todo es opinión.

---

### Paso 5: Identificar Deuda Técnica

Documentar problemas conocidos y potenciales:
- TODOs y FIXMEs en el código
- Patrones obsoletos o deprecated
- Áreas de alto acoplamiento
- Código sin tests

**Verificación:** Lista priorizada de deuda técnica con impacto estimado.

> **Si no puedes continuar:** Deuda técnica abrumadora → Priorizar por impacto en la funcionalidad actual. No toda la deuda necesita pagarse ahora.

---

### Paso 6: Documentar Hallazgos

Consolidar el análisis en un documento estructurado:
- Resumen ejecutivo (1 párrafo)
- Estructura y arquitectura actual
- Dependencias críticas
- Deuda técnica priorizada
- Recomendaciones

**Verificación:** El documento puede ser entendido por alguien que no ha visto el código.

> **Si no puedes continuar:** Hallazgos demasiado técnicos → Traducir a impacto en negocio. "Código duplicado" → "Cambios requieren modificar 5 archivos en vez de 1".

---

## Output de Este Patrón

Al completar este patrón, el Orquestador tiene:
- Mapa mental de la estructura del código
- Lista de entry points y flujos principales
- Inventario de dependencias
- Métricas de calidad base
- Deuda técnica documentada y priorizada
- Documento de análisis compartible

---

## Adaptación por Contexto

### Proyecto Pequeño (<10K LOC)
- Pasos 1-3 pueden combinarse en uno
- Métricas formales opcionales
- Foco en entender flujos principales

### Proyecto Grande (>100K LOC)
- Análisis por módulo/dominio
- Métricas automatizadas obligatorias
- Múltiples iteraciones del análisis

### Proyecto Legacy
- Énfasis en arqueología (git history)
- Buscar documentación existente primero
- Identificar "knowledge holders" humanos

---

## Anti-Patrones

| Anti-Patrón | Problema | Solución |
|-------------|----------|----------|
| Asumir sin verificar | Decisiones sobre premisas falsas | Verificar cada asunción contra código real |
| Análisis parálisis | Nunca terminar de analizar | Timeboxear cada paso, iterar |
| Ignorar tests | Perder conocimiento codificado | Tests son documentación ejecutable |
| Solo mirar código | Perder contexto de negocio | Hablar con usuarios del sistema |

---

## Referencias

- Meta-Kata: [`principios-00-meta-kata`](../principios/00-meta-kata.md)
- Patrón relacionado: [`patron-02-ecosystem-discovery`](./02-ecosystem-discovery.md)
- Metodología: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md)
