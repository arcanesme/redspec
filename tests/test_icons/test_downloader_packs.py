"""Tests for pack-aware download functions."""

import io
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from redspec.icons.downloader import download_pack, download_packs
from redspec.icons.packs import AZURE_PACK, DYNAMICS365_PACK, IconPack


def _make_zip_bytes(files: dict[str, bytes]) -> bytes:
    """Create an in-memory ZIP file with the given entries."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


SVG_BYTES = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="1"/></svg>'


class TestDownloadPack:
    def test_skips_if_already_downloaded(self, tmp_path):
        pack = IconPack(
            name="test-pack",
            display_name="Test Pack",
            url="https://example.com/test.zip",
            namespace="test",
            filename_prefix_re="",
            filename_suffix_re="",
            extract_filter="*.svg",
        )
        # Patch cache_dir to tmp_path
        cache_dir = tmp_path / "test-pack"
        cache_dir.mkdir()
        marker = cache_dir / ".downloaded"
        marker.touch()

        with patch.object(type(pack), "cache_dir", new_callable=lambda: property(lambda self: cache_dir)), \
             patch.object(type(pack), "downloaded_marker", new_callable=lambda: property(lambda self: marker)):
            count = download_pack(pack, force=False)
        assert count == 0

    def test_downloads_and_extracts(self, tmp_path, monkeypatch):
        zip_data = _make_zip_bytes({
            "icons/Sales_scalable.svg": SVG_BYTES,
            "icons/Finance_scalable.svg": SVG_BYTES,
            "readme.txt": b"not an svg",
        })

        cache_dir = tmp_path / "dynamics365"

        pack = IconPack(
            name="dynamics365",
            display_name="Dynamics 365",
            url="https://example.com/dynamics.zip",
            namespace="dynamics365",
            filename_prefix_re="",
            filename_suffix_re=r"_scalable$",
            extract_filter="*.svg",
        )

        def mock_urlretrieve(url, path):
            Path(path).write_bytes(zip_data)

        with patch.object(type(pack), "cache_dir", new_callable=lambda: property(lambda self: cache_dir)), \
             patch.object(type(pack), "downloaded_marker", new_callable=lambda: property(lambda self: cache_dir / ".downloaded")), \
             patch("redspec.icons.downloader.urllib.request.urlretrieve", side_effect=mock_urlretrieve):
            count = download_pack(pack, force=False)

        assert count == 2
        assert (cache_dir / "Sales_scalable.svg").exists()
        assert (cache_dir / "Finance_scalable.svg").exists()
        assert (cache_dir / ".downloaded").exists()

    def test_extract_filter_applied(self, tmp_path):
        zip_data = _make_zip_bytes({
            "Brand/48x48 Dark/Chat.svg": SVG_BYTES,
            "Brand/48x48 Light/Chat.svg": SVG_BYTES,
            "Brand/96x96 Dark/Chat.svg": SVG_BYTES,
        })

        cache_dir = tmp_path / "m365"

        pack = IconPack(
            name="m365",
            display_name="M365",
            url="https://example.com/m365.zip",
            namespace="m365",
            filename_prefix_re="",
            filename_suffix_re="",
            extract_filter="*/48x48 Dark*/*.svg",
        )

        def mock_urlretrieve(url, path):
            Path(path).write_bytes(zip_data)

        with patch.object(type(pack), "cache_dir", new_callable=lambda: property(lambda self: cache_dir)), \
             patch.object(type(pack), "downloaded_marker", new_callable=lambda: property(lambda self: cache_dir / ".downloaded")), \
             patch("redspec.icons.downloader.urllib.request.urlretrieve", side_effect=mock_urlretrieve):
            count = download_pack(pack, force=False)

        # Only the 48x48 Dark variant should be extracted
        assert count == 1


class TestDownloadPacks:
    def test_downloads_default_packs(self):
        with patch("redspec.icons.downloader.download_pack", return_value=5) as mock_dl:
            results = download_packs()
        assert "azure" in results
        assert results["azure"] == 5
        mock_dl.assert_called_once()

    def test_downloads_specified_packs(self):
        with patch("redspec.icons.downloader.download_pack", return_value=3) as mock_dl:
            results = download_packs(["azure", "dynamics365"])
        assert len(results) == 2
        assert mock_dl.call_count == 2

    def test_skips_unknown_packs(self, capsys):
        with patch("redspec.icons.downloader.download_pack", return_value=0):
            results = download_packs(["nonexistent"])
        assert "nonexistent" not in results
        captured = capsys.readouterr()
        assert "Unknown icon pack" in captured.out
