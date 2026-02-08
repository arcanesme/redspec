"""Tests for the Diagrams-based renderer."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from redspec.exceptions import ConnectionTargetNotFoundError, IconNotFoundError
from redspec.generator.renderer import render
from redspec.models.diagram import DiagramSpec


class TestRender:
    def test_render_minimal(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Test"},
            "resources": [
                {"type": "azure/app-service", "name": "web-app"},
                {"type": "azure/sql-database", "name": "prod-db"},
            ],
            "connections": [
                {"from": "web-app", "to": "prod-db", "label": "SQL"},
            ],
        })
        output = tmp_path / "test.png"
        result = render(spec, str(output))
        assert result.exists()
        assert result.suffix == ".png"

    def test_render_svg_format(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "SVG Test"},
            "resources": [
                {"type": "azure/vm", "name": "my-vm"},
            ],
        })
        output = tmp_path / "test.svg"
        result = render(spec, str(output), out_format="svg")
        assert result.exists()
        assert result.suffix == ".svg"

    def test_render_nested_containers(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Nested Test"},
            "resources": [
                {
                    "type": "azure/resource-group",
                    "name": "rg-prod",
                    "children": [
                        {
                            "type": "azure/vnet",
                            "name": "main-vnet",
                            "children": [
                                {
                                    "type": "azure/subnet",
                                    "name": "app-subnet",
                                    "children": [
                                        {"type": "azure/app-service", "name": "web"},
                                    ],
                                },
                            ],
                        },
                        {"type": "azure/sql-database", "name": "db"},
                    ],
                },
            ],
            "connections": [
                {"from": "web", "to": "db", "label": "SQL"},
            ],
        })
        output = tmp_path / "nested.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_render_dashed_edge(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "style": "dashed"},
            ],
        })
        output = tmp_path / "dashed.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_render_missing_source_raises(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
            "connections": [
                {"from": "missing", "to": "vm1"},
            ],
        })
        output = tmp_path / "bad.png"
        with pytest.raises(ConnectionTargetNotFoundError, match="from"):
            render(spec, str(output))

    def test_render_missing_target_raises(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
            "connections": [
                {"from": "vm1", "to": "missing"},
            ],
        })
        output = tmp_path / "bad.png"
        with pytest.raises(ConnectionTargetNotFoundError, match="to"):
            render(spec, str(output))

    def test_render_empty_connections(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
            "connections": [],
        })
        output = tmp_path / "no_edges.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_render_with_custom_icon_registry(self, tmp_path, sample_svg):
        """Custom icon registry provides fallback for unknown types."""
        registry = MagicMock()
        registry.resolve.return_value = sample_svg

        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "custom/unknown-type", "name": "custom-node"},
            ],
        })
        output = tmp_path / "custom.png"
        result = render(spec, str(output), icon_registry=registry)
        assert result.exists()

    def test_render_unknown_type_no_registry(self, tmp_path):
        """Unknown type with no registry uses generic fallback."""
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "totally-unknown", "name": "mystery"},
            ],
        })
        output = tmp_path / "unknown.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderDirectionOverride:
    def test_direction_from_spec(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "LR Test", "direction": "LR"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "lr.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_direction_override(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Override Test", "direction": "TB"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "override.png"
        result = render(spec, str(output), direction_override="RL")
        assert result.exists()


class TestRenderDpiOverride:
    def test_dpi_from_spec(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "DPI Test", "dpi": 300},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "dpi.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_dpi_override(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "DPI Override"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "dpi_override.png"
        result = render(spec, str(output), dpi_override=72)
        assert result.exists()


class TestRenderDarkTheme:
    def test_dark_theme(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Dark Test", "theme": "dark"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "dark.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderEdgeArrowhead:
    def test_edge_with_arrowhead_vee(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "label": "link", "arrowhead": "vee"},
            ],
        })
        output = tmp_path / "arrowhead.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_edge_bidirectional(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {
                    "from": "a",
                    "to": "b",
                    "label": "sync",
                    "direction": "both",
                    "arrowtail": "diamond",
                },
            ],
        })
        output = tmp_path / "bidirectional.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderEdgeColor:
    def test_edge_with_color(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "label": "link", "color": "#FF0000"},
            ],
        })
        output = tmp_path / "colored.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_edge_with_penwidth(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "penwidth": "3.0"},
            ],
        })
        output = tmp_path / "thick.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderPresentationTheme:
    def test_presentation_theme(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Presentation Test", "theme": "presentation"},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
            ],
        })
        output = tmp_path / "presentation.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_presentation_nested_containers(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Presentation Nested", "theme": "presentation"},
            "resources": [
                {
                    "type": "azure/resource-group",
                    "name": "rg-prod",
                    "children": [
                        {
                            "type": "azure/vnet",
                            "name": "vnet",
                            "children": [
                                {
                                    "type": "azure/subnet",
                                    "name": "subnet",
                                    "children": [
                                        {"type": "azure/app-service", "name": "app"},
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        })
        output = tmp_path / "presentation_nested.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderStrictMode:
    def test_strict_unknown_type_raises(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "totally-unknown", "name": "mystery"},
            ],
        })
        output = tmp_path / "strict.png"
        with pytest.raises(IconNotFoundError, match="totally-unknown"):
            render(spec, str(output), strict=True)

    def test_strict_off_unknown_type_fallback(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "totally-unknown", "name": "mystery"},
            ],
        })
        output = tmp_path / "fallback.png"
        result = render(spec, str(output), strict=False)
        assert result.exists()


class TestRenderGlowParameter:
    def test_glow_true_svg_dark_applies_enhancement(self, tmp_path):
        """SVG + dark theme + glow=True → <style> injected."""
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Glow On", "theme": "dark"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "glow_on.svg"
        result = render(spec, str(output), out_format="svg", glow=True)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "<style" in content

    def test_glow_false_svg_dark_skips_enhancement(self, tmp_path):
        """SVG + dark theme + glow=False → no drop-shadow injected."""
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Glow Off", "theme": "dark"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "glow_off.svg"
        result = render(spec, str(output), out_format="svg", glow=False)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "drop-shadow" not in content

    def test_glow_none_preserves_legacy(self, tmp_path):
        """SVG + dark theme + glow=None → <style> injected (backward compat)."""
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Glow Legacy", "theme": "dark"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "glow_legacy.svg"
        result = render(spec, str(output), out_format="svg", glow=None)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "<style" in content

    def test_glow_true_png_no_effect(self, tmp_path):
        """PNG + glow=True → valid PNG, no crash."""
        spec = DiagramSpec.model_validate({
            "diagram": {"name": "Glow PNG", "theme": "dark"},
            "resources": [{"type": "azure/vm", "name": "vm1"}],
        })
        output = tmp_path / "glow.png"
        result = render(spec, str(output), out_format="png", glow=True)
        assert result.exists()
        assert result.suffix == ".png"


class TestRenderWithStyleRef:
    def test_style_ref_applies_preset(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "connection_styles": [
                {"name": "data-flow", "color": "#0078D4", "penwidth": "2.0"},
            ],
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "style_ref": "data-flow"},
            ],
        })
        output = tmp_path / "style_ref.png"
        result = render(spec, str(output))
        assert result.exists()

    def test_inline_overrides_preset(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "connection_styles": [
                {"name": "data-flow", "color": "#0078D4"},
            ],
            "resources": [
                {"type": "azure/vm", "name": "a"},
                {"type": "azure/vm", "name": "b"},
            ],
            "connections": [
                {"from": "a", "to": "b", "style_ref": "data-flow", "color": "#FF0000"},
            ],
        })
        output = tmp_path / "override.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderWithZones:
    def test_zones_produce_output(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "web"},
                {"type": "azure/vm", "name": "db"},
            ],
            "zones": [
                {"name": "DMZ", "resources": ["web"], "style": "dmz"},
            ],
            "connections": [{"from": "web", "to": "db"}],
        })
        output = tmp_path / "zones.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderWithMetadata:
    def test_metadata_renders(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "resources": [
                {"type": "azure/vm", "name": "vm1", "metadata": {"sku": "D2s_v3"}},
            ],
        })
        output = tmp_path / "metadata.png"
        result = render(spec, str(output))
        assert result.exists()


class TestRenderWithLegend:
    def test_legend_produces_output(self, tmp_path):
        spec = DiagramSpec.model_validate({
            "diagram": {"legend": True},
            "resources": [
                {"type": "azure/vm", "name": "vm1"},
                {"type": "azure/app-service", "name": "web"},
            ],
        })
        output = tmp_path / "legend.png"
        result = render(spec, str(output))
        assert result.exists()
