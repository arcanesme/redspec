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
    # --- AWS ---
    "aws/vpc": {"bgcolor": "#FF990020", "pencolor": "#FF9900"},
    "aws/subnet": {"bgcolor": "#FF990010", "pencolor": "#CC7A00", "style": "dashed,rounded"},
    "aws/region": {"bgcolor": "#23282020", "pencolor": "#232F3E", "style": "dashed"},
    # --- GCP ---
    "gcp/vpc": {"bgcolor": "#4285F420", "pencolor": "#4285F4"},
    "gcp/subnet": {"bgcolor": "#4285F410", "pencolor": "#3367D6", "style": "dashed,rounded"},
    # --- K8S ---
    "namespace": {"bgcolor": "#326CE520", "pencolor": "#326CE5"},
}

DEFAULT_CLUSTER_STYLE: dict[str, str] = {
    "bgcolor": "#F5F5F580",
    "pencolor": "#666666",
}

_DARK_CLUSTER_STYLES: dict[str, dict[str, str]] = {
    "resource-group": {"bgcolor": "#0D1B2A70", "pencolor": "#0078D4", "style": "dashed,rounded,filled"},
    "resource-groups": {"bgcolor": "#0D1B2A70", "pencolor": "#0078D4", "style": "dashed,rounded,filled"},
    "vnet": {"bgcolor": "#0A264760", "pencolor": "#00B4D8"},
    "virtual-network": {"bgcolor": "#0A264760", "pencolor": "#00B4D8"},
    "virtual-networks": {"bgcolor": "#0A264760", "pencolor": "#00B4D8"},
    "subnet": {"bgcolor": "#0D213760", "pencolor": "#5C6BC0"},
    "subnets": {"bgcolor": "#0D213760", "pencolor": "#5C6BC0"},
    "subscription": {"bgcolor": "#1A150060", "pencolor": "#FFB300"},
    "subscriptions": {"bgcolor": "#1A150060", "pencolor": "#FFB300"},
}

_DARK_DEFAULT_CLUSTER_STYLE: dict[str, str] = {
    "bgcolor": "#0D1B2A70",
    "pencolor": "#0078D4",
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
    # AWS
    "aws/vpc",
    "aws/subnet",
    "aws/region",
    # GCP
    "gcp/vpc",
    "gcp/subnet",
    # K8S
    "namespace",
})


def get_cluster_style(
    resource_type: str,
    theme: dict[str, dict[str, Any]] | None = None,
    theme_name: str = "default",
) -> dict[str, str]:
    """Return Graphviz graph_attr dict for a container type.

    When *theme* is provided, the theme's ``cluster_base`` is used as defaults
    underneath the type-specific color overrides.  When *theme_name* is
    ``"dark"`` or ``"presentation"``, dark-specific container colors are used.
    """
    key = resource_type.lower()

    # Try the full key first (for namespaced types like aws/vpc)
    if theme_name in ("dark", "presentation"):
        type_style = _DARK_CLUSTER_STYLES.get(key)
        if type_style is None and "/" in key:
            type_style = _DARK_CLUSTER_STYLES.get(key.split("/", 1)[1])
        if type_style is None:
            type_style = _DARK_DEFAULT_CLUSTER_STYLE
    else:
        type_style = CLUSTER_STYLES.get(key)
        if type_style is None and "/" in key:
            type_style = CLUSTER_STYLES.get(key.split("/", 1)[1])
        if type_style is None:
            type_style = DEFAULT_CLUSTER_STYLE

    if theme is None:
        return dict(type_style)

    merged: dict[str, str] = {}
    merged.update(theme["cluster_base"])
    merged.update(type_style)
    return merged


def is_container_type(resource_type: str) -> bool:
    """Check if a resource type should render as a Cluster."""
    key = resource_type.lower()
    # Check full key first (e.g. "aws/vpc")
    if key in CONTAINER_TYPES:
        return True
    # Then check stripped suffix (e.g. "resource-group" from "azure/resource-group")
    if "/" in key:
        suffix = key.split("/", 1)[1]
        return suffix in CONTAINER_TYPES
    return key in CONTAINER_TYPES
