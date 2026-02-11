"""Tests for CLI commands."""

import json
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

    def test_init_aws_template(self, runner, tmp_path):
        output = tmp_path / "aws.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output), "--template", "aws"])
        assert result.exit_code == 0
        content = output.read_text()
        assert "aws/" in content

    def test_init_gcp_template(self, runner, tmp_path):
        output = tmp_path / "gcp.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output), "--template", "gcp"])
        assert result.exit_code == 0
        content = output.read_text()
        assert "gcp/" in content

    def test_init_k8s_template(self, runner, tmp_path):
        output = tmp_path / "k8s.yaml"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["init", str(output), "--template", "k8s"])
        assert result.exit_code == 0
        content = output.read_text()
        assert "k8s/" in content


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

    def test_validate_with_lint(self, runner, tmp_path):
        yaml_file = tmp_path / "lint.yaml"
        yaml_file.write_text(
            "diagram:\n  name: Test\n"
            "resources:\n"
            "  - type: azure/vm\n    name: orphan-vm\n"
            "connections: []\n",
            encoding="utf-8",
        )
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["validate", str(yaml_file), "--lint"])
        assert result.exit_code == 0
        assert "WARN" in result.output or "No lint warnings" in result.output


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


class TestGeneratePolish:
    def test_generate_with_polish_flag(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.svg"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--format", "svg", "--polish", "premium"]
            )

        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_generate_invalid_polish_rejected(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.svg"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--polish", "bogus"]
            )

        assert result.exit_code != 0

    def test_generate_with_glow_flag(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.svg"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--format", "svg", "--glow"]
            )

        assert result.exit_code == 0, result.output

    def test_generate_with_no_glow_flag(self, runner, minimal_yaml_path, tmp_path):
        output = tmp_path / "output.svg"

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(
                main, ["generate", str(minimal_yaml_path), "-o", str(output), "--format", "svg", "--no-glow"]
            )

        assert result.exit_code == 0, result.output


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


