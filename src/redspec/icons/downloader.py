"""Download and extract icon packs."""

from __future__ import annotations

import fnmatch
import urllib.request
import zipfile
import tempfile
from pathlib import Path

from redspec.config import ICON_CACHE_DIR
from redspec.icons.packs import ALL_PACKS, DEFAULT_PACK_NAMES, IconPack


def download_pack(pack: IconPack, force: bool = False) -> int:
    """Download and extract SVGs for a single icon pack.

    Returns the number of SVGs extracted.
    """
    if not force and pack.downloaded_marker.exists():
        return 0

    pack.cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {pack.display_name} from {pack.url} ...")
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        urllib.request.urlretrieve(pack.url, tmp_path)

    count = 0
    try:
        with zipfile.ZipFile(tmp_path) as zf:
            for entry in zf.namelist():
                if not entry.lower().endswith(".svg"):
                    continue
                # Apply extract filter if specified
                if pack.extract_filter and not fnmatch.fnmatch(
                    entry, pack.extract_filter
                ):
                    continue
                filename = Path(entry).name
                target = pack.cache_dir / filename
                target.write_bytes(zf.read(entry))
                count += 1
    finally:
        tmp_path.unlink(missing_ok=True)

    pack.downloaded_marker.touch()
    print(f"Extracted {count} SVG icons to {pack.cache_dir}")
    return count


def download_packs(
    pack_names: list[str] | None = None, force: bool = False
) -> dict[str, int]:
    """Download multiple icon packs.

    Args:
        pack_names: List of pack names to download. Defaults to DEFAULT_PACK_NAMES.
        force: Re-download even if already present.

    Returns:
        Mapping of pack name to number of SVGs extracted.
    """
    names = pack_names or DEFAULT_PACK_NAMES
    results: dict[str, int] = {}
    for name in names:
        pack = ALL_PACKS.get(name)
        if pack is None:
            print(f"Unknown icon pack: {name}")
            continue
        results[name] = download_pack(pack, force=force)
    return results


def download_icons(force: bool = False) -> None:
    """Backward-compatible wrapper: download the Azure icon pack.

    Skips download if the per-pack .downloaded marker already exists.
    """
    azure = ALL_PACKS["azure"]
    if not force and azure.downloaded_marker.exists():
        print(f"Icons already downloaded ({azure.downloaded_marker}), skipping.")
        return
    download_pack(azure, force=force)
