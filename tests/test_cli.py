"""Tests for CLI commands."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from redspec.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestInit:
    def test_init_creates_file(self, runner, tmp_path):
        output = tmp_path / "test.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        assert "template" in result.output.lower() or "written" in result.output.lower()

    def test_init_default_name(self, runner, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / "architecture.yaml").exists()

    def test_init_existing_file(self, runner, tmp_path):
        existing = tmp_path / "exists.yaml"
        existing.write_text("existing content")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(existing)])
        assert result.exit_code != 0

    def test_init_template_m365(self, runner, tmp_path):
        output = tmp_path / "m365.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output), "--template", "m365"])
        assert result.exit_code == 0
        content = output.read_text()
        assert "m365/" in content

    def test_init_template_multi_cloud(self, runner, tmp_path):
        output = tmp_path / "multi.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output), "--template", "multi-cloud"])
        assert result.exit_code == 0
        content = output.read_text()
        assert "azure/" in content
        assert "dynamics365/" in content

    def test_init_template_has_direction_and_theme(self, runner, tmp_path):
        output = tmp_path / "test.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output)])
        assert result.exit_code == 0
        content = output.read_text()
        assert "direction: TB" in content
        assert "theme: default" in content


class TestValidate:
    def test_validate_valid_yaml(self, runner, minimal_yaml_path):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["validate", str(minimal_yaml_path)])
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_validate_invalid_yaml(self, runner, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("{{not yaml")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["validate", str(bad)])
        assert result.exit_code != 0

    def test_validate_shows_counts(self, runner, minimal_yaml_path):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["validate", str(minimal_yaml_path)])
        assert "2 resources" in result.output
        assert "1 connections" in result.output


class TestGenerate:
    def test_generate_creates_png(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output)]
            )

        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_generate_with_format_svg(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.svg"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--format", "svg"]
            )

        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_generate_with_direction(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--direction", "LR"]
            )

        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_generate_with_dpi(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--dpi", "300"]
            )

        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_generate_direction_case_insensitive(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--direction", "lr"]
            )

        assert result.exit_code == 0, result.output

    def test_generate_dpi_out_of_range(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--dpi", "10"]
            )

        assert result.exit_code != 0

    def test_generate_default_organized_output(self, runner, minimal_yaml_path, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path)]
            )

        assert result.exit_code == 0, result.output
        assert "Diagram written to" in result.output

    def test_generate_custom_output_dir(self, runner, minimal_yaml_path, tmp_path):
        output_dir = tmp_path / "custom_out"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-d", str(output_dir)]
            )

        assert result.exit_code == 0, result.output
        assert "Diagram written to" in result.output

    def test_generate_output_and_output_dir_conflict(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.png"
        output_dir = tmp_path / "dir"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "-d", str(output_dir)]
            )

        assert result.exit_code != 0
        assert "Cannot use both" in result.output


class TestServe:
    def test_serve_help(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["serve", "--help"])
        assert result.exit_code == 0
        assert "port" in result.output


class TestListResources:
    def test_list_resources(self, runner, mock_icon_dir):
        mock_registry = MagicMock()
        mock_registry.list_all.return_value = ["app-services", "virtual-machines"]

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.registry.IconRegistry", return_value=mock_registry):
            result = runner.invoke(main, ["list-resources"])
        assert result.exit_code == 0
        assert "app-services" in result.output
        assert "virtual-machines" in result.output

    def test_list_resources_with_pack_filter(self, runner):
        mock_registry = MagicMock()
        mock_registry.list_all.return_value = ["dynamics365/sales", "dynamics365/finance"]

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.registry.IconRegistry", return_value=mock_registry):
            result = runner.invoke(main, ["list-resources", "--pack", "dynamics365"])
        assert result.exit_code == 0
        mock_registry.list_all.assert_called_with(namespace="dynamics365")


class TestUpdateIcons:
    def test_update_icons_default(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.downloader.download_packs", return_value={"azure": 100}) as mock_dl:
            result = runner.invoke(main, ["update-icons"])
        assert result.exit_code == 0
        assert "Icons updated" in result.output
        mock_dl.assert_called_once_with(["azure"], force=True)

    def test_update_icons_specific_packs(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.downloader.download_packs", return_value={"azure": 100, "dynamics365": 16}) as mock_dl:
            result = runner.invoke(main, ["update-icons", "azure", "dynamics365"])
        assert result.exit_code == 0
        mock_dl.assert_called_once_with(["azure", "dynamics365"], force=True)

    def test_update_icons_all(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.downloader.download_packs", return_value={}) as mock_dl:
            result = runner.invoke(main, ["update-icons", "--all"])
        assert result.exit_code == 0
        call_args = mock_dl.call_args[0][0]
        assert len(call_args) == 4

    def test_update_icons_list(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.display_name = "Azure Public Service Icons"
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.items.return_value = [("azure", mock_pack)]
            result = runner.invoke(main, ["update-icons", "--list"])
        assert result.exit_code == 0
        assert "azure" in result.output
        assert "installed" in result.output
