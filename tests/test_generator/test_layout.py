"""Tests for layout positioning."""

from drawpyo import File, Page
from drawpyo.diagram import Object

from redspec.generator.layout import layout_resources
from redspec.models.resource import ResourceDef


def _make_page():
    file = File(file_name="test.drawio", file_path="/tmp")
    page = Page(file=file, name="Test")
    file.add_page(page)
    return page


def test_layout_flat_resources():
    page = _make_page()
    r1 = ResourceDef(type="azure/vm", name="vm1")
    r2 = ResourceDef(type="azure/vm", name="vm2")

    obj1 = Object(value="vm1", page=page, width=64, height=64)
    obj2 = Object(value="vm2", page=page, width=64, height=64)

    name_to_object = {"vm1": obj1, "vm2": obj2}
    name_to_container = {}

    layout_resources([r1, r2], name_to_object, name_to_container)

    # First resource at x=50
    assert obj1.position[0] == 50
    assert obj1.position[1] == 50
    # Second resource to the right
    assert obj2.position[0] > obj1.position[0]
    assert obj2.position[1] == 50


def test_layout_container_with_children():
    page = _make_page()
    child_def = ResourceDef(type="azure/vm", name="vm1")
    container_def = ResourceDef(
        type="azure/resource-group", name="rg", children=[child_def]
    )

    container_obj = Object(value="rg", page=page, width=200, height=200)
    child_obj = Object(value="vm1", page=page, width=64, height=64, parent=container_obj)

    name_to_object = {"rg": container_obj, "vm1": child_obj}
    name_to_container = {"rg": container_obj}

    layout_resources([container_def], name_to_object, name_to_container)

    # Container should be positioned
    assert container_obj.position[0] == 50
    # Container should have been sized to fit child
    assert container_obj.geometry.width >= 64
    assert container_obj.geometry.height >= 64


def test_layout_empty_container():
    page = _make_page()
    container_def = ResourceDef(
        type="azure/resource-group", name="rg", children=[]
    )

    container_obj = Object(value="rg", page=page, width=200, height=200)

    name_to_object = {"rg": container_obj}
    name_to_container = {"rg": container_obj}

    layout_resources([container_def], name_to_object, name_to_container)

    assert container_obj.geometry.width == 200
    assert container_obj.geometry.height == 100
