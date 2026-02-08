"""Tests for the generation pipeline."""

import pytest

from redspec.exceptions import DuplicateResourceNameError
from redspec.generator.pipeline import (
    _collect_names,
    _validate_unique_names,
    generate,
)
from redspec.models.diagram import DiagramSpec
from redspec.models.resource import ResourceDef


class TestCollectNames:
    def test_flat(self):
        resources = [
            ResourceDef(type="azure/vm", name="a"),
            ResourceDef(type="azure/vm", name="b"),
        ]
        assert _collect_names(resources) == ["a", "b"]

    def test_nested(self):
        resources = [
            ResourceDef(
                type="azure/resource-group",
                name="rg",
                children=[ResourceDef(type="azure/vm", name="vm1")],
            ),
        ]
        assert _collect_names(resources) == ["rg", "vm1"]


class TestValidateUniqueNames:
    def test_unique_passes(self):
        resources = [
            ResourceDef(type="azure/vm", name="a"),
            ResourceDef(type="azure/vm", name="b"),
        ]
        _validate_unique_names(resources)  # Should not raise

    def test_duplicate_raises(self):
        resources = [
            ResourceDef(type="azure/vm", name="dup"),
            ResourceDef(type="azure/vm", name="dup"),
        ]
        with pytest.raises(DuplicateResourceNameError, match="dup"):
            _validate_unique_names(resources)


class TestGenerate:
    def test_generate_produces_file(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/app-service", "name": "web"},
                {"type": "azure/sql-database", "name": "db"},
            ],
            "connections": [{"from": "web", "to": "db"}],
        })
        output = tmp_path / "out.png"
        result = generate(spec, str(output))
        assert result.exists()

    def test_generate_rejects_duplicates(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "same"},
                {"type": "azure/vm", "name": "same"},
            ],
        })
        output = tmp_path / "dup.png"
        with pytest.raises(DuplicateResourceNameError):
            generate(spec, str(output))

    def test_generate_accepts_embedder_fn_for_compat(self, tmp_path):
        """The embedder_fn parameter should be accepted but ignored."""
        spec = DiagramSpec.model_validate({
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "compat.png"
        result = generate(spec, str(output), embedder_fn=lambda x: "ignored")
        assert result.exists()

    def test_generate_forwards_glow_param(self, tmp_path):
        """generate() accepts glow parameter and forwards it without error."""
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Glow Pipeline", "theme": "dark"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "glow_pipeline.svg"
        result = generate(spec, str(output), out_format="svg", glow=True)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "<style" in content
