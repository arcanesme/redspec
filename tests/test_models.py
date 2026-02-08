"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from redspec.models.resource import ConnectionDef, ResourceDef
from redspec.models.diagram import DiagramMeta, DiagramSpec


class TestResourceDef:
    def test_simple_resource(self):
        r = ResourceDef(type="azure/app-service", name="web-app")
        assert r.type == "azure/app-service"
        assert r.name == "web-app"
        assert r.children == []

    def test_resource_with_children(self):
        r = ResourceDef(
            type="azure/vnet",
            name="main-vnet",
            children=[
                ResourceDef(type="azure/subnet", name="sub1"),
                ResourceDef(type="azure/subnet", name="sub2"),
            ],
        )
        assert len(r.children) == 2
        assert r.children[0].name == "sub1"

    def test_deeply_nested(self):
        r = ResourceDef(
            type="azure/resource-group",
            name="rg",
            children=[
                ResourceDef(
                    type="azure/vnet",
                    name="vnet",
                    children=[
                        ResourceDef(
                            type="azure/subnet",
                            name="subnet",
                            children=[
                                ResourceDef(type="azure/vm", name="vm1"),
                            ],
                        )
                    ],
                )
            ],
        )
        assert r.children[0].children[0].children[0].name == "vm1"

    def test_missing_type_raises(self):
        with pytest.raises(ValidationError):
            ResourceDef(name="no-type")  # type: ignore[call-arg]

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            ResourceDef(type="azure/vm")  # type: ignore[call-arg]


class TestConnectionDef:
    def test_from_alias(self):
        c = ConnectionDef(**{"from": "web-app", "to": "db"})
        assert c.source == "web-app"
        assert c.to == "db"

    def test_with_label(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "label": "reads"})
        assert c.label == "reads"

    def test_with_dashed_style(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "style": "dashed"})
        assert c.style == "dashed"

    def test_label_defaults_none(self):
        c = ConnectionDef(**{"from": "a", "to": "b"})
        assert c.label is None
        assert c.style is None


class TestDiagramMeta:
    def test_defaults(self):
        m = DiagramMeta()
        assert m.name == "Azure Architecture"
        assert m.layout == "auto"

    def test_custom_values(self):
        m = DiagramMeta(name="My Diagram", layout="manual")
        assert m.name == "My Diagram"


class TestDiagramSpec:
    def test_from_dict(self):
        data = {
            "diagram": {"name": "Test", "layout": "auto"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
            "connections": [{"from": "vm1", "to": "vm2", "label": "link"}],
        }
        spec = DiagramSpec.model_validate(data)
        assert spec.diagram.name == "Test"
        assert len(spec.resources) == 2
        assert len(spec.connections) == 1
        assert spec.connections[0].source == "vm1"

    def test_empty_defaults(self):
        spec = DiagramSpec.model_validate({})
        assert spec.diagram.name == "Azure Architecture"
        assert spec.resources == []
        assert spec.connections == []

    def test_nested_resources(self):
        data = {
            "resources": [
                {
                    "type": "azure/resource-group",
                    "name": "rg",
                    "children": [{"type": "azure/vm", "name": "vm1"}],
                }
            ]
        }
        spec = DiagramSpec.model_validate(data)
        assert len(spec.resources[0].children) == 1
