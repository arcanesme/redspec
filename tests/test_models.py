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

    def test_color_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "color": "#0078D4"})
        assert c.color == "#0078D4"

    def test_penwidth_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "penwidth": "2.5"})
        assert c.penwidth == "2.5"

    def test_color_and_penwidth_default_none(self):
        c = ConnectionDef(**{"from": "a", "to": "b"})
        assert c.color is None
        assert c.penwidth is None

    def test_arrowhead_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "arrowhead": "vee"})
        assert c.arrowhead == "vee"

    def test_arrowtail_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "arrowtail": "diamond"})
        assert c.arrowtail == "diamond"

    def test_direction_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "direction": "both"})
        assert c.direction == "both"

    def test_minlen_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "minlen": "2"})
        assert c.minlen == "2"

    def test_constraint_field(self):
        c = ConnectionDef(**{"from": "a", "to": "b", "constraint": "false"})
        assert c.constraint == "false"

    def test_new_fields_default_none(self):
        c = ConnectionDef(**{"from": "a", "to": "b"})
        assert c.arrowhead is None
        assert c.arrowtail is None
        assert c.direction is None
        assert c.minlen is None
        assert c.constraint is None


class TestDiagramMeta:
    def test_defaults(self):
        m = DiagramMeta()
        assert m.name == "Azure Architecture"
        assert m.layout == "auto"
        assert m.direction == "TB"
        assert m.theme == "default"
        assert m.dpi == 150

    def test_custom_values(self):
        m = DiagramMeta(name="My Diagram", layout="manual")
        assert m.name == "My Diagram"

    def test_direction_uppercased(self):
        m = DiagramMeta(direction="lr")
        assert m.direction == "LR"

    def test_direction_valid_values(self):
        for d in ("TB", "LR", "BT", "RL"):
            m = DiagramMeta(direction=d)
            assert m.direction == d

    def test_direction_invalid_raises(self):
        with pytest.raises(ValidationError, match="direction"):
            DiagramMeta(direction="XX")

    def test_theme_valid_values(self):
        for t in ("default", "light", "dark"):
            m = DiagramMeta(theme=t)
            assert m.theme == t

    def test_theme_invalid_raises(self):
        with pytest.raises(ValidationError, match="theme"):
            DiagramMeta(theme="neon")

    def test_dpi_valid_range(self):
        m = DiagramMeta(dpi=72)
        assert m.dpi == 72
        m = DiagramMeta(dpi=600)
        assert m.dpi == 600

    def test_dpi_too_low_raises(self):
        with pytest.raises(ValidationError, match="dpi"):
            DiagramMeta(dpi=50)

    def test_dpi_too_high_raises(self):
        with pytest.raises(ValidationError, match="dpi"):
            DiagramMeta(dpi=700)


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

    def test_spec_with_direction_and_theme(self):
        data = {
            "diagram": {"name": "Test", "direction": "LR", "theme": "dark", "dpi": 300},
        }
        spec = DiagramSpec.model_validate(data)
        assert spec.diagram.direction == "LR"
        assert spec.diagram.theme == "dark"
        assert spec.diagram.dpi == 300

    def test_spec_with_edge_color(self):
        data = {
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "color": "#FF0000", "penwidth": "2.0"},
            ],
        }
        spec = DiagramSpec.model_validate(data)
        assert spec.connections[0].color == "#FF0000"
        assert spec.connections[0].penwidth == "2.0"
