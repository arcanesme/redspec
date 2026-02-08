"""Render a visual diff between two DiagramSpecs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from diagrams import Cluster, Diagram, Edge
from diagrams.azure.general import Resource

from redspec.diff import DiffResult, diff_specs
from redspec.generator.node_mapper import resolve_node_class

if TYPE_CHECKING:
    from diagrams import Node

    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef


def _create_diff_node(name: str, resource_type: str, color: str) -> Node:
    """Create a node with a colored label for diff visualization."""
    node_cls = resolve_node_class(resource_type)
    if node_cls is not None:
        return node_cls(name)
    return Resource(name)


def _collect_type_map(resources: list[ResourceDef]) -> dict[str, str]:
    """Map resource names to types."""
    result: dict[str, str] = {}
    for r in resources:
        result[r.name] = r.type
        result.update(_collect_type_map(r.children))
    return result


def render_diff(
    old: DiagramSpec,
    new: DiagramSpec,
    output_path: str,
    out_format: str = "svg",
) -> Path:
    """Render a visual diff diagram.

    Added nodes in green cluster, removed in red cluster, unchanged in default.
    """
    result = diff_specs(old, new)

    old_types = _collect_type_map(old.resources)
    new_types = _collect_type_map(new.resources)
    all_types = {**old_types, **new_types}

    out = Path(output_path)
    filename = str(out.with_suffix(""))

    name_to_node: dict[str, Node] = {}

    with Diagram(
        name="Diagram Diff",
        filename=filename,
        outformat=out_format,
        show=False,
    ):
        # Added resources (green)
        if result.added_resources:
            with Cluster("Added", graph_attr={"bgcolor": "#00C85320", "pencolor": "#00C853", "style": "dashed,rounded"}):
                for name in result.added_resources:
                    rtype = all_types.get(name, "resource")
                    node = _create_diff_node(name, rtype, "#00C853")
                    name_to_node[name] = node

        # Removed resources (red)
        if result.removed_resources:
            with Cluster("Removed", graph_attr={"bgcolor": "#FF444420", "pencolor": "#FF4444", "style": "dashed,rounded"}):
                for name in result.removed_resources:
                    rtype = all_types.get(name, "resource")
                    node = _create_diff_node(name, rtype, "#FF4444")
                    name_to_node[name] = node

        # Unchanged resources
        unchanged = (set(old_types) & set(new_types)) - set(result.added_resources) - set(result.removed_resources)
        for name in sorted(unchanged):
            rtype = all_types.get(name, "resource")
            node = _create_diff_node(name, rtype, "#888888")
            name_to_node[name] = node

        # Draw connections from new spec
        for conn in new.connections:
            if conn.source in name_to_node and conn.to in name_to_node:
                pair = (conn.source, conn.to)
                edge_attrs: dict[str, str] = {}
                if conn.label:
                    edge_attrs["label"] = conn.label
                if pair in result.added_connections:
                    edge_attrs["color"] = "#00C853"
                    edge_attrs["penwidth"] = "2.0"
                elif pair in result.changed_connections:
                    edge_attrs["color"] = "#FF9800"
                    edge_attrs["penwidth"] = "2.0"
                name_to_node[conn.source] >> Edge(**edge_attrs) >> name_to_node[conn.to]

    return Path(f"{filename}.{out_format}")
