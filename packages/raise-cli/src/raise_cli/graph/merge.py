"""Lógica pura de merge entre grafos local y server (S-KS.1).

Implementa Last-Writer-Wins (LWW) por node ID usando updated_at (ADR-103).
Módulo puro: sin I/O, sin efectos secundarios — completamente testeable.
"""

from __future__ import annotations

from datetime import UTC, datetime

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge

__all__ = ["merge_server_graph"]


def _parse_utc(ts: str) -> datetime:
    """Normaliza un timestamp ISO-8601 UTC a datetime aware.

    Acepta tanto el sufijo 'Z' (emitido por el CLI local) como '+00:00'
    (emitido por Pydantic/FastAPI en el servidor).  Ambas formas representan
    el mismo instante y deben compararse como iguales (Q3 — ADR-103).
    """
    normalized = ts.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    # astimezone convierte correctamente si ya es aware; attach UTC para naive
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _compare_timestamps(a: str | None, b: str | None) -> int:
    """Compara dos timestamps ISO-8601 UTC normalizando Z y +00:00.

    Reglas de asimetría:
    - a tiene timestamp, b no → a gana (1)
    - b tiene timestamp, a no → b gana (-1)
    - ninguno tiene timestamp → empate (0) → server gana por tie-break

    Returns:
        1  si a > b (a es más reciente, local gana)
        0  si empate o ambos None
        -1 si a < b (b es más reciente, server gana)
    """
    if a is not None and b is None:
        return 1  # local tiene timestamp, server no → local gana
    if a is None and b is not None:
        return -1  # server tiene timestamp, local no → server gana
    if a is None or b is None:
        return 0  # ambos None — empate
    # Normalizar a datetime aware para comparación correcta entre Z y +00:00
    # Tratar error de parseo como timestamp ausente → empate → server gana (Q-O1)
    try:
        dt_a = _parse_utc(a)
    except ValueError:
        return 0
    try:
        dt_b = _parse_utc(b)
    except ValueError:
        return 0
    if dt_a > dt_b:
        return 1
    if dt_a < dt_b:
        return -1
    return 0


def merge_server_graph(local: Graph, server: Graph) -> Graph:
    """Merge por node ID con Last-Writer-Wins por updated_at (ADR-103).

    Reglas:
    - Solo-server → añadir al resultado.
    - Solo-local  → conservar en el resultado.
    - Conflicto (mismo id): gana el nodo con updated_at más reciente.
      Empate o timestamp ausente → server gana (fuente canónica del equipo).
    - Preserva metadata['cartridge_name'] del nodo ganador.

    Args:
        local: Graph local del proyecto (fuente de verdad local).
        server: Graph descargado del servidor (fuente canónica del equipo).

    Returns:
        Nuevo Graph con todos los nodos y aristas del merge.
    """
    merged = Graph()

    # Índice de nodos
    local_ids: set[str] = {str(nid) for nid in local.graph.nodes()}
    server_ids: set[str] = {str(nid) for nid in server.graph.nodes()}

    # Procesar nodos
    for node_id in local_ids | server_ids:
        local_node = local.get_concept(node_id) if node_id in local_ids else None
        server_node = server.get_concept(node_id) if node_id in server_ids else None

        if local_node is None and server_node is not None:
            # Solo-server → añadir
            merged.add_concept(server_node)
        elif server_node is None and local_node is not None:
            # Solo-local → conservar
            merged.add_concept(local_node)
        elif local_node is not None and server_node is not None:
            # Conflicto → LWW
            cmp = _compare_timestamps(local_node.updated_at, server_node.updated_at)
            if cmp > 0:
                # Local más reciente → local gana
                merged.add_concept(local_node)
            else:
                # Server más reciente, empate, o sin timestamps → server gana
                merged.add_concept(server_node)

    # Incluir aristas de ambos grafos
    for source, target, _key, attrs in local.graph.edges(keys=True, data=True):
        edge = GraphEdge(
            source=str(source),
            target=str(target),
            type=str(attrs.get("type", "")),
            weight=float(attrs.get("weight", 1.0)),
            metadata={k: v for k, v in attrs.items() if k not in ("type", "weight")},
        )
        merged.add_relationship(edge)

    for source, target, _key, attrs in server.graph.edges(keys=True, data=True):
        edge = GraphEdge(
            source=str(source),
            target=str(target),
            type=str(attrs.get("type", "")),
            weight=float(attrs.get("weight", 1.0)),
            metadata={k: v for k, v in attrs.items() if k not in ("type", "weight")},
        )
        merged.add_relationship(edge)

    return merged
