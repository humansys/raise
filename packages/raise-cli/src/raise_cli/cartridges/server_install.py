"""Install cartridges from the raise-server registry (S5877.5)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from raise_cli.cartridges.server_client import CartridgeServerClient
from raise_cli.cartridges.server_models import CartridgeNodeResult
from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
from raise_core.graph.models import GraphNode


def install_from_server(
    name: str,
    server_url: str,
    api_key: str,
    project_id: str,
    db_path: Path,
    policy: str = "optional",
    ensure_org_install: bool = True,
) -> int:
    """Fetch cartridge from server and write nodes to local graph.

    Returns the number of nodes installed.
    Raises CartridgeServerError on network/auth/404 errors.

    ensure_org_install=False skips the org-install call — used by sync,
    where the assignment already guarantees an org install exists (C-3)
    and sync must stay one-way (C-6: no server writes).
    """
    client = CartridgeServerClient(server_url, api_key)
    try:
        if ensure_org_install:
            client.org_install(name)
        detail = client.fetch_cartridge(name)
        nodes = [_to_graph_node(n, cartridge_name=name) for n in detail.nodes]
        backend = SQLiteGraphBackend(project_id, db_path)
        backend.upsert_cartridge_nodes(name, nodes)
        backend.register_cartridge_installation(
            name, "server", server_url, len(nodes), policy=policy
        )
        return len(nodes)
    finally:
        client.close()


def _to_graph_node(node: CartridgeNodeResult, *, cartridge_name: str) -> GraphNode:
    """Convert server node to local GraphNode."""
    return GraphNode(
        id=node.node_id,
        type=node.node_type,
        content=node.content,
        source_file=node.source_file,
        created=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        metadata={**node.properties, "cartridge_name": cartridge_name},
    )
