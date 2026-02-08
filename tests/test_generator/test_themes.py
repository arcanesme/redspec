"""Tests for the theme system."""

import pytest

from redspec.generator.themes import VALID_THEMES, get_theme


class TestGetTheme:
    def test_all_themes_exist(self):
        for name in VALID_THEMES:
            theme = get_theme(name)
            assert isinstance(theme, dict)

    @pytest.mark.parametrize("name", sorted(VALID_THEMES))
    def test_theme_has_required_keys(self, name):
        theme = get_theme(name)
        assert "graph_attr" in theme
        assert "node_attr" in theme
        assert "edge_attr" in theme
        assert "cluster_base" in theme

    def test_default_theme_graph_attr(self):
        theme = get_theme("default")
        ga = theme["graph_attr"]
        assert ga["dpi"] == "150"
        assert ga["nodesep"] == "0.80"
        assert ga["ranksep"] == "1.0"
        assert ga["splines"] == "ortho"

    def test_default_theme_edge_attr(self):
        theme = get_theme("default")
        ea = theme["edge_attr"]
        assert ea["penwidth"] == "1.5"
        assert ea["arrowsize"] == "0.8"
        assert ea["fontsize"] == "11"

    def test_default_theme_cluster_base(self):
        theme = get_theme("default")
        cb = theme["cluster_base"]
        assert cb["penwidth"] == "2.0"
        assert cb["labeljust"] == "l"
        assert cb["labelloc"] == "t"
        assert cb["margin"] == "16"

    def test_dark_theme_colors(self):
        theme = get_theme("dark")
        assert theme["graph_attr"]["bgcolor"] == "#1E1E2E"
        assert theme["graph_attr"]["fontcolor"] == "#CDD6F4"
        assert theme["edge_attr"]["color"] == "#6C7086"

    def test_light_theme_bgcolor(self):
        theme = get_theme("light")
        assert theme["graph_attr"]["bgcolor"] == "#FAFAFA"

    def test_unknown_theme_raises(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            get_theme("neon")

    def test_valid_themes_frozenset(self):
        assert VALID_THEMES == {"default", "light", "dark"}
