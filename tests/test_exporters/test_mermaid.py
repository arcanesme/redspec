"""Tests for Mermaid export."""

from redspec.exporters.mermaid import export_mermaid
from redspec.models.diagram import DiagramSpec


class TestExportMermaid:
    def test_minimal_spec(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
            "connections": [{"from": "vm1", "to": "vm2", "label": "link"}],
        })
        result = export_mermaid(spec)
        assert "flowchart" in result
        assert "vm1" in result
        assert "vm2" in result
        assert "link" in result

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
        result = export_mermaid(spec)
        assert "subgraph" in result
        assert "end" in result

    def test_dashed_edge(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b", "style": "dashed"}],
        })
        result = export_mermaid(spec)
        assert "-.->" in result

    def test_direction_lr(self):
        spec = DiagramSpec.model_validate({
            "diagram": {"direction": "LR"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        result = export_mermaid(spec)
        assert "flowchart LR" in result
