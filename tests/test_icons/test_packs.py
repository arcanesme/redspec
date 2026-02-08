"""Tests for IconPack dataclass and pack definitions."""

from redspec.icons.packs import (
    ALL_PACKS,
    AZURE_PACK,
    DEFAULT_PACK_NAMES,
    DYNAMICS365_PACK,
    M365_PACK,
    POWER_PLATFORM_PACK,
    IconPack,
)


class TestIconPack:
    def test_cache_dir(self):
        assert AZURE_PACK.cache_dir.name == "azure"
        assert AZURE_PACK.cache_dir.parent.name == "icons"

    def test_downloaded_marker(self):
        assert AZURE_PACK.downloaded_marker.name == ".downloaded"
        assert AZURE_PACK.downloaded_marker.parent == AZURE_PACK.cache_dir

    def test_normalize_azure(self):
        assert AZURE_PACK.normalize_filename("10035-icon-service-App-Services.svg") == "app-services"

    def test_normalize_dynamics365(self):
        assert DYNAMICS365_PACK.normalize_filename("Sales_scalable.svg") == "sales"

    def test_normalize_power_platform(self):
        assert POWER_PLATFORM_PACK.normalize_filename("PowerApps_scalable.svg") == "powerapps"

    def test_normalize_m365(self):
        assert M365_PACK.normalize_filename("Chat.svg") == "chat"

    def test_normalize_m365_spaces(self):
        assert M365_PACK.normalize_filename("Icon Name.svg") == "icon-name"

    def test_frozen(self):
        import pytest
        with pytest.raises(AttributeError):
            AZURE_PACK.name = "changed"  # type: ignore[misc]


class TestAllPacks:
    def test_all_packs_contains_four(self):
        assert len(ALL_PACKS) == 4

    def test_all_packs_keys(self):
        assert set(ALL_PACKS.keys()) == {"azure", "m365", "dynamics365", "power-platform"}

    def test_each_pack_has_url(self):
        for pack in ALL_PACKS.values():
            assert pack.url.startswith("https://")

    def test_each_pack_has_namespace(self):
        for pack in ALL_PACKS.values():
            assert pack.namespace == pack.name

    def test_default_packs(self):
        assert DEFAULT_PACK_NAMES == ["azure"]

    def test_azure_aliases_populated(self):
        assert "vm" in AZURE_PACK.aliases
        assert AZURE_PACK.aliases["vm"] == "virtual-machines"

    def test_dynamics365_aliases(self):
        assert "bc" in DYNAMICS365_PACK.aliases
        assert DYNAMICS365_PACK.aliases["bc"] == "businesscentral"

    def test_power_platform_aliases(self):
        assert "power-apps" in POWER_PLATFORM_PACK.aliases
        assert POWER_PLATFORM_PACK.aliases["power-apps"] == "powerapps"
