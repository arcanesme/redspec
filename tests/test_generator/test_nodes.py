"""Tests for node creation."""

from drawpyo import File, Page
from drawpyo.diagram import Object

from redspec.icons.embedder import embed_svg
from redspec.icons.registry import IconRegistry
from redspec.models.resource import ResourceDef


def test_create_node_with_icon(mock_icon_dir):
    from redspec.generator.nodes import create_node

    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)

    registry = IconRegistry(icon_dir=mock_icon_dir)
    resource = ResourceDef(type="azure/app-service", name="my-app")

    node = create_node(resource, page, registry, embed_svg)
    assert isinstance(node, Object)
    assert node.value == "my-app"
    assert node.geometry.width == 64
    assert node.geometry.height == 64


def test_create_node_fallback_no_icon(tmp_path):
    from redspec.generator.nodes import create_node

    empty = tmp_path / "empty"
    empty.mkdir()

    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)

    registry = IconRegistry(icon_dir=empty)
    resource = ResourceDef(type="azure/nonexistent-xyz", name="unknown-res")

    node = create_node(resource, page, registry, embed_svg)
    assert isinstance(node, Object)
    assert node.value == "unknown-res"


def test_create_node_with_parent(mock_icon_dir):
    from redspec.generator.nodes import create_node

    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)

    registry = IconRegistry(icon_dir=mock_icon_dir)
    parent_obj = Object(value="parent", page=page, width=400, height=300)

    resource = ResourceDef(type="azure/app-service", name="child-app")
    node = create_node(resource, page, registry, embed_svg, parent=parent_obj)
    assert node.parent == parent_obj
