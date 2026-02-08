"""Tests for watch mode (D1)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from redspec.watcher import _get_mtime, watch_loop


class TestGetMtime:
    def test_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert _get_mtime(f) > 0

    def test_missing_file(self, tmp_path):
        assert _get_mtime(tmp_path / "nonexistent.txt") == 0.0


class TestWatchLoop:
    def test_detects_change_and_calls_rebuild(self, tmp_path):
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("resources: []\n")

        rebuild_paths = []

        def on_rebuild(path):
            rebuild_paths.append(path)

        # Stop immediately after first rebuild
        def should_stop():
            return len(rebuild_paths) >= 1

        mock_result = tmp_path / "diagram.svg"
        mock_result.write_text("<svg></svg>")

        with patch("redspec.watcher._rebuild", return_value=mock_result):
            watch_loop(
                yaml_file,
                on_rebuild=on_rebuild,
                should_stop=should_stop,
                poll_interval=0.01,
            )

        assert len(rebuild_paths) >= 1

    def test_on_first_build_called_once(self, tmp_path):
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("resources: []\n")

        first_build_count = [0]
        rebuild_count = [0]

        def on_first_build(path):
            first_build_count[0] += 1

        def on_rebuild(path):
            rebuild_count[0] += 1

        def should_stop():
            return rebuild_count[0] >= 1

        mock_result = tmp_path / "diagram.svg"
        mock_result.write_text("<svg></svg>")

        with patch("redspec.watcher._rebuild", return_value=mock_result):
            watch_loop(
                yaml_file,
                on_rebuild=on_rebuild,
                on_first_build=on_first_build,
                should_stop=should_stop,
                poll_interval=0.01,
            )

        assert first_build_count[0] == 1

    def test_error_resilience(self, tmp_path):
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("resources: []\n")

        from redspec.exceptions import YAMLParseError

        error_count = [0]

        def on_error(exc):
            error_count[0] += 1

        def should_stop():
            return error_count[0] >= 1

        def mock_rebuild(f):
            raise YAMLParseError("bad yaml")

        with patch("redspec.watcher._rebuild", side_effect=mock_rebuild):
            watch_loop(
                yaml_file,
                on_rebuild=lambda p: None,
                on_error=on_error,
                should_stop=should_stop,
                poll_interval=0.01,
            )

        assert error_count[0] >= 1
