"""Tests for icon registry."""

from redspec.icons.registry import IconRegistry, _normalize_filename


class TestNormalizeFilename:
    def test_strip_prefix(self):
        assert _normalize_filename("10035-icon-service-App-Services.svg") == "app-services"

    def test_no_prefix(self):
        assert _normalize_filename("My-Icon.svg") == "my-icon"

    def test_spaces_to_hyphens(self):
        assert _normalize_filename("10035-icon-service-App Services.svg") == "app-services"


class TestIconRegistry:
    def test_scan_finds_icons(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        names = registry.list_all()
        assert len(names) > 0
        assert "app-services" in names

    def test_resolve_direct_match(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/app-services")
        assert path is not None
        assert path.suffix == ".svg"

    def test_resolve_alias(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/app-service")
        assert path is not None

    def test_resolve_vm_alias(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/vm")
        assert path is not None

    def test_resolve_vnet_alias(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/vnet")
        assert path is not None

    def test_resolve_aks_alias(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/aks")
        assert path is not None

    def test_resolve_unknown_returns_none(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/nonexistent-thing-xyz")
        assert path is None

    def test_resolve_fuzzy_match(self, mock_icon_dir):
        registry = IconRegistry(icon_dir=mock_icon_dir)
        path = registry.resolve("azure/function")
        assert path is not None

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty_icons"
        empty.mkdir()
        registry = IconRegistry(icon_dir=empty)
        assert registry.list_all() == []
        assert registry.resolve("azure/vm") is None

    def test_nonexistent_dir(self, tmp_path):
        registry = IconRegistry(icon_dir=tmp_path / "does-not-exist")
        assert registry.list_all() == []
