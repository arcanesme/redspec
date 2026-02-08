"""Diagram diff: compute structural changes between two specs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redspec.models.diagram import DiagramSpec
    from redspec.models.resource import ResourceDef


@dataclass
class DiffResult:
    """Structured diff between two DiagramSpecs."""

    added_resources: list[str] = field(default_factory=list)
    removed_resources: list[str] = field(default_factory=list)
    added_connections: list[tuple[str, str]] = field(default_factory=list)
    removed_connections: list[tuple[str, str]] = field(default_factory=list)
    changed_connections: list[tuple[str, str]] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (
            self.added_resources
            or self.removed_resources
            or self.added_connections
            or self.removed_connections
            or self.changed_connections
        )


def _collect_names(resources: list[ResourceDef]) -> set[str]:
    names: set[str] = set()
    for r in resources:
        names.add(r.name)
        names.update(_collect_names(r.children))
    return names


def _collect_connections(spec: DiagramSpec) -> dict[tuple[str, str], dict]:
    conns: dict[tuple[str, str], dict] = {}
    for c in spec.connections:
        key = (c.source, c.to)
        conns[key] = {
            "label": c.label,
            "style": c.style,
            "color": c.color,
        }
    return conns


def diff_specs(old: DiagramSpec, new: DiagramSpec) -> DiffResult:
    """Compute structural diff between two DiagramSpecs."""
    old_names = _collect_names(old.resources)
    new_names = _collect_names(new.resources)

    old_conns = _collect_connections(old)
    new_conns = _collect_connections(new)

    result = DiffResult(
        added_resources=sorted(new_names - old_names),
        removed_resources=sorted(old_names - new_names),
        added_connections=sorted(set(new_conns) - set(old_conns)),
        removed_connections=sorted(set(old_conns) - set(new_conns)),
    )

    # Check for changed connections (same from/to but different attrs)
    for key in set(old_conns) & set(new_conns):
        if old_conns[key] != new_conns[key]:
            result.changed_connections.append(key)
    result.changed_connections.sort()

    return result
