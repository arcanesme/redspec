"""Tests for flat cache migration."""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from redspec.icons.migration import migrate_flat_cache


class TestMigrateFlatCache:
    def test_migration_moves_svgs(self, tmp_path, sample_svg):
        """Migration moves SVGs from icons/ to icons/azure/."""
        icon_dir = tmp_path / "icons"
        icon_dir.mkdir()

        # Create fake flat-layout files
        shutil.copy(sample_svg, icon_dir / "app-services.svg")
        shutil.copy(sample_svg, icon_dir / "virtual-machines.svg")
        (icon_dir / ".downloaded").touch()

        with patch("redspec.icons.migration.ICON_CACHE_DIR", icon_dir):
            result = migrate_flat_cache()

        assert result is True
        assert (icon_dir / "azure" / "app-services.svg").exists()
        assert (icon_dir / "azure" / "virtual-machines.svg").exists()
        assert (icon_dir / "azure" / ".downloaded").exists()
        # Old files should be gone
        assert not (icon_dir / "app-services.svg").exists()
        assert not (icon_dir / ".downloaded").exists()

    def test_no_migration_if_already_done(self, tmp_path):
        """No migration if azure/.downloaded already exists."""
        icon_dir = tmp_path / "icons"
        azure_dir = icon_dir / "azure"
        azure_dir.mkdir(parents=True)
        (azure_dir / ".downloaded").touch()

        with patch("redspec.icons.migration.ICON_CACHE_DIR", icon_dir):
            result = migrate_flat_cache()

        assert result is False

    def test_no_migration_if_no_marker(self, tmp_path):
        """No migration if old .downloaded marker doesn't exist."""
        icon_dir = tmp_path / "icons"
        icon_dir.mkdir()

        with patch("redspec.icons.migration.ICON_CACHE_DIR", icon_dir):
            result = migrate_flat_cache()

        assert result is False

    def test_migration_empty_dir(self, tmp_path):
        """Migration handles empty icon dir (only marker, no SVGs)."""
        icon_dir = tmp_path / "icons"
        icon_dir.mkdir()
        (icon_dir / ".downloaded").touch()

        with patch("redspec.icons.migration.ICON_CACHE_DIR", icon_dir):
            result = migrate_flat_cache()

        assert result is True
        assert (icon_dir / "azure" / ".downloaded").exists()
