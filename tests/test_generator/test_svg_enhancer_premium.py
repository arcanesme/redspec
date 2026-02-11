"""Tests for the premium SVG enhancer with configurable effects."""

from pathlib import Path

import pytest

from redspec.generator.svg_enhancer import (
    AZURE_BLUE,
    AZURE_CYAN,
    CATPPUCCIN_BLUE,
    _build_css,
    _gradient_defs,
    _parse_hex,
    enhance_svg,
)
from redspec.models.diagram import PolishConfig, resolve_polish

_MINIMAL_SVG = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">\n'
    '<rect width="100" height="100" fill="white"/>\n'
    "</svg>\n"
)


class TestParseHex:
    def test_six_digit(self):
        assert _parse_hex("#0078D4") == (0, 120, 212)

    def test_three_digit(self):
        assert _parse_hex("#FFF") == (255, 255, 255)

    def test_no_hash(self):
        assert _parse_hex("0078D4") == (0, 120, 212)

    def test_none_returns_none(self):
        assert _parse_hex(None) is None

    def test_empty_returns_none(self):
        assert _parse_hex("") is None

    def test_invalid_returns_none(self):
        assert _parse_hex("not-a-color") is None


class TestBuildCss:
    def test_minimal_returns_empty(self):
        cfg = resolve_polish(PolishConfig.model_validate("minimal"))
        css = _build_css("default", cfg)
        assert css == ""

    def test_premium_presentation_has_glow(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert "drop-shadow" in css
        assert f"{AZURE_BLUE[0]}, {AZURE_BLUE[1]}, {AZURE_BLUE[2]}" in css

    def test_premium_dark_has_catppuccin(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("dark", cfg)
        assert f"{CATPPUCCIN_BLUE[0]}, {CATPPUCCIN_BLUE[1]}, {CATPPUCCIN_BLUE[2]}" in css

    def test_presentation_forces_white_text(self):
        cfg = resolve_polish(PolishConfig.model_validate("standard"))
        css = _build_css("presentation", cfg)
        assert "fill: #FFFFFF" in css

    def test_dark_forces_catppuccin_text(self):
        cfg = resolve_polish(PolishConfig.model_validate("standard"))
        css = _build_css("dark", cfg)
        assert "fill: #CDD6F4" in css

    def test_text_halo_included(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        # Text should have a halo drop-shadow
        assert "255, 255, 255" in css

    def test_text_halo_disabled(self):
        cfg = resolve_polish(PolishConfig(preset="premium", text_halo=False))
        css = _build_css("presentation", cfg)
        # Text rule should still exist (forced color) but no halo filter
        assert "fill: #FFFFFF" in css

    def test_custom_glow_color(self):
        cfg = resolve_polish(PolishConfig(
            preset="premium",
            glow={"enabled": True, "intensity": 0.8, "color": "#FF0000"},
        ))
        css = _build_css("presentation", cfg)
        assert "255, 0, 0" in css

    def test_shadow_elevation(self):
        cfg = resolve_polish(PolishConfig(
            preset="premium",
            shadow={"enabled": True, "elevation": 3},
        ))
        css = _build_css("presentation", cfg)
        assert "drop-shadow" in css

    def test_edge_glow(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert ".edge path" in css
        assert ".edge polygon" in css

    def test_icon_sharpening(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert ".node image" in css
        assert "contrast(1.05)" in css

    def test_icon_glow(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert ".node image" in css

    def test_glassmorphism(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert "fill-opacity:" in css
        assert "0.45" in css

    def test_ultra_has_more_layers(self):
        cfg = resolve_polish(PolishConfig.model_validate("ultra"))
        css = _build_css("presentation", cfg)
        # Ultra has 3 glow layers, should have more drop-shadow entries for clusters
        cluster_section = css.split(".edge")[0]
        assert cluster_section.count("drop-shadow") >= 3

    def test_style_tag_present(self):
        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        css = _build_css("presentation", cfg)
        assert '<style type="text/css">' in css
        assert "</style>" in css


class TestGradientDefs:
    def test_disabled_returns_empty(self):
        cfg = resolve_polish(PolishConfig(preset="minimal"))
        assert _gradient_defs("presentation", cfg) == ""

    def test_azure_style(self):
        cfg = resolve_polish(PolishConfig(
            preset="premium",
            gradient={"enabled": True, "style": "azure"},
        ))
        defs = _gradient_defs("presentation", cfg)
        assert "<defs>" in defs
        assert "linearGradient" in defs
        assert "radialGradient" in defs
        assert "rs-grad-cluster" in defs
        assert "rs-grad-node" in defs

    def test_linear_style(self):
        cfg = resolve_polish(PolishConfig(
            preset="premium",
            gradient={"enabled": True, "style": "linear"},
        ))
        defs = _gradient_defs("presentation", cfg)
        assert "linearGradient" in defs
        assert "rs-grad-cluster" in defs

    def test_radial_style(self):
        cfg = resolve_polish(PolishConfig(
            preset="premium",
            gradient={"enabled": True, "style": "radial"},
        ))
        defs = _gradient_defs("presentation", cfg)
        assert "radialGradient" in defs


class TestEnhanceSvgWithPolish:
    """Test enhance_svg with the new polish parameter."""

    def test_premium_injects_style(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        enhance_svg(svg, "presentation", polish=cfg)

        result = svg.read_text(encoding="utf-8")
        assert "<style" in result
        assert "drop-shadow" in result

    def test_premium_injects_gradients(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        enhance_svg(svg, "presentation", polish=cfg)

        result = svg.read_text(encoding="utf-8")
        assert "<defs>" in result
        assert "linearGradient" in result

    def test_minimal_is_noop(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        cfg = resolve_polish(PolishConfig.model_validate("minimal"))
        enhance_svg(svg, "default", polish=cfg)

        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG

    def test_output_remains_valid_svg(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        cfg = resolve_polish(PolishConfig.model_validate("ultra"))
        enhance_svg(svg, "presentation", polish=cfg)

        result = svg.read_text(encoding="utf-8")
        assert result.startswith("<?xml")
        assert "<svg" in result
        assert "</svg>" in result

    def test_style_placed_after_svg_tag(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        cfg = resolve_polish(PolishConfig.model_validate("premium"))
        enhance_svg(svg, "presentation", polish=cfg)

        result = svg.read_text(encoding="utf-8")
        style_pos = result.index("<style")
        svg_tag_pos = result.index("<svg")
        assert style_pos > svg_tag_pos


class TestEnhanceSvgLegacy:
    """Backward-compatibility tests: enhance_svg without polish param."""

    def test_presentation_legacy(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "presentation")

        result = svg.read_text(encoding="utf-8")
        assert "<style" in result
        assert "drop-shadow" in result
        assert "0, 120, 212" in result

    def test_dark_legacy(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "dark")

        result = svg.read_text(encoding="utf-8")
        assert "<style" in result
        assert "137, 180, 250" in result

    def test_default_legacy_noop(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "default")

        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG

    def test_light_legacy_noop(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "light")

        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG
