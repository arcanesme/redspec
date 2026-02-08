"""Theme presets for diagram styling."""

from __future__ import annotations

from typing import Any

VALID_THEMES: frozenset[str] = frozenset({"default", "light", "dark", "presentation"})

_SHARED_FONT = "Sans-Serif"

_THEMES: dict[str, dict[str, dict[str, Any]]] = {
    "default": {
        "graph_attr": {
            "bgcolor": "white",
            "fontname": _SHARED_FONT,
            "fontsize": "16",
            "fontcolor": "#2D3436",
            "pad": "1.0",
            "nodesep": "0.80",
            "ranksep": "1.0",
            "splines": "ortho",
            "dpi": "150",
        },
        "node_attr": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#2D3436",
        },
        "edge_attr": {
            "color": "#7B8894",
            "penwidth": "1.5",
            "fontname": _SHARED_FONT,
            "fontsize": "11",
            "fontcolor": "#636E72",
            "arrowsize": "0.8",
            "arrowhead": "vee",
        },
        "cluster_base": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#2D3436",
            "penwidth": "2.0",
            "style": "rounded",
            "labeljust": "l",
            "labelloc": "t",
            "margin": "16",
        },
    },
    "light": {
        "graph_attr": {
            "bgcolor": "#FAFAFA",
            "fontname": _SHARED_FONT,
            "fontsize": "16",
            "fontcolor": "#2D3436",
            "pad": "1.0",
            "nodesep": "0.80",
            "ranksep": "1.0",
            "splines": "ortho",
            "dpi": "150",
        },
        "node_attr": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#2D3436",
        },
        "edge_attr": {
            "color": "#7B8894",
            "penwidth": "1.5",
            "fontname": _SHARED_FONT,
            "fontsize": "11",
            "fontcolor": "#636E72",
            "arrowsize": "0.8",
            "arrowhead": "vee",
        },
        "cluster_base": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#2D3436",
            "penwidth": "2.0",
            "style": "rounded",
            "labeljust": "l",
            "labelloc": "t",
            "margin": "16",
        },
    },
    "dark": {
        "graph_attr": {
            "bgcolor": "#1E1E2E",
            "fontname": _SHARED_FONT,
            "fontsize": "16",
            "fontcolor": "#CDD6F4",
            "pad": "1.0",
            "nodesep": "0.80",
            "ranksep": "1.0",
            "splines": "ortho",
            "dpi": "150",
        },
        "node_attr": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#CDD6F4",
        },
        "edge_attr": {
            "color": "#89B4FA",
            "penwidth": "1.5",
            "fontname": _SHARED_FONT,
            "fontsize": "11",
            "fontcolor": "#A6ADC8",
            "arrowsize": "0.8",
            "arrowhead": "vee",
        },
        "cluster_base": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#CDD6F4",
            "penwidth": "2.5",
            "bgcolor": "#1A1A3E",
            "style": "rounded",
            "labeljust": "l",
            "labelloc": "t",
            "margin": "16",
        },
    },
    "presentation": {
        "graph_attr": {
            "bgcolor": "#0A0E1A",
            "fontname": _SHARED_FONT,
            "fontsize": "16",
            "fontcolor": "#FFFFFF",
            "pad": "1.0",
            "nodesep": "0.80",
            "ranksep": "1.0",
            "splines": "ortho",
            "dpi": "150",
        },
        "node_attr": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#FFFFFF",
        },
        "edge_attr": {
            "color": "#4FC3F7",
            "penwidth": "2.0",
            "fontname": _SHARED_FONT,
            "fontsize": "11",
            "fontcolor": "#E0E0E0",
            "arrowsize": "0.8",
            "arrowhead": "vee",
        },
        "cluster_base": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#FFFFFF",
            "pencolor": "#0078D4",
            "penwidth": "3.0",
            "bgcolor": "#0D1B2A80",
            "style": "rounded,filled",
            "labeljust": "l",
            "labelloc": "t",
            "margin": "16",
        },
    },
}


def get_theme(name: str = "default") -> dict[str, dict[str, Any]]:
    """Return a theme dict by name.

    Raises ``ValueError`` if the theme name is unknown.
    """
    if name not in _THEMES:
        raise ValueError(
            f"Unknown theme {name!r}. Valid themes: {', '.join(sorted(VALID_THEMES))}"
        )
    return _THEMES[name]


def register_custom_theme(name: str, theme_dict: dict[str, dict[str, Any]]) -> None:
    """Register a custom theme for use in rendering.

    The theme_dict must have keys: graph_attr, node_attr, edge_attr, cluster_base.
    """
    global VALID_THEMES
    required_keys = {"graph_attr", "node_attr", "edge_attr", "cluster_base"}
    missing = required_keys - set(theme_dict.keys())
    if missing:
        raise ValueError(f"Custom theme missing required keys: {missing}")
    _THEMES[name] = theme_dict
    VALID_THEMES = frozenset(VALID_THEMES | {name})
