"""Export DiagramSpec to Mermaid flowchart syntax."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef

_DIRECTION_MAP = {"TB": "TD", "LR": "LR", "BT": "BU", "RL": "RL"}


def _sanitize_id(name: str) -> str:
    """Convert a resource name to a valid Mermaid node ID."""
    return name.replace("-", "_").replace(" ", "_")


def _process_resource(resource: ResourceDef, lines: list[str], depth: int = 0) -> None:
    """Recursively process resources into Mermaid syntax."""
    indent = "    " * depth
    sid = _sanitize_id(resource.name)

    if resource.children:
        lines.append(f"{indent}subgraph {sid}[{resource.name}]")
        for child in resource.children:
            _process_resource(child, lines, depth + 1)
        lines.append(f"{indent}end")
    else:
        lines.append(f"{indent}{sid}[{resource.name}]")


def export_mermaid(spec: DiagramSpec) -> str:
    """Convert a DiagramSpec to Mermaid flowchart syntax."""
    direction = _DIRECTION_MAP.get(spec.diagram.direction, "TD")
    lines: list[str] = [f"flowchart {direction}"]

    for resource in spec.resources:
        _process_resource(resource, lines, depth=1)

    for conn in spec.connections:
        src = _sanitize_id(conn.source)
        tgt = _sanitize_id(conn.to)
        if conn.label:
            if conn.style == "dashed":
                lines.append(f"    {src} -.->|{conn.label}| {tgt}")
            else:
                lines.append(f"    {src} -->|{conn.label}| {tgt}")
        else:
            if conn.style == "dashed":
                lines.append(f"    {src} -.-> {tgt}")
            else:
                lines.append(f"    {src} --> {tgt}")

    return "\n".join(lines) + "\n"
