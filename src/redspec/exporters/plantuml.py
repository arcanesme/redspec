"""Export DiagramSpec to PlantUML syntax."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef

_DIRECTION_MAP = {"TB": "top to bottom direction", "LR": "left to right direction", "BT": "top to bottom direction", "RL": "left to right direction"}


def _process_resource(resource: ResourceDef, lines: list[str], depth: int = 0) -> None:
    """Recursively process resources into PlantUML syntax."""
    indent = "  " * depth
    if resource.children:
        lines.append(f"{indent}package \"{resource.name}\" {{")
        for child in resource.children:
            _process_resource(child, lines, depth + 1)
        lines.append(f"{indent}}}")
    else:
        lines.append(f"{indent}component \"{resource.name}\" as {resource.name.replace('-', '_')}")


def export_plantuml(spec: DiagramSpec) -> str:
    """Convert a DiagramSpec to PlantUML syntax."""
    lines: list[str] = ["@startuml"]

    direction = _DIRECTION_MAP.get(spec.diagram.direction, "top to bottom direction")
    lines.append(direction)
    lines.append("")

    for resource in spec.resources:
        _process_resource(resource, lines, depth=0)

    lines.append("")

    for conn in spec.connections:
        src = conn.source.replace("-", "_")
        tgt = conn.to.replace("-", "_")
        arrow = "..>" if conn.style == "dashed" else "-->"
        if conn.label:
            lines.append(f"{src} {arrow} {tgt} : {conn.label}")
        else:
            lines.append(f"{src} {arrow} {tgt}")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"
