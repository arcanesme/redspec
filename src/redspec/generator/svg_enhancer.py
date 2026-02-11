"""SVG post-processing for premium visual effects.

Generates CSS for glow, shadow, gradient, glassmorphism, and icon quality
effects based on a :class:`PolishConfig` and the active theme.  When no
``PolishConfig`` is provided the legacy behaviour (hardcoded CSS for *dark*
and *presentation* themes) is preserved for backward compatibility.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redspec.models.diagram import PolishConfig

# ---------------------------------------------------------------------------
# Azure design-system colour constants
# ---------------------------------------------------------------------------

AZURE_BLUE = (0, 120, 212)
AZURE_CYAN = (79, 195, 247)
CATPPUCCIN_BLUE = (137, 180, 250)
CATPPUCCIN_TEXT = (205, 214, 244)

_THEME_ACCENT: dict[str, tuple[int, int, int]] = {
    "presentation": AZURE_BLUE,
    "dark": CATPPUCCIN_BLUE,
    "default": (123, 136, 148),
    "light": (123, 136, 148),
}

_THEME_EDGE_ACCENT: dict[str, tuple[int, int, int]] = {
    "presentation": AZURE_CYAN,
    "dark": CATPPUCCIN_BLUE,
    "default": (123, 136, 148),
    "light": (123, 136, 148),
}

_THEME_TEXT_COLOR: dict[str, str] = {
    "presentation": "#FFFFFF",
    "dark": "#CDD6F4",
    "default": "#2D3436",
    "light": "#2D3436",
}

_THEME_TEXT_HALO: dict[str, tuple[int, int, int]] = {
    "presentation": (255, 255, 255),
    "dark": CATPPUCCIN_TEXT,
    "default": (45, 52, 54),
    "light": (45, 52, 54),
}


# ---------------------------------------------------------------------------
# Elevation -> shadow offset/blur lookup
# ---------------------------------------------------------------------------

_ELEVATION_MAP: dict[int, dict[str, float]] = {
    0: {"offset_y": 0, "blur": 0, "spread": 0},
    1: {"offset_y": 1, "blur": 3, "spread": 4},
    2: {"offset_y": 2, "blur": 6, "spread": 8},
    3: {"offset_y": 4, "blur": 10, "spread": 14},
    4: {"offset_y": 6, "blur": 16, "spread": 20},
}


# ---------------------------------------------------------------------------
# Gradient SVG definitions
# ---------------------------------------------------------------------------

def _gradient_defs(theme_name: str, config: PolishConfig) -> str:
    """Generate SVG ``<defs>`` block with gradient definitions."""
    if not config.gradient.enabled:
        return ""

    accent = _THEME_ACCENT.get(theme_name, AZURE_BLUE)
    intensity = config.gradient.intensity

    if config.gradient.style == "azure":
        # Azure-branded gradient: deep navy to accent blue
        return (
            "<defs>\n"
            f'  <linearGradient id="rs-grad-cluster" x1="0%" y1="0%" x2="0%" y2="100%">\n'
            f'    <stop offset="0%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.4:.2f})"/>\n'
            f'    <stop offset="100%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.1:.2f})"/>\n'
            f"  </linearGradient>\n"
            f'  <radialGradient id="rs-grad-node" cx="50%" cy="30%" r="70%">\n'
            f'    <stop offset="0%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.25:.2f})"/>\n'
            f'    <stop offset="100%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.05:.2f})"/>\n'
            f"  </radialGradient>\n"
            "</defs>"
        )
    elif config.gradient.style == "radial":
        return (
            "<defs>\n"
            f'  <radialGradient id="rs-grad-cluster" cx="50%" cy="50%" r="70%">\n'
            f'    <stop offset="0%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.35:.2f})"/>\n'
            f'    <stop offset="100%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.08:.2f})"/>\n'
            f"  </radialGradient>\n"
            "</defs>"
        )
    else:  # linear
        return (
            "<defs>\n"
            f'  <linearGradient id="rs-grad-cluster" x1="0%" y1="0%" x2="100%" y2="100%">\n'
            f'    <stop offset="0%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.3:.2f})"/>\n'
            f'    <stop offset="100%" stop-color="rgba({accent[0]}, {accent[1]}, {accent[2]}, {intensity * 0.08:.2f})"/>\n'
            f"  </linearGradient>\n"
            "</defs>"
        )


# ---------------------------------------------------------------------------
# CSS generation from PolishConfig
# ---------------------------------------------------------------------------

def _build_css(theme_name: str, config: PolishConfig) -> str:
    """Build a complete ``<style>`` block from *config* and *theme_name*."""
    accent = _THEME_ACCENT.get(theme_name, AZURE_BLUE)
    edge_accent = _THEME_EDGE_ACCENT.get(theme_name, AZURE_CYAN)
    text_color = _THEME_TEXT_COLOR.get(theme_name, "#2D3436")
    text_halo = _THEME_TEXT_HALO.get(theme_name, (45, 52, 54))

    # Override accent colour if user specified one
    if config.glow.color:
        parsed = _parse_hex(config.glow.color)
        if parsed:
            accent = parsed

    rules: list[str] = []

    # --- Cluster effects (glassmorphism + glow + shadow) ---
    cluster_filters: list[str] = []
    cluster_rules: list[str] = []

    if config.glassmorphism > 0:
        cluster_rules.append(f"    fill-opacity: {config.glassmorphism:.2f};")

    if config.glow.enabled and config.glow.intensity > 0:
        r, g, b = accent
        for i in range(config.glow.layers):
            scale = 1.0 + i * 0.8
            blur = config.glow.blur_radius * scale
            opacity = config.glow.intensity * (0.8 - i * 0.2)
            opacity = max(0.05, opacity)
            cluster_filters.append(
                f"drop-shadow(0 0 {blur:.0f}px rgba({r}, {g}, {b}, {opacity:.2f}))"
            )

    if config.shadow.enabled and config.shadow.elevation > 0:
        elev = _ELEVATION_MAP.get(config.shadow.elevation, _ELEVATION_MAP[2])
        sr, sg, sb = _parse_hex(config.shadow.color) if config.shadow.color else (0, 0, 0)
        cluster_filters.append(
            f"drop-shadow(0 {elev['offset_y']:.0f}px {elev['blur']:.0f}px "
            f"rgba({sr}, {sg}, {sb}, {config.shadow.opacity:.2f}))"
        )

    if cluster_rules or cluster_filters:
        rule = ".cluster polygon, .cluster path {\n"
        if cluster_rules:
            rule += "\n".join(cluster_rules) + "\n"
        if cluster_filters:
            rule += "    stroke-width: 3;\n"
            rule += "    filter: " + "\n            ".join(cluster_filters) + ";\n"
        rule += "}"
        rules.append(rule)

    # --- Text styling ---
    if theme_name in ("dark", "presentation"):
        text_rule = f"text {{\n    fill: {text_color} !important;\n"
        if config.text_halo:
            hr, hg, hb = text_halo
            text_rule += f"    filter: drop-shadow(0 0 3px rgba({hr}, {hg}, {hb}, 0.4));\n"
        text_rule += "}"
        rules.append(text_rule)

    # --- Edge effects ---
    edge_filters: list[str] = []
    if config.glow.enabled and config.glow.intensity > 0:
        er, eg, eb = edge_accent
        edge_blur = config.glow.blur_radius * 0.5
        edge_opacity = config.glow.intensity * 0.75
        edge_filters.append(
            f"drop-shadow(0 0 {edge_blur:.0f}px rgba({er}, {eg}, {eb}, {edge_opacity:.2f}))"
        )
        if config.glow.layers >= 2:
            edge_filters.append(
                f"drop-shadow(0 0 {edge_blur * 2:.0f}px rgba({er}, {eg}, {eb}, {edge_opacity * 0.4:.2f}))"
            )

    if edge_filters:
        rules.append(
            ".edge path {\n    filter: "
            + "\n            ".join(edge_filters)
            + ";\n}"
        )
        # Arrowheads get a slightly reduced version
        rules.append(
            ".edge polygon {\n    filter: "
            + edge_filters[0].replace(
                f"{edge_opacity:.2f}",
                f"{edge_opacity * 0.8:.2f}",
            )
            + ";\n}"
        )

    # --- Icon quality ---
    icon_filters: list[str] = []
    if config.icon_quality.glow and config.icon_quality.glow_intensity > 0:
        ir, ig, ib = accent
        icon_filters.append(
            f"drop-shadow(0 0 4px rgba({ir}, {ig}, {ib}, {config.icon_quality.glow_intensity:.2f}))"
        )
    if config.icon_quality.sharpening:
        icon_filters.append("contrast(1.05)")

    if icon_filters:
        rules.append(
            ".node image {\n    filter: "
            + " ".join(icon_filters)
            + ";\n}"
        )

    if not rules:
        return ""

    css_body = "\n\n".join(rules)
    return f'<style type="text/css">\n{css_body}\n</style>'


# ---------------------------------------------------------------------------
# Legacy hardcoded CSS (backward-compatible with original enhance_svg)
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

_LEGACY_THEME_CSS: dict[str, str] = {
    "presentation": _PRESENTATION_CSS,
    "dark": _DARK_CSS,
}


# ---------------------------------------------------------------------------
# Helper: parse hex colour to RGB tuple
# ---------------------------------------------------------------------------

def _parse_hex(color: str | None) -> tuple[int, int, int] | None:
    """Parse ``#RRGGBB`` or ``#RGB`` to an ``(r, g, b)`` tuple."""
    if not color:
        return None
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    if len(color) != 6:
        return None
    try:
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enhance_svg(
    svg_path: Path,
    theme_name: str,
    polish: PolishConfig | None = None,
) -> None:
    """Inject visual enhancement CSS into an SVG file.

    When *polish* is provided the CSS is dynamically generated from its
    settings.  Otherwise the legacy hardcoded CSS for *dark* /
    *presentation* themes is injected.

    Modifies *svg_path* in-place.  Does nothing when there are no effects
    to apply.
    """
    if polish is not None:
        css_block = _build_css(theme_name, polish)
        defs_block = _gradient_defs(theme_name, polish)
    else:
        # Legacy path: hardcoded CSS for dark themes only
        css_block = _LEGACY_THEME_CSS.get(theme_name, "")
        defs_block = ""

    if not css_block and not defs_block:
        return

    text = svg_path.read_text(encoding="utf-8")

    inject = ""
    if css_block:
        inject += "\n" + css_block
    if defs_block:
        inject += "\n" + defs_block

    # Insert right after the opening <svg ...> tag.
    text = re.sub(
        r"(<svg\b[^>]*>)",
        rf"\1{inject}",
        text,
        count=1,
    )

    svg_path.write_text(text, encoding="utf-8")
