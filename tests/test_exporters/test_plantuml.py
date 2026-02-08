"""Tests for PlantUML export."""

from redspec.exporters.plantuml import export_plantuml
from redspec.models.diagram import DiagramSpec


class TestExportPlantUML:
    def test_minimal_spec(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
            "connections": [{"from": "vm1", "to": "vm2", "label": "link"}],
        })
        result = export_plantuml(spec)
        assert "@startuml" in result
        assert "@enduml" in result
        assert "vm1" in result
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
        result = export_plantuml(spec)
        assert "package" in result

    def test_dashed_edge(self):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b", "style": "dashed"}],
        })
        result = export_plantuml(spec)
        assert "..>" in result
