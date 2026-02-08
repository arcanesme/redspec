"""Structured output organization for generated diagrams."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug.

    >>> slugify("My Azure Arch")
    'my-azure-arch'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def organize_output(
    generated_file: Path,
    source_yaml: Path,
    output_dir: Path,
    diagram_name: str,
    **meta: Any,
) -> Path:
    """Move a generated diagram into a structured output directory.

    Creates::

        <output_dir>/<slug>/
            diagram.<format>
            spec.yaml
            metadata.json

    Returns the Path to the organized diagram file.
    """
    slug = slugify(diagram_name)
    dest_dir = output_dir / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy diagram
    ext = generated_file.suffix
    diagram_dest = dest_dir / f"diagram{ext}"
    shutil.copy2(generated_file, diagram_dest)

    # Copy source YAML
    spec_dest = dest_dir / "spec.yaml"
    shutil.copy2(source_yaml, spec_dest)

    # Write metadata
    metadata = {
        "name": diagram_name,
        "slug": slug,
        "format": ext.lstrip("."),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_yaml": str(source_yaml),
        "output_path": str(diagram_dest),
        **meta,
    }
    metadata_dest = dest_dir / "metadata.json"
    metadata_dest.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return diagram_dest


def list_gallery(output_dir: Path) -> list[dict[str, Any]]:
    """Scan output directory and return metadata dicts sorted newest-first."""
    entries: list[dict[str, Any]] = []

    if not output_dir.is_dir():
        return entries

    for subdir in output_dir.iterdir():
        if not subdir.is_dir():
            continue
        meta_file = subdir / "metadata.json"
        if not meta_file.exists():
            continue
        try:
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            data["slug"] = subdir.name
            entries.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return entries
