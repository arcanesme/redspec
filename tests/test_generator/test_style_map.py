"""Tests for style_map: container type -> Cluster styling."""

from redspec.generator.style_map import (
    CONTAINER_TYPES,
    get_cluster_style,
    is_container_type,
)
from redspec.generator.themes import get_theme


class TestIsContainerType:
    def test_resource_group(self):
        assert is_container_type("azure/resource-group") is True

    def test_vnet(self):
        assert is_container_type("azure/vnet") is True

    def test_subnet(self):
        assert is_container_type("azure/subnet") is True

    def test_subscription(self):
        assert is_container_type("azure/subscription") is True

    def test_leaf_node(self):
        assert is_container_type("azure/app-service") is False

    def test_case_insensitive(self):
        assert is_container_type("Azure/Resource-Group") is True

    def test_without_namespace(self):
        assert is_container_type("resource-group") is True

    def test_virtual_network_alias(self):
        assert is_container_type("azure/virtual-network") is True


class TestGetClusterStyle:
    def test_resource_group_style(self):
        style = get_cluster_style("azure/resource-group")
        assert style["bgcolor"] == "#F5F5F580"
        assert style["pencolor"] == "#666666"
        assert style["style"] == "dashed,rounded"

    def test_vnet_style(self):
        style = get_cluster_style("azure/vnet")
        assert style["bgcolor"] == "#DAE8FC80"
        assert style["pencolor"] == "#6C8EBF"

    def test_subnet_style(self):
        style = get_cluster_style("azure/subnet")
        assert style["bgcolor"] == "#E1D5E780"
        assert style["pencolor"] == "#9673A6"

    def test_subscription_style(self):
        style = get_cluster_style("azure/subscription")
        assert style["bgcolor"] == "#FFF2CC80"
        assert style["pencolor"] == "#D6B656"

    def test_unknown_returns_default(self):
        style = get_cluster_style("azure/custom-group")
        assert style["bgcolor"] == "#F5F5F580"
        assert style["pencolor"] == "#666666"


class TestGetClusterStyleWithTheme:
    def test_theme_merges_cluster_base(self):
        theme = get_theme("default")
        style = get_cluster_style("azure/vnet", theme=theme)
        assert style["penwidth"] == "2.0"
        assert style["labeljust"] == "l"
        assert style["labelloc"] == "t"
        assert style["margin"] == "16"
        # Type-specific values are preserved
        assert style["bgcolor"] == "#DAE8FC80"
        assert style["pencolor"] == "#6C8EBF"

    def test_type_overrides_theme_base(self):
        theme = get_theme("default")
        style = get_cluster_style("azure/resource-group", theme=theme)
        # Type-specific style overrides theme base style
        assert style["style"] == "dashed,rounded"

    def test_dark_theme_cluster(self):
        theme = get_theme("dark")
        style = get_cluster_style("azure/subnet", theme=theme)
        assert style["fontcolor"] == "#CDD6F4"
        assert style["penwidth"] == "2.0"
        assert style["bgcolor"] == "#E1D5E780"

    def test_without_theme_no_extra_keys(self):
        style = get_cluster_style("azure/vnet")
        assert "penwidth" not in style
        assert "labeljust" not in style
        assert "labelloc" not in style
        assert "margin" not in style
