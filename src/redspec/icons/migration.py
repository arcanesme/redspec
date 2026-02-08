"""One-time migration from flat icon cache to per-pack layout."""

from pathlib import Path

from redspec.config import ICON_CACHE_DIR


def migrate_flat_cache() -> bool:
    """Move existing flat cache (icons/*.svg) into icons/azure/.

    Returns True if migration was performed, False if not needed.
    """
    old_marker = ICON_CACHE_DIR / ".downloaded"
    new_dir = ICON_CACHE_DIR / "azure"
    new_marker = new_dir / ".downloaded"

    # Already migrated or nothing to migrate
    if new_marker.exists() or not old_marker.exists():
        return False

    new_dir.mkdir(parents=True, exist_ok=True)

    # Move all SVGs
    moved = 0
    for svg in ICON_CACHE_DIR.glob("*.svg"):
        svg.rename(new_dir / svg.name)
        moved += 1

    # Move marker
    old_marker.rename(new_marker)

    if moved:
        print(f"Migrated {moved} icons to {new_dir}")

    return True
