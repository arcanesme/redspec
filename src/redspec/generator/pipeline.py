"""Main generation pipeline: YAML spec -> diagram image."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from redspec.exceptions import DuplicateResourceNameError
from redspec.generator.renderer import render

if TYPE_CHECKING:
    from redspec.icons.registry import IconRegistry
    from redspec.models import DiagramSpec
    from redspec.models.resource import ResourceDef


def _collect_names(resources: list[ResourceDef]) -> list[str]:
    """Flatten all resource names from the tree (pre-order)."""
    names: list[str] = []
    for r in resources:
        names.append(r.name)
        names.extend(_collect_names(r.children))
    return names


def _validate_unique_names(resources: list[ResourceDef]) -> None:
    """Raise DuplicateResourceNameError if any name appears more than once."""
    seen: set[str] = set()
    for name in _collect_names(resources):
        if name in seen:
            raise DuplicateResourceNameError(name)
        seen.add(name)


def generate(
    spec: DiagramSpec,
    output_path: str,
    icon_registry: IconRegistry | None = None,
    embedder_fn: Callable | None = None,
    strict: bool = False,
    out_format: str = "png",
    direction_override: str | None = None,
    dpi_override: int | None = None,
) -> Path:
    """Generate a diagram image from a DiagramSpec.

    Returns the Path to the written file.  The *embedder_fn* parameter is
    accepted for backward compatibility but ignored (Diagrams uses its own
    icon rendering).
    """
    _validate_unique_names(spec.resources)
    return render(
        spec,
        output_path,
        icon_registry=icon_registry,
        strict=strict,
        out_format=out_format,
        direction_override=direction_override,
        dpi_override=dpi_override,
    )
