"""Container styling for Diagrams Cluster graph_attr."""

from __future__ import annotations

from typing import Any

CLUSTER_STYLES: dict[str, dict[str, str]] = {
    "resource-group": {
        "bgcolor": "#F5F5F580",
        "pencolor": "#666666",
        "style": "dashed,rounded",
    },
    "resource-groups": {
        "bgcolor": "#F5F5F580",
        "pencolor": "#666666",
        "style": "dashed,rounded",
    },
    "vnet": {
        "bgcolor": "#DAE8FC80",
        "pencolor": "#6C8EBF",
    },
    "virtual-network": {
        "bgcolor": "#DAE8FC80",
        "pencolor": "#6C8EBF",
    },
    "virtual-networks": {
        "bgcolor": "#DAE8FC80",
        "pencolor": "#6C8EBF",
    },
    "subnet": {
        "bgcolor": "#E1D5E780",
        "pencolor": "#9673A6",
    },
    "subnets": {
        "bgcolor": "#E1D5E780",
        "pencolor": "#9673A6",
    },
    "subscription": {
        "bgcolor": "#FFF2CC80",
        "pencolor": "#D6B656",
    },
    "subscriptions": {
        "bgcolor": "#FFF2CC80",
        "pencolor": "#D6B656",
    },
}

DEFAULT_CLUSTER_STYLE: dict[str, str] = {
    "bgcolor": "#F5F5F580",
    "pencolor": "#666666",
}


# Container types that render as Clusters rather than leaf nodes
CONTAINER_TYPES: frozenset[str] = frozenset({
    "resource-group",
    "resource-groups",
    "vnet",
    "virtual-network",
    "virtual-networks",
    "subnet",
    "subnets",
    "subscription",
    "subscriptions",
})


def get_cluster_style(
    resource_type: str,
    theme: dict[str, dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Return Graphviz graph_attr dict for a container type.

    When *theme* is provided, the theme's ``cluster_base`` is used as defaults
    underneath the type-specific color overrides.
    """
    key = resource_type.lower()
    if "/" in key:
        key = key.split("/", 1)[1]
    type_style = CLUSTER_STYLES.get(key, DEFAULT_CLUSTER_STYLE)

    if theme is None:
        return dict(type_style)

    merged: dict[str, str] = {}
    merged.update(theme["cluster_base"])
    merged.update(type_style)
    return merged


def is_container_type(resource_type: str) -> bool:
    """Check if a resource type should render as a Cluster."""
    key = resource_type.lower()
    if "/" in key:
        key = key.split("/", 1)[1]
    return key in CONTAINER_TYPES
