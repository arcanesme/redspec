"""Automatic layout: position nodes and size containers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from drawpyo.diagram import Object

from redspec.config import (
    CHILD_SPACING_X,
    CONTAINER_HEADER,
    CONTAINER_PADDING,
    LABEL_HEIGHT,
    NODE_HEIGHT,
    NODE_WIDTH,
)

if TYPE_CHECKING:
    from redspec.models.resource import ResourceDef


def _layout_recursive(
    resource: ResourceDef,
    name_to_object: dict[str, Object],
    name_to_container: dict[str, Object],
) -> tuple[float, float]:
    """Lay out *resource* and return its (width, height).

    For containers the children are positioned first (bottom-up) and the
    container is then resized to enclose them.  For leaf nodes the fixed
    node dimensions are returned.
    """
    if resource.name in name_to_container:
        container = name_to_container[resource.name]

        if not resource.children:
            container.geometry.width = 200
            container.geometry.height = 100
            return 200.0, 100.0

        cursor_x: float = CONTAINER_PADDING
        max_child_h: float = 0.0

        for child in resource.children:
            child_w, child_h = _layout_recursive(
                child, name_to_object, name_to_container
            )
            child_obj = name_to_object.get(child.name) or name_to_container.get(
                child.name
            )
            if child_obj is not None:
                child_obj.position = (cursor_x, CONTAINER_HEADER + CONTAINER_PADDING)
            cursor_x += child_w + CHILD_SPACING_X
            max_child_h = max(max_child_h, child_h)

        # Remove trailing spacing
        total_children_w = cursor_x - CHILD_SPACING_X
        container_w = max(total_children_w + CONTAINER_PADDING, 200)
        container_h = max_child_h + CONTAINER_HEADER + 2 * CONTAINER_PADDING

        container.geometry.width = container_w
        container.geometry.height = container_h

        return container_w, container_h

    # Leaf node
    obj = name_to_object.get(resource.name)
    if obj is not None:
        return float(obj.geometry.width), float(obj.geometry.height + LABEL_HEIGHT)

    return float(NODE_WIDTH), float(NODE_HEIGHT + LABEL_HEIGHT)


def layout_resources(
    resource_defs: list[ResourceDef],
    name_to_object: dict[str, Object],
    name_to_container: dict[str, Object],
) -> None:
    """Position all top-level resources and recursively size containers."""
    cursor_x: float = 50.0

    for resource in resource_defs:
        w, h = _layout_recursive(resource, name_to_object, name_to_container)

        top_obj = name_to_object.get(resource.name) or name_to_container.get(
            resource.name
        )
        if top_obj is not None:
            top_obj.position = (cursor_x, 50)

        cursor_x += w + CHILD_SPACING_X
