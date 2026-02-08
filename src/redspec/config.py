"""Cache paths, Azure icon URL, and constants."""

from pathlib import Path

AZURE_ICON_URL = (
    "https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V23.zip"
)

CACHE_DIR = Path.home() / ".cache" / "redspec"
ICON_CACHE_DIR = CACHE_DIR / "icons"
DOWNLOADED_MARKER = ICON_CACHE_DIR / "azure" / ".downloaded"
