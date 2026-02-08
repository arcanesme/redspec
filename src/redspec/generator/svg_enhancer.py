"""SVG post-processing for glow and glassmorphism effects on dark themes."""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Presentation theme: strong Azure-blue glow, glassmorphism clusters,
# forced bright-white text everywhere.
# ---------------------------------------------------------------------------
_PRESENTATION_CSS = """\
<style type="text/css">
/* ── Glassmorphism: semi-transparent cluster fills with glow borders ── */
.cluster polygon, .cluster path {
    fill-opacity: 0.45;
    stroke-width: 3;
    filter: drop-shadow(0 0 10px rgba(0, 120, 212, 0.8))
            drop-shadow(0 0 24px rgba(0, 120, 212, 0.35));
}

/* ── Force ALL text bright white with subtle halo ── */
text {
    fill: #FFFFFF !important;
    filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.4));
}

/* ── Edge paths: cyan glow ── */
.edge path {
    filter: drop-shadow(0 0 5px rgba(79, 195, 247, 0.75))
            drop-shadow(0 0 12px rgba(79, 195, 247, 0.3));
}

/* ── Edge arrowheads inherit glow ── */
.edge polygon {
    filter: drop-shadow(0 0 3px rgba(79, 195, 247, 0.6));
}

/* ── Node icons: subtle ambient glow ── */
.node image {
    filter: drop-shadow(0 0 4px rgba(0, 120, 212, 0.3));
}
</style>"""

# ---------------------------------------------------------------------------
# Dark theme: softer Catppuccin-blue glow, same glassmorphism approach.
# ---------------------------------------------------------------------------
_DARK_CSS = """\
<style type="text/css">
.cluster polygon, .cluster path {
    fill-opacity: 0.5;
    filter: drop-shadow(0 0 6px rgba(137, 180, 250, 0.7))
            drop-shadow(0 0 16px rgba(137, 180, 250, 0.25));
}

text {
    fill: #CDD6F4 !important;
    filter: drop-shadow(0 0 2px rgba(205, 214, 244, 0.3));
}

.edge path {
    filter: drop-shadow(0 0 4px rgba(137, 180, 250, 0.6));
}

.edge polygon {
    filter: drop-shadow(0 0 2px rgba(137, 180, 250, 0.5));
}
</style>"""

_THEME_CSS: dict[str, str] = {
    "presentation": _PRESENTATION_CSS,
    "dark": _DARK_CSS,
}


def enhance_svg(svg_path: Path, theme_name: str) -> None:
    """Inject glassmorphism / glow CSS into an SVG file for dark themes.

    Modifies *svg_path* in-place.  Does nothing if *theme_name* has no
    associated enhancement CSS.
    """
    css_block = _THEME_CSS.get(theme_name)
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
