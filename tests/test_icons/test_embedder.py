"""Tests for SVG embedding."""

import urllib.parse

from redspec.icons.embedder import embed_svg


def test_embed_svg_produces_data_uri(sample_svg):
    result = embed_svg(str(sample_svg))
    assert result.startswith("data:image/svg+xml,")


def test_embed_svg_valid_percent_encoding(sample_svg):
    result = embed_svg(str(sample_svg))
    encoded_part = result.split(",", 1)[1]
    decoded = urllib.parse.unquote(encoded_part)
    assert "<svg" in decoded


def test_embed_svg_no_semicolons_in_encoded_data(sample_svg):
    """Semicolons must be percent-encoded to avoid draw.io style parsing issues."""
    result = embed_svg(str(sample_svg))
    # The only comma is the one separating the MIME type from data
    encoded_part = result.split(",", 1)[1]
    assert ";" not in encoded_part


def test_embed_svg_missing_file_returns_empty():
    result = embed_svg("/nonexistent/path/icon.svg")
    assert result == ""


def test_embed_svg_caching(sample_svg):
    r1 = embed_svg(str(sample_svg))
    r2 = embed_svg(str(sample_svg))
    assert r1 is r2  # Same object from cache
