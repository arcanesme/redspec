"""Declarative icon pack definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from redspec.config import ICON_CACHE_DIR


@dataclass(frozen=True)
class IconPack:
    """Metadata and extraction rules for a downloadable icon pack."""

    name: str  # "azure", "m365", "dynamics365", "power-platform"
    display_name: str
    url: str
    namespace: str  # prefix in YAML resource types
    filename_prefix_re: str  # regex to strip from SVG filenames
    filename_suffix_re: str  # regex to strip (e.g., "_scalable")
    extract_filter: str | None  # glob pattern to select which SVGs from ZIP
    aliases: dict[str, str] = field(default_factory=dict)

    @property
    def cache_dir(self) -> Path:
        """Per-pack icon cache directory."""
        return ICON_CACHE_DIR / self.name

    @property
    def downloaded_marker(self) -> Path:
        """Per-pack .downloaded marker file."""
        return self.cache_dir / ".downloaded"

    @property
    def _compiled_prefix_re(self) -> re.Pattern[str] | None:
        if not self.filename_prefix_re:
            return None
        return re.compile(self.filename_prefix_re, re.IGNORECASE)

    @property
    def _compiled_suffix_re(self) -> re.Pattern[str] | None:
        if not self.filename_suffix_re:
            return None
        return re.compile(self.filename_suffix_re, re.IGNORECASE)

    def normalize_filename(self, filename: str) -> str:
        """Strip prefix/suffix patterns, .svg extension, lowercase, hyphenate."""
        name = filename
        prefix = self._compiled_prefix_re
        if prefix:
            name = prefix.sub("", name)
        name = name.removesuffix(".svg").removesuffix(".SVG")
        suffix = self._compiled_suffix_re
        if suffix:
            name = suffix.sub("", name)
        return name.lower().replace(" ", "-").replace("_", "-")


# ---------------------------------------------------------------------------
# Pack definitions
# ---------------------------------------------------------------------------

AZURE_PACK = IconPack(
    name="azure",
    display_name="Azure Public Service Icons",
    url="https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V23.zip",
    namespace="azure",
    filename_prefix_re=r"^\d+-icon-service-",
    filename_suffix_re="",
    extract_filter="*.svg",
    aliases={
        "vm": "virtual-machines",
        "vnet": "virtual-networks",
        "aks": "kubernetes-services",
        "sql-database": "sql-database",
        "app-service": "app-services",
        "nsg": "network-security-groups",
        "lb": "load-balancers",
        "agw": "application-gateways",
        "func": "function-apps",
        "kv": "key-vaults",
        "acr": "container-registries",
        "apim": "api-management-services",
        "storage": "storage-accounts",
        "cosmos": "azure-cosmos-db",
        "redis": "cache-redis",
        "frontdoor": "front-doors",
        "law": "log-analytics-workspaces",
        "adf": "data-factory",
        "resource-group": "resource-groups",
        "subnet": "subnets-with-delegation",
        "subscription": "subscriptions",
    },
)

M365_PACK = IconPack(
    name="m365",
    display_name="Microsoft 365 Content Icons",
    url=(
        "https://download.microsoft.com/download/"
        "0/5/2/0526e49c-fe81-4578-a2d1-5003f5dc8432/"
        "2024-microsoft-365-content-icons.zip"
    ),
    namespace="m365",
    filename_prefix_re="",
    filename_suffix_re="",
    extract_filter="*/48x48 Dark*/*.svg",
    aliases={},
)

DYNAMICS365_PACK = IconPack(
    name="dynamics365",
    display_name="Dynamics 365 Icons",
    url=(
        "https://download.microsoft.com/download/"
        "b/a/9/ba9f10fa-c3cf-40f0-bab8-77da9e206946/"
        "Dynamics-365-icons-scalable.zip"
    ),
    namespace="dynamics365",
    filename_prefix_re="",
    filename_suffix_re=r"_scalable$",
    extract_filter="*.svg",
    aliases={
        "bc": "businesscentral",
        "sales": "sales",
        "finance": "finance",
        "cs": "customerservices",
        "scm": "supplychainmanagement",
    },
)

POWER_PLATFORM_PACK = IconPack(
    name="power-platform",
    display_name="Power Platform Icons",
    url=(
        "https://download.microsoft.com/download/"
        "5/4/0/540cc80f-af0a-411b-97d3-f15e2a9e1b8a/"
        "Power-Platform-icons-scalable.zip"
    ),
    namespace="power-platform",
    filename_prefix_re="",
    filename_suffix_re=r"_scalable$",
    extract_filter="*.svg",
    aliases={
        "power-apps": "powerapps",
        "power-automate": "powerautomate",
        "power-bi": "powerbi",
    },
)

ALL_PACKS: dict[str, IconPack] = {
    pack.name: pack
    for pack in (AZURE_PACK, M365_PACK, DYNAMICS365_PACK, POWER_PLATFORM_PACK)
}

DEFAULT_PACK_NAMES: list[str] = ["azure"]
