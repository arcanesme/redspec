"""SVG post-processing for glow effects on dark/presentation themes."""

from __future__ import annotations

import re
from pathlib import Path

_PRESENTATION_GLOW_CSS = """\
<style type="text/css">
.cluster polygon, .cluster path {
    filter: drop-shadow(0 0 6px #0078D4);
}
.edge path {
    filter: drop-shadow(0 0 3px #4FC3F7);
}
</style>"""

_DARK_GLOW_CSS = """\
<style type="text/css">
.cluster polygon, .cluster path {
    filter: drop-shadow(0 0 4px #89B4FA);
}
.edge path {
    filter: drop-shadow(0 0 2px #89B4FA);
}
</style>"""

_GLOW_CSS: dict[str, str] = {
    "presentation": _PRESENTATION_GLOW_CSS,
    "dark": _DARK_GLOW_CSS,
}


def enhance_svg(svg_path: Path, theme_name: str) -> None:
    """Inject glow CSS into an SVG file for dark/presentation themes.

    Modifies *svg_path* in-place.  Does nothing if *theme_name* is not a
    dark variant.
    """
    css_block = _GLOW_CSS.get(theme_name)
    if css_block is None:
        return

    text = svg_path.read_text(encoding="utf-8")

    # Insert the <style> block right after the opening <svg ...> tag.
    text = re.sub(
        r"(<svg\b[^>]*>)",
        rf"\1\n{css_block}",
        text,
        count=1,
    )

    svg_path.write_text(text, encoding="utf-8")
