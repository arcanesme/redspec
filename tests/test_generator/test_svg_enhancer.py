"""Tests for SVG post-processing glow injection."""

from pathlib import Path

from redspec.generator.svg_enhancer import enhance_svg

_MINIMAL_SVG = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">\n'
    '<rect width="100" height="100" fill="white"/>\n'
    '</svg>\n'
)


class TestEnhanceSvg:
    def test_injects_glow_for_presentation(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "presentation")

        result = svg.read_text(encoding="utf-8")
        assert "<style" in result
        assert "drop-shadow" in result
        assert "fill-opacity" in result
        assert "0, 120, 212" in result  # Azure blue in rgba

    def test_injects_glow_for_dark(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "dark")

        result = svg.read_text(encoding="utf-8")
        assert "<style" in result
        assert "drop-shadow" in result
        assert "137, 180, 250" in result  # Catppuccin blue in rgba

    def test_presentation_forces_white_text(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "presentation")

        result = svg.read_text(encoding="utf-8")
        assert "fill: #FFFFFF" in result

    def test_noop_for_default_theme(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "default")

        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG

    def test_noop_for_light_theme(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "light")

        result = svg.read_text(encoding="utf-8")
        assert result == _MINIMAL_SVG

    def test_output_still_valid_svg(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "presentation")

        result = svg.read_text(encoding="utf-8")
        assert result.startswith("<?xml")
        assert "<svg" in result
        assert "</svg>" in result

    def test_style_placed_after_svg_tag(self, tmp_path):
        svg = tmp_path / "test.svg"
        svg.write_text(_MINIMAL_SVG, encoding="utf-8")

        enhance_svg(svg, "presentation")

        result = svg.read_text(encoding="utf-8")
        svg_open_end = result.index(">")  # end of <?xml ...>
        style_pos = result.index("<style")
        svg_tag_pos = result.index("<svg")
        assert style_pos > svg_tag_pos
