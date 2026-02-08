"""Diagrams-based renderer: DiagramSpec -> PNG/SVG/PDF."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from diagrams import Cluster, Diagram, Edge

from redspec.exceptions import ConnectionTargetNotFoundError, IconNotFoundError
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
    strict: bool = False,
) -> Node:
    """Create a Diagrams node for a leaf resource."""
    node_cls = resolve_node_class(resource.type)
    if node_cls is not None:
        node = node_cls(resource.name)
    elif icon_registry is not None:
        icon_path = icon_registry.resolve(resource.type)
        if icon_path is not None:
            from diagrams.custom import Custom
            node = Custom(resource.name, str(icon_path))
        elif strict:
            raise IconNotFoundError(resource.type)
        else:
            from diagrams.azure.general import Resource
            node = Resource(resource.name)
    elif strict:
        raise IconNotFoundError(resource.type)
    else:
        from diagrams.azure.general import Resource
        node = Resource(resource.name)

    return node


def _process_resource(
    resource: ResourceDef,
    icon_registry: IconRegistry | None,
    name_to_node: dict[str, Node],
    theme: dict[str, dict[str, Any]] | None = None,
    theme_name: str = "default",
    strict: bool = False,
) -> None:
    """Recursively create Diagrams nodes/clusters for a resource tree."""
    if is_container_type(resource.type):
        style = get_cluster_style(resource.type, theme=theme, theme_name=theme_name)
        with Cluster(resource.name, graph_attr=style):
            for child in resource.children:
                _process_resource(
                    child, icon_registry, name_to_node,
                    theme=theme, theme_name=theme_name, strict=strict,
                )
    else:
        node = _create_node(resource, icon_registry, strict=strict)
        name_to_node[resource.name] = node


def _create_edges(
    connections: list[ConnectionDef],
    name_to_node: dict[str, Node],
    spec: DiagramSpec | None = None,
) -> None:
    """Create Diagrams edges between nodes."""
    # Build style lookup from connection_styles
    style_lookup: dict[str, dict[str, str]] = {}
    if spec and spec.connection_styles:
        for cs in spec.connection_styles:
            preset: dict[str, str] = {}
            if cs.color:
                preset["color"] = cs.color
            if cs.style == "dashed":
                preset["style"] = "dashed"
            if cs.penwidth:
                preset["penwidth"] = cs.penwidth
            if cs.arrowhead:
                preset["arrowhead"] = cs.arrowhead
            style_lookup[cs.name] = preset

    for conn in connections:
        if conn.source not in name_to_node:
            raise ConnectionTargetNotFoundError(conn.source, field="from")
        if conn.to not in name_to_node:
            raise ConnectionTargetNotFoundError(conn.to, field="to")

        source = name_to_node[conn.source]
        target = name_to_node[conn.to]

        # Start with preset style, then override with inline values
        edge_attrs: dict[str, str] = {}
        if conn.style_ref and conn.style_ref in style_lookup:
            edge_attrs.update(style_lookup[conn.style_ref])

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


_ZONE_STYLES: dict[str, dict[str, str]] = {
    "dmz": {"bgcolor": "#FFCCCC40", "pencolor": "#CC0000", "style": "dashed,rounded"},
    "private": {"bgcolor": "#CCE5FF40", "pencolor": "#0066CC", "style": "rounded"},
    "public": {"bgcolor": "#CCFFCC40", "pencolor": "#006600", "style": "rounded"},
}


def render(
    spec: DiagramSpec,
    output_path: str,
    icon_registry: IconRegistry | None = None,
    strict: bool = False,
    out_format: str = "png",
    direction_override: str | None = None,
    dpi_override: int | None = None,
    glow: bool | None = None,
) -> Path:
    """Render a DiagramSpec to an image file using Diagrams (Graphviz)."""
    theme = get_theme(spec.diagram.theme)

    direction = direction_override or spec.diagram.direction
    dpi = dpi_override or spec.diagram.dpi

    graph_attr = dict(theme["graph_attr"])
    graph_attr["dpi"] = str(dpi)

    node_attr = dict(theme["node_attr"])
    edge_attr = dict(theme["edge_attr"])

    out = Path(output_path)
    filename = str(out.with_suffix(""))

    name_to_node: dict[str, Node] = {}

    # Build a set of resource names that belong to zones
    zoned_resources: dict[str, str] = {}
    for zone in spec.zones:
        for rname in zone.resources:
            zoned_resources[rname] = zone.name

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
        # Render zones first
        zone_rendered_resources: set[str] = set()
        for zone in spec.zones:
            zone_style = _ZONE_STYLES.get(zone.style or "", {
                "bgcolor": "#F5F5F540",
                "pencolor": "#999999",
                "style": "rounded",
            })
            if theme:
                merged_style: dict[str, str] = {}
                merged_style.update(theme.get("cluster_base", {}))
                merged_style.update(zone_style)
            else:
                merged_style = dict(zone_style)

            with Cluster(zone.name, graph_attr=merged_style):
                for resource in spec.resources:
                    if resource.name in zone.resources:
                        _process_resource(
                            resource, icon_registry, name_to_node,
                            theme=theme, theme_name=spec.diagram.theme, strict=strict,
                        )
                        zone_rendered_resources.add(resource.name)

        # Render non-zoned resources
        for resource in spec.resources:
            if resource.name not in zone_rendered_resources:
                _process_resource(
                    resource, icon_registry, name_to_node,
                    theme=theme, theme_name=spec.diagram.theme, strict=strict,
                )

        _create_edges(spec.connections, name_to_node, spec=spec)

        # Legend
        if spec.diagram.legend and name_to_node:
            seen_types: set[str] = set()
            with Cluster("Legend", graph_attr={"bgcolor": "#FFFFFF20", "style": "rounded", "labeljust": "l"}):
                for resource in spec.resources:
                    _add_legend_types(resource, icon_registry, seen_types)

    generated = Path(f"{filename}.{out_format}")

    should_glow = glow if glow is not None else (spec.diagram.theme in ("dark", "presentation"))
    if out_format == "svg" and should_glow:
        from redspec.generator.svg_enhancer import enhance_svg
        enhance_svg(generated, spec.diagram.theme)

    # SVG animations
    if out_format == "svg" and spec.diagram.animation:
        from redspec.generator.svg_animator import animate_svg
        animate_svg(generated, spec.diagram.animation)

    return generated


def _add_legend_types(
    resource: ResourceDef,
    icon_registry: IconRegistry | None,
    seen_types: set[str],
) -> None:
    """Add legend entries for unique resource types."""
    if not is_container_type(resource.type) and resource.type not in seen_types:
        seen_types.add(resource.type)
        try:
            _create_node(
                type("_FakeResource", (), {"type": resource.type, "name": resource.type, "metadata": {}, "style": None})(),
                icon_registry,
                strict=False,
            )
        except Exception:
            pass

    for child in resource.children:
        _add_legend_types(child, icon_registry, seen_types)
