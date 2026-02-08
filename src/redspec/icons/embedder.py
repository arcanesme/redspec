"""Embed SVG files as base64 data URIs."""

import base64
import functools
from pathlib import Path


@functools.lru_cache(maxsize=256)
def embed_svg(svg_path: str | Path) -> str:
    """Read an SVG file and return a base64 data URI.

    Args:
        svg_path: Path to the SVG file.

    Returns:
        A data URI string, or an empty string if the file is not found.
    """
    path = Path(svg_path)
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return ""
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
