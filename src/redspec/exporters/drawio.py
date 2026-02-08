"""Export DiagramSpec to draw.io XML (mxGraphModel) format."""

from __future__ import annotations

from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element, SubElement, tostring

if TYPE_CHECKING:
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef


def _add_resource(
    parent: Element,
    resource: ResourceDef,
    id_counter: list[int],
    parent_id: str = "1",
    x: int = 40,
    y: int = 40,
) -> str:
    """Add a resource as an mxCell. Returns the cell ID."""
    cell_id = str(id_counter[0])
    id_counter[0] += 1

    if resource.children:
        cell = SubElement(parent, "mxCell", {
            "id": cell_id,
            "value": resource.name,
            "style": "group;rounded=1;whiteSpace=wrap;",
            "vertex": "1",
            "connectable": "0",
            "parent": parent_id,
        })
        SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y),
            "width": "300", "height": "200",
            "as": "geometry",
        })
        child_y = 40
        for child in resource.children:
            _add_resource(parent, child, id_counter, parent_id=cell_id, x=20, y=child_y)
            child_y += 80
    else:
        cell = SubElement(parent, "mxCell", {
            "id": cell_id,
            "value": resource.name,
            "style": "rounded=1;whiteSpace=wrap;html=1;",
            "vertex": "1",
            "parent": parent_id,
        })
        SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y),
            "width": "120", "height": "60",
            "as": "geometry",
        })

    return cell_id


def export_drawio(spec: DiagramSpec) -> str:
    """Convert a DiagramSpec to draw.io XML format."""
    root = Element("mxGraphModel")
    root_cell = SubElement(root, "root")

    # Required draw.io parent cells
    SubElement(root_cell, "mxCell", {"id": "0"})
    SubElement(root_cell, "mxCell", {"id": "1", "parent": "0"})

    id_counter = [2]
    name_to_id: dict[str, str] = {}

    # Build resources
    x = 40
    for resource in spec.resources:
        cell_id = _add_resource(root_cell, resource, id_counter, x=x)
        _collect_ids(resource, cell_id, name_to_id, id_counter)
        x += 200

    # Build connections
    for conn in spec.connections:
        edge_id = str(id_counter[0])
        id_counter[0] += 1
        src_id = name_to_id.get(conn.source, "1")
        tgt_id = name_to_id.get(conn.to, "1")

        style = "edgeStyle=orthogonalEdgeStyle;rounded=1;"
        if conn.style == "dashed":
            style += "dashed=1;"

        edge = SubElement(root_cell, "mxCell", {
            "id": edge_id,
            "value": conn.label or "",
            "style": style,
            "edge": "1",
            "source": src_id,
            "target": tgt_id,
            "parent": "1",
        })
        SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})

    return tostring(root, encoding="unicode")


def _collect_ids(
    resource: ResourceDef,
    start_id: str,
    name_to_id: dict[str, str],
    id_counter: list[int],
) -> None:
    """Map resource names to their mxCell IDs."""
    name_to_id[resource.name] = start_id
    # For children, IDs are assigned sequentially after the parent
    # We need to re-trace the ID assignment order
    if resource.children:
        # The parent used start_id. Children start at start_id + 1
        child_id = int(start_id) + 1
        for child in resource.children:
            _collect_ids(child, str(child_id), name_to_id, id_counter)
            child_id += 1 + _count_descendants(child)


def _count_descendants(resource: ResourceDef) -> int:
    """Count total descendants of a resource."""
    count = 0
    for child in resource.children:
        count += 1 + _count_descendants(child)
    return count
