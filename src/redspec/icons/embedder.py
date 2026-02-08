"""Embed SVG files as percent-encoded data URIs for draw.io compatibility."""

import functools
import urllib.parse
from pathlib import Path


@functools.lru_cache(maxsize=256)
def embed_svg(svg_path: str | Path) -> str:
    """Read an SVG file and return a percent-encoded data URI.

    Uses percent-encoding instead of base64 because draw.io's style parser
    splits on semicolons, which corrupts ``data:image/svg+xml;base64,...``
    data URIs.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        A data URI string, or an empty string if the file is not found.
    """
    path = Path(svg_path)
    try:
        data = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    encoded = urllib.parse.quote(data, safe="")
    return f"data:image/svg+xml,{encoded}"
