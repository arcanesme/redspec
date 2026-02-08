"""SVG CSS animations for data flow, pulsing nodes, and build-up effects."""

from __future__ import annotations

import re
from pathlib import Path

_FLOW_CSS = """\
<style type="text/css">
@keyframes flow {
    to { stroke-dashoffset: -20; }
}
.edge path {
    stroke-dasharray: 10 5;
    animation: flow 1s linear infinite;
}
</style>"""

_PULSE_CSS = """\
<style type="text/css">
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
.node image, .node polygon, .node ellipse {
    animation: pulse 2s ease-in-out infinite;
}
</style>"""

_BUILD_CSS = """\
<style type="text/css">
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.node { animation: fadeIn 0.5s ease-out both; }
.cluster { animation: fadeIn 0.3s ease-out both; }
</style>"""

_ANIMATION_CSS: dict[str, str] = {
    "flow": _FLOW_CSS,
    "pulse": _PULSE_CSS,
    "build": _BUILD_CSS,
}


def animate_svg(svg_path: Path, animation_type: str) -> None:
    """Inject CSS animation into an SVG file.

    Modifies *svg_path* in-place. Does nothing if animation_type is unknown.
    """
    css_block = _ANIMATION_CSS.get(animation_type)
    if css_block is None:
        return

    text = svg_path.read_text(encoding="utf-8")
    text = re.sub(
        r"(<svg\b[^>]*>)",
        rf"\1\n{css_block}",
        text,
        count=1,
    )
    svg_path.write_text(text, encoding="utf-8")
