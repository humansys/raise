# ADR-001: Usar Python para CLI

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-26  
**Autores:** Emilio (HumanSys.ai)

---

## Contexto

Necesitamos elegir un lenguaje para implementar raise-kit (CLI). Los criterios principales son:
- Ecosistema AI/ML maduro
- Facilidad de extensión
- Distribución cross-platform
- Velocidad de desarrollo

## Decisión

Usar **Python 3.11+** como lenguaje principal para raise-kit.

## Consecuencias

### Positivas
- Ecosistema AI/ML excelente (integración con libs existentes)
- Desarrollo rápido (scripts a producción)
- Comunidad amplia (contributors potenciales)
- Click + Rich = UX de CLI excelente

### Negativas
- Requiere Python runtime en máquina target
- Performance inferior a Go/Rust para operaciones IO-bound
- Distribución como binario requiere PyInstaller

### Neutras
- Typing opcional (usamos strict con mypy)

## Alternativas Consideradas

1. **Go** - Binarios estáticos, performance. Rechazado por: ecosistema AI menos maduro, desarrollo más lento.
2. **Rust** - Performance máximo. Rechazado por: curva de aprendizaje, overhead para MVP.
3. **TypeScript/Node** - Web-native. Rechazado por: dependency hell, menos afinidad con ML.

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