class TestSchema:
    def test_schema_stdout(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["schema"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "$schema" in data

    def test_schema_output_file(self, runner, tmp_path):
        output = tmp_path / "schema.json"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["schema", "-o", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert "$schema" in data

    def test_schema_bundled(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["schema", "--bundled"])
        assert result.exit_code == 0
        assert "redspec-spec.json" in result.output


class TestBatch:
    def test_batch_valid_files(self, runner, tmp_path):
        # Create 2 valid YAML files
        for name in ("a.yaml", "b.yaml"):
            (tmp_path / name).write_text(
                "diagram:\n  name: Test\nresources:\n  - type: azure/vm\n    name: vm1\nconnections: []\n",
                encoding="utf-8",
            )

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(main, ["batch", str(tmp_path)])

        assert result.exit_code == 0
        assert "2 succeeded" in result.output

    def test_batch_empty_directory(self, runner, tmp_path):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["batch", str(tmp_path)])
        assert result.exit_code == 0
        assert "No YAML files" in result.output

    def test_batch_mixed(self, runner, tmp_path):
        # 1 valid + 1 invalid
        (tmp_path / "good.yaml").write_text(
            "diagram:\n  name: Good\nresources:\n  - type: azure/vm\n    name: vm1\nconnections: []\n",
            encoding="utf-8",
        )
        (tmp_path / "bad.yaml").write_text("{{not yaml", encoding="utf-8")

        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("redspec.icons.packs.ALL_PACKS") as mock_packs:
            mock_pack = MagicMock()
            mock_pack.downloaded_marker.exists.return_value = True
            mock_packs.__getitem__ = MagicMock(return_value=mock_pack)
            result = runner.invoke(main, ["batch", str(tmp_path)])

        assert result.exit_code == 0
        assert "1 succeeded" in result.output
        assert "1 failed" in result.output


def _make_gallery_entry(output_dir, slug, name="Test", fmt="png"):
    """Helper to create a fake gallery entry."""
    d = output_dir / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / f"diagram.{fmt}").write_bytes(b"\x00")
    (d / "spec.yaml").write_text("diagram:\n  name: Test\n")
    import json, datetime
    (d / "metadata.json").write_text(json.dumps({
        "name": name, "slug": slug, "format": fmt,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }))
    return d


class TestClean:
    def test_clean_no_output_dir(self, runner, tmp_path):
        missing = tmp_path / "no-such-dir"
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(missing)])
        assert result.exit_code == 0
        assert "does not exist" in result.output

    def test_clean_list_mode_shows_files(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-diagram", name="My Diagram")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out)])
        assert result.exit_code == 0
        assert "my-diagram" in result.output
        assert "My Diagram" in result.output
        # Should show individual files
        assert "diagram.png" in result.output
        assert "spec.yaml" in result.output
        assert "metadata.json" in result.output
        # Should show total
        assert "Total:" in result.output

    def test_clean_list_empty(self, runner, tmp_path):
        out = tmp_path / "output"
        out.mkdir()
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out)])
        assert result.exit_code == 0
        assert "No generated diagrams" in result.output

    def test_clean_specific_slug(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "keep-me")
        _make_gallery_entry(out, "delete-me")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "delete-me"])
        assert result.exit_code == 0
        assert "Removed: delete-me/" in result.output
        assert (out / "keep-me").is_dir()
        assert not (out / "delete-me").exists()

    def test_clean_specific_slug_shows_file_count(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "my-app"])
        assert result.exit_code == 0
        assert "3 files" in result.output

    def test_clean_specific_not_found(self, runner, tmp_path):
        out = tmp_path / "output"
        out.mkdir()
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "nope"])
        assert "Not found: nope" in result.output

    def test_clean_all(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "a")
        _make_gallery_entry(out, "b")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--all", "-y"])
        assert result.exit_code == 0
        assert "Removed" in result.output
        assert "2 diagram(s)" in result.output
        assert not out.exists()

    def test_clean_dry_run_all_shows_files(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "a")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--all", "--dry-run"])
        assert result.exit_code == 0
        assert "Would delete" in result.output
        assert "a/" in result.output
        assert "diagram.png" in result.output
        assert out.is_dir()  # not actually deleted

    def test_clean_dry_run_specific_shows_files(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--dry-run", "my-app"])
        assert result.exit_code == 0
        assert "Would delete: my-app/" in result.output
        assert "diagram.png" in result.output
        assert "spec.yaml" in result.output
        assert (out / "my-app").is_dir()  # not actually deleted

    # --- Delete individual files within a spec ---

    def test_clean_delete_single_file(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "--file", "diagram.png", "my-app"])
        assert result.exit_code == 0
        assert "Deleted: my-app/diagram.png" in result.output
        assert not (out / "my-app" / "diagram.png").exists()
        # Other files still there
        assert (out / "my-app" / "spec.yaml").exists()

    def test_clean_delete_single_file_not_found(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "--file", "nope.txt", "my-app"])
        assert "File not found: my-app/nope.txt" in result.output

    def test_clean_delete_file_dry_run(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--dry-run", "--file", "diagram.png", "my-app"])
        assert "Would delete: my-app/diagram.png" in result.output
        assert (out / "my-app" / "diagram.png").exists()  # not actually deleted

    def test_clean_delete_all_files_removes_empty_dir(self, runner, tmp_path):
        out = tmp_path / "output"
        d = out / "solo"
        d.mkdir(parents=True)
        (d / "only-file.txt").write_text("x")
        # Need metadata.json so the slug dir is found
        import json, datetime
        (d / "metadata.json").write_text(json.dumps({
            "name": "Solo", "slug": "solo", "format": "txt",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }))
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            # Delete only-file.txt
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "--file", "only-file.txt", "solo"])
        assert result.exit_code == 0
        assert "Deleted: solo/only-file.txt" in result.output
        # metadata.json remains, so directory still exists
        assert (out / "solo").is_dir()
        # Now delete metadata.json too
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "-y", "--file", "metadata.json", "solo"])
        assert "Deleted: solo/metadata.json" in result.output
        assert "Removed empty directory: solo/" in result.output
        assert not (out / "solo").exists()

    # --- Edit mode ---

    def test_clean_edit_opens_editor(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("click.edit") as mock_edit:
            result = runner.invoke(main, ["clean", "-d", str(out), "--edit", "my-app"])
        assert result.exit_code == 0
        mock_edit.assert_called_once()
        # Should open spec.yaml by default
        call_kwargs = mock_edit.call_args
        assert "spec.yaml" in call_kwargs.kwargs["filename"]

    def test_clean_edit_custom_file(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False), \
             patch("click.edit") as mock_edit:
            result = runner.invoke(main, ["clean", "-d", str(out), "--edit", "--file", "metadata.json", "my-app"])
        assert result.exit_code == 0
        call_kwargs = mock_edit.call_args
        assert "metadata.json" in call_kwargs.kwargs["filename"]

    def test_clean_edit_missing_slug(self, runner, tmp_path):
        out = tmp_path / "output"
        out.mkdir()
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--edit"])
        assert result.exit_code != 0

    def test_clean_edit_missing_file(self, runner, tmp_path):
        out = tmp_path / "output"
        _make_gallery_entry(out, "my-app")
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["clean", "-d", str(out), "--edit", "--file", "nope.txt", "my-app"])
        assert result.exit_code != 0
        assert "File not found" in result.output


class TestWatch:
    def test_watch_help(self, runner):
        with patch("redspec.icons.migration.migrate_flat_cache", return_value=False):
            result = runner.invoke(main, ["watch", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output
        assert "--no-browser" in result.output
        assert "--format" in result.output
