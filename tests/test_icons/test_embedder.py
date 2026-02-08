"""Tests for SVG embedding."""

import base64

from redspec.icons.embedder import embed_svg


def test_embed_svg_produces_data_uri(sample_svg):
    result = embed_svg(str(sample_svg))
    assert result.startswith("data:image/svg+xml;base64,")


def test_embed_svg_valid_base64(sample_svg):
    result = embed_svg(str(sample_svg))
    b64_part = result.split(",", 1)[1]
    decoded = base64.b64decode(b64_part)
    assert b"<svg" in decoded


def test_embed_svg_missing_file_returns_empty():
    result = embed_svg("/nonexistent/path/icon.svg")
    assert result == ""


def test_embed_svg_caching(sample_svg):
    r1 = embed_svg(str(sample_svg))
    r2 = embed_svg(str(sample_svg))
    assert r1 is r2  # Same object from cache
