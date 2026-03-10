# RAISE-472 Retrospective

## Fix verifica root cause (no síntoma)

Root cause: adaptadores MCP no verificaban result.is_error antes de parsear.
Fix: verificación explícita antes de cada parse — propaga McpBridgeError al CLI.
No es workaround — honra el contrato del protocolo MCP estándar.

## Regression tests verdes

9 tests nuevos: 7 en TestIsErrorPropagation (McpJiraAdapter) + 2 en
TestIsErrorPropagation (DeclarativeMcpAdapter). Todos verdes.

## Sin regresiones

323/323 tests de adapter pasan. 3 fallos pre-existentes (rai_core rename, no relacionados).

## Decisión de diseño: _dispatch vs métodos individuales

McpJiraAdapter: is_error check por método (7 puntos) — necesario porque cada método
tiene su propia lógica de parsing y el check es parte del contrato explícito.

DeclarativeMcpAdapter: is_error check en _dispatch() — un solo punto cubre todos
los métodos porque _dispatch es la única vía de llamada MCP en ese adapter. Más DRY.

## Patrón a capturar

Integración con sistemas externos vía protocolo MCP: siempre verificar result.is_error
antes de parsear. Es el contrato del protocolo, no un edge case. Silenciarlo produce
salida vacía sin diagnóstico — UX peor que un crash explícito.
