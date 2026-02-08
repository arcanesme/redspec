"""Tests for SVG CSS animations."""

from pathlib import Path

from redspec.generator.svg_animator import animate_svg

_MINIMAL_SVG = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">\n'
    '<rect width="100" height="100" fill="white"/>\n'
    '</svg>\n'
)


class TestAnimateSvg:
    def test_flow_animation(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")
        animate_svg(svg, "flow")
        result = svg.read_text(encoding="utf-8")
        assert "@keyframes flow" in result
        assert "stroke-dashoffset" in result

    def test_pulse_animation(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")
        animate_svg(svg, "pulse")
        result = svg.read_text(encoding="utf-8")
        assert "@keyframes pulse" in result
        assert "opacity" in result

    def test_build_animation(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")
        animate_svg(svg, "build")
        result = svg.read_text(encoding="utf-8")
        assert "@keyframes fadeIn" in result

    def test_null_animation_noop(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")
        animate_svg(svg, "nonexistent")
        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG

    def test_unknown_type_noop(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")
        animate_svg(svg, "unknown")
        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG
