"""Tests for container creation."""

from drawpyo import File, Page
from drawpyo.diagram import Object

from redspec.generator.containers import create_container
from redspec.models.resource import ResourceDef


def _make_page():
    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)
    return page


def test_resource_group_container():
    page = _make_page()
    resource = ResourceDef(type="azure/resource-group", name="rg-main")
    container = create_container(resource, page)
    assert isinstance(container, Object)
    assert container.value == "rg-main"


def test_vnet_container():
    page = _make_page()
    resource = ResourceDef(type="azure/vnet", name="main-vnet")
    container = create_container(resource, page)
    assert isinstance(container, Object)
    assert container.value == "main-vnet"


def test_subnet_container():
    page = _make_page()
    resource = ResourceDef(type="azure/subnet", name="app-subnet")
    container = create_container(resource, page)
    assert isinstance(container, Object)


def test_container_with_parent():
    page = _make_page()
    parent = Object(value="parent", page=page, width=400, height=300)
    resource = ResourceDef(type="azure/resource-group", name="rg")
    container = create_container(resource, page, parent=parent)
    assert container.parent == parent


def test_unknown_container_type_uses_default():
    page = _make_page()
    resource = ResourceDef(type="azure/custom-group", name="custom")
    container = create_container(resource, page)
    assert isinstance(container, Object)
    assert container.value == "custom"
