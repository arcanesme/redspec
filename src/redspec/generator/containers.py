"""Create draw.io container objects for grouping resources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from drawpyo.diagram import Object

if TYPE_CHECKING:
    from drawpyo import Page

    from redspec.models.resource import ResourceDef


@dataclass(frozen=True)
class _ContainerStyle:
    """Container visual style split into baseStyle (non-property) and direct properties."""

    # Attributes that go into baseStyle (not settable as Object properties)
    base: str
    # Native drawpyo Object properties
    fill_color: str
    stroke_color: str
    rounded: int = 1
    dashed: bool = False


_STYLES: dict[str, _ContainerStyle] = {
    "resource-group": _ContainerStyle(
        base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10;dashPattern=5 5",
        fill_color="#F5F5F5",
        stroke_color="#666666",
        dashed=True,
    ),
    "vnet": _ContainerStyle(
        base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10",
        fill_color="#DAE8FC",
        stroke_color="#6C8EBF",
    ),
    "virtual-network": _ContainerStyle(
        base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10",
        fill_color="#DAE8FC",
        stroke_color="#6C8EBF",
    ),
    "subnet": _ContainerStyle(
        base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10",
        fill_color="#E1D5E7",
        stroke_color="#9673A6",
    ),
    "subscription": _ContainerStyle(
        base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10",
        fill_color="#FFF2CC",
        stroke_color="#D6B656",
    ),
}

_DEFAULT_STYLE = _ContainerStyle(
    base="container=1;collapsible=0;html=1;fontStyle=1;verticalAlign=top;align=left;spacingLeft=10",
    fill_color="#F5F5F5",
    stroke_color="#666666",
)


def create_container(
    resource: ResourceDef,
    page: Page,
    parent: Object | None = None,
) -> Object:
    """Create a drawpyo container Object for a grouping resource."""
    raw = resource.type.lower()
    key = raw.split("/", 1)[-1] if "/" in raw else raw
    cs = _STYLES.get(key, _DEFAULT_STYLE)

    obj = Object(
        value=resource.name,
        width=200,
        height=200,
        page=page,
    )
    if parent is not None:
        obj.parent = parent

    obj.baseStyle = cs.base
    obj.rounded = cs.rounded
    obj.whiteSpace = "wrap"
    obj.fillColor = cs.fill_color
    obj.strokeColor = cs.stroke_color
    obj.dashed = cs.dashed

    return obj
