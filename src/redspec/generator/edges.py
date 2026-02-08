"""Create draw.io edges (connections) between resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

from drawpyo.diagram import Edge, Object

from redspec.exceptions import ConnectionTargetNotFoundError

if TYPE_CHECKING:
    from drawpyo import Page

    from redspec.models.resource import ConnectionDef


def create_edges(
    connections: list[ConnectionDef],
    name_to_object: dict[str, Object],
    page: Page,
) -> list[Edge]:
    """Create Edge objects for every connection definition.

    Raises ConnectionTargetNotFoundError when a connection references a
    resource name that does not exist in *name_to_object*.
    """
    edges: list[Edge] = []

    for conn in connections:
        if conn.source not in name_to_object:
            raise ConnectionTargetNotFoundError(conn.source, field="from")
        if conn.to not in name_to_object:
            raise ConnectionTargetNotFoundError(conn.to, field="to")

        source_obj = name_to_object[conn.source]
        target_obj = name_to_object[conn.to]

        edge = Edge(
            source=source_obj,
            target=target_obj,
            label=conn.label or "",
            page=page,
        )

        if conn.style == "dashed":
            edge.apply_style_string("dashed=1;dashPattern=5 5;")

        edges.append(edge)

    return edges
