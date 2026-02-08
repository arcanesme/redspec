"""Cache paths, Azure icon URL, and constants."""

from pathlib import Path

AZURE_ICON_URL = (
    "https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V23.zip"
)

CACHE_DIR = Path.home() / ".cache" / "redspec"
ICON_CACHE_DIR = CACHE_DIR / "icons"
DOWNLOADED_MARKER = ICON_CACHE_DIR / "azure" / ".downloaded"

# Layout constants
NODE_WIDTH = 64
NODE_HEIGHT = 64
LABEL_HEIGHT = 20
CONTAINER_PADDING = 40
CONTAINER_HEADER = 30
CHILD_SPACING_X = 30
CHILD_SPACING_Y = 30

# Container types that render as draw.io containers
CONTAINER_TYPES = frozenset({
    "azure/resource-group",
    "azure/vnet",
    "azure/virtual-network",
    "azure/subnet",
    "azure/subscription",
})
