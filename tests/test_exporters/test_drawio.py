"""Tests for draw.io XML export."""

from redspec.exporters.drawio import export_drawio
from redspec.models.diagram import DiagramSpec


class TestExportDrawio:
    def test_minimal_spec(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
            "connections": [{"from": "vm1", "to": "vm2"}],
        })
        result = export_drawio(spec)
        assert "<mxGraphModel" in result
        assert "vm1" in result
        assert "vm2" in result

    def test_nested_spec(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {
                    "type": "azure/resource-group",
                    "name": "rg",
                    "children": [{"type": "azure/vm", "name": "vm1"}],
                },
            ],
        })
        result = export_drawio(spec)
        assert "<mxGraphModel" in result
        assert "group" in result

    def test_dashed_edge(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b", "style": "dashed"}],
        })
        result = export_drawio(spec)
        assert "dashed=1" in result
