"""Diagrams-based renderer: DiagramSpec -> PNG/SVG/PDF."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from diagrams import Cluster, Diagram, Edge

from redspec.exceptions import ConnectionTargetNotFoundError
from redspec.generator.node_mapper import resolve_node_class
from redspec.generator.style_map import get_cluster_style, is_container_type
from redspec.generator.themes import get_theme

if TYPE_CHECKING:
    from typing import Any

    from diagrams import Node

    from redspec.icons.registry import IconRegistry
    from redspec.models import DiagramSpec
    from redspec.models.resource import ConnectionDef, ResourceDef


def _create_node(
    resource: ResourceDef,
    icon_registry: IconRegistry | None,
) -> Node:
    """Create a Diagrams node for a leaf resource.

    Uses the built-in Azure node class if available, otherwise falls back
    to ``diagrams.custom.Custom`` with an icon from the registry, or a
    generic node.
    """
    node_cls = resolve_node_class(resource.type)
    if node_cls is not None:
        return node_cls(resource.name)

    # Try custom icon from registry
    if icon_registry is not None:
        icon_path = icon_registry.resolve(resource.type)
        if icon_path is not None:
            from diagrams.custom import Custom

            return Custom(resource.name, str(icon_path))

    # Fallback: use a generic resource node
    from diagrams.azure.general import Resource

    return Resource(resource.name)


def _process_resource(
    resource: ResourceDef,
    icon_registry: IconRegistry | None,
    name_to_node: dict[str, Node],
    theme: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Recursively create Diagrams nodes/clusters for a resource tree."""
    if is_container_type(resource.type):
        style = get_cluster_style(resource.type, theme=theme)
        with Cluster(resource.name, graph_attr=style):
            for child in resource.children:
                _process_resource(child, icon_registry, name_to_node, theme=theme)
    else:
        node = _create_node(resource, icon_registry)
        name_to_node[resource.name] = node


def _create_edges(
    connections: list[ConnectionDef],
    name_to_node: dict[str, Node],
) -> None:
    """Create Diagrams edges between nodes."""
    for conn in connections:
        if conn.source not in name_to_node:
            raise ConnectionTargetNotFoundError(conn.source, field="from")
        if conn.to not in name_to_node:
            raise ConnectionTargetNotFoundError(conn.to, field="to")

        source = name_to_node[conn.source]
        target = name_to_node[conn.to]

        edge_attrs: dict[str, str] = {}
        if conn.label:
            edge_attrs["label"] = conn.label
        if conn.style == "dashed":
            edge_attrs["style"] = "dashed"
        if conn.color:
            edge_attrs["color"] = conn.color
        if conn.penwidth:
            edge_attrs["penwidth"] = conn.penwidth
        for attr in ("arrowhead", "arrowtail", "direction", "minlen", "constraint"):
            val = getattr(conn, attr, None)
            if val is not None:
                edge_attrs[attr] = val

        source >> Edge(**edge_attrs) >> target


def render(
    spec: DiagramSpec,
    output_path: str,
    icon_registry: IconRegistry | None = None,
    strict: bool = False,
    out_format: str = "png",
    direction_override: str | None = None,
    dpi_override: int | None = None,
) -> Path:
    """Render a DiagramSpec to an image file using Diagrams (Graphviz).

    Returns the Path to the generated file.
    """
    theme = get_theme(spec.diagram.theme)

    direction = direction_override or spec.diagram.direction
    dpi = dpi_override or spec.diagram.dpi

    graph_attr = dict(theme["graph_attr"])
    graph_attr["dpi"] = str(dpi)

    node_attr = dict(theme["node_attr"])
    edge_attr = dict(theme["edge_attr"])

    out = Path(output_path)
    # Diagrams appends the format extension itself, so we give it a stem
    filename = str(out.with_suffix(""))

    name_to_node: dict[str, Node] = {}

    with Diagram(
        name=spec.diagram.name,
        filename=filename,
        outformat=out_format,
        show=False,
        direction=direction,
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        for resource in spec.resources:
            _process_resource(resource, icon_registry, name_to_node, theme=theme)

        _create_edges(spec.connections, name_to_node)

    # Diagrams creates <filename>.<format>
    generated = Path(f"{filename}.{out_format}")
    return generated
