"""Main generation pipeline: YAML spec -> .drawio file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from drawpyo import File, Page
from drawpyo.diagram import Object

from redspec.config import CONTAINER_TYPES
from redspec.exceptions import DuplicateResourceNameError
from redspec.generator.containers import create_container
from redspec.generator.edges import create_edges
from redspec.generator.layout import layout_resources
from redspec.generator.nodes import create_node

if TYPE_CHECKING:
    from redspec.icons.registry import IconRegistry
    from redspec.models import DiagramSpec
    from redspec.models.resource import ResourceDef


def _is_container_type(resource_type: str) -> bool:
    """Check if a resource type is a container, ignoring namespace prefix."""
    key = resource_type.lower()
    if key in CONTAINER_TYPES:
        return True
    # Strip namespace and check suffix only
    if "/" in key:
        suffix = key.split("/", 1)[1]
        return any(ct.endswith("/" + suffix) for ct in CONTAINER_TYPES)
    return False


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


def _process_resource(
    resource: ResourceDef,
    page: Page,
    icon_registry: IconRegistry,
    embedder_fn: Callable[[Path], str],
    name_to_object: dict[str, Object],
    name_to_container: dict[str, Object],
    parent: Object | None = None,
) -> None:
    """Recursively create drawpyo objects for a resource tree."""
    if _is_container_type(resource.type):
        container = create_container(resource, page, parent=parent)
        name_to_object[resource.name] = container
        name_to_container[resource.name] = container

        for child in resource.children:
            _process_resource(
                child,
                page,
                icon_registry,
                embedder_fn,
                name_to_object,
                name_to_container,
                parent=container,
            )
    else:
        node = create_node(
            resource, page, icon_registry, embedder_fn, parent=parent
        )
        name_to_object[resource.name] = node


def generate(
    spec: DiagramSpec,
    output_path: str,
    icon_registry: IconRegistry,
    embedder_fn: Callable[[Path], str],
    strict: bool = False,
) -> Path:
    """Generate a .drawio file from a DiagramSpec.

    Returns the Path to the written file.
    """
    # Validate unique names
    _validate_unique_names(spec.resources)

    out = Path(output_path)
    file = File(file_name=out.name, file_path=str(out.parent))
    page = Page(file=file, name=spec.diagram.name)

    name_to_object: dict[str, Object] = {}
    name_to_container: dict[str, Object] = {}

    # Build resource tree
    for resource in spec.resources:
        _process_resource(
            resource,
            page,
            icon_registry,
            embedder_fn,
            name_to_object,
            name_to_container,
        )

    # Create edges
    create_edges(spec.connections, name_to_object, page)

    # Layout
    layout_resources(spec.resources, name_to_object, name_to_container)

    # Write
    file.write(overwrite=True)

    return out
