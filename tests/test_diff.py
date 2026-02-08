"""Tests for diagram diffing (A5)."""

from redspec.diff import diff_specs
from redspec.models.diagram import DiagramSpec


class TestDiffSpecs:
    def test_added_resources_detected(self):
        old = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        new = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
        })
        result = diff_specs(old, new)
        assert "vm2" in result.added_resources
        assert not result.removed_resources

    def test_removed_resources_detected(self):
        old = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/vm", "name": "vm2"},
            ],
        })
        new = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        result = diff_specs(old, new)
        assert "vm2" in result.removed_resources
        assert not result.added_resources

    def test_added_connections(self):
        old = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
        })
        new = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b"}],
        })
        result = diff_specs(old, new)
        assert ("a", "b") in result.added_connections

    def test_removed_connections(self):
        old = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b"}],
        })
        new = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
        })
        result = diff_specs(old, new)
        assert ("a", "b") in result.removed_connections

    def test_changed_connections(self):
        old = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b", "label": "old"}],
        })
        new = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [{"from": "a", "to": "b", "label": "new"}],
        })
        result = diff_specs(old, new)
        assert ("a", "b") in result.changed_connections

    def test_identical_specs_empty_diff(self):
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "vm1"}],
            "connections": [],
        })
        result = diff_specs(spec, spec)
        assert result.is_empty
