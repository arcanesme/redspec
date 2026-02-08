"""Theme presets for diagram styling."""

from __future__ import annotations

from typing import Any

VALID_THEMES: frozenset[str] = frozenset({"default", "light", "dark"})

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
            "color": "#6C7086",
            "penwidth": "1.5",
            "fontname": _SHARED_FONT,
            "fontsize": "11",
            "fontcolor": "#6C7086",
            "arrowsize": "0.8",
            "arrowhead": "vee",
        },
        "cluster_base": {
            "fontname": _SHARED_FONT,
            "fontsize": "13",
            "fontcolor": "#CDD6F4",
            "penwidth": "2.0",
            "style": "rounded",
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
