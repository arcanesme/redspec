"""Create draw.io node objects for leaf resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from drawpyo.diagram import Object

from redspec.config import NODE_HEIGHT, NODE_WIDTH

if TYPE_CHECKING:
    from pathlib import Path

    from drawpyo import Page

    from redspec.icons.registry import IconRegistry
    from redspec.models.resource import ResourceDef


def create_node(
    resource: ResourceDef,
    page: Page,
    icon_registry: IconRegistry,
    embedder_fn: Callable[[Path], str],
    parent: Object | None = None,
) -> Object:
    """Create a drawpyo Object for a leaf resource.

    If the icon registry resolves the resource type, the node is rendered as an
    image using the data-URI returned by *embedder_fn*.  Otherwise a yellow
    rounded rectangle with the type name is used as a fallback.
    """
    svg_path = icon_registry.resolve(resource.type)

    if svg_path is not None:
        data_uri = embedder_fn(svg_path)
        obj = Object(
            value=resource.name,
            width=NODE_WIDTH,
            height=NODE_HEIGHT,
            page=page,
        )
        if parent is not None:
            obj.parent = parent
        obj.apply_style_string(
            "shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
            "imageAspect=fixed;aspect=fixed;"
            f"image={data_uri};"
        )
    else:
        # Fallback: yellow rounded rectangle
        obj = Object(
            value=resource.name,
            width=NODE_WIDTH + 40,
            height=NODE_HEIGHT,
            page=page,
        )
        if parent is not None:
            obj.parent = parent
        obj.apply_style_string(
            "rounded=1;whiteSpace=wrap;html=1;"
            "fillColor=#FFF2CC;strokeColor=#D6B656;"
        )

    return obj
