"""Tests for multi-pack IconRegistry and PackRegistry."""

import shutil
from pathlib import Path

import pytest

from redspec.icons.packs import AZURE_PACK, DYNAMICS365_PACK, POWER_PLATFORM_PACK
from redspec.icons.registry import IconRegistry, PackRegistry


@pytest.fixture
def dynamics_icon_dir(tmp_path, sample_svg):
    """Create a temp directory with fake Dynamics 365 icons."""
    icon_dir = tmp_path / "dynamics365"
    icon_dir.mkdir()
    icons = [
        "Sales_scalable.svg",
        "Finance_scalable.svg",
        "BusinessCentral_scalable.svg",
        "CustomerServices_scalable.svg",
    ]
    for name in icons:
        shutil.copy(sample_svg, icon_dir / name)
    return icon_dir


@pytest.fixture
def power_platform_icon_dir(tmp_path, sample_svg):
    """Create a temp directory with fake Power Platform icons."""
    icon_dir = tmp_path / "power-platform"
    icon_dir.mkdir()
    icons = [
        "PowerApps_scalable.svg",
        "PowerAutomate_scalable.svg",
        "Dataverse_scalable.svg",
    ]
    for name in icons:
        shutil.copy(sample_svg, icon_dir / name)
    return icon_dir


class TestPackRegistry:
    def test_scan_dynamics365(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        names = reg.list_all()
        assert "sales" in names
        assert "finance" in names
        assert "businesscentral" in names

    def test_resolve_alias_dynamics365(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        path = reg.resolve("bc")
        assert path is not None
        assert path.suffix == ".svg"

    def test_resolve_direct_dynamics365(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        path = reg.resolve("sales")
        assert path is not None

    def test_resolve_unknown_returns_none(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        assert reg.resolve("nonexistent-xyz") is None

    def test_power_platform_normalize(self, power_platform_icon_dir):
        reg = PackRegistry(POWER_PLATFORM_PACK, icon_dir=power_platform_icon_dir)
        names = reg.list_all()
        assert "powerapps" in names
        assert "powerautomate" in names
        assert "dataverse" in names

    def test_power_platform_alias(self, power_platform_icon_dir):
        reg = PackRegistry(POWER_PLATFORM_PACK, icon_dir=power_platform_icon_dir)
        path = reg.resolve("power-apps")
        assert path is not None

    def test_namespace_property(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        assert reg.namespace == "dynamics365"

    def test_pack_name_property(self, dynamics_icon_dir):
        reg = PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir)
        assert reg.pack_name == "dynamics365"


class TestIconRegistryLegacy:
    """Tests for backward-compatible legacy mode (icon_dir= parameter)."""

    def test_legacy_mode(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        assert registry.installed_packs() == ["azure"]

    def test_legacy_resolve(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/app-services")
        assert path is not None

    def test_legacy_list_all(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        names = registry.list_all()
        assert "app-services" in names
        # Single pack: no namespace prefix
        assert all("/" not in n for n in names)


class TestIconRegistryMultiPack:
    """Tests for multi-pack mode with multiple registries."""

    @pytest.fixture
    def multi_registry(self, mock_icon_dir, dynamics_icon_dir, power_platform_icon_dir, monkeypatch):
        """Create IconRegistry backed by mock pack directories."""
        # We build manually since IconRegistry normally looks at cache_dir
        registry = IconRegistry.__new__(IconRegistry)
        registry._registries = {
            "azure": PackRegistry(AZURE_PACK, icon_dir=mock_icon_dir),
            "dynamics365": PackRegistry(DYNAMICS365_PACK, icon_dir=dynamics_icon_dir),
            "power-platform": PackRegistry(POWER_PLATFORM_PACK, icon_dir=power_platform_icon_dir),
        }
        return registry

    def test_namespace_routing(self, multi_registry):
        path = multi_registry.resolve("dynamics365/sales")
        assert path is not None
        assert path.suffix == ".svg"

    def test_namespace_routing_azure(self, multi_registry):
        path = multi_registry.resolve("azure/app-services")
        assert path is not None

    def test_namespace_routing_power_platform(self, multi_registry):
        path = multi_registry.resolve("power-platform/powerapps")
        assert path is not None

    def test_unknown_namespace_returns_none(self, multi_registry):
        assert multi_registry.resolve("unknown/something") is None

    def test_fallback_search_no_namespace(self, multi_registry):
        # Should find in azure pack via fuzzy matching
        path = multi_registry.resolve("app-services")
        assert path is not None

    def test_list_all_multi_pack(self, multi_registry):
        names = multi_registry.list_all()
        # Multi-pack: includes namespace prefixes
        assert any(n.startswith("azure/") for n in names)
        assert any(n.startswith("dynamics365/") for n in names)
        assert any(n.startswith("power-platform/") for n in names)

    def test_list_all_namespace_filter(self, multi_registry):
        names = multi_registry.list_all(namespace="dynamics365")
        assert all(n.startswith("dynamics365/") for n in names)
        assert "dynamics365/sales" in names

    def test_list_all_unknown_namespace(self, multi_registry):
        names = multi_registry.list_all(namespace="unknown")
        assert names == []

    def test_installed_packs(self, multi_registry):
        packs = multi_registry.installed_packs()
        assert set(packs) == {"azure", "dynamics365", "power-platform"}
