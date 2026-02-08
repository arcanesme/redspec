"""Icon registry: scan cached SVGs and resolve resource types to file paths."""

from __future__ import annotations

import re
from pathlib import Path

from redspec.config import ICON_CACHE_DIR
from redspec.icons.packs import ALL_PACKS, IconPack

# Legacy prefix pattern for backward compatibility with _normalize_filename
_PREFIX_RE = re.compile(r"^\d+-icon-service-", re.IGNORECASE)


def _normalize_filename(filename: str) -> str:
    """Strip numeric prefix and .svg suffix, lowercase, hyphenate.

    Kept for backward compatibility with tests referencing this function.
    """
    name = _PREFIX_RE.sub("", filename)
    name = name.removesuffix(".svg").removesuffix(".SVG")
    return name.lower().replace(" ", "-")


# Legacy aliases kept for backward-compat (used by PackRegistry for azure pack)
ALIASES: dict[str, str] = {
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
}


class PackRegistry:
    """Lookup table for a single icon pack's SVG files."""

    def __init__(
        self,
        pack: IconPack,
        icon_dir: Path | None = None,
    ) -> None:
        self._pack = pack
        self._icon_dir = icon_dir or pack.cache_dir
        self._icons: dict[str, Path] = {}
        self._scan()

    @property
    def namespace(self) -> str:
        return self._pack.namespace

    @property
    def pack_name(self) -> str:
        return self._pack.name

    def _scan(self) -> None:
        if not self._icon_dir.is_dir():
            return
        for svg in self._icon_dir.glob("*.svg"):
            normalised = self._pack.normalize_filename(svg.name)
            self._icons[normalised] = svg

    def resolve(self, key: str) -> Path | None:
        """Resolve a key (without namespace prefix) to an SVG path."""
        k = key.lower()

        # Alias resolution
        k = self._pack.aliases.get(k, k)

        # Direct match
        if k in self._icons:
            return self._icons[k]

        # Fuzzy substring match
        for name, path in self._icons.items():
            if k in name or name in k:
                return path

        return None

    def list_all(self) -> list[str]:
        """Return all available icon type names, sorted."""
        return sorted(self._icons)


class IconRegistry:
    """Multi-pack icon registry that composes multiple PackRegistry instances.

    Supports namespace routing (e.g. "azure/vm") and fallback search across
    all packs.
    """

    def __init__(
        self,
        icon_dir: Path | None = None,
        pack_names: list[str] | None = None,
    ) -> None:
        self._registries: dict[str, PackRegistry] = {}

        if icon_dir is not None:
            # Legacy mode: single directory treated as azure pack
            azure_pack = ALL_PACKS["azure"]
            self._registries["azure"] = PackRegistry(azure_pack, icon_dir=icon_dir)
        else:
            # Multi-pack mode: load installed packs
            names = pack_names or list(ALL_PACKS.keys())
            for name in names:
                pack = ALL_PACKS.get(name)
                if pack is None:
                    continue
                if pack.cache_dir.is_dir():
                    self._registries[name] = PackRegistry(pack)

    def resolve(self, resource_type: str) -> Path | None:
        """Resolve a resource type string to an SVG path.

        If the resource_type contains a namespace prefix (e.g. "azure/vm"),
        routes to the specific pack. Otherwise searches all packs in order.
        """
        key = resource_type.lower()

        # Check for namespace prefix
        if "/" in key:
            namespace, icon_key = key.split("/", 1)
            registry = self._registries.get(namespace)
            if registry is not None:
                return registry.resolve(icon_key)
            return None

        # Search all packs in order
        for registry in self._registries.values():
            result = registry.resolve(key)
            if result is not None:
                return result

        return None

    def list_all(self, namespace: str | None = None) -> list[str]:
        """Return all available icon names, optionally filtered by namespace.

        Returns fully-qualified names (e.g. "azure/app-services") unless
        only one pack is loaded.
        """
        if namespace is not None:
            registry = self._registries.get(namespace)
            if registry is None:
                return []
            return [f"{namespace}/{name}" for name in registry.list_all()]

        results: list[str] = []
        if len(self._registries) == 1:
            # Single pack: return unqualified names for backward compat
            reg = next(iter(self._registries.values()))
            return reg.list_all()

        for ns, registry in self._registries.items():
            results.extend(f"{ns}/{name}" for name in registry.list_all())
        return sorted(results)

    def installed_packs(self) -> list[str]:
        """Return names of loaded packs."""
        return list(self._registries.keys())
